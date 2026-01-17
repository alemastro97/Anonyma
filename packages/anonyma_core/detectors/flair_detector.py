from flair.data import Sentence
from flair.models import SequenceTagger
from typing import List, Dict, Any
import logging
import re
import os

class FlairPIIDetector:
    """PII Detector basato su Flair - Multilingua e ultra-accurato"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🧠 Loading Flair PII Detector...")
        
        # Configura cache directory per Flair (persiste tra restart)
        os.environ.setdefault('FLAIR_CACHE_ROOT', '/app/.flair_cache')
        
        self.models = {}
        self.pattern_detector = self._init_pattern_detector()
        
        # Carica modelli Flair (dovrebbero essere già cached)
        self._load_flair_models()
        
        # Mapping delle etichette
        self.label_mapping = {
            'PER': 'NOME_PERSONA',
            'PERSON': 'NOME_PERSONA',
            'ORG': 'ORGANIZZAZIONE',
            'LOC': 'LUOGO', 
            'GPE': 'LUOGO',
            'MISC': 'ALTRO'
        }
        
        self.logger.info(f"✅ Flair detector ready with {len(self.models)} models")
    
    def _load_flair_models(self):
        """Carica modelli Flair (dovrebbero essere cached)"""
        
        model_configs = [
            ('multi', 'ner-multi', "Multi-lingual NER"),
            ('english_large', 'ner-english-ontonotes-large', "English large NER"), 
            ('english_fast', 'ner-english-ontonotes-fast', "English fast NER")
        ]
        
        for key, model_name, description in model_configs:
            try:
                self.logger.info(f"📦 Loading {description}...")
                self.models[key] = SequenceTagger.load(model_name)
                self.logger.info(f"✅ {description} loaded from cache")
            except Exception as e:
                self.logger.warning(f"⚠️ {description} failed: {e}")
        
        if not self.models:
            raise Exception("No Flair models could be loaded!")
        
    def _init_pattern_detector(self):
        """Pattern detector per entità specifiche non coperte da Flair"""
        return {
            'EMAIL': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'confidence': 0.98
            },
            'CODICE_FISCALE_IT': {
                'pattern': r'\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b',
                'confidence': 0.99
            },
            'PARTITA_IVA_IT': {
                'pattern': r'\b(?:IT\s?)?[0-9]{11}\b',
                'confidence': 0.95
            },
            'TELEFONO': {
                'pattern': r'\b(?:\+\d{1,3})?[\s-]?(?:\(?\d{1,4}\)?)?[\s-]?\d{1,4}[\s-]?\d{4,10}\b',
                'confidence': 0.90
            },
            'IBAN': {
                'pattern': r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b',
                'confidence': 0.97
            },
            'CREDIT_CARD': {
                'pattern': r'\b(?:\d{4}[\s-]?){3}\d{4}\b',
                'confidence': 0.85
            }
        }
    
    def detect(self, text: str, language: str = 'it') -> List[Dict[str, Any]]:
        """Detection PII con Flair + pattern specifici"""
        
        all_detections = []
        
        # 1. Detection con Flair NER
        flair_detections = self._detect_with_flair(text)
        all_detections.extend(flair_detections)
        
        # 2. Detection con pattern specifici
        pattern_detections = self._detect_with_patterns(text)
        all_detections.extend(pattern_detections)
        
        # 3. Post-processing e filtering
        filtered_detections = self._post_process(all_detections, text)
        
        self.logger.info(f"🔍 Found {len(filtered_detections)} high-confidence detections")
        
        return filtered_detections
    
    def _detect_with_flair(self, text: str) -> List[Dict[str, Any]]:
        """Detection con modelli Flair"""
        all_detections = []
        
        # Crea sentence Flair
        sentence = Sentence(text)
        
        for model_name, model in self.models.items():
            try:
                # Predict entities
                model.predict(sentence)
                
                for entity in sentence.get_spans('ner'):
                    label = entity.get_label("ner").value
                    confidence = entity.get_label("ner").score
                    
                    # Mappa etichetta ai nostri tipi
                    entity_type = self.label_mapping.get(label, label)
                    
                    # Filtra entità di bassa qualità
                    if self._is_valid_entity(entity.text, entity_type, confidence):
                        all_detections.append({
                            'entity_type': entity_type,
                            'start': entity.start_position,
                            'end': entity.end_position,
                            'confidence': confidence,
                            'text': entity.text,
                            'source': f'flair_{model_name}',
                            'original_label': label
                        })
                
                # Clear predictions per evitare interferenze
                sentence.clear_embeddings()
                
            except Exception as e:
                self.logger.error(f"❌ Flair model {model_name} failed: {e}")
        
        return all_detections
    
    def _detect_with_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Detection con pattern specifici"""
        detections = []
        
        for entity_type, config in self.pattern_detector.items():
            pattern = config['pattern']
            confidence = config['confidence']
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    'entity_type': entity_type,
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': confidence,
                    'text': match.group(),
                    'source': 'patterns'
                })
        
        return detections
    
    def _is_valid_entity(self, text: str, entity_type: str, confidence: float) -> bool:
        """Filtra entità non valide"""
        
        # Confidence minima
        if confidence < 0.7:
            return False
        
        # Filtri specifici per tipo
        if entity_type == 'NOME_PERSONA':
            return self._is_valid_person_name(text, confidence)
        elif entity_type == 'ORGANIZZAZIONE':
            return self._is_valid_organization(text, confidence)
        elif entity_type == 'LUOGO':
            return self._is_valid_location(text, confidence)
        
        return True
    
    def _is_valid_person_name(self, text: str, confidence: float) -> bool:
        """Valida se è realmente un nome di persona"""
        
        # Lista di parole che NON sono mai nomi
        invalid_words = {
            'test', 'email', 'telefono', 'solo', 'nessun', 'dato', 'sensibile',
            'codice', 'fiscale', 'partita', 'iva', 'via', 'corso', 'piazza',
            'esempio', 'sample', 'demo', 'fake', 'dummy'
        }
        
        text_lower = text.lower()
        
        # Se contiene parole invalide
        if any(invalid in text_lower for invalid in invalid_words):
            return False
        
        # Deve essere almeno 2 parole per nome completo
        parts = text.split()
        if len(parts) < 2:
            return confidence > 0.9  # Soglia più alta per nomi singoli
        
        # Non più di 3 parole (evita frasi intere)
        if len(parts) > 3:
            return False
        
        # Ogni parte deve iniziare con maiuscola (per lingue che lo richiedono)
        if not all(part[0].isupper() for part in parts):
            return confidence > 0.85
        
        return True
    
    def _is_valid_organization(self, text: str, confidence: float) -> bool:
        """Valida organizzazioni"""
        # Evita parole generiche
        generic_words = {'test', 'example', 'sample', 'demo'}
        return not any(word in text.lower() for word in generic_words)
    
    def _is_valid_location(self, text: str, confidence: float) -> bool:
        """Valida luoghi"""
        # Evita parole generiche
        generic_words = {'test', 'example', 'sample', 'here', 'there'}
        return not any(word in text.lower() for word in generic_words)
    
    def _post_process(self, detections: List[Dict], text: str) -> List[Dict[str, Any]]:
        """Post-processing: rimuovi duplicati e applica ensemble"""
        
        if not detections:
            return []
        
        # 1. Raggruppa detection sovrapposte
        groups = self._group_overlapping_detections(detections)
        
        # 2. Ensemble voting per ogni gruppo
        final_detections = []
        for group in groups:
            ensemble_detection = self._ensemble_vote_group(group)
            if ensemble_detection:
                final_detections.append(ensemble_detection)
        
        return final_detections
    
    def _group_overlapping_detections(self, detections: List[Dict]) -> List[List[Dict]]:
        """Raggruppa detection che si sovrappongono"""
        if not detections:
            return []
        
        # Ordina per posizione
        sorted_detections = sorted(detections, key=lambda x: x['start'])
        
        groups = []
        current_group = [sorted_detections[0]]
        
        for detection in sorted_detections[1:]:
            # Se si sovrappone con l'ultimo del gruppo
            if detection['start'] < current_group[-1]['end']:
                current_group.append(detection)
            else:
                groups.append(current_group)
                current_group = [detection]
        
        groups.append(current_group)
        return groups
    
    def _ensemble_vote_group(self, group: List[Dict]) -> Dict[str, Any]:
        """Ensemble voting per un gruppo di detection"""
        
        if len(group) == 1:
            detection = group[0]
            # Soglia minima per detection singole
            return detection if detection['confidence'] >= 0.8 else None
        
        # Multi-detection: calcola consensus
        entity_types = [d['entity_type'] for d in group]
        most_common_type = max(set(entity_types), key=entity_types.count)
        
        # Filtra per il tipo più comune
        same_type_group = [d for d in group if d['entity_type'] == most_common_type]
        
        if len(same_type_group) >= 2:  # Almeno 2 detection dello stesso tipo
            # Calcola confidence media pesata
            sources = [d['source'] for d in same_type_group]
            unique_sources = len(set(sources))
            
            avg_confidence = sum(d['confidence'] for d in same_type_group) / len(same_type_group)
            
            # Boost per agreement tra fonti diverse
            if unique_sources >= 2:
                avg_confidence = min(0.98, avg_confidence * 1.1)
            
            # Prendi la detection migliore del gruppo
            best_detection = max(same_type_group, key=lambda x: x['confidence'])
            best_detection['confidence'] = avg_confidence
            best_detection['ensemble_size'] = len(same_type_group)
            best_detection['source_agreement'] = unique_sources
            
            return best_detection
        
        return None