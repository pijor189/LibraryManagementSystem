from data.database_manager import DatabaseManager
from typing import Self

class UserRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def add_user(self, name: str) -> None:
        self.db.execute(
            "INSERT INTO users(name) VALUES(?)",
            name,
        )

    def get_all_users(self) -> Self:
        return self.db.fetchall(
            "SELECT * from users"
        )
