#!/usr/bin/env python3
"""
Test DeepSeek translation functionality
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Import the translation service from our scraper
sys.path.append('.')
from tophat_archery_scraper import TranslationService

async def test_translation():
    """Test DeepSeek translation with German archery text"""
    
    load_dotenv()
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment variables")
        return
    
    print(f"✅ DeepSeek API key found: {deepseek_api_key[:8]}...")
    
    # Initialize translation service
    translator = TranslationService(deepseek_api_key)
    
    # Test German archery texts
    test_texts = [
        {
            "type": "Title",
            "text": "Aurel Agil 300"
        },
        {
            "type": "Arrow Type", 
            "text": "3D, Feld, FITA, Target, WA"
        },
        {
            "type": "Arrow Type 2",
            "text": "3D, Allzweck, Feld, Target"
        },
        {
            "type": "Description",
            "text": "Der AGIL™ folgt dem Standard-Carbonschaft-Durchmesser und wurde als Ultraleicht-Schaft konzipiert. Die Leistungsparameter der Schäfte erlauben messerscharfe Flugbahnen über längere Distanzen mit hervorragender Penetrationskraft im Ziel."
        },
        {
            "type": "Long Description",
            "text": "Von vielen Schützen werden die dünnen Durchmesser für Field und Target bevorzugt. Nun hat auch die ABSOLUTE.Serie einen schlanken Schaft im Programm. Die Spinewerte decken einen breiten Einsatzbereich ab. Erhältlich in Spine 350, 400, 500 und 600."
        }
    ]
    
    print(f"\n🤖 Testing DeepSeek Translation")
    print("=" * 50)
    
    for i, test_item in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {test_item['type']}")
        print(f"🇩🇪 German: {test_item['text']}")
        
        try:
            translated = await translator.translate_text(test_item['text'])
            print(f"🇺🇸 English: {translated}")
            
            if translated != test_item['text']:
                print("✅ Translation successful!")
            else:
                print("⚠️  No translation occurred (might not be German)")
                
        except Exception as e:
            print(f"❌ Translation failed: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_translation())