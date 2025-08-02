#!/usr/bin/env python3
"""
Test image URL extraction from TopHat Archery pages
"""

import asyncio
import sys
import os
from pathlib import Path

# Add crawl4ai to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'crawl4ai'))

from crawl4ai import AsyncWebCrawler
from tophat_archery_scraper import TopHatManualExtractor

async def test_image_extraction():
    """Test image URL extraction"""
    
    test_urls = [
        "https://tophatarchery.com/search-by-shaft/brands/aurel/7933/aurel-agil-300",
        "https://tophatarchery.com/komponentensuche-nach-schaft/marke/ok-archery/absolute/8387/ok-archery-absolute.15-350"
    ]
    
    extractor = TopHatManualExtractor()
    
    print(f"🖼️  Testing Image URL Extraction")
    print("=" * 50)
    
    async with AsyncWebCrawler() as crawler:
        for i, url in enumerate(test_urls, 1):
            print(f"\n📝 Test {i}: {url}")
            
            try:
                result = await crawler.arun(url=url)
                
                if result.success:
                    print(f"✅ Page fetched successfully")
                    
                    # Extract all product data including image
                    product_data = extractor.extract_product_data(result.html, url)
                    
                    if product_data:
                        print(f"📋 Product: {product_data.get('title', 'Unknown')}")
                        print(f"🏭 Manufacturer: {product_data.get('manufacturer', 'Unknown')}")
                        print(f"🎯 Spine: {product_data.get('spine', 'Unknown')}")
                        
                        if 'image_url' in product_data and product_data['image_url']:
                            print(f"🖼️  Image URL: {product_data['image_url']}")
                            print("✅ Image extraction successful!")
                        else:
                            print("❌ No image URL found")
                            
                        # Also test the direct image extraction method
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(result.html, 'html.parser')
                        direct_image = extractor._extract_image_url(soup)
                        if direct_image:
                            print(f"🔍 Direct extraction: {direct_image}")
                        
                    else:
                        print("❌ Product data extraction failed")
                        
                else:
                    print(f"❌ Failed to fetch page: {result.error_message}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_image_extraction())