#!/usr/bin/env python3
"""
Test the scraper with direct arrow product URLs that should have specifications
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from scrapers.easton_scraper import EastonScraper

async def test_direct_arrow_urls():
    """Test scraping direct arrow product URLs"""
    print("Testing Direct Arrow Product URLs")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found in .env file")
        return False
    
    # Create scraper
    scraper = EastonScraper(deepseek_api_key)
    print(f"✓ Scraper created with session ID: {scraper.session_id}")
    
    # Direct arrow product URLs that should have specifications
    direct_urls = [
        "https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/",
        "https://eastonarchery.com/arrows_/carbon-legacy/",
        "https://eastonarchery.com/arrows_/bowhunter/",
        "https://eastonarchery.com/arrows_/fmj/",
        "https://eastonarchery.com/arrows_/axis-traditional/",
    ]
    
    print(f"📡 Testing {len(direct_urls)} direct product URLs")
    
    all_arrows = []
    successful_extractions = 0
    
    for i, url in enumerate(direct_urls, 1):
        print(f"\n🔗 [{i}/{len(direct_urls)}] Testing: {url}")
        
        try:
            # Get extraction prompt
            extraction_prompt = scraper.get_easton_extraction_prompt()
            
            # Scrape the URL
            result = await scraper.scrape_url(url, extraction_prompt)
            
            if result.success:
                print(f"   ✅ Scrape successful")
                print(f"   📊 Arrows found: {result.arrows_found}")
                
                if result.processed_data and len(result.processed_data) > 0:
                    successful_extractions += 1
                    all_arrows.extend(result.processed_data)
                    
                    for j, arrow in enumerate(result.processed_data):
                        print(f"   🎯 Arrow {j+1}: {arrow.model_name}")
                        print(f"      Spine options: {arrow.get_spine_options()}")
                        print(f"      Diameter range: {arrow.get_diameter_range()[0]:.3f}\" - {arrow.get_diameter_range()[1]:.3f}\"")
                        print(f"      GPI range: {arrow.get_gpi_range()[0]:.1f} - {arrow.get_gpi_range()[1]:.1f}")
                        
                        # Show first few spine specifications
                        print(f"      Spine details:")
                        for spec in arrow.spine_specifications[:3]:
                            inner_text = f", {spec.inner_diameter:.3f}\" ID" if spec.inner_diameter else ""
                            print(f"        Spine {spec.spine}: {spec.outer_diameter:.3f}\" OD{inner_text}, {spec.gpi_weight:.1f} GPI")
                        
                        if len(arrow.spine_specifications) > 3:
                            print(f"        ... and {len(arrow.spine_specifications) - 3} more")
                else:
                    print(f"   ⚠️  No arrow data extracted")
            else:
                print(f"   ❌ Scrape failed: {result.errors}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    # Save session data
    scraper.save_session_data()
    
    # Summary
    print(f"\n📊 DIRECT URL TEST SUMMARY:")
    print(f"   URLs tested: {len(direct_urls)}")
    print(f"   Successful extractions: {successful_extractions}")
    print(f"   Total arrows found: {len(all_arrows)}")
    print(f"   Total spine options: {sum(len(arrow.spine_specifications) for arrow in all_arrows)}")
    print(f"   Success rate: {(successful_extractions/len(direct_urls)*100):.1f}%")
    
    return successful_extractions > 0

def main():
    """Run the direct URL test"""
    success = asyncio.run(test_direct_arrow_urls())
    
    if success:
        print("\n🎉 Direct URL test found arrows with spine-specific data!")
        print("✅ The scraper works when given proper product pages")
        print("\n💡 NEXT STEPS:")
        print("1. Need to discover individual arrow product URLs from category pages")
        print("2. Or create a list of known arrow product URLs for each manufacturer")
        print("3. Category pages just list arrows, they don't contain specifications")
    else:
        print("\n❌ No arrows extracted from direct URLs")
        print("This could mean:")
        print("1. The URLs don't contain arrow specifications")
        print("2. The LLM extraction needs fine-tuning")
        print("3. The website structure has changed")

if __name__ == "__main__":
    main()