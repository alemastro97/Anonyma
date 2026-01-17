"""
Input validation for Anonyma Core.

Provides Pydantic models for validating user inputs
before processing, ensuring data integrity and security.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from .exceptions import ValidationError, TextTooLongError, EmptyTextError


class AnonymizationModeEnum(str, Enum):
    """Supported anonymization modes"""

    REDACT = "redact"
    SUBSTITUTE = "substitute"
    VISUAL_REDACT = "visual_redact"


class LanguageCode(str, Enum):
    """Supported language codes"""

    ITALIAN = "it"
    ENGLISH = "en"


class AnonymizationRequest(BaseModel):
    """
    Validation model for anonymization requests.

    Attributes:
        text: Input text to anonymize
        mode: Anonymization mode to use
        language: Language code for detection
        confidence_threshold: Optional override for detection confidence
    """

    text: str = Field(..., description="Text to anonymize")
    mode: AnonymizationModeEnum = Field(
        default=AnonymizationModeEnum.REDACT, description="Anonymization mode"
    )
    language: LanguageCode = Field(default=LanguageCode.ITALIAN, description="Language code")
    confidence_threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Detection confidence threshold (0.0 to 1.0)"
    )

    @validator("text")
    def validate_text(cls, v):
        """Validate input text"""
        if not v or not v.strip():
            raise EmptyTextError()

        # Default max length (can be overridden by config)
        max_length = 10_000_000  # 10MB
        if len(v) > max_length:
            raise TextTooLongError(len(v), max_length)

        return v

    class Config:
        use_enum_values = True


class DetectionRequest(BaseModel):
    """
    Validation model for detection requests.

    Attributes:
        text: Input text to analyze
        language: Language code
        confidence_threshold: Minimum confidence for detections
    """

    text: str = Field(..., description="Text to analyze for PII")
    language: LanguageCode = Field(default=LanguageCode.ITALIAN, description="Language code")
    confidence_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum detection confidence"
    )

    @validator("text")
    def validate_text(cls, v):
        """Validate input text"""
        if not v or not v.strip():
            raise EmptyTextError()

        max_length = 10_000_000
        if len(v) > max_length:
            raise TextTooLongError(len(v), max_length)

        return v

    class Config:
        use_enum_values = True


class Detection(BaseModel):
    """
    Validation model for detection results.

    Attributes:
        entity_type: Type of PII detected (EMAIL, PHONE, etc.)
        start: Start position in text
        end: End position in text
        confidence: Detection confidence score (0.0 to 1.0)
        text: The detected text snippet
    """

    entity_type: str = Field(..., description="Type of entity detected")
    start: int = Field(..., ge=0, description="Start position in text")
    end: int = Field(..., ge=0, description="End position in text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    text: str = Field(..., description="Detected text")

    @validator("end")
    def validate_positions(cls, v, values):
        """Ensure end > start"""
        if "start" in values and v <= values["start"]:
            raise ValueError("end position must be greater than start position")
        return v


class BatchAnonymizationRequest(BaseModel):
    """
    Validation model for batch anonymization requests.

    Attributes:
        texts: List of texts to anonymize
        mode: Anonymization mode
        language: Language code
    """

    texts: List[str] = Field(..., min_items=1, max_items=100, description="Texts to anonymize")
    mode: AnonymizationModeEnum = Field(
        default=AnonymizationModeEnum.REDACT, description="Anonymization mode"
    )
    language: LanguageCode = Field(default=LanguageCode.ITALIAN, description="Language code")

    @validator("texts")
    def validate_texts(cls, v):
        """Validate each text in batch"""
        for idx, text in enumerate(v):
            if not text or not text.strip():
                raise ValidationError(f"Text at index {idx} is empty", {"index": idx})

            max_length = 10_000_000
            if len(text) > max_length:
                raise TextTooLongError(len(text), max_length)

        return v

    class Config:
        use_enum_values = True


def validate_text_input(text: str, max_length: int = 10_000_000) -> str:
    """
    Validate text input.

    Args:
        text: Input text to validate
        max_length: Maximum allowed text length

    Returns:
        Validated text

    Raises:
        EmptyTextError: If text is empty or whitespace
        TextTooLongError: If text exceeds max_length
    """
    if not text or not text.strip():
        raise EmptyTextError()

    if len(text) > max_length:
        raise TextTooLongError(len(text), max_length)

    return text


def validate_detections(detections: List[Dict[str, Any]]) -> List[Detection]:
    """
    Validate detection results.

    Args:
        detections: List of detection dictionaries

    Returns:
        List of validated Detection objects

    Raises:
        ValidationError: If detections are invalid
    """
    validated = []
    for detection in detections:
        try:
            validated.append(Detection(**detection))
        except Exception as e:
            raise ValidationError(
                f"Invalid detection: {str(e)}", {"detection": detection, "error": str(e)}
            )

    return validated


def validate_confidence_threshold(threshold: float) -> float:
    """
    Validate confidence threshold.

    Args:
        threshold: Confidence threshold (0.0 to 1.0)

    Returns:
        Validated threshold

    Raises:
        ValidationError: If threshold is out of range
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValidationError(
            f"Confidence threshold must be between 0.0 and 1.0, got {threshold}",
            {"threshold": threshold},
        )

    return threshold
