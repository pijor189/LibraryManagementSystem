from fastapi import APIRouter
from pydantic import BaseModel
from .app_state import library
from library.book import Book, EBook

router = APIRouter()


class BookCreate(BaseModel):
    title: str
    author: str
    genre: str | list[str]
    year: int
    amount: int


class EBookCreate(BaseModel):
    title: str
    author: str
    genre: str | list[str]
    year: int
    file_size: int


class BookResponse(BaseModel):
    type: str
    title: str
    author: str
    genre: str | list[str]
    year: int


class EBookResponse(BaseModel):
    type: str
    title: str
    author: str
    genre: str | list[str]
    year: int
    file_size: int


def book_to_response(book: Book) -> BookResponse | EBookResponse:
    if isinstance(book, EBook):
        return EBookResponse(
            type="EBook",
            title=book.title,
            author=book.author,
            genre=book.genre,
            year=book.year,
            file_size=book.file_size
        )
    return BookResponse(
        type="Book",
        title=book.title,
        author=book.author,
        genre=book.genre,
        year=book.year
    )


@router.get("/books/all", response_model=list[BookResponse | EBookResponse])
def get_all_books():
    books = library.get_all_books()

    return [book_to_response(b) for b in books]


@router.get("/books/available", response_model=list[BookResponse | EBookResponse])
def get_available_books():
    books = library.get_available_books()

    return [book_to_response(b) for b in books]


@router.post("/books")
def add_book(book: BookCreate):
    new_book = Book(book.title, book.author, book.genre, book.year, book.amount)
    library.add_book(new_book)

    return book_to_response(new_book)


@router.post("/ebooks")
def add_ebook(ebook: EBookCreate):
    new_ebook = EBook(ebook.title, ebook.author, ebook.genre, ebook.year, ebook.file_size)
    library.add_book(new_ebook)

    return book_to_response(new_ebook)
