from library.user import User
from library.book import EBook, Book
from datetime import date, timedelta, datetime
from exceptions.loan_exceptions import (
    LoanInitializationError,
    InvalidExtendDaysError
)


class Loan:
    MAX_DAYS = 30

    def __init__(self, user: User, book: Book | EBook, days: int = 30):
        if (
            not isinstance(user, User)
            or (not isinstance(book, Book) and not isinstance(book, EBook))
            or not isinstance(days, int)
        ):
            raise LoanInitializationError("Invalid loan initialization")
        self.id = 0
        self.user_id = user.id
        self.book_id = book.id
        self.borrowed_at = date.today()
        if isinstance(book, EBook):
            self.due_date = None
        else:
            if days <= 0:
                raise InvalidExtendDaysError("Days must be greater than 0")
            days = min(days, self.MAX_DAYS)
            self.due_date = self.borrowed_at + timedelta(days=days)
        self.returned_at = None

    def __str__(self):
        return f"Borrowed at: {self.borrowed_at}\nDue date: {self.due_date}"

    def __repr__(self):
        return f"Borrowed at: {self.borrowed_at}\nDue date: {self.due_date}"

    def extend(self, days: int) -> None:
        if not self.due_date:
            return

        if days <= 0:
            raise InvalidExtendDaysError("Days must be greater than 0")

        days = min(days, self.MAX_DAYS)
        self.due_date = datetime.strptime(str(self.due_date), '%Y-%m-%d').date()
        self.due_date = self.due_date + timedelta(days=days)

    def is_overdue(self) -> bool:
        if not self.due_date:
            return False

        self.due_date = datetime.strptime(str(self.due_date), '%Y-%m-%d').date()

        return date.today() > self.due_date
