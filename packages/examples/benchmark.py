#!/usr/bin/env python3
"""Benchmark test per valutare le performance"""

import sys
import time
sys.path.append('..')

from anonyma_core import AnonymaEngine, AnonymizationMode

def benchmark_test():
    """Test di performance"""
    engine = AnonymaEngine()
    
    # Testo di test più lungo
    long_text = """
    La società ABC S.r.l., con sede legale in Via Roma 123, 20100 Milano, 
    P.IVA 12345678901, rappresentata dal sig. Mario Rossi (CF: RSSMRA85C15H501X),
    nato a Milano il 15/03/1985, residente in Via Garibaldi 456, 20121 Milano,
    telefono +39 02 1234567, email mario.rossi@abc.it, comunica che in data
    01/12/2023 è stato sottoscritto un contratto con la dott.ssa Elena Bianchi
    (CF: BNCELN80M41F205Z), nata a Roma il 15/08/1980, email elena.bianchi@xyz.com,
    telefono +39 06 9876543, per la fornitura di servizi di consulenza.
    """ * 10  # Moltiplica per aumentare la dimensione
    
    print("⚡ BENCHMARK TEST")
    print("=" * 50)
    print(f"📏 Lunghezza testo: {len(long_text)} caratteri")
    
    modes = [
        (AnonymizationMode.REDACT, "REDACT"),
        (AnonymizationMode.SUBSTITUTE, "SUBSTITUTE"),
        (AnonymizationMode.VISUAL_REDACT, "VISUAL_REDACT")
    ]
    
    for mode, name in modes:
        print(f"\n🧪 Testing {name}...")
        
        # Warm up
        engine.anonymize(long_text[:100], mode)
        
        # Benchmark
        start_time = time.time()
        result = engine.anonymize(long_text, mode)
        end_time = time.time()
        
        duration = end_time - start_time
        chars_per_sec = len(long_text) / duration
        
        print(f"   ⏱️  Tempo: {duration:.3f}s")
        print(f"   🚀 Velocità: {chars_per_sec:.0f} chars/sec")
        print(f"   📝 Output length: {len(result.anonymized_text)} chars")

if __name__ == "__main__":
    benchmark_test()