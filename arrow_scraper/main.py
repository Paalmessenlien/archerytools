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
from deepseek_translator import DeepSeekTranslator
from url_manager import URLManager
from url_discovery import URLDiscovery
from component_extractors import ComponentExtractorFactory
from component_database import ComponentDatabase

def load_environment():
    """Load environment variables"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        print("Warning: .env file not found. Please create one based on .env.example")
        print("You'll need to set DEEPSEEK_API_KEY")

async def extract_components(url: str, component_type: str, manufacturer: str = None):
    """Extract components from a URL"""
    try:
        print(f"🧩 Extracting {component_type} components from: {url}")
        
        # Get the appropriate extractor
        extractor = ComponentExtractorFactory.get_extractor(component_type)
        if not extractor:
            print(f"❌ No extractor available for component type: {component_type}")
            print(f"Available types: {ComponentExtractorFactory.get_available_types()}")
            return False
        
        # Crawl the page
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            if not result.success:
                print(f"❌ Failed to crawl {url}: {result.error_message}")
                return False
            
            # Extract components using the specialized extractor
            components = extractor.extract_component_data(result.html, url)
            
            if not components:
                print(f"⚠️  No {component_type} found on the page")
                return False
            
            # Initialize component database
            component_db = ComponentDatabase()
            
            # Save components to database
            saved_count = 0
            for component in components:
                # Override manufacturer if provided
                if manufacturer:
                    component['manufacturer'] = manufacturer
                
                component_id = component_db.add_component(
                    category_name=component_type,
                    manufacturer=component['manufacturer'],
                    model_name=component['model_name'],
                    specifications=component['specifications'],
                    image_url=component.get('image_url'),
                    local_image_path=component.get('local_image_path'),
                    price_range=component.get('price_range'),
                    description=component.get('description'),
                    source_url=component.get('source_url', url),
                    scraped_at=datetime.now().isoformat()
                )
                
                if component_id:
                    saved_count += 1
            
            print(f"✅ Extracted and saved {saved_count}/{len(components)} {component_type}")
            
            # Show sample extracted data
            print(f"\n📦 Sample {component_type}:")
            for i, component in enumerate(components[:3]):
                print(f"  {i+1}. {component['manufacturer']} {component['model_name']}")
                specs = component['specifications']
                for key, value in list(specs.items())[:3]:  # Show first 3 specs
                    print(f"     {key}: {value}")
                if i < len(components) - 1:
                    print()
            
            return saved_count > 0
            
    except Exception as e:
        print(f"❌ Error extracting components: {e}")
        import traceback
        traceback.print_exc()
        return False

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
        print(f"Manufacturer '{manufacturer}' not yet implemented for individual scraping")
        print(f"Available for individual scraping: ['easton']")
        print(f"Use --update-all to scrape all {len(MANUFACTURERS)} configured manufacturers with translation support")
        return False

async def update_all_manufacturers(deepseek_api_key: str, force_update: bool = False, enable_translation: bool = True):
    """Update all manufacturers in the database using the working architecture"""
    
    print("🚀 Starting comprehensive manufacturer update...")
    print("⚡ FAST MODE: Skipping image downloads for non-vision manufacturers")
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
            
            # Initialize extractors with fast mode
            from run_comprehensive_extraction_fast import FastDirectLLMExtractor
            text_extractor = FastDirectLLMExtractor(
                deepseek_api_key, 
                manufacturer_name=manufacturer_name,
                skip_images=not is_vision_based  # Only download images for vision extraction
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
                            # Translate arrows if not in English and translation enabled
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
  # Scraping
  python main.py easton                           # Scrape Easton only
  python main.py --update-all                    # Update all manufacturers (with translation)
  python main.py --update-all --force            # Force update all manufacturers
  python main.py --update-all --no-translate     # Update without translating non-English content
  
  # URL Management
  python main.py --add --manufacturer=easton --type=arrow --url=http://example.com
  python main.py --add-list --manufacturer=easton --type=components --url=http://example.com
  python main.py --list-urls --manufacturer=easton --type=arrow
  python main.py --list-manufacturers            # List available manufacturers with languages
  
  # Component Extraction
  python main.py --extract-components --type=points --url=http://example.com --manufacturer=easton
  python main.py --extract-components --type=nocks --url=http://example.com
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
    parser.add_argument(
        "--no-translate",
        action="store_true", 
        help="Disable automatic translation of non-English content"
    )
    parser.add_argument(
        "--add",
        action="store_true",
        help="Add URL to manufacturer configuration"
    )
    parser.add_argument(
        "--add-list", 
        action="store_true",
        help="Discover and add URLs from a page"
    )
    parser.add_argument(
        "--list-urls",
        action="store_true",
        help="List URLs in configuration"
    )
    parser.add_argument(
        "--manufacturer",
        help="Manufacturer name for URL operations"
    )
    parser.add_argument(
        "--type", 
        help="URL content type (arrow, components, points, nocks, etc.)"
    )
    parser.add_argument(
        "--url",
        help="URL to add or discover from"
    )
    parser.add_argument(
        "--auto-add",
        action="store_true",
        help="Automatically add discovered URLs without prompting"
    )
    parser.add_argument(
        "--max-urls",
        type=int,
        default=50,
        help="Maximum URLs to discover (default: 50)"
    )
    parser.add_argument(
        "--extract-components",
        action="store_true",
        help="Extract components from a URL (requires --type and --url)"
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
    
    # Handle URL management commands first (don't need API key)
    if args.add:
        if not all([args.manufacturer, args.type, args.url]):
            print("❌ --add requires --manufacturer, --type, and --url")
            print("Example: python main.py --add --manufacturer=easton --type=arrow --url=http://example.com")
            sys.exit(1)
        
        url_manager = URLManager()
        success = url_manager.add_url(args.manufacturer, args.type, args.url)
        sys.exit(0 if success else 1)
    
    elif args.add_list:
        if not all([args.url]):
            print("❌ --add-list requires --url")
            print("Example: python main.py --add-list --url=http://example.com --manufacturer=easton --type=components")
            sys.exit(1)
        
        url_discovery = URLDiscovery()
        discovered = url_discovery.discover_urls(
            args.url, 
            args.type or 'auto',
            max_urls=args.max_urls
        )
        
        # Validate discovered URLs
        discovered = url_discovery.validate_discovered_urls(discovered)
        
        if args.manufacturer:
            success = url_discovery.add_discovered_urls_to_config(
                args.manufacturer, 
                discovered, 
                args.auto_add
            )
            sys.exit(0 if success else 1)
        else:
            print(f"\n📊 Discovery Results:")
            total = sum(len(urls) for urls in discovered.values())
            print(f"Total URLs discovered: {total}")
            
            for category, urls in discovered.items():
                if urls:
                    print(f"\n{category.upper()} ({len(urls)} URLs):")
                    for url in urls[:5]:  # Show first 5
                        print(f"  • {url}")
                    if len(urls) > 5:
                        print(f"  ... and {len(urls) - 5} more")
            sys.exit(0)
    
    elif args.list_urls:
        url_manager = URLManager()
        results = url_manager.list_urls(args.manufacturer, args.type)
        
        if not results:
            print("❌ No URLs found matching criteria")
            sys.exit(1)
        
        print("📋 URL Configuration:")
        print("=" * 60)
        
        for mfr_name, mfr_data in results.items():
            print(f"\n🏭 {mfr_name}")
            print(f"   Language: {mfr_data['language']}")
            print(f"   Method: {mfr_data['extraction_method']}")
            print(f"   Total URLs: {mfr_data['total_urls']}")
            
            for url_data in mfr_data['filtered_urls']:
                print(f"   • [{url_data['type']}] {url_data['url']}")
                print(f"     Added: {url_data['added_at']}")
        sys.exit(0)
    
    # Handle component extraction command
    if args.extract_components:
        if not all([args.type, args.url]):
            print("❌ --extract-components requires --type and --url")
            print("Example: python main.py --extract-components --type=points --url=http://example.com --manufacturer=easton")
            print(f"Available component types: {ComponentExtractorFactory.get_available_types()}")
            sys.exit(1)
        
        success = await extract_components(args.url, args.type, args.manufacturer)
        sys.exit(0 if success else 1)

    # Load environment for scraping commands
    load_environment()
    
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if args.update_all:
        # Update all manufacturers
        success = await update_all_manufacturers(deepseek_api_key, args.force, not args.no_translate)
    elif args.manufacturer:
        # Scrape single manufacturer
        success = await scrape_manufacturer(args.manufacturer, deepseek_api_key)
    else:
        print("Error: Please specify a manufacturer, use --update-all, or use URL management commands")
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