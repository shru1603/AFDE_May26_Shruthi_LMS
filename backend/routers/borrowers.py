from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend import schemas
from backend.services import borrower_service
from database.database import get_db

router = APIRouter(prefix="/borrowers", tags=["Borrowers"])


@router.get("/", response_model=List[schemas.BorrowerResponse])
def get_all_borrowers(db: Session = Depends(get_db)):
    return borrower_service.get_all_borrowers(db)


@router.post("/", response_model=schemas.BorrowerResponse, status_code=201)
def create_borrower(borrower: schemas.BorrowerCreate, db: Session = Depends(get_db)):
    return borrower_service.create_borrower(db, borrower)


@router.put("/{borrower_id}", response_model=schemas.BorrowerResponse)
def update_borrower(borrower_id: int, borrower: schemas.BorrowerUpdate, db: Session = Depends(get_db)):
    return borrower_service.update_borrower(db, borrower_id, borrower)


@router.delete("/{borrower_id}", response_model=schemas.BorrowerResponse)
def delete_borrower(borrower_id: int, db: Session = Depends(get_db)):
    return borrower_service.delete_borrower(db, borrower_id)
