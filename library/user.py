from .exceptions import InvalidUser

class User:
    def __init__(self, name: str):
        if not isinstance(name, str) or name.strip() == "":
            raise InvalidUser("Invalid user initialization")
        self.id = 0
        self.name = name
        self.borrowed_physical_books = []
        self.borrowed_ebooks = []
        self.waitlist = []

    def __str__(self):
        books = [b.book.title for b in self.borrowed_physical_books]
        ebooks = [b.title for b in self.borrowed_ebooks]
        waitlist = [b.title for b in self.waitlist]
        return f"User name: {self.name}\nBorrowed books: {books}\nBorrowed ebooks: {ebooks}\nWaitlist: {waitlist}"
