from .base import LibraryError


class UserError(LibraryError):
    """Basic exceptions for user exceptions"""
    pass


class InvalidUser(UserError):
    """Raise an exceptions for invalid user initialization"""
    pass


class NoUser(UserError):
    """Raise an exceptions when the user does not exist"""
    pass
