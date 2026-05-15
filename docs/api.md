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
| GET | `/transactions` | List all transactions |
| POST | `/borrow` | Borrow a book |
| POST | `/return` | Return a book |
| GET | `/search?q={query}` | Search books by keyword |

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
{
  "detail": "Book not found"
}
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
{
  "detail": "Book not found"
}
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
{
  "detail": "Cannot delete: book is currently borrowed. Return it first."
}
```

**Response `404 Not Found`**
```json
{
  "detail": "Book not found"
}
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
  },
  {
    "borrower_id": 2,
    "borrower_name": "Bob Smith",
    "email": "bob@example.com",
    "phone": "9123456780"
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
{
  "phone": "9000000001"
}
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
{
  "detail": "Borrower not found"
}
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
{
  "detail": "Cannot delete: borrower has books not yet returned."
}
```

**Response `404 Not Found`**
```json
{
  "detail": "Borrower not found"
}
```

---

## Transactions

### GET `/transactions`
Returns all transactions (both active and returned).

**Response `200 OK`**
```json
[
  {
    "transaction_id": 1,
    "book_id": 2,
    "borrower_id": 1,
    "book_title": "The Pragmatic Programmer",
    "borrower_name": "Alice Johnson",
    "borrow_date": "2025-05-01T09:30:00",
    "return_date": "2025-05-10T14:00:00"
  },
  {
    "transaction_id": 2,
    "book_id": 3,
    "borrower_id": 2,
    "book_title": "Clean Code",
    "borrower_name": "Bob Smith",
    "borrow_date": "2025-05-12T11:00:00",
    "return_date": null
  }
]
```

> `return_date` is `null` for books that have not yet been returned.  
> Transaction status (Borrowed / Returned) is derived on the frontend from whether `return_date` is set.

---

### POST `/borrow`
Records a new borrow transaction. Sets the book's status to `borrowed`. Stores the book title and borrower name as snapshots on the transaction.

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
  "transaction_id": 3,
  "book_id": 1,
  "borrower_id": 2,
  "book_title": "Clean Code",
  "borrower_name": "Bob Smith",
  "borrow_date": "2025-05-15T10:00:00",
  "return_date": null
}
```

**Response `400 Bad Request`** — book is not available
```json
{
  "detail": "Book is not available"
}
```

**Response `404 Not Found`** — borrower not found
```json
{
  "detail": "Borrower not found"
}
```

---

### POST `/return`
Records the return of a borrowed book. Sets `return_date` on the transaction and resets the book's status to `available`.

**Request Body**
```json
{
  "transaction_id": 3
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `transaction_id` | integer | Yes | ID of the active transaction to close |

**Response `200 OK`**
```json
{
  "transaction_id": 3,
  "book_id": 1,
  "borrower_id": 2,
  "book_title": "Clean Code",
  "borrower_name": "Bob Smith",
  "borrow_date": "2025-05-15T10:00:00",
  "return_date": "2025-05-20T16:30:00"
}
```

**Response `404 Not Found`** — no active transaction with that ID
```json
{
  "detail": "Active transaction not found"
}
```

---

## Search

### GET `/search?q={query}`
Searches books by keyword across title, author, category, and ISBN. Case-insensitive partial match.

**Query Parameter**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `q` | string | Yes | Search keyword (minimum 1 character) |

**Example Request**
```
GET /search?q=clean
```

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

**Response `200 OK`** — no matches (returns empty array)
```json
[]
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
