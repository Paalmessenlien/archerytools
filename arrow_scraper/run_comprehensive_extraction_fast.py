#!/usr/bin/env python3
"""
Fast comprehensive extraction that:
1. Skips image downloads unless vision extraction is needed
2. Uses consistent manufacturer names from config
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from models import ArrowSpecification, SpineSpecification, ManufacturerData, ScrapingSession, ScrapingResult
from run_comprehensive_extraction import DirectLLMExtractor as OriginalExtractor

class FastDirectLLMExtractor(OriginalExtractor):
    """Optimized extractor that only downloads images for vision-based extraction"""
    
    def __init__(self, api_key: str, manufacturer_name: str = None, skip_images: bool = True):
        super().__init__(api_key)
        self.manufacturer_name = manufacturer_name  # Use consistent name from config
        self.skip_images = skip_images  # Skip image downloads by default
        
    def extract_arrow_data(self, content: str, url: str) -> List[ArrowSpecification]:
        """Extract arrow data with consistent manufacturer naming"""
        
        # Get arrows from parent implementation
        arrows = super().extract_arrow_data(content, url)
        
        # Override manufacturer name with config value if provided
        if self.manufacturer_name and arrows:
            for arrow in arrows:
                arrow.manufacturer = self.manufacturer_name
                print(f"✅ Using config manufacturer name: {self.manufacturer_name}")
        
        return arrows
    
    def download_image(self, image_url: str, manufacturer: str, model_name: str, image_type: str = "primary") -> str:
        """Download image and return local path, or just return URL if skipping"""
        if self.skip_images:
            # Return the URL instead of downloading
            return image_url
            
        # Original download logic
        return super().download_image(image_url, manufacturer, model_name, image_type)


# Update the main.py update_all_manufacturers function
async def update_all_manufacturers_fast(deepseek_api_key: str, force_update: bool = False, enable_translation: bool = True):
    """Fast update that skips unnecessary image downloads"""
    
    print("🚀 Starting FAST comprehensive manufacturer update...")
    print("⚡ Image downloads disabled for non-vision extraction")
    print("==" * 30)
    
    # Import necessary modules
    from config_loader import ConfigLoader
    from arrow_database import ArrowDatabase
    from easyocr_carbon_express_extractor import EasyOCRCarbonExpressExtractor
    from deepseek_knowledge_extractor import DeepSeekKnowledgeExtractor
    from deepseek_translator import DeepSeekTranslator
    
    try:
        config = ConfigLoader()
        database = ArrowDatabase()
    except Exception as e:
        print(f"❌ Failed to initialize systems: {e}")
        return False
    
    manufacturer_names = config.get_manufacturer_names()
    
    start_time = time.time()
    total_manufacturers = len(manufacturer_names)
    successful_updates = 0
    total_arrows_found = 0
    
    print(f"📊 Updating {total_manufacturers} manufacturers from config...")
    print(f"🔄 Force update: {'Yes' if force_update else 'No'}")
    print(f"🌍 Translation: {'Enabled' if enable_translation else 'Disabled'}")
    print()
    
    for i, manufacturer_name in enumerate(manufacturer_names, 1):
        print(f"[{i}/{total_manufacturers}] 🏹 Processing: {manufacturer_name}")
        print("-" * 40)
        
        try:
            # Check if manufacturer exists in database
            if not force_update:
                existing_count = database.get_arrows_by_manufacturer(manufacturer_name.lower())
                if existing_count and len(existing_count) > 0:
                    print(f"ℹ️  Found {len(existing_count)} existing arrows - skipping")
                    print("   Use --force to update existing data")
                    print()
                    continue
            
            # Get URLs for this manufacturer
            all_urls = config.get_manufacturer_urls(manufacturer_name)
            if not all_urls:
                print(f"⚠️  No URLs found for {manufacturer_name}")
                print()
                continue
                
            print(f"📊 Found {len(all_urls)} URLs to process")
            
            # Check if vision extraction is needed
            is_vision_based = config.is_vision_extraction(manufacturer_name)
            skip_images = not is_vision_based  # Only download images for vision-based extraction
            
            # Initialize extractors with manufacturer name
            text_extractor = FastDirectLLMExtractor(
                deepseek_api_key, 
                manufacturer_name=manufacturer_name,
                skip_images=skip_images
            )
            vision_extractor = None
            knowledge_extractor = DeepSeekKnowledgeExtractor(deepseek_api_key)
            translator = DeepSeekTranslator(deepseek_api_key)
            
            if is_vision_based:
                print(f"🤖 Vision extraction enabled - images WILL be downloaded")
            else:
                print(f"⚡ Text extraction only - images will NOT be downloaded")
            
            # Initialize vision extractor if needed
            if is_vision_based:
                print(f"🤖 Initializing vision extractor for {manufacturer_name}...")
                vision_extractor = EasyOCRCarbonExpressExtractor()
                if vision_extractor.reader:
                    print("✅ EasyOCR ready for image extraction")
                else:
                    print("⚠️  EasyOCR not available, falling back to text extraction")
                    vision_extractor = None
            
            manufacturer_arrows = []
            failed_urls = []
            
            # Process URLs
            async with AsyncWebCrawler(verbose=False) as crawler:
                for j, url in enumerate(all_urls, 1):
                    print(f"   📎 [{j}/{len(all_urls)}] Processing URL...", end="")
                    
                    try:
                        # Crawl the page
                        result = await crawler.arun(url=url, bypass_cache=True)
                        
                        if not result.success:
                            print(" ❌ Crawl failed")
                            failed_urls.append(url)
                            continue
                        
                        print(f" ✓ Crawled", end="")
                        
                        # Three-tier extraction system
                        arrows = []
                        
                        # Tier 1: Text extraction (with consistent manufacturer name)
                        arrows = text_extractor.extract_arrow_data(result.markdown, url)
                        
                        # Tier 2: Vision extraction (if available and needed)
                        if not arrows and vision_extractor:
                            print(" → 🖼️  Vision...", end="")
                            arrows = vision_extractor.extract_vision_based_data(
                                result.html, result.markdown, url
                            )
                            # Override manufacturer name for vision-extracted arrows
                            for arrow in arrows:
                                arrow.manufacturer = manufacturer_name
                        
                        # Tier 3: Knowledge base fallback
                        if not arrows:
                            print(" → 🧠 Knowledge...", end="")
                            arrows = knowledge_extractor.extract_from_failed_url(url, manufacturer_name)
                        
                        if arrows:
                            # Ensure all arrows have consistent manufacturer name
                            for arrow in arrows:
                                arrow.manufacturer = manufacturer_name
                            
                            # Translate arrows if needed
                            manufacturer_language = config.get_manufacturer_language(manufacturer_name)
                            if enable_translation and manufacturer_language and manufacturer_language != 'english':
                                print(f" → 🌍 Translating from {manufacturer_language}...", end="")
                                translated_arrows = []
                                for arrow in arrows:
                                    translated_arrow = translator.translate_arrow_data(arrow, manufacturer_language)
                                    # Ensure manufacturer name stays consistent after translation
                                    translated_arrow.manufacturer = manufacturer_name
                                    translated_arrows.append(translated_arrow)
                                arrows = translated_arrows
                                print(" ✅")
                            
                            manufacturer_arrows.extend(arrows)
                            print(f" → ✅ {len(arrows)} arrows")
                        else:
                            print(" → ❌ No data")
                            failed_urls.append(url)
                        
                        # Rate limiting
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        print(f" → 💥 Error: {str(e)[:30]}...")
                        failed_urls.append(url)
                        continue
            
            # Process results
            if manufacturer_arrows:
                arrow_count = len(manufacturer_arrows)
                total_arrows_found += arrow_count
                successful_updates += 1
                
                # Update database
                added_count = 0
                for arrow in manufacturer_arrows:
                    try:
                        database.add_arrow(arrow)
                        added_count += 1
                    except Exception as e:
                        print(f"⚠️  Database error for {arrow.model_name}: {e}")
                
                print(f"✅ {manufacturer_name}: {arrow_count} arrows extracted, {added_count} added to database")
                
                # Show unique models
                unique_models = set(arrow.model_name for arrow in manufacturer_arrows)
                print(f"   📋 Unique models: {len(unique_models)}")
                total_spines = sum(len(arrow.spine_specifications) for arrow in manufacturer_arrows)
                print(f"   🎯 Total spine specs: {total_spines}")
                
            else:
                print(f"❌ {manufacturer_name}: No arrows found")
                
            if failed_urls:
                print(f"   ⚠️  Failed URLs: {len(failed_urls)}/{len(all_urls)}")
            
            # Add delay between manufacturers
            if i < total_manufacturers:
                print("⏱️  Waiting 5 seconds...")
                await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Error processing {manufacturer_name}: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Summary
    duration = time.time() - start_time
    print("=" * 60)
    print("📋 FAST UPDATE SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"🏢 Manufacturers processed: {successful_updates}/{total_manufacturers}")
    print(f"🏹 Total arrows found: {total_arrows_found}")
    print(f"✅ Success rate: {(successful_updates/total_manufacturers*100):.1f}%")
    print(f"⚡ Speed improvement: Image downloads skipped for non-vision manufacturers")
    print()
    
    # Database summary
    try:
        stats = database.get_statistics()
        total_db_arrows = stats.get('total_arrows', 0)
        total_db_manufacturers = stats.get('total_manufacturers', 0)
        print(f"💾 Database now contains:")
        print(f"   • {total_db_arrows} arrows")
        print(f"   • {total_db_manufacturers} manufacturers")
    except Exception as e:
        print(f"💾 Database summary unavailable: {e}")
    print()
    
    if successful_updates > 0:
        print("🎯 Fast update completed successfully!")
        return True
    else:
        print("⚠️  No manufacturers were updated")
        return False


if __name__ == "__main__":
    # Test the fast extraction
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        sys.exit(1)
    
    # Run the fast update
    asyncio.run(update_all_manufacturers_fast(api_key, force_update=True))