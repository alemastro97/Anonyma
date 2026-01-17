from typing import List, Dict, Any, Tuple
from faker import Faker
import uuid

class Substitutor:
    def __init__(self):
        self.faker_it = Faker('it_IT')
        self.faker_en = Faker('en_US')
        
        self.substitution_map = {
            'PERSON': lambda: self.faker_it.name(),
            'PHONE_NUMBER': lambda: self.faker_it.phone_number(),
            'EMAIL_ADDRESS': lambda: self.faker_it.email(),
            'LOCATION': lambda: self.faker_it.city(),
            'CODICE_FISCALE': lambda: self._generate_fake_cf(),
            'PARTITA_IVA': lambda: f"{self.faker_it.random_int(10000000000, 99999999999)}",
        }
    
    def anonymize(self, text: str, detections: List[Dict[str, Any]]) -> Tuple[str, Dict[str, str], str]:
        """Modalità 2: Sostituisce con dati fake + mappa di reversibilità"""
        # Sort detections by start position (reverse order)
        sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)
        
        result = text
        mapping = {}
        reverse_key = str(uuid.uuid4())
        
        for i, detection in enumerate(sorted_detections):
            start = detection['start']
            end = detection['end']
            entity_type = detection['entity_type']
            original_value = detection['text']
            
            # Generate replacement
            replacement = self._get_replacement(entity_type, original_value)
            
            # Create mapping key
            mapping_key = f"{entity_type}_{i}"
            mapping[mapping_key] = original_value
            
            # Replace in text
            result = result[:start] + replacement + result[end:]
        
        return result, mapping, reverse_key
    
    def _get_replacement(self, entity_type: str, original_value: str) -> str:
        """Genera sostituzione appropriata per il tipo di entità"""
        if entity_type in self.substitution_map:
            return self.substitution_map[entity_type]()
        else:
            # Generic replacement
            return f"[{entity_type.replace('_', ' ').title()}]"
    
    def _generate_fake_cf(self) -> str:
        """Genera un codice fiscale fake ma realistico"""
        import random
        import string
        
        # Simplified fake CF generator
        letters = ''.join(random.choices(string.ascii_uppercase, k=6))
        numbers = ''.join(random.choices(string.digits, k=2))
        letter = random.choice(string.ascii_uppercase)
        more_numbers = ''.join(random.choices(string.digits, k=2))
        more_letter = random.choice(string.ascii_uppercase)
        final_numbers = ''.join(random.choices(string.digits, k=3))
        final_letter = random.choice(string.ascii_uppercase)
        
        return f"{letters}{numbers}{letter}{more_numbers}{more_letter}{final_numbers}{final_letter}"