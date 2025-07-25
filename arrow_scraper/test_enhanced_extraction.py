#!/usr/bin/env python3
"""
Test the enhanced AI extraction on real manufacturer pages
"""

import asyncio
import json
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from deepseek_extractor import DeepSeekArrowExtractor

async def test_enhanced_extraction():
    """Test enhanced extraction on real pages"""
    
    print("Enhanced Arrow Extraction Test")
    print("=" * 50)
    
    test_urls = [
        "https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/",
        "https://eastonarchery.com/arrows_/carbon-legacy/",
        "https://eastonarchery.com/arrows_/x27/"
    ]
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ No DeepSeek API key found")
        return
    
    extractor = DeepSeekArrowExtractor(api_key)
    all_arrows = []
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        for i, url in enumerate(test_urls, 1):
            print(f"\n🔍 [{i}/{len(test_urls)}] Testing: {url}")
            print("-" * 70)
            
            try:
                # Crawl the page
                result = await crawler.arun(url=url, bypass_cache=True)
                
                if result.success:
                    content = result.markdown or result.html or ""
                    print(f"✓ Page crawled ({len(content)} chars)")
                    
                    # Extract with enhanced AI
                    arrows = extractor.extract_arrows_from_content(
                        content=content,
                        source_url=url,
                        manufacturer="Easton"
                    )
                    
                    if arrows:
                        print(f"🎉 Successfully extracted {len(arrows)} arrows!")
                        
                        for j, arrow in enumerate(arrows, 1):
                            print(f"\n   🏹 Arrow {j}: {arrow.model_name}")
                            print(f"      Spines: {arrow.spine_options}")
                            print(f"      Outer Diameter: {arrow.diameter}\"")
                            if arrow.inner_diameter:
                                print(f"      Inner Diameter: {arrow.inner_diameter}\"")
                            print(f"      GPI Weight: {arrow.gpi_weight}")
                            if arrow.length_options:
                                print(f"      Lengths: {arrow.length_options}\"")
                            print(f"      Type: {arrow.arrow_type}")
                            if arrow.recommended_use:
                                print(f"      Uses: {arrow.recommended_use}")
                            if arrow.description:
                                print(f"      Description: {arrow.description[:100]}...")
                        
                        all_arrows.extend(arrows)
                    else:
                        print(f"❌ No arrows extracted")
                        
                        # Show what content was analyzed
                        print(f"📄 Sample content analyzed:")
                        content_sample = content[3000:4000] if len(content) > 4000 else content[:1000]
                        print(f"   {content_sample}...")
                
                else:
                    print(f"❌ Failed to crawl: {result.error_message}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Save results and summary
    print(f"\n{'='*50}")
    print(f"📊 ENHANCED EXTRACTION SUMMARY")
    print(f"{'='*50}")
    print(f"URLs tested: {len(test_urls)}")
    print(f"Total arrows extracted: {len(all_arrows)}")
    
    if all_arrows:
        # Save to file
        output_file = Path(__file__).parent / "data" / "processed" / "enhanced_extraction_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        results_data = {
            "enhanced_extraction_test": True,
            "total_arrows_found": len(all_arrows),
            "extraction_details": [
                {
                    "model_name": arrow.model_name,
                    "spine_options": arrow.spine_options,
                    "outer_diameter": arrow.diameter,
                    "inner_diameter": arrow.inner_diameter,
                    "gpi_weight": arrow.gpi_weight,
                    "length_options": arrow.length_options,
                    "arrow_type": str(arrow.arrow_type) if arrow.arrow_type else None,
                    "recommended_use": arrow.recommended_use,
                    "description": arrow.description,
                    "source_url": arrow.source_url
                }
                for arrow in all_arrows
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        print(f"\n💾 Enhanced extraction results saved to:")
        print(f"    {output_file}")
        
        print(f"\n🏹 COMPLETE ARROW DATA EXTRACTED:")
        for arrow in all_arrows:
            print(f"\n📋 {arrow.model_name}")
            print(f"   🎯 Primary Use: {arrow.arrow_type}")
            print(f"   📏 Measurements:")
            print(f"      • Spines: {arrow.spine_options}")
            print(f"      • Outer Ø: {arrow.diameter}\"")
            if arrow.inner_diameter:
                print(f"      • Inner Ø: {arrow.inner_diameter}\"")
            print(f"      • Weight: {arrow.gpi_weight} GPI")
            if arrow.length_options:
                print(f"      • Lengths: {arrow.length_options}\"")
            if arrow.recommended_use:
                print(f"   🎪 All Uses: {', '.join(arrow.recommended_use)}")
            if arrow.description:
                print(f"   📝 Description: {arrow.description}")
        
        print(f"\n🎉 Enhanced extraction successful!")
        print(f"   Ready for production scraping of all manufacturer arrows!")
        
    else:
        print(f"\n⚠️  No complete arrow specifications extracted")
        print(f"   Enhanced prompts may need further refinement")

if __name__ == "__main__":
    asyncio.run(test_enhanced_extraction())