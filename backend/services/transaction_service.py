from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import models
from backend import crud, schemas


def get_all_transactions(db: Session):
    return crud.get_transactions(db)


def borrow_book(db: Session, borrow: schemas.BorrowRequest):
    book = crud.get_book(db, borrow.book_id)
    if not book or book.availability_status != "available":
        raise HTTPException(status_code=400, detail="Book is not available")

    borrower = crud.get_borrower(db, borrow.borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    transaction = models.Transaction(
        book_id=borrow.book_id,
        borrower_id=borrow.borrower_id,
        book_title=book.title,
        borrower_name=borrower.borrower_name,
        borrow_date=datetime.now(timezone.utc),
    )
    book.availability_status = "borrowed"
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def return_book(db: Session, return_req: schemas.ReturnRequest):
    transaction = crud.get_active_transaction(db, return_req.transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Active transaction not found")

    transaction.return_date = datetime.now(timezone.utc)
    book = crud.get_book(db, transaction.book_id)
    if book:
        book.availability_status = "available"
    db.commit()
    db.refresh(transaction)
    return transaction
