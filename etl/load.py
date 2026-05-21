"""
etl/load.py

Load step: writes aggregated DataFrames into analytics tables.
Each run does a full replace (truncate + insert) so tables always
reflect the latest ETL run.

Run from project root:
    python -m etl.pipeline
"""

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal
from database import models


def _clear_table(db, model):
    db.query(model).delete()
    db.commit()


def load_popular_books(db, df: pd.DataFrame):
    _clear_table(db, models.AnalyticsPopularBooks)
    for _, row in df.iterrows():
        isbn_val = row.get("isbn")
        record = models.AnalyticsPopularBooks(
            book_id=int(row["book_id"]),
            title=str(row.get("title", "") or ""),
            author=str(row.get("author", "") or ""),
            category=str(row.get("category", "") or ""),
            isbn=str(isbn_val) if pd.notna(isbn_val) else None,
            borrow_count=int(row["borrow_count"]),
        )
        db.add(record)
    db.commit()
    print(f"[Load] Popular books  : {len(df)} rows written")


def load_category_stats(db, df: pd.DataFrame):
    _clear_table(db, models.AnalyticsCategoryStats)
    for _, row in df.iterrows():
        book_count = row.get("book_count", 0)
        record = models.AnalyticsCategoryStats(
            category=str(row["category"]),
            borrow_count=int(row["borrow_count"]),
            book_count=int(book_count) if pd.notna(book_count) else 0,
        )
        db.add(record)
    db.commit()
    print(f"[Load] Category stats : {len(df)} rows written")


def load_monthly_trends(db, df: pd.DataFrame):
    _clear_table(db, models.AnalyticsMonthlyTrends)
    for _, row in df.iterrows():
        record = models.AnalyticsMonthlyTrends(
            year=int(row["year"]),
            month=int(row["month"]),
            borrow_count=int(row["borrow_count"]),
            return_count=int(row.get("return_count", 0)),
        )
        db.add(record)
    db.commit()
    print(f"[Load] Monthly trends : {len(df)} rows written")


def load_overdue(db, df: pd.DataFrame):
    _clear_table(db, models.AnalyticsOverdue)
    for _, row in df.iterrows():
        record = models.AnalyticsOverdue(
            transaction_id=int(row.get("transaction_id", 0)),
            book_id=int(row["book_id"]),
            borrower_id=int(row["borrower_id"]),
            book_title=str(row["book_title"]) if pd.notna(row.get("book_title")) else None,
            borrower_name=str(row["borrower_name"]) if pd.notna(row.get("borrower_name")) else None,
            borrow_date=row["borrow_date"],
            days_overdue=int(row["days_overdue"]),
        )
        db.add(record)
    db.commit()
    print(f"[Load] Overdue        : {len(df)} rows written")


def run(transformed: dict):
    print("\n" + "=" * 50)
    print("LOAD")
    print("=" * 50)

    db = SessionLocal()
    try:
        load_popular_books(db, transformed["popular_books"])
        load_category_stats(db, transformed["category_stats"])
        load_monthly_trends(db, transformed["monthly_trends"])
        load_overdue(db, transformed["overdue"])
    finally:
        db.close()

    print("\n[Load] All analytics tables updated successfully.")
