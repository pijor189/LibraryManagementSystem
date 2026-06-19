import data.library_state as state

from data.database_manager import DatabaseManager
from library.loan import Loan
from library.book import Book


def migrate_borrowings_to_object(db: DatabaseManager):
    data = db.fetchall(
        """
        SELECT * FROM borrowings
        """
    )

    for d in data:
        book = state.lib.find_book_by_id(d[2])
        user = state.lib.find_user_by_id(d[1])
        loan = Loan(user, book)
        loan.id = d[0]
        loan.borrowed_at = d[4]
        loan.due_date = d[5]
        loan.returned_at = d[6]
        state.lib.loans[loan.id] = loan
        state.lib.loans_id.add(loan.id)

    loans = db.fetchall(
        """
        SELECT id, user_id, book_id
        FROM borrowings
        WHERE returned_at IS NULL
        """
    )

    for loan in loans:
        book = state.lib.catalog[loan[2]]
        user = state.lib.users_list[loan[1]]
        if isinstance(book, Book):
            book.borrowed += 1
            user.borrowed_physical_books[loan[0]] = loan[2]
        else:
            user.borrowed_ebooks[loan[0]] = loan[2]
