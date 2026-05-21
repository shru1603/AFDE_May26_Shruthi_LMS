"""
etl/extract.py

Extract step: reads raw CSV files and live DB transactions.
Returns raw DataFrames — no cleaning done here.

Run from project root:
    python -m etl.pipeline
"""

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal
from database import models

BOOKS_CSV = "datasets/books.csv"
BORROWERS_CSV = "datasets/borrowers.csv"
TRANSACTIONS_CSV = "datasets/transactions.csv"


def extract_books() -> pd.DataFrame:
    df = pd.read_csv(BOOKS_CSV)
    print(f"[Extract] Books CSV        : {len(df)} rows")
    return df


def extract_borrowers() -> pd.DataFrame:
    df = pd.read_csv(BORROWERS_CSV)
    print(f"[Extract] Borrowers CSV    : {len(df)} rows")
    return df


def extract_transactions_csv() -> pd.DataFrame:
    df = pd.read_csv(TRANSACTIONS_CSV)
    print(f"[Extract] Transactions CSV : {len(df)} rows")
    return df


def extract_transactions_db() -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(models.Transaction).all()
        data = [
            {
                "transaction_id": r.transaction_id,
                "book_id": r.book_id,
                "borrower_id": r.borrower_id,
                "book_title": r.book_title,
                "borrower_name": r.borrower_name,
                "borrow_date": r.borrow_date,
                "return_date": r.return_date,
            }
            for r in rows
        ]
        df = pd.DataFrame(data)
        print(f"[Extract] Transactions DB  : {len(df)} rows")
        return df
    finally:
        db.close()


def extract_books_db() -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(models.Book).all()
        data = [
            {
                "book_id": r.book_id,
                "title": r.title,
                "author": r.author,
                "category": r.category,
                "isbn": r.isbn,
            }
            for r in rows
        ]
        df = pd.DataFrame(data)
        print(f"[Extract] Books DB         : {len(df)} rows")
        return df
    finally:
        db.close()


def run() -> dict:
    print("\n" + "=" * 50)
    print("EXTRACT")
    print("=" * 50)
    return {
        "books_csv": extract_books(),
        "borrowers_csv": extract_borrowers(),
        "transactions_csv": extract_transactions_csv(),
        "transactions_db": extract_transactions_db(),
        "books_db": extract_books_db(),
    }
