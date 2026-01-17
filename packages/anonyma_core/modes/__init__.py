from enum import Enum
from typing import Dict, Any, Optional

class AnonymizationMode(str, Enum):
    REDACT = "redact"
    SUBSTITUTE = "substitute" 
    VISUAL_REDACT = "visual_redact"

class AnonymizationResult:
    def __init__(
        self,
        anonymized_text: str,
        original_text: str,
        mode: AnonymizationMode,
        mapping: Optional[Dict[str, str]] = None,
        reverse_key: Optional[str] = None,
        detections_count: int = 0  # ← Aggiungi questo parametro
    ):
        self.anonymized_text = anonymized_text
        self.original_text = original_text
        self.mode = mode
        self.mapping = mapping
        self.reverse_key = reverse_key
        self.detections_count = detections_count  # ← E questo attributo
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "anonymized_text": self.anonymized_text,
            "mode": self.mode.value,
            "mapping": self.mapping,
            "reverse_key": self.reverse_key,
            "detections_count": self.detections_count
        }