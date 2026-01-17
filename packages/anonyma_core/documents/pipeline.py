"""
Document processing pipeline.

Orchestrates the entire document anonymization workflow:
1. Format detection
2. Text extraction
3. PII detection
4. Anonymization
5. Document reconstruction
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from .base import BaseDocument, DocumentFormat
from .pdf_document import PDFDocument
from .image_document import ImageDocument
from .word_document import WordDocument
from .excel_document import ExcelDocument
from .powerpoint_document import PowerPointDocument
from .email_document import EmailDocument
from ..logging_config import get_logger
from ..exceptions import DocumentProcessingError, UnsupportedLanguageError
from ..modes import AnonymizationMode

logger = get_logger(__name__)


@dataclass
class ProcessingResult:
    """
    Result of document processing.

    Attributes:
        success: Whether processing was successful
        original_file: Path to original file
        output_file: Path to output file (if saved)
        format: Document format
        anonymized_text: Anonymized text content
        original_text: Original text content (for reference)
        detections: List of PII detections
        detections_count: Number of detections found
        mode: Anonymization mode used
        processing_time: Processing time in seconds
        metadata: Document metadata
        error: Error message if failed
    """

    success: bool
    original_file: Path
    output_file: Optional[Path] = None
    format: Optional[DocumentFormat] = None
    anonymized_text: Optional[str] = None
    original_text: Optional[str] = None
    detections: List[Dict[str, Any]] = field(default_factory=list)
    detections_count: int = 0
    mode: Optional[AnonymizationMode] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "original_file": str(self.original_file),
            "output_file": str(self.output_file) if self.output_file else None,
            "format": self.format.value if self.format else None,
            "detections_count": self.detections_count,
            "mode": self.mode.value if self.mode else None,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
            "error": self.error,
        }


class DocumentPipeline:
    """
    Unified pipeline for processing documents of any format.

    Handles:
    - Automatic format detection
    - Text extraction (with OCR if needed)
    - PII detection
    - Anonymization
    - Document reconstruction

    Example:
        >>> from anonyma_core import AnonymaEngine
        >>> from anonyma_core.documents import DocumentPipeline
        >>> from anonyma_core.modes import AnonymizationMode
        >>>
        >>> engine = AnonymaEngine(use_flair=False)
        >>> pipeline = DocumentPipeline(engine)
        >>>
        >>> result = pipeline.process(
        ...     file_path=Path("document.pdf"),
        ...     mode=AnonymizationMode.REDACT,
        ...     output_path=Path("anonymized.pdf")
        ... )
        >>>
        >>> print(f"Success: {result.success}")
        >>> print(f"Detections: {result.detections_count}")
    """

    def __init__(self, engine):
        """
        Initialize document pipeline.

        Args:
            engine: AnonymaEngine instance for anonymization
        """
        self.engine = engine

        # Register document handlers
        self.handlers = {
            DocumentFormat.PDF: PDFDocument,
            DocumentFormat.IMAGE: ImageDocument,
            DocumentFormat.WORD: WordDocument,
            DocumentFormat.EXCEL: ExcelDocument,
            DocumentFormat.POWERPOINT: PowerPointDocument,
            DocumentFormat.EMAIL: EmailDocument,
        }

        logger.info(
            "DocumentPipeline initialized",
            extra={"extra_fields": {"supported_formats": list(self.handlers.keys())}},
        )

    def process(
        self,
        file_path: Path,
        mode: AnonymizationMode,
        output_path: Optional[Path] = None,
        language: str = "it",
        save_output: bool = True,
    ) -> ProcessingResult:
        """
        Process a document through the complete pipeline.

        Args:
            file_path: Path to input document
            mode: Anonymization mode to use
            output_path: Path to save output (optional)
            language: Language code for detection
            save_output: Whether to save output file

        Returns:
            ProcessingResult with all processing information

        Raises:
            DocumentProcessingError: If processing fails
        """
        start_time = datetime.now()

        logger.info(
            f"Starting document processing",
            extra={
                "extra_fields": {
                    "file": str(file_path),
                    "mode": mode.value,
                    "language": language,
                }
            },
        )

        try:
            # Step 1: Detect format
            doc_format = self._detect_format(file_path)
            logger.info(f"Detected format: {doc_format.value}")

            # Step 2: Load document handler
            handler = self._get_handler(file_path, doc_format)

            # Step 3: Extract text
            logger.info("Extracting text from document")
            original_text = handler.extract_text()
            logger.info(
                f"Text extracted",
                extra={"extra_fields": {"text_length": len(original_text)}},
            )

            # Step 4: Anonymize text
            logger.info("Starting anonymization")
            result = self.engine.anonymize(original_text, mode, language)
            logger.info(
                f"Anonymization completed",
                extra={"extra_fields": {"detections_count": len(result.detections) if hasattr(result, 'detections') else 0}},
            )

            # Step 5: Rebuild document
            logger.info("Rebuilding document")
            detections = result.detections if hasattr(result, "detections") else []
            output_bytes = handler.rebuild(result.anonymized_text, detections)

            # Step 6: Save output
            if save_output:
                if output_path is None:
                    output_path = self._generate_output_path(file_path)

                output_path.write_bytes(output_bytes)
                logger.info(f"Output saved to: {output_path}")

            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            # Create result
            processing_result = ProcessingResult(
                success=True,
                original_file=file_path,
                output_file=output_path if save_output else None,
                format=doc_format,
                anonymized_text=result.anonymized_text,
                original_text=original_text,
                detections=detections,
                detections_count=len(detections),
                mode=mode,
                processing_time=processing_time,
                metadata=handler.get_metadata().to_dict(),
            )

            logger.info(
                f"Document processing completed successfully",
                extra={
                    "extra_fields": {
                        "processing_time": processing_time,
                        "detections": len(detections),
                    }
                },
            )

            return processing_result

        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            logger.error(f"Document processing failed: {e}", exc_info=True)

            return ProcessingResult(
                success=False,
                original_file=file_path,
                format=doc_format if "doc_format" in locals() else None,
                processing_time=processing_time,
                error=str(e),
            )

    def _detect_format(self, file_path: Path) -> DocumentFormat:
        """
        Detect document format from file extension and magic bytes.

        Args:
            file_path: Path to file

        Returns:
            Detected document format
        """
        # Check file extension
        suffix = file_path.suffix.lower()

        format_map = {
            ".pdf": DocumentFormat.PDF,
            ".png": DocumentFormat.IMAGE,
            ".jpg": DocumentFormat.IMAGE,
            ".jpeg": DocumentFormat.IMAGE,
            ".tiff": DocumentFormat.IMAGE,
            ".tif": DocumentFormat.IMAGE,
            ".docx": DocumentFormat.WORD,
            ".doc": DocumentFormat.WORD,
            ".xlsx": DocumentFormat.EXCEL,
            ".xls": DocumentFormat.EXCEL,
            ".pptx": DocumentFormat.POWERPOINT,
            ".ppt": DocumentFormat.POWERPOINT,
            ".eml": DocumentFormat.EMAIL,
            ".msg": DocumentFormat.EMAIL,
            ".txt": DocumentFormat.TEXT,
            ".html": DocumentFormat.HTML,
            ".htm": DocumentFormat.HTML,
        }

        detected_format = format_map.get(suffix, DocumentFormat.UNKNOWN)

        logger.debug(
            f"Format detection",
            extra={"extra_fields": {"extension": suffix, "format": detected_format.value}},
        )

        return detected_format

    def _get_handler(self, file_path: Path, doc_format: DocumentFormat) -> BaseDocument:
        """
        Get appropriate document handler for format.

        Args:
            file_path: Path to file
            doc_format: Document format

        Returns:
            Document handler instance

        Raises:
            DocumentProcessingError: If format not supported
        """
        handler_class = self.handlers.get(doc_format)

        if handler_class is None:
            raise DocumentProcessingError(
                f"Unsupported document format: {doc_format.value}",
                {"format": doc_format.value, "supported": list(self.handlers.keys())},
            )

        return handler_class(file_path)

    def _generate_output_path(self, input_path: Path) -> Path:
        """
        Generate output file path.

        Args:
            input_path: Input file path

        Returns:
            Output file path with 'anonymized_' prefix
        """
        return input_path.parent / f"anonymized_{input_path.name}"

    def get_supported_formats(self) -> List[DocumentFormat]:
        """
        Get list of supported document formats.

        Returns:
            List of supported formats
        """
        return list(self.handlers.keys())

    def is_format_supported(self, format: DocumentFormat) -> bool:
        """
        Check if document format is supported.

        Args:
            format: Document format to check

        Returns:
            True if supported, False otherwise
        """
        return format in self.handlers
