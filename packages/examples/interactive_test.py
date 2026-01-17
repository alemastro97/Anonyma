#!/usr/bin/env python3
"""Interactive test per Anonyma Core con input personalizzato"""

import sys
sys.path.append('..')

from anonyma_core import AnonymaEngine, AnonymizationMode

def test_custom_text():
    """Test interattivo con testo personalizzato"""
    engine = AnonymaEngine()
    
    print("🎭 ANONYMA CORE - Test Interattivo")
    print("=" * 50)
    
    # Esempi predefiniti
    examples = {
        "1": "Mario Rossi abita in Via Roma 123, Milano. Email: mario@test.com",
        "2": "La dottoressa Elena Bianchi (CF: BNCELN80M41H501Z) lavora presso l'ospedale di Roma",
        "3": "Contattare Giovanni Verdi al numero +39 335 1234567 oppure all'email giovanni.verdi@azienda.it",
        "4": "Azienda XYZ S.r.l., P.IVA 12345678901, sede in Via Milano 45, 20100 Milano"
    }
    
    print("\nScegli un esempio o inserisci testo personalizzato:")
    for key, example in examples.items():
        print(f"{key}. {example[:50]}...")
    print("5. Inserisci testo personalizzato")
    print("0. Exit")
    
    choice = input("\nScegli (0-5): ").strip()
    
    if choice == "0":
        return
    elif choice in examples:
        text = examples[choice]
    elif choice == "5":
        text = input("\nInserisci il tuo testo: ")
    else:
        print("Scelta non valida!")
        return
    
    print(f"\n📝 Testo da processare:")
    print(f"'{text}'")
    print("\n" + "="*60)
    
    # Test tutte le modalità
    modes = [
        (AnonymizationMode.REDACT, "🔒 REDACT"),
        (AnonymizationMode.SUBSTITUTE, "🔄 SUBSTITUTE"), 
        (AnonymizationMode.VISUAL_REDACT, "👁️ VISUAL_REDACT")
    ]
    
    for mode, name in modes:
        print(f"\n{name}:")
        print("-" * 30)
        try:
            result = engine.anonymize(text, mode)
            print(f"Result: {result.anonymized_text}")
            
            if result.mapping:
                print(f"Mapping: {result.mapping}")
            if result.reverse_key:
                print(f"Reverse Key: {result.reverse_key}")
                
        except Exception as e:
            print(f"❌ Errore: {e}")
    
    # Ask for another test
    again = input("\n🔄 Vuoi testare altro testo? (y/n): ").strip().lower()
    if again == 'y':
        test_custom_text()

def batch_test():
    """Test batch con più testi"""
    engine = AnonymaEngine()
    
    test_texts = [
        "Mario Rossi, nato il 15/03/1985",
        "Email: test@example.com, Tel: +39 333 1234567", 
        "CF: RSSMRA85C15H501X, P.IVA: 12345678901",
        "Indirizzo: Via Roma 123, 20100 Milano"
    ]
    
    print("🚀 BATCH TEST")
    print("=" * 40)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Testing: {text}")
        result = engine.anonymize(text, AnonymizationMode.REDACT)
        print(f"   Result: {result.anonymized_text}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        batch_test()
    else:
        test_custom_text()