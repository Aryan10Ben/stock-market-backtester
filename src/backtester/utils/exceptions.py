"""Custom exceptions for the backtesting system."""


class BacktesterError(Exception):
    """Base exception for all backtester errors."""


class ConfigError(BacktesterError):
    """Raised when configuration is invalid or cannot be loaded."""


class DataFetchError(BacktesterError):
    """Raised when historical data cannot be fetched from the provider."""


class DataValidationError(BacktesterError):
    """Raised when fetched data fails validation checks."""


class BacktestError(BacktesterError):
    """Raised when the backtesting engine encounters a fatal error."""
