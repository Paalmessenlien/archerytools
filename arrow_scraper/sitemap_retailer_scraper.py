#!/usr/bin/env python3
"""
Sitemap-Based Retailer Scraper for Arrow Tuning System
Uses sitemap data to systematically enhance existing arrow database with retailer information
"""

import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import re
from urllib.parse import urlparse

# Add crawl4ai to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "crawl4ai"))

from retailer_integration import RetailerIntegrationManager
from arrow_database import ArrowDatabase
from enhance_database_schema import enhance_database_schema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SitemapRetailerScraper:
    """Enhanced retailer scraper that uses sitemap data for systematic scraping"""
    
    def __init__(self, deepseek_api_key: str, db_path: str = "arrow_database.db"):
        self.manager = RetailerIntegrationManager(deepseek_api_key, db_path)
        self.db = ArrowDatabase(db_path)
        self.sitemap_path = Path(__file__).parent.parent / "docs" / "sitemap_komponentensuche.json"
        
        # Ensure enhanced schema exists
        enhance_database_schema(db_path)
        
        # Load sitemap data
        self.sitemap_data = self._load_sitemap()
        
        # Manufacturer mapping for better matching
        self.manufacturer_mapping = {
            'easton': 'Easton',
            'gold-tip': 'Gold Tip',
            'goldtip': 'Gold Tip', 
            'victory': 'Victory',
            'carbon-express': 'Carbon Express',
            'carbon_express': 'Carbon Express',
            'beman': 'Beman',
            'pse': 'PSE',
            'maxima': 'Carbon Express',  # Maxima is a Carbon Express line
            'ok-archery': 'OK Archery',
            'ok_archery': 'OK Archery',
            'x7': 'Easton',  # X7 is an Easton line
            'xx75': 'Easton',  # XX75 is an Easton line
            'axis': 'Easton',  # Axis is an Easton line
            'navigator': 'Easton',  # Navigator is an Easton line
        }
    
    def _load_sitemap(self) -> List[Dict]:
        """Load sitemap data from JSON file"""
        try:
            if not self.sitemap_path.exists():
                logger.error(f"Sitemap file not found: {self.sitemap_path}")
                return []
            
            with open(self.sitemap_path, 'r', encoding='utf-8') as f:
                sitemap_data = json.load(f)
            
            logger.info(f"✅ Loaded sitemap with {len(sitemap_data)} URLs")
            return sitemap_data
            
        except Exception as e:
            logger.error(f"Error loading sitemap: {e}")
            return []
    
    def analyze_sitemap(self) -> Dict[str, any]:
        """Analyze sitemap to understand manufacturers and products available"""
        analysis = {
            'total_urls': len(self.sitemap_data),
            'manufacturers': {},
            'url_patterns': [],
            'sample_urls': []
        }
        
        manufacturer_counts = {}
        url_patterns = set()
        
        for entry in self.sitemap_data:
            url = entry.get('loc', '')
            
            # Extract manufacturer from URL pattern
            # Pattern: /marke/{manufacturer}/{model}/{id}/{product-name}
            match = re.search(r'/marke/([^/]+)/', url)
            if match:
                manufacturer = match.group(1)
                manufacturer_counts[manufacturer] = manufacturer_counts.get(manufacturer, 0) + 1
            
            # Extract URL pattern
            path_parts = urlparse(url).path.split('/')
            if len(path_parts) >= 4:
                pattern = '/'.join(path_parts[:4])  # Keep /komponentensuche-nach-schaft/marke/{manufacturer}
                url_patterns.add(pattern)
        
        analysis['manufacturers'] = dict(sorted(manufacturer_counts.items(), key=lambda x: x[1], reverse=True))
        analysis['url_patterns'] = list(url_patterns)
        analysis['sample_urls'] = [entry.get('loc') for entry in self.sitemap_data[:5]]
        
        return analysis
    
    def get_manufacturer_urls(self, manufacturer_filter: str = None) -> List[str]:
        """Get URLs for specific manufacturer or all manufacturers"""
        urls = []
        
        for entry in self.sitemap_data:
            url = entry.get('loc', '')
            
            if manufacturer_filter:
                # Check if URL contains the manufacturer
                if f'/marke/{manufacturer_filter.lower()}/' in url.lower():
                    urls.append(url)
            else:
                urls.append(url)
        
        return urls
    
    def extract_product_info_from_url(self, url: str) -> Dict[str, str]:
        """Extract manufacturer, model, and product info from TopHat URL"""
        try:
            # Pattern: /marke/{manufacturer}/{model}/{id}/{product-name}
            path = urlparse(url).path
            parts = path.split('/')
            
            if len(parts) >= 6 and 'marke' in parts:
                marke_index = parts.index('marke')
                manufacturer_slug = parts[marke_index + 1] if marke_index + 1 < len(parts) else ''
                model_slug = parts[marke_index + 2] if marke_index + 2 < len(parts) else ''
                product_id = parts[marke_index + 3] if marke_index + 3 < len(parts) else ''
                product_name = parts[marke_index + 4] if marke_index + 4 < len(parts) else ''
                
                # Map manufacturer slug to proper name
                manufacturer = self.manufacturer_mapping.get(manufacturer_slug.lower(), manufacturer_slug.title())
                
                # Extract spine from product name if available
                spine_match = re.search(r'(\d{3,4})', product_name)
                spine = int(spine_match.group(1)) if spine_match else None
                
                return {
                    'manufacturer': manufacturer,
                    'manufacturer_slug': manufacturer_slug,
                    'model': model_slug.replace('-', ' ').title(),
                    'model_slug': model_slug,
                    'product_id': product_id,
                    'product_name': product_name,
                    'spine': spine,
                    'url': url
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting product info from URL {url}: {e}")
            return {}
    
    async def find_matching_arrows(self, manufacturer: str, model: str, spine: int = None) -> List[Dict]:
        """Find matching arrows in database for retailer product"""
        try:
            # Search with exact manufacturer
            matches = self.db.search_arrows(
                manufacturer=manufacturer,
                model_search=model,
                limit=10
            )
            
            # If no exact matches, try fuzzy matching
            if not matches:
                # Try variations of manufacturer name
                manufacturer_variations = [
                    manufacturer.replace(' ', ''),
                    manufacturer.replace('-', ' '),
                    manufacturer.split()[0] if ' ' in manufacturer else manufacturer
                ]
                
                for var_manufacturer in manufacturer_variations:
                    matches = self.db.search_arrows(
                        manufacturer=var_manufacturer,
                        model_search=model,
                        limit=10
                    )
                    if matches:
                        break
            
            # If we have spine info, filter by compatible spine range
            if spine and matches:
                compatible_matches = []
                for arrow in matches:
                    # Check if spine falls within arrow's spine range
                    min_spine = arrow.get('min_spine', 0)
                    max_spine = arrow.get('max_spine', 9999)
                    
                    if min_spine <= spine <= max_spine:
                        compatible_matches.append(arrow)
                
                if compatible_matches:
                    matches = compatible_matches
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding matching arrows: {e}")
            return []
    
    async def scrape_manufacturer_batch(self, manufacturer: str, limit: int = 20, delay: float = 3.0) -> Dict[str, any]:
        """Scrape all products for a specific manufacturer"""
        logger.info(f"🎯 Starting batch scrape for manufacturer: {manufacturer}")
        
        manufacturer_urls = self.get_manufacturer_urls(manufacturer.lower())
        
        if not manufacturer_urls:
            return {
                'success': False,
                'error': f'No URLs found for manufacturer: {manufacturer}'
            }
        
        logger.info(f"   Found {len(manufacturer_urls)} URLs for {manufacturer}")
        
        # Limit URLs for testing/safety
        if limit:
            manufacturer_urls = manufacturer_urls[:limit]
            logger.info(f"   Limited to {len(manufacturer_urls)} URLs for processing")
        
        results = {
            'manufacturer': manufacturer,
            'total_urls': len(manufacturer_urls),
            'processed_urls': 0,
            'successful_scrapes': 0,
            'matched_arrows': 0,
            'new_enhancements': 0,
            'errors': [],
            'successful_products': []
        }
        
        for i, url in enumerate(manufacturer_urls):
            try:
                logger.info(f"   Processing URL {i+1}/{len(manufacturer_urls)}: {url}")
                
                # Extract product info from URL
                product_info = self.extract_product_info_from_url(url)
                if not product_info:
                    results['errors'].append(f"Could not extract product info from {url}")
                    continue
                
                # Find matching arrows in database
                matching_arrows = await self.find_matching_arrows(
                    product_info['manufacturer'],
                    product_info['model'],
                    product_info.get('spine')
                )
                
                if not matching_arrows:
                    logger.info(f"     No matching arrows found for {product_info['manufacturer']} {product_info['model']}")
                    results['errors'].append(f"No database match for {product_info['manufacturer']} {product_info['model']}")
                    continue
                
                # Enhance the best matching arrow
                best_match = matching_arrows[0]  # Use first/best match
                logger.info(f"     Found matching arrow: {best_match['manufacturer']} {best_match['model_name']} (ID: {best_match['id']})")
                
                # Enhance with retailer data
                enhancement_result = await self.manager.enhance_arrow_with_retailer_data(
                    best_match['id'], 
                    [url]
                )
                
                if enhancement_result.get('success'):
                    results['new_enhancements'] += 1
                    results['successful_products'].append({
                        'url': url,
                        'product_info': product_info,
                        'matched_arrow': {
                            'id': best_match['id'],
                            'manufacturer': best_match['manufacturer'],
                            'model_name': best_match['model_name']
                        },
                        'enhancement_result': enhancement_result
                    })
                    logger.info(f"     ✅ Successfully enhanced arrow {best_match['id']}")
                else:
                    results['errors'].append(f"Enhancement failed for {url}: {enhancement_result.get('error')}")
                
                results['matched_arrows'] += len(matching_arrows)
                results['successful_scrapes'] += 1
                
            except Exception as e:
                error_msg = f"Error processing {url}: {str(e)}"
                logger.error(f"     ❌ {error_msg}")
                results['errors'].append(error_msg)
            
            finally:
                results['processed_urls'] += 1
                
                # Add delay to be respectful
                if delay > 0:
                    await asyncio.sleep(delay)
        
        # Calculate success rate
        results['success_rate'] = results['successful_scrapes'] / results['processed_urls'] if results['processed_urls'] > 0 else 0
        results['enhancement_rate'] = results['new_enhancements'] / results['successful_scrapes'] if results['successful_scrapes'] > 0 else 0
        
        logger.info(f"✅ Completed batch scrape for {manufacturer}:")
        logger.info(f"   URLs processed: {results['processed_urls']}")
        logger.info(f"   Successful scrapes: {results['successful_scrapes']}")
        logger.info(f"   New enhancements: {results['new_enhancements']}")
        logger.info(f"   Success rate: {results['success_rate']:.1%}")
        
        return results
    
    async def run_comprehensive_enhancement(self, manufacturers: List[str] = None, urls_per_manufacturer: int = 10) -> Dict[str, any]:
        """Run comprehensive enhancement for multiple manufacturers"""
        if not manufacturers:
            # Get top manufacturers from sitemap
            analysis = self.analyze_sitemap()
            top_manufacturers = list(analysis['manufacturers'].keys())[:5]  # Top 5
            manufacturers = [self.manufacturer_mapping.get(m, m.title()) for m in top_manufacturers]
        
        logger.info(f"🚀 Starting comprehensive retailer enhancement for {len(manufacturers)} manufacturers")
        logger.info(f"   Manufacturers: {', '.join(manufacturers)}")
        
        comprehensive_results = {
            'total_manufacturers': len(manufacturers),
            'manufacturer_results': {},
            'overall_stats': {
                'total_urls_processed': 0,
                'total_successful_scrapes': 0,
                'total_new_enhancements': 0,
                'total_errors': 0
            },
            'started_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        for manufacturer in manufacturers:
            try:
                logger.info(f"\n📦 Processing manufacturer: {manufacturer}")
                
                # Map back to slug for URL filtering
                manufacturer_slug = None
                for slug, mapped_name in self.manufacturer_mapping.items():
                    if mapped_name.lower() == manufacturer.lower():
                        manufacturer_slug = slug
                        break
                
                if not manufacturer_slug:
                    manufacturer_slug = manufacturer.lower().replace(' ', '-')
                
                result = await self.scrape_manufacturer_batch(
                    manufacturer_slug, 
                    limit=urls_per_manufacturer,
                    delay=2.0  # 2 second delay between requests
                )
                
                comprehensive_results['manufacturer_results'][manufacturer] = result
                
                # Update overall stats
                if result.get('processed_urls'):
                    comprehensive_results['overall_stats']['total_urls_processed'] += result['processed_urls']
                if result.get('successful_scrapes'):
                    comprehensive_results['overall_stats']['total_successful_scrapes'] += result['successful_scrapes']
                if result.get('new_enhancements'):
                    comprehensive_results['overall_stats']['total_new_enhancements'] += result['new_enhancements']
                if result.get('errors'):
                    comprehensive_results['overall_stats']['total_errors'] += len(result['errors'])
                
                # Add delay between manufacturers
                await asyncio.sleep(5.0)
                
            except Exception as e:
                logger.error(f"Error processing manufacturer {manufacturer}: {e}")
                comprehensive_results['manufacturer_results'][manufacturer] = {
                    'success': False,
                    'error': str(e)
                }
        
        comprehensive_results['completed_at'] = datetime.now().isoformat()
        
        # Calculate overall success rates
        stats = comprehensive_results['overall_stats']
        stats['overall_success_rate'] = stats['total_successful_scrapes'] / max(stats['total_urls_processed'], 1)
        stats['enhancement_rate'] = stats['total_new_enhancements'] / max(stats['total_successful_scrapes'], 1)
        
        logger.info(f"\n🎉 Comprehensive enhancement completed!")
        logger.info(f"   Total URLs processed: {stats['total_urls_processed']}")
        logger.info(f"   Total successful scrapes: {stats['total_successful_scrapes']}")
        logger.info(f"   Total new enhancements: {stats['total_new_enhancements']}")
        logger.info(f"   Overall success rate: {stats['overall_success_rate']:.1%}")
        logger.info(f"   Enhancement rate: {stats['enhancement_rate']:.1%}")
        
        return comprehensive_results

async def main():
    """Test the sitemap-based retailer scraper"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
    scraper = SitemapRetailerScraper(api_key)
    
    print("🧪 Testing Sitemap-Based Retailer Scraper")
    print("=" * 60)
    
    # 1. Analyze sitemap
    print("\n📊 Analyzing sitemap...")
    analysis = scraper.analyze_sitemap()
    
    print(f"   Total URLs: {analysis['total_urls']:,}")
    print(f"   Manufacturers found: {len(analysis['manufacturers'])}")
    print("   Top manufacturers:")
    for manufacturer, count in list(analysis['manufacturers'].items())[:10]:
        print(f"     {manufacturer}: {count} products")
    
    # 2. Test with a single manufacturer (Easton)
    print("\n🎯 Testing with Easton manufacturer (5 products)...")
    result = await scraper.scrape_manufacturer_batch('easton', limit=5, delay=1.0)
    
    print(f"   Result: {result.get('success', 'Unknown')}")
    print(f"   URLs processed: {result.get('processed_urls', 0)}")
    print(f"   Successful scrapes: {result.get('successful_scrapes', 0)}")
    print(f"   New enhancements: {result.get('new_enhancements', 0)}")
    
    if result.get('successful_products'):
        print("   Sample successful products:")
        for product in result['successful_products'][:3]:
            product_info = product['product_info']
            matched_arrow = product['matched_arrow']
            print(f"     {product_info['manufacturer']} {product_info['model']} -> Arrow ID {matched_arrow['id']}")
    
    if result.get('errors'):
        print(f"   Errors encountered: {len(result['errors'])}")
        for error in result['errors'][:3]:
            print(f"     {error}")

if __name__ == "__main__":
    asyncio.run(main())