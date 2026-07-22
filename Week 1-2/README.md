# Library Management System — REST API

A REST API built with **FastAPI** and **SQLite** (via SQLAlchemy) for managing a library's books, members, and borrowing operations. Includes a simple Bootstrap frontend (`index.html`).

## Project Structure

```
library_api/
├── app/
│   ├── database.py       # SQLAlchemy engine/session setup
│   ├── models.py         # Book, Member, BorrowRecord tables
│   ├── schemas.py        # Pydantic request/response models
│   └── routers/
│       ├── books.py      # /api/books endpoints
│       ├── members.py    # /api/members endpoints
│       └── borrow.py     # /api/borrow endpoints
├── main.py                # Entry point
├── index.html              # Frontend (open directly in your browser)
├── requirements.txt
└── library.db              # SQLite database (auto-created on first run)
```

## Setup (VS Code)

1. Open this folder in VS Code.
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python main.py
   ```
5. Open **http://127.0.0.1:8000/** for an endpoint map, or **http://127.0.0.1:8000/docs** for interactive Swagger docs where you can try every endpoint directly.
6. Open `index.html` in your browser (just double-click it, or use VS Code's "Live Server" extension) to use the visual frontend. CORS is already enabled so it will talk to the API on port 8000 with no extra setup.

## Business Rules

- A book can only be borrowed if `available > 0`
- A member cannot borrow the same book twice at once (until returned)
- Loan period is **14 days** from the borrow date
- `is_overdue` is calculated automatically based on the current date
- Returning a book restores its availability count
- Books/members with active loans can't be deleted

## Example requests

**Add a book** — `POST /api/books/`
```json
{ "title": "The Alchemist", "author": "Paulo Coelho", "isbn": "978-0062315007", "genre": "Fiction", "total_copies": 3 }
```

**Register a member** — `POST /api/members/`
```json
{ "name": "Ishika Dubey", "email": "ishika@example.com", "phone": "9876543210", "address": "Delhi, India" }
```

**Borrow a book** — `POST /api/borrow/`
```json
{ "book_id": 1, "member_id": 1 }
```

**Return a book** — `POST /api/borrow/return`
```json
{ "record_id": 1 }
```
