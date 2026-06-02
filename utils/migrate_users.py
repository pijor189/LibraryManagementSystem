import json
from data.database_manager import DatabaseManager
from utils.uid import generate_uid


library_users_id = set()


def migrate_users():
    db = DatabaseManager()

    global library_users_id

    with open("data/users.json", "r") as f:
        users = json.load(f)

    for user in users:
        db.execute(
            """
            INSERT INTO users(id, name)
            VALUES (?, ?)
            """,
            (
                generate_uid(library_users_id),
                user["name"]
            )
        )
