#!/usr/bin/env python3
"""
Simple test script to debug TopHat Archery scraping
"""

import asyncio
import sys
import os
from pathlib import Path

# Add crawl4ai to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'crawl4ai'))

from crawl4ai import AsyncWebCrawler

async def test_simple_fetch():
    """Test simple HTML fetching without LLM extraction"""
    test_url = "https://tophatarchery.com/search-by-shaft/brands/aurel/7933/aurel-agil-300"
    
    print(f"Testing simple fetch for: {test_url}")
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=test_url)
        
        if result.success:
            print(f"✅ Successfully fetched content")
            print(f"📊 Content length: {len(result.html)} characters")
            print(f"📋 Markdown length: {len(result.markdown)} characters")
            
            # Save HTML for inspection
            with open('/tmp/tophat_test.html', 'w', encoding='utf-8') as f:
                f.write(result.html)
            print(f"💾 HTML saved to /tmp/tophat_test.html")
            
            # Look for key elements
            if '<h1 class="product--title">' in result.html:
                print("✅ Found product title element")
            else:
                print("❌ Product title element not found")
                
            if 'product--description' in result.html:
                print("✅ Found product description area")
            else:
                print("❌ Product description area not found")
                
            # Extract title manually
            import re
            title_match = re.search(r'<h1 class="product--title"[^>]*>(.*?)</h1>', result.html, re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                print(f"📝 Extracted title: {title}")
            
            # Extract any spine info
            spine_match = re.search(r'(\d{3,4})', test_url)
            if spine_match:
                spine = spine_match.group(1)
                print(f"🎯 Extracted spine from URL: {spine}")
                
        else:
            print(f"❌ Failed to fetch content: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(test_simple_fetch())