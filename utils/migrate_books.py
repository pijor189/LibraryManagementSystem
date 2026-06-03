import json
from data.database_manager import DatabaseManager
from utils.uid import generate_uid


library_books_id = set()
library_books_copy_id = set()


def migrate_books():
    db = DatabaseManager()

    global library_books_id, library_books_copy_id

    with open("data/books.json", "r") as f:
        books = json.load(f)

    for book in books:
        genre_str = json.dumps(book["genre"])
        book_id = generate_uid(library_books_id)

        db.execute(
            """
            INSERT INTO books(id, title, author, genre, year, amount)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                book_id,
                book["title"],
                book["author"],
                genre_str,
                book["year"],
                book["amount"]
            )
        )

        for _ in range(book["amount"]):
            db.execute(
                """
                INSERT INTO book_copies(id, book_id, is_available)
                VALUES (?, ?, ?)
                """,
                (
                    generate_uid(library_books_copy_id),
                    book_id,
                    1
                )
            )


def migrate_ebooks():
    db = DatabaseManager()

    with open("data/ebooks.json", "r") as f:
        ebooks = json.load(f)

    global library_books_id

    for ebook in ebooks:
        genre_str = json.dumps(ebook["genre"])

        db.execute(
            """
            INSERT INTO ebooks(id, title, author, genre, year, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                generate_uid(library_books_id),
                ebook["title"],
                ebook["author"],
                genre_str,
                ebook["year"],
                ebook["file_size"]
            )
        )
