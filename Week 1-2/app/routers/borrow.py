from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/borrow", tags=["Borrow & Return"])

LOAN_PERIOD_DAYS = 14


def _to_out(record: models.BorrowRecord) -> schemas.BorrowRecordOut:
    """Build the response schema, computing is_overdue on the fly."""
    is_overdue = (not record.is_returned) and datetime.utcnow() > record.due_date
    return schemas.BorrowRecordOut(
        id=record.id,
        book_id=record.book_id,
        book_title=record.book.title,
        member_id=record.member_id,
        member_name=record.member.name,
        borrow_date=record.borrow_date,
        due_date=record.due_date,
        return_date=record.return_date,
        is_returned=record.is_returned,
        is_overdue=is_overdue,
    )


@router.post("/", response_model=schemas.BorrowRecordOut, status_code=201)
def borrow_book(payload: schemas.BorrowCreate, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == payload.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    member = db.query(models.Member).filter(models.Member.id == payload.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if book.available <= 0:
        raise HTTPException(status_code=400, detail="No copies of this book are available")

    # A member cannot borrow the same book twice until it's returned
    already_borrowed = (
        db.query(models.BorrowRecord)
        .filter(
            models.BorrowRecord.book_id == payload.book_id,
            models.BorrowRecord.member_id == payload.member_id,
            models.BorrowRecord.is_returned.is_(False),
        )
        .first()
    )
    if already_borrowed:
        raise HTTPException(
            status_code=400,
            detail="This member has already borrowed this book and not yet returned it",
        )

    borrow_date = datetime.utcnow()
    record = models.BorrowRecord(
        book_id=book.id,
        member_id=member.id,
        borrow_date=borrow_date,
        due_date=borrow_date + timedelta(days=LOAN_PERIOD_DAYS),
        is_returned=False,
    )
    book.available -= 1

    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_out(record)


@router.post("/return", response_model=schemas.BorrowRecordOut)
def return_book(payload: schemas.ReturnRequest, db: Session = Depends(get_db)):
    record = (
        db.query(models.BorrowRecord)
        .filter(models.BorrowRecord.id == payload.record_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Borrow record not found")

    if record.is_returned:
        raise HTTPException(status_code=400, detail="This book has already been returned")

    record.is_returned = True
    record.return_date = datetime.utcnow()
    record.book.available += 1

    db.commit()
    db.refresh(record)
    return _to_out(record)


@router.get("/active", response_model=List[schemas.BorrowRecordOut])
def active_borrows(db: Session = Depends(get_db)):
    records = (
        db.query(models.BorrowRecord)
        .filter(models.BorrowRecord.is_returned.is_(False))
        .all()
    )
    return [_to_out(r) for r in records]


@router.get("/history", response_model=List[schemas.BorrowRecordOut])
def borrow_history(db: Session = Depends(get_db)):
    records = db.query(models.BorrowRecord).order_by(models.BorrowRecord.id.desc()).all()
    return [_to_out(r) for r in records]


@router.get("/overdue", response_model=List[schemas.BorrowRecordOut])
def overdue_borrows(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    records = (
        db.query(models.BorrowRecord)
        .filter(
            models.BorrowRecord.is_returned.is_(False),
            models.BorrowRecord.due_date < now,
        )
        .all()
    )
    return [_to_out(r) for r in records]
