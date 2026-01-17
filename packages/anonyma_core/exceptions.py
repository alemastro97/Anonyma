"""
Custom exceptions for Anonyma Core.

Provides specific exception types for different error scenarios,
making error handling more precise and informative.
"""


class AnonymaException(Exception):
    """
    Base exception for all Anonyma errors.

    All custom exceptions inherit from this base class,
    allowing catch-all error handling when needed.
    """

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(AnonymaException):
    """
    Configuration-related errors.

    Raised when:
    - Invalid configuration values
    - Missing required configuration
    - Configuration file errors
    """

    pass


class DetectionError(AnonymaException):
    """
    PII detection errors.

    Raised when:
    - Detector initialization fails
    - Detection process fails
    - Model loading errors
    """

    pass


class AnonymizationError(AnonymaException):
    """
    Anonymization process errors.

    Raised when:
    - Anonymization mode fails
    - Invalid anonymization parameters
    - Processing errors
    """

    pass


class ValidationError(AnonymaException):
    """
    Input validation errors.

    Raised when:
    - Invalid input text (too long, wrong type)
    - Invalid parameters
    - Input doesn't meet requirements
    """

    pass


class ModelLoadingError(DetectionError):
    """
    ML model loading errors.

    Raised when:
    - Flair models fail to load
    - Presidio models unavailable
    - Model file corruption
    """

    pass


class DocumentProcessingError(AnonymaException):
    """
    Document processing errors.

    Raised when:
    - Document format unsupported
    - Document parsing fails
    - Document reconstruction fails
    """

    pass


class SecurityError(AnonymaException):
    """
    Security-related errors.

    Raised when:
    - Encryption/decryption fails
    - Authentication fails
    - Authorization denied
    """

    pass


class StorageError(AnonymaException):
    """
    Storage operation errors.

    Raised when:
    - File I/O errors
    - Database errors
    - Cache errors
    """

    pass


class UnsupportedLanguageError(DetectionError):
    """
    Unsupported language error.

    Raised when:
    - Language not supported by detectors
    - Language code invalid
    """

    def __init__(self, language: str, supported_languages: list = None):
        message = f"Unsupported language: {language}"
        details = {"language": language}
        if supported_languages:
            details["supported_languages"] = supported_languages
            message += f". Supported: {', '.join(supported_languages)}"
        super().__init__(message, details)


class InvalidModeError(AnonymizationError):
    """
    Invalid anonymization mode error.

    Raised when:
    - Anonymization mode not recognized
    - Mode not available
    """

    def __init__(self, mode: str, available_modes: list = None):
        message = f"Invalid anonymization mode: {mode}"
        details = {"mode": mode}
        if available_modes:
            details["available_modes"] = available_modes
            message += f". Available: {', '.join(available_modes)}"
        super().__init__(message, details)


class TextTooLongError(ValidationError):
    """
    Text exceeds maximum length.

    Raised when:
    - Input text exceeds configured maximum
    """

    def __init__(self, text_length: int, max_length: int):
        message = f"Text too long: {text_length} characters (max: {max_length})"
        details = {"text_length": text_length, "max_length": max_length}
        super().__init__(message, details)


class EmptyTextError(ValidationError):
    """
    Empty or whitespace-only text.

    Raised when:
    - Input text is empty
    - Input text is only whitespace
    """

    def __init__(self):
        super().__init__("Input text is empty or contains only whitespace")


class DetectionConfidenceError(DetectionError):
    """
    Detection confidence issues.

    Raised when:
    - No detections above confidence threshold
    - Confidence scoring fails
    """

    pass
