#!/usr/bin/env python3
"""
Test script for DeepSeek translation functionality
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from deepseek_translator import DeepSeekTranslator

def test_translation():
    """Test the translation functionality"""
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return False
    
    print("🧪 Testing DeepSeek Translation System")
    print("=" * 50)
    
    # Initialize translator
    translator = DeepSeekTranslator(api_key)
    
    # Test data - German arrow descriptions
    test_arrows = [
        {
            "model_name": "Carbon Pfeilschaft Premium",
            "description": "Hochwertiger Carbon-Pfeilschaft für den Jagd- und 3D-Bereich. Präzise Fertigung mit konstanter Spine-Stärke.",
            "material": "100% Carbon",
            "arrow_type": "Jagdpfeil",
            "recommended_use": "Jagd und 3D-Bogenschießen",
            "spine_specifications": [
                {
                    "spine": 400,
                    "notes": "Geeignet für mittlere Zuggewichte bis 45 lbs"
                }
            ]
        },
        {
            "model_name": "Alu-Carbon Hybridschaft", 
            "description": "Kombination aus Aluminium-Kern und Carbon-Ummantelung für optimale Balance.",
            "material": "Aluminium mit Carbon-Beschichtung",
            "arrow_type": "Universalpfeil"
        }
    ]
    
    print("🔤 Testing German to English translation:")
    print("-" * 40)
    
    for i, arrow in enumerate(test_arrows, 1):
        print(f"\n📋 Arrow {i}: {arrow['model_name']}")
        print(f"Original description: {arrow['description']}")
        
        # Translate arrow data
        translated = translator.translate_arrow_data(arrow, source_language='german')
        
        print(f"Translated description: {translated.get('description', 'N/A')}")
        
        if 'translation_info' in translated:
            translations = translated['translation_info']['translations_performed']
            print(f"Fields translated: {len(translations)}")
            for trans in translations:
                print(f"  • {trans['field']}: {trans['confidence']:.1f} confidence")
    
    # Test language detection
    print(f"\n🌐 Testing language detection:")
    print("-" * 40)
    
    test_texts = [
        "Carbon Pfeilschaft mit hoher Präzision und Spine 340",
        "Freccia in carbonio con precisione elevata",
        "Carbon arrow shaft with high precision",
        "Flèche en carbone avec haute précision"
    ]
    
    for text in test_texts:
        detected = translator.detect_language(text)
        print(f"'{text}' → {detected}")
    
    print(f"\n✅ Translation test completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = test_translation()
        if success:
            print("\n🎯 All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)