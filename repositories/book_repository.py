import data.state as state
from library.book import Book, EBook, Item
from data.database_manager import DatabaseManager
from typing import Self


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
    ) -> None:
        book = Book(title, author, genre, year, amount)
        state.lib.add_book(book)
        genre_str = "; ".join(genre)

        self.db.execute(
            """
            INSERT INTO books(id, title, author, genre, year, amount)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                book.id,
                title,
                author,
                genre_str,
                year,
                amount,
            )
        )

    def add_ebook(
            self,
            title: str,
            author: str,
            genre: list[str] | str,
            year: int,
            file_size: int = 1,
    ) -> None:
        ebook = EBook(title, author, genre, year, file_size)
        state.lib.add_book(ebook)
        genre_str = "; ".join(genre)

        self.db.execute(
            """
            INSERT INTO ebooks(id, title, author, genre, year, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ebook.id,
                title,
                author,
                genre_str,
                year,
                file_size,
            )
        )

    def add_existing_book(self, book: Book, amount: int) -> None:
        state.lib.add_existing_book(book, amount)

        self.db.execute(
            """
            UPDATE books
            SET amount = ?
            WHERE id = ?
            """,
            (
                book.amount,
                book.id
            )
        )

    def reduce_existing_book(self, book: Book, amount: int) -> None:
        state.lib.reduce_book_amount(book, amount)

        self.db.execute(
            """
            UPDATE books
            SET amount = ?
            WHERE id = ?
            """,
            (
                book.amount,
                book.id
            )
        )

    def remove_book(self, item: Item) -> None:
        id = item.id
        type = 'books' if isinstance(item, Book) else 'ebooks'
        state.lib.remove_item(item)

        if type == 'books':
            self.db.execute(
                """
                DELETE FROM books
                WHERE id = ?
                """,
                (
                    id,
                )
            )
        elif type == 'ebooks':
            self.db.execute(
                """
                DELETE FROM ebooks
                WHERE id = ?
                """,
                (
                    id,
                )
            )

    def get_all_books(self) -> Self:
        return self.db.fetchall(
            """
            SELECT title, author, genre, year, 'book'
            FROM books
            
            UNION ALL
            
            SELECT title, author, genre, year, 'ebook'
            FROM ebooks
            """
        )

    def get_available_books(self) -> Self:
        return self.db.fetchall(
            """
            SELECT title, author, genre, year, 'book'
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

            SELECT title, author, genre, year, 'ebook'
            FROM ebooks
            """
        )

    def find_book_by_id(self, id: int) -> Self:
        return self.db.fetchone(
            """
            SELECT title, author, genre, year, 'book'
            FROM books
            WHERE id = ?
            
            UNION ALL
            
            SELECT title, author, genre, year, 'ebook'
            FROM ebooks
            WHERE id = ?
            """,
            (
                id,
                id
            )
        )

    def find_book_by_title(self, title: str) -> Self:
        return self.db.fetchall(
            """
            SELECT title, author, genre, year, 'book'
            FROM books
            WHERE title = ?

            UNION ALL

            SELECT title, author, genre, year, 'ebook'
            FROM ebooks
            WHERE title = ?
            """,
            (
                title,
                title
            )
        )

    def find_book_by_genre(self, genre: str) -> Self:
        return self.db.fetchall(
            """
            SELECT title, author, genre, year, 'book'
            FROM books
            WHERE genre LIKE ?

            UNION ALL

            SELECT title, author, genre, year, 'ebook'
            FROM ebooks
            WHERE genre LIKE ?
            """,
            (
                f"%{genre}%",
                f"%{genre}%"
            )
        )

    def find_book_by_author(self, author: str) -> Self:
        return self.db.fetchall(
            """
            SELECT title, author, genre, year, 'book'
            FROM books
            WHERE author = ?

            UNION ALL

            SELECT title, author, genre, year, 'ebook'
            FROM ebooks
            WHERE author = ?
            """,
            (
                author,
                author
            )
        )
