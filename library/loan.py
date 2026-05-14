from library.user import User
from library.book import Book, EBook
from datetime import datetime, timedelta

class Loan:
    MAX_DAYS = 30

    def __init__(self, user: User, book: Book, days: int = 30):
        self.user = user
        self.book = book
        self.borrowed_at = datetime.now()
        if isinstance(book, EBook):
            self.due_date = None
        else:
            if days <= 0:
                raise ValueError("Days must be greater than 0")
            days = min(days, self.MAX_DAYS)
            self.due_date = self.borrowed_at + timedelta(days=days)
        self.returned_at = None

    def __str__(self):
        return f"Borrowed at: {self.borrowed_at}\nDue date: {self.due_date}"

    def __repr__(self):
        return f"Borrowed at: {self.borrowed_at}\nDue date: {self.due_date}"

    def extend(self, days: int) -> None:
        if isinstance(self.book, EBook):
            return

        if days <= 0:
            raise ValueError("Days must be greater than 0")

        new_due = self.due_date + timedelta(days=days)
        max_due = self.due_date + timedelta(days=self.MAX_DAYS)

        if new_due > max_due:
            self.due_date = max_due
        else:
            self.due_date = new_due

    def is_overdue(self) -> bool:
        if isinstance(self.book, EBook):
            return False
        return datetime.now() > self.due_date