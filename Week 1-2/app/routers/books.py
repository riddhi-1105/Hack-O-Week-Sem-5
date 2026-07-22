from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/books", tags=["Books"])


@router.get("/", response_model=List[schemas.BookOut])
def list_books(
    search: Optional[str] = Query(
        default=None, description="Filter by title or author (case-insensitive)"
    ),
    db: Session = Depends(get_db),
):
    """List all books, optionally filtered by a search term."""
    query = db.query(models.Book)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.Book.title.ilike(like)) | (models.Book.author.ilike(like))
        )
    return query.all()


@router.get("/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=schemas.BookOut, status_code=201)
def add_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    if payload.isbn:
        existing = (
            db.query(models.Book).filter(models.Book.isbn == payload.isbn).first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="A book with this ISBN already exists"
            )

    book = models.Book(
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        genre=payload.genre,
        total_copies=payload.total_copies,
        available=payload.total_copies,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    borrowed_out = book.total_copies - book.available

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    # Keep `available` consistent if total_copies changed
    if "total_copies" in update_data:
        if payload.total_copies < borrowed_out:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot set total_copies below {borrowed_out}; "
                f"that many copies are currently borrowed",
            )
        book.available = payload.total_copies - borrowed_out

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    active_loan = (
        db.query(models.BorrowRecord)
        .filter(
            models.BorrowRecord.book_id == book_id,
            models.BorrowRecord.is_returned.is_(False),
        )
        .first()
    )
    if active_loan:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a book that currently has copies borrowed",
        )

    db.delete(book)
    db.commit()
    return {"success": True, "message": f"Book {book_id} deleted"}
