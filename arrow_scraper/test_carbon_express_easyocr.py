#!/usr/bin/env python3
"""
Test EasyOCR on real Carbon Express URL
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from easyocr_carbon_express_extractor import EasyOCRCarbonExpressExtractor

async def test_carbon_express_extraction():
    """Test EasyOCR extraction on Carbon Express page"""
    
    url = "https://www.feradyne.com/product/maxima-sable-rz/"
    
    print("🚀 Testing EasyOCR on Carbon Express")
    print(f"URL: {url}")
    print("=" * 60)
    
    # Initialize extractor
    extractor = EasyOCRCarbonExpressExtractor()
    
    if not extractor.reader:
        print("❌ EasyOCR not available")
        return
    
    # Crawl the page
    async with AsyncWebCrawler(verbose=True) as crawler:
        print("🔍 Crawling Carbon Express page...")
        
        result = await crawler.arun(url=url, bypass_cache=True)
        
        if not result.success:
            print(f"❌ Failed to crawl: {result.error_message}")
            return
        
        print(f"✅ Crawled successfully")
        print(f"HTML: {len(result.html):,} chars")
        print(f"Markdown: {len(result.markdown):,} chars")
        
        # Extract using EasyOCR
        print("\n🤖 Running EasyOCR extraction...")
        arrows = extractor.extract_carbon_express_data(
            result.html, 
            result.markdown, 
            url
        )
        
        if arrows:
            print(f"\n✅ SUCCESS: Extracted {len(arrows)} arrows")
            
            for arrow in arrows:
                print(f"\n📋 {arrow.model_name}")
                print(f"   Manufacturer: {arrow.manufacturer}")
                print(f"   Specifications: {len(arrow.spine_specifications)}")
                
                for spec in arrow.spine_specifications:
                    print(f"      Spine {spec.spine}: GPI {spec.gpi_weight}, OD {spec.outer_diameter}")
                
                if arrow.straightness_tolerance:
                    print(f"   Straightness: {arrow.straightness_tolerance}")
                
                print(f"   Source: {arrow.source_url}")
                print(f"   Image: {arrow.primary_image_url}")
        else:
            print("❌ No arrows extracted")

if __name__ == "__main__":
    asyncio.run(test_carbon_express_extraction())