from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── Book schemas ──────────────────────────────────────────────────────────────

class BookBase(BaseModel):
    title: str
    author: str
    category: str
    isbn: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    isbn: Optional[str] = None
    availability_status: Optional[str] = None


class BookResponse(BookBase):
    book_id: int
    availability_status: str

    model_config = {"from_attributes": True}


# ── Borrower schemas ──────────────────────────────────────────────────────────

class BorrowerBase(BaseModel):
    borrower_name: str
    email: EmailStr
    phone: str


class BorrowerCreate(BorrowerBase):
    pass


class BorrowerUpdate(BaseModel):
    borrower_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class BorrowerResponse(BorrowerBase):
    borrower_id: int

    model_config = {"from_attributes": True}


# ── Transaction schemas ───────────────────────────────────────────────────────

class BorrowRequest(BaseModel):
    book_id: int
    borrower_id: int


class ReturnRequest(BaseModel):
    transaction_id: int


class TransactionResponse(BaseModel):
    transaction_id: int
    book_id: int
    borrower_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None
    book: Optional[BookResponse] = None
    borrower: Optional[BorrowerResponse] = None

    model_config = {"from_attributes": True}
