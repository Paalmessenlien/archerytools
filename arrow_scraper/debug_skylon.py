#!/usr/bin/env python3
"""
Debug Skylon content extraction
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler

async def debug_skylon():
    """Debug what content we're getting from Skylon"""
    print("🔍 Debugging Skylon Content")
    print("=" * 40)
    
    url = "https://www.skylonarchery.com/arrows/id-3-2/performa"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url, bypass_cache=True)
        
        if result.success:
            print(f"✅ Successfully crawled: {len(result.markdown)} chars")
            print(f"\n📄 Raw content:")
            print("=" * 50)
            print(result.markdown)
            print("=" * 50)
            
            # Check for specific Skylon content
            content_lower = result.markdown.lower()
            
            print(f"\n🔍 Content Analysis:")
            print(f"Contains 'spine': {'spine' in content_lower}")
            print(f"Contains 'gpi': {'gpi' in content_lower}")
            print(f"Contains 'grain': {'grain' in content_lower}")
            print(f"Contains 'diameter': {'diameter' in content_lower}")
            print(f"Contains 'article': {'article' in content_lower}")
            print(f"Contains 'table': {'table' in content_lower}")
            
            # Look for specific Skylon patterns
            if "spine" in content_lower:
                spine_pos = content_lower.find("spine")
                print(f"\n📍 'spine' found at position {spine_pos}")
                print(f"Context: {result.markdown[max(0, spine_pos-100):spine_pos+200]}")
                
            if "gpi" in content_lower or "grain" in content_lower:
                gpi_pos = content_lower.find("gpi")
                grain_pos = content_lower.find("grain")
                pos = max(gpi_pos, grain_pos)
                if pos > -1:
                    print(f"\n📍 Weight info found at position {pos}")
                    print(f"Context: {result.markdown[max(0, pos-100):pos+200]}")
        else:
            print(f"❌ Failed to crawl: {result.error_message}")

def main():
    load_dotenv()
    asyncio.run(debug_skylon())

if __name__ == "__main__":
    main()