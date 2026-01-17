from presidio_analyzer import AnalyzerEngine
from typing import List, Dict, Any
import re
import spacy

class PIIDetector:
    def __init__(self):
        try:
            self.analyzer = AnalyzerEngine()
        except Exception:
            print("⚠️  Presidio non disponibile, usando solo pattern personalizzati")
            self.analyzer = None
        
        # Pattern italiani migliorati
        self.italian_patterns = {
            'CODICE_FISCALE': r'\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b',
            'PARTITA_IVA': r'\b[0-9]{11}\b',
            'TELEFONO_IT': r'\b(?:\+39)?[\s-]?[0-9]{2,4}[\s-]?[0-9]{6,8}\b',
            'CAP_IT': r'\b[0-9]{5}\b',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            # Pattern più specifico per nomi italiani
            'NOME_PERSONA': r'\b(?:sig\.?\s+|dott\.?\s+|prof\.?\s+|ing\.?\s+)?[A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,20}\b',
            # Indirizzi italiani
            'INDIRIZZO': r'\b(?:Via|Viale|Piazza|Corso|Largo)\s+[A-Z][a-zA-Z\s]+\s+\d{1,4}\b',
            # Date formato italiano
            'DATA': r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b',
        }
    
    def detect(self, text: str, language: str = 'it') -> List[Dict[str, Any]]:
        """Rileva informazioni sensibili nel testo"""
        detections = []
        
        # Prova prima con Presidio (se disponibile)
        if self.analyzer:
            try:
                lang_to_use = 'en' if language == 'it' else language
                results = self.analyzer.analyze(text=text, language=lang_to_use)
                
                for result in results:
                    detections.append({
                        'entity_type': result.entity_type,
                        'start': result.start,
                        'end': result.end,
                        'confidence': result.score,
                        'text': text[result.start:result.end]
                    })
            except Exception as e:
                print(f"⚠️  Presidio fallito: {e}")
        
        # Aggiungi pattern italiani personalizzati
        detections.extend(self._detect_italian_patterns(text))
        
        # Rimuovi duplicati e sovrapposizioni
        detections = self._remove_duplicates(detections)
        
        return detections
    
    def _detect_italian_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Rileva pattern specifici italiani"""
        detections = []
        
        for pattern_name, pattern in self.italian_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    'entity_type': pattern_name,
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.9,  # Aumentiamo la confidence per i nostri pattern
                    'text': match.group()
                })
        
        return detections
    
    def _remove_duplicates(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rimuove detection duplicate o sovrapposte"""
        if not detections:
            return []
        
        # Ordina per posizione
        sorted_detections = sorted(detections, key=lambda x: x['start'])
        
        # Rimuovi sovrapposizioni
        filtered = [sorted_detections[0]]
        
        for detection in sorted_detections[1:]:
            last = filtered[-1]
            # Se non si sovrappone, aggiungilo
            if detection['start'] >= last['end']:
                filtered.append(detection)
            else:
                # Se si sovrappone, tieni quello con confidence maggiore
                if detection['confidence'] > last['confidence']:
                    filtered[-1] = detection
        
        return filtered