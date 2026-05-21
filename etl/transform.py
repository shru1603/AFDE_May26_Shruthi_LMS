"""
etl/transform.py

Transform step: cleans raw DataFrames, then aggregates into analytics tables.
Two sub-steps:
  1. clean()  — fix dirty data (nulls, formats, duplicates, invalid values)
  2. aggregate() — compute analytics summaries from clean data

Run from project root:
    python -m etl.pipeline
"""

import pandas as pd
import re
from datetime import datetime, timezone

TODAY = datetime.now(timezone.utc).replace(tzinfo=None)
OVERDUE_THRESHOLD_DAYS = 14


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


# ── Aggregate ─────────────────────────────────────────────────────────────────

def aggregate_popular_books(transactions: pd.DataFrame, books: pd.DataFrame) -> pd.DataFrame:
    """Top borrowed books ranked by borrow_count."""
    counts = (
        transactions.groupby("book_id")
        .size()
        .reset_index(name="borrow_count")
    )

    # Map book metadata from books DataFrame (CSV columns: Title/Authors/Category/isbn)
    if "Title" in books.columns:
        cols = ["book_id", "Title", "Authors", "Category"]
        if "isbn" in books.columns:
            cols.append("isbn")
        book_meta = books[cols].copy()
        book_meta = book_meta.rename(columns={"Title": "title", "Authors": "author", "Category": "category"})
    else:
        cols = ["book_id", "title", "author", "category"]
        if "isbn" in books.columns:
            cols.append("isbn")
        book_meta = books[cols].copy()

    merged = counts.merge(book_meta, on="book_id", how="left")
    merged = merged.sort_values("borrow_count", ascending=False).reset_index(drop=True)
    print(f"[Transform] Popular books  : {len(merged)} entries")
    return merged


def aggregate_category_stats(transactions: pd.DataFrame, books: pd.DataFrame) -> pd.DataFrame:
    """Borrow count and book count per category."""
    if "Title" in books.columns:
        book_meta = books[["book_id", "Category"]].rename(columns={"Category": "category"})
    else:
        book_meta = books[["book_id", "category"]]

    tx_with_cat = transactions.merge(book_meta, on="book_id", how="left")
    tx_with_cat["category"] = tx_with_cat["category"].fillna("Unknown")

    borrow_counts = (
        tx_with_cat.groupby("category")
        .size()
        .reset_index(name="borrow_count")
    )

    book_counts = (
        book_meta.groupby("category")
        .size()
        .reset_index(name="book_count")
    )

    merged = borrow_counts.merge(book_counts, on="category", how="left")
    merged = merged.sort_values("borrow_count", ascending=False).reset_index(drop=True)
    print(f"[Transform] Category stats : {len(merged)} categories")
    return merged


def aggregate_monthly_trends(transactions: pd.DataFrame) -> pd.DataFrame:
    """Borrow and return counts per calendar month."""
    df = transactions.copy()
    df["year"] = df["borrow_date"].dt.year
    df["month"] = df["borrow_date"].dt.month

    borrow_counts = (
        df.groupby(["year", "month"])
        .size()
        .reset_index(name="borrow_count")
    )

    returned = df[df["return_date"].notna()].copy()
    returned["ret_year"] = returned["return_date"].dt.year
    returned["ret_month"] = returned["return_date"].dt.month

    return_counts = (
        returned.groupby(["ret_year", "ret_month"])
        .size()
        .reset_index(name="return_count")
        .rename(columns={"ret_year": "year", "ret_month": "month"})
    )

    merged = borrow_counts.merge(return_counts, on=["year", "month"], how="left")
    merged["return_count"] = merged["return_count"].fillna(0).astype(int)
    merged = merged.sort_values(["year", "month"]).reset_index(drop=True)
    print(f"[Transform] Monthly trends : {len(merged)} months")
    return merged


def aggregate_overdue(transactions: pd.DataFrame) -> pd.DataFrame:
    """Transactions with no return_date and borrow_date older than threshold."""
    df = transactions.copy()
    active = df[df["return_date"].isna()].copy()
    active["days_overdue"] = (TODAY - active["borrow_date"]).dt.days
    overdue = active[active["days_overdue"] > OVERDUE_THRESHOLD_DAYS].copy()
    overdue = overdue.sort_values("days_overdue", ascending=False).reset_index(drop=True)
    print(f"[Transform] Overdue        : {len(overdue)} transactions")
    return overdue


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

    # Merge CSV transactions with live DB transactions
    tx_csv = extracted["transactions_csv"].copy()
    tx_db = extracted["transactions_db"].copy()

    combined_tx = pd.concat([tx_csv, tx_db], ignore_index=True)

    transactions_clean = clean_transactions(combined_tx, valid_book_ids, valid_borrower_ids)

    # Books from CSV are the authoritative source for analytics (the 150 Kaggle books).
    # The DB books table only contains manually-added entries via the API.
    books_for_agg = books_clean  # has book_id, Title, Authors, Category columns

    # --- Aggregate ---
    popular_books = aggregate_popular_books(transactions_clean, books_for_agg)
    category_stats = aggregate_category_stats(transactions_clean, books_for_agg)
    monthly_trends = aggregate_monthly_trends(transactions_clean)
    overdue = aggregate_overdue(transactions_clean)

    # Attach book title/borrower name to overdue rows using books_csv + borrowers_csv
    title_map = books_clean.set_index("book_id")["Title"].to_dict()
    name_map = dict(zip(extracted["borrowers_csv"]["borrower_id"], extracted["borrowers_csv"]["borrower_name"]))
    overdue["book_title"] = overdue["book_id"].map(title_map)
    overdue["borrower_name"] = overdue["borrower_id"].map(name_map)

    return {
        "popular_books": popular_books,
        "category_stats": category_stats,
        "monthly_trends": monthly_trends,
        "overdue": overdue,
    }
