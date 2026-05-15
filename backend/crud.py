from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone

from database import models
import schemas


# ── Book CRUD ─────────────────────────────────────────────────────────────────

def get_books(db: Session):
    return db.query(models.Book).all()


def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.book_id == book_id).first()


def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(
        title=book.title,
        author=book.author,
        category=book.category,
        isbn=book.isbn,
        availability_status="available",
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book: schemas.BookUpdate):
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    for field, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    db.delete(db_book)
    db.commit()
    return db_book


# ── Borrower CRUD ─────────────────────────────────────────────────────────────

def get_borrowers(db: Session):
    return db.query(models.Borrower).all()


def get_borrower(db: Session, borrower_id: int):
    return db.query(models.Borrower).filter(
        models.Borrower.borrower_id == borrower_id
    ).first()


def create_borrower(db: Session, borrower: schemas.BorrowerCreate):
    db_borrower = models.Borrower(
        borrower_name=borrower.borrower_name,
        email=borrower.email,
        phone=borrower.phone,
    )
    db.add(db_borrower)
    db.commit()
    db.refresh(db_borrower)
    return db_borrower


def update_borrower(db: Session, borrower_id: int, borrower: schemas.BorrowerUpdate):
    db_borrower = get_borrower(db, borrower_id)
    if not db_borrower:
        return None
    for field, value in borrower.model_dump(exclude_unset=True).items():
        setattr(db_borrower, field, value)
    db.commit()
    db.refresh(db_borrower)
    return db_borrower


def delete_borrower(db: Session, borrower_id: int):
    db_borrower = get_borrower(db, borrower_id)
    if not db_borrower:
        return None
    db.delete(db_borrower)
    db.commit()
    return db_borrower


# ── Transaction CRUD ──────────────────────────────────────────────────────────

def get_transactions(db: Session):
    return db.query(models.Transaction).all()


def borrow_book(db: Session, borrow: schemas.BorrowRequest):
    book = get_book(db, borrow.book_id)
    if not book or book.availability_status != "available":
        return None, "Book is not available"

    borrower = get_borrower(db, borrow.borrower_id)
    if not borrower:
        return None, "Borrower not found"

    transaction = models.Transaction(
        book_id=borrow.book_id,
        borrower_id=borrow.borrower_id,
        borrow_date=datetime.now(timezone.utc),
    )
    book.availability_status = "borrowed"
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction, None


def return_book(db: Session, return_req: schemas.ReturnRequest):
    transaction = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.transaction_id == return_req.transaction_id,
            models.Transaction.return_date == None,
        )
        .first()
    )
    if not transaction:
        return None, "Active transaction not found"

    transaction.return_date = datetime.now(timezone.utc)
    book = get_book(db, transaction.book_id)
    if book:
        book.availability_status = "available"
    db.commit()
    db.refresh(transaction)
    return transaction, None


# ── Search ────────────────────────────────────────────────────────────────────

def search_books(db: Session, query: str):
    keyword = f"%{query}%"
    return (
        db.query(models.Book)
        .filter(
            or_(
                models.Book.title.ilike(keyword),
                models.Book.author.ilike(keyword),
                models.Book.category.ilike(keyword),
                models.Book.isbn.ilike(keyword),
            )
        )
        .all()
    )
