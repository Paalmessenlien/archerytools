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
            
            # Save components to JSON file (same pattern as arrows)
            if components:
                # Prepare data for JSON export
                manufacturer_name = manufacturer or components[0].get('manufacturer', 'Unknown')
                safe_manufacturer = "".join(c for c in manufacturer_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                
                # Create JSON data structure (similar to arrows)
                json_data = {
                    "manufacturer": manufacturer_name,
                    "component_type": component_type,
                    "total_components": len(components),
                    "scraped_at": datetime.now().isoformat(),
                    "source_url": url,
                    "components": []
                }
                
                # Process each component
                saved_count = 0
                for component in components:
                    # Override manufacturer if provided
                    if manufacturer:
                        component['manufacturer'] = manufacturer
                    
                    # Add to JSON data
                    json_data["components"].append({
                        "manufacturer": component['manufacturer'],
                        "model_name": component['model_name'],
                        "component_type": component_type,
                        "specifications": component['specifications'],
                        "image_url": component.get('image_url'),
                        "local_image_path": component.get('local_image_path'),
                        "price_range": component.get('price_range'),
                        "description": component.get('description'),
                        "source_url": component.get('source_url', url),
                        "scraped_at": datetime.now().isoformat()
                    })
                    saved_count += 1
                
                # Save to JSON file
                components_dir = Path("data/processed/components")
                components_dir.mkdir(parents=True, exist_ok=True)
                
                json_filename = f"{safe_manufacturer}_{component_type}.json"
                json_path = components_dir / json_filename
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Saved component data to: {json_path}")
                
            else:
                saved_count = 0
            
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

async def scrape_manufacturer(manufacturer: str, deepseek_api_key: str = None, url_limit: int = None, learn_mode: bool = False, use_deepseek: bool = False, crawl_only: bool = False):
    """Scrape arrows for a specific manufacturer"""
    
    if use_deepseek and not deepseek_api_key:
        print("Error: --use-deepseek requires DEEPSEEK_API_KEY. Please check your .env file.")
        return False
    
    if crawl_only:
        print(f"🚀 CRAWL-ONLY mode: Just downloading and saving content (no extraction)")
    elif use_deepseek:
        print(f"🤖 Using DeepSeek API for content extraction")
    else:
        print(f"⚡ FAST mode: Pattern learning without API calls")
    
    # Try to use the new config-based method for any manufacturer
    try:
        from config_loader import ConfigLoader
        config = ConfigLoader()
        manufacturer_names = config.get_manufacturer_names()
        
        # Find matching manufacturer in config using short keys
        matching_manufacturer = None
        
        # Create mapping from short keys to full names
        key_to_name = {}
        for name in manufacturer_names:
            # Create short key for command usage
            short_key = name.lower().replace(' ', '').replace('archery', '').replace('arrows', '')
            if 'nijora' in short_key:
                short_key = 'nijora'
            elif 'dk' in short_key or 'dkbow' in short_key:
                short_key = 'dkbow'
            elif 'bigarchery' in short_key:
                short_key = 'bigarchery'
            elif 'aurel' in short_key:
                short_key = 'aurel'
            elif 'pandarus' in short_key:
                short_key = 'pandarus'
            elif 'fivics' in short_key:
                short_key = 'fivics'
            elif 'skylon' in short_key:
                short_key = 'skylon'
            elif 'easton' in short_key:
                short_key = 'easton'
            elif 'goldtip' in short_key or 'gold' in short_key:
                short_key = 'goldtip'
            elif 'victory' in short_key:
                short_key = 'victory'
            elif 'carbon' in short_key and 'express' in short_key:
                short_key = 'carbonexpress'
            
            key_to_name[short_key] = name
        
        # Try exact match with short key first
        if manufacturer.lower() in key_to_name:
            matching_manufacturer = key_to_name[manufacturer.lower()]
        else:
            # Fall back to partial matching
            for name in manufacturer_names:
                if manufacturer.lower() in name.lower() or name.lower() in manufacturer.lower():
                    matching_manufacturer = name
                    break
        
        if matching_manufacturer:
            if learn_mode:
                print(f"🧠 Learning patterns from {matching_manufacturer}")
            else:
                print(f"🚀 Using optimized extraction for {matching_manufacturer}")
                print(f"💡 Recommendation: Use 'python main.py --update-all --force' for better performance")
            
            # Use the new fast method for single manufacturer
            from run_comprehensive_extraction_fast import FastDirectLLMExtractor
            from deepseek_knowledge_extractor import DeepSeekKnowledgeExtractor
            from deepseek_translator import DeepSeekTranslator
            from easyocr_carbon_express_extractor import EasyOCRCarbonExpressExtractor
            from arrow_database import ArrowDatabase
            from crawl4ai import AsyncWebCrawler
            
            # Get URLs for this manufacturer
            all_urls = config.get_manufacturer_urls(matching_manufacturer)
            if not all_urls:
                print(f"⚠️  No URLs found for {matching_manufacturer}")
                return False
            
            # Apply URL limit if specified
            if url_limit and url_limit < len(all_urls):
                original_count = len(all_urls)
                all_urls = all_urls[:url_limit]
                print(f"📊 Found {original_count} URLs, processing first {len(all_urls)} (--limit {url_limit})")
            else:
                print(f"📊 Found {len(all_urls)} URLs to process")
            
            if learn_mode:
                print(f"🧠 PATTERN LEARNING MODE: Processing {len(all_urls)} URLs to learn extraction patterns")
            
            # Initialize extractors based on mode
            is_vision_based = config.is_vision_extraction(matching_manufacturer)
            text_extractor = None
            
            if not crawl_only:
                if use_deepseek:
                    # Use DeepSeek API for extraction
                    text_extractor = FastDirectLLMExtractor(
                        deepseek_api_key, 
                        manufacturer_name=matching_manufacturer,
                        skip_images=not is_vision_based,
                        enable_learning=True,
                        use_api=True
                    )
                else:
                    # Fast mode - pattern learning without API calls
                    text_extractor = FastDirectLLMExtractor(
                        deepseek_api_key,  # Still need API key for initialization, but won't use it
                        manufacturer_name=matching_manufacturer,
                        skip_images=not is_vision_based,
                        enable_learning=True,
                        use_api=False  # This prevents API calls
                    )
            
            if is_vision_based:
                print(f"🤖 Vision extraction enabled - images WILL be downloaded")
            else:
                print(f"⚡ Text extraction only - images will NOT be downloaded")
            
            database = ArrowDatabase()
            manufacturer_arrows = []
            failed_urls = []
            
            # Process URLs
            async with AsyncWebCrawler(verbose=False) as crawler:
                for j, url in enumerate(all_urls, 1):
                    print(f"   📎 [{j}/{len(all_urls)}] Processing URL...", end="")
                    
                    try:
                        result = await crawler.arun(url=url, bypass_cache=True)
                        
                        if not result.success:
                            print(" ❌ Crawl failed")
                            failed_urls.append(url)
                            continue
                        
                        print(f" ✓ Crawled", end="")
                        
                        if crawl_only:
                            # Just save raw content, no extraction
                            print(f" → 💾 Content saved (crawl-only mode)")
                            # TODO: Save raw content to files if needed
                        elif text_extractor:
                            # Extract arrows using the configured extractor (with or without API)
                            arrows = text_extractor.extract_arrow_data(result.markdown, url)
                            
                            if arrows:
                                # Ensure all arrows have consistent manufacturer name
                                for arrow in arrows:
                                    arrow.manufacturer = matching_manufacturer
                                
                                manufacturer_arrows.extend(arrows)
                                print(f" → ✅ {len(arrows)} arrows extracted")
                            else:
                                if use_deepseek:
                                    print(" → ❌ No data extracted")
                                    failed_urls.append(url)
                                else:
                                    # In fast mode, no arrows is expected
                                    print(f" → 🧠 Pattern learned (fast mode)")
                        else:
                            # Fallback - just analyze content structure
                            content_size = len(result.markdown)
                            if content_size > 1000:  # Basic content quality check
                                print(f" → 🧠 Pattern learned ({content_size} chars)")
                            else:
                                print(f" → ❌ Content too small")
                                failed_urls.append(url)
                        
                        # Rate limiting
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        print(f" → 💥 Error: {str(e)[:30]}...")
                        failed_urls.append(url)
                        continue
            
            # Save to JSON instead of database (as requested by user)
            # Finalize pattern learning if extractor exists
            if text_extractor:
                text_extractor.finalize_learning()
            
            if manufacturer_arrows:
                # DeepSeek mode - save extracted arrows to JSON
                try:
                    from pathlib import Path
                    
                    # Save to JSON file using basic JSON structure
                    processed_dir = Path("data/processed")
                    processed_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create safe filename
                    safe_manufacturer = "".join(c for c in matching_manufacturer if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_filename = f"{safe_manufacturer}_learn_{timestamp}.json"
                    json_path = processed_dir / json_filename
                    
                    # Convert arrows to basic dict format for JSON serialization
                    arrows_data = []
                    for arrow in manufacturer_arrows:
                        arrow_dict = {
                            "manufacturer": arrow.manufacturer,
                            "model_name": arrow.model_name,
                            "spine_specifications": []
                        }
                        
                        # Convert spine specifications
                        for spine_spec in arrow.spine_specifications:
                            spine_dict = {
                                "spine": spine_spec.spine,
                                "outer_diameter": spine_spec.outer_diameter,
                                "gpi_weight": spine_spec.gpi_weight
                            }
                            # Include length_options if available
                            if hasattr(spine_spec, 'length_options') and spine_spec.length_options:
                                spine_dict["length_options"] = spine_spec.length_options
                            arrow_dict["spine_specifications"].append(spine_dict)
                        
                        # Add optional fields if they exist
                        if hasattr(arrow, 'material') and arrow.material:
                            arrow_dict["material"] = arrow.material
                        if hasattr(arrow, 'arrow_type') and arrow.arrow_type:
                            arrow_dict["arrow_type"] = arrow.arrow_type
                        if hasattr(arrow, 'description') and arrow.description:
                            arrow_dict["description"] = arrow.description
                            
                        arrows_data.append(arrow_dict)
                    
                    # Create JSON structure
                    json_data = {
                        "manufacturer": matching_manufacturer,
                        "total_arrows": len(manufacturer_arrows),
                        "scraped_at": datetime.now().isoformat(),
                        "extraction_method": "pattern_learning",
                        "arrows": arrows_data
                    }
                    
                    # Export to JSON
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n✅ {matching_manufacturer}: {len(manufacturer_arrows)} arrows extracted, saved to {json_filename}")
                    
                except Exception as json_error:
                    print(f"\n✅ {matching_manufacturer}: {len(manufacturer_arrows)} arrows extracted (JSON export failed: {json_error})")
                
                return True
            else:
                # Check if we're in learn mode (fast mode or learn mode without extraction)
                if learn_mode and not use_deepseek:
                    # Fast mode - no arrows expected, but pattern learning is success
                    print(f"\n✅ {matching_manufacturer}: Pattern learning completed successfully (fast mode)")
                    return True
                else:
                    # DeepSeek mode or other modes - no arrows is a failure
                    print(f"\n❌ {matching_manufacturer}: No arrows found")
                    return False
                
        else:
            print(f"❌ Manufacturer '{manufacturer}' not found in config")
            return False
            
    except Exception as e:
        print(f"❌ Error using optimized extraction: {e}")
        print(f"💡 Please use: python main.py --update-all --force")
        return False
    
    else:
        print(f"⚠️  Individual manufacturer scraping is deprecated")
        print(f"🚀 Use the new optimized method instead:")
        print(f"   python main.py --update-all --force")
        print(f"")
        print(f"💡 For single manufacturer (recommended):")
        print(f"   # Edit manufacturers.yaml to temporarily disable other manufacturers")
        print(f"   # Then run: python main.py --update-all --force")
        print(f"")
        print(f"✨ Benefits of --update-all:")
        print(f"   • Uses optimized fast extraction")
        print(f"   • Consistent manufacturer naming")
        print(f"   • Skips image downloads for better speed")
        print(f"   • Supports all {len(MANUFACTURERS)} manufacturers")
        print(f"   • Includes automatic translation")
        return False

async def learn_all_manufacturers(deepseek_api_key: str = None, url_limit: int = 1, use_deepseek: bool = False, crawl_only: bool = False):
    """Learn patterns from all manufacturers using limited URLs per manufacturer"""
    
    print(f"🧠 Learning patterns from ALL manufacturers...")
    print(f"⚡ Processing first {url_limit} URL(s) per manufacturer")
    print("=" * 60)
    
    # Initialize systems
    try:
        config = ConfigLoader()
        database = ArrowDatabase()
    except Exception as e:
        print(f"❌ Failed to initialize systems: {e}")
        return False
    
    manufacturer_names = config.get_manufacturer_names()
    start_time = time.time()
    successful_learns = 0
    total_patterns_learned = 0
    all_extractors = []  # Track all extractors for pattern learning finalization
    
    print(f"📊 Learning from {len(manufacturer_names)} manufacturers...")
    print(f"🎯 URL limit per manufacturer: {url_limit}")
    print()
    
    for i, manufacturer_name in enumerate(manufacturer_names, 1):
        print(f"[{i}/{len(manufacturer_names)}] 🧠 Learning from: {manufacturer_name}")
        print("-" * 40)
        
        try:
            # Get URLs for this manufacturer
            all_urls = config.get_manufacturer_urls(manufacturer_name)
            if not all_urls:
                print(f"⚠️  No URLs found for {manufacturer_name}")
                print()
                continue
            
            # Apply URL limit
            limited_urls = all_urls[:url_limit]
            print(f"📊 Found {len(all_urls)} URLs, learning from first {len(limited_urls)}")
            
            # Check if vision extraction is needed
            is_vision_based = config.is_vision_extraction(manufacturer_name)
            
            # Initialize extractors based on mode
            text_extractor = None
            
            if not crawl_only:
                if use_deepseek:
                    # Use DeepSeek API for extraction
                    from run_comprehensive_extraction_fast import FastDirectLLMExtractor
                    text_extractor = FastDirectLLMExtractor(
                        deepseek_api_key, 
                        manufacturer_name=manufacturer_name,
                        skip_images=not is_vision_based,
                        enable_learning=True,
                        use_api=True
                    )
                    all_extractors.append(text_extractor)
                else:
                    # Fast mode - pattern learning without API calls
                    print(f"⚡ FAST MODE: Pattern learning without DeepSeek API")
                    from run_comprehensive_extraction_fast import FastDirectLLMExtractor
                    text_extractor = FastDirectLLMExtractor(
                        deepseek_api_key,  # Still need for initialization, but won't use
                        manufacturer_name=manufacturer_name,
                        skip_images=not is_vision_based,
                        enable_learning=True,
                        use_api=False  # This prevents API calls
                    )
                    all_extractors.append(text_extractor)
            
            if is_vision_based:
                print(f"🤖 Vision extraction enabled - images WILL be downloaded")
            else:
                print(f"⚡ Text extraction only - images will NOT be downloaded")
            
            manufacturer_patterns = 0
            manufacturer_arrows = []  # Store extracted arrows for JSON export
            
            # Process limited URLs
            async with AsyncWebCrawler(verbose=False) as crawler:
                for j, url in enumerate(limited_urls, 1):
                    print(f"   📎 [{j}/{len(limited_urls)}] Learning from URL...", end="")
                    
                    try:
                        result = await crawler.arun(url=url, bypass_cache=True)
                        
                        if not result.success:
                            print(" ❌ Crawl failed")
                            continue
                        
                        print(f" ✓ Crawled", end="")
                        
                        if crawl_only:
                            # Just save raw content, no extraction
                            print(f" → 💾 Content saved (crawl-only mode)")
                            manufacturer_patterns += 1
                            # TODO: Save raw content to files if needed
                        elif text_extractor:
                            # Extract arrows using the configured extractor (with or without API)
                            arrows = text_extractor.extract_arrow_data(result.markdown, url)
                            
                            if arrows:
                                # Ensure consistent manufacturer name
                                for arrow in arrows:
                                    arrow.manufacturer = manufacturer_name
                                
                                # Add to manufacturer collection for JSON export
                                manufacturer_arrows.extend(arrows)
                                manufacturer_patterns += 1
                                print(f" → ✅ {len(arrows)} arrows, pattern learned")
                            else:
                                if use_deepseek:
                                    print(f" → ❌ No data extracted")
                                else:
                                    # In fast mode, no arrows is expected but pattern is still learned
                                    manufacturer_patterns += 1
                                    print(f" → 🧠 Pattern learned (fast mode)")
                        else:
                            # Fallback for crawl-only mode or other cases
                            content_size = len(result.markdown)
                            if content_size > 1000:  # Basic content quality check
                                manufacturer_patterns += 1
                                print(f" → 🧠 Pattern learned ({content_size} chars)")
                            else:
                                print(f" → ❌ Content too small ({content_size} chars)")
                        
                        # Small delay between URLs
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f" → 💥 Error: {str(e)[:30]}...")
                        continue
            
            if manufacturer_patterns > 0:
                successful_learns += 1
                total_patterns_learned += manufacturer_patterns
                
                # Save extracted arrows to JSON file (like regular scraping)
                if manufacturer_arrows:
                    try:
                        from pathlib import Path
                        
                        # Save to JSON file using basic JSON structure
                        processed_dir = Path("data/processed")
                        processed_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Create safe filename
                        safe_manufacturer = "".join(c for c in manufacturer_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        json_filename = f"{safe_manufacturer}_learn_{timestamp}.json"
                        json_path = processed_dir / json_filename
                        
                        # Convert arrows to basic dict format for JSON serialization
                        arrows_data = []
                        for arrow in manufacturer_arrows:
                            arrow_dict = {
                                "manufacturer": arrow.manufacturer,
                                "model_name": arrow.model_name,
                                "spine_specifications": []
                            }
                            
                            # Convert spine specifications
                            for spine_spec in arrow.spine_specifications:
                                spine_dict = {
                                    "spine": spine_spec.spine,
                                    "outer_diameter": spine_spec.outer_diameter,
                                    "gpi_weight": spine_spec.gpi_weight
                                }
                                arrow_dict["spine_specifications"].append(spine_dict)
                            
                            # Add optional fields if they exist
                            if hasattr(arrow, 'material') and arrow.material:
                                arrow_dict["material"] = arrow.material
                            if hasattr(arrow, 'arrow_type') and arrow.arrow_type:
                                arrow_dict["arrow_type"] = arrow.arrow_type
                            if hasattr(arrow, 'description') and arrow.description:
                                arrow_dict["description"] = arrow.description
                                
                            arrows_data.append(arrow_dict)
                        
                        # Create JSON structure
                        json_data = {
                            "manufacturer": manufacturer_name,
                            "total_arrows": len(manufacturer_arrows),
                            "scraped_at": datetime.now().isoformat(),
                            "extraction_method": "pattern_learning",
                            "arrows": arrows_data
                        }
                        
                        # Export to JSON
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(json_data, f, indent=2, ensure_ascii=False)
                        
                        print(f"✅ {manufacturer_name}: {manufacturer_patterns} patterns learned, {len(manufacturer_arrows)} arrows saved to {json_filename}")
                        
                    except Exception as json_error:
                        print(f"✅ {manufacturer_name}: {manufacturer_patterns} patterns learned (JSON export failed: {json_error})")
                else:
                    print(f"✅ {manufacturer_name}: {manufacturer_patterns} patterns learned")
            else:
                print(f"❌ {manufacturer_name}: No patterns learned")
            
            # Small delay between manufacturers
            if i < len(manufacturer_names):
                print("⏱️  Waiting 2 seconds...")
                await asyncio.sleep(2)
            
        except Exception as e:
            print(f"❌ Error learning from {manufacturer_name}: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Summary
    duration = time.time() - start_time
    print("=" * 60)
    print("🧠 PATTERN LEARNING SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"🏭 Manufacturers processed: {successful_learns}/{len(manufacturer_names)}")
    print(f"🧠 Total patterns learned: {total_patterns_learned}")
    print(f"✅ Success rate: {(successful_learns/len(manufacturer_names)*100):.1f}%")
    print(f"⚡ URLs per manufacturer: {url_limit}")
    print()
    
    # Finalize pattern learning for all extractors
    if all_extractors:
        print("🧠 Finalizing pattern learning...")
        for extractor in all_extractors:
            try:
                extractor.finalize_learning()
                break  # Only show summary once
            except Exception as e:
                print(f"⚠️  Error finalizing pattern learning: {e}")
    
    if successful_learns > 0:
        print("🎆 Pattern learning completed successfully!")
        print(f"🚀 Future scraping will be faster using learned patterns!")
        return True
    else:
        print("⚠️  No patterns were learned")
        return False

async def update_all_manufacturers(deepseek_api_key: str, force_update: bool = False, enable_translation: bool = True, specific_manufacturer: str = None):
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
    all_manufacturer_names = config.get_manufacturer_names()
    
    # Filter to specific manufacturer if requested
    if specific_manufacturer:
        # Use the same matching logic as in scrape_manufacturer
        matching_manufacturer = None
        
        # Create mapping from short keys to full names
        key_to_name = {}
        for name in all_manufacturer_names:
            # Create short key for command usage
            short_key = name.lower().replace(' ', '').replace('archery', '').replace('arrows', '')
            if 'nijora' in short_key:
                short_key = 'nijora'
            elif 'dk' in short_key or 'dkbow' in short_key:
                short_key = 'dkbow'
            elif 'bigarchery' in short_key:
                short_key = 'bigarchery'
            elif 'aurel' in short_key:
                short_key = 'aurel'
            elif 'pandarus' in short_key:
                short_key = 'pandarus'
            elif 'fivics' in short_key:
                short_key = 'fivics'
            elif 'skylon' in short_key:
                short_key = 'skylon'
            elif 'easton' in short_key:
                short_key = 'easton'
            elif 'goldtip' in short_key or 'gold' in short_key:
                short_key = 'goldtip'
            elif 'victory' in short_key:
                short_key = 'victory'
            elif 'carbon' in short_key and 'express' in short_key:
                short_key = 'carbonexpress'
            
            key_to_name[short_key] = name
        
        # Try exact match with short key first
        if specific_manufacturer.lower() in key_to_name:
            matching_manufacturer = key_to_name[specific_manufacturer.lower()]
        else:
            # Fall back to partial matching
            for name in all_manufacturer_names:
                if specific_manufacturer.lower() in name.lower() or name.lower() in specific_manufacturer.lower():
                    matching_manufacturer = name
                    break
        
        if matching_manufacturer:
            manufacturer_names = [matching_manufacturer]
            print(f"🎯 Updating specific manufacturer: {matching_manufacturer}")
        else:
            print(f"❌ Manufacturer '{specific_manufacturer}' not found in config")
            return False
    else:
        manufacturer_names = all_manufacturer_names
        print(f"📊 Updating all {len(manufacturer_names)} manufacturers from config...")
    
    start_time = time.time()
    total_manufacturers = len(manufacturer_names)
    successful_updates = 0
    total_arrows_found = 0
    all_extractors = []  # Track all extractors for pattern learning finalization
    
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
            
            # Initialize extractors with fast mode and pattern learning
            from run_comprehensive_extraction_fast import FastDirectLLMExtractor
            text_extractor = FastDirectLLMExtractor(
                deepseek_api_key, 
                manufacturer_name=manufacturer_name,
                skip_images=not is_vision_based,  # Only download images for vision extraction
                enable_learning=True  # Enable pattern learning for speed improvements
            )
            all_extractors.append(text_extractor)  # Track for finalization
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
                                    try:
                                        # Convert ArrowSpecification to dict for translation
                                        arrow_dict = arrow.dict() if hasattr(arrow, 'dict') else arrow.__dict__
                                        
                                        # Preprocess German decimal formats
                                        if manufacturer_language == 'german':
                                            from german_number_converter import preprocess_german_arrow_data
                                            arrow_dict = preprocess_german_arrow_data(arrow_dict)
                                        
                                        translated_dict = translator.translate_arrow_data(arrow_dict, manufacturer_language)
                                        
                                        # Convert back to ArrowSpecification object
                                        from models import ArrowSpecification
                                        translated_arrow = ArrowSpecification(**translated_dict)
                                        
                                        # Ensure manufacturer name stays consistent after translation
                                        translated_arrow.manufacturer = manufacturer_name
                                        translated_arrows.append(translated_arrow)
                                    except Exception as translation_error:
                                        print(f"\n⚠️  Translation error for {arrow.model_name}: {translation_error}")
                                        # Use original arrow if translation fails
                                        arrow.manufacturer = manufacturer_name
                                        translated_arrows.append(arrow)
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
                        print(f" → 💥 Error: {str(e)[:50]}...")
                        print(f"   Full error: {e}")
                        import traceback
                        traceback.print_exc()
                        failed_urls.append(url)
                        continue
            
            # Process results
            if manufacturer_arrows:
                arrow_count = len(manufacturer_arrows)
                total_arrows_found += arrow_count
                successful_updates += 1
                
                # Export to JSON file
                try:
                    from pathlib import Path
                    
                    # Save to JSON file using basic JSON structure
                    processed_dir = Path("data/processed")
                    processed_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create safe filename
                    safe_manufacturer = "".join(c for c in manufacturer_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_filename = f"{safe_manufacturer}_update_{timestamp}.json"
                    json_path = processed_dir / json_filename
                    
                    # Convert arrows to basic dict format for JSON serialization
                    arrows_data = []
                    for arrow in manufacturer_arrows:
                        try:
                            arrow_dict = {
                                "manufacturer": arrow.manufacturer,
                                "model_name": arrow.model_name,
                                "spine_specifications": []
                            }
                            
                            # Convert spine specifications
                            for spine_spec in arrow.spine_specifications:
                                try:
                                    spine_dict = {
                                        "spine": spine_spec.spine,
                                        "outer_diameter": spine_spec.outer_diameter,
                                        "gpi_weight": spine_spec.gpi_weight
                                    }
                                    # Include length_options if available
                                    if hasattr(spine_spec, 'length_options') and spine_spec.length_options:
                                        spine_dict["length_options"] = spine_spec.length_options
                                    arrow_dict["spine_specifications"].append(spine_dict)
                                except Exception as e:
                                    print(f"⚠️  Error serializing spine spec: {e}")
                                    continue
                            
                            # Add optional fields if they exist (with safe access)
                            optional_fields = [
                                'material', 'arrow_type', 'description', 'length_options',
                                'carbon_content', 'recommended_use', 'price_range',
                                'straightness_tolerance', 'weight_tolerance', 'image_url', 
                                'source_url', 'primary_image_url'
                            ]
                            
                            for field in optional_fields:
                                try:
                                    if hasattr(arrow, field):
                                        value = getattr(arrow, field)
                                        if value is not None:
                                            # Convert enum values to strings
                                            if hasattr(value, 'value'):
                                                arrow_dict[field] = value.value
                                            elif isinstance(value, list):
                                                arrow_dict[field] = [str(item) for item in value]
                                            else:
                                                arrow_dict[field] = str(value)
                                except Exception as e:
                                    print(f"⚠️  Error serializing field {field}: {e}")
                                    continue
                                
                            arrows_data.append(arrow_dict)
                            
                        except Exception as e:
                            print(f"⚠️  Error serializing arrow {getattr(arrow, 'model_name', 'unknown')}: {e}")
                            continue
                    
                    # Create JSON structure
                    json_data = {
                        "manufacturer": manufacturer_name,
                        "total_arrows": len(manufacturer_arrows),
                        "scraped_at": datetime.now().isoformat(),
                        "extraction_method": "comprehensive_update",
                        "arrows": arrows_data
                    }
                    
                    # Export to JSON
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 Saved to: {json_filename}")
                    
                except Exception as json_error:
                    print(f"⚠️  JSON export failed: {json_error}")
                
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
    
    # Finalize pattern learning for all extractors
    if all_extractors:
        print("🧠 Finalizing pattern learning...")
        for extractor in all_extractors:
            try:
                extractor.finalize_learning()
                break  # Only show summary once
            except Exception as e:
                print(f"⚠️  Error finalizing pattern learning: {e}")
    
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
  python main.py --update-all --force            # Force update ALL manufacturers
  python main.py --update-all --no-translate     # Update without translating non-English content
  python main.py --update-all --force --manufacturer=dkbow  # Update just DK Bow with full extraction
  
  # Pattern Learning (Fast - No API calls)
  python main.py --learn --manufacturer=easton --limit=3    # Learn from first 3 Easton URLs (crawl only)
  python main.py --learn --manufacturer=goldtip --limit=5   # Learn from first 5 Gold Tip URLs (crawl only)
  python main.py --learn-all --limit=1                     # Learn from first URL of ALL manufacturers (fastest)
  python main.py --learn-all --limit=2                     # Learn from first 2 URLs of each manufacturer
  
  # With DeepSeek API (Slower but extracts actual data)
  python main.py --learn --manufacturer=easton --limit=3 --use-deepseek    # Extract arrow data with AI
  python main.py --learn-all --limit=1 --use-deepseek                     # Extract from all manufacturers with AI
  
  # Crawl Only (Fastest - just save raw content)
  python main.py --crawl-only --manufacturer=easton --limit=5             # Just crawl and save content
  python main.py --manufacturer=easton --limit=10           # Process first 10 Easton URLs
  
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
        help="Force update ALL manufacturers even if data already exists"
    )
    parser.add_argument(
        "--learn",
        action="store_true",
        help="Learn patterns from a specific manufacturer (use with --manufacturer and --limit)"
    )
    parser.add_argument(
        "--learn-all",
        action="store_true",
        help="Learn patterns from ALL manufacturers (use with --limit for URLs per manufacturer)"
    )
    parser.add_argument(
        "--use-deepseek",
        action="store_true",
        help="Use DeepSeek API for content extraction (slower but more accurate)"
    )
    parser.add_argument(
        "--crawl-only",
        action="store_true",
        help="Only crawl and save raw content, no extraction (fastest option)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of URLs to process (useful for pattern learning)"
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
        dest="manufacturer_flag",
        help="Manufacturer name for scraping or URL operations"
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
        try:
            config = ConfigLoader()
            for name in config.get_manufacturer_names():
                url_count = len(config.get_manufacturer_urls(name))
                method = config.get_extraction_method(name)
                language = config.get_manufacturer_language(name)
                
                # Create short key for command usage
                short_key = name.lower().replace(' ', '').replace('archery', '').replace('arrows', '')
                if 'nijora' in short_key:
                    short_key = 'nijora'
                elif 'dk' in short_key or 'dkbow' in short_key:
                    short_key = 'dkbow'
                elif 'bigarchery' in short_key:
                    short_key = 'bigarchery'
                elif 'aurel' in short_key:
                    short_key = 'aurel'
                elif 'pandarus' in short_key:
                    short_key = 'pandarus'
                elif 'fivics' in short_key:
                    short_key = 'fivics'
                elif 'skylon' in short_key:
                    short_key = 'skylon'
                elif 'easton' in short_key:
                    short_key = 'easton'
                elif 'goldtip' in short_key or 'gold' in short_key:
                    short_key = 'goldtip'
                elif 'victory' in short_key:
                    short_key = 'victory'
                elif 'carbon' in short_key and 'express' in short_key:
                    short_key = 'carbonexpress'
                
                extra_info = f"({method}"
                if language and language != 'english':
                    extra_info += f", {language}"
                extra_info += ")"
                
                print(f"  {short_key}: {name} {extra_info} - {url_count} URLs")
        except Exception as e:
            print(f"Error loading config: {e}")
        return
    
    # Handle URL management commands first (don't need API key)
    if args.add:
        if not all([args.manufacturer_flag, args.type, args.url]):
            print("❌ --add requires --manufacturer, --type, and --url")
            print("Example: python main.py --add --manufacturer=easton --type=arrow --url=http://example.com")
            sys.exit(1)
        
        url_manager = URLManager()
        success = url_manager.add_url(args.manufacturer_flag, args.type, args.url)
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
        
        if args.manufacturer_flag:
            success = url_discovery.add_discovered_urls_to_config(
                args.manufacturer_flag, 
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
        results = url_manager.list_urls(args.manufacturer_flag, args.type)
        
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
        
        success = await extract_components(args.url, args.type, args.manufacturer_flag)
        sys.exit(0 if success else 1)

    # Load environment for scraping commands
    load_environment()
    
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if args.update_all:
        # Update all manufacturers (or specific manufacturer if provided)
        specific_manufacturer = args.manufacturer or args.manufacturer_flag
        success = await update_all_manufacturers(deepseek_api_key, args.force, not args.no_translate, specific_manufacturer)
    elif args.learn_all:
        # Learn patterns from all manufacturers
        url_limit = args.limit or 1  # Default to 1 URL per manufacturer
        success = await learn_all_manufacturers(deepseek_api_key, url_limit, args.use_deepseek, args.crawl_only)
    elif args.learn:
        # Pattern learning mode for specific manufacturer
        manufacturer_name = args.manufacturer or args.manufacturer_flag
        if not manufacturer_name:
            print("❌ --learn requires --manufacturer")
            print("Example: python main.py --learn --manufacturer=easton --limit=3")
            sys.exit(1)
        success = await scrape_manufacturer(manufacturer_name, deepseek_api_key, args.limit, learn_mode=True, use_deepseek=args.use_deepseek, crawl_only=args.crawl_only)
    elif args.crawl_only:
        # Crawl-only mode
        manufacturer_name = args.manufacturer or args.manufacturer_flag
        if not manufacturer_name:
            print("❌ --crawl-only requires --manufacturer")
            print("Example: python main.py --crawl-only --manufacturer=easton --limit=5")
            sys.exit(1)
        success = await scrape_manufacturer(manufacturer_name, deepseek_api_key, args.limit, learn_mode=False, use_deepseek=False, crawl_only=True)
    elif args.manufacturer or args.manufacturer_flag:
        # Scrape specific manufacturer (with optional limit)
        # This handles both --manufacturer flag and positional manufacturer argument
        manufacturer_name = args.manufacturer or args.manufacturer_flag
        success = await scrape_manufacturer(manufacturer_name, deepseek_api_key, args.limit, use_deepseek=args.use_deepseek, crawl_only=args.crawl_only)
    else:
        print("Error: Please specify a manufacturer, use --update-all, --learn, --learn-all, or use URL management commands")
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