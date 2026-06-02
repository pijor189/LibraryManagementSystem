import json
from library.book import Book, EBook
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
