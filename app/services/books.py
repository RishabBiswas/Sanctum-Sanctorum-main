"""Book catalogue operations."""
from typing import Optional,List

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Book
from app.schemas import BookCreate, BookPage, BookSort, BookUpdate


def create_book(db: Session, data: BookCreate) -> Book:
    """Add a book to the catalogue.

    Rules: the (already normalized) ISBN must be unique -> 409 otherwise.
    """
    book = Book(**data.model_dump())
    db.add(book)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="ISBN already exists")

    db.refresh(book)
    return book


def get_book(db: Session, book_id: int) -> Book:
    """Return a book by id, or raise 404."""
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    """Apply a partial update. Only fields present in the request are changed; 404 if missing."""
    book = db.get(Book, book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)

    return book


def list_books(
    db: Session,
    q: Optional[str] = None,
    restricted: Optional[bool] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort: Optional[BookSort] = None,
    limit: int = 20,
    offset: int = 0,
) -> BookPage:
    """Search the catalogue.

    Rules:
    - ``q`` matches title OR author, case-insensitive substring.
    - ``restricted`` filters exactly; ``min_price``/``max_price`` are inclusive.
    - Sorted by ``sort`` (title / price, ``-`` for descending) with ties broken by id;
      default order is id ascending.
    - ``total`` counts all matches before ``limit``/``offset`` are applied.
    """
    query = select(Book)

    # Search title OR author
    if q:
        query = query.where(
            or_(
                Book.title.icontains(q, autoescape=True),
                Book.author.icontains(q, autoescape=True),
            )
        )

    # Filter by restricted status
    if restricted is not None:
        query = query.where(Book.restricted == restricted)

    # Inclusive price filters
    if min_price is not None:
        query = query.where(Book.price_cents >= min_price)

    if max_price is not None:
        query = query.where(Book.price_cents <= max_price)

    # Count all matching books BEFORE pagination
    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    )

    # Sorting
    if sort == "title":
        query = query.order_by(Book.title.asc(), Book.id.asc())
    elif sort == "-title":
        query = query.order_by(Book.title.desc(), Book.id.asc())
    elif sort == "price":
        query = query.order_by(Book.price_cents.asc(), Book.id.asc())
    elif sort == "-price":
        query = query.order_by(Book.price_cents.desc(), Book.id.asc())
    else:
        query = query.order_by(Book.id.asc())

    # Pagination
    books = db.scalars(
        query.limit(limit).offset(offset)
    ).all()

    return BookPage(
        items=books,
        total=total or 0,
        limit=limit,
        offset=offset,
    )


