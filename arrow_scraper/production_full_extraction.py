#!/usr/bin/env python3
"""
PRODUCTION FULL SCALE ARROW EXTRACTION
Extract ALL arrow specifications from ALL manufacturers in phase documentation
Complete database population for Phase 1
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import time
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from deepseek_extractor import DeepSeekArrowExtractor
from models import ArrowSpecification, ManufacturerData, ScrapingSession

class ProductionArrowScraper:
    """Production-scale scraper for complete arrow database extraction"""
    
    def __init__(self, api_key: str):
        self.extractor = DeepSeekArrowExtractor(api_key)
        self.session_id = f"production_full_{int(time.time())}"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'production_extraction_{self.session_id}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Complete manufacturer configuration from phase documentation
        self.manufacturers = {
            "Skylon Archery": {
                "base_url": "https://www.skylonarchery.com/",
                "total_expected": 21,
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
                "total_expected": 54,
                "product_urls": [
                    # Core Models
                    "https://nijora.com/product/songan/",
                    "https://nijora.com/product/3d-fly/",
                    "https://nijora.com/product/nigan-pro/",
                    "https://nijora.com/product/ilyan-pro-1000-350/",
                    "https://nijora.com/product/payat/",
                    "https://nijora.com/product/3k-pro/",
                    "https://nijora.com/product/tokala/",
                    "https://nijora.com/product/tokala-m/",
                    "https://nijora.com/product/tokala-long-36-inch/",
                    "https://nijora.com/product/nijora-yona/",
                    "https://nijora.com/product/oxx-pro/",
                    # Taperon Series
                    "https://nijora.com/product/taperon/",
                    "https://nijora.com/product/taperon-crust/",
                    "https://nijora.com/product/taperon-crust-600-turned-white/",
                    "https://nijora.com/product/taperon-sx/",
                    "https://nijora.com/product/nijora-taperon-330-hunter/",
                    "https://nijora.com/product/nijora-taperon-3k-400-orange-hunter/",
                    "https://nijora.com/product/taperon-orange/",
                    # Bark Series
                    "https://nijora.com/product/bark/",
                    "https://nijora.com/product/bark-m/",
                    "https://nijora.com/product/bark-pro/",
                    "https://nijora.com/product/bark-heavy/",
                    "https://nijora.com/product/bark-small/",
                    # Elsu Series
                    "https://nijora.com/product/elsu-golden-edition/",
                    "https://nijora.com/product/elsu-pro/",
                    # Other Models
                    "https://nijora.com/product/zitkala/",
                    "https://nijora.com/product/nijora-linawa/",
                    "https://nijora.com/product/big-9-9-2/",
                    "https://nijora.com/product/mammut-schaft-39-inch/",
                    # Onawa Series
                    "https://nijora.com/product/onawa-fly/",
                    "https://nijora.com/product/onawa-pro/",
                    "https://nijora.com/product/onawa-pro-x/",
                    "https://nijora.com/product/onawa-pro-xt-3-2/",
                    "https://nijora.com/product/onawa-pro-xt-40/",
                    # Junior Series
                    "https://nijora.com/product/junior-black-1800/",
                    "https://nijora.com/product/junior-1500-black-pink-yellow-orange/",
                    "https://nijora.com/product/junior-carbonschaft-optionale-komponenten/",
                    # Specialty Models
                    "https://nijora.com/product/hakan/",
                    "https://nijora.com/product/color-line/",
                    # 3D Series
                    "https://nijora.com/product/nijora-3d-fun/",
                    "https://nijora.com/product/nijora-3d-fun-neon-gelb-small-800-1200/",
                    "https://nijora.com/product/nijora-3d-red-spider/",
                    "https://nijora.com/product/nijora-3d-red-spider-small/",
                    "https://nijora.com/product/nijora-3d-blue/",
                    "https://nijora.com/product/nijora-3d-blue-small-1000/",
                    "https://nijora.com/product/nijora-3d-green/",
                    "https://nijora.com/product/nijora-3d-green-small-1000/",
                    "https://nijora.com/product/nijora-3d-white-rose/",
                    "https://nijora.com/product/nijora-3d-white-rose-small-1000/",
                    # Color Series
                    "https://nijora.com/product/nijora-orange/",
                    "https://nijora.com/product/nijora-orange-small-800-1200/",
                    "https://nijora.com/product/nijora-pink/",
                    "https://nijora.com/product/nijora-pink-1000-1200/",
                    "https://nijora.com/product/cyan-color-line-spine-1200-1000/",
                    "https://nijora.com/product/tokala-long-white-rose/",
                    "https://nijora.com/product/nijora-grey-panther-500-800/",
                    "https://nijora.com/product/mammut-atlatl-78-inch-fertigpfeil/"
                ]
            },
            "DK Bow": {
                "base_url": "https://dkbow.de/",
                "total_expected": 6,
                "product_urls": [
                    "https://dkbow.de/DK-Panther-Carbon-Arrow-ID-6.2/SW10007",
                    "https://dkbow.de/DK-Cougar-Carbon-Arrow-ID-4.2/36721",
                    "https://dkbow.de/DK-Tyrfing-Carbon-Arrow-ID-5.2/418",
                    "https://dkbow.de/DK-Gungnir-Carbon-Arrow-ID-4.2/SW10006"
                ]
            },
            "Pandarus Archery": {
                "base_url": "https://www.pandarusarchery.com/",
                "total_expected": 11,
                "product_urls": [
                    # Target Arrows
                    "https://www.pandarusarchery.com/elite_ca320",
                    "https://www.pandarusarchery.com/elite-xt",
                    "https://www.pandarusarchery.com/elite-ca320-pro",
                    "https://www.pandarusarchery.com/elite-ca390",
                    "https://www.pandarusarchery.com/ice-pointee77bb06",
                    "https://www.pandarusarchery.com/champion",
                    "https://www.pandarusarchery.com/infinity4d2a3aac",
                    "https://www.pandarusarchery.com/precision",
                    "https://www.pandarusarchery.com/alpha-xt",
                    "https://www.pandarusarchery.com/versus",
                    # Hunting Arrows
                    "https://www.pandarusarchery.com/alpha-x"
                ]
            },
            "BigArchery": {
                "base_url": "https://www.bigarchery.com/gb/",
                "total_expected": 37,
                "product_urls": [
                    # CROSS-X Series - Complete lineup
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/282-706-cross-x-shaft-ambitionpoint.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/283-716-cross-x-shaft-helios.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/284-722-cross-x-shaft-ares-hu.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/285-797-cross-x-shaft-gladiator.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/286-724-cross-x-shaft-maior-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/287-731-cross-x-shaft-plurima.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/288-742-cross-x-shaft-ambition-se-point.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/289-752-cross-x-shaft-madera.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/290-755-cross-x-shaft-plurima-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/291-765-cross-x-shaft-exentia.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/292-cross-x-shaft-xxiii-350.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/293-775-cross-x-shaft-hurricane-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/295-782-cross-x-shaft-hurricane-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/296-788-cross-x-shaft-maior-penta.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/297-791-cross-x-shaft-maior-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/298-800-cross-x-shaft-ambition-gold-ed.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/299-810-cross-x-shaft-fulmen.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/300-814-cross-x-shaft-madera-light.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/301-818-cross-x-shaft-avatar-penta.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/302-824-cross-x-shaft-avatar-cresting.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/303-cross-x-shaft-xxiii-octagon-350.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/304-828-cross-x-shaft-avatar-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/305-834-cross-x-shaft-pegasus-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/306-840-cross-x-shaft-pegasus-penta.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/307-846-cross-x-shaft-pegasus-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/308-870-cross-x-shaft-fulmen-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/309-877-cross-x-shaft-pegasus-cubecrest.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/310-881-cross-x-shaft-centurion.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/311-884-cross-x-shaft-exentia-test-pack.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/312-894-cross-x-shaft-raptor.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/313-900-cross-x-shaft-phoenix.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/314-905-cross-x-shaft-iridium.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1471-3444-cross-x-shaft-fulmen-xxl.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1640-4110-cross-x-shaft-avatar-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1671-4076-cross-x-shaft-fulmen-xxl-penta.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1734-4286-cross-x-shaft-pegasus.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1735-4294-cross-x-shaft-fulmen-xl.html"
                ]
            },
            "Carbon Express": {
                "base_url": "https://www.feradyne.com/",
                "total_expected": 9,
                "product_urls": [
                    "https://www.feradyne.com/product/maxima-sable-rz/",
                    "https://www.feradyne.com/product/maxima-sable-rz-select/",
                    "https://www.feradyne.com/product/maxima-photon-sd/",
                    "https://www.feradyne.com/product/maxima-triad/",
                    "https://www.feradyne.com/product/d-stroyer/",
                    "https://www.feradyne.com/product/d-stroyer-mx-hunter/",
                    "https://www.feradyne.com/product/cx-adrenaline/",
                    "https://www.feradyne.com/product/thunder-express/",
                    "https://www.feradyne.com/product/flu-flu-arrows/"
                ]
            }
        }
        
        # Calculate total expected arrows
        self.total_expected_arrows = sum(config["total_expected"] for config in self.manufacturers.values())
        self.logger.info(f"Production extraction targeting {self.total_expected_arrows} arrows across {len(self.manufacturers)} manufacturers")
    
    async def scrape_manufacturer_batch(self, crawler: AsyncWebCrawler, manufacturer: str, config: Dict[str, Any]) -> ManufacturerData:
        """Scrape all arrows from a manufacturer with batch processing"""
        
        self.logger.info(f"Starting {manufacturer} extraction - {config['total_expected']} arrows expected")
        print(f"\n🏭 PRODUCTION SCRAPING: {manufacturer.upper()}")
        print("=" * 70)
        
        all_arrows = []
        urls_to_scrape = config["product_urls"]
        batch_size = 10  # Process in batches to manage memory
        
        print(f"📋 Processing {len(urls_to_scrape)} URLs in batches of {batch_size}")
        
        successful_extractions = 0
        total_batches = (len(urls_to_scrape) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(urls_to_scrape))
            batch_urls = urls_to_scrape[start_idx:end_idx]
            
            print(f"\n🔄 Batch {batch_num + 1}/{total_batches} ({len(batch_urls)} URLs)")
            
            # Process batch
            for i, url in enumerate(batch_urls, start_idx + 1):
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
                                if len(arrow.spine_options) > 5:
                                    spine_display = f"{arrow.spine_options[:3]}...{arrow.spine_options[-2:]} ({len(arrow.spine_options)} total)"
                                else:
                                    spine_display = str(arrow.spine_options)
                                print(f"         Spines: {spine_display}")
                                print(f"         {arrow.diameter}\" OD | {arrow.gpi_weight} GPI")
                            all_arrows.extend(arrows)
                            successful_extractions += 1
                        else:
                            print(f"   ⚠️  No arrows extracted")
                    else:
                        print(f"   ❌ Failed to crawl: {result.error_message}")
                    
                    # Rate limiting between requests
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {url}: {e}")
                    print(f"   ❌ Error: {e}")
                    continue
            
            # Longer pause between batches
            if batch_num < total_batches - 1:
                print(f"   ⏸️  Batch pause (2s)...")
                await asyncio.sleep(2)
        
        # Create manufacturer data
        manufacturer_data = ManufacturerData(
            manufacturer=manufacturer,
            arrows=all_arrows
        )
        
        success_rate = (successful_extractions / len(urls_to_scrape) * 100) if urls_to_scrape else 0
        arrows_vs_expected = (len(all_arrows) / config["total_expected"] * 100) if config["total_expected"] else 0
        
        print(f"\n📊 {manufacturer.upper()} FINAL RESULTS:")
        print(f"   URLs processed: {len(urls_to_scrape)}")
        print(f"   Successful extractions: {successful_extractions}")
        print(f"   Total arrows found: {len(all_arrows)}")
        print(f"   Expected arrows: {config['total_expected']}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Coverage: {arrows_vs_expected:.1f}% of expected")
        
        self.logger.info(f"{manufacturer} complete: {len(all_arrows)}/{config['total_expected']} arrows ({arrows_vs_expected:.1f}%)")
        
        return manufacturer_data
    
    async def run_production_extraction(self) -> Dict[str, ManufacturerData]:
        """Run complete production extraction of all manufacturers"""
        
        print("PRODUCTION FULL SCALE ARROW EXTRACTION")
        print("=" * 80)
        print(f"Session ID: {self.session_id}")
        print(f"Target: {len(self.manufacturers)} manufacturers, {self.total_expected_arrows} arrows")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_manufacturer_data = {}
        total_arrows_extracted = 0
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            for i, (manufacturer, config) in enumerate(self.manufacturers.items(), 1):
                try:
                    print(f"\n{'='*80}")
                    print(f"MANUFACTURER {i}/{len(self.manufacturers)}: {manufacturer.upper()}")
                    print(f"{'='*80}")
                    
                    manufacturer_data = await self.scrape_manufacturer_batch(crawler, manufacturer, config)
                    all_manufacturer_data[manufacturer] = manufacturer_data
                    total_arrows_extracted += len(manufacturer_data.arrows)
                    
                    # Progress update
                    progress = (total_arrows_extracted / self.total_expected_arrows * 100)
                    print(f"\n🎯 OVERALL PROGRESS: {total_arrows_extracted}/{self.total_expected_arrows} arrows ({progress:.1f}%)")
                    
                    # Pause between manufacturers
                    if i < len(self.manufacturers):
                        print(f"⏸️  Manufacturer pause (3s)...")
                        await asyncio.sleep(3)
                    
                except Exception as e:
                    self.logger.error(f"Failed to scrape {manufacturer}: {e}")
                    print(f"❌ Failed to scrape {manufacturer}: {e}")
                    continue
        
        return all_manufacturer_data
    
    def save_production_results(self, all_data: Dict[str, ManufacturerData]):
        """Save complete production results with comprehensive analysis"""
        
        # Create production output directory
        output_dir = Path(__file__).parent / "data" / "production_extraction"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        total_arrows = sum(len(data.arrows) for data in all_data.values())
        total_coverage = (total_arrows / self.total_expected_arrows * 100) if self.total_expected_arrows else 0
        
        print(f"\n{'='*80}")
        print(f"SAVING PRODUCTION RESULTS")
        print(f"{'='*80}")
        
        # Save individual manufacturer files
        for manufacturer, data in all_data.items():
            manufacturer_file = output_dir / f"{manufacturer.lower().replace(' ', '_')}_complete.json"
            
            manufacturer_export = {
                "manufacturer_info": {
                    "name": manufacturer,
                    "extraction_date": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "base_url": self.manufacturers[manufacturer]["base_url"],
                    "total_arrows_found": len(data.arrows),
                    "expected_arrows": self.manufacturers[manufacturer]["total_expected"],
                    "coverage_percentage": (len(data.arrows) / self.manufacturers[manufacturer]["total_expected"] * 100) if self.manufacturers[manufacturer]["total_expected"] else 0
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
                    for arrow in data.arrows
                ]
            }
            
            with open(manufacturer_file, 'w') as f:
                json.dump(manufacturer_export, f, indent=2, default=str)
            
            print(f"💾 {manufacturer}: {len(data.arrows)} arrows → {manufacturer_file.name}")
        
        # Create comprehensive master file
        master_file = output_dir / "complete_arrow_database.json"
        
        # Calculate detailed statistics
        all_spines = set()
        all_diameters = []
        all_gpi_weights = []
        arrow_types = {}
        manufacturer_stats = {}
        
        for manufacturer, data in all_data.items():
            manufacturer_stats[manufacturer] = {
                "arrows_count": len(data.arrows),
                "expected_count": self.manufacturers[manufacturer]["total_expected"],
                "coverage": (len(data.arrows) / self.manufacturers[manufacturer]["total_expected"] * 100) if self.manufacturers[manufacturer]["total_expected"] else 0,
                "unique_models": len(set(arrow.model_name for arrow in data.arrows)),
                "spine_range": {
                    "min": min((min(arrow.spine_options) for arrow in data.arrows), default=0) if data.arrows else 0,
                    "max": max((max(arrow.spine_options) for arrow in data.arrows), default=0) if data.arrows else 0
                },
                "diameter_range": {
                    "min": min((arrow.diameter for arrow in data.arrows), default=0) if data.arrows else 0,
                    "max": max((arrow.diameter for arrow in data.arrows), default=0) if data.arrows else 0
                }
            }
            
            for arrow in data.arrows:
                all_spines.update(arrow.spine_options)
                all_diameters.append(arrow.diameter)
                all_gpi_weights.append(arrow.gpi_weight)
                arrow_type = str(arrow.arrow_type) if arrow.arrow_type else "unknown"
                arrow_types[arrow_type] = arrow_types.get(arrow_type, 0) + 1
        
        master_data = {
            "production_extraction": {
                "session_id": self.session_id,
                "extraction_date": datetime.now().isoformat(),
                "total_manufacturers": len(all_data),
                "total_arrows_extracted": total_arrows,
                "total_arrows_expected": self.total_expected_arrows,
                "overall_coverage_percentage": total_coverage,
                "extraction_success": "COMPLETE" if total_coverage > 80 else "PARTIAL"
            },
            "database_statistics": {
                "spine_values": {
                    "unique_count": len(all_spines),
                    "range": {
                        "min": min(all_spines) if all_spines else 0,
                        "max": max(all_spines) if all_spines else 0
                    },
                    "all_values": sorted(list(all_spines))
                },
                "diameter_analysis": {
                    "min": min(all_diameters) if all_diameters else 0,
                    "max": max(all_diameters) if all_diameters else 0,
                    "average": sum(all_diameters) / len(all_diameters) if all_diameters else 0
                },
                "gpi_analysis": {
                    "min": min(all_gpi_weights) if all_gpi_weights else 0,
                    "max": max(all_gpi_weights) if all_gpi_weights else 0,
                    "average": sum(all_gpi_weights) / len(all_gpi_weights) if all_gpi_weights else 0
                },
                "arrow_types_distribution": arrow_types
            },
            "manufacturer_statistics": manufacturer_stats,
            "complete_arrow_database": {
                manufacturer: [
                    {
                        "model": arrow.model_name,
                        "spines": arrow.spine_options,
                        "diameter": arrow.diameter,
                        "inner_diameter": arrow.inner_diameter,
                        "gpi": arrow.gpi_weight,
                        "lengths": arrow.length_options,
                        "type": str(arrow.arrow_type) if arrow.arrow_type else None,
                        "uses": arrow.recommended_use,
                        "description": arrow.description,
                        "url": arrow.source_url
                    }
                    for arrow in data.arrows
                ]
                for manufacturer, data in all_data.items()
            }
        }
        
        with open(master_file, 'w') as f:
            json.dump(master_data, f, indent=2, default=str)
        
        print(f"\n📋 MASTER DATABASE saved to: {master_file.name}")
        
        return master_data

async def main():
    """Main production extraction execution"""
    
    # Check for DeepSeek API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not found")
        print("Please set your DeepSeek API key:")
        print("export DEEPSEEK_API_KEY='your_api_key_here'")
        return
    
    print("🚀 STARTING PRODUCTION FULL SCALE EXTRACTION...")
    print("This will extract ALL arrow specifications from ALL manufacturers")
    print("Estimated time: 15-30 minutes depending on response times")
    
    # Create production scraper
    scraper = ProductionArrowScraper(api_key)
    
    # Run complete extraction
    all_data = await scraper.run_production_extraction()
    
    # Save comprehensive results
    master_data = scraper.save_production_results(all_data)
    
    # Final production report
    print("\n" + "=" * 80)
    print("🎉 PRODUCTION EXTRACTION COMPLETE!")
    print("=" * 80)
    
    extraction_stats = master_data["production_extraction"]
    database_stats = master_data["database_statistics"]
    
    print(f"✅ Total arrows extracted: {extraction_stats['total_arrows_extracted']}")
    print(f"✅ Target arrows: {extraction_stats['total_arrows_expected']}")
    print(f"✅ Overall coverage: {extraction_stats['overall_coverage_percentage']:.1f}%")
    print(f"✅ Extraction status: {extraction_stats['extraction_success']}")
    
    print(f"\n📊 DATABASE COMPOSITION:")
    print(f"   Manufacturers: {extraction_stats['total_manufacturers']}")
    print(f"   Unique spine values: {database_stats['spine_values']['unique_count']}")
    print(f"   Spine range: {database_stats['spine_values']['range']['min']}-{database_stats['spine_values']['range']['max']}")
    print(f"   Diameter range: {database_stats['diameter_analysis']['min']:.3f}\"-{database_stats['diameter_analysis']['max']:.3f}\"")
    print(f"   GPI range: {database_stats['gpi_analysis']['min']}-{database_stats['gpi_analysis']['max']}")
    
    print(f"\n🏭 MANUFACTURER BREAKDOWN:")
    for manufacturer, stats in master_data["manufacturer_statistics"].items():
        print(f"   {manufacturer}: {stats['arrows_count']}/{stats['expected_count']} ({stats['coverage']:.1f}%)")
    
    print(f"\n🎪 ARROW TYPE DISTRIBUTION:")
    for arrow_type, count in database_stats["arrow_types_distribution"].items():
        print(f"   {arrow_type}: {count} arrows")
    
    print(f"\n💾 All data saved to: data/production_extraction/")
    print(f"📄 Master database: complete_arrow_database.json")
    print(f"\n🎯 PHASE 1 (DATA SCRAPING & COLLECTION) - COMPLETE!")
    print(f"✅ Ready for Phase 2: Database Design & Implementation")

if __name__ == "__main__":
    asyncio.run(main())