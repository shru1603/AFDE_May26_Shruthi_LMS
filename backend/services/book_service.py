from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend import crud, schemas


def get_all_books(db: Session):
    return crud.get_books(db)


def get_book(db: Session, book_id: int):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def create_book(db: Session, book: schemas.BookCreate):
    return crud.create_book(db, book)


def update_book(db: Session, book_id: int, book: schemas.BookUpdate):
    updated = crud.update_book(db, book_id, book)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated


def delete_book(db: Session, book_id: int):
    if crud.count_active_borrows_for_book(db, book_id) > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete: book is currently borrowed. Return it first.",
        )
    book = crud.delete_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def search_books(db: Session, query: str):
    return crud.search_books(db, query)
