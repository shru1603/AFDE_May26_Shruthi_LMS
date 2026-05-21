"""
generate_raw_datasets.py

Generates intentionally messy/uncleaned books.csv (150 rows from BooksDataset.csv),
borrowers.csv, and transactions.csv into the datasets/ folder.
These simulate real-world raw data problems that the ETL transform step will clean.

Run from project root:
    python -m etl.generate_raw_datasets
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import os

random.seed(42)

RAW_BOOKS_FILE = "datasets/BooksDataset.csv"
OUT_BOOKS = "datasets/books.csv"
OUT_BORROWERS = "datasets/borrowers.csv"
OUT_TRANSACTIONS = "datasets/transactions.csv"

TODAY = datetime.today()
SIX_MONTHS_AGO = TODAY - timedelta(days=180)


# ── Helpers ───────────────────────────────────────────────────────────────────

def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def messy_date(dt: datetime) -> str:
    """Return date in one of three formats to simulate inconsistency."""
    fmt = random.choice(["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"])
    return dt.strftime(fmt)


# ── Extract 150 Books from BooksDataset.csv ───────────────────────────────────

def generate_books() -> pd.DataFrame:
    df = pd.read_csv(RAW_BOOKS_FILE)
    df = df.head(150).copy()

    # ── Dirty: mixed case in Category ─────────────────────────────────────────
    for i in [2, 5, 10, 15, 20, 25]:
        if pd.notna(df.at[i, "Category"]):
            df.at[i, "Category"] = df.at[i, "Category"].upper()
    for i in [3, 7, 12, 18, 22]:
        if pd.notna(df.at[i, "Category"]):
            df.at[i, "Category"] = df.at[i, "Category"].lower()

    # ── Dirty: extra whitespace in Title and Authors ───────────────────────────
    for i in [1, 8, 14, 30, 45]:
        df.at[i, "Title"] = "  " + str(df.at[i, "Title"]) + "  "
    for i in [4, 11, 19, 35]:
        df.at[i, "Authors"] = "  " + str(df.at[i, "Authors"]) + "  "

    # ── Dirty: garbled author names ────────────────────────────────────────────
    df.at[6,  "Authors"] = "SMITH, JOHN"
    df.at[13, "Authors"] = "jane doe; mark lee"
    df.at[27, "Authors"] = "Unknown_Author_##"
    df.at[40, "Authors"] = None
    df.at[55, "Authors"] = "N/A"

    # ── Dirty: null titles ────────────────────────────────────────────────────
    df.at[9,  "Title"] = None
    df.at[33, "Title"] = None

    # ── Dirty: messy Price values ─────────────────────────────────────────────
    df.at[16, "Price"] = "Free"
    df.at[24, "Price"] = "$12.99"
    df.at[38, "Price"] = "N/A"
    df.at[50, "Price"] = "£9.99"

    # ── Dirty: inconsistent Publish Date formats ───────────────────────────────
    df.at[20, "Publish Date"] = "15/03/2020"
    df.at[28, "Publish Date"] = "March 2019"
    df.at[42, "Publish Date"] = "2018"
    df.at[60, "Publish Date"] = None

    # ── Dirty: duplicate rows ─────────────────────────────────────────────────
    duplicates = df.iloc[[0, 5, 10, 20]].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    print(f"Books extracted     : {len(df)} rows (raw, uncleaned)")
    print(f"  Null counts:\n{df.isnull().sum()}\n")
    return df


# ── Generate Borrowers ────────────────────────────────────────────────────────

def generate_borrowers() -> pd.DataFrame:
    first_names = [
        "Aarav", "Aisha", "Arjun", "Bhavna", "Chitra", "Deepak",
        "Divya", "Farhan", "Geeta", "Harish", "Ishaan", "Jaya",
        "Karan", "Lakshmi", "Manoj", "Meera", "Naveen", "Neha",
        "Pooja", "Prakash", "Priya", "Rahul", "Rajesh", "Ritu",
        "Rohan", "Sana", "Sneha", "Suresh", "Vikram", "Zara",
    ]
    last_names = [
        "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar",
        "Nair", "Reddy", "Joshi", "Mehta", "Iyer", "Rao",
    ]

    clean_rows = []
    for i in range(1, 31):
        first = first_names[i - 1]
        last = random.choice(last_names)
        clean_rows.append({
            "borrower_id": i,
            "borrower_name": f"{first} {last}",
            "email": f"{first.lower()}.{last.lower()}{i}@email.com",
            "phone": "9" + "".join([str(random.randint(0, 9)) for _ in range(9)]),
        })

    # ── Dirty rows ────────────────────────────────────────────────────────────

    dirty_rows = [
        # Missing borrower_name
        {"borrower_id": 31, "borrower_name": None,
         "email": "unknown31@email.com", "phone": "9876543201"},

        # Missing email
        {"borrower_id": 32, "borrower_name": "  Ravi Shankar  ",
         "email": None, "phone": "9123456789"},

        # Missing phone
        {"borrower_id": 33, "borrower_name": "Anita Desai",
         "email": "anita.desai@email.com", "phone": None},

        # Invalid email — no @
        {"borrower_id": 34, "borrower_name": "Kabir Malhotra",
         "email": "kabirmalhotra.email.com", "phone": "9988776655"},

        # Invalid email — missing domain
        {"borrower_id": 35, "borrower_name": "Sunita Roy",
         "email": "sunita@", "phone": "9876001234"},

        # Phone too short (8 digits)
        {"borrower_id": 36, "borrower_name": "Tarun Bhat",
         "email": "tarun.bhat@email.com", "phone": "98765432"},

        # Phone too long (11 digits)
        {"borrower_id": 37, "borrower_name": "Meghna Pillai",
         "email": "meghna.pillai@email.com", "phone": "98765432101"},

        # Phone with dashes
        {"borrower_id": 38, "borrower_name": "Arun Nair",
         "email": "arun.nair@email.com", "phone": "98-765-4321"},

        # Extra whitespace in name
        {"borrower_id": 39, "borrower_name": "  Pooja   Tiwari  ",
         "email": "pooja.tiwari@email.com", "phone": "9001234567"},

        # Both name and email missing
        {"borrower_id": 40, "borrower_name": None,
         "email": None, "phone": "9123456700"},
    ]

    # ── Duplicate rows (exact copies of existing clean records) ───────────────
    duplicates = [
        clean_rows[0].copy(),   # duplicate of borrower_id 1
        clean_rows[4].copy(),   # duplicate of borrower_id 5
        clean_rows[9].copy(),   # duplicate of borrower_id 10
        dirty_rows[0].copy(),   # duplicate of dirty row
    ]

    all_rows = clean_rows + dirty_rows + duplicates
    df = pd.DataFrame(all_rows)

    print(f"Borrowers generated : {len(df)} rows")
    print(f"  Clean rows        : {len(clean_rows)}")
    print(f"  Dirty rows        : {len(dirty_rows)}")
    print(f"  Duplicate rows    : {len(duplicates)}")
    print(f"  Null counts:\n{df.isnull().sum()}\n")
    return df


# ── Generate Transactions ─────────────────────────────────────────────────────

def generate_transactions() -> pd.DataFrame:
    # Valid book_ids: 1–150 (rows from BooksDataset.csv)
    # Valid borrower_ids: 1–30 (clean borrowers)

    clean_rows = []
    tx_id = 1

    for _ in range(200):
        book_id = random.randint(1, 150)
        borrower_id = random.randint(1, 30)
        borrow_date = random_date(SIX_MONTHS_AGO, TODAY - timedelta(days=1))

        roll = random.random()

        if roll < 0.50:
            # Returned
            days_kept = random.randint(3, 20)
            return_date = borrow_date + timedelta(days=days_kept)
            if return_date > TODAY:
                return_date = TODAY - timedelta(days=1)
            clean_rows.append({
                "transaction_id": tx_id,
                "book_id": book_id,
                "borrower_id": borrower_id,
                "borrow_date": messy_date(borrow_date),
                "return_date": messy_date(return_date),
            })
        elif roll < 0.75:
            # Active — within 14 days
            borrow_date = TODAY - timedelta(days=random.randint(1, 13))
            clean_rows.append({
                "transaction_id": tx_id,
                "book_id": book_id,
                "borrower_id": borrower_id,
                "borrow_date": messy_date(borrow_date),
                "return_date": None,
            })
        else:
            # Overdue — more than 14 days, not returned
            borrow_date = TODAY - timedelta(days=random.randint(15, 90))
            clean_rows.append({
                "transaction_id": tx_id,
                "book_id": book_id,
                "borrower_id": borrower_id,
                "borrow_date": messy_date(borrow_date),
                "return_date": None,
            })

        tx_id += 1

    # ── Dirty rows ────────────────────────────────────────────────────────────

    dirty_rows = [
        # Missing borrow_date
        {"transaction_id": tx_id + 1, "book_id": 10,
         "borrower_id": 5, "borrow_date": None, "return_date": None},

        # Missing book_id
        {"transaction_id": tx_id + 2, "book_id": None,
         "borrower_id": 8, "borrow_date": "2025-01-15", "return_date": None},

        # Missing borrower_id
        {"transaction_id": tx_id + 3, "book_id": 22,
         "borrower_id": None, "borrow_date": "2025-02-10", "return_date": "2025-02-20"},

        # Return date BEFORE borrow date (invalid)
        {"transaction_id": tx_id + 4, "book_id": 35,
         "borrower_id": 12, "borrow_date": "2025-03-20", "return_date": "2025-03-01"},

        # book_id out of range (does not exist in 1–150)
        {"transaction_id": tx_id + 5, "book_id": 999,
         "borrower_id": 7, "borrow_date": "2025-01-05", "return_date": None},

        # borrower_id out of range (does not exist in 1–30)
        {"transaction_id": tx_id + 6, "book_id": 45,
         "borrower_id": 999, "borrow_date": "2025-02-14", "return_date": None},

        # Both book_id and borrower_id missing
        {"transaction_id": tx_id + 7, "book_id": None,
         "borrower_id": None, "borrow_date": "2025-03-01", "return_date": None},

        # borrow_date in wrong format (text)
        {"transaction_id": tx_id + 8, "book_id": 60,
         "borrower_id": 15, "borrow_date": "March 5 2025", "return_date": None},

        # Future borrow_date (invalid)
        {"transaction_id": tx_id + 9, "book_id": 80,
         "borrower_id": 20, "borrow_date": (TODAY + timedelta(days=30)).strftime("%Y-%m-%d"),
         "return_date": None},

        # return_date missing but borrow_date very old (clearly overdue)
        {"transaction_id": tx_id + 10, "book_id": 100,
         "borrower_id": 25, "borrow_date": "2024-01-01", "return_date": None},
    ]

    # ── Duplicate rows ────────────────────────────────────────────────────────
    duplicates = [
        clean_rows[0].copy(),
        clean_rows[10].copy(),
        clean_rows[25].copy(),
        clean_rows[50].copy(),
        dirty_rows[0].copy(),
    ]

    all_rows = clean_rows + dirty_rows + duplicates
    df = pd.DataFrame(all_rows)

    returned = df[df["return_date"].notna() & (df["return_date"] != "")].shape[0]
    no_return = df[df["return_date"].isna() | (df["return_date"] == "")].shape[0]

    print(f"Transactions generated : {len(df)} rows")
    print(f"  Clean rows           : {len(clean_rows)}")
    print(f"  Dirty rows           : {len(dirty_rows)}")
    print(f"  Duplicate rows       : {len(duplicates)}")
    print(f"  With return_date     : {returned}")
    print(f"  Without return_date  : {no_return}")
    print(f"  Null counts:\n{df.isnull().sum()}\n")
    return df


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs("datasets", exist_ok=True)

    print("=" * 50)
    print("Generating raw (uncleaned) datasets")
    print("=" * 50 + "\n")

    books = generate_books()
    borrowers = generate_borrowers()
    transactions = generate_transactions()

    books.to_csv(OUT_BOOKS, index=False)
    borrowers.to_csv(OUT_BORROWERS, index=False)
    transactions.to_csv(OUT_TRANSACTIONS, index=False)

    print("=" * 50)
    print("Raw datasets saved:")
    print(f"  {OUT_BOOKS}        (150 rows from BooksDataset.csv)")
    print(f"  {OUT_BORROWERS}")
    print(f"  {OUT_TRANSACTIONS}")
    print("=" * 50)


if __name__ == "__main__":
    main()
