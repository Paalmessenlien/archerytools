#!/usr/bin/env python3
"""
Fast demonstration of comprehensive extraction
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent))

from run_comprehensive_extraction import DirectLLMExtractor
from crawl4ai import AsyncWebCrawler

async def run_fast_demo():
    """Run fast demo extraction on diverse URLs"""
    print("🚀 Fast Demo: Comprehensive Arrow Extraction")
    print("=" * 50)
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    # Select diverse URLs from different manufacturers
    demo_urls = [
        # Easton - known to work well
        ("https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/", "Easton Archery"),
        ("https://eastonarchery.com/arrows_/carbon-legacy/", "Easton Archery"),
        ("https://eastonarchery.com/arrows_/x10/", "Easton Archery"),
        
        # Gold Tip - test different manufacturer
        ("https://www.goldtip.com/hunting-arrows/hunter-series/hunter-hunting-arrows/P01268.html", "Gold Tip"),
        ("https://www.goldtip.com/hunting-arrows/kinetic-series/kinetic-hunting-arrows/P01275.html", "Gold Tip"),
        
        # Victory Archery - another manufacturer
        ("https://victoryarchery.com/arrows-hunting/vap-ss/", "Victory Archery"),
        
        # Skylon - European manufacturer
        ("https://www.skylonarchery.com/arrows/id-3-2/performa", "Skylon Archery")
    ]
    
    print(f"🎯 Testing {len(demo_urls)} URLs across multiple manufacturers")
    
    extractor = DirectLLMExtractor(api_key)
    all_arrows = []
    failed_urls = []
    manufacturer_stats = {}
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        for i, (url, manufacturer) in enumerate(demo_urls, 1):
            print(f"\n🔗 [{i}/{len(demo_urls)}] {manufacturer}: {url.split('/')[-2] if '/' in url else url.split('/')[-1]}")
            
            # Initialize manufacturer stats
            if manufacturer not in manufacturer_stats:
                manufacturer_stats[manufacturer] = {"processed": 0, "successful": 0, "arrows": 0}
            
            manufacturer_stats[manufacturer]["processed"] += 1
            
            try:
                # Crawl the page
                result = await crawler.arun(url=url, bypass_cache=True)
                
                if not result.success:
                    print(f"❌ Failed to crawl")
                    failed_urls.append((url, manufacturer, "Crawl failed"))
                    continue
                
                print(f"✓ Crawled ({len(result.markdown)} chars)", end="")
                
                # Extract arrow data
                arrows = extractor.extract_arrow_data(result.markdown, url)
                
                if arrows:
                    manufacturer_stats[manufacturer]["successful"] += 1
                    manufacturer_stats[manufacturer]["arrows"] += len(arrows)
                    total_spine_specs = sum(len(arrow.spine_specifications) for arrow in arrows)
                    print(f" → 🎯 {len(arrows)} arrows, {total_spine_specs} spine specs")
                    
                    for arrow in arrows:
                        print(f"      📋 {arrow.model_name}: {len(arrow.spine_specifications)} spine options")
                        # Show sample spine data
                        if arrow.spine_specifications:
                            sample_spec = arrow.spine_specifications[0]
                            print(f"         Sample: Spine {sample_spec.spine}, {sample_spec.gpi_weight} GPI, {sample_spec.outer_diameter}\" OD")
                    
                    all_arrows.extend(arrows)
                else:
                    print(f" → ❌ No data")
                    failed_urls.append((url, manufacturer, "No data extracted"))
                
                # Rate limiting
                await asyncio.sleep(1)  # Faster for demo
                
            except Exception as e:
                print(f" → 💥 Error: {str(e)[:50]}...")
                failed_urls.append((url, manufacturer, str(e)))
                continue
    
    # Save comprehensive demo results
    if all_arrows:
        output_data = {
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_type": "fast_demo_comprehensive",
            "total_arrows": len(all_arrows),
            "total_spine_specs": sum(len(arrow.spine_specifications) for arrow in all_arrows),
            "urls_processed": len(demo_urls),
            "successful_extractions": len(demo_urls) - len(failed_urls),
            "success_rate": ((len(demo_urls) - len(failed_urls)) / len(demo_urls) * 100),
            "manufacturer_stats": manufacturer_stats,
            "arrows": [arrow.model_dump(mode='json') for arrow in all_arrows],
            "failed_urls": [{"url": url, "manufacturer": mfr, "reason": reason} for url, mfr, reason in failed_urls]
        }
        
        output_file = Path("data/processed/fast_demo_comprehensive_results.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"📊 COMPREHENSIVE DEMO RESULTS")
        print(f"{'='*60}")
        print(f"💾 Results saved to {output_file}")
        
        print(f"\n🎯 EXTRACTION SUMMARY:")
        print(f"   Total arrows extracted: {len(all_arrows)}")
        print(f"   Total spine specifications: {sum(len(arrow.spine_specifications) for arrow in all_arrows)}")
        print(f"   URLs processed: {len(demo_urls)}")
        print(f"   Successful extractions: {len(demo_urls) - len(failed_urls)}")
        print(f"   Success rate: {((len(demo_urls) - len(failed_urls)) / len(demo_urls) * 100):.1f}%")
        
        print(f"\n🏭 MANUFACTURER BREAKDOWN:")
        for manufacturer, stats in manufacturer_stats.items():
            success_rate = (stats["successful"] / stats["processed"] * 100) if stats["processed"] > 0 else 0
            print(f"   {manufacturer}:")
            print(f"     URLs processed: {stats['processed']}")
            print(f"     Successful: {stats['successful']}")
            print(f"     Arrows found: {stats['arrows']}")
            print(f"     Success rate: {success_rate:.1f}%")
        
        # Show unique models
        unique_models = set(arrow.model_name for arrow in all_arrows)
        print(f"\n📋 UNIQUE ARROW MODELS ({len(unique_models)}):")
        for model in sorted(unique_models):
            model_arrows = [arrow for arrow in all_arrows if arrow.model_name == model]
            total_spines = sum(len(arrow.spine_specifications) for arrow in model_arrows)
            print(f"   • {model}: {total_spines} spine specifications")
        
        # Spine distribution
        spine_counts = {}
        for arrow in all_arrows:
            count = len(arrow.spine_specifications)
            spine_counts[count] = spine_counts.get(count, 0) + 1
        
        print(f"\n🎯 SPINE SPECIFICATION DISTRIBUTION:")
        for count, freq in sorted(spine_counts.items()):
            print(f"     {count} spine options: {freq} arrows")
        
        return len(all_arrows)
    else:
        print("\n❌ No arrows extracted in demo")
        return 0

def main():
    result = asyncio.run(run_fast_demo())
    print(f"\n✅ Demo complete: {result} arrows extracted with spine-specific data!")

if __name__ == "__main__":
    main()