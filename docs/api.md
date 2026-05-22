# LMS API Documentation

**Base URL:** `http://localhost:8000`  
**Interactive Docs:** `http://localhost:8000/docs`  
**Content-Type:** `application/json`

---

## Endpoint List

| Method | Endpoint | Description |
|---|---|---|
| GET | `/books/` | List all books |
| GET | `/books/{book_id}` | Get a single book |
| POST | `/books/` | Add a new book |
| PUT | `/books/{book_id}` | Update a book |
| DELETE | `/books/{book_id}` | Delete a book |
| GET | `/borrowers/` | List all borrowers |
| POST | `/borrowers/` | Add a new borrower |
| PUT | `/borrowers/{borrower_id}` | Update a borrower |
| DELETE | `/borrowers/{borrower_id}` | Delete a borrower |
| GET | `/transactions` | List all transactions (sorted by borrow date desc) |
| POST | `/borrow` | Borrow a book |
| POST | `/return` | Return a book |
| GET | `/search?q={query}` | Search books by keyword |
| GET | `/analytics/summary` | Dashboard summary counts |
| GET | `/analytics/popular-books` | Top borrowed books |
| GET | `/analytics/category-stats` | Borrow and book counts per category |
| GET | `/analytics/monthly-trends` | Monthly borrow and return counts |
| GET | `/analytics/overdue` | List of overdue transactions |
| POST | `/etl/upload` | Upload CSVs and run the import pipeline |

---

## Books

### GET `/books/`
Returns all books in the library.

**Response `200 OK`**
```json
[
  {
    "book_id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "category": "Software Engineering",
    "isbn": "9780132350884",
    "availability_status": "available"
  },
  {
    "book_id": 2,
    "title": "The Pragmatic Programmer",
    "author": "Andrew Hunt",
    "category": "Software Engineering",
    "isbn": "9780201616224",
    "availability_status": "borrowed"
  }
]
```

---

### GET `/books/{book_id}`
Returns a single book by ID.

**Path Parameter**
| Parameter | Type | Description |
|---|---|---|
| `book_id` | integer | ID of the book |

**Response `200 OK`**
```json
{
  "book_id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "category": "Software Engineering",
  "isbn": "9780132350884",
  "availability_status": "available"
}
```

**Response `404 Not Found`**
```json
{ "detail": "Book not found" }
```

---

### POST `/books/`
Creates a new book. Initial status is set to `available` automatically.

