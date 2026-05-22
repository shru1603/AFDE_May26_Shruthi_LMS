from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from backend.schemas import (
    PopularBookResponse,
    CategoryStatResponse,
    MonthlyTrendResponse,
    OverdueResponse,
)
from backend.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return analytics_service.get_summary(db)


@router.get("/popular-books", response_model=List[PopularBookResponse])
def popular_books(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return analytics_service.get_popular_books(db, limit=limit)


@router.get("/category-stats", response_model=List[CategoryStatResponse])
def category_stats(db: Session = Depends(get_db)):
    return analytics_service.get_category_stats(db)


@router.get("/monthly-trends", response_model=List[MonthlyTrendResponse])
def monthly_trends(db: Session = Depends(get_db)):
    return analytics_service.get_monthly_trends(db)


@router.get("/overdue", response_model=List[OverdueResponse])
def overdue_books(db: Session = Depends(get_db)):
    return analytics_service.get_overdue(db)
