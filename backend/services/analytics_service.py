from sqlalchemy.orm import Session
from database import models


def get_popular_books(db: Session, limit: int = 10):
    return (
        db.query(models.AnalyticsPopularBooks)
        .order_by(models.AnalyticsPopularBooks.borrow_count.desc())
        .limit(limit)
        .all()
    )


def get_category_stats(db: Session):
    return (
        db.query(models.AnalyticsCategoryStats)
        .order_by(models.AnalyticsCategoryStats.borrow_count.desc())
        .all()
    )


def get_monthly_trends(db: Session):
    return (
        db.query(models.AnalyticsMonthlyTrends)
        .order_by(
            models.AnalyticsMonthlyTrends.year,
            models.AnalyticsMonthlyTrends.month,
        )
        .all()
    )


def get_overdue(db: Session):
    return (
        db.query(models.AnalyticsOverdue)
        .order_by(models.AnalyticsOverdue.days_overdue.desc())
        .all()
    )
