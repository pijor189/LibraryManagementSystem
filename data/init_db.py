from data.database_manager import DatabaseManager
from data.migrate_books import migrate_books_from_json, migrate_ebooks_from_json
from data.migrate_users import migrate_users_from_json


def initialize_database(db: DatabaseManager) -> None:
    with open("data/db/schema.sql", "r") as f:
        db.cursor.executescript(f.read())
        db.conn.commit()


def migrate_to_db_and_object(db: DatabaseManager) -> None:
    migrate_books_from_json(db)
    migrate_ebooks_from_json(db)
    migrate_users_from_json(db)
