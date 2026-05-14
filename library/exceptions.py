# Exceptions
class InvalidUser(Exception):
    # Raise an exception for invalid user initialization
    pass

class InvalidBook(Exception):
    # Raise an exception for invalid book initialization
    pass

class NoUser(Exception):
    # Raise an exception when the user does not exist
    pass

class NoBook(Exception):
    # Raise an exception when the book does not exist
    pass

class InvalidNumberOfBooks(Exception):
    # Raise an exception when provide invalid number of books
    pass

class UserWithItemsCannotBeUnregistered(Exception):
    # Raise an exception when attempting to unregister a user with borrowed books
    pass