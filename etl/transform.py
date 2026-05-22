"""
etl/transform.py

Transform step: cleans raw DataFrames before loading into operational tables.
Handles nulls, format inconsistencies, duplicates, and invalid values.

Run from project root:
    python -m etl.pipeline
"""

import pandas as pd
import re
from datetime import datetime, timezone

TODAY = datetime.now(timezone.utc).replace(tzinfo=None)


# ── Clean ─────────────────────────────────────────────────────────────────────

def clean_books(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Strip whitespace from string columns
    for col in ["Title", "Authors", "Category"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Normalize category to title case; fill missing with Unknown
    if "Category" in df.columns:
        df["Category"] = df["Category"].fillna("Unknown").astype(str).str.strip().str.title()

    # Normalize ISBN: strip dashes/spaces, keep only valid 10 or 13 digit strings
    if "isbn" in df.columns:
        def _clean_isbn(x):
            if pd.isna(x):
                return None
            x = str(x).replace("-", "").replace(" ", "").strip()
            return x if (x.isdigit() and len(x) in (10, 13)) else None
        df["isbn"] = df["isbn"].apply(_clean_isbn)

    # Drop rows with null/empty Title (can't use a book without a title)
    df = df[df["Title"].notna() & (df["Title"] != "") & (df["Title"] != "None")]

    # Replace garbled / placeholder author values with Unknown
    placeholder_authors = {"n/a", "none", "unknown_author_##", ""}
    if "Authors" in df.columns:
        df["Authors"] = df["Authors"].apply(
            lambda x: "Unknown" if str(x).strip().lower() in placeholder_authors else x
        )
        df["Authors"] = df["Authors"].fillna("Unknown")

    # Drop duplicate rows
    df = df.drop_duplicates()

    after = len(df)
    print(f"[Transform] Books cleaned  : {before} -> {after} rows ({before - after} dropped)")
    return df.reset_index(drop=True)


def _parse_date(val) -> pd.Timestamp | None:
    if pd.isna(val) or str(val).strip() == "":
        return None
    val = str(val).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return pd.to_datetime(val, format=fmt)
        except ValueError:
            pass
    try:
        return pd.to_datetime(val, infer_datetime_format=True)
    except Exception:
        return None


def clean_borrowers(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Strip whitespace from name
    df["borrower_name"] = df["borrower_name"].astype(str).str.strip()
    df["borrower_name"] = df["borrower_name"].str.replace(r"\s+", " ", regex=True)

    # Drop rows missing name or email (both required)
    df = df[df["borrower_name"].notna() & (df["borrower_name"] != "") & (df["borrower_name"] != "None")]
    df = df[df["email"].notna() & (df["email"] != "") & (df["email"] != "None")]

    # Validate email format (must contain @ and a dot after @)
    email_regex = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    df = df[df["email"].apply(lambda e: bool(email_regex.match(str(e).strip())))]

    # Normalize phone: keep digits only, require exactly 10
    df["phone"] = df["phone"].astype(str).str.replace(r"\D", "", regex=True)
    df = df[df["phone"].str.len() == 10]

    # Drop duplicates by email (primary unique identifier)
    df = df.drop_duplicates(subset=["email"])

    after = len(df)
    print(f"[Transform] Borrowers clean: {before} -> {after} rows ({before - after} dropped)")
    return df.reset_index(drop=True)


def clean_transactions(df: pd.DataFrame, valid_book_ids: set, valid_borrower_ids: set) -> pd.DataFrame:
    before = len(df)

    # Drop rows missing book_id or borrower_id
    df = df[df["book_id"].notna() & df["borrower_id"].notna()]
    df["book_id"] = df["book_id"].astype(int)
    df["borrower_id"] = df["borrower_id"].astype(int)

    # Keep only valid foreign keys
    df = df[df["book_id"].isin(valid_book_ids)]
    df = df[df["borrower_id"].isin(valid_borrower_ids)]

    # Parse borrow_date; drop rows where it cannot be parsed
    df["borrow_date"] = df["borrow_date"].apply(_parse_date)
    df = df[df["borrow_date"].notna()]

    # Drop future borrow dates
    df = df[df["borrow_date"] <= TODAY]

    # Parse return_date (nullable)
    df["return_date"] = df["return_date"].apply(_parse_date)

    # Drop rows where return_date is before borrow_date
    invalid_return = df["return_date"].notna() & (df["return_date"] < df["borrow_date"])
    df = df[~invalid_return]

    # Drop duplicate transactions (same book_id + borrower_id + borrow_date)
    df = df.drop_duplicates(subset=["book_id", "borrower_id", "borrow_date"])

    after = len(df)
    print(f"[Transform] Transactions cl: {before} -> {after} rows ({before - after} dropped)")
    return df.reset_index(drop=True)


# ── Run ───────────────────────────────────────────────────────────────────────

def run(extracted: dict) -> dict:
    print("\n" + "=" * 50)
    print("TRANSFORM")
    print("=" * 50)

    # --- Clean ---
    books_clean = clean_books(extracted["books_csv"])
    borrowers_clean = clean_borrowers(extracted["borrowers_csv"])

    # book_id is now an explicit column in books.csv (added by generate script)
    valid_book_ids = set(books_clean["book_id"].dropna().astype(int).tolist())

    # borrower_ids from cleaned borrowers CSV
    valid_borrower_ids = set(extracted["borrowers_csv"]["borrower_id"].dropna().astype(int).tolist())

    # Only process CSV transactions — DB transactions are already in the DB
    transactions_clean = clean_transactions(
        extracted["transactions_csv"].copy(), valid_book_ids, valid_borrower_ids
    )

    return {
        "books_clean":        books_clean,
        "borrowers_clean":    borrowers_clean,
        "transactions_clean": transactions_clean,
    }
