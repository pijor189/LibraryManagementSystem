from library.book import Book, EBook
from library.user import User
import json


class DataLoader:
    @staticmethod
    def load_books(path: str) -> tuple[list[Book], list[EBook]]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        books = []
        ebooks = []

        for item in data:
            if item["type"] == "book":
                books.append(
                    Book(
                        item["title"],
                        item["author"],
                        item["genre"],
                        item["year"],
                        item["amount"],
                    )
                )
            elif item["type"] == "ebook":
                ebooks.append(
                    EBook(
                        item["title"],
                        item["author"],
                        item["genre"],
                        item["year"],
                        item["file_size"],
                    )
                )

        return books, ebooks

    @staticmethod
    def load_users(path: str) -> list[User]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [User(item["name"]) for item in data]
