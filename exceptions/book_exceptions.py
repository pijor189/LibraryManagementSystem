from .base import LibraryError


class BookError(LibraryError):
    """Basic exceptions for book exceptions"""
    pass


class InvalidBook(BookError):
    """Raise an exceptions for invalid book initialization"""
    pass


class NoBook(BookError):
    """Raise an exceptions when the book does not exist"""
    pass
