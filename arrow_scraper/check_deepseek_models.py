#!/usr/bin/env python3
"""
Check what models DeepSeek API actually supports
"""

import os
import requests
from dotenv import load_dotenv

def check_deepseek_models():
    """Check available DeepSeek models"""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Try to get models list
        response = requests.get(
            "https://api.deepseek.com/v1/models",
            headers=headers,
            timeout=30
        )
        
        print(f"Models API Status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print("Available models:")
            for model in models.get('data', []):
                print(f"  - {model.get('id', 'Unknown')}")
        else:
            print(f"Models API Error: {response.text}")
    
    except Exception as e:
        print(f"Error checking models: {e}")
    
    # Test basic chat completion
    print("\nTesting basic chat completion...")
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello, can you analyze images?"}
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"Chat API Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"Response: {content}")
        else:
            print(f"Chat API Error: {response.text}")
    
    except Exception as e:
        print(f"Error testing chat: {e}")

if __name__ == "__main__":
    check_deepseek_models()