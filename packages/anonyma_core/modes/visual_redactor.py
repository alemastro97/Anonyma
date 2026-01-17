from typing import List, Dict, Any

class VisualRedactor:
    def __init__(self):
        self.redaction_symbol = "██████"
    
    def anonymize(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """Modalità 3: Redazione visiva irrecuperabile"""
        # Sort detections by start position (reverse order)
        sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)
        
        result = text
        for detection in sorted_detections:
            start = detection['start']
            end = detection['end']
            
            # Replace with fixed visual redaction
            result = result[:start] + self.redaction_symbol + result[end:]
        
        return result