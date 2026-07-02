import json

from library.book import Book, EBook
from library.library import Library
from library.user import User


class DataLoader:
    @staticmethod
    def load_books(path: str) -> list[Book]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [
            Book(
                item["title"],
                item["author"],
                item["genre"],
                item["year"],
                item["amount"]
            )
            for item in data
        ]

    @staticmethod
    def load_ebooks(path: str) -> list[EBook]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [
            EBook(
                item["title"],
                item["author"],
                item["genre"],
                item["year"],
                item["file_size"]
            )
            for item in data
        ]

    @staticmethod
    def load_users(path: str) -> list[User]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [User(item["name"]) for item in data]


def init_library() -> Library:
    lib = Library()
    users = DataLoader.load_users("data/json/users.json")
    books = DataLoader.load_books("data/json/books.json")
    ebooks = DataLoader.load_ebooks("data/json/ebooks.json")

    for book in books:
        lib.add_book(book)
    for ebook in ebooks:
        lib.add_book(ebook)
    for user in users:
        lib.register_user(user)

    return lib
