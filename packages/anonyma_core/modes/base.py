"""
Base anonymization mode interface.

Defines the contract that all anonymization modes must implement,
ensuring consistency across different anonymization strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from ..logging_config import get_logger

logger = get_logger(__name__)


class BaseAnonymizationMode(ABC):
    """
    Abstract base class for all anonymization modes.

    All mode implementations must inherit from this class
    and implement the required methods.

    Attributes:
        mode_name: Identifier for this mode
        description: Human-readable description
        reversible: Whether this mode supports reversibility
    """

    def __init__(self):
        self._mode_name = self.__class__.__name__.replace("Mode", "").lower()
        self._description = "Base anonymization mode"
        self._reversible = False
        logger.info(f"Initializing anonymization mode: {self.mode_name}")

    @property
    def mode_name(self) -> str:
        """Get mode identifier"""
        return self._mode_name

    @property
    def description(self) -> str:
        """Get mode description"""
        return self._description

    @property
    def is_reversible(self) -> bool:
        """Check if mode is reversible"""
        return self._reversible

    @abstractmethod
    def anonymize(
        self, text: str, detections: List[Dict[str, Any]]
    ) -> Tuple[str, Optional[Dict[str, str]], Optional[str]]:
        """
        Anonymize text based on detections.

        Args:
            text: Original text to anonymize
            detections: List of PII detections

        Returns:
            Tuple of (anonymized_text, mapping, reverse_key)
                - anonymized_text: str - Anonymized version of input text
                - mapping: dict or None - Original to fake value mapping (for reversible modes)
                - reverse_key: str or None - Key for reversing anonymization

        Raises:
            AnonymizationError: If anonymization fails
        """
        pass

    def validate_detections(self, detections: List[Dict[str, Any]]) -> bool:
        """
        Validate detection format.

        Args:
            detections: List of detections to validate

        Returns:
            True if valid, False otherwise
        """
        required_keys = {"entity_type", "start", "end", "text", "confidence"}

        for detection in detections:
            if not all(key in detection for key in required_keys):
                logger.warning(
                    f"Invalid detection format: missing keys",
                    extra={"extra_fields": {"detection": detection}},
                )
                return False

            # Validate position sanity
            if detection["start"] < 0 or detection["end"] <= detection["start"]:
                logger.warning(
                    f"Invalid detection positions",
                    extra={
                        "extra_fields": {
                            "start": detection["start"],
                            "end": detection["end"],
                        }
                    },
                )
                return False

        return True

    def get_info(self) -> Dict[str, Any]:
        """
        Get mode information.

        Returns:
            Dictionary with mode metadata
        """
        return {
            "mode_name": self.mode_name,
            "description": self.description,
            "reversible": self.is_reversible,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(mode='{self.mode_name}', reversible={self.is_reversible})"
