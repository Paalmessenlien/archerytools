#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup

def debug_page_content():
    """Debug the page content to see what we're actually getting"""
    
    url = "https://eastonarchery.com/arrows_/x10-parallel-pro/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, timeout=30, headers=headers)
    print(f"HTTP Status: {response.status_code}")
    print(f"Content Length: {len(response.text)}")
    
    # Save the full HTML content to examine
    with open('/tmp/x10_page.html', 'w') as f:
        f.write(response.text)
    print("Saved full HTML to /tmp/x10_page.html")
    
    # Parse and look for specific patterns
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for script tags that might contain data
    scripts = soup.find_all('script')
    print(f"\nFound {len(scripts)} script tags")
    
    # Look for JSON data in scripts
    for i, script in enumerate(scripts):
        if script.string:
            script_content = script.string
            if 'spine' in script_content.lower() or 'gpi' in script_content.lower():
                print(f"\nScript {i} contains spine/gpi data:")
                print(script_content[:500])
    
    # Look for meta tags
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        if meta.get('name') == 'description' or meta.get('property') == 'og:description':
            print(f"\nDescription: {meta.get('content', '')}")
    
    # Look for any divs with data attributes
    divs_with_data = soup.find_all('div', attrs=lambda x: x and any(key.startswith('data-') for key in x.keys()))
    print(f"\nFound {len(divs_with_data)} divs with data attributes")
    
    # Look for the page title and any product info
    title = soup.find('title')
    if title:
        print(f"\nPage title: {title.string}")
    
    # Look for any mentions of specifications in the text content
    page_text = soup.get_text()
    
    # Search for common archery terms
    archery_terms = ['spine', 'gpi', 'grain', 'diameter', 'carbon', 'arrow', 'shaft', 'target', 'hunting']
    
    print(f"\nSearching for archery terms in page text:")
    for term in archery_terms:
        count = page_text.lower().count(term)
        if count > 0:
            print(f"  {term}: {count} occurrences")
    
    # Look for numeric patterns that might be specifications
    numbers = re.findall(r'\b\d+\.?\d*\b', page_text)
    print(f"\nFound {len(numbers)} numbers in text: {numbers[:20]}")  # Show first 20
    
    # Look for specific product model mentions
    if 'x10' in page_text.lower():
        print(f"\nX10 mentioned in text")
        # Find context around X10 mentions
        x10_contexts = []
        for match in re.finditer(r'.{0,50}x10.{0,50}', page_text, re.IGNORECASE):
            x10_contexts.append(match.group())
        
        print(f"X10 contexts:")
        for context in x10_contexts[:5]:  # Show first 5
            print(f"  {context.strip()}")

if __name__ == "__main__":
    debug_page_content()