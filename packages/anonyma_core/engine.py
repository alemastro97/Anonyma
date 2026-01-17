from typing import Optional, Dict, Any, List
from .modes import AnonymizationMode, AnonymizationResult
from .modes.redactor import Redactor
from .modes.substitutor import Substitutor
from .modes.visual_redactor import VisualRedactor
from .logging_config import get_logger

logger = get_logger(__name__)


class AnonymaEngine:
    """Main Anonymization Engine with Flair Detection"""

    def __init__(self, use_flair: bool = True):
        logger.info("Initializing Anonyma Engine", extra={"extra_fields": {"use_flair": use_flair}})

        if use_flair:
            try:
                from .detectors.flair_detector import FlairPIIDetector
                self.detector = FlairPIIDetector()
                logger.info("Using Flair detector (ultra-accurate)")
            except Exception as e:
                logger.warning(
                    "Flair detector initialization failed, falling back to basic detector",
                    extra={"extra_fields": {"error": str(e)}}
                )
                from .detectors.pii_detector import PIIDetector
                self.detector = PIIDetector()
        else:
            from .detectors.pii_detector import PIIDetector
            self.detector = PIIDetector()
            logger.info("Using basic PII detector")

        self.redactor = Redactor()
        self.substitutor = Substitutor()
        self.visual_redactor = VisualRedactor()

        logger.info("Anonyma Engine initialized successfully")
    
    def anonymize(
        self,
        text: str,
        mode: AnonymizationMode,
        language: str = 'it'
    ) -> AnonymizationResult:
        """Anonimizza il testo con Flair detection"""
        logger.info(
            "Starting anonymization",
            extra={"extra_fields": {
                "text_length": len(text),
                "mode": mode.value,
                "language": language
            }}
        )

        # 1. Detect PII con Flair
        detections = self.detector.detect(text, language)
        logger.debug(
            "Detection phase completed",
            extra={"extra_fields": {"detections_found": len(detections)}}
        )
        
        # 2. Apply anonymization based on mode
        if mode == AnonymizationMode.REDACT:
            anonymized = self.redactor.anonymize(text, detections)
            logger.info("Anonymization completed using REDACT mode")
            return AnonymizationResult(
                anonymized_text=anonymized,
                original_text=text,
                mode=mode
            )

        elif mode == AnonymizationMode.SUBSTITUTE:
            anonymized, mapping, reverse_key = self.substitutor.anonymize(text, detections)
            logger.info(
                "Anonymization completed using SUBSTITUTE mode",
                extra={"extra_fields": {"mappings_created": len(mapping) if mapping else 0}}
            )
            return AnonymizationResult(
                anonymized_text=anonymized,
                original_text=text,
                mode=mode,
                mapping=mapping,
                reverse_key=reverse_key
            )

        elif mode == AnonymizationMode.VISUAL_REDACT:
            anonymized = self.visual_redactor.anonymize(text, detections)
            logger.info("Anonymization completed using VISUAL_REDACT mode")
            return AnonymizationResult(
                anonymized_text=anonymized,
                original_text=text,
                mode=mode
            )

        else:
            logger.error(
                "Unsupported anonymization mode",
                extra={"extra_fields": {"mode": str(mode)}}
            )
            raise ValueError(f"Unsupported anonymization mode: {mode}")