import data.library_state as state
from data.database_manager import DatabaseManager


def migrate_waitlist_to_object(db: DatabaseManager):
    data = db.fetchall(
        """
        SELECT * FROM waitlist
        """
    )

    for d in data:
        book = state.lib.find_book_by_id(d[2])
        user = state.lib.find_user_by_id(d[1])
        book.waitlist.add(user.id)
