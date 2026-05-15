# Library Management System (LMS)

## Project Information

### Project Title
Library Management System (LMS)

### Project Overview
A full-stack web application for managing a library's books, borrowers, and transactions. The system supports two roles — **Admin** and **User** — each with their own set of features. Role selection is handled on the landing page and stored in the browser's local storage; no authentication is required.

---

## Features Implemented

### Admin
- **Dashboard** — Overview of total books, available books, borrowed books, and registered borrowers. Highlights overdue borrows (past 14 days) and shows the 5 most recent transactions.
- **Book Management** — Add, edit, and delete books. Books can only be deleted when they have no active (unreturned) borrows.
- **Borrower Management** — Add, edit, and delete borrowers with email and phone validation. Borrowers can only be deleted when all their books have been returned.
- **Transactions** — View the full transaction history with book title, borrower name, borrow date, return date, and status.

### User
- **Search Books** — Search by title, author, category, or ISBN. Filter results by category or author using dropdowns. Results update in real time.
- **Borrow / Return** — Borrow an available book by selecting it from a dropdown and entering a registered borrower name. Return a book by selecting the active transaction. Full transaction history is shown on the same page.

### General
- Transaction history is preserved even after a book or borrower is deleted. Book title and borrower name are stored as snapshots on the transaction record at the time of borrowing.
- Borrow and return dates are recorded automatically.
- Status (Borrowed / Returned) is derived from whether a return date exists.

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18.2.0 | UI framework |
| React Router DOM | 6.22.0 | Client-side routing |
| Axios | 1.6.7 | HTTP client for API calls |
| Create React App | 5.0.1 | Project setup and build tooling |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| FastAPI | Latest | REST API framework |
| Uvicorn | Latest | ASGI server |
| SQLAlchemy | Latest | ORM for database access |
| Pydantic (with email) | Latest | Request/response schema validation |

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
│   │   ├── books.py          # Book endpoints
│   │   ├── borrowers.py      # Borrower endpoints
│   │   └── transactions.py   # Transaction, borrow, return, search endpoints
│   ├── services/
│   │   ├── book_service.py       # Book business logic
│   │   ├── borrower_service.py   # Borrower business logic
│   │   └── transaction_service.py # Borrow/return orchestration
│   ├── crud.py               # Pure database query functions
│   ├── schemas.py            # Pydantic request/response models
│   └── main.py               # FastAPI app entry point
├── database/
│   ├── database.py           # SQLAlchemy engine and session setup
│   ├── models.py             # ORM table definitions
│   └── library.db            # SQLite database file (auto-created)
├── frontend/
│   └── src/
│       ├── components/
│       │   └── Navbar.jsx
│       ├── pages/
│       │   ├── admin/
│       │   │   ├── Dashboard.jsx
│       │   │   ├── Books.jsx
│       │   │   ├── Borrowers.jsx
│       │   │   └── Transactions.jsx
│       │   └── user/
│       │       ├── SearchBooks.jsx
│       │       └── BorrowReturn.jsx
│       ├── services/
│       │   └── api.js        # All Axios API call functions
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

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/books/` | List all books |
| POST | `/books/` | Add a new book |
| PUT | `/books/{id}` | Update a book |
| DELETE | `/books/{id}` | Delete a book (if no active borrows) |
| GET | `/borrowers/` | List all borrowers |
| POST | `/borrowers/` | Add a new borrower |
| PUT | `/borrowers/{id}` | Update a borrower |
| DELETE | `/borrowers/{id}` | Delete a borrower (if no active borrows) |
| GET | `/transactions` | List all transactions |
| POST | `/borrow` | Borrow a book |
| POST | `/return` | Return a book |
| GET | `/search?q=` | Search books by keyword |
