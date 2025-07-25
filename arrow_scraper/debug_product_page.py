#!/usr/bin/env python3
"""
Debug specific product pages to see what content we're getting
"""

import asyncio
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from deepseek_extractor import DeepSeekArrowExtractor

async def debug_specific_product():
    """Debug a specific arrow product page"""
    
    # Test with a known Easton arrow product page
    product_urls = [
        "https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/",
        "https://eastonarchery.com/arrows_/x27/",
        "https://eastonarchery.com/arrows_/carbon-legacy/"
    ]
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        for url in product_urls:
            print(f"\n{'='*80}")
            print(f"DEBUGGING PRODUCT PAGE: {url}")
            print(f"{'='*80}")
            
            result = await crawler.arun(url=url, bypass_cache=True)
            
            if result.success:
                content = result.markdown or result.html or ""
                
                print(f"Content length: {len(content)}")
                print(f"Status: {result.status_code}")
                
                # Show first 2000 characters to see the structure
                print(f"\nFirst 2000 characters of content:")
                print("-" * 50)
                print(content[:2000])
                print("-" * 50)
                
                # Check for technical specification keywords
                content_lower = content.lower()
                tech_keywords = {
                    'spine': content_lower.count('spine'),
                    'diameter': content_lower.count('diameter'),
                    'gpi': content_lower.count('gpi'),
                    'grains per inch': content_lower.count('grains per inch'),
                    'weight': content_lower.count('weight'),
                    'straightness': content_lower.count('straightness'),
                    'tolerance': content_lower.count('tolerance'),
                    'specification': content_lower.count('specification'),
                    'spec': content_lower.count('spec'),
                    'carbon': content_lower.count('carbon'),
                    'material': content_lower.count('material'),
                    '0.': content_lower.count('0.'),  # Decimal measurements
                    'inch': content_lower.count('inch'),
                    'mm': content_lower.count('mm')
                }
                
                print(f"\nTechnical keyword analysis:")
                for keyword, count in tech_keywords.items():
                    if count > 0:
                        print(f"  {keyword}: {count}")
                
                # Look for numeric patterns that might be spine values
                import re
                spine_pattern = r'\b([234567]\d{2})\b'  # 300-799 range
                diameter_pattern = r'\b0\.\d{3}\b'  # 0.xxx format
                gpi_pattern = r'\b\d+\.\d+\s*gpi\b'  # X.X gpi format
                
                spine_matches = re.findall(spine_pattern, content_lower)
                diameter_matches = re.findall(diameter_pattern, content_lower)
                gpi_matches = re.findall(gpi_pattern, content_lower)
                
                print(f"\nPattern matches:")
                print(f"  Potential spines: {spine_matches}")
                print(f"  Potential diameters: {diameter_matches}")
                print(f"  Potential GPI values: {gpi_matches}")
                
                # Try DeepSeek extraction on this content
                print(f"\nTesting DeepSeek extraction...")
                try:
                    api_key = os.getenv("DEEPSEEK_API_KEY")
                    if api_key:
                        extractor = DeepSeekArrowExtractor(api_key)
                        arrows = extractor.extract_arrows_from_content(
                            content=content,
                            source_url=url,
                            manufacturer="Easton"
                        )
                        print(f"  DeepSeek found: {len(arrows)} arrows")
                        if arrows:
                            for arrow in arrows:
                                print(f"    - {arrow.model_name}")
                    else:
                        print("  No API key found for DeepSeek test")
                except Exception as e:
                    print(f"  DeepSeek extraction error: {e}")
                
            else:
                print(f"Failed to fetch: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(debug_specific_product())