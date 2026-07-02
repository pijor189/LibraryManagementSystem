import sqlite3
from datetime import date, datetime
from typing import Any

sqlite3.register_adapter(date, lambda d: d.isoformat())
sqlite3.register_adapter(datetime, lambda d: d.isoformat())


class DatabaseManager:
    def __init__(self, db_name: str="data/db/library.db") -> None:
        self.conn = sqlite3.connect(db_name)
        self.conn.text_factory = str
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, query: str, params: Any=()) -> None:
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchall(self, query: str, params: Any=()) -> list[Any]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query: str, params: Any=()) -> Any:
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self) -> None:
        self.conn.close()
