import data.state as state
from library.user import User
from data.database_manager import DatabaseManager
from typing import Self


class UserRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def register_user(self, name: str) -> None:
        user = User(name)
        state.lib.register_user(user)

        self.db.execute(
            """
            INSERT INTO users(id, name) VALUES (?, ?)
            """,
            (
                user.id,
                name,
            )
        )

    def unregister_user(self, user: User) -> None:
        id = user.id
        state.lib.unregister_user(user)

        self.db.execute(
            """
            DELETE FROM users
            WHERE id = ?
            """,
            (
                id,
            )
        )

    def get_all_users(self) -> Self:
        return self.db.fetchall(
            "SELECT * FROM users"
        )

    def find_user_by_id(self, id: int) -> Self:
        return self.db.fetchone(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (
                id,
            )
        )

    def find_user_by_name(self, name: str) -> Self:
        return self.db.fetchall(
            """
            SELECT *
            FROM users
            WHERE name = ?
            """,
            (
                name,
            )
        )
