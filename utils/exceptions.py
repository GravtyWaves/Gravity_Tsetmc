"""
Exception classes for Gravity TSETMC project
"""


class GravityTSEException(Exception):
    """Base exception for Gravity TSETMC project"""
    pass


class APIException(GravityTSEException):
    """Exception raised for API-related errors"""
    pass


class APITimeoutException(APIException):
    """Exception raised when API request times out"""
    pass


class APIConnectionException(APIException):
    """Exception raised when API connection fails"""
    pass


class SymbolNotFoundException(GravityTSEException):
    """Exception raised when a stock symbol is not found"""
    pass


class DataValidationException(GravityTSEException):
    """Exception raised when data validation fails"""
    pass


class DatabaseException(GravityTSEException):
    """Exception raised for database-related errors"""
    pass


class DateValidationException(GravityTSEException):
    """Exception raised when date validation fails"""
    pass
