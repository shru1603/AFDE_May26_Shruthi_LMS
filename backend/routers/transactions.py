from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from backend import schemas
from backend.services import transaction_service, book_service
from database.database import get_db

router = APIRouter(tags=["Transactions"])


@router.get("/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return transaction_service.get_all_transactions(db)


@router.post("/borrow", response_model=schemas.TransactionResponse, status_code=201)
def borrow_book(borrow: schemas.BorrowRequest, db: Session = Depends(get_db)):
    return transaction_service.borrow_book(db, borrow)


@router.post("/return", response_model=schemas.TransactionResponse)
def return_book(return_req: schemas.ReturnRequest, db: Session = Depends(get_db)):
    return transaction_service.return_book(db, return_req)


@router.get("/search", response_model=List[schemas.BookResponse])
def search_books(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return book_service.search_books(db, q)
