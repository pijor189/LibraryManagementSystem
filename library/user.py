from exceptions.user_exceptions import UserInitializationError


class User:
    LIMIT_OF_BOOKS = 3

    def __init__(self, name: str):
        if not isinstance(name, str) or name.strip() == "":
            raise UserInitializationError("Invalid user initialization")
        self.id = 0
        self.name = name
        self.borrowed_physical_books = {}
        self.borrowed_ebooks = {}

    def __str__(self):
        return f"User name: {self.name}"
