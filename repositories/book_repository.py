from datetime import datetime
from typing import Any

from data.database_manager import DatabaseManager
from exceptions.book_exceptions import ItemInitializationError, MissingItemError
from exceptions.library_exceptions import (
    BookCurrentlyBorrowedError,
    InvalidNumberOfBooksError,
)
from utils.uid import generate_uid


class BookRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_book(
            self,
            title: str,
            author: str,
            genre: list[str] | str,
            year: int,
            amount: int = 1,
    ) -> str:
        if (
                not isinstance(title, str)
                or not isinstance(author, str)
                or not isinstance(genre, list | str)
                or not isinstance(year, int)
                or title.strip() == ""
                or author.strip() == ""
                or year == 0
                or year > datetime.now().year
                or (isinstance(genre, list) and not genre)
                or (isinstance(genre, str) and genre.strip() == "")
                or not isinstance(amount, int)
                or amount < 1
        ):
            raise ItemInitializationError("Invalid item initialization")

        items = self.get_all_books()
        items_ids = set()

        for item in items:
            items_ids.add(item["id"])

        uid = generate_uid(items_ids)

        if isinstance(genre, list):
            genre_str = "; ".join(genre)
        else:
            genre_str = genre

        self.db.execute(
            """
            INSERT INTO books(id, title, author, genre, year, amount)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                uid,
                title,
                author,
                genre_str,
                year,
                amount,
            )
        )

        return uid

    def add_ebook(
            self,
            title: str,
            author: str,
            genre: list[str] | str,
            year: int,
            file_size: int = 1,
    ) -> str:
        if (
                not isinstance(title, str)
                or not isinstance(author, str)
                or not isinstance(genre, list | str)
                or not isinstance(year, int)
                or title.strip() == ""
                or author.strip() == ""
                or year == 0
                or year > datetime.now().year
                or (isinstance(genre, list) and not genre)
                or (isinstance(genre, str) and genre.strip() == "")
                or not isinstance(file_size, int)
                or file_size < 0
        ):
            raise ItemInitializationError("Invalid item initialization")

        items = self.get_all_books()
        items_ids = set()

        for item in items:
            items_ids.add(item["id"])

        uid = generate_uid(items_ids)

        if isinstance(genre, list):
            genre_str = "; ".join(genre)
        else:
            genre_str = genre

        self.db.execute(
            """
            INSERT INTO ebooks(id, title, author, genre, year, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                uid,
                title,
                author,
                genre_str,
                year,
                file_size,
            )
        )

        return uid

    def update_books_amount(self, book_id: str, amount: int) -> None:
        self.db.execute(
            """
            UPDATE books
            SET amount = ?
            WHERE id = ?
            """,
            (
                amount,
                book_id
            )
        )

    def add_existing_book(self, book_id: str, amount: int) -> None:
        if amount <= 0:
            raise InvalidNumberOfBooksError(
                "Invalid number of amount."
            )

        data = self.find_book_by_id(book_id)

        if data:
            self.update_books_amount(book_id, data["amount"] + amount)
        else:
            raise MissingItemError(
                f"Book {book_id} does not exist."
            )

    def reduce_existing_book(self, book_id: str, amount: int) -> None:
        data = self.find_book_by_id(book_id)

        if not data:
            raise MissingItemError(
                f"Book {book_id} does not exist."
            )

        if amount <= 0 or amount > data["amount"]:
            raise InvalidNumberOfBooksError(
                "Invalid number of amount."
            )

        self.update_books_amount(book_id, data["amount"] - amount)

    def remove_book(self, book_id: str) -> None:
        book = self.find_book_by_id(book_id)

        if not book:
            raise MissingItemError(
                f"Book {book_id} does not exist."
            )

        if book["type"] == 'book':
            borrowings = self.db.fetchall(
                """
                SELECT 1
                FROM borrowings b
                WHERE b.book_id = ?
                    AND b.returned_at IS NULL
                """,
                (
                    book_id,
                )
            )

            if not borrowings:
                self.db.execute(
                    """
                    DELETE FROM books
                    WHERE id = ?
                    """,
                    (
                        book_id,
                    )
                )
            else:
                raise BookCurrentlyBorrowedError(
                    f"Book {book_id} is currently borrowed "
                    "and cannot be removed."
                )
        elif book["type"] == 'ebook':
            borrowings = self.db.fetchall(
                """
                SELECT 1
                FROM borrowings b
                WHERE b.book_id = ?
                """,
                (
                    book_id,
                )
            )

            if not borrowings:
                self.db.execute(
                    """
                    DELETE FROM ebooks
                    WHERE id = ?
                    """,
                    (
                        book_id,
                    )
                )
            else:
                raise BookCurrentlyBorrowedError(
                    f"Book {book_id} is currently borrowed "
                    "and cannot be removed."
                )

    def get_all_books(self) -> list[Any]:
        return self.db.fetchall(
            """
            SELECT id, title, author, genre, year, 'book' AS type
            FROM books

            UNION ALL

            SELECT id, title, author, genre, year, 'ebook' AS type
            FROM ebooks
            """
        )

    def get_available_books(self) -> list[Any]:
        return self.db.fetchall(
            """
            SELECT title, author, genre, year, 'book' AS type
            FROM books
            LEFT JOIN (
                SELECT book_id, COUNT(*) AS borrowed
                FROM borrowings
                WHERE returned_at IS NULL
                GROUP BY book_id
            ) br
            ON books.id = br.book_id
            WHERE books.amount > COALESCE(br.borrowed, 0)

            UNION ALL

            SELECT title, author, genre, year, 'ebook' AS type
            FROM ebooks
            """
        )

    def is_book_available(self, book_id: str) -> Any:
        return self.db.fetchone(
            """
            SELECT b.amount >
                (SELECT COUNT(*)
                FROM borrowings
                WHERE book_id = b.id
                    AND returned_at IS NULL)
            AS available
            FROM books b
            WHERE b.id = ?
            """,
            (
                book_id,
            )
        )

    def find_book_by_id(self, book_id: str) -> Any:
        return self.db.fetchone(
            """
            SELECT title, author, genre, year, amount, 'book' AS type
            FROM books
            WHERE id = ?

            UNION ALL

            SELECT title, author, genre, year, file_size, 'ebook' AS type
            FROM ebooks
            WHERE id = ?
            """,
            (
                book_id,
                book_id
            )
        )

    def find_book_by_title(self, title: str) -> list[Any]:
        title = " ".join(title.lower().split())

        return self.db.fetchall(
            """
            SELECT id, title, author, genre, year, 'book' AS type
            FROM books
            WHERE LOWER(title) = ?

            UNION ALL

            SELECT id, title, author, genre, year, 'ebook' AS type
            FROM ebooks
            WHERE LOWER(title) = ?
            """,
            (
                title,
                title
            )
        )

    def find_book_by_genre(self, genre: str) -> list[Any]:
        return self.db.fetchall(
            """
            SELECT id, title, author, genre, year, 'book' AS type
            FROM books
            WHERE genre LIKE ?

            UNION ALL

            SELECT id, title, author, genre, year, 'ebook' AS type
            FROM ebooks
            WHERE genre LIKE ?
            """,
            (
                f"%{genre}%",
                f"%{genre}%"
            )
        )

    def find_book_by_author(self, author: str) -> list[Any]:
        return self.db.fetchall(
            """
            SELECT id, title, author, genre, year, 'book' AS type
            FROM books
            WHERE author = ?

            UNION ALL

            SELECT id, title, author, genre, year, 'ebook' AS type
            FROM ebooks
            WHERE author = ?
            """,
            (
                author,
                author
            )
        )
