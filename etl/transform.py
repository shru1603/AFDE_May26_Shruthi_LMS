"""
etl/transform.py

Transform step: cleans raw DataFrames before loading into operational tables.
Only processes DataFrames that were actually extracted (non-None).
Returns cleaned DataFrames and per-reason drop stats.
"""

import pandas as pd
import re
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

TODAY = datetime.now(timezone.utc).replace(tzinfo=None)


# ── Clean ─────────────────────────────────────────────────────────────────────

def clean_books(df: pd.DataFrame):
    stats = {"input_rows": len(df), "dropped": {}}

    for col in ["Title", "Authors", "Category"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "Category" in df.columns:
        df["Category"] = df["Category"].fillna("Unknown").astype(str).str.strip().str.title()

    if "isbn" in df.columns:
        def _clean_isbn(x):
            if pd.isna(x):
                return None
            x = str(x).replace("-", "").replace(" ", "").strip()
            return x if (x.isdigit() and len(x) in (10, 13)) else None
        df["isbn"] = df["isbn"].apply(_clean_isbn)

    before = len(df)
    df = df[df["Title"].notna() & (df["Title"] != "") & (df["Title"] != "None")]
    stats["dropped"]["null_title"] = before - len(df)

    placeholder_authors = {"n/a", "none", "unknown_author_##", ""}
    if "Authors" in df.columns:
        df["Authors"] = df["Authors"].apply(
            lambda x: "Unknown" if str(x).strip().lower() in placeholder_authors else x
        )
        df["Authors"] = df["Authors"].fillna("Unknown")

    before = len(df)
    df = df.drop_duplicates()
    stats["dropped"]["duplicates"] = before - len(df)

    stats["output_rows"] = len(df)
    print(f"[Transform] Books cleaned  : {stats['input_rows']} -> {stats['output_rows']} rows ({stats['input_rows'] - stats['output_rows']} dropped)")
    return df.reset_index(drop=True), stats


def _parse_date(val) -> pd.Timestamp | None:
    if pd.isna(val) or str(val).strip() == "":
        return None
    val = str(val).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return pd.to_datetime(val, format=fmt)
        except ValueError:
            pass
    try:
        return pd.to_datetime(val)
    except Exception:
        return None


def clean_borrowers(df: pd.DataFrame):
    stats = {"input_rows": len(df), "dropped": {}}

    df["borrower_name"] = df["borrower_name"].astype(str).str.strip()
    df["borrower_name"] = df["borrower_name"].str.replace(r"\s+", " ", regex=True)

    before = len(df)
    df = df[df["borrower_name"].notna() & (df["borrower_name"] != "") & (df["borrower_name"] != "None")]
    df = df[df["email"].notna() & (df["email"] != "") & (df["email"] != "None")]
    stats["dropped"]["missing_name_or_email"] = before - len(df)

    before = len(df)
    email_regex = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    df = df[df["email"].apply(lambda e: bool(email_regex.match(str(e).strip())))]
    stats["dropped"]["invalid_email"] = before - len(df)

    before = len(df)
    df["phone"] = df["phone"].astype(str).str.replace(r"\D", "", regex=True)
    df = df[df["phone"].str.len() == 10]
    stats["dropped"]["invalid_phone"] = before - len(df)

    before = len(df)
    df = df.drop_duplicates(subset=["email"])
    stats["dropped"]["duplicate_email"] = before - len(df)

    stats["output_rows"] = len(df)
    print(f"[Transform] Borrowers clean: {stats['input_rows']} -> {stats['output_rows']} rows ({stats['input_rows'] - stats['output_rows']} dropped)")
    return df.reset_index(drop=True), stats


def clean_transactions(df: pd.DataFrame, valid_book_ids: set, valid_borrower_ids: set):
    stats = {"input_rows": len(df), "dropped": {}}

    before = len(df)
    df = df[df["book_id"].notna() & df["borrower_id"].notna()]
    stats["dropped"]["missing_ids"] = before - len(df)

    df["book_id"] = df["book_id"].astype(int)
    df["borrower_id"] = df["borrower_id"].astype(int)

    before = len(df)
    df = df[df["book_id"].isin(valid_book_ids)]
    df = df[df["borrower_id"].isin(valid_borrower_ids)]
    stats["dropped"]["invalid_fk"] = before - len(df)

    before = len(df)
    df["borrow_date"] = df["borrow_date"].apply(_parse_date)
    df = df[df["borrow_date"].notna()]
    stats["dropped"]["unparseable_date"] = before - len(df)

    before = len(df)
    df = df[df["borrow_date"] <= TODAY]
    stats["dropped"]["future_date"] = before - len(df)

    df["return_date"] = df["return_date"].apply(_parse_date)

    before = len(df)
    invalid_return = df["return_date"].notna() & (df["return_date"] < df["borrow_date"])
    df = df[~invalid_return]
    stats["dropped"]["return_before_borrow"] = before - len(df)

    before = len(df)
    df = df.drop_duplicates(subset=["book_id", "borrower_id", "borrow_date"])
    stats["dropped"]["duplicates"] = before - len(df)

    stats["output_rows"] = len(df)
    print(f"[Transform] Transactions cl: {stats['input_rows']} -> {stats['output_rows']} rows ({stats['input_rows'] - stats['output_rows']} dropped)")
    return df.reset_index(drop=True), stats


# ── Run ───────────────────────────────────────────────────────────────────────

def run(extracted: dict) -> dict:
    print("\n" + "=" * 50)
    print("TRANSFORM")
    print("=" * 50)

    books_clean = borrowers_clean = transactions_clean = None
    transform_stats = {}

    if extracted.get("books_csv") is not None:
        books_clean, transform_stats["books"] = clean_books(extracted["books_csv"])

    if extracted.get("borrowers_csv") is not None:
        borrowers_clean, transform_stats["borrowers"] = clean_borrowers(extracted["borrowers_csv"])

    if extracted.get("transactions_csv") is not None:
        if books_clean is not None:
            valid_book_ids = set(books_clean["book_id"].dropna().astype(int).tolist())
        else:
            from database.database import SessionLocal
            from database import models
            db = SessionLocal()
            try:
                valid_book_ids = {r.book_id for r in db.query(models.Book.book_id).all()}
            finally:
                db.close()
            print(f"[Transform] valid_book_ids from DB : {len(valid_book_ids)}")

        if extracted.get("borrowers_csv") is not None:
            valid_borrower_ids = set(extracted["borrowers_csv"]["borrower_id"].dropna().astype(int).tolist())
        else:
            from database.database import SessionLocal
            from database import models
            db = SessionLocal()
            try:
                valid_borrower_ids = {r.borrower_id for r in db.query(models.Borrower.borrower_id).all()}
            finally:
                db.close()
            print(f"[Transform] valid_borrower_ids from DB : {len(valid_borrower_ids)}")

        transactions_clean, transform_stats["transactions"] = clean_transactions(
            extracted["transactions_csv"].copy(), valid_book_ids, valid_borrower_ids
        )

    return {
        "books_clean":        books_clean,
        "borrowers_clean":    borrowers_clean,
        "transactions_clean": transactions_clean,
        "transform_stats":    transform_stats,
    }
