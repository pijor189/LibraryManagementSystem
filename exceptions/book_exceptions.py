from .base import LibraryError


class ItemError(LibraryError):
    """Basic exceptions for item exceptions"""
    pass


class ItemInitializationError(ItemError):
    """Raise an exceptions for invalid item initialization"""
    pass


class BookInitializationError(ItemError):
    """Raise an exceptions for invalid book initialization"""
    pass


class EBookInitializationError(ItemError):
    """Raise an exceptions for invalid ebook initialization"""
    pass


class MissingItemError(ItemError):
    """Raise an exceptions when the item does not exist"""
    pass
