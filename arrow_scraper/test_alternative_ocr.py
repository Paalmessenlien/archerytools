#!/usr/bin/env python3
"""
Test alternative OCR methods for Carbon Express specification images.

This script tests multiple OCR approaches:
1. Tesseract OCR (free, local)
2. EasyOCR (free, local, AI-based)
3. Google Cloud Vision API (paid, cloud)
4. Azure Computer Vision (paid, cloud)
5. AWS Textract (paid, cloud)
"""

import os
import requests
import json
import re
from pathlib import Path
from typing import List, Dict, Optional

def download_image(url: str, filename: str) -> str:
    """Download image and return local path"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filepath = Path(filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded image: {filename}")
        return str(filepath)
    except Exception as e:
        print(f"❌ Failed to download image: {e}")
        return None

def test_tesseract_ocr(image_path: str) -> Optional[str]:
    """Test Tesseract OCR (requires pytesseract + tesseract installation)"""
    try:
        import pytesseract
        from PIL import Image
        
        print("🔍 Testing Tesseract OCR...")
        
        # Open image
        image = Image.open(image_path)
        
        # Extract text
        text = pytesseract.image_to_string(image)
        
        print(f"📝 Tesseract extracted {len(text)} characters")
        return text
        
    except ImportError:
        print("⚠️  Tesseract not available (pip install pytesseract)")
        return None
    except Exception as e:
        print(f"❌ Tesseract error: {e}")
        return None

def test_easyocr(image_path: str) -> Optional[str]:
    """Test EasyOCR (requires easyocr installation)"""
    try:
        import easyocr
        
        print("🔍 Testing EasyOCR...")
        
        # Initialize reader
        reader = easyocr.Reader(['en'])
        
        # Extract text
        results = reader.readtext(image_path)
        
        # Combine all text
        text_parts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Only include confident results
                text_parts.append(text)
        
        combined_text = " ".join(text_parts)
        print(f"📝 EasyOCR extracted {len(combined_text)} characters from {len(results)} detections")
        return combined_text
        
    except ImportError:
        print("⚠️  EasyOCR not available (pip install easyocr)")
        return None
    except Exception as e:
        print(f"❌ EasyOCR error: {e}")
        return None

def test_google_vision_ocr(image_path: str, api_key: str = None) -> Optional[str]:
    """Test Google Cloud Vision OCR"""
    if not api_key:
        print("⚠️  Google Cloud Vision API key not provided")
        return None
    
    try:
        import base64
        
        print("🔍 Testing Google Cloud Vision OCR...")
        
        # Encode image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # API request
        url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
        
        data = {
            "requests": [
                {
                    "image": {
                        "content": base64_image
                    },
                    "features": [
                        {
                            "type": "TEXT_DETECTION"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'responses' in result and result['responses']:
                annotations = result['responses'][0].get('textAnnotations', [])
                if annotations:
                    text = annotations[0]['description']
                    print(f"📝 Google Vision extracted {len(text)} characters")
                    return text
        
        print(f"❌ Google Vision API error: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"❌ Google Vision error: {e}")
        return None

def parse_specification_text(ocr_text: str) -> Dict:
    """Parse OCR text to extract arrow specifications"""
    print("🔍 Parsing OCR text for specifications...")
    
    # Common patterns for arrow specifications
    spine_pattern = r'\b(250|300|340|350|400|450|500|550|600|650|700|750|800|850|900|950|1000|1100|1200|1300|1400|1500|1600|1700|1800)\b'
    gpi_pattern = r'\b(\d+\.?\d*)\s*(?:gpi|grains?|grain per inch)\b'
    diameter_pattern = r'\.?(\d+\.\d+)["″]?\s*(?:diameter|od|o\.d\.)?'
    
    # Find all spine values
    spine_matches = re.findall(spine_pattern, ocr_text, re.IGNORECASE)
    
    # Find GPI weights (decimal numbers near "gpi" or "grain")
    gpi_matches = re.findall(gpi_pattern, ocr_text, re.IGNORECASE)
    
    # Find diameter values
    diameter_matches = re.findall(diameter_pattern, ocr_text, re.IGNORECASE)
    
    # Try to extract model name
    model_patterns = [
        r'maxima\s+(\w+)',
        r'(\w+)\s+arrow',
        r'carbon\s+express\s+(\w+)'
    ]
    
    model_name = None
    for pattern in model_patterns:
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            model_name = match.group(0)
            break
    
    result = {
        "model_name": model_name or "Carbon Express Model",
        "spine_values": [int(s) for s in spine_matches],
        "gpi_values": [float(g) for g in gpi_matches],
        "diameter_values": [float(d) for d in diameter_matches],
        "raw_text": ocr_text
    }
    
    print(f"📊 Parsed: {len(result['spine_values'])} spines, {len(result['gpi_values'])} GPI values, {len(result['diameter_values'])} diameters")
    
    return result

def test_all_ocr_methods():
    """Test all available OCR methods on Carbon Express images"""
    
    print("🚀 Testing Alternative OCR Methods for Carbon Express")
    print("=" * 70)
    
    # Test images
    test_images = [
        {
            "name": "Maxima Sable RZ",
            "url": "https://cdn-ilchokf.nitrocdn.com/nqkqluPOLqauqjblimVNksnJtfbWDRlW/assets/images/optimized/rev-c783676/www.feradyne.com/wp-content/uploads/2022/01/Maxima-Sable-RZ.png"
        },
        {
            "name": "Maxima Triad", 
            "url": "https://cdn-ilchokf.nitrocdn.com/nqkqluPOLqauqjblimVNksnJtfbWDRlW/assets/images/optimized/rev-c783676/www.feradyne.com/wp-content/uploads/2019/12/Maxima-Triad.png"
        }
    ]
    
    # OCR methods to test
    ocr_methods = [
        ("Tesseract", test_tesseract_ocr),
        ("EasyOCR", test_easyocr),
        ("Google Vision", lambda path: test_google_vision_ocr(path, os.getenv("GOOGLE_VISION_API_KEY")))
    ]
    
    for i, image_info in enumerate(test_images, 1):
        print(f"\n🖼️  Test Image {i}: {image_info['name']}")
        print(f"URL: {image_info['url']}")
        print("-" * 60)
        
        # Download image
        filename = f"ocr_test_{i}.png"
        image_path = download_image(image_info['url'], filename)
        
        if not image_path:
            continue
        
        # Test each OCR method
        for method_name, method_func in ocr_methods:
            print(f"\n📋 Testing {method_name}:")
            
            ocr_text = method_func(image_path)
            
            if ocr_text:
                # Parse the extracted text
                parsed_data = parse_specification_text(ocr_text)
                
                print(f"✅ {method_name} Results:")
                print(f"   Model: {parsed_data['model_name']}")
                print(f"   Spines: {parsed_data['spine_values']}")
                print(f"   GPI values: {parsed_data['gpi_values']}")
                print(f"   Diameters: {parsed_data['diameter_values']}")
                
                # Show sample of raw text
                sample_text = ocr_text[:200].replace('\n', ' ')
                print(f"   Sample text: {sample_text}...")
                
                # Check if we got useful data
                if parsed_data['spine_values'] and parsed_data['gpi_values']:
                    print(f"🎯 {method_name}: SUCCESS - Found specifications!")
                else:
                    print(f"⚠️  {method_name}: Partial - OCR worked but specs unclear")
            else:
                print(f"❌ {method_name}: Failed to extract text")
        
        # Clean up
        try:
            os.remove(image_path)
            print(f"\n🗑️  Cleaned up {filename}")
        except:
            pass
    
    print("\n" + "=" * 70)
    print("📊 OCR METHOD COMPARISON:")
    print("🆓 Tesseract: Free, local, basic OCR")
    print("🤖 EasyOCR: Free, local, AI-based, better accuracy")
    print("☁️  Google Vision: Paid, cloud, enterprise-grade")
    print("💡 OpenAI Vision: Paid, cloud, AI + reasoning (tested earlier)")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("1. Try EasyOCR first (free, good for tables)")
    print("2. Fallback to Tesseract (free, widely available)")
    print("3. Use Google Vision for production (most reliable)")
    print("4. Consider OpenAI Vision for complex layouts")

def install_ocr_dependencies():
    """Show how to install OCR dependencies"""
    print("🔧 OCR DEPENDENCY INSTALLATION:")
    print("-" * 40)
    print("Tesseract:")
    print("  sudo apt-get install tesseract-ocr  # Ubuntu/Debian")
    print("  brew install tesseract             # macOS")
    print("  pip install pytesseract pillow")
    print()
    print("EasyOCR:")
    print("  pip install easyocr")
    print()
    print("Google Vision:")
    print("  pip install google-cloud-vision")
    print("  # Need Google Cloud account + API key")

if __name__ == "__main__":
    import sys
    
    if "--help" in sys.argv:
        install_ocr_dependencies()
    else:
        test_all_ocr_methods()