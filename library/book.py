from datetime import datetime

from exceptions.book_exceptions import (
    BookInitializationError,
    EBookInitializationError,
    ItemInitializationError,
)


class Item:
    def __init__(
            self,
            title: str,
            author: str,
            genre: list[str] | str,
            year: int
    ):
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
        ):
            raise ItemInitializationError("Invalid item initialization")

        self.id = 0
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year


class Book(Item):
    def __init__(
        self,
        title: str,
        author: str,
        genre: list[str] | str,
        year: int,
        amount: int = 1,
    ):
        if (
            not isinstance(amount, int)
            or amount < 1
        ):
            raise BookInitializationError("Invalid book initialization")
        super().__init__(title, author, genre, year)
        self.id = 0
        self.amount = amount
        self.borrowed = 0
        self.waitlist = set()

    def __str__(self):
        return (f"Book: Title: {self.title} - Author: {self.author}"
                f" - Genre: {self.genre} - Year: {self.year}")

    def __repr__(self):
        return (f"Book: Title: {self.title} - Author: {self.author}"
                f" - Genre: {self.genre} - Year: {self.year}\n")

    def is_book_available(self) -> bool:
        return False if self.amount == self.borrowed else True


class EBook(Item):
    def __init__(
        self,
        title: str,
        author: str,
        genre: list[str] | str,
        year: int,
        file_size: int
    ):
        if not isinstance(file_size, int) or file_size < 0:
            raise EBookInitializationError("Invalid ebook initialization")
        super().__init__(title, author, genre, year)
        self.id = 0
        self.file_size = file_size

    def __str__(self):
        return (
            f"EBook: Title: {self.title} - Author: {self.author}"
            f" - Genre: {self.genre} - Year: {self.year}"
            f" - File size: {self.file_size}"
        )

    def __repr__(self):
        return (
            f"EBook: Title: {self.title} - Author: {self.author}"
            f" - Genre: {self.genre} - Year: {self.year}"
            f" - File size: {self.file_size}"
        )
