import logging
import cli.interface as interface
import data.state as state

# debug / release
MODE = "release"

if MODE == "debug":
    from pathlib import Path
    from data.init_db import initialize_database, migrate_to_db_and_object
    from repositories.book_repository import BookRepository
    from repositories.borrowing_repository import BorrowingRepository
    from repositories.user_repository import UserRepository
elif MODE == "release":
    from data.migrate_books import migrate_books_to_object, migrate_ebooks_to_object
    from data.migrate_users import migrate_users_to_object
    from data.migrate_borrowings import migrate_borrowings_to_object


logging.disable(logging.CRITICAL)


if __name__ == "__main__":

    if MODE == "debug":
        db_debug_path = "data/db/library_debug.db"
        db_debug_file = Path(db_debug_path)
        if db_debug_file.exists():
            state.db.close()
            db_debug_file.unlink()


            state.db = state.get_db(db_debug_path)
            initialize_database(state.db)
            migrate_to_db_and_object(state.db)
            state.book_repository = BookRepository(state.db)
            state.borrowing_repository = BorrowingRepository(state.db)
            state.user_repository = UserRepository(state.db)
    elif MODE == "release":
        migrate_books_to_object(state.db)
        migrate_ebooks_to_object(state.db)
        migrate_users_to_object(state.db)
        migrate_borrowings_to_object(state.db)

    interface.run_cli()
