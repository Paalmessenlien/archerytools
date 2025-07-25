#!/usr/bin/env python3
"""
Demonstration script to extract and show actual arrow data
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from deepseek_extractor import DeepSeekArrowExtractor

async def demo_arrow_extraction():
    """Demonstrate actual arrow data extraction"""
    
    print("Arrow Data Extraction Demonstration")
    print("=" * 50)
    
    # Test URLs with likely arrow specifications
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
            print(f"\n🔍 [{i}/{len(test_urls)}] Extracting from: {url}")
            print("-" * 60)
            
            try:
                # Crawl the page
                result = await crawler.arun(url=url, bypass_cache=True)
                
                if result.success:
                    content = result.markdown or result.html or ""
                    print(f"✓ Page crawled successfully ({len(content)} characters)")
                    
                    # Show content sample to see what we're working with
                    print(f"📄 Content sample (chars 2000-4000):")
                    print("-" * 30)
                    print(content[2000:4000])
                    print("-" * 30)
                    
                    # Extract with DeepSeek
                    print(f"🤖 Attempting AI extraction...")
                    arrows = extractor.extract_arrows_from_content(
                        content=content,
                        source_url=url,
                        manufacturer="Easton"
                    )
                    
                    if arrows:
                        print(f"✅ Found {len(arrows)} arrows!")
                        for arrow in arrows:
                            print(f"   🏹 {arrow.model_name}")
                            print(f"      Spines: {arrow.spine_options}")
                            print(f"      Diameter: {arrow.diameter}\"")
                            print(f"      GPI: {arrow.gpi_weight}")
                            print(f"      Type: {arrow.arrow_type}")
                            all_arrows.extend(arrows)
                    else:
                        print(f"❌ No arrows extracted")
                        
                        # Try manual pattern extraction as fallback
                        print(f"🔧 Trying manual pattern extraction...")
                        import re
                        
                        content_lower = content.lower()
                        
                        # Look for spine values
                        spine_pattern = r'\b([2-7]\d{2})\b'
                        spines = re.findall(spine_pattern, content_lower)
                        spines = [int(s) for s in spines if 250 <= int(s) <= 800]
                        
                        # Look for diameter values  
                        diameter_pattern = r'\b0\.([2-4]\d{2})\b'
                        diameters = re.findall(diameter_pattern, content_lower)
                        diameters = [float(f"0.{d}") for d in diameters]
                        
                        # Look for GPI values
                        gpi_pattern = r'\b(\d+\.\d+)\s*gpi\b'
                        gpis = re.findall(gpi_pattern, content_lower)
                        gpis = [float(g) for g in gpis]
                        
                        print(f"   📊 Manual extraction results:")
                        print(f"      Spine values found: {list(set(spines))}")
                        print(f"      Diameter values: {list(set(diameters))}")
                        print(f"      GPI values: {gpis}")
                        
                        if spines or diameters:
                            print(f"   ℹ️  Technical data detected but not extracted by AI")
                
                else:
                    print(f"❌ Failed to crawl: {result.error_message}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()
    
    # Summary
    print("=" * 50)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 50)
    print(f"URLs tested: {len(test_urls)}")
    print(f"Arrows extracted: {len(all_arrows)}")
    
    if all_arrows:
        print(f"\n🎉 Successfully extracted arrow data!")
        
        # Save to file
        output_file = Path(__file__).parent / "data" / "processed" / "demo_arrows.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        demo_data = {
            "extraction_demo": True,
            "total_arrows": len(all_arrows),
            "arrows": [arrow.model_dump() for arrow in all_arrows],
            "source_urls": test_urls
        }
        
        with open(output_file, 'w') as f:
            json.dump(demo_data, f, indent=2, default=str)
        
        print(f"💾 Data saved to: {output_file}")
        
        # Show the data
        print(f"\n📋 EXTRACTED ARROW DATA:")
        for i, arrow in enumerate(all_arrows, 1):
            print(f"\nArrow {i}:")
            print(f"  Model: {arrow.model_name}")
            print(f"  Manufacturer: {arrow.manufacturer}")
            print(f"  Spines: {arrow.spine_options}")
            print(f"  Diameter: {arrow.diameter}\"")
            print(f"  GPI Weight: {arrow.gpi_weight}")
            print(f"  Type: {arrow.arrow_type}")
            print(f"  Material: {arrow.material}")
            print(f"  Source: {arrow.source_url}")
    
    else:
        print(f"\n⚠️  No complete arrow specifications extracted")
        print(f"   This indicates the AI extraction needs refinement")
        print(f"   Manual patterns show technical data is present")

if __name__ == "__main__":
    asyncio.run(demo_arrow_extraction())