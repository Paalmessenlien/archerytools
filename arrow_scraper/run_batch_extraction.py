#!/usr/bin/env python3
"""
Run extraction in batches with progress saving
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import requests
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from models import ArrowSpecification, SpineSpecification
from run_comprehensive_extraction import DirectLLMExtractor

async def run_batch_extraction(batch_size=10, start_index=0):
    """Run extraction in smaller batches"""
    print(f"🚀 Running Batch Arrow Extraction (batch_size={batch_size}, start_index={start_index})")
    print("=" * 60)
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    # Load all manufacturer URLs
    from scrape_all_manufacturers import ComprehensiveArrowScraper
    temp_scraper = ComprehensiveArrowScraper(api_key)
    all_urls = []
    
    for manufacturer_name, manufacturer_data in temp_scraper.manufacturers.items():
        manufacturer_urls = manufacturer_data.get("product_urls", [])
        all_urls.extend([(url, manufacturer_name) for url in manufacturer_urls])
    
    print(f"📊 Total URLs available: {len(all_urls)}")
    
    # Select batch
    end_index = min(start_index + batch_size, len(all_urls))
    urls_to_process = all_urls[start_index:end_index]
    
    print(f"📦 Processing URLs {start_index} to {end_index-1} ({len(urls_to_process)} URLs)")
    
    extractor = DirectLLMExtractor(api_key)
    all_arrows = []
    failed_urls = []
    
    async with AsyncWebCrawler(verbose=False) as crawler:  # Reduced verbosity
        for i, (url, manufacturer_name) in enumerate(urls_to_process, 1):
            print(f"\n🔗 [{start_index + i}/{end_index}] {manufacturer_name}: {url.split('/')[-2] if '/' in url else url}")
            
            try:
                # Crawl the page
                result = await crawler.arun(url=url, bypass_cache=True)
                
                if not result.success:
                    print(f"❌ Failed to crawl")
                    failed_urls.append((url, manufacturer_name, "Crawl failed"))
                    continue
                
                print(f"✓ Crawled ({len(result.markdown)} chars)", end="")
                
                # Extract arrow data
                arrows = extractor.extract_arrow_data(result.markdown, url)
                
                if arrows:
                    print(f" → 🎯 {len(arrows)} arrows")
                    for arrow in arrows:
                        print(f"      {arrow.model_name}: {len(arrow.spine_specifications)} spine options")
                    all_arrows.extend(arrows)
                else:
                    print(f" → ❌ No data")
                    failed_urls.append((url, manufacturer_name, "No data extracted"))
                
                # Short rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f" → 💥 Error: {str(e)[:50]}...")
                failed_urls.append((url, manufacturer_name, str(e)))
                continue
    
    # Save batch results
    if all_arrows or failed_urls:
        batch_data = {
            "batch_info": {
                "start_index": start_index,
                "end_index": end_index,
                "batch_size": len(urls_to_process),
                "timestamp": datetime.now().isoformat()
            },
            "arrows": [arrow.model_dump(mode='json') for arrow in all_arrows],
            "failed_urls": [{"url": url, "manufacturer": mfr, "reason": reason} for url, mfr, reason in failed_urls],
            "stats": {
                "total_arrows": len(all_arrows),
                "successful_urls": len(urls_to_process) - len(failed_urls),
                "failed_urls": len(failed_urls)
            }
        }
        
        batch_file = Path(f"data/processed/batch_{start_index:03d}_{end_index:03d}.json")
        batch_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(batch_file, 'w') as f:
            json.dump(batch_data, f, indent=2)
        
        print(f"\n💾 Batch results saved to {batch_file}")
        print(f"📊 Batch Summary:")
        print(f"   Arrows extracted: {len(all_arrows)}")
        print(f"   Successful URLs: {len(urls_to_process) - len(failed_urls)}/{len(urls_to_process)}")
        print(f"   Success rate: {((len(urls_to_process) - len(failed_urls)) / len(urls_to_process) * 100):.1f}%")
        
        return len(all_arrows)
    else:
        print("\n❌ No results in this batch")
        return 0

def main():
    """Run batch extraction with command line arguments"""
    import sys
    
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    start_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    result = asyncio.run(run_batch_extraction(batch_size, start_index))
    print(f"\n✅ Batch complete: {result} arrows extracted")

if __name__ == "__main__":
    main()