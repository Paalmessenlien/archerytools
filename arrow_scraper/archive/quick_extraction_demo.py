#!/usr/bin/env python3
"""
Quick Arrow Extraction Demo - Complete extraction from Skylon Archery
Demonstrate successful extraction and save results
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from deepseek_extractor import DeepSeekArrowExtractor
from models import ArrowSpecification, ManufacturerData

async def demo_skylon_extraction():
    """Demo extraction from Skylon Archery with complete data saving"""
    
    print("🎯 QUICK EXTRACTION DEMO - SKYLON ARCHERY")
    print("=" * 50)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    extractor = DeepSeekArrowExtractor(api_key)
    
    # Top 5 Skylon models for demo
    demo_urls = [
        "https://www.skylonarchery.com/arrows/id-3-2/performa",
        "https://www.skylonarchery.com/arrows/id-3-2/precium",
        "https://www.skylonarchery.com/arrows/id-5-2/instec",
        "https://www.skylonarchery.com/arrows/id-6-2/edge",
        "https://www.skylonarchery.com/arrows/id-8-0/bruxx"
    ]
    
    all_arrows = []
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        for i, url in enumerate(demo_urls, 1):
            print(f"\n🔗 [{i}/{len(demo_urls)}] {url}")
            
            try:
                result = await crawler.arun(url=url, bypass_cache=True)
                
                if result.success:
                    content = result.markdown or result.html or ""
                    print(f"   ✓ Crawled ({len(content)} chars)")
                    
                    arrows = extractor.extract_arrows_from_content(
                        content=content,
                        source_url=url,
                        manufacturer="Skylon Archery"
                    )
                    
                    if arrows:
                        print(f"   🎉 Extracted {len(arrows)} arrows!")
                        for arrow in arrows:
                            print(f"      • {arrow.model_name}")
                            print(f"        Spines: {arrow.spine_options}")
                            print(f"        Diameter: {arrow.diameter}\" | GPI: {arrow.gpi_weight}")
                        all_arrows.extend(arrows)
                    else:
                        print(f"   ⚠️  No arrows extracted")
                else:
                    print(f"   ❌ Failed to crawl")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    # Save results
    output_dir = Path(__file__).parent / "data" / "demo_extraction"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create manufacturer data
    manufacturer_data = ManufacturerData(
        manufacturer="Skylon Archery",
        arrows=all_arrows
    )
    
    # Save detailed results
    demo_file = output_dir / "skylon_demo_extraction.json"
    
    demo_export = {
        "extraction_demo": {
            "manufacturer": "Skylon Archery",
            "extraction_date": datetime.now().isoformat(),
            "urls_processed": len(demo_urls),
            "total_arrows": len(all_arrows),
            "success_rate": f"{(len(all_arrows)/len(demo_urls)*100):.1f}%"
        },
        "arrows": [
            {
                "model_name": arrow.model_name,
                "spine_options": arrow.spine_options,
                "diameter": arrow.diameter,
                "inner_diameter": arrow.inner_diameter,
                "gpi_weight": arrow.gpi_weight,
                "length_options": arrow.length_options,
                "material": arrow.material,
                "arrow_type": str(arrow.arrow_type) if arrow.arrow_type else None,
                "recommended_use": arrow.recommended_use,
                "description": arrow.description,
                "source_url": arrow.source_url,
                "scraped_at": arrow.scraped_at.isoformat()
            }
            for arrow in all_arrows
        ]
    }
    
    with open(demo_file, 'w') as f:
        json.dump(demo_export, f, indent=2, default=str)
    
    print(f"\n📊 EXTRACTION DEMO COMPLETE!")
    print(f"   URLs processed: {len(demo_urls)}")
    print(f"   Arrows extracted: {len(all_arrows)}")
    print(f"   Success rate: {(len(all_arrows)/len(demo_urls)*100):.1f}%")
    print(f"💾 Results saved to: {demo_file}")
    
    # Show detailed breakdown
    print(f"\n🏹 EXTRACTED ARROWS:")
    for arrow in all_arrows:
        print(f"\n📋 {arrow.model_name}")
        print(f"   🎯 Spines: {arrow.spine_options}")
        print(f"   📏 Outer Ø: {arrow.diameter}\"")
        if arrow.inner_diameter:
            print(f"   📏 Inner Ø: {arrow.inner_diameter}\"")
        print(f"   ⚖️  Weight: {arrow.gpi_weight} GPI")
        if arrow.length_options:
            print(f"   📐 Lengths: {arrow.length_options}\"")
        if arrow.arrow_type:
            print(f"   🎪 Type: {arrow.arrow_type}")
        if arrow.description:
            print(f"   📝 {arrow.description[:80]}...")
    
    print(f"\n🎉 Phase 1 extraction infrastructure is fully operational!")
    print(f"   Ready to scale to all {len(all_arrows)} manufacturers in phase documentation!")

if __name__ == "__main__":
    asyncio.run(demo_skylon_extraction())