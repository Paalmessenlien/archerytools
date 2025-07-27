#!/usr/bin/env python3
"""
DeepSeek Translation Service for Arrow Scraper
Translates scraped content from various languages to English
"""

import json
import time
from typing import Dict, Any, Optional, List
import openai
from pathlib import Path

class DeepSeekTranslator:
    """Translation service using DeepSeek API"""
    
    def __init__(self, api_key: str):
        """Initialize translator with DeepSeek API key"""
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Language detection patterns
        self.language_indicators = {
            'german': [
                'der', 'die', 'das', 'und', 'oder', 'mit', 'von', 'zu', 'in', 'auf',
                'für', 'ein', 'eine', 'einen', 'ich', 'du', 'er', 'sie', 'es',
                'wir', 'ihr', 'haben', 'sein', 'werden', 'können', 'sollen',
                'pfeil', 'bogen', 'schaft', 'spine', 'carbon', 'aluminium'
            ],
            'italian': [
                'il', 'la', 'lo', 'gli', 'le', 'un', 'una', 'di', 'da', 'in',
                'con', 'su', 'per', 'tra', 'fra', 'a', 'del', 'della', 'dello',
                'dei', 'delle', 'nel', 'nella', 'nei', 'nelle', 'sul', 'sulla',
                'freccia', 'arco', 'carbonio', 'alluminio', 'spine'
            ],
            'french': [
                'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou',
                'avec', 'pour', 'dans', 'sur', 'par', 'sans', 'sous', 'entre',
                'flèche', 'arc', 'carbone', 'aluminium', 'spine'
            ],
            'spanish': [
                'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'y', 'o',
                'con', 'para', 'en', 'por', 'sin', 'sobre', 'entre', 'desde',
                'flecha', 'arco', 'carbono', 'aluminio', 'spine'
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Detect the primary language of the text"""
        if not text or len(text) < 50:
            return 'english'  # Default to English for short texts
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count language-specific words
        language_scores = {}
        
        for language, indicators in self.language_indicators.items():
            score = 0
            for indicator in indicators:
                # Count exact word matches
                score += words.count(indicator)
                # Count partial matches for compound words (especially German)
                if language == 'german':
                    score += sum(1 for word in words if indicator in word and len(word) > 3)
            
            language_scores[language] = score
        
        # Determine most likely language
        if not language_scores or max(language_scores.values()) < 3:
            return 'english'  # Default if no clear indicators
        
        detected = max(language_scores, key=language_scores.get)
        print(f"🌐 Detected language: {detected} (confidence: {language_scores[detected]} indicators)")
        return detected
    
    def translate_text(self, text: str, source_language: Optional[str] = None, 
                       target_language: str = 'english') -> Dict[str, Any]:
        """Translate text using DeepSeek API"""
        
        if not text or not text.strip():
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': 'unknown',
                'target_language': target_language,
                'translation_confidence': 0.0
            }
        
        # Auto-detect language if not provided
        if not source_language:
            source_language = self.detect_language(text)
        
        # Skip translation if already in target language
        if source_language == target_language:
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': source_language,
                'target_language': target_language,
                'translation_confidence': 1.0
            }
        
        try:
            # Create translation prompt
            prompt = f"""
Translate the following {source_language} text about archery arrows to {target_language}.
Preserve all technical terms, specifications, measurements, and product names.
Keep arrow spine numbers, diameters, weights, and brand names unchanged.
Maintain the original structure and formatting.

Text to translate:
{text}

Provide only the translation, no explanations."""

            print(f"🌍 Translating {len(text)} characters from {source_language} to {target_language}...")
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional translator specializing in archery and sporting goods terminology. Translate accurately while preserving technical specifications."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent translations
                max_tokens=4000
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Rate limiting
            time.sleep(1)
            
            return {
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language,
                'translation_confidence': 0.9,  # High confidence for API translation
                'translation_model': 'deepseek-chat'
            }
            
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return {
                'original_text': text,
                'translated_text': text,  # Fallback to original
                'source_language': source_language,
                'target_language': target_language,
                'translation_confidence': 0.0,
                'error': str(e)
            }
    
    def translate_arrow_data(self, arrow_data: Dict[str, Any], 
                            source_language: Optional[str] = None) -> Dict[str, Any]:
        """Translate arrow specification data"""
        
        translated_data = arrow_data.copy()
        translation_info = {
            'translations_performed': [],
            'source_language': source_language,
            'target_language': 'english'
        }
        
        # Fields to translate
        translatable_fields = [
            'model_name',
            'description', 
            'material',
            'arrow_type',
            'recommended_use',
            'notes'
        ]
        
        # Auto-detect language from description if not provided
        if not source_language and arrow_data.get('description'):
            source_language = self.detect_language(arrow_data['description'])
            translation_info['source_language'] = source_language
        
        # Skip translation if already English
        if source_language == 'english':
            translated_data['translation_info'] = translation_info
            return translated_data
        
        print(f"🔤 Translating arrow data from {source_language}...")
        
        # Translate each field
        for field in translatable_fields:
            if field in arrow_data and arrow_data[field]:
                original_value = arrow_data[field]
                
                # Skip very short values (likely already English or not worth translating)
                if len(str(original_value)) < 10:
                    continue
                
                translation_result = self.translate_text(
                    str(original_value), 
                    source_language=source_language
                )
                
                if translation_result['translation_confidence'] > 0.5:
                    # Store original and translated versions
                    translated_data[f'{field}_original'] = original_value
                    translated_data[field] = translation_result['translated_text']
                    
                    translation_info['translations_performed'].append({
                        'field': field,
                        'original': original_value,
                        'translated': translation_result['translated_text'],
                        'confidence': translation_result['translation_confidence']
                    })
                    
                    print(f"   ✅ {field}: {original_value[:50]}... → {translation_result['translated_text'][:50]}...")
        
        # Translate spine specification notes if present
        if 'spine_specifications' in translated_data:
            for i, spec in enumerate(translated_data['spine_specifications']):
                if 'notes' in spec and spec['notes']:
                    translation_result = self.translate_text(
                        spec['notes'], 
                        source_language=source_language
                    )
                    
                    if translation_result['translation_confidence'] > 0.5:
                        translated_data['spine_specifications'][i]['notes_original'] = spec['notes']
                        translated_data['spine_specifications'][i]['notes'] = translation_result['translated_text']
        
        translated_data['translation_info'] = translation_info
        
        if translation_info['translations_performed']:
            print(f"   🌍 Completed {len(translation_info['translations_performed'])} translations")
        
        return translated_data
    
    def translate_manufacturer_data(self, manufacturer_data: Dict[str, Any], 
                                   source_language: Optional[str] = None) -> Dict[str, Any]:
        """Translate complete manufacturer data including all arrows"""
        
        translated_data = manufacturer_data.copy()
        
        print(f"🏭 Translating manufacturer data: {manufacturer_data.get('manufacturer', 'Unknown')}")
        
        if 'arrows' in translated_data:
            translated_arrows = []
            
            for i, arrow in enumerate(translated_data['arrows']):
                print(f"   📋 Translating arrow {i+1}/{len(translated_data['arrows'])}: {arrow.get('model_name', 'Unknown')}")
                
                translated_arrow = self.translate_arrow_data(arrow, source_language)
                translated_arrows.append(translated_arrow)
                
                # Rate limiting between arrows
                time.sleep(0.5)
            
            translated_data['arrows'] = translated_arrows
        
        # Add metadata about translation
        translated_data['translation_metadata'] = {
            'translated_at': time.time(),
            'source_language': source_language,
            'target_language': 'english',
            'translator': 'deepseek-chat',
            'total_arrows_processed': len(translated_data.get('arrows', []))
        }
        
        return translated_data

def main():
    """Test the translation functionality"""
    import os
    from dotenv import load_dotenv
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
    translator = DeepSeekTranslator(api_key)
    
    # Test language detection
    test_texts = [
        "Der Carbon Pfeilschaft mit hoher Präzision und ausgezeichneter Ballung",
        "Freccia in carbonio con elevata precisione e ottimo raggruppamento",
        "Carbon arrow shaft with high precision and excellent grouping",
        "Flèche en carbone avec haute précision et excellent groupement"
    ]
    
    print("🧪 Testing language detection:")
    for text in test_texts:
        lang = translator.detect_language(text)
        print(f"   '{text[:40]}...' → {lang}")
    
    # Test translation
    print(f"\n🔤 Testing translation:")
    german_text = "Hochwertiger Carbon-Pfeilschaft für den Jagd- und 3D-Bereich. Spine 400, Außendurchmesser 8.5mm, Gewicht 9.5 GPI."
    
    result = translator.translate_text(german_text)
    print(f"Original: {result['original_text']}")
    print(f"Translated: {result['translated_text']}")
    print(f"Language: {result['source_language']} → {result['target_language']}")
    print(f"Confidence: {result['translation_confidence']}")

if __name__ == "__main__":
    main()