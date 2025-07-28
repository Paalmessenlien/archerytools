#!/usr/bin/env python3
"""
Batch Sitemap Processor for TopHat Archery
Systematically processes all manufacturers from sitemap and creates retailer URL mappings
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from simple_sitemap_scraper import SimpleSitemapProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_comprehensive_batch_processing():
    """Run comprehensive batch processing for all manufacturers"""
    
    processor = SimpleSitemapProcessor()
    
    print("🚀 Starting Comprehensive TopHat Archery Sitemap Processing")
    print("=" * 80)
    
    # 1. Analyze sitemap
    print("\n📊 Analyzing sitemap...")
    analysis = processor.analyze_sitemap()
    
    print(f"   Total URLs: {analysis['total_urls']:,}")
    print(f"   Manufacturers found: {len(analysis['manufacturers'])}")
    
    # 2. Show manufacturer mapping
    print("\n🏭 Manufacturer Mapping:")
    for manufacturer_slug, count in analysis['manufacturers'].items():
        mapped_name = processor.manufacturer_mapping.get(manufacturer_slug, manufacturer_slug.title())
        print(f"   {manufacturer_slug} -> {mapped_name}: {count} products")
    
    # 3. Process each manufacturer
    print("\n📦 Processing All Manufacturers:")
    print("-" * 60)
    
    overall_results = {
        'started_at': datetime.now().isoformat(),
        'total_manufacturers': len(analysis['manufacturers']),
        'manufacturer_results': {},
        'overall_stats': {
            'total_urls': 0,
            'total_processed': 0,
            'total_matched': 0,
            'total_stored': 0,
            'total_errors': 0
        }
    }
    
    # Process top manufacturers with reasonable limits
    processing_limits = {
        'easton': 20,      # Top priority - most arrows
        'carbon-express': 15,
        'goldtip': 15,
        'skylon-archery': 10,
        'black-eagle': 10,
        'crossx': 10,
        'nijora': 10,
        'victory': 8,      # If available
        'bearpaw': 5,
        'aurel': 5,
        'carbon-impact': 5
    }
    
    for manufacturer_slug, limit in processing_limits.items():
        if manufacturer_slug not in analysis['manufacturers']:
            print(f"   ⚠️  Skipping {manufacturer_slug} - not found in sitemap")
            continue
        
        available_count = analysis['manufacturers'][manufacturer_slug]
        actual_limit = min(limit, available_count)
        
        print(f"\n🎯 Processing {manufacturer_slug} ({actual_limit}/{available_count} URLs)...")
        
        try:
            result = processor.process_manufacturer_urls(manufacturer_slug, limit=actual_limit)
            
            overall_results['manufacturer_results'][manufacturer_slug] = result
            
            # Update overall stats
            overall_results['overall_stats']['total_urls'] += result['total_urls']
            overall_results['overall_stats']['total_processed'] += result['processed_urls']
            overall_results['overall_stats']['total_matched'] += result['matched_arrows']
            overall_results['overall_stats']['total_stored'] += result['stored_mappings']
            overall_results['overall_stats']['total_errors'] += len(result['errors'])
            
            # Show immediate results
            print(f"   ✅ Results: {result['processed_urls']} processed, {result['matched_arrows']} matched, {result['stored_mappings']} stored")
            if result['errors']:
                print(f"   ⚠️  Errors: {len(result['errors'])}")
            
        except Exception as e:
            error_msg = f"Error processing {manufacturer_slug}: {str(e)}"
            logger.error(error_msg)
            overall_results['manufacturer_results'][manufacturer_slug] = {
                'success': False,
                'error': error_msg
            }
            overall_results['overall_stats']['total_errors'] += 1
            print(f"   ❌ Error: {error_msg}")
    
    overall_results['completed_at'] = datetime.now().isoformat()
    
    # 4. Show final statistics
    print("\n🎉 Comprehensive Processing Completed!")
    print("=" * 80)
    
    stats = overall_results['overall_stats']
    print(f"📊 Overall Statistics:")
    print(f"   Total URLs available: {stats['total_urls']}")
    print(f"   URLs processed: {stats['total_processed']}")
    print(f"   Arrows matched: {stats['total_matched']}")
    print(f"   URL mappings stored: {stats['total_stored']}")
    print(f"   Errors encountered: {stats['total_errors']}")
    
    if stats['total_processed'] > 0:
        match_rate = stats['total_matched'] / stats['total_processed']
        storage_rate = stats['total_stored'] / stats['total_matched'] if stats['total_matched'] > 0 else 0
        print(f"   Match rate: {match_rate:.1%}")
        print(f"   Storage rate: {storage_rate:.1%}")
    
    # 5. Show manufacturer breakdown
    print(f"\n📋 Manufacturer Breakdown:")
    for manufacturer, result in overall_results['manufacturer_results'].items():
        if result.get('success', True):  # Default to success if not specified
            mapped_name = processor.manufacturer_mapping.get(manufacturer, manufacturer.title())
            print(f"   {mapped_name} ({manufacturer}):")
            print(f"     URLs: {result.get('processed_urls', 0)}, Matched: {result.get('matched_arrows', 0)}, Stored: {result.get('stored_mappings', 0)}")
        else:
            print(f"   {manufacturer}: ERROR - {result.get('error', 'Unknown error')}")
    
    # 6. Show database statistics
    print(f"\n📊 Final Database Statistics:")
    db_stats = processor.get_database_statistics()
    
    print(f"   Total retailer data entries: {db_stats.get('total_retailer_data_entries', 0)}")
    print(f"   Arrows with retailer data: {db_stats.get('arrows_with_retailer_data', 0)}")
    print("   Retailer sources:")
    for retailer in db_stats.get('retailer_sources', []):
        print(f"     {retailer['name']}: {retailer['arrow_count']} arrows")
    
    # 7. Save comprehensive results
    output_dir = Path(__file__).parent / "data" / "retailer_scraping"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = output_dir / f"comprehensive_sitemap_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(overall_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # 8. Show next steps
    print(f"\n🚀 Next Steps:")
    print(f"   1. Review the results file for detailed analysis")
    print(f"   2. Check database for new retailer URL mappings")
    print(f"   3. Consider running actual web scraping on the stored URLs")
    print(f"   4. Integrate retailer data display in the frontend")
    
    return overall_results

if __name__ == "__main__":
    run_comprehensive_batch_processing()