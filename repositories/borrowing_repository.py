import data.state as state
from library.book import Item, Book
from library.user import User
from library.loan import Loan
from data.database_manager import DatabaseManager
from datetime import date


class BorrowingRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def borrow_book(
        self,
        user: User,
        item: Item | list[Item],
        days: int = 30
    ):
        state.lib.borrow(user, item, days)
        loan_id = list(state.lib.loans.keys())[-1]
        loan = state.lib.loans[loan_id]
        type = 'book' if isinstance(item, Book) else 'ebook'

        self.db.execute(
            """
            INSERT INTO borrowings(
            id, user_id, book_id, type, 
            borrowed_at, due_to, returned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                loan_id,
                loan.user_id,
                loan.book_id,
                type,
                loan.borrowed_at,
                loan.due_date,
                loan.returned_at
            )
        )

    def extend_loan(self, loan: Loan, days: int = 30) -> None:
        loan.extend(days)

        self.db.execute(
            """
            UPDATE borrowings
            SET due_to = ?
            WHERE user_id = ? and book_id = ?
            """,
            (
                loan.due_date,
                loan.user_id,
                loan.book_id
            )
        )

    def return_book(self, user: User, book: Book) -> None:
        state.lib.return_book(user, book)

        self.db.execute(
            """
            UPDATE borrowings
            SET returned_at = ?
            WHERE user_id = ? and book_id = ? and returned_at IS NULL
            """,
            (
                date.today(),
                user.id,
                book.id
            )
        )

    def return_all_items(self, user: User) -> None:
        state.lib.return_all_items(user)

        self.db.execute(
            """
            UPDATE borrowings
            SET returned_at = ?
            WHERE user_id = ? and returned_at IS NULL
            """,
            (
                date.today(),
                user.id
            )
        )
