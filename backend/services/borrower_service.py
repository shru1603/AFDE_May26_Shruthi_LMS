from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend import crud, schemas


def get_all_borrowers(db: Session):
    return crud.get_borrowers(db)


def create_borrower(db: Session, borrower: schemas.BorrowerCreate):
    return crud.create_borrower(db, borrower)


def update_borrower(db: Session, borrower_id: int, borrower: schemas.BorrowerUpdate):
    updated = crud.update_borrower(db, borrower_id, borrower)
    if not updated:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return updated


def delete_borrower(db: Session, borrower_id: int):
    if crud.count_active_borrows_for_borrower(db, borrower_id) > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete: borrower has books not yet returned.",
        )
    borrower = crud.delete_borrower(db, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return borrower
