from .base import LibraryError


class BookError(LibraryError):
    """Basic exceptions for book exceptions"""
    pass


class BookInitializationError(BookError):
    """Raise an exceptions for invalid book initialization"""
    pass


class MissingBookError(BookError):
    """Raise an exceptions when the book does not exist"""
    pass
