from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend import schemas
from backend.services import book_service
from database.database import get_db

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=List[schemas.BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    return book_service.get_all_books(db)


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return book_service.get_book(db, book_id)


@router.post("/", response_model=schemas.BookResponse, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return book_service.create_book(db, book)


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    return book_service.update_book(db, book_id, book)


@router.delete("/{book_id}", response_model=schemas.BookResponse)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return book_service.delete_book(db, book_id)
