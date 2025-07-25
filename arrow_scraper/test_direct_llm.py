#!/usr/bin/env python3
"""
Test LLM directly with the actual scraped content
"""

import os
import json
from dotenv import load_dotenv
import requests

def test_direct_llm():
    """Test DeepSeek API directly"""
    print("🤖 Testing DeepSeek API Directly")
    print("=" * 35)
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ API key not found")
        return
    
    # Sample content from the Easton page
    sample_content = """
    Size  | Shaft Weight  
    (GPI) | Spine @ 28″ Span  
    (deflection in inches) | Stock Length  
    (inches) | Deep 6 Field Point  
    100 Grains (optional) | 8-32 Field Point  
    (inches) | O.D.  
    (inches) | 4MM Halfout  
    (size) | 4mm Nock
    250 | 9.8 | 0.638 | *33.63 | ✓ | 100gr | .244 | L | Red
    300 | 9.8 | 0.522 | *33.63 | ✓ | 100gr | .244 | L | Red  
    340 | 9.8 | 0.453 | *33.63 | ✓ | 100gr | .244 | L | Red
    400 | 9.8 | 0.386 | *33.63 | ✓ | 100gr | .244 | L | Red
    """
    
    # Simple prompt
    prompt = """
    Extract arrow specifications from this table data.
    Look for spine values (250, 300, 340, 400), GPI weights, and diameters.
    Return as JSON with this structure:
    {
        "arrows": [
            {
                "model_name": "4MM Axis Long Range",
                "spine_specifications": [
                    {"spine": 250, "gpi_weight": 9.8, "outer_diameter": 0.244},
                    {"spine": 300, "gpi_weight": 9.8, "outer_diameter": 0.244}
                ]
            }
        ]
    }
    """
    
    # API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that extracts structured data from text."},
            {"role": "user", "content": f"{prompt}\n\nData to extract:\n{sample_content}"}
        ],
        "max_tokens": 1000,
        "temperature": 0.1
    }
    
    try:
        print("📡 Making API call...")
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"📝 Response:\n{content}")
                
                # Try to parse as JSON
                try:
                    json_data = json.loads(content)
                    print("🎉 Successfully parsed JSON!")
                    print(f"📊 Extracted: {json.dumps(json_data, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"⚠️  Failed to parse JSON: {e}")
            else:
                print("❌ No choices in response")
                print(f"Response: {result}")
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_direct_llm()