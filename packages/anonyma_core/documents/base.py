"""
Base document interface for all document types.

Defines the contract that all document handlers must implement,
ensuring consistency across different document formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from ..logging_config import get_logger
from ..exceptions import DocumentProcessingError

logger = get_logger(__name__)


class DocumentFormat(str, Enum):
    """Supported document formats"""

    PDF = "pdf"
    IMAGE = "image"
    WORD = "word"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    EMAIL = "email"
    TEXT = "text"
    HTML = "html"
    UNKNOWN = "unknown"


@dataclass
class DocumentMetadata:
    """
    Document metadata container.

    Attributes:
        file_name: Original file name
        file_size: File size in bytes
        format: Document format
        page_count: Number of pages (if applicable)
        creation_date: Document creation date
        modification_date: Last modification date
        author: Document author
        title: Document title
        is_scanned: Whether document is scanned (OCR needed)
        language: Detected language
        custom: Additional custom metadata
    """

    file_name: str
    file_size: int
    format: DocumentFormat
    page_count: Optional[int] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    author: Optional[str] = None
    title: Optional[str] = None
    is_scanned: bool = False
    language: Optional[str] = None
    custom: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "file_name": self.file_name,
            "file_size": self.file_size,
            "format": self.format.value,
            "page_count": self.page_count,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None,
            "modification_date": (
                self.modification_date.isoformat() if self.modification_date else None
            ),
            "author": self.author,
            "title": self.title,
            "is_scanned": self.is_scanned,
            "language": self.language,
            "custom": self.custom,
        }


class BaseDocument(ABC):
    """
    Abstract base class for all document types.

    All document handlers must inherit from this class and implement
    the required methods for extraction, anonymization, and reconstruction.

    Attributes:
        file_path: Path to the document file
        metadata: Document metadata
        format: Document format
        text_content: Extracted text content (cached)
    """

    def __init__(self, file_path: Path):
        """
        Initialize document handler.

        Args:
            file_path: Path to document file

        Raises:
            DocumentProcessingError: If file doesn't exist or can't be read
        """
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise DocumentProcessingError(
                f"File not found: {file_path}", {"file_path": str(file_path)}
            )

        if not self.file_path.is_file():
            raise DocumentProcessingError(
                f"Path is not a file: {file_path}", {"file_path": str(file_path)}
            )

        self.format = self._detect_format()
        self.metadata = self._extract_metadata()
        self.text_content: Optional[str] = None

        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={
                "extra_fields": {
                    "file_path": str(file_path),
                    "format": self.format.value,
                    "file_size": self.metadata.file_size,
                }
            },
        )

    @abstractmethod
    def extract_text(self) -> str:
        """
        Extract plain text from document.

        This method should extract all textual content from the document,
        handling OCR if necessary for scanned documents.

        Returns:
            Extracted text content

        Raises:
            DocumentProcessingError: If extraction fails
        """
        pass

    @abstractmethod
    def rebuild(
        self, anonymized_text: str, detections: List[Dict[str, Any]]
    ) -> bytes:
        """
        Rebuild document with anonymized content.

        This method should reconstruct the original document with
        anonymized text, preserving as much formatting as possible.

        Args:
            anonymized_text: Anonymized version of text
            detections: List of PII detections used for anonymization

        Returns:
            Document bytes (ready to save to file)

        Raises:
            DocumentProcessingError: If rebuilding fails
        """
        pass

    @abstractmethod
    def _detect_format(self) -> DocumentFormat:
        """
        Detect document format.

        Returns:
            Detected document format
        """
        pass

    @abstractmethod
    def _extract_metadata(self) -> DocumentMetadata:
        """
        Extract document metadata.

        Returns:
            Document metadata object
        """
        pass

    def get_text(self, force_refresh: bool = False) -> str:
        """
        Get text content (with caching).

        Args:
            force_refresh: Force re-extraction even if cached

        Returns:
            Document text content
        """
        if self.text_content is None or force_refresh:
            logger.debug("Extracting text from document")
            self.text_content = self.extract_text()
            logger.info(
                "Text extracted",
                extra={"extra_fields": {"text_length": len(self.text_content)}},
            )

        return self.text_content

    def is_scanned(self) -> bool:
        """
        Check if document is scanned (requires OCR).

        Returns:
            True if document is scanned, False otherwise
        """
        return self.metadata.is_scanned

    def get_metadata(self) -> DocumentMetadata:
        """
        Get document metadata.

        Returns:
            Document metadata object
        """
        return self.metadata

    def get_file_size(self) -> int:
        """
        Get file size in bytes.

        Returns:
            File size in bytes
        """
        return self.file_path.stat().st_size

    def get_format(self) -> DocumentFormat:
        """
        Get document format.

        Returns:
            Document format enum
        """
        return self.format

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"file='{self.file_path.name}', "
            f"format={self.format.value}, "
            f"size={self.metadata.file_size})"
        )

    def __str__(self) -> str:
        return f"{self.format.value.upper()} Document: {self.file_path.name}"
