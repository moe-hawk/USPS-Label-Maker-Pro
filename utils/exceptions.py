class AppError(Exception):
    """User-facing application error."""

class ValidationError(AppError):
    """Validation-related error."""

class ProviderError(AppError):
    """External provider/API error."""

class CancelledError(AppError):
    """Raised when a background job is cancelled."""
