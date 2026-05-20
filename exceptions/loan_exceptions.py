from .base import LibraryError


class LoanError(LibraryError):
    """Basic exceptions for loan exceptions"""
    pass


class InvalidLoan(LoanError):
    """Raise an exceptions for invalid loan initialization"""
    pass


class InvalidExtendDays(LoanError):
    """Raised when the number of days is less than or equal to 0"""
    pass
