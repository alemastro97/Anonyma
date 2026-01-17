#!/usr/bin/env python3
"""Script per pre-scaricare tutti i modelli necessari"""

def download_flair_models():
    """Scarica modelli Flair"""
    from flair.models import SequenceTagger
    
    models_to_download = [
        'ner-multi',
        'ner-english-ontonotes-large',
        'ner-english-ontonotes-fast'
    ]
    
    print("🧠 Downloading Flair models...")
    
    for model_name in models_to_download:
        try:
            print(f"📦 Downloading {model_name}...")
            model = SequenceTagger.load(model_name)
            print(f"✅ {model_name} downloaded and cached")
            del model  # Free memory
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
    
    print("🎯 Flair models download completed!")

def download_spacy_models():
    """Scarica modelli spaCy"""
    import spacy.cli
    
    models_to_download = [
        'it_core_news_sm',
        'en_core_web_sm'
    ]
    
    print("🔤 Downloading spaCy models...")
    
    for model_name in models_to_download:
        try:
            print(f"📦 Downloading {model_name}...")
            spacy.cli.download(model_name)
            print(f"✅ {model_name} downloaded")
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
    
    print("🎯 spaCy models download completed!")

if __name__ == "__main__":
    print("🚀 ANONYMA - Models Download Script")
    print("=" * 50)
    
    download_flair_models()
    download_spacy_models()
    
    print("\n✅ All models downloaded and cached!")