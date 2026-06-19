from data.database_manager import DatabaseManager
from exceptions.book_exceptions import MissingItemError
from utils.uid import generate_uid
from datetime import date, datetime, timedelta
from typing import Self


class BorrowingRepository:
    def __init__(
            self,
            db: DatabaseManager,
            book_repo,
            user_repo,
            waitlist_repo
    ):
        self.db = db
        self.book_repo = book_repo
        self.user_repo = user_repo
        self.waitlist_repo = waitlist_repo

    def borrow_book(
        self,
        user_id: str,
        book_id: str,
        days: int = 30
    ) -> None:
        book = self.book_repo.find_book_by_id(book_id)
        if not book:
            raise MissingItemError(
                f"Book {book_id} does not exist."
            )
        available = self.book_repo.is_book_available(book_id)

        if book["type"] == 'book' and not available["available"]:
            self.waitlist_repo.add_user_to_waitlist(user_id, book_id)
        else:
            loans = self.get_all_loans()
            loan_ids = set()

            for loan in loans:
                loan_ids.add(loan["id"])

            uid = generate_uid(loan_ids)
            days = min(days, 30)
            due_to = date.today() + timedelta(days=days)
            self.db.execute(
                """
                INSERT INTO borrowings(
                id, user_id, book_id, type, 
                borrowed_at, due_to, returned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uid,
                    user_id,
                    book_id,
                    book["type"],
                    date.today(),
                    due_to if book["type"] == 'book' else None,
                    None
                )
            )

    def extend_loan(self, book_id: str, user_id: str, days: int = 30) -> None:
        loan = self.db.fetchone(
            """
            SELECT id, due_to
            FROM borrowings
            WHERE book_id = ?
                AND user_id = ?
                AND returned_at IS NULL
            """,
            (
                book_id,
                user_id
            )
        )

        loan_id = loan["id"]
        due_to = datetime.strptime(str(loan["due_to"]), '%Y-%m-%d').date()
        due_to = due_to + timedelta(days=days)

        self.db.execute(
            """
            UPDATE borrowings
            SET due_to = ?
            WHERE id = ?
            """,
            (
                due_to,
                loan_id
            )
        )

    def return_book(self, user_id: str, book_id: str) -> None:
        self.db.execute(
            """
            UPDATE borrowings
            SET returned_at = ?
            WHERE user_id = ? 
                AND book_id = ? 
                AND returned_at IS NULL
            """,
            (
                date.today(),
                user_id,
                book_id
            )
        )

        if self.book_repo.is_book_available(book_id):
            self.waitlist_repo.manage_queue(book_id)

    def return_all_items(self, user_id: str) -> None:
        borrow_books = self.user_repo.get_all_books_from_user(user_id)
        books = []

        for book in borrow_books:
            books.append(book["id"])

        self.db.execute(
            """
            UPDATE borrowings
            SET returned_at = ?
            WHERE user_id = ? 
                AND returned_at IS NULL
            """,
            (
                date.today(),
                user_id
            )
        )

        for book in books:
            self.waitlist_repo.manage_queue(book)

    def get_all_loans(self) -> Self:
        return self.db.fetchall(
            """
            SELECT id
            FROM borrowings
            """
        )
