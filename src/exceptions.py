"""
Custom exceptions for the Eclipse Sites application
Provides specific exception types for better error handling
"""


class EclipseSitesError(Exception):
    """Base exception for all Eclipse Sites errors"""
    pass


class ConfigurationError(EclipseSitesError):
    """Raised when there's a configuration error"""
    pass


class ScrapingError(EclipseSitesError):
    """Base exception for scraping-related errors"""
    pass


class IGMEScrapingError(ScrapingError):
    """Raised when IGME site scraping fails"""
    pass


class EclipseCheckError(ScrapingError):
    """Raised when eclipse visibility checking fails"""
    pass


class CloudCoverageError(ScrapingError):
    """Raised when cloud coverage scraping fails"""
    pass


class HorizonImageError(ScrapingError):
    """Raised when horizon image downloading fails"""
    pass


class DataValidationError(EclipseSitesError):
    """Raised when data validation fails"""
    pass


class CoordinateError(DataValidationError):
    """Raised when coordinate data is invalid"""
    pass


class WebDriverError(EclipseSitesError):
    """Raised when WebDriver setup or operation fails"""
    pass


class NetworkError(EclipseSitesError):
    """Raised when network requests fail"""
    pass


class TimeoutError(NetworkError):
    """Raised when a request times out"""
    pass


class RateLimitError(NetworkError):
    """Raised when rate limiting is triggered"""
    pass


class FileOperationError(EclipseSitesError):
    """Raised when file operations fail"""
    pass


class CSVError(FileOperationError):
    """Raised when CSV operations fail"""
    pass


class KMLError(FileOperationError):
    """Raised when KML operations fail"""
    pass


# Exception context managers for better error handling

class ScrapingContext:
    """Context manager for scraping operations with automatic error handling"""
    
    def __init__(self, site_code: str, operation: str):
        self.site_code = site_code
        self.operation = operation
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the error but don't suppress it
            return False
        return True


# Helper functions for error handling

def handle_scraping_error(error: Exception, site_code: str, operation: str) -> dict:
    """Handle scraping errors and return error info
    
    Args:
        error: The exception that occurred
        site_code: Site code being processed
        operation: Operation being performed
    
    Returns:
        Dictionary with error information
    """
    error_info = {
        'site_code': site_code,
        'operation': operation,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'status': 'error'
    }
    return error_info


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable
    
    Args:
        error: The exception to check
    
    Returns:
        True if the error should be retried
    """
    retryable_types = (
        NetworkError,
        TimeoutError,
        WebDriverError,
    )
    return isinstance(error, retryable_types)

# Made with Bob