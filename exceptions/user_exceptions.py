from .base import LibraryError


class UserError(LibraryError):
    """Basic exceptions for user exceptions"""
    pass


class UserInitializationError(UserError):
    """Raise an exceptions for invalid user initialization"""
    pass


class MissingUserError(UserError):
    """Raise an exceptions when the user does not exist"""
    pass
