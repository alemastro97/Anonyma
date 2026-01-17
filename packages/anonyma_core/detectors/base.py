"""
Base detector interface for PII detection.

Defines the contract that all detectors must implement,
ensuring consistency across different detection strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..logging_config import get_logger

logger = get_logger(__name__)


class BaseDetector(ABC):
    """
    Abstract base class for all PII detectors.

    All detector implementations must inherit from this class
    and implement the required methods.

    Attributes:
        name: Human-readable name of the detector
        version: Detector version
        supported_languages: List of supported language codes
    """

    def __init__(self):
        self._name = self.__class__.__name__
        self._version = "1.0.0"
        self._supported_languages = ["it", "en"]
        logger.info(f"Initializing detector: {self.name}")

    @property
    def name(self) -> str:
        """Get detector name"""
        return self._name

    @property
    def version(self) -> str:
        """Get detector version"""
        return self._version

    @property
    def supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self._supported_languages

    @abstractmethod
    def detect(self, text: str, language: str = "it") -> List[Dict[str, Any]]:
        """
        Detect PII entities in text.

        Args:
            text: Input text to analyze
            language: Language code (default: 'it')

        Returns:
            List of detection dictionaries with keys:
                - entity_type: str (e.g., 'EMAIL', 'PHONE')
                - start: int (start position)
                - end: int (end position)
                - confidence: float (0.0 to 1.0)
                - text: str (detected text)

        Raises:
            DetectionError: If detection fails
        """
        pass

    def is_language_supported(self, language: str) -> bool:
        """
        Check if language is supported.

        Args:
            language: Language code to check

        Returns:
            True if language is supported, False otherwise
        """
        return language in self.supported_languages

    def get_info(self) -> Dict[str, Any]:
        """
        Get detector information.

        Returns:
            Dictionary with detector metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "supported_languages": self.supported_languages,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}')"
