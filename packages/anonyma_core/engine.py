from typing import Optional, Dict, Any, List
from .modes import AnonymizationMode, AnonymizationResult
from .modes.redactor import Redactor
from .modes.substitutor import Substitutor
from .modes.visual_redactor import VisualRedactor

class AnonymaEngine:
    """Main Anonymization Engine with Flair Detection"""
    
    def __init__(self, use_flair: bool = True):
        print("🎭 Initializing Anonyma Engine...")
        
        if use_flair:
            try:
                from .detectors.flair_detector import FlairPIIDetector
                self.detector = FlairPIIDetector()
                print("✅ Using Flair detector (ultra-accurate)")
            except Exception as e:
                print(f"⚠️ Flair failed, using basic detector: {e}")
                from .detectors.pii_detector import PIIDetector
                self.detector = PIIDetector()
        else:
            from .detectors.pii_detector import PIIDetector
            self.detector = PIIDetector()
            
        self.redactor = Redactor()
        self.substitutor = Substitutor()
        self.visual_redactor = VisualRedactor()
        
        print("🎯 Anonyma Engine ready!")
    
    def anonymize(
        self, 
        text: str, 
        mode: AnonymizationMode,
        language: str = 'it'
    ) -> AnonymizationResult:
        """Anonimizza il testo con Flair detection"""
        
        # 1. Detect PII con Flair
        detections = self.detector.detect(text, language)
        
        # 2. Apply anonymization based on mode
        if mode == AnonymizationMode.REDACT:
            anonymized = self.redactor.anonymize(text, detections)
            return AnonymizationResult(
                anonymized_text=anonymized,
                original_text=text,
                mode=mode
            )
        
        elif mode == AnonymizationMode.SUBSTITUTE:
            anonymized, mapping, reverse_key = self.substitutor.anonymize(text, detections)
            return AnonymizationResult(
                anonymized_text=anonymized,
                original_text=text,
                mode=mode,
                mapping=mapping,
                reverse_key=reverse_key
            )
        
        elif mode == AnonymizationMode.VISUAL_REDACT:
            anonymized = self.visual_redactor.anonymize(text, detections)
            return AnonymizationResult(
                anonymized_text=anonymized,
                original_text=text,
                mode=mode
            )
        
        else:
            raise ValueError(f"Unsupported anonymization mode: {mode}")