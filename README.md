# Library Management System (LMS)

## Project Information

### Project Title
Library Management System (LMS)

### Project Overview
A full-stack web application for managing a library's books, borrowers, and transactions. The system supports two roles — **Admin** and **User** — each with their own set of features. Role selection is handled on the landing page and stored in the browser's local storage; no authentication is required.

---

## Features Implemented

### Admin
- **Dashboard** — Overview of total books, available books, borrowed books, overdue count, and registered borrowers. Includes charts for top borrowed books (bar), category distribution (pie), monthly borrow/return trends (line), an overdue table, and recent transactions.
- **Book Management** — Add, edit, and delete books. Books can only be deleted when they have no active (unreturned) borrows.
- **Borrower Management** — Add, edit, and delete borrowers with email and phone validation. Borrowers can only be deleted when all their books have been returned.
- **Transactions** — View the full transaction history sorted by most recent borrow date, with book title, borrower name, borrow date, return date, and status.
- **Import (ETL)** — Upload historical CSV files (books, borrowers, transactions — any combination). The ETL pipeline transforms and cleans the data before loading it into the operational tables. After import, the dashboard and analytics reflect the combined historical and live data. A per-file row breakdown is shown after each import.

### User
- **Search Books** — Search by title, author, category, or ISBN. Filter results by category or author using dropdowns. Results update in real time.
- **Borrow / Return** — Borrow an available book using a searchable combobox (type to filter by title or author) and enter a registered borrower name. Return a book by searching and selecting the active transaction. Full transaction history is shown on the same page.

### General
- Transaction history is preserved even after a book or borrower is deleted. Book title and borrower name are stored as snapshots on the transaction record at the time of borrowing.
- Borrow and return dates are recorded automatically.
- Status (Borrowed / Returned) is derived from whether a return date exists.
- Analytics are computed live from the operational tables — no separate analytics tables.

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18.2.0 | UI framework |
| React Router DOM | 6.22.0 | Client-side routing |
| Axios | 1.6.7 | HTTP client for API calls |
| Recharts | 2.x | Analytics charts (bar, pie, line) |
| Create React App | 5.0.1 | Project setup and build tooling |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| FastAPI | 0.136.1 | REST API framework |
| Uvicorn | 0.47.0 | ASGI server |
| SQLAlchemy | 2.0.49 | ORM for database access |
| Pydantic (with email) | 2.13.4 | Request/response schema validation |
| Pandas | 3.0.3 | ETL data transformation and cleaning |
| python-multipart | 0.0.29 | CSV file upload support |

### Database
| Technology | Purpose |
|---|---|
| SQLite | Lightweight file-based relational database |

---

## Project Structure

```
AFDE_May26_Shruthi_LMS/
├── backend/
│   ├── routers/
│   │   ├── books.py           # Book CRUD endpoints
│   │   ├── borrowers.py       # Borrower CRUD endpoints
│   │   ├── transactions.py    # Transaction, borrow, return endpoints
│   │   ├── analytics.py       # Analytics endpoints (summary, charts, overdue)
│   │   └── etl.py             # CSV import endpoint
│   ├── services/
│   │   ├── analytics_service.py   # Live SQL analytics queries
│   │   ├── book_service.py        # Book business logic
│   │   ├── borrower_service.py    # Borrower business logic
│   │   └── transaction_service.py # Borrow/return orchestration
│   ├── crud.py                # Pure database query functions
│   ├── schemas.py             # Pydantic request/response models
│   └── main.py                # FastAPI app entry point
├── database/
│   ├── database.py            # SQLAlchemy engine and session setup
│   ├── models.py              # ORM table definitions (books, borrowers, transactions)
│   └── library.db             # SQLite database file (auto-created)
├── etl/
│   ├── extract.py             # Reads uploaded CSV files into DataFrames
│   ├── transform.py           # Cleans and validates DataFrames; returns drop stats
│   ├── load.py                # Inserts cleaned data into operational tables
│   ├── pipeline.py            # Runs extract → transform → load end-to-end
│   └── generate_raw_datasets.py # Generates intentionally dirty sample CSVs
├── datasets/
│   ├── BooksDataset.csv       # Source dataset (150 books)
│   ├── books.csv              # Generated dirty books CSV
│   ├── borrowers.csv          # Generated dirty borrowers CSV
│   └── transactions.csv       # Generated dirty transactions CSV
├── frontend/
│   └── src/
│       ├── components/
│       │   └── Navbar.jsx
│       ├── pages/
│       │   ├── admin/
│       │   │   ├── Dashboard.jsx    # Analytics charts and summary cards
│       │   │   ├── Books.jsx
│       │   │   ├── Borrowers.jsx
│       │   │   ├── Transactions.jsx
│       │   │   └── ETL.jsx          # Import CSV UI
│       │   └── user/
│       │       ├── SearchBooks.jsx
│       │       └── BorrowReturn.jsx
│       ├── services/
│       │   └── api.js               # All Axios API call functions
│       └── App.js
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher and npm

---

### Backend Setup

1. Navigate to the project root:
   ```bash
   cd AFDE_May26_Shruthi_LMS
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   uvicorn backend.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.  
   Interactive API docs: `http://localhost:8000/docs`

