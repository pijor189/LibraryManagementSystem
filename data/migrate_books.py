import json
import data.state as state

from library.book import Book, EBook
from data.database_manager import DatabaseManager


def migrate_books_from_json(db: DatabaseManager):
    with open("data/json/books.json", "r", encoding="utf-8") as f:
        books = json.load(f)

    for book in books:
        data = Book(
                book["title"],
                book["author"],
                book["genre"],
                book["year"],
                book["amount"]
            )
        state.lib.add_book(data)
        genre_str = "; ".join(book["genre"])

        db.execute(
            """
            INSERT INTO books(id, title, author, genre, year, amount)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.id,
                book["title"],
                book["author"],
                genre_str,
                book["year"],
                book["amount"]
            )
        )


def migrate_ebooks_from_json(db: DatabaseManager):
    with open("data/json/ebooks.json", "r", encoding="utf-8") as f:
        ebooks = json.load(f)

    for ebook in ebooks:
        data = EBook(
                ebook["title"],
                ebook["author"],
                ebook["genre"],
                ebook["year"],
                ebook["file_size"]
            )
        state.lib.add_book(data)
        genre_str = "; ".join(ebook["genre"])

        db.execute(
            """
            INSERT INTO ebooks(id, title, author, genre, year, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.id,
                ebook["title"],
                ebook["author"],
                genre_str,
                ebook["year"],
                ebook["file_size"]
            )
        )


def migrate_books_to_object(db: DatabaseManager):
    data = db.fetchall(
        """
        SELECT * FROM books
        """
    )

    for d in data:
        genre = d[3].split('; ')
        book = Book(d[1], d[2], genre, d[4], d[5])
        book.id = d[0]
        state.lib.catalog[book.id] = book
        state.lib.items_id.add(book.id)


def migrate_ebooks_to_object(db: DatabaseManager):
    data = db.fetchall(
        """
        SELECT * FROM ebooks
        """
    )

    for d in data:
        genre = d[3].split('; ')
        ebook = EBook(d[1], d[2], genre, d[4], d[5])
        ebook.id = d[0]
        state.lib.catalog[ebook.id] = ebook
        state.lib.items_id.add(ebook.id)
