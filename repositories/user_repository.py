from typing import Any

from data.database_manager import DatabaseManager
from exceptions.library_exceptions import UserHasBorrowedItemsError
from exceptions.user_exceptions import MissingUserError, UserInitializationError
from utils.uid import generate_uid


class UserRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def register_user(self, name: str) -> str:
        if not isinstance(name, str) or name.strip() == "":
            raise UserInitializationError("Invalid user initialization")

        users = self.get_all_users()
        users_id = set()

        for user in users:
            users_id.add(user["id"])

        uid = generate_uid(users_id)

        self.db.execute(
            """
            INSERT INTO users(id, name)
            VALUES (?, ?)
            """,
            (
                uid,
                name
            )
        )

        return uid

    def unregister_user(self, user_id: str) -> None:
        user = self.find_user_by_id(user_id)

        if user:
            borrowed_books = self.db.fetchall(
                """
                SELECT book_id
                FROM borrowings
                WHERE user_id == ?
                    AND returned_at IS NULL
                """,
                (
                    user_id,
                )
            )
            if borrowed_books:
                raise UserHasBorrowedItemsError(
                    f"User {user_id} has borrowed books "
                    "and must return them before unregistering."
                )
            else:
                self.db.execute(
                    """
                    DELETE FROM users
                    WHERE id = ?
                    """,
                    (
                        user_id,
                    )
                )
                print(f"Successfully unregistered user {user_id}.")
        else:
            raise MissingUserError(
                f"User {user_id} does not exist."
            )

    def find_user_by_id(self, user_id: str) -> Any:
        return self.db.fetchone(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (
                user_id,
            )
        )

    def find_user_by_name(self, name: str) -> list[Any]:
        name = " ".join(name.lower().split())

        return self.db.fetchall(
            """
            SELECT *
            FROM users
            WHERE LOWER(name) = ?
            """,
            (
                name,
            )
        )

    def get_all_users(self) -> list[Any]:
        return self.db.fetchall(
            "SELECT * FROM users"
        )

    def get_all_books_from_user(self, user_id: str) -> list[Any]:
        return self.db.fetchall(
            """
            SELECT b.id, b.title, b.author, 'book' AS type, br.due_to
            FROM books b
            JOIN borrowings br
            ON b.id = br.book_id
            WHERE br.user_id = ?
                AND br.returned_at IS NULL
            """,
            (
                user_id,
            )
        )

    def get_all_ebooks_from_user(self, user_id: str) -> list[Any]:
        return self.db.fetchall(
            """
            SELECT e.id, e.title, e.author, 'ebook' AS type
            FROM ebooks e
            JOIN borrowings br
            ON e.id = br.book_id
            WHERE br.user_id = ?
                AND br.returned_at IS NULL
            """,
            (
                user_id,
            )
        )
