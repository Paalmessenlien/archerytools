#!/usr/bin/env python3

import requests
import json
import sys

def test_url_scraping():
    """Test the URL scraping endpoint"""
    
    # API endpoint
    url = "http://localhost:5000/api/admin/scrape-url"
    
    # Test data
    payload = {
        "url": "https://eastonarchery.com/arrows_/x10-parallel-pro/",
        "manufacturer": "Easton"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing URL scraping endpoint...")
    print(f"URL: {payload['url']}")
    print(f"Manufacturer: {payload['manufacturer']}")
    print()
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nSuccess! Response data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"\nError response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_url_scraping()