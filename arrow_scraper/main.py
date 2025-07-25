#!/usr/bin/env python3
"""
Arrow Scraper Main Entry Point - Enhanced with Update All Functionality
Phase 1: Data Scraping & Collection for Arrow Database & Tuning Calculator
"""

import asyncio
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to the path so we can import from crawl4ai
sys.path.append(str(Path(__file__).parent.parent))

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from scrapers.easton_scraper import EastonScraper
from config.settings import MANUFACTURERS
from arrow_database import ArrowDatabase
from crawl4ai import AsyncWebCrawler
from config_loader import ConfigLoader
from run_comprehensive_extraction import DirectLLMExtractor
from easyocr_carbon_express_extractor import EasyOCRCarbonExpressExtractor
from deepseek_knowledge_extractor import DeepSeekKnowledgeExtractor

def load_environment():
    """Load environment variables"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        print("Warning: .env file not found. Please create one based on .env.example")
        print("You'll need to set DEEPSEEK_API_KEY")

async def scrape_manufacturer(manufacturer: str, deepseek_api_key: str):
    """Scrape arrows for a specific manufacturer"""
    
    if not deepseek_api_key:
        print("Error: DEEPSEEK_API_KEY not set. Please check your .env file.")
        return False
    
    if manufacturer.lower() == "easton":
        scraper = EastonScraper(deepseek_api_key)
        
        print(f"Starting Easton arrow scraping...")
        print(f"Session ID: {scraper.session_id}")
        
        try:
            # Scrape all Easton categories
            results = await scraper.scrape_all_easton_categories()
            
            # Save session data
            scraper.save_session_data()
            
            # Print summary
            total_arrows = sum(r.arrows_found for r in results)
            successful_scrapes = sum(1 for r in results if r.success)
            
            print(f"\nScraping Summary:")
            print(f"  Manufacturer: {manufacturer}")
            print(f"  URLs processed: {len(results)}")
            print(f"  Successful scrapes: {successful_scrapes}/{len(results)}")
            print(f"  Total arrows found: {total_arrows}")
            print(f"  Success rate: {(successful_scrapes/len(results)*100):.1f}%")
            
            return True
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return False
    
    else:
        print(f"Manufacturer '{manufacturer}' not yet implemented")
        print(f"Available manufacturers: {list(MANUFACTURERS.keys())}")
        return False

async def update_all_manufacturers(deepseek_api_key: str, force_update: bool = False):
    """Update all manufacturers in the database using the working architecture"""
    
    print("🚀 Starting comprehensive manufacturer update...")
    print("=" * 60)
    
    # Initialize systems using the working architecture
    try:
        config = ConfigLoader()
        database = ArrowDatabase()
    except Exception as e:
        print(f"❌ Failed to initialize systems: {e}")
        return False
    
    # Get all manufacturers from config
    manufacturer_names = config.get_manufacturer_names()
    
    start_time = time.time()
    total_manufacturers = len(manufacturer_names)
    successful_updates = 0
    total_arrows_found = 0
    
    print(f"📊 Updating {total_manufacturers} manufacturers from config...")
    print(f"🔄 Force update: {'Yes' if force_update else 'No'}")
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
            
            # Initialize extractors (same as working script)
            text_extractor = DirectLLMExtractor(deepseek_api_key)
            vision_extractor = None
            knowledge_extractor = DeepSeekKnowledgeExtractor(deepseek_api_key)
            
            # Initialize vision extractor if needed
            if config.is_vision_extraction(manufacturer_name):
                print(f"🤖 Initializing vision extractor for {manufacturer_name}...")
                vision_extractor = EasyOCRCarbonExpressExtractor()
                if vision_extractor.reader:
                    print("✅ EasyOCR ready for image extraction")
                else:
                    print("⚠️  EasyOCR not available, falling back to text extraction")
                    vision_extractor = None
            
            manufacturer_arrows = []
            failed_urls = []
            
            # Process URLs using the working three-tier extraction system
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
                        
                        # Three-tier extraction system (same as working script)
                        arrows = []
                        
                        # Tier 1: Text extraction
                        arrows = text_extractor.extract_arrow_data(result.markdown, url)
                        
                        # Tier 2: Vision extraction (if available and needed)
                        if not arrows and vision_extractor:
                            print(" → 🖼️  Vision...", end="")
                            arrows = vision_extractor.extract_vision_based_data(
                                result.html, result.markdown, url
                            )
                        
                        # Tier 3: Knowledge base fallback
                        if not arrows:
                            print(" → 🧠 Knowledge...", end="")
                            arrows = knowledge_extractor.extract_from_failed_url(url, manufacturer_name)
                        
                        if arrows:
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
            
            # Add delay between manufacturers to be respectful
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
    print("📋 UPDATE SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"🏢 Manufacturers processed: {successful_updates}/{total_manufacturers}")
    print(f"🏹 Total arrows found: {total_arrows_found}")
    print(f"✅ Success rate: {(successful_updates/total_manufacturers*100):.1f}%")
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
        print("🎯 Update completed successfully!")
        return True
    else:
        print("⚠️  No manufacturers were updated")
        return False

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Arrow Database Scraper with Update Capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py easton                    # Scrape Easton only
  python main.py --update-all             # Update all manufacturers
  python main.py --update-all --force     # Force update all manufacturers
  python main.py --list-manufacturers     # List available manufacturers
        """
    )
    
    parser.add_argument(
        "manufacturer", 
        nargs="?", 
        help="Manufacturer to scrape (e.g., easton, goldtip, victory)"
    )
    parser.add_argument(
        "--update-all", 
        action="store_true",
        help="Update all manufacturers in the database"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force update even if manufacturer data already exists"
    )
    parser.add_argument(
        "--list-manufacturers", 
        action="store_true",
        help="List available manufacturers"
    )
    
    args = parser.parse_args()
    
    if args.list_manufacturers:
        print("Available manufacturers:")
        for key, config in MANUFACTURERS.items():
            print(f"  {key}: {config['name']}")
        
        # Also show config-based manufacturers (the working ones)
        try:
            config = ConfigLoader()
            print("\nConfig-based manufacturers (used by --update-all):")
            for name in config.get_manufacturer_names():
                url_count = len(config.get_manufacturer_urls(name))
                method = config.get_extraction_method(name)
                language = config.get_manufacturer_language(name)
                
                extra_info = f"({method}"
                if language != 'english':
                    extra_info += f", {language}"
                extra_info += ")"
                
                print(f"  {name} {extra_info} - {url_count} URLs")
        except Exception as e:
            print(f"\nError loading config: {e}")
        return
    
    # Load environment
    load_environment()
    
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if args.update_all:
        # Update all manufacturers
        success = await update_all_manufacturers(deepseek_api_key, args.force)
    elif args.manufacturer:
        # Scrape single manufacturer
        success = await scrape_manufacturer(args.manufacturer, deepseek_api_key)
    else:
        print("Error: Please specify a manufacturer or use --update-all")
        print("Use --help for usage information")
        sys.exit(1)
    
    if success:
        print("\n🎉 Operation completed successfully!")
        print("Check the database and 'data/processed' directory for results.")
    else:
        print("\n❌ Operation failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())