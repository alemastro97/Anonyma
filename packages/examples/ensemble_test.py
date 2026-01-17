#!/usr/bin/env python3
"""Test completo dell'ensemble detector"""

import sys
sys.path.append('..')

from anonyma_core import AnonymaEngine, AnonymizationMode
import time

def test_ensemble_accuracy():
    """Test di accuratezza dell'ensemble"""
    
    # Test cases con ground truth
    test_cases = [
        {
            'text': 'Mario Rossi, CF: RSSMRA85C15H501X, email: mario@test.com',
            'expected': ['NOME_PERSONA', 'CODICE_FISCALE', 'EMAIL'],
            'description': 'Caso misto con validazione CF'
        },
        {
            'text': 'Partita IVA: 12345678901, telefono: +39 339 1234567',
            'expected': ['PARTITA_IVA', 'TELEFONO_MOBILE_IT'],
            'description': 'P.IVA e telefono con validazione'
        },
        {
            'text': 'IBAN: IT60 X054 2811 1010 0000 0123 456',
            'expected': ['IBAN'],
            'description': 'IBAN italiano con validazione'
        },
        {
            'text': 'Solo testo normale senza dati sensibili',
            'expected': [],
            'description': 'Nessun dato sensibile (test falsi positivi)'
        },
        {
            'text': 'CF errato: ABCDEF12G34H567I, email valida: test@valid.com',
            'expected': ['EMAIL'],
            'description': 'CF invalido + email valida (test validazione)'
        }
    ]
    
    print("🎯 ENSEMBLE ACCURACY TEST")
    print("=" * 70)
    
    # Test con ensemble
    engine_ensemble = AnonymaEngine(use_ensemble=True)
    
    # Test senza ensemble (per confronto)
    engine_basic = AnonymaEngine(use_ensemble=False)
    
    total_tests = len(test_cases)
    ensemble_correct = 0
    basic_correct = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Input: {case['text']}")
        print(f"   Expected: {case['expected']}")
        
        # Test Ensemble
        start_time = time.time()
        details_ensemble = engine_ensemble.get_detection_details(case['text'])
        ensemble_time = time.time() - start_time
        
        detected_types_ensemble = [d['entity_type'] for d in details_ensemble['detections']]
        
        # Test Basic
        start_time = time.time()
        basic_detections = engine_basic.detector.detect(case['text'])
        basic_time = time.time() - start_time
        
        detected_types_basic = [d['entity_type'] for d in basic_detections if d['confidence'] >= 0.99]
        
        print(f"   Ensemble: {detected_types_ensemble} ({ensemble_time:.3f}s)")
        print(f"   Basic: {detected_types_basic} ({basic_time:.3f}s)")
        
        # Check accuracy
        ensemble_match = set(detected_types_ensemble) == set(case['expected'])
        basic_match = set(detected_types_basic) == set(case['expected'])
        
        if ensemble_match:
            ensemble_correct += 1
        if basic_match:
            basic_correct += 1
        
        print(f"   Ensemble: {'✅' if ensemble_match else '❌'}")
        print(f"   Basic: {'✅' if basic_match else '❌'}")
        
        # Mostra confidence details per ensemble
        if details_ensemble['detections']:
            print("   Confidence details:")
            for det in details_ensemble['detections']:
                sources = det.get('ensemble_sources', [det.get('source', 'unknown')])
                print(f"     - {det['entity_type']}: {det['confidence']:.3f} (sources: {sources})")
    
    print("\n" + "=" * 70)
    print("📊 RISULTATI FINALI")
    print(f"Ensemble Accuracy: {ensemble_correct}/{total_tests} ({ensemble_correct/total_tests*100:.1f}%)")
    print(f"Basic Accuracy: {basic_correct}/{total_tests} ({basic_correct/total_tests*100:.1f}%)")

def test_performance_benchmark():
    """Test di performance"""
    
    print("\n⚡ PERFORMANCE BENCHMARK")
    print("=" * 50)
    
    # Testo lungo per test performance
    long_text = """
    La società ABC S.r.l. (P.IVA: 12345678901) con sede in Via Roma 123, Milano,
    rappresentata dal sig. Mario Rossi (CF: RSSMRA85C15H501X), nato il 15/03/1985,
    email mario.rossi@abc.com, telefono +39 339 1234567, comunica che il contratto
    sottoscritto in data 15/12/2023 con la dott.ssa Elena Bianchi (CF: BNCELN80M41F205Z),
    email elena@xyz.it, telefono +39 02 12345678, per servizi di consulenza presso
    l'indirizzo Via Milano 456, Roma, è stato perfezionato. Il pagamento dell'importo
    di €50.000,00 avverrà tramite bonifico bancario sul c/c IBAN IT60X0542811101000000123456.
    """ * 5  # Moltiplica per aumentare il volume
    
    engine = AnonymaEngine(use_ensemble=True)
    
    print(f"📏 Lunghezza testo: {len(long_text)} caratteri")
    
    # Benchmark detection
    start_time = time.time()
    details = engine.get_detection_details(long_text)
    detection_time = time.time() - start_time
    
    print(f"⏱️ Tempo detection: {detection_time:.3f}s")
    print(f"🚀 Velocità: {len(long_text)/detection_time:.0f} chars/sec")
    print(f"🔍 Detection trovate: {details['high_confidence_detections']}")
    print(f"📊 Tipi rilevati: {details['detection_summary']}")
    
    # Benchmark anonymization
    start_time = time.time()
    result = engine.anonymize(long_text, AnonymizationMode.REDACT)
    anon_time = time.time() - start_time
    
    print(f"⏱️ Tempo anonymization: {anon_time:.3f}s")
    print(f"⚡ Tempo totale: {detection_time + anon_time:.3f}s")

if __name__ == "__main__":
    test_ensemble_accuracy()
    test_performance_benchmark()