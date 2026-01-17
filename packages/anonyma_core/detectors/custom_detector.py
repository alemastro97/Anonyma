"""
Custom pattern detector for user-defined sensitive data.

Allows users to define their own patterns for detecting any type of sensitive information,
not just standard PII. Examples:
- Chemical compound names (e.g., "Compound-XYZ-123")
- Internal IDs (e.g., "EMP-001234", "PRJ-ALPHA-2024")
- Proprietary codes
- Domain-specific identifiers
- Any regex-matchable pattern
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .base import BaseDetector
from ..logging_config import get_logger
from ..exceptions import ValidationError

logger = get_logger(__name__)


@dataclass
class CustomPattern:
    """
    Custom pattern definition.

    Attributes:
        name: Pattern name (used as entity_type)
        pattern: Regex pattern to match
        confidence: Confidence score for matches (0.0 to 1.0)
        description: Human-readable description
        flags: Regex flags (default: re.IGNORECASE)
        validate: Optional validation function
    """

    name: str
    pattern: str
    confidence: float = 0.9
    description: str = ""
    flags: int = re.IGNORECASE
    validate: Optional[callable] = None

    def __post_init__(self):
        """Validate and compile pattern"""
        if not self.name:
            raise ValidationError("Pattern name cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValidationError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")

        try:
            self._compiled = re.compile(self.pattern, self.flags)
            logger.debug(f"Custom pattern compiled: {self.name}")
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern '{self.pattern}': {e}")

    def match(self, text: str) -> List[re.Match]:
        """Find all matches in text"""
        return list(self._compiled.finditer(text))

    def is_valid_match(self, match_text: str) -> bool:
        """
        Check if match is valid using optional validation function.

        Args:
            match_text: Matched text

        Returns:
            True if valid (or no validator), False otherwise
        """
        if self.validate is None:
            return True

        try:
            return self.validate(match_text)
        except Exception as e:
            logger.warning(f"Validation function failed for '{match_text}': {e}")
            return False


class CustomPatternDetector(BaseDetector):
    """
    Detector for user-defined custom patterns.

    Allows detection of any sensitive data based on regex patterns,
    not limited to standard PII types.

    Example:
        >>> detector = CustomPatternDetector()
        >>>
        >>> # Add chemical compound pattern
        >>> detector.add_pattern(
        ...     name="COMPOUND_NAME",
        ...     pattern=r"Compound-[A-Z]{3}-\d{3}",
        ...     description="Chemical compound identifier"
        ... )
        >>>
        >>> # Add employee ID pattern
        >>> detector.add_pattern(
        ...     name="EMPLOYEE_ID",
        ...     pattern=r"EMP-\d{6}",
        ...     description="Employee identifier"
        ... )
        >>>
        >>> # Detect
        >>> text = "Study on Compound-XYZ-123 by employee EMP-001234"
        >>> detections = detector.detect(text)
        >>> print(len(detections))  # 2
    """

    def __init__(self, patterns: Optional[List[CustomPattern]] = None):
        """
        Initialize custom pattern detector.

        Args:
            patterns: List of custom patterns (optional)
        """
        super().__init__()
        self._patterns: Dict[str, CustomPattern] = {}

        if patterns:
            for pattern in patterns:
                self.add_pattern_object(pattern)

        logger.info(f"CustomPatternDetector initialized with {len(self._patterns)} patterns")

    def add_pattern(
        self,
        name: str,
        pattern: str,
        confidence: float = 0.9,
        description: str = "",
        flags: int = re.IGNORECASE,
        validate: Optional[callable] = None,
    ) -> None:
        """
        Add a custom pattern.

        Args:
            name: Pattern name (entity type)
            pattern: Regex pattern
            confidence: Confidence score (0.0 to 1.0)
            description: Pattern description
            flags: Regex flags
            validate: Optional validation function

        Raises:
            ValidationError: If pattern is invalid
        """
        custom_pattern = CustomPattern(
            name=name,
            pattern=pattern,
            confidence=confidence,
            description=description,
            flags=flags,
            validate=validate,
        )

        self.add_pattern_object(custom_pattern)

    def add_pattern_object(self, pattern: CustomPattern) -> None:
        """
        Add a CustomPattern object.

        Args:
            pattern: CustomPattern object

        Raises:
            ValidationError: If pattern name already exists
        """
        if pattern.name in self._patterns:
            logger.warning(f"Overwriting existing pattern: {pattern.name}")

        self._patterns[pattern.name] = pattern
        logger.info(
            f"Added custom pattern: {pattern.name}",
            extra={"extra_fields": {"pattern": pattern.pattern, "confidence": pattern.confidence}},
        )

    def remove_pattern(self, name: str) -> bool:
        """
        Remove a pattern by name.

        Args:
            name: Pattern name

        Returns:
            True if removed, False if not found
        """
        if name in self._patterns:
            del self._patterns[name]
            logger.info(f"Removed custom pattern: {name}")
            return True

        return False

    def get_pattern(self, name: str) -> Optional[CustomPattern]:
        """
        Get pattern by name.

        Args:
            name: Pattern name

        Returns:
            CustomPattern or None if not found
        """
        return self._patterns.get(name)

    def list_patterns(self) -> List[str]:
        """
        List all pattern names.

        Returns:
            List of pattern names
        """
        return list(self._patterns.keys())

    def detect(self, text: str, language: str = "it") -> List[Dict[str, Any]]:
        """
        Detect all custom patterns in text.

        Args:
            text: Text to analyze
            language: Language (not used for custom patterns)

        Returns:
            List of detections
        """
        if not self._patterns:
            logger.debug("No custom patterns defined, returning empty list")
            return []

        logger.debug(
            f"Running custom pattern detection",
            extra={"extra_fields": {"patterns_count": len(self._patterns), "text_length": len(text)}},
        )

        detections = []

        for pattern_name, custom_pattern in self._patterns.items():
            matches = custom_pattern.match(text)

            for match in matches:
                match_text = match.group()

                # Validate match if validator provided
                if not custom_pattern.is_valid_match(match_text):
                    logger.debug(
                        f"Match failed validation: {match_text}",
                        extra={"extra_fields": {"pattern": pattern_name}},
                    )
                    continue

                detection = {
                    "entity_type": pattern_name,
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": custom_pattern.confidence,
                    "text": match_text,
                }

                detections.append(detection)

                logger.debug(
                    f"Detected {pattern_name}: '{match_text}'",
                    extra={
                        "extra_fields": {
                            "pattern": pattern_name,
                            "start": match.start(),
                            "end": match.end(),
                        }
                    },
                )

        logger.info(
            f"Custom pattern detection completed",
            extra={"extra_fields": {"detections_found": len(detections)}},
        )

        return detections

    @property
    def name(self) -> str:
        return "CustomPatternDetector"

    @property
    def supported_languages(self) -> List[str]:
        # Custom patterns are language-agnostic
        return ["*"]  # All languages

    def __repr__(self) -> str:
        return f"CustomPatternDetector(patterns={len(self._patterns)})"


# Predefined pattern collections for common use cases

class CompoundPatternDetector(CustomPatternDetector):
    """Detector for chemical compound identifiers"""

    def __init__(self):
        patterns = [
            CustomPattern(
                name="COMPOUND_ID",
                pattern=r"Compound-[A-Z]{3,5}-\d{3,6}",
                confidence=0.95,
                description="Chemical compound identifier (e.g., Compound-XYZ-123)",
            ),
            CustomPattern(
                name="CAS_NUMBER",
                pattern=r"\d{2,7}-\d{2}-\d",
                confidence=0.90,
                description="CAS Registry Number",
            ),
            CustomPattern(
                name="DRUG_CODE",
                pattern=r"DRG-[A-Z0-9]{4,8}",
                confidence=0.95,
                description="Drug code identifier",
            ),
        ]
        super().__init__(patterns=patterns)


class InternalIDDetector(CustomPatternDetector):
    """Detector for internal company identifiers"""

    def __init__(self):
        patterns = [
            CustomPattern(
                name="EMPLOYEE_ID",
                pattern=r"EMP-\d{6,8}",
                confidence=0.95,
                description="Employee ID",
            ),
            CustomPattern(
                name="PROJECT_CODE",
                pattern=r"PRJ-[A-Z]{3,5}-\d{4}",
                confidence=0.95,
                description="Project code",
            ),
            CustomPattern(
                name="DOCUMENT_ID",
                pattern=r"DOC-\d{8,10}",
                confidence=0.95,
                description="Document ID",
            ),
            CustomPattern(
                name="CONTRACT_ID",
                pattern=r"CTR-[A-Z]{2}\d{6}",
                confidence=0.95,
                description="Contract ID",
            ),
        ]
        super().__init__(patterns=patterns)
