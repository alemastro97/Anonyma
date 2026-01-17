#!/usr/bin/env python3
"""Test semplificato senza dipendenze esterne complicate"""

import sys
sys.path.append('..')

import re
from anonyma_core.modes import AnonymizationMode

def simple_pii_detector(text: str):
    """Detector semplificato con solo regex"""
    patterns = {
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'PHONE': r'\+39[\s-]?[0-9]{2,4}[\s-]?[0-9]{6,8}',
        'CODICE_FISCALE': r'\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b',
        'PERSON': r'\b(?:sig\.?\s+|dott\.?\s+)?[A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,20}\b',
    }
    
    detections = []
    for entity_type, pattern in patterns.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            detections.append({
                'entity_type': entity_type,
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.8,
                'text': match.group()
            })
    
    return detections

def simple_redactor(text: str, detections):
    """Redattore semplificato"""
    sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)
    
    result = text
    for detection in sorted_detections:
        start = detection['start']
        end = detection['end']
        redacted = "█" * (end - start)
        result = result[:start] + redacted + result[end:]
    
    return result

def test_simple():
    """Test semplificato"""
    test_text = """
    Il sig. Mario Rossi, nato il 15/03/1985, abita in Via Roma 123, Milano.
    Email: mario.rossi@email.com
    Telefono: +39 339 1234567
    Codice Fiscale: RSSMRA85C15H501X
    """
    
    print("🎭 ANONYMA CORE - Test Semplificato")
    print("=" * 50)
    print(f"📝 Testo originale:")
    print(test_text)
    print("\n" + "="*60 + "\n")
    
    # Detect PII
    detections = simple_pii_detector(test_text)
    print(f"🔍 Trovate {len(detections)} informazioni sensibili:")
    for detection in detections:
        print(f"   - {detection['entity_type']}: '{detection['text']}'")
    
    # Redact
    print(f"\n🔒 Testo anonimizzato:")
    anonymized = simple_redactor(test_text, detections)
    print(anonymized)

def test_with_engine():
    """Test usando l'engine vero"""
    print("\n" + "="*60)
    print("🚀 Test con AnonymaEngine")
    print("="*60)
    
    try:
        from anonyma_core import AnonymaEngine, AnonymizationMode
        
        # Usa engine senza ensemble per sicurezza
        engine = AnonymaEngine(use_ensemble=False)
        
        test_text = "Email: mario@test.com, Tel: +39 339 1234567"
        print(f"Input: {test_text}")
        
        result = engine.anonymize(test_text, AnonymizationMode.REDACT)
        print(f"Output: {result.anonymized_text}")
        
        print("✅ Engine test passed!")
        
    except Exception as e:
        print(f"❌ Engine test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()
    test_with_engine()