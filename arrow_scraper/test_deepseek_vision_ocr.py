#!/usr/bin/env python3
"""
Test DeepSeek vision model for OCR on Carbon Express specification images.

This script will:
1. Download a Carbon Express specification image
2. Use DeepSeek's vision model to analyze the image
3. Extract spine, GPI, diameter, and other specifications from the image
4. Test if this approach can work for Carbon Express extraction
"""

import os
import requests
import base64
import json
from pathlib import Path
from dotenv import load_dotenv

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

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for API"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return base64_encoded
    except Exception as e:
        print(f"❌ Failed to encode image: {e}")
        return None

def analyze_image_with_deepseek(image_path: str, api_key: str) -> dict:
    """Use DeepSeek vision model to analyze specification image"""
    
    # Encode image to base64
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return None
    
    # Prepare API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Create the vision prompt
    prompt = """
    Analyze this arrow specification image and extract all technical data in JSON format.

    Look for:
    1. SPINE values (e.g., 250, 300, 350, 400, 500, 600, 700, 800, 900, 1000)
    2. GPI weights (grains per inch) - usually decimal numbers like 6.2, 7.8, 9.1
    3. DIAMETER measurements (outer diameter) - usually in inches like .244", .294"
    4. LENGTH options if shown
    5. Arrow model name
    6. Any other specifications like straightness tolerance

    Common formats in Carbon Express charts:
    - Tables with columns: Spine, GPI, O.D., Length
    - Sometimes called "Weight" instead of GPI
    - Diameters may be in format like .244" or 0.244"
    - Spine values are usually 3-4 digit numbers

    Return ONLY valid JSON in this exact format:
    {
        "model_name": "Arrow Model Name",
        "spine_specifications": [
            {
                "spine": 350,
                "gpi_weight": 9.07,
                "outer_diameter": 0.244,
                "inner_diameter": null,
                "length_options": [30.0, 31.0]
            }
        ],
        "material": "Material if shown",
        "description": "Any additional info from image"
    }

    If no clear specification data is found, return: {"error": "No specifications found in image"}
    """
    
    # Try different model names for vision
    models_to_try = [
        "deepseek-vl",
        "deepseek-vl-chat", 
        "deepseek-vision",
        "deepseek-multimodal",
        "deepseek-chat"  # Fallback to regular chat model
    ]
    
    for model_name in models_to_try:
        print(f"🔍 Trying model: {model_name}")
        
        data = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            print(f"📊 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content'].strip()
                    print(f"✅ Success with model: {model_name}")
                    print(f"📝 Raw response: {content[:500]}...")
                    
                    # Clean up response
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.startswith('```'):
                        content = content[3:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    # Parse JSON
                    try:
                        parsed_data = json.loads(content)
                        return parsed_data
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parse error with {model_name}: {e}")
                        print(f"Content: {content}")
                        continue  # Try next model
                else:
                    print(f"❌ No choices in response for {model_name}")
                    continue
            else:
                print(f"❌ API Error for {model_name}: {response.text}")
                continue  # Try next model
                
        except Exception as e:
            print(f"💥 API call error for {model_name}: {e}")
            continue  # Try next model
    
    print("❌ All models failed")
    return None

def main():
    """Test DeepSeek vision OCR on Carbon Express images"""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
    print("🚀 Testing DeepSeek Vision OCR for Carbon Express")
    print("=" * 60)
    
    # Test images from our debug analysis
    test_images = [
        {
            "name": "Maxima Sable RZ Main",
            "url": "https://cdn-ilchokf.nitrocdn.com/nqkqluPOLqauqjblimVNksnJtfbWDRlW/assets/images/optimized/rev-c783676/www.feradyne.com/wp-content/uploads/2022/01/Maxima-Sable-RZ.png"
        },
        {
            "name": "Maxima Triad (from user example)",
            "url": "https://cdn-ilchokf.nitrocdn.com/nqkqluPOLqauqjblimVNksnJtfbWDRlW/assets/images/optimized/rev-c783676/www.feradyne.com/wp-content/uploads/2019/12/Maxima-Triad.png"
        }
    ]
    
    for i, image_info in enumerate(test_images, 1):
        print(f"\n🖼️  Test {i}: {image_info['name']}")
        print(f"URL: {image_info['url']}")
        print("-" * 50)
        
        # Download image
        filename = f"test_carbon_express_{i}.png"
        image_path = download_image(image_info['url'], filename)
        
        if not image_path:
            continue
        
        # Analyze with DeepSeek vision
        result = analyze_image_with_deepseek(image_path, api_key)
        
        if result:
            print("✅ OCR Analysis Result:")
            print(json.dumps(result, indent=2))
            
            # Check if we got useful specification data
            if 'spine_specifications' in result and result['spine_specifications']:
                specs = result['spine_specifications']
                print(f"\n🎯 Found {len(specs)} spine specifications:")
                for spec in specs:
                    spine = spec.get('spine', 'N/A')
                    gpi = spec.get('gpi_weight', 'N/A')
                    od = spec.get('outer_diameter', 'N/A')
                    print(f"   Spine {spine}: GPI {gpi}, OD {od}")
            elif 'error' in result:
                print(f"⚠️  {result['error']}")
            else:
                print("⚠️  No spine specifications extracted")
        else:
            print("❌ OCR analysis failed")
        
        # Clean up
        try:
            os.remove(image_path)
            print(f"🗑️  Cleaned up {filename}")
        except:
            pass
        
        print()
    
    print("=" * 60)
    print("🏁 DeepSeek Vision OCR Test Complete")

if __name__ == "__main__":
    main()