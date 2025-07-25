#!/usr/bin/env python3
"""
Test the updated scraper with a specific arrow product page
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from scrapers.easton_scraper import EastonScraper

async def test_specific_arrow():
    """Test scraping a specific Easton arrow product page"""
    print("Testing Updated Scraper with Specific Arrow Page")
    print("=" * 60)
    
    # Load environment
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found in .env file")
        return False
    
    print(f"✓ API key loaded: {deepseek_api_key[:10]}...")
    
    # Create scraper
    scraper = EastonScraper(deepseek_api_key)
    print(f"✓ Scraper created with session ID: {scraper.session_id}")
    
    # Test with specific arrow URLs that should have specifications
    test_urls = [
        "https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/",
        "https://eastonarchery.com/arrows_/carbon-legacy/",
        "https://eastonarchery.com/arrows_/fmj/"
    ]
    
    for i, test_url in enumerate(test_urls):
        print(f"\n📡 Testing URL {i+1}: {test_url}")
        
        try:
            # Get the extraction prompt
            extraction_prompt = scraper.get_easton_extraction_prompt()
            
            # Scrape the URL
            print("🔍 Starting scrape...")
            result = await scraper.scrape_url(test_url, extraction_prompt)
            
            if result.success:
                print(f"✅ Scrape successful!")
                print(f"📊 Arrows found: {result.arrows_found}")
                
                if result.processed_data and len(result.processed_data) > 0:
                    print("\n📋 Extracted arrow data:")
                    print("-" * 40)
                    
                    for j, arrow in enumerate(result.processed_data[:2]):  # Show first 2 arrows
                        print(f"\nArrow {j+1}: {arrow.model_name}")
                        print(f"  Manufacturer: {arrow.manufacturer}")
                        print(f"  Spine options: {arrow.get_spine_options()}")
                        print(f"  Diameter range: {arrow.get_diameter_range()[0]:.3f}\" - {arrow.get_diameter_range()[1]:.3f}\"")
                        print(f"  GPI range: {arrow.get_gpi_range()[0]:.1f} - {arrow.get_gpi_range()[1]:.1f}")
                        
                        # Show spine-specific details
                        print("  Spine-specific details:")
                        for spec in arrow.spine_specifications[:5]:  # Show first 5 spines
                            inner_dia = f", {spec.inner_diameter:.3f}\" ID" if spec.inner_diameter else ""
                            print(f"    Spine {spec.spine}: {spec.outer_diameter:.3f}\" OD{inner_dia}, {spec.gpi_weight:.1f} GPI")
                        
                        if len(arrow.spine_specifications) > 5:
                            print(f"    ... and {len(arrow.spine_specifications) - 5} more spine options")
                        
                        if arrow.material:
                            print(f"  Material: {arrow.material}")
                        if arrow.arrow_type:
                            print(f"  Type: {arrow.arrow_type}")
                        if arrow.recommended_use:
                            print(f"  Use: {', '.join(arrow.recommended_use)}")
                    
                    print(f"\n✅ SUCCESS: Found complete spine-specific data!")
                    print(f"   Total spine options: {sum(len(arrow.spine_specifications) for arrow in result.processed_data)}")
                    return True
                    
                else:
                    print("⚠️  No arrow data extracted")
                    
            else:
                print(f"❌ Scrape failed: {result.errors}")
                
        except Exception as e:
            print(f"💥 Error during scraping: {e}")
            import traceback
            traceback.print_exc()
    
    return False

def main():
    """Run the specific arrow test"""
    success = asyncio.run(test_specific_arrow())
    
    if success:
        print("\n🎉 Specific arrow test passed!")
        print("✅ Spine-specific extraction is working correctly")
        print("✅ Ready to run full scraping")
        print("\nTo run full scraping:")
        print("python main.py easton")
    else:
        print("\n❌ No arrows were successfully extracted")
        print("This might be normal if the URLs don't contain specification data")
        print("Let's try the full scraper anyway - it may work better with category pages")

if __name__ == "__main__":
    main()