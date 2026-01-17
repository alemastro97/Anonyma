from typing import List, Dict, Any

class Redactor:
    def __init__(self, redaction_char: str = "█"):
        self.redaction_char = redaction_char
    
    def anonymize(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """Modalità 1: Oscura completamente le informazioni sensibili"""
        # Sort detections by start position (reverse order for replacement)
        sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)
        
        result = text
        for detection in sorted_detections:
            start = detection['start']
            end = detection['end']
            original_length = end - start
            
            # Replace with redaction characters
            redacted = self.redaction_char * original_length
            result = result[:start] + redacted + result[end:]
        
        return result