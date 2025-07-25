#!/usr/bin/env python3
"""
Focused Arrow Data Extraction - Complete extraction from working manufacturers
Focus on manufacturers that have direct product URLs and are working well
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from deepseek_extractor import DeepSeekArrowExtractor
from models import ArrowSpecification, ManufacturerData

class FocusedArrowScraper:
    """Focused scraper for manufacturers with working direct product URLs"""
    
    def __init__(self, api_key: str):
        self.extractor = DeepSeekArrowExtractor(api_key)
        self.session_id = f"focused_extraction_{int(time.time())}"
        
        # Focus on manufacturers with direct product URLs that are working
        self.manufacturers = {
            "Skylon Archery": {
                "base_url": "https://www.skylonarchery.com/",
                "product_urls": [
                    # ID 3.2 Series (4 arrows)
                    "https://www.skylonarchery.com/arrows/id-3-2/performa",
                    "https://www.skylonarchery.com/arrows/id-3-2/precium",
                    "https://www.skylonarchery.com/arrows/id-3-2/paragon",
                    "https://www.skylonarchery.com/arrows/id-3-2/preminens",
                    # ID 4.2 Series (3 arrows)
                    "https://www.skylonarchery.com/arrows/2023-06-29-08-52-09/novice",
                    "https://www.skylonarchery.com/arrows/2023-06-29-08-52-09/radius",
                    "https://www.skylonarchery.com/arrows/2023-06-29-08-52-09/brixxon",
                    # ID 5.2 Series (4 arrows)
                    "https://www.skylonarchery.com/arrows/id-5-2/instec",
                    "https://www.skylonarchery.com/arrows/id-5-2/quantic",
                    "https://www.skylonarchery.com/arrows/id-5-2/ebony",
                    "https://www.skylonarchery.com/arrows/id-5-2/backbone",
                    # ID 6.2 Series (8 arrows)
                    "https://www.skylonarchery.com/arrows/id-6-2/fast-wing",
                    "https://www.skylonarchery.com/arrows/id-6-2/savage",
                    "https://www.skylonarchery.com/arrows/id-6-2/edge",
                    "https://www.skylonarchery.com/arrows/id-6-2/maverick",
                    "https://www.skylonarchery.com/arrows/id-6-2/rove",
                    "https://www.skylonarchery.com/arrows/id-6-2/phoric",
                    "https://www.skylonarchery.com/arrows/id-6-2/frontier",
                    "https://www.skylonarchery.com/arrows/id-6-2/bentwood",
                    # ID 8.0 Series (2 arrows)
                    "https://www.skylonarchery.com/arrows/id-8-0/bruxx",
                    "https://www.skylonarchery.com/arrows/id-8-0/empros"
                ]
            },
            "Nijora Archery": {
                "base_url": "https://nijora.com/",
                "product_urls": [
                    # Top 10 most popular models
                    "https://nijora.com/product/songan/",
                    "https://nijora.com/product/3d-fly/",
                    "https://nijora.com/product/nigan-pro/",
                    "https://nijora.com/product/payat/",
                    "https://nijora.com/product/tokala/",
                    "https://nijora.com/product/bark/",
                    "https://nijora.com/product/elsu-pro/",
                    "https://nijora.com/product/zitkala/",
                    "https://nijora.com/product/onawa-pro/",
                    "https://nijora.com/product/big-9-9-2/"
                ]
            },
            "DK Bow": {
                "base_url": "https://dkbow.de/",
                "product_urls": [
                    "https://dkbow.de/Pfeile/DK-Carbon-Arrows/DK-Cougar-ID4.2/",
                    "https://dkbow.de/Pfeile/DK-Carbon-Arrows/DK-Panther-ID6.2/",
                    "https://dkbow.de/Pfeile/DK-Carbon-Arrows/DK-Tyrfing-ID5.2/",
                    "https://dkbow.de/Pfeile/DK-Carbon-Arrows/DK-Gungnir-ID4.2/",
                    "https://dkbow.de/Pfeile/DK-Carbon-Arrows/DK-Perregrin-Fertigpfeil/"
                ]
            },
            "Pandarus Archery": {
                "base_url": "https://www.pandarusarchery.com/",
                "product_urls": [
                    # Target Arrows
                    "https://www.pandarusarchery.com/elite_ca320",
                    "https://www.pandarusarchery.com/elite-xt",
                    "https://www.pandarusarchery.com/elite-ca320-pro",
                    "https://www.pandarusarchery.com/champion",
                    "https://www.pandarusarchery.com/precision",
                    # Hunting Arrows
                    "https://www.pandarusarchery.com/alpha-x"
                ]
            }
        }
    
    async def scrape_manufacturer(self, crawler: AsyncWebCrawler, manufacturer: str, config: Dict[str, Any]) -> ManufacturerData:
        """Scrape all arrows from a single manufacturer"""
        
        print(f"\n🏭 FOCUSED SCRAPING: {manufacturer.upper()}")
        print("=" * 60)
        
        all_arrows = []
        urls_to_scrape = config["product_urls"]
        
        print(f"📋 Processing {len(urls_to_scrape)} direct product URLs")
        
        # Scrape each URL
        successful_extractions = 0
        for i, url in enumerate(urls_to_scrape, 1):
            print(f"\n🔗 [{i}/{len(urls_to_scrape)}] {url}")
            
            try:
                # Crawl the page
                result = await crawler.arun(url=url, bypass_cache=True)
                
                if result.success:
                    content = result.markdown or result.html or ""
                    print(f"   ✓ Crawled ({len(content)} chars)")
                    
                    # Extract arrow specifications
                    arrows = self.extractor.extract_arrows_from_content(
                        content=content,
                        source_url=url,
                        manufacturer=manufacturer
                    )
                    
                    if arrows:
                        print(f"   🎉 Extracted {len(arrows)} arrows!")
                        for j, arrow in enumerate(arrows, 1):
                            print(f"      {j}. {arrow.model_name}")
                            print(f"         Spines: {arrow.spine_options}")
                            print(f"         Diameter: {arrow.diameter}\"")
                            if arrow.inner_diameter:
                                print(f"         Inner Ø: {arrow.inner_diameter}\"")
                            print(f"         GPI: {arrow.gpi_weight}")
                            if arrow.length_options:
                                print(f"         Lengths: {arrow.length_options}\"")
                            if arrow.arrow_type:
                                print(f"         Type: {arrow.arrow_type}")
                        all_arrows.extend(arrows)
                        successful_extractions += 1
                    else:
                        print(f"   ⚠️  No arrows extracted")
                else:
                    print(f"   ❌ Failed to crawl: {result.error_message}")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        # Create manufacturer data
        manufacturer_data = ManufacturerData(
            manufacturer=manufacturer,
            arrows=all_arrows
        )
        
        print(f"\n📊 {manufacturer.upper()} SUMMARY:")
        print(f"   URLs processed: {len(urls_to_scrape)}")
        print(f"   Successful extractions: {successful_extractions}")
        print(f"   Total arrows found: {len(all_arrows)}")
        print(f"   Success rate: {(successful_extractions/len(urls_to_scrape)*100):.1f}%" if urls_to_scrape else "N/A")
        
        return manufacturer_data
    
    async def scrape_focused_manufacturers(self) -> Dict[str, ManufacturerData]:
        """Scrape focused set of manufacturers"""
        
        print("FOCUSED ARROW EXTRACTION")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Manufacturers to process: {len(self.manufacturers)}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_manufacturer_data = {}
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            for manufacturer, config in self.manufacturers.items():
                try:
                    manufacturer_data = await self.scrape_manufacturer(crawler, manufacturer, config)
                    all_manufacturer_data[manufacturer] = manufacturer_data
                    
                    # Add delay between manufacturers
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Failed to scrape {manufacturer}: {e}")
                    continue
        
        return all_manufacturer_data
    
    def save_results(self, all_data: Dict[str, ManufacturerData]):
        """Save focused results to files"""
        
        # Create output directory
        output_dir = Path(__file__).parent / "data" / "focused_extraction"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        total_arrows = 0
        total_manufacturers = len(all_data)
        
        # Save individual manufacturer files
        for manufacturer, data in all_data.items():
            manufacturer_file = output_dir / f"{manufacturer.lower().replace(' ', '_')}_arrows.json"
            
            manufacturer_export = {
                "manufacturer": manufacturer,
                "extraction_date": datetime.now().isoformat(),
                "total_arrows": len(data.arrows),
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
                    for arrow in data.arrows
                ]
            }
            
            with open(manufacturer_file, 'w') as f:
                json.dump(manufacturer_export, f, indent=2, default=str)
            
            print(f"💾 {manufacturer}: {len(data.arrows)} arrows saved to {manufacturer_file.name}")
            total_arrows += len(data.arrows)
        
        # Save focused summary
        summary_file = output_dir / "focused_summary.json"
        
        summary_data = {
            "extraction_session": {
                "session_id": self.session_id,
                "extraction_date": datetime.now().isoformat(),
                "total_manufacturers": total_manufacturers,
                "total_arrows_extracted": total_arrows
            },
            "manufacturer_summaries": {
                manufacturer: {
                    "arrows_found": len(data.arrows),
                    "unique_models": len(set(arrow.model_name for arrow in data.arrows)),
                    "spine_range": {
                        "min": min((min(arrow.spine_options) for arrow in data.arrows), default=0),
                        "max": max((max(arrow.spine_options) for arrow in data.arrows), default=0)
                    } if data.arrows else {"min": 0, "max": 0},
                    "diameter_range": {
                        "min": min((arrow.diameter for arrow in data.arrows), default=0),
                        "max": max((arrow.diameter for arrow in data.arrows), default=0)
                    } if data.arrows else {"min": 0, "max": 0}
                }
                for manufacturer, data in all_data.items()
            },
            "detailed_arrow_breakdown": {
                manufacturer: [
                    {
                        "model": arrow.model_name,
                        "spines": len(arrow.spine_options),
                        "diameter": arrow.diameter,
                        "gpi": arrow.gpi_weight,
                        "type": str(arrow.arrow_type) if arrow.arrow_type else "unknown"
                    }
                    for arrow in data.arrows
                ]
                for manufacturer, data in all_data.items()
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)
        
        print(f"\n📋 FOCUSED SUMMARY saved to {summary_file.name}")
        
        return summary_data

async def main():
    """Main execution function"""
    
    # Check for DeepSeek API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not found")
        print("Please set your DeepSeek API key:")
        print("export DEEPSEEK_API_KEY='your_api_key_here'")
        return
    
    print("🎯 Starting focused arrow extraction from working manufacturers...")
    
    # Create scraper and run extraction
    scraper = FocusedArrowScraper(api_key)
    all_data = await scraper.scrape_focused_manufacturers()
    
    # Save results
    summary = scraper.save_results(all_data)
    
    # Final report
    print("\n" + "=" * 60)
    print("🎉 FOCUSED EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"✅ Manufacturers processed: {len(all_data)}")
    print(f"✅ Total arrows extracted: {summary['extraction_session']['total_arrows_extracted']}")
    
    print(f"\n📊 MANUFACTURER BREAKDOWN:")
    for manufacturer, stats in summary['manufacturer_summaries'].items():
        if stats['arrows_found'] > 0:
            print(f"   {manufacturer}: {stats['arrows_found']} arrows, {stats['unique_models']} models")
            spine_range = stats['spine_range']
            diameter_range = stats['diameter_range']
            print(f"      Spine range: {spine_range['min']}-{spine_range['max']}")
            print(f"      Diameter range: {diameter_range['min']:.3f}\"-{diameter_range['max']:.3f}\"")
    
    print(f"\n💾 All data saved to: data/focused_extraction/")
    
    # Show sample arrows
    print(f"\n🏹 SAMPLE ARROWS EXTRACTED:")
    for manufacturer, data in all_data.items():
        if data.arrows:
            sample_arrow = data.arrows[0]
            print(f"\n📋 {manufacturer} - {sample_arrow.model_name}")
            print(f"   🎯 Spines: {sample_arrow.spine_options}")
            print(f"   📏 Diameter: {sample_arrow.diameter}\" | GPI: {sample_arrow.gpi_weight}")
            if sample_arrow.arrow_type:
                print(f"   🎪 Type: {sample_arrow.arrow_type}")
            if sample_arrow.description:
                print(f"   📝 {sample_arrow.description[:80]}...")
    
    print(f"\n🎯 Focused extraction successful - ready to scale to all manufacturers!")

if __name__ == "__main__":
    asyncio.run(main())