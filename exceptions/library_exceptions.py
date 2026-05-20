from .base import LibraryError


class LibraryOperationError(LibraryError):
    """Basic exceptions for library operation exceptions"""
    pass


class InvalidNumberOfBooks(LibraryError):
    """Raise an exceptions when provide invalid number of books"""
    pass


class UserWithItemsCannotBeUnregistered(LibraryError):
    """Raise an exceptions when attempting to unregister a user with borrowed books"""
    pass
