"""
Library Management System — REST API
Run with:  python main.py
Then visit http://127.0.0.1:8000/  for an endpoint map,
or       http://127.0.0.1:8000/docs for interactive Swagger UI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import books, members, borrow

# Create all tables (library.db is created automatically on first run)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management API",
    description="A REST API for managing books, members, and borrowing operations.",
    version="1.0.0",
)

# Allow the frontend (index.html, opened from anywhere) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(borrow.router)


@app.get("/")
def root():
    """Simple JSON map of available endpoints."""
    return {
        "message": "Library Management API is running",
        "docs": "/docs",
        "endpoints": {
            "books": {
                "GET /api/books/": "List all books (optional ?search=)",
                "GET /api/books/{id}": "Get a book by ID",
                "POST /api/books/": "Add a new book",
                "PUT /api/books/{id}": "Update a book",
                "DELETE /api/books/{id}": "Delete a book",
            },
            "members": {
                "GET /api/members/": "List all members",
                "GET /api/members/{id}": "Get a member by ID",
                "POST /api/members/": "Register a member",
                "PUT /api/members/{id}": "Update a member",
                "DELETE /api/members/{id}": "Remove a member",
            },
            "borrow": {
                "POST /api/borrow/": "Borrow a book",
                "POST /api/borrow/return": "Return a book",
                "GET /api/borrow/active": "All currently borrowed books",
                "GET /api/borrow/history": "Full borrow history",
                "GET /api/borrow/overdue": "Overdue books",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
