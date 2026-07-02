import pytest

from data.database_manager import DatabaseManager
from data.init_db import initialize_database
from repositories.book_repository import BookRepository
from repositories.borrowing_repository import BorrowingRepository
from repositories.user_repository import UserRepository
from repositories.waitlist_repository import WaitlistRepository


@pytest.fixture(scope="function")
def test_db():
    db = DatabaseManager(":memory:")

    initialize_database(db)

    class DB:
        def __init__(self, db: DatabaseManager):
            self.book = BookRepository(db)
            self.user = UserRepository(db)
            self.borrow = BorrowingRepository(
                db,
                self.book,
                self.user,
                None
            )
            self.waitlist = WaitlistRepository(
                db,
                self.borrow
            )
            self.borrow.waitlist_repo = self.waitlist

    database = DB(db)

    database.user.register_user("Adam Kowalski")
    database.user.register_user("Tomasz Nowak")

    database.book.add_book(
        "The Hobbit",
        "J.R.R. Tolkien",
        ["fantasy", "adventure fiction"],
        1937,
        1
    )
    database.book.add_book(
        "Dune",
        "Frank Herbert",
        ["science fiction", "space opera", "political fiction"],
        1965,
        1
    )
    database.book.add_book(
        "1984",
        "George Orwell",
        ["dystopian fiction", "political fiction", "science fiction"],
        1949,
        1
    )
    database.book.add_book(
        "Krzyżacy",
        "Henryk Sienkiewicz",
        ["historical fiction"],
        1900,
        1
    )

    database.book.add_ebook(
    "Python 101",
    "John Doe",
    ["technical literature", "educational programming"],
    2020,
    5
    )

    yield database

    db.close()
