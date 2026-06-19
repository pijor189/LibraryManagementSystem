from data.database_manager import DatabaseManager
from repositories.book_repository import BookRepository
from repositories.borrowing_repository import BorrowingRepository
from repositories.user_repository import UserRepository
from repositories.waitlist_repository import WaitlistRepository


# Database initialization
db = DatabaseManager(db_name="data/db/library.db")

# Repositories initialization
book_repo = BookRepository(db)
user_repo = UserRepository(db)
borrow_repo = BorrowingRepository(
    db,
    book_repo,
    user_repo,
    None
)
waitlist_repo = WaitlistRepository(db, borrow_repo)

borrow_repo.waitlist_repo = waitlist_repo
