#!/usr/bin/env python3
"""
Quick test to demonstrate the scaling works
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent))

from run_comprehensive_extraction import DirectLLMExtractor
from crawl4ai import AsyncWebCrawler

async def quick_test():
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    # Test just the URLs we know work
    test_urls = [
        ("https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/", "Easton"),
        ("https://eastonarchery.com/arrows_/carbon-legacy/", "Easton"),
        ("https://eastonarchery.com/arrows_/x10/", "Easton")
    ]
    
    extractor = DirectLLMExtractor(api_key)
    all_arrows = []
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        for url, manufacturer in test_urls:
            print(f"🔗 Testing {url.split('/')[-2]}")
            
            try:
                result = await crawler.arun(url=url, bypass_cache=True)
                if result.success:
                    arrows = extractor.extract_arrow_data(result.markdown, url)
                    if arrows:
                        print(f"✅ {len(arrows)} arrows, {sum(len(arrow.spine_specifications) for arrow in arrows)} total spine specs")
                        all_arrows.extend(arrows)
                    else:
                        print("❌ No arrows")
            except Exception as e:
                print(f"💥 Error: {e}")
            
            await asyncio.sleep(1)
    
    # Save results
    if all_arrows:
        output_data = {
            "total_arrows": len(all_arrows),
            "total_spine_specs": sum(len(arrow.spine_specifications) for arrow in all_arrows),
            "arrows": [arrow.model_dump(mode='json') for arrow in all_arrows]
        }
        
        output_file = Path("data/processed/quick_test_results.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n🎉 SUCCESS! Extracted {len(all_arrows)} arrows with {sum(len(arrow.spine_specifications) for arrow in all_arrows)} spine specifications")
        print(f"💾 Results saved to {output_file}")
        
        # Show sample
        for arrow in all_arrows[:1]:
            print(f"\nSample: {arrow.model_name}")
            for spec in arrow.spine_specifications[:3]:
                print(f"  Spine {spec.spine}: {spec.gpi_weight} GPI, {spec.outer_diameter}\" OD")

def main():
    asyncio.run(quick_test())

if __name__ == "__main__":
    main()