import json

import data.library_state as state
from data.database_manager import DatabaseManager
from library.user import User


def migrate_users_from_json(db: DatabaseManager):
    with open("data/json/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    for user in users:
        data = User(user["name"])
        state.lib.register_user(data)

        db.execute(
            """
            INSERT INTO users(id, name)
            VALUES (?, ?)
            """,
            (
                data.id,
                user["name"]
            )
        )


def migrate_users_to_object(db: DatabaseManager):
    data = db.fetchall(
        """
        SELECT * FROM users
        """
    )

    for d in data:
        user = User(d[1])
        user.id = d[0]
        state.lib.users_list[user.id] = user
        state.lib.users_id.add(user.id)
