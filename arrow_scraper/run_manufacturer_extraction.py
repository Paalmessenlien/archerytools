#!/usr/bin/env python3
"""
Run extraction for a specific manufacturer with command line options
Usage: python run_manufacturer_extraction.py [manufacturer_name] [batch_size] [start_index]

Examples:
python run_manufacturer_extraction.py "Easton Archery"
python run_manufacturer_extraction.py "Gold Tip" 10
python run_manufacturer_extraction.py "Victory Archery" 15 5
python run_manufacturer_extraction.py --list  # List available manufacturers
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import requests
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass

# Handle optional imports gracefully
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("⚠️  crawl4ai not available - web crawling disabled")

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from models import ArrowSpecification, SpineSpecification
from run_comprehensive_extraction import DirectLLMExtractor
from easyocr_carbon_express_extractor import EasyOCRCarbonExpressExtractor
from deepseek_knowledge_extractor import DeepSeekKnowledgeExtractor
from config_loader import ConfigLoader

def get_processed_urls(manufacturer: str) -> set:
    """Get set of URLs already processed for a manufacturer"""
    processed_urls = set()
    
    # Look for existing extraction files
    processed_dir = Path("data/processed")
    if processed_dir.exists():
        safe_manufacturer = "".join(c for c in manufacturer if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
        
        for file_path in processed_dir.glob(f"{safe_manufacturer}_*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Extract URLs from arrows
                for arrow in data.get('arrows', []):
                    source_url = arrow.get('source_url')
                    if source_url:
                        processed_urls.add(source_url)
                        
                # Also check failed URLs
                for failed in data.get('failed_urls', []):
                    failed_url = failed.get('url')
                    if failed_url:
                        processed_urls.add(failed_url)
                        
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                continue
    
    return processed_urls

def list_manufacturers():
    """List all available manufacturers"""
    try:
        config = ConfigLoader()
        
        print("📋 Available Manufacturers:")
        print("=" * 40)
        for manufacturer in config.get_manufacturer_names():
            url_count = len(config.get_manufacturer_urls(manufacturer))
            processed_count = len(get_processed_urls(manufacturer))
            new_count = url_count - processed_count
            
            method = config.get_extraction_method(manufacturer)
            language = config.get_manufacturer_language(manufacturer)
            
            extra_info = f"({method}"
            if language != 'english':
                extra_info += f", {language}"
            extra_info += ")"
            
            print(f"• {manufacturer} {extra_info} - {url_count} URLs total, {processed_count} processed, {new_count} new")
        print("\nUsage: python run_manufacturer_extraction.py \"Manufacturer Name\"")
        print("       python run_manufacturer_extraction.py \"Manufacturer Name\" --update")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")

async def run_manufacturer_extraction(manufacturer_name: str, batch_size: int = None, start_index: int = 0, update_mode: bool = False):
    """Run extraction for a specific manufacturer"""
    mode_text = "UPDATE" if update_mode else "EXTRACTION"
    print(f"🚀 Running {mode_text} for: {manufacturer_name}")
    print("=" * 60)
    
    # Check if crawling is available
    if not CRAWL4AI_AVAILABLE:
        print("❌ Web crawling not available - crawl4ai package required")
        print("   Install with: pip install crawl4ai")
        return 0
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    # Load manufacturer data from config
    try:
        config = ConfigLoader()
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return
    
    # Find matching manufacturer (case-insensitive partial matching)
    matched_manufacturer = config.find_manufacturer_by_partial_name(manufacturer_name)
    
    if not matched_manufacturer:
        print(f"❌ Manufacturer '{manufacturer_name}' not found")
        print("\nAvailable manufacturers:")
        for mfr_name in config.get_manufacturer_names():
            print(f"  • {mfr_name}")
        return
    
    # Get URLs for this manufacturer
    all_urls = config.get_manufacturer_urls(matched_manufacturer)
    manufacturer_data = config.get_manufacturer(matched_manufacturer)
    
    if not all_urls:
        print(f"❌ No URLs found for {matched_manufacturer}")
        return
    
    # Filter URLs based on mode
    if update_mode:
        # In update mode, only process new URLs
        processed_urls = get_processed_urls(matched_manufacturer)
        new_urls = [url for url in all_urls if url not in processed_urls]
        
        print(f"📊 Update Mode Analysis:")
        print(f"   Total URLs available: {len(all_urls)}")
        print(f"   Previously processed: {len(processed_urls)}")
        print(f"   New URLs to process: {len(new_urls)}")
        
        if not new_urls:
            print(f"✅ No new URLs found for {matched_manufacturer} - all up to date!")
            return 0
        
        urls = new_urls
        start_index = 0  # Reset start index for new URLs only
    else:
        # In normal mode, use all URLs
        urls = all_urls
    
    # Apply batch size and start index
    if batch_size is None:
        batch_size = len(urls)  # Process all URLs if not specified
    
    end_index = min(start_index + batch_size, len(urls))
    urls_to_process = urls[start_index:end_index]
    
    print(f"🏭 Manufacturer: {matched_manufacturer}")
    print(f"📊 Total URLs available: {len(urls)}")
    print(f"📦 Processing URLs {start_index} to {end_index-1} ({len(urls_to_process)} URLs)")
    print(f"🔗 Base URL: {manufacturer_data.get('base_url', 'N/A')}")
    print(f"🛠️  Extraction Method: {config.get_extraction_method(matched_manufacturer)}")
    
    language = config.get_manufacturer_language(matched_manufacturer)
    if language != 'english':
        print(f"🌐 Language: {language}")
    
    # Initialize extractors
    text_extractor = DirectLLMExtractor(api_key)
    vision_extractor = None
    knowledge_extractor = DeepSeekKnowledgeExtractor(api_key)
    
    # Initialize vision extractor based on config
    if config.is_vision_extraction(matched_manufacturer):
        print(f"🤖 Initializing {config.get_extraction_method(matched_manufacturer)} extractor for {matched_manufacturer}...")
        vision_extractor = EasyOCRCarbonExpressExtractor()
        if vision_extractor.reader:
            print("✅ EasyOCR ready for image extraction")
        else:
            print("⚠️  EasyOCR not available, falling back to text extraction")
            vision_extractor = None
    
    # Check if knowledge extractor can help with this manufacturer
    if knowledge_extractor.can_help_with_manufacturer(matched_manufacturer):
        print(f"🧠 DeepSeek knowledge extractor available for {matched_manufacturer}")
    else:
        print(f"ℹ️  DeepSeek knowledge extractor may have limited data for {matched_manufacturer}")
    
    all_arrows = []
    failed_urls = []
    stats = {"processed": 0, "successful": 0, "arrows": 0}
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        for i, url in enumerate(urls_to_process, 1):
            print(f"\n🔗 [{start_index + i}/{end_index}] {url.split('/')[-2] if '/' in url else url}")
            
            stats["processed"] += 1
            
            try:
                # Crawl the page
                result = await crawler.arun(url=url, bypass_cache=True)
                
                if not result.success:
                    print(f"❌ Failed to crawl")
                    failed_urls.append((url, matched_manufacturer, "Crawl failed"))
                    continue
                
                print(f"✓ Crawled ({len(result.markdown)} chars)", end="")
                
                # Extract arrow data using three-tier extraction system
                arrows = []
                
                # Tier 1: Try text extraction first
                arrows = text_extractor.extract_arrow_data(result.markdown, url)
                
                # Tier 2: If no results and we have vision extractor, try image extraction
                if not arrows and vision_extractor:
                    print(" → 🖼️  Trying image extraction...", end="")
                    arrows = vision_extractor.extract_vision_based_data(
                        result.html, result.markdown, url
                    )
                
                # Tier 3: If still no results, try DeepSeek knowledge base as fallback
                if not arrows:
                    print(" → 🧠 Trying DeepSeek knowledge base...", end="")
                    arrows = knowledge_extractor.extract_from_failed_url(url, matched_manufacturer)
                
                if arrows:
                    stats["successful"] += 1
                    stats["arrows"] += len(arrows)
                    total_spine_specs = sum(len(arrow.spine_specifications) for arrow in arrows)
                    print(f" → 🎯 {len(arrows)} arrows, {total_spine_specs} spine specs")
                    
                    for arrow in arrows:
                        print(f"      📋 {arrow.model_name}: {len(arrow.spine_specifications)} spine options")
                    
                    all_arrows.extend(arrows)
                else:
                    print(f" → ❌ No data")
                    failed_urls.append((url, matched_manufacturer, "No data extracted"))
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f" → 💥 Error: {str(e)[:50]}...")
                failed_urls.append((url, matched_manufacturer, str(e)))
                continue
    
    # Save results
    if all_arrows or failed_urls:
        # Create safe filename
        safe_manufacturer = "".join(c for c in matched_manufacturer if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
        
        # Generate filename based on mode
        if update_mode and all_arrows:
            # For updates, include timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(f"data/processed/{safe_manufacturer}_update_{timestamp}.json")
        else:
            # For normal mode, use range-based naming
            output_file = Path(f"data/processed/{safe_manufacturer}_{start_index:03d}_{end_index:03d}.json")
        
        output_data = {
            "extraction_timestamp": datetime.now().isoformat(),
            "manufacturer": matched_manufacturer,
            "extraction_mode": "update" if update_mode else "full",
            "extraction_range": {
                "start_index": start_index,
                "end_index": end_index,
                "total_urls_available": len(all_urls) if update_mode else len(urls),
                "urls_processed": len(urls_to_process),
                "new_urls_only": update_mode
            },
            "statistics": stats,
            "success_rate": (stats["successful"] / stats["processed"] * 100) if stats["processed"] > 0 else 0,
            "total_arrows": len(all_arrows),
            "total_spine_specs": sum(len(arrow.spine_specifications) for arrow in all_arrows),
            "arrows": [arrow.model_dump(mode='json') for arrow in all_arrows],
            "failed_urls": [{"url": url, "manufacturer": mfr, "reason": reason} for url, mfr, reason in failed_urls]
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"📊 EXTRACTION SUMMARY: {matched_manufacturer}")
        print(f"{'='*60}")
        print(f"💾 Results saved to: {output_file}")
        
        print(f"\n🎯 RESULTS:")
        print(f"   URLs processed: {stats['processed']}")
        print(f"   Successful extractions: {stats['successful']}")
        print(f"   Failed extractions: {len(failed_urls)}")
        print(f"   Success rate: {(stats['successful'] / stats['processed'] * 100):.1f}%")
        print(f"   Total arrows: {len(all_arrows)}")
        print(f"   Total spine specifications: {sum(len(arrow.spine_specifications) for arrow in all_arrows)}")
        
        if all_arrows:
            # Show unique models
            unique_models = set(arrow.model_name for arrow in all_arrows)
            print(f"\n📋 ARROW MODELS EXTRACTED ({len(unique_models)}):")
            for model in sorted(unique_models):
                model_arrows = [arrow for arrow in all_arrows if arrow.model_name == model]
                total_spines = sum(len(arrow.spine_specifications) for arrow in model_arrows)
                print(f"   • {model}: {total_spines} spine specifications")
            
            # Spine distribution
            spine_counts = {}
            for arrow in all_arrows:
                count = len(arrow.spine_specifications)
                spine_counts[count] = spine_counts.get(count, 0) + 1
            
            print(f"\n🎯 SPINE SPECIFICATION DISTRIBUTION:")
            for count, freq in sorted(spine_counts.items()):
                print(f"     {count} spine options: {freq} arrows")
        
        if failed_urls:
            print(f"\n❌ FAILED URLS:")
            failure_reasons = {}
            for url, manufacturer, reason in failed_urls:
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
            
            for reason, count in failure_reasons.items():
                print(f"     {reason}: {count} URLs")
        
        return len(all_arrows)
    else:
        print(f"\n❌ No results for {matched_manufacturer}")
        return 0

def main():
    """Main function with command line argument parsing"""
    if len(sys.argv) < 2:
        print("Usage: python run_manufacturer_extraction.py [manufacturer_name] [options]")
        print("\nExamples:")
        print('  python run_manufacturer_extraction.py "Easton Archery"')
        print('  python run_manufacturer_extraction.py "Gold Tip" 10')
        print('  python run_manufacturer_extraction.py "Victory Archery" 15 5')
        print('  python run_manufacturer_extraction.py "Skylon" --update')
        print('  python run_manufacturer_extraction.py --list')
        return
    
    if sys.argv[1] == "--list":
        list_manufacturers()
        return
    
    # Parse arguments
    manufacturer_name = sys.argv[1]
    update_mode = False
    batch_size = None
    start_index = 0
    
    # Check for --update flag in any position
    remaining_args = [arg for arg in sys.argv[2:] if arg != "--update"]
    if "--update" in sys.argv:
        update_mode = True
        print("🔄 Update mode enabled - processing only new URLs")
    
    # Parse remaining numeric arguments
    if len(remaining_args) > 0 and remaining_args[0].isdigit():
        batch_size = int(remaining_args[0])
    if len(remaining_args) > 1 and remaining_args[1].isdigit():
        start_index = int(remaining_args[1])
    
    # In update mode, ignore start_index as we process new URLs only
    if update_mode:
        start_index = 0
    
    result = asyncio.run(run_manufacturer_extraction(manufacturer_name, batch_size, start_index, update_mode))
    
    if result is not None:
        mode_text = "updated" if update_mode else "extracted"
        print(f"\n✅ {mode_text.title()} complete: {result} arrows {mode_text} for {manufacturer_name}")
    else:
        print(f"\n✅ No action needed for {manufacturer_name}")

if __name__ == "__main__":
    main()