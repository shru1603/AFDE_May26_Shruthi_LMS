from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base


class AvailabilityStatus(str, enum.Enum):
    available = "available"
    borrowed = "borrowed"


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, nullable=False)
    availability_status = Column(
        String, default=AvailabilityStatus.available, nullable=False
    )

    transactions = relationship("Transaction", back_populates="book")


class Borrower(Base):
    __tablename__ = "borrowers"

    borrower_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="borrower")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    borrower_id = Column(Integer, ForeignKey("borrowers.borrower_id"), nullable=False)
    borrow_date = Column(DateTime, server_default=func.now(), nullable=False)
    return_date = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="transactions")
    borrower = relationship("Borrower", back_populates="transactions")