**Request Body**
```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "category": "Software Engineering",
  "isbn": "9780132350884"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | Yes | Book title |
| `author` | string | Yes | Author name |
| `category` | string | Yes | Book category or genre |
| `isbn` | string | Yes | Unique ISBN number |

**Response `201 Created`**
```json
{
  "book_id": 3,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "category": "Software Engineering",
  "isbn": "9780132350884",
  "availability_status": "available"
}
```

---

### PUT `/books/{book_id}`
Updates one or more fields of an existing book. Only fields included in the request body are updated.

**Path Parameter**
| Parameter | Type | Description |
|---|---|---|
| `book_id` | integer | ID of the book to update |

**Request Body** (all fields optional)
```json
{
  "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
  "category": "Programming"
}
```

**Response `200 OK`**
```json
{
  "book_id": 1,
  "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
  "author": "Robert C. Martin",
  "category": "Programming",
  "isbn": "9780132350884",
  "availability_status": "available"
}
```

**Response `404 Not Found`**
```json
{ "detail": "Book not found" }
```

---

### DELETE `/books/{book_id}`
Deletes a book permanently. Deletion is blocked if the book is currently borrowed.

**Path Parameter**
| Parameter | Type | Description |
|---|---|---|
| `book_id` | integer | ID of the book to delete |

**Response `200 OK`**
```json
{
  "book_id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "category": "Software Engineering",
  "isbn": "9780132350884",
  "availability_status": "available"
}
```

**Response `400 Bad Request`** — book is currently borrowed
```json
{ "detail": "Cannot delete: book is currently borrowed. Return it first." }
```

**Response `404 Not Found`**
```json
{ "detail": "Book not found" }
```

---

## Borrowers

### GET `/borrowers/`
Returns all registered borrowers.

**Response `200 OK`**
```json
[
  {
    "borrower_id": 1,
    "borrower_name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "9876543210"
  }
]
```

---

### POST `/borrowers/`
Registers a new borrower.

**Request Body**
```json
{
  "borrower_name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "9876543210"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `borrower_name` | string | Yes | Full name |
| `email` | string | Yes | Must be a valid email format; must be unique |
| `phone` | string | Yes | Must be exactly 10 digits |

**Response `201 Created`**
```json
{
  "borrower_id": 3,
  "borrower_name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "9876543210"
}
```

---

### PUT `/borrowers/{borrower_id}`
Updates one or more fields of an existing borrower.

**Path Parameter**
| Parameter | Type | Description |
|---|---|---|
| `borrower_id` | integer | ID of the borrower to update |

**Request Body** (all fields optional)
```json
{ "phone": "9000000001" }
```

**Response `200 OK`**
```json
{
  "borrower_id": 1,
  "borrower_name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "9000000001"
}
```

**Response `404 Not Found`**
```json
{ "detail": "Borrower not found" }
```

---

### DELETE `/borrowers/{borrower_id}`
Deletes a borrower permanently. Deletion is blocked if the borrower has any unreturned books.

**Path Parameter**
| Parameter | Type | Description |
|---|---|---|
| `borrower_id` | integer | ID of the borrower to delete |

**Response `200 OK`**
```json
{
  "borrower_id": 1,
  "borrower_name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "9876543210"
}
```

**Response `400 Bad Request`** — borrower has active borrows
```json
{ "detail": "Cannot delete: borrower has books not yet returned." }
```

**Response `404 Not Found`**
```json
{ "detail": "Borrower not found" }
```

---

## Transactions

### GET `/transactions`
Returns all transactions sorted by `borrow_date` descending (most recent first), with a secondary sort by `transaction_id` descending.

**Response `200 OK`**
```json
[
  {
    "transaction_id": 5,
    "book_id": 2,
    "borrower_id": 1,
    "book_title": "The Pragmatic Programmer",
    "borrower_name": "Alice Johnson",
    "borrow_date": "2026-05-20T09:30:00",
    "return_date": null
  },
  {
    "transaction_id": 3,
    "book_id": 3,
    "borrower_id": 2,
    "book_title": "Clean Code",
    "borrower_name": "Bob Smith",
    "borrow_date": "2026-04-12T11:00:00",
    "return_date": "2026-04-20T14:00:00"
  }
]
```

> `return_date` is `null` for books that have not yet been returned.

---

### POST `/borrow`
Records a new borrow transaction. Sets the book's status to `borrowed`. Stores book title and borrower name as snapshots.

**Request Body**
```json
{
  "book_id": 1,
  "borrower_id": 2
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `book_id` | integer | Yes | ID of the book to borrow |
| `borrower_id` | integer | Yes | ID of the borrower |

**Response `201 Created`**
```json
{
  "transaction_id": 6,
  "book_id": 1,
  "borrower_id": 2,
  "book_title": "Clean Code",
  "borrower_name": "Bob Smith",
  "borrow_date": "2026-05-22T10:00:00",
  "return_date": null
}
```

**Response `400 Bad Request`** — book is not available
```json
{ "detail": "Book is not available" }
```

**Response `404 Not Found`**
```json
{ "detail": "Borrower not found" }
```

---

### POST `/return`
Records the return of a borrowed book. Sets `return_date` on the transaction and resets the book's status to `available`.

**Request Body**
```json
{ "transaction_id": 6 }
```

| Field | Type | Required | Description |
|---|---|---|---|
| `transaction_id` | integer | Yes | ID of the active transaction to close |

**Response `200 OK`**
```json
{
  "transaction_id": 6,
  "book_id": 1,
  "borrower_id": 2,
  "book_title": "Clean Code",
  "borrower_name": "Bob Smith",
  "borrow_date": "2026-05-22T10:00:00",
  "return_date": "2026-05-22T16:30:00"
}
```

**Response `404 Not Found`** — no active transaction with that ID
```json
{ "detail": "Active transaction not found" }
```

---

## Search

### GET `/search?q={query}`
Searches books by keyword across title, author, category, and ISBN. Case-insensitive partial match.

**Query Parameter**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `q` | string | Yes | Search keyword |

**Example:** `GET /search?q=clean`

**Response `200 OK`**
```json
[
  {
    "book_id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "category": "Software Engineering",
    "isbn": "9780132350884",
    "availability_status": "available"
  }
]
```

---

## Analytics

All analytics are computed live from the operational `books`, `borrowers`, and `transactions` tables.

---

### GET `/analytics/summary`
Returns headline counts for the dashboard.

**Response `200 OK`**
```json
{
  "total_books": 152,
  "total_borrowers": 31,
  "total_transactions": 201,
  "available": 120,
  "borrowed": 32,
  "overdue_count": 14
}
```

| Field | Description |
|---|---|
| `total_books` | Total books in the library |
| `total_borrowers` | Total registered borrowers |
| `total_transactions` | Total borrow transactions (all time) |
| `available` | Books with `availability_status = available` |
| `borrowed` | Books with `availability_status = borrowed` |
| `overdue_count` | Active borrows with `borrow_date` older than 14 days |

---

### GET `/analytics/popular-books?limit=10`
Returns the most borrowed books ranked by borrow count.

**Query Parameter**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | integer | 10 | Number of books to return |

**Response `200 OK`**
```json
[
  {
    "book_id": 5,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "category": "Fiction",
    "isbn": "9780743273565",
    "borrow_count": 8
  }
]
```

---

### GET `/analytics/category-stats`
Returns borrow count and book count grouped by category.

**Response `200 OK`**
```json
[
  {
    "category": "Fiction",
    "borrow_count": 45,
    "book_count": 30
  },
  {
    "category": "Science",
    "borrow_count": 28,
    "book_count": 18
  }
]
```

---

### GET `/analytics/monthly-trends`
Returns monthly borrow and return counts for the trend line chart.

**Response `200 OK`**
```json
[
  {
    "month": "2025-12",
    "borrows": 18,
    "returns": 14
  },
  {
    "month": "2026-01",
    "borrows": 22,
    "returns": 19
  }
]
```

---

### GET `/analytics/overdue`
Returns all active transactions where `borrow_date` is older than 14 days.

**Response `200 OK`**
```json
[
  {
    "transaction_id": 39,
    "book_id": 12,
    "borrower_id": 4,
    "book_title": "What Went Wrong at Enron",
    "borrower_name": "Deepak Verma",
    "borrow_date": "2026-04-10T00:00:00",
    "return_date": null,
    "days_overdue": 42
  }
]
```

---

## Import (ETL)

### POST `/etl/upload`
Accepts up to three CSV files, runs the ETL pipeline (Extract → Transform → Load), and returns a summary with per-file row breakdown. Only the uploaded files are processed — any file not included is skipped.

**Request** — `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `books_csv` | file | No | Books CSV (`book_id`, `isbn`, `Title`, `Authors`, `Category`, …) |
| `borrowers_csv` | file | No | Borrowers CSV (`borrower_id`, `borrower_name`, `email`, `phone`) |
| `transactions_csv` | file | No | Transactions CSV (`transaction_id`, `book_id`, `borrower_id`, `borrow_date`, `return_date`) |

At least one file must be provided.

**Response `200 OK`** — success
```json
{
  "status": "success",
  "uploaded": ["books.csv", "transactions.csv"],
  "transform_stats": {
    "books": {
      "input_rows": 154,
      "output_rows": 148,
      "dropped": {
        "null_title": 2,
        "duplicates": 4
      }
    },
    "transactions": {
      "input_rows": 215,
      "output_rows": 193,
      "dropped": {
        "missing_ids": 5,
        "invalid_fk": 3,
        "unparseable_date": 2,
        "future_date": 1,
        "return_before_borrow": 1,
        "duplicates": 10
      }
    }
  },
  "summary": {
    "books": 150,
    "borrowers": 30,
    "transactions": 193,
    "overdue": 14
  }
}
```

**Transform drop reasons by file:**

*Books*
| Reason | Description |
|---|---|
| `null_title` | Rows with missing or empty title |
| `duplicates` | Exact duplicate rows |

*Borrowers*
| Reason | Description |
|---|---|
| `missing_name_or_email` | Rows with missing borrower name or email |
| `invalid_email` | Email does not match `name@domain.ext` format |
| `invalid_phone` | Phone is not exactly 10 digits after stripping non-digits |
| `duplicate_email` | Duplicate rows by email |

*Transactions*
| Reason | Description |
|---|---|
| `missing_ids` | Rows with null `book_id` or `borrower_id` |
| `invalid_fk` | `book_id` or `borrower_id` not found in books/borrowers |
| `unparseable_date` | `borrow_date` cannot be parsed in any supported format |
| `future_date` | `borrow_date` is in the future |
| `return_before_borrow` | `return_date` is earlier than `borrow_date` |
| `duplicates` | Duplicate rows by (`book_id`, `borrower_id`, `borrow_date`) |

**Response `200 OK`** — error (e.g. no files uploaded)
```json
{
  "status": "error",
  "message": "No CSV files uploaded."
}
```

---

## Error Reference

| Status Code | Meaning |
|---|---|
| `200` | Request succeeded |
| `201` | Resource created successfully |
| `400` | Bad request — business rule violation (e.g. active borrow exists) |
| `404` | Resource not found |
| `422` | Validation error — missing or invalid request fields |

**Example `422 Unprocessable Entity`**
```json
{
  "detail": [
    {
      "loc": ["body", "isbn"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
