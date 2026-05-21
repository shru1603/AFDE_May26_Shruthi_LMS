from sqlalchemy import Column, Integer, String, DateTime, Float
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
    availability_status = Column(String, default="available", nullable=False)


class Borrower(Base):
    __tablename__ = "borrowers"

    borrower_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, nullable=False)
    borrower_id = Column(Integer, nullable=False)
    book_title = Column(String, nullable=True)
    borrower_name = Column(String, nullable=True)
    borrow_date = Column(DateTime, server_default=func.now(), nullable=False)
    return_date = Column(DateTime, nullable=True)


# ── Analytics Tables (populated by ETL pipeline) ──────────────────────────────

class AnalyticsPopularBooks(Base):
    __tablename__ = "analytics_popular_books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category = Column(String, nullable=False)
    isbn = Column(String, nullable=True)
    borrow_count = Column(Integer, nullable=False, default=0)


class AnalyticsCategoryStats(Base):
    __tablename__ = "analytics_category_stats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String, nullable=False, unique=True, index=True)
    borrow_count = Column(Integer, nullable=False, default=0)
    book_count = Column(Integer, nullable=False, default=0)


class AnalyticsMonthlyTrends(Base):
    __tablename__ = "analytics_monthly_trends"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    borrow_count = Column(Integer, nullable=False, default=0)
    return_count = Column(Integer, nullable=False, default=0)


class AnalyticsOverdue(Base):
    __tablename__ = "analytics_overdue"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(Integer, nullable=False, index=True)
    book_id = Column(Integer, nullable=False)
    borrower_id = Column(Integer, nullable=False)
    book_title = Column(String, nullable=True)
    borrower_name = Column(String, nullable=True)
    borrow_date = Column(DateTime, nullable=False)
    days_overdue = Column(Integer, nullable=False, default=0)
