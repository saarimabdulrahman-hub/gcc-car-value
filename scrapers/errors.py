"""Standard scraper exception hierarchy."""


class ScraperError(Exception):
    """Base exception for all scraper errors."""
    def __init__(self, message: str = "", retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class NetworkError(ScraperError):
    """Connection failure, timeout, DNS error."""


class RateLimitError(ScraperError):
    """Rate limited by the target site (HTTP 429 or similar)."""


class ParserError(ScraperError):
    """Failed to parse page content — site structure may have changed."""


class CaptchaError(ScraperError):
    """CAPTCHA or bot detection encountered."""


class AuthenticationError(ScraperError):
    """Login or authentication failure."""


class TemporaryFailure(ScraperError):
    """Transient error — retry may succeed."""
    def __init__(self, message: str = ""):
        super().__init__(message, retryable=True)


class PermanentFailure(ScraperError):
    """Non-recoverable error — retry will not help."""
    def __init__(self, message: str = ""):
        super().__init__(message, retryable=False)


class StorageError(ScraperError):
    """Failed to store raw data or results."""


class ValidationError(ScraperError):
    """Scraped data failed validation."""
