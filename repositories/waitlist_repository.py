from datetime import datetime

from data.database_manager import DatabaseManager


class WaitlistRepository:
    def __init__(
            self,
            db: DatabaseManager,
            borrow_repo
    ):
        self.db = db
        self.borrow_repo = borrow_repo

    def add_user_to_waitlist(
            self,
            user_id: str,
            book_id: str
    ) -> None:
        self.db.execute(
            """
            INSERT INTO waitlist(user_id, book_id, created_at)
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                book_id,
                datetime.now()
            )
        )
        print(f"User {user_id} has been added to the waitlist.")

    def manage_queue(self, book_id: str) -> None:
        waitlist_users = self.db.fetchall(
            """
            SELECT id, user_id
            FROM waitlist
            WHERE book_id = ?
            ORDER BY created_at
            """,
            (
                book_id,
            )
        )

        for wait_user in waitlist_users:
            user_id = self.db.fetchone(
                """
                SELECT id
                FROM users u
                WHERE u.id = ?
                    AND (
                        SELECT COUNT(*)
                        from borrowings b
                        WHERE u.id = b.user_id
                            AND b.due_to IS NOT NULL
                            AND b.returned_at IS NULL
                    ) < 3
                """,
                (
                    wait_user["user_id"],
                )
            )

            if user_id:
                self.borrow_repo.borrow_book(user_id["id"], book_id)

                self.db.execute(
                    """
                    DELETE FROM waitlist
                    WHERE id = ?
                    """,
                    (
                        wait_user["id"],
                    )
                )
                break
            else:
                print(f"User {wait_user["user_id"]} "
                      "has reached the book limit.")
