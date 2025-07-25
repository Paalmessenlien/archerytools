#!/usr/bin/env python3
"""
Run extraction using the approach that we know worked before, 
then adapt it for the spine-specific model
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from scrapers.easton_scraper import EastonScraper

async def run_working_extraction():
    """Run extraction that should work based on previous success"""
    print("Running Working Extraction Test")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    # Use the URL that worked before
    working_url = "https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/"
    print(f"🔗 Testing previously working URL: {working_url}")
    
    # Create scraper
    scraper = EastonScraper(deepseek_api_key)
    print(f"✓ Scraper created: {scraper.session_id}")
    
    try:
        # Get extraction prompt
        extraction_prompt = scraper.get_easton_extraction_prompt()
        print("✓ Extraction prompt created")
        
        print("\n🔍 Starting extraction...")
        
        # Try the extraction
        result = await scraper.scrape_url(working_url, extraction_prompt)
        
        print(f"📊 Extraction result:")
        print(f"   Success: {result.success}")
        print(f"   Arrows found: {result.arrows_found}")
        print(f"   Processing time: {result.processing_time:.2f}s")
        print(f"   Errors: {result.errors}")
        
        if result.success and result.processed_data:
            print("\n🎉 SUCCESS! Extraction worked!")
            
            for i, arrow in enumerate(result.processed_data, 1):
                print(f"\n   Arrow {i}: {arrow.model_name}")
                print(f"      Manufacturer: {arrow.manufacturer}")
                print(f"      Spine options: {arrow.get_spine_options()}")
                print(f"      Spine specifications count: {len(arrow.spine_specifications)}")
                print(f"      Diameter range: {arrow.get_diameter_range()[0]:.3f}\" - {arrow.get_diameter_range()[1]:.3f}\"")
                print(f"      GPI range: {arrow.get_gpi_range()[0]:.1f} - {arrow.get_gpi_range()[1]:.1f}")
                
                # Show detailed spine specifications
                print(f"      Detailed spine specs:")
                for spec in arrow.spine_specifications:
                    inner_text = f", ID: {spec.inner_diameter:.3f}\"" if spec.inner_diameter else ""
                    lengths = f", Lengths: {spec.length_options}" if spec.length_options else ""
                    print(f"        Spine {spec.spine}: OD {spec.outer_diameter:.3f}\", GPI {spec.gpi_weight:.1f}{inner_text}{lengths}")
                
                if arrow.material:
                    print(f"      Material: {arrow.material}")
                if arrow.arrow_type:
                    print(f"      Type: {arrow.arrow_type}")
                if arrow.recommended_use:
                    print(f"      Uses: {', '.join(arrow.recommended_use)}")
                if arrow.description:
                    print(f"      Description: {arrow.description[:100]}...")
            
            # Save the working session
            scraper.save_session_data()
            
            print(f"\n💾 Session data saved for inspection")
            print(f"✅ The spine-specific extraction is WORKING!")
            
            return True
            
        else:
            print("\n❌ Extraction failed or no data found")
            if result.errors:
                print(f"Errors: {result.errors}")
            
            return False
            
    except Exception as e:
        print(f"\n💥 Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_urls():
    """Test extraction on multiple URLs to verify consistency"""
    print("\n" + "=" * 50)
    print("Testing Multiple Arrow URLs")
    print("=" * 50)
    
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    scraper = EastonScraper(deepseek_api_key)
    
    # URLs that should have specifications
    test_urls = [
        "https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/",
        "https://eastonarchery.com/arrows_/carbon-legacy/",
        "https://eastonarchery.com/arrows_/fmj/",
        "https://eastonarchery.com/arrows_/bowhunter/"
    ]
    
    successful_extractions = 0
    total_arrows = 0
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🔗 [{i}/{len(test_urls)}] Testing: {url}")
        
        try:
            extraction_prompt = scraper.get_easton_extraction_prompt()
            result = await scraper.scrape_url(url, extraction_prompt)
            
            if result.success and result.processed_data:
                successful_extractions += 1
                arrows_count = len(result.processed_data)
                total_arrows += arrows_count
                print(f"   ✅ Success: {arrows_count} arrows found")
                
                for arrow in result.processed_data:
                    spine_count = len(arrow.spine_specifications)
                    print(f"      {arrow.model_name}: {spine_count} spine options")
            else:
                print(f"   ❌ Failed: {result.errors}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print(f"\n📊 MULTI-URL TEST SUMMARY:")
    print(f"   URLs tested: {len(test_urls)}")
    print(f"   Successful extractions: {successful_extractions}")
    print(f"   Total arrows found: {total_arrows}")
    print(f"   Success rate: {(successful_extractions/len(test_urls)*100):.1f}%")
    
    return successful_extractions > 0

def main():
    """Run the working extraction tests"""
    print("🚀 Testing Spine-Specific Arrow Extraction")
    
    # Test single URL first
    single_success = asyncio.run(run_working_extraction())
    
    if single_success:
        # Test multiple URLs
        multi_success = asyncio.run(test_multiple_urls())
        
        if multi_success:
            print(f"\n🎉 EXTRACTION SYSTEM IS WORKING!")
            print(f"✅ Ready to run comprehensive extraction")
            print(f"\nTo run full extraction:")
            print(f"python run_comprehensive_extraction.py")
        else:
            print(f"\n⚠️  Single URL worked but multiple failed")
            print(f"May need rate limiting or retry logic")
    else:
        print(f"\n❌ Basic extraction not working")
        print(f"Need to debug API or extraction logic")

if __name__ == "__main__":
    main()