---

### Frontend Setup

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`.

---

### Database Setup

No manual setup is required. SQLite is file-based and the database (`database/library.db`) is created automatically when the backend server starts for the first time.

> **Note:** If you change the database schema (models.py), delete `database/library.db` and restart the backend to recreate the tables with the updated structure.

---

### Generating Sample CSV Data (optional)

To generate intentionally dirty sample CSVs for testing the import pipeline:

```bash
python -m etl.generate_raw_datasets
```

This creates `datasets/books.csv`, `datasets/borrowers.csv`, and `datasets/transactions.csv` with realistic data quality issues (missing values, invalid formats, duplicates) that the ETL transform step will clean.

---

## API Endpoints

### Books
| Method | Endpoint | Description |
|---|---|---|
| GET | `/books/` | List all books |
| POST | `/books/` | Add a new book |
| PUT | `/books/{id}` | Update a book |
| DELETE | `/books/{id}` | Delete a book (if no active borrows) |
| GET | `/books/search?q=` | Search books by keyword |

### Borrowers
| Method | Endpoint | Description |
|---|---|---|
| GET | `/borrowers/` | List all borrowers |
| POST | `/borrowers/` | Add a new borrower |
| PUT | `/borrowers/{id}` | Update a borrower |
| DELETE | `/borrowers/{id}` | Delete a borrower (if no active borrows) |

### Transactions
| Method | Endpoint | Description |
|---|---|---|
| GET | `/transactions` | List all transactions (sorted by borrow date desc) |
| POST | `/borrow` | Borrow a book |
| POST | `/return` | Return a book |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/summary` | Total books, borrowers, transactions, available, borrowed, overdue count |
| GET | `/analytics/popular-books?limit=10` | Top borrowed books with borrow count |
| GET | `/analytics/category-stats` | Borrow count and book count per category |
| GET | `/analytics/monthly-trends` | Monthly borrow and return counts |
| GET | `/analytics/overdue` | List of overdue transactions (unreturned past 14 days) |

### Import (ETL)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/etl/upload` | Upload one or more CSV files (`books_csv`, `borrowers_csv`, `transactions_csv`). Runs the ETL pipeline on uploaded files only and returns a summary with per-file transform stats. |

---

## ETL Pipeline

The import pipeline runs in three steps:

1. **Extract** — Reads only the uploaded CSV files into DataFrames.
2. **Transform** — Cleans each DataFrame and tracks per-reason drop counts:
   - *Books:* strips whitespace, normalises category case, cleans ISBNs, drops null titles and duplicates
   - *Borrowers:* validates email format, normalises phone to 10 digits, drops missing name/email and duplicates
   - *Transactions:* validates foreign keys, parses dates (multiple formats), drops future borrow dates, drops return-before-borrow, drops duplicates
3. **Load** — Inserts cleaned rows into the operational `books`, `borrowers`, and `transactions` tables. Skips rows that already exist (deduplication by ISBN, email, and borrow key). Syncs `availability_status` on all books after loading transactions.

Analytics on the Dashboard are computed live from these same operational tables.
