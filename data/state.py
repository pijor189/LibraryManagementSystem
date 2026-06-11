from library.library import Library
from data.database_manager import DatabaseManager
from repositories.book_repository import BookRepository
from repositories.borrowing_repository import BorrowingRepository
from repositories.user_repository import UserRepository


def get_db(db_name="data/db/library.db") -> DatabaseManager:
    return DatabaseManager(db_name)


# Library initialization
lib = Library()

# Database initialization
db = get_db()

# Repositories initialization
book_repository = BookRepository(db)
borrowing_repository = BorrowingRepository(db)
user_repository = UserRepository(db)
