"""
Document processing module for Anonyma Core.

Handles extraction, anonymization, and reconstruction of various document formats.
"""

from .base import BaseDocument, DocumentFormat, DocumentMetadata
from .pipeline import DocumentPipeline, ProcessingResult
from .pdf_document import PDFDocument
from .image_document import ImageDocument
from .word_document import WordDocument
from .excel_document import ExcelDocument
from .powerpoint_document import PowerPointDocument
from .email_document import EmailDocument

__all__ = [
    "BaseDocument",
    "DocumentFormat",
    "DocumentMetadata",
    "DocumentPipeline",
    "ProcessingResult",
    "PDFDocument",
    "ImageDocument",
    "WordDocument",
    "ExcelDocument",
    "PowerPointDocument",
    "EmailDocument",
]
