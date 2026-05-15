from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from backend import crud, schemas
from database.database import get_db

router = APIRouter(tags=["Transactions"])


@router.get("/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return crud.get_transactions(db)


@router.post("/borrow", response_model=schemas.TransactionResponse, status_code=201)
def borrow_book(borrow: schemas.BorrowRequest, db: Session = Depends(get_db)):
    transaction, error = crud.borrow_book(db, borrow)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return transaction


@router.post("/return", response_model=schemas.TransactionResponse)
def return_book(return_req: schemas.ReturnRequest, db: Session = Depends(get_db)):
    transaction, error = crud.return_book(db, return_req)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return transaction


@router.get("/search", response_model=List[schemas.BookResponse])
def search_books(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return crud.search_books(db, q)
