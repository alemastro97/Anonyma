#!/usr/bin/env python3
"""Test completo con engine"""

import sys
sys.path.append('..')

from anonyma_core import AnonymaEngine, AnonymizationMode

def test_all_modes():
    # Test text con vari tipi di PII italiani
    test_text = """
    Il sig. Mario Rossi, nato il 15/03/1985, abita in Via Roma 123, Milano.
    Email: mario.rossi@email.com
    Telefono: +39 339 1234567
    Codice Fiscale: RSSMRA85C15H501X
    """
    
    # Prova prima senza ensemble, poi con ensemble
    for use_ensemble in [False, True]:
        ensemble_label = "CON ENSEMBLE" if use_ensemble else "SENZA ENSEMBLE"
        print(f"\n🎭 ANONYMA CORE - {ensemble_label}")
        print("=" * 60)
        
        try:
            engine = AnonymaEngine(use_ensemble=use_ensemble)
            
            print(f"📝 Testo originale:")
            print(test_text)
            print("\n" + "="*60 + "\n")
            
            # Test Mode 1: Redaction
            print("1️⃣  MODALITÀ REDACT:")
            result1 = engine.anonymize(test_text, AnonymizationMode.REDACT)
            print(result1.anonymized_text)
            print("\n" + "-"*40 + "\n")
            
            # Test Mode 2: Substitute
            print("2️⃣  MODALITÀ SUBSTITUTE:")
            result2 = engine.anonymize(test_text, AnonymizationMode.SUBSTITUTE)
            print(result2.anonymized_text)
            if result2.mapping:
                print(f"\n🔑 Mapping: {result2.mapping}")
            if result2.reverse_key:
                print(f"🆔 Reverse Key: {result2.reverse_key}")
            print("\n" + "-"*40 + "\n")
            
            # Test Mode 3: Visual Redact
            print("3️⃣  MODALITÀ VISUAL_REDACT:")
            result3 = engine.anonymize(test_text, AnonymizationMode.VISUAL_REDACT)
            print(result3.anonymized_text)
            
            print(f"\n✅ {ensemble_label} completato con successo!")
            
        except Exception as e:
            print(f"❌ Errore con {ensemble_label}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_all_modes()