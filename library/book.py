from .exceptions import InvalidBook
from utils.uid import generate_uid_book

class Book:
    def __init__(self, title: str, author: str, genre: list[str] | str, year: int, amount: int = 1):
        if not isinstance(title, str) or not isinstance(author, str) or not isinstance(genre, list | str) \
                or not isinstance(year, int) or title.strip() == "" or author.strip() == "" or year == 0 \
                or not isinstance(amount, int) or (isinstance(genre, list) and not genre) \
                or (isinstance(genre, str) and genre.strip() == ""):
            raise InvalidBook("Invalid book initialization")
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.amount = amount
        self.book_id = generate_uid_book()
        self.copies = []
        self.waitlist = []

    def __str__(self):
        return f"Book: Title: {self.title} - Author: {self.author} - Genre: {self.genre} - Year: {self.year}"

    def __repr__(self):
        return f"Book: Title: {self.title} - Author: {self.author} - Genre: {self.genre} - Year: {self.year}\n"

    def available_copy(self):
        for copy in self.copies:
            if copy.is_available:
                return copy
        return None

class BookCopy:
    def __init__(self, book: Book):
        self.book = book
        self.id = 0
        self.loan = None
        self.is_available = True

    def __str__(self):
        return (f"Book: Title: {self.book.title} - Author: {self.book.author} - Genre: {self.book.genre} "
                f"- Year: {self.book.year}")

    def __repr__(self):
        return (f"Book: Title: {self.book.title} - Author: {self.book.author} - Genre: {self.book.genre} "
                f"- Year: {self.book.year}")

class EBook(Book):
    def __init__(self, title: str, author: str, genre: list[str] | str, year: int, file_size: int):
        if not isinstance(file_size, int) or file_size < 0:
            raise InvalidBook("Invalid ebook initialization")
        super().__init__(title, author, genre, year)
        self.id = 0
        self.file_size = file_size

    def __str__(self):
        return (f"EBook: Title: {self.title} - Author: {self.author} - Genre: {self.genre} "
                f"- Year: {self.year} - File size: {self.file_size}")

    def __repr__(self):
        return (f"EBook: Title: {self.title} - Author: {self.author} - Genre: {self.genre} "
                f"- Year: {self.year} - File size: {self.file_size}\n")

    def available_copy(self):
        return self