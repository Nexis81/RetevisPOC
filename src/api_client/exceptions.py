"""
Custom exceptions for Retivis POC API client
"""


class RetivisPOCError(Exception):
    """Base exception for Retivis POC API errors"""

    pass


class AuthenticationError(RetivisPOCError):
    """Raised when authentication fails"""

    pass


class ConnectionError(RetivisPOCError):
    """Raised when connection to API fails"""

    pass


class ValidationError(RetivisPOCError):
    """Raised when request validation fails"""

    pass



