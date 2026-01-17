"""
PDF document handler with OCR support.

Handles both digital PDFs (with selectable text) and scanned PDFs
(requiring OCR). Preserves layout and formatting where possible.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import io

from .base import BaseDocument, DocumentFormat, DocumentMetadata
from ..logging_config import get_logger
from ..exceptions import DocumentProcessingError

logger = get_logger(__name__)


class PDFDocument(BaseDocument):
    """
    PDF document handler.

    Supports:
    - Digital PDFs with selectable text
    - Scanned PDFs with OCR
    - Multi-page documents
    - Metadata preservation
    - Layout preservation (basic)

    Note: Requires pdfplumber, PyPDF2, and optionally pytesseract for OCR.
    """

    def __init__(self, file_path: Path, enable_ocr: bool = True):
        """
        Initialize PDF document handler.

        Args:
            file_path: Path to PDF file
            enable_ocr: Enable OCR for scanned PDFs

        Raises:
            DocumentProcessingError: If PDF can't be loaded
        """
        self.enable_ocr = enable_ocr
        self._pdf_reader = None
        self._pages_text = None

        super().__init__(file_path)

        # Load PDF
        self._load_pdf()

    def _load_pdf(self):
        """Load PDF file with pdfplumber"""
        try:
            import pdfplumber

            self._pdf = pdfplumber.open(self.file_path)
            logger.info(
                f"PDF loaded successfully",
                extra={
                    "extra_fields": {
                        "pages": len(self._pdf.pages),
                        "file_size": self.get_file_size(),
                    }
                },
            )
        except ImportError:
            raise DocumentProcessingError(
                "pdfplumber not installed. Install with: pip install pdfplumber",
                {"required_package": "pdfplumber"},
            )
        except Exception as e:
            logger.error(f"Failed to load PDF: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to load PDF: {str(e)}", {"file_path": str(self.file_path)}
            )

    def _detect_format(self) -> DocumentFormat:
        """Detect format (always PDF for this handler)"""
        return DocumentFormat.PDF

    def _extract_metadata(self) -> DocumentMetadata:
        """Extract PDF metadata"""
        file_stats = self.file_path.stat()

        # Try to load PDF metadata
        page_count = None
        creation_date = None
        modification_date = None
        author = None
        title = None

        try:
            if hasattr(self, "_pdf") and self._pdf:
                page_count = len(self._pdf.pages)

                # Get PDF metadata
                if hasattr(self._pdf, "metadata") and self._pdf.metadata:
                    metadata = self._pdf.metadata
                    author = metadata.get("Author")
                    title = metadata.get("Title")

                    # Parse dates if present
                    if "CreationDate" in metadata:
                        creation_date = self._parse_pdf_date(metadata["CreationDate"])
                    if "ModDate" in metadata:
                        modification_date = self._parse_pdf_date(metadata["ModDate"])

        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata: {e}")

        # Check if scanned (heuristic: no text extractable)
        is_scanned = self._check_if_scanned()

        return DocumentMetadata(
            file_name=self.file_path.name,
            file_size=file_stats.st_size,
            format=DocumentFormat.PDF,
            page_count=page_count,
            creation_date=creation_date,
            modification_date=modification_date,
            author=author,
            title=title,
            is_scanned=is_scanned,
        )

    def _parse_pdf_date(self, date_str: str) -> Optional[datetime]:
        """Parse PDF date string (format: D:YYYYMMDDHHmmSS)"""
        try:
            if date_str.startswith("D:"):
                date_str = date_str[2:16]  # Remove D: and take YYYYMMDDHHMMSS
                return datetime.strptime(date_str, "%Y%m%d%H%M%S")
        except Exception as e:
            logger.debug(f"Failed to parse PDF date: {e}")
        return None

    def _check_if_scanned(self) -> bool:
        """
        Check if PDF is scanned (heuristic: no extractable text).

        Returns:
            True if PDF appears to be scanned
        """
        try:
            if not hasattr(self, "_pdf") or not self._pdf:
                return False

            # Check first page for text
            if len(self._pdf.pages) > 0:
                first_page = self._pdf.pages[0]
                text = first_page.extract_text()

                # If very little or no text, likely scanned
                if not text or len(text.strip()) < 50:
                    logger.info("PDF appears to be scanned (no extractable text)")
                    return True

            return False

        except Exception as e:
            logger.warning(f"Failed to check if scanned: {e}")
            return False

    def extract_text(self) -> str:
        """
        Extract text from PDF.

        For digital PDFs, extracts text directly.
        For scanned PDFs, uses OCR if enabled.

        Returns:
            Extracted text content

        Raises:
            DocumentProcessingError: If extraction fails
        """
        try:
            if self.is_scanned() and self.enable_ocr:
                logger.info("PDF is scanned, using OCR")
                return self._extract_text_with_ocr()
            else:
                return self._extract_text_direct()

        except Exception as e:
            logger.error(f"Text extraction failed: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to extract text from PDF: {str(e)}",
                {"file_path": str(self.file_path)},
            )

    def _extract_text_direct(self) -> str:
        """Extract text directly from digital PDF"""
        logger.debug("Extracting text directly from PDF")

        text_parts = []

        for page_num, page in enumerate(self._pdf.pages, start=1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    logger.debug(
                        f"Extracted text from page {page_num}",
                        extra={
                            "extra_fields": {"page": page_num, "text_length": len(page_text)}
                        },
                    )
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {e}")

        full_text = "\n\n".join(text_parts)

        logger.info(
            f"Text extraction completed",
            extra={
                "extra_fields": {
                    "total_pages": len(self._pdf.pages),
                    "total_length": len(full_text),
                }
            },
        )

        return full_text

    def _extract_text_with_ocr(self) -> str:
        """
        Extract text using OCR for scanned PDFs.

        Requires: pytesseract and pdf2image

        Returns:
            Extracted text from OCR
        """
        try:
            import pytesseract
            from pdf2image import convert_from_path
        except ImportError as e:
            raise DocumentProcessingError(
                f"OCR dependencies not installed: {e}. "
                "Install with: pip install pytesseract pdf2image",
                {"missing_package": str(e)},
            )

        logger.info("Performing OCR on PDF")

        try:
            # Convert PDF pages to images
            images = convert_from_path(self.file_path)

            text_parts = []

            for page_num, image in enumerate(images, start=1):
                logger.debug(f"Running OCR on page {page_num}")

                # Run OCR (support Italian and English)
                page_text = pytesseract.image_to_string(image, lang="ita+eng")

                if page_text:
                    text_parts.append(page_text)

                logger.debug(
                    f"OCR completed for page {page_num}",
                    extra={"extra_fields": {"page": page_num, "text_length": len(page_text)}},
                )

            full_text = "\n\n".join(text_parts)

            logger.info(
                f"OCR extraction completed",
                extra={
                    "extra_fields": {
                        "total_pages": len(images),
                        "total_length": len(full_text),
                    }
                },
            )

            return full_text

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"OCR extraction failed: {str(e)}", {"file_path": str(self.file_path)}
            )

    def rebuild(self, anonymized_text: str, detections: List[Dict[str, Any]]) -> bytes:
        """
        Rebuild PDF with anonymized content.

        Note: This is a basic implementation that creates a new text-based PDF.
        Advanced layout preservation requires more complex processing.

        Args:
            anonymized_text: Anonymized text
            detections: List of detections (for reference)

        Returns:
            PDF file bytes
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
        except ImportError:
            raise DocumentProcessingError(
                "reportlab not installed. Install with: pip install reportlab",
                {"required_package": "reportlab"},
            )

        logger.info("Rebuilding PDF with anonymized content")

        try:
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)

            # Create story (content)
            story = []
            styles = getSampleStyleSheet()

            # Split text into paragraphs
            paragraphs = anonymized_text.split("\n\n")

            for para_text in paragraphs:
                if para_text.strip():
                    # Create paragraph
                    para = Paragraph(para_text.replace("\n", "<br/>"), styles["Normal"])
                    story.append(para)
                    story.append(Spacer(1, 0.2 * inch))

            # Build PDF
            doc.build(story)

            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(
                "PDF rebuilt successfully",
                extra={"extra_fields": {"output_size": len(pdf_bytes)}},
            )

            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF rebuild failed: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to rebuild PDF: {str(e)}", {"file_path": str(self.file_path)}
            )

    def get_page_count(self) -> int:
        """
        Get number of pages.

        Returns:
            Page count
        """
        if hasattr(self, "_pdf") and self._pdf:
            return len(self._pdf.pages)
        return 0

    def close(self):
        """Close PDF file"""
        if hasattr(self, "_pdf") and self._pdf:
            self._pdf.close()
            logger.debug("PDF file closed")

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
