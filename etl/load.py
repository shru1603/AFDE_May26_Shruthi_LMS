"""
etl/load.py

Load step: inserts cleaned CSV data into the operational tables
(books, borrowers, transactions). Skips rows that already exist.

Analytics are computed live from these tables — no separate analytics
tables are needed as a primary source.
"""

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal
from database import models


def load_books(db, df: pd.DataFrame) -> dict:
    """Insert cleaned books. Returns mapping: csv_book_id -> db_book_id."""
    existing_isbns = {r.isbn: r.book_id for r in db.query(models.Book.isbn, models.Book.book_id).all()}
    book_id_map = {}
    inserted = skipped = 0

    for _, row in df.iterrows():
        csv_id = int(row["book_id"])
        isbn = row.get("isbn")
        isbn = str(isbn) if pd.notna(isbn) else None

        effective_isbn = isbn if isbn else f"CSV-{csv_id}"
        if effective_isbn in existing_isbns:
            book_id_map[csv_id] = existing_isbns[effective_isbn]
            skipped += 1
            continue

        book = models.Book(
            title=str(row.get("Title", "") or "").strip(),
            author=str(row.get("Authors", "") or "").strip(),
            category=str(row.get("Category", "") or "").strip(),
            isbn=effective_isbn,
            availability_status="available",
        )
        db.add(book)
        db.flush()
        book_id_map[csv_id] = book.book_id
        existing_isbns[effective_isbn] = book.book_id
        inserted += 1

    db.commit()
    print(f"[Load] Books        : {inserted} inserted, {skipped} skipped (duplicate ISBN)")
    return book_id_map


def load_borrowers(db, df: pd.DataFrame) -> dict:
    """Insert cleaned borrowers. Returns mapping: csv_borrower_id -> db_borrower_id."""
    existing_emails = {r.email: r.borrower_id for r in db.query(models.Borrower.email, models.Borrower.borrower_id).all()}
    borrower_id_map = {}
    inserted = skipped = 0

    for _, row in df.iterrows():
        csv_id = int(row["borrower_id"])
        email = str(row.get("email", "")).strip()

        if email in existing_emails:
            borrower_id_map[csv_id] = existing_emails[email]
            skipped += 1
            continue

        borrower = models.Borrower(
            borrower_name=str(row.get("borrower_name", "") or "").strip(),
            email=email,
            phone=str(row.get("phone", "") or "").strip(),
        )
        db.add(borrower)
        db.flush()
        borrower_id_map[csv_id] = borrower.borrower_id
        existing_emails[email] = borrower.borrower_id
        inserted += 1

    db.commit()
    print(f"[Load] Borrowers    : {inserted} inserted, {skipped} skipped (duplicate email)")
    return borrower_id_map


def load_transactions(db, df: pd.DataFrame, book_id_map: dict, borrower_id_map: dict):
    """Insert cleaned transactions using mapped DB IDs. Skips duplicates."""
    inserted = skipped = 0

    # Pre-load existing transactions as a set of (book_id, borrower_id, borrow_date)
    existing = {
        (r.book_id, r.borrower_id, r.borrow_date)
        for r in db.query(
            models.Transaction.book_id,
            models.Transaction.borrower_id,
            models.Transaction.borrow_date,
        ).all()
    }

    # Pre-load book titles and borrower names for snapshots
    book_titles = {r.book_id: r.title for r in db.query(models.Book.book_id, models.Book.title).all()}
    borrower_names = {r.borrower_id: r.borrower_name for r in db.query(models.Borrower.borrower_id, models.Borrower.borrower_name).all()}

    batch = []
    for _, row in df.iterrows():
        db_book_id = book_id_map.get(int(row["book_id"])) if pd.notna(row["book_id"]) else None
        db_borrower_id = borrower_id_map.get(int(row["borrower_id"])) if pd.notna(row["borrower_id"]) else None

        if not db_book_id or not db_borrower_id:
            skipped += 1
            continue

        borrow_date = row["borrow_date"]
        if pd.isna(borrow_date):
            skipped += 1
            continue

        borrow_dt = borrow_date.to_pydatetime() if hasattr(borrow_date, "to_pydatetime") else borrow_date
        key = (db_book_id, db_borrower_id, borrow_dt)
        if key in existing:
            skipped += 1
            continue

        return_date = row.get("return_date")
        return_dt = None
        if pd.notna(return_date):
            return_dt = return_date.to_pydatetime() if hasattr(return_date, "to_pydatetime") else return_date

        batch.append(models.Transaction(
            book_id=db_book_id,
            borrower_id=db_borrower_id,
            book_title=book_titles.get(db_book_id),
            borrower_name=borrower_names.get(db_borrower_id),
            borrow_date=borrow_dt,
            return_date=return_dt,
        ))
        existing.add(key)
        inserted += 1

    batch.sort(key=lambda t: t.borrow_date)
    db.bulk_save_objects(batch)
    db.commit()
    print(f"[Load] Transactions : {inserted} inserted, {skipped} skipped (unmapped/duplicate)")

    # Sync book availability_status based on active (unreturned) transactions
    active_book_ids = {
        r.book_id
        for r in db.query(models.Transaction.book_id)
        .filter(models.Transaction.return_date.is_(None))
        .all()
    }
    db.query(models.Book).update({"availability_status": "available"}, synchronize_session=False)
    if active_book_ids:
        db.query(models.Book).filter(
            models.Book.book_id.in_(active_book_ids)
        ).update({"availability_status": "borrowed"}, synchronize_session=False)
    db.commit()
    borrowed_count = len(active_book_ids)
    print(f"[Load] Availability : {borrowed_count} books marked borrowed, rest available")


def run(transformed: dict):
    print("\n" + "=" * 50)
    print("LOAD")
    print("=" * 50)

    db = SessionLocal()
    try:
        book_id_map = (
            load_books(db, transformed["books_clean"])
            if transformed.get("books_clean") is not None
            else {r.book_id: r.book_id for r in db.query(models.Book.book_id).all()}
        )

        borrower_id_map = (
            load_borrowers(db, transformed["borrowers_clean"])
            if transformed.get("borrowers_clean") is not None
            else {r.borrower_id: r.borrower_id for r in db.query(models.Borrower.borrower_id).all()}
        )

        if transformed.get("transactions_clean") is not None:
            load_transactions(db, transformed["transactions_clean"], book_id_map, borrower_id_map)
        else:
            print("[Load] Transactions : skipped (not uploaded)")
    finally:
        db.close()

    print("\n[Load] Operational tables updated successfully.")
