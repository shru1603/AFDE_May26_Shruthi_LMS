"""
etl/extract.py

Extract step: reads only the CSV files that were uploaded.
Returns raw DataFrames — no cleaning done here.
"""

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BOOKS_CSV       = "datasets/books.csv"
BORROWERS_CSV   = "datasets/borrowers.csv"
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


def run(uploaded_files: set) -> dict:
    print("\n" + "=" * 50)
    print("EXTRACT")
    print("=" * 50)
    return {
        "books_csv":        extract_books()            if "books"        in uploaded_files else None,
        "borrowers_csv":    extract_borrowers()        if "borrowers"    in uploaded_files else None,
        "transactions_csv": extract_transactions_csv() if "transactions" in uploaded_files else None,
    }
