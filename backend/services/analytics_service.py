from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from datetime import datetime, timedelta

from database import models

OVERDUE_DAYS = 14


def get_summary(db: Session):
    total_books       = db.query(func.count(models.Book.book_id)).scalar() or 0
    total_borrowers   = db.query(func.count(models.Borrower.borrower_id)).scalar() or 0
    total_transactions= db.query(func.count(models.Transaction.transaction_id)).scalar() or 0
    available         = db.query(func.count(models.Book.book_id)).filter(models.Book.availability_status == "available").scalar() or 0
    borrowed          = db.query(func.count(models.Book.book_id)).filter(models.Book.availability_status == "borrowed").scalar() or 0

    threshold = datetime.now() - timedelta(days=OVERDUE_DAYS)
    overdue_count = db.query(func.count(models.Transaction.transaction_id)).filter(
        models.Transaction.return_date.is_(None),
        models.Transaction.borrow_date < threshold,
    ).scalar() or 0

    return {
        "total_books":        total_books,
        "total_borrowers":    total_borrowers,
        "total_transactions": total_transactions,
        "available":          available,
        "borrowed":           borrowed,
        "overdue_count":      overdue_count,
    }


def get_popular_books(db: Session, limit: int = 10):
    rows = (
        db.query(
            models.Book.book_id,
            models.Book.title,
            models.Book.author,
            models.Book.category,
            models.Book.isbn,
            func.count(models.Transaction.transaction_id).label("borrow_count"),
        )
        .join(models.Transaction, models.Transaction.book_id == models.Book.book_id)
        .group_by(models.Book.book_id)
        .order_by(desc("borrow_count"))
        .limit(limit)
        .all()
    )
    return [
        {
            "book_id": r.book_id, "title": r.title, "author": r.author,
            "category": r.category, "isbn": r.isbn, "borrow_count": r.borrow_count,
        }
        for r in rows
    ]


def get_category_stats(db: Session):
    borrow_counts = {
        r.category: r.cnt
        for r in db.query(
            models.Book.category,
            func.count(models.Transaction.transaction_id).label("cnt"),
        )
        .join(models.Transaction, models.Transaction.book_id == models.Book.book_id)
        .group_by(models.Book.category)
        .all()
    }

    book_counts = {
        r.category: r.cnt
        for r in db.query(
            models.Book.category,
            func.count(models.Book.book_id).label("cnt"),
        )
        .group_by(models.Book.category)
        .all()
    }

    all_categories = set(borrow_counts) | set(book_counts)
    result = [
        {
            "category":    cat,
            "borrow_count": borrow_counts.get(cat, 0),
            "book_count":   book_counts.get(cat, 0),
        }
        for cat in all_categories
    ]
    return sorted(result, key=lambda x: x["borrow_count"], reverse=True)


def get_monthly_trends(db: Session):
    merged = {}

    for r in (
        db.query(
            extract("year",  models.Transaction.borrow_date).label("yr"),
            extract("month", models.Transaction.borrow_date).label("mo"),
            func.count(models.Transaction.transaction_id).label("cnt"),
        )
        .filter(models.Transaction.borrow_date.isnot(None))
        .group_by("yr", "mo")
        .all()
    ):
        key = (int(r.yr), int(r.mo))
        merged[key] = {"year": int(r.yr), "month": int(r.mo), "borrow_count": r.cnt, "return_count": 0}

    for r in (
        db.query(
            extract("year",  models.Transaction.return_date).label("yr"),
            extract("month", models.Transaction.return_date).label("mo"),
            func.count(models.Transaction.transaction_id).label("cnt"),
        )
        .filter(models.Transaction.return_date.isnot(None))
        .group_by("yr", "mo")
        .all()
    ):
        key = (int(r.yr), int(r.mo))
        if key in merged:
            merged[key]["return_count"] += r.cnt
        else:
            merged[key] = {"year": int(r.yr), "month": int(r.mo), "borrow_count": 0, "return_count": r.cnt}

    return sorted(merged.values(), key=lambda x: (x["year"], x["month"]))


def get_overdue(db: Session):
    threshold = datetime.now() - timedelta(days=OVERDUE_DAYS)
    rows = (
        db.query(models.Transaction, models.Book, models.Borrower)
        .outerjoin(models.Book,     models.Transaction.book_id     == models.Book.book_id)
        .outerjoin(models.Borrower, models.Transaction.borrower_id == models.Borrower.borrower_id)
        .filter(models.Transaction.return_date.is_(None))
        .filter(models.Transaction.borrow_date < threshold)
        .all()
    )
    result = []
    for tx, book, borrower in rows:
        result.append({
            "transaction_id": tx.transaction_id,
            "book_id":        tx.book_id,
            "borrower_id":    tx.borrower_id,
            "book_title":     tx.book_title or (book.title if book else None),
            "borrower_name":  tx.borrower_name or (borrower.borrower_name if borrower else None),
            "borrow_date":    tx.borrow_date,
            "days_overdue":   (datetime.now() - tx.borrow_date).days,
        })
    return sorted(result, key=lambda x: x["days_overdue"], reverse=True)
