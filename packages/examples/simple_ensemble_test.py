#!/usr/bin/env python3
"""Test Flair detector"""

import sys
sys.path.append('..')

def test_flair_multilingual():
    """Test multilingua con Flair"""
    print("🌍 Testing Flair multilingual detection...")
    
    test_cases = {
        'Italian': "Mario Rossi abita a Roma. Email: mario@test.com",
        'English': "John Smith lives in London. Email: john@example.com", 
        'Spanish': "Carlos García vive en Madrid. Email: carlos@ejemplo.com",
        'French': "Pierre Dubois habite à Paris. Email: pierre@exemple.fr",
        'German': "Hans Müller wohnt in Berlin. Email: hans@beispiel.de"
    }
    
    try:
        from anonyma_core import AnonymaEngine, AnonymizationMode
        
        engine = AnonymaEngine(use_flair=True)
        
        for language, text in test_cases.items():
            print(f"\n🔍 {language}: {text}")
            
            result = engine.anonymize(text, AnonymizationMode.REDACT)
            print(f"   Result: {result.anonymized_text}")
            
        print("\n✅ Multilingual test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_problematic_cases():
    """Test casi che davano problemi prima"""
    print("\n🎯 Testing problematic cases...")
    
    problem_cases = [
        "Test email: user@example.com",  # Non deve rilevare "Test email" come persona
        "Solo telefono: +39 333 1234567",  # Non deve rilevare "Solo telefono" come persona
        "Mario Rossi e Elena Bianchi",  # Deve rilevare entrambi i nomi
        "Nessun dato sensibile qui"  # Non deve rilevare niente
    ]
    
    try:
        from anonyma_core import AnonymaEngine, AnonymizationMode
        
        engine = AnonymaEngine(use_flair=True)
        
        for case in problem_cases:
            print(f"\n📝 Input: {case}")
            result = engine.anonymize(case, AnonymizationMode.REDACT)
            print(f"   Output: {result.anonymized_text}")
            
        print("\n✅ Problematic cases test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧠 FLAIR PII DETECTOR TEST")
    print("=" * 50)
    
    test_flair_multilingual()
    test_problematic_cases()