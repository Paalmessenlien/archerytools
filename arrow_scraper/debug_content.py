#!/usr/bin/env python3
"""
Debug content extraction to understand what we're getting from manufacturer pages
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler

async def debug_manufacturer_content():
    """Debug what content we're getting from manufacturer pages"""
    
    urls_to_test = [
        "https://eastonarchery.com/huntingarrows/",
        "https://eastonarchery.com/indoor/"
    ]
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        for url in urls_to_test:
            print(f"\n{'='*60}")
            print(f"DEBUGGING: {url}")
            print(f"{'='*60}")
            
            result = await crawler.arun(
                url=url,
                bypass_cache=True
            )
            
            if result.success:
                content = result.markdown or result.html or ""
                
                print(f"Content length: {len(content)}")
                print(f"Status: {result.status_code}")
                
                # Show first 1000 characters
                print(f"\nFirst 1000 characters:")
                print("-" * 40)
                print(content[:1000])
                print("-" * 40)
                
                # Check for arrow-related keywords
                content_lower = content.lower()
                keywords = {
                    'arrow': content_lower.count('arrow'),
                    'shaft': content_lower.count('shaft'), 
                    'spine': content_lower.count('spine'),
                    'diameter': content_lower.count('diameter'),
                    'gpi': content_lower.count('gpi'),
                    'grains': content_lower.count('grains'),
                    'carbon': content_lower.count('carbon'),
                    'link': content_lower.count('href')
                }
                
                print(f"\nKeyword analysis:")
                for keyword, count in keywords.items():
                    print(f"  {keyword}: {count}")
                
                # Look for product links
                import re
                links = re.findall(r'href="([^"]*)"', content.lower())
                arrow_links = [link for link in links if any(term in link for term in ['arrow', 'shaft', 'product'])]
                
                print(f"\nPotential arrow product links found: {len(arrow_links)}")
                for i, link in enumerate(arrow_links[:5], 1):
                    print(f"  {i}. {link}")
                
            else:
                print(f"Failed to fetch: {result.error_message}")
            
            print(f"\n{'='*60}")

if __name__ == "__main__":
    asyncio.run(debug_manufacturer_content())