class TSEError(Exception):
    """Base exception for TSE related errors"""
    pass


class TSEConnectionError(TSEError):
    """Raised when a network or HTTP issue occurs communicating with TSE"""
    pass


class TSEValidationError(TSEError):
    """Raised when input validation (e.g., dates or symbol formats) fails"""
    pass
