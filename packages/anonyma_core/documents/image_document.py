"""
Image document handler with OCR and visual redaction.

Handles images (PNG, JPG, TIFF) with:
- Text extraction via OCR
- Bounding box detection
- Visual redaction (draw black boxes over detected text)
- Support for multiple OCR engines
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import io

from .base import BaseDocument, DocumentFormat, DocumentMetadata
from ..logging_config import get_logger
from ..exceptions import DocumentProcessingError

logger = get_logger(__name__)


class ImageDocument(BaseDocument):
    """
    Image document handler with OCR and visual redaction.

    Supports:
    - PNG, JPG, JPEG, TIFF images
    - OCR text extraction with bounding boxes
    - Visual redaction (black boxes over sensitive text)
    - Multiple OCR engines (EasyOCR, Tesseract)

    Note: Requires Pillow and an OCR engine (easyocr or pytesseract).
    """

    def __init__(self, file_path: Path, ocr_engine: str = "easyocr"):
        """
        Initialize image document handler.

        Args:
            file_path: Path to image file
            ocr_engine: OCR engine to use ('easyocr' or 'tesseract')

        Raises:
            DocumentProcessingError: If image can't be loaded
        """
        self.ocr_engine = ocr_engine
        self._ocr_reader = None
        self._ocr_data = None  # Cache OCR results with bounding boxes

        super().__init__(file_path)

        # Load image
        self._load_image()

        # Initialize OCR
        self._init_ocr()

    def _load_image(self):
        """Load image with Pillow"""
        try:
            from PIL import Image

            self._image = Image.open(self.file_path)

            logger.info(
                f"Image loaded successfully",
                extra={
                    "extra_fields": {
                        "size": self._image.size,
                        "mode": self._image.mode,
                        "format": self._image.format,
                    }
                },
            )

        except ImportError:
            raise DocumentProcessingError(
                "Pillow not installed. Install with: pip install Pillow",
                {"required_package": "Pillow"},
            )
        except Exception as e:
            logger.error(f"Failed to load image: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to load image: {str(e)}", {"file_path": str(self.file_path)}
            )

    def _init_ocr(self):
        """Initialize OCR engine"""
        if self.ocr_engine == "easyocr":
            self._init_easyocr()
        elif self.ocr_engine == "tesseract":
            self._init_tesseract()
        else:
            raise DocumentProcessingError(
                f"Unsupported OCR engine: {self.ocr_engine}",
                {"ocr_engine": self.ocr_engine, "supported": ["easyocr", "tesseract"]},
            )

    def _init_easyocr(self):
        """Initialize EasyOCR reader"""
        try:
            import easyocr

            logger.info("Initializing EasyOCR (this may take a moment)...")
            self._ocr_reader = easyocr.Reader(["it", "en"], gpu=False)
            logger.info("EasyOCR initialized successfully")

        except ImportError:
            raise DocumentProcessingError(
                "EasyOCR not installed. Install with: pip install easyocr",
                {"required_package": "easyocr"},
            )
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to initialize EasyOCR: {str(e)}")

    def _init_tesseract(self):
        """Initialize Tesseract OCR"""
        try:
            import pytesseract

            # Test if tesseract is available
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR initialized successfully")

        except ImportError:
            raise DocumentProcessingError(
                "pytesseract not installed. Install with: pip install pytesseract",
                {"required_package": "pytesseract"},
            )
        except Exception as e:
            logger.error(f"Tesseract not found: {e}")
            raise DocumentProcessingError(
                "Tesseract OCR not found. Please install tesseract-ocr.",
                {"install_info": "macOS: brew install tesseract, Ubuntu: apt-get install tesseract-ocr"},
            )

    def _detect_format(self) -> DocumentFormat:
        """Detect format (always IMAGE for this handler)"""
        return DocumentFormat.IMAGE

    def _extract_metadata(self) -> DocumentMetadata:
        """Extract image metadata"""
        file_stats = self.file_path.stat()

        # Get image dimensions
        width, height = self._image.size if hasattr(self, "_image") else (None, None)

        return DocumentMetadata(
            file_name=self.file_path.name,
            file_size=file_stats.st_size,
            format=DocumentFormat.IMAGE,
            is_scanned=True,  # Images always need OCR
            custom={
                "width": width,
                "height": height,
                "mode": self._image.mode if hasattr(self, "_image") else None,
                "image_format": self._image.format if hasattr(self, "_image") else None,
            },
        )

    def extract_text(self) -> str:
        """
        Extract text from image using OCR.

        Returns:
            Extracted text content

        Raises:
            DocumentProcessingError: If OCR fails
        """
        try:
            if self.ocr_engine == "easyocr":
                return self._extract_with_easyocr()
            elif self.ocr_engine == "tesseract":
                return self._extract_with_tesseract()
            else:
                raise DocumentProcessingError(f"Unknown OCR engine: {self.ocr_engine}")

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to extract text from image: {str(e)}",
                {"file_path": str(self.file_path)},
            )

    def _extract_with_easyocr(self) -> str:
        """Extract text using EasyOCR (with bounding boxes)"""
        logger.info("Running EasyOCR on image")

        # Run OCR
        results = self._ocr_reader.readtext(str(self.file_path))

        # Cache results with bounding boxes
        self._ocr_data = results

        # Extract text
        text_parts = [result[1] for result in results]
        full_text = " ".join(text_parts)

        logger.info(
            f"EasyOCR extraction completed",
            extra={
                "extra_fields": {
                    "text_regions": len(results),
                    "total_length": len(full_text),
                }
            },
        )

        return full_text

    def _extract_with_tesseract(self) -> str:
        """Extract text using Tesseract OCR"""
        import pytesseract

        logger.info("Running Tesseract OCR on image")

        # Run OCR with Italian + English
        text = pytesseract.image_to_string(self._image, lang="ita+eng")

        # Also get bounding box data for visual redaction
        ocr_data = pytesseract.image_to_data(
            self._image, lang="ita+eng", output_type=pytesseract.Output.DICT
        )

        # Cache OCR data
        self._ocr_data = ocr_data

        logger.info(
            f"Tesseract extraction completed",
            extra={"extra_fields": {"text_length": len(text)}},
        )

        return text

    def rebuild(self, anonymized_text: str, detections: List[Dict[str, Any]]) -> bytes:
        """
        Rebuild image with visual redaction.

        Draws black boxes over detected sensitive text regions.

        Args:
            anonymized_text: Anonymized text (not used for images)
            detections: List of PII detections with positions

        Returns:
            Image bytes with visual redaction
        """
        try:
            from PIL import Image, ImageDraw

            logger.info("Rebuilding image with visual redaction")

            # Create a copy of the image
            redacted_image = self._image.copy()
            draw = ImageDraw.Draw(redacted_image)

            # Get bounding boxes for detections
            boxes = self._get_bounding_boxes(detections)

            logger.info(
                f"Drawing {len(boxes)} redaction boxes",
                extra={"extra_fields": {"boxes_count": len(boxes)}},
            )

            # Draw black rectangles over sensitive regions
            for box in boxes:
                # Expand box slightly for better coverage
                x1, y1, x2, y2 = box
                padding = 5
                draw.rectangle(
                    [x1 - padding, y1 - padding, x2 + padding, y2 + padding],
                    fill="black",
                    outline="black",
                    width=2,
                )

            # Save to bytes
            buffer = io.BytesIO()
            save_format = self._image.format or "PNG"
            redacted_image.save(buffer, format=save_format)
            image_bytes = buffer.getvalue()
            buffer.close()

            logger.info(
                "Image rebuilt successfully",
                extra={"extra_fields": {"output_size": len(image_bytes)}},
            )

            return image_bytes

        except Exception as e:
            logger.error(f"Image rebuild failed: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to rebuild image: {str(e)}", {"file_path": str(self.file_path)}
            )

    def _get_bounding_boxes(self, detections: List[Dict[str, Any]]) -> List[Tuple[int, int, int, int]]:
        """
        Map text detections to image bounding boxes.

        Args:
            detections: List of text detections with start/end positions

        Returns:
            List of bounding boxes (x1, y1, x2, y2)
        """
        if not self._ocr_data:
            logger.warning("No OCR data available, cannot map bounding boxes")
            return []

        boxes = []

        if self.ocr_engine == "easyocr":
            boxes = self._map_boxes_easyocr(detections)
        elif self.ocr_engine == "tesseract":
            boxes = self._map_boxes_tesseract(detections)

        return boxes

    def _map_boxes_easyocr(self, detections: List[Dict[str, Any]]) -> List[Tuple[int, int, int, int]]:
        """Map detections to EasyOCR bounding boxes"""
        boxes = []

        # EasyOCR format: [[bbox], text, confidence]
        for detection in detections:
            detected_text = detection.get("text", "").strip().lower()

            # Find matching OCR result
            for ocr_result in self._ocr_data:
                bbox, ocr_text, confidence = ocr_result
                ocr_text = ocr_text.strip().lower()

                # Check if detection text matches OCR text
                if detected_text in ocr_text or ocr_text in detected_text:
                    # Convert bbox to x1, y1, x2, y2
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]

                    x1, x2 = min(x_coords), max(x_coords)
                    y1, y2 = min(y_coords), max(y_coords)

                    boxes.append((int(x1), int(y1), int(x2), int(y2)))
                    logger.debug(
                        f"Mapped detection '{detected_text}' to box ({x1}, {y1}, {x2}, {y2})"
                    )

        return boxes

    def _map_boxes_tesseract(self, detections: List[Dict[str, Any]]) -> List[Tuple[int, int, int, int]]:
        """Map detections to Tesseract bounding boxes"""
        boxes = []

        # Tesseract format: dict with 'text', 'left', 'top', 'width', 'height'
        for detection in detections:
            detected_text = detection.get("text", "").strip().lower()

            # Find matching OCR word
            for i, ocr_text in enumerate(self._ocr_data["text"]):
                ocr_text = ocr_text.strip().lower()

                if detected_text in ocr_text or ocr_text in detected_text:
                    left = self._ocr_data["left"][i]
                    top = self._ocr_data["top"][i]
                    width = self._ocr_data["width"][i]
                    height = self._ocr_data["height"][i]

                    x1, y1 = left, top
                    x2, y2 = left + width, top + height

                    boxes.append((x1, y1, x2, y2))
                    logger.debug(
                        f"Mapped detection '{detected_text}' to box ({x1}, {y1}, {x2}, {y2})"
                    )

        return boxes

    def get_image_size(self) -> Tuple[int, int]:
        """
        Get image dimensions.

        Returns:
            (width, height) tuple
        """
        return self._image.size

    def close(self):
        """Close image"""
        if hasattr(self, "_image") and self._image:
            self._image.close()
            logger.debug("Image closed")

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
