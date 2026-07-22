"""Pydantic schemas — request/response validation and serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Book ----------

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    genre: Optional[str] = None
    total_copies: int = Field(default=1, ge=1)


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    total_copies: Optional[int] = Field(default=None, ge=1)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    isbn: Optional[str] = None
    genre: Optional[str] = None
    total_copies: int
    available: int


# ---------- Member ----------

class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


# ---------- Borrow ----------

class BorrowCreate(BaseModel):
    book_id: int
    member_id: int


class ReturnRequest(BaseModel):
    record_id: int


class BorrowRecordOut(BaseModel):
    id: int
    book_id: int
    book_title: str
    member_id: int
    member_name: str
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool
    is_overdue: bool
