#!/usr/bin/env python3
"""
Comprehensive Sitemap-Based Retailer Scraper
Uses the TopHat Archery sitemap to systematically scrape and enhance arrow data
Designed to work with crawl4ai virtual environment
"""

import json
import logging
import subprocess
import sys
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from dataclasses import dataclass, field

from arrow_database import ArrowDatabase
from enhance_database_schema import enhance_database_schema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SitemapProduct:
    """Product information extracted from sitemap URL"""
    manufacturer: str
    manufacturer_slug: str
    model: str
    model_slug: str
    product_id: str
    product_name: str
    spine: Optional[int] = None
    url: str = ""

class ComprehensiveSitemapScraper:
    """Comprehensive scraper that uses crawl4ai venv and sitemap data"""
    
    def __init__(self, db_path: str = "arrow_database.db"):
        self.db = ArrowDatabase(db_path)
        self.sitemap_path = Path(__file__).parent.parent / "docs" / "sitemap_komponentensuche.json"
        self.crawl4ai_path = Path(__file__).parent.parent / "crawl4ai"
        
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
            'maxima': 'Carbon Express',
            'ok-archery': 'OK Archery',
            'ok_archery': 'OK Archery',
            'x7': 'Easton',
            'xx75': 'Easton',
            'axis': 'Easton',
            'navigator': 'Easton',
            'skylon-archery': 'Skylon',
            'skylon_archery': 'Skylon',
            'black-eagle': 'Black Eagle',
            'black_eagle': 'Black Eagle',
            'crossx': 'Cross-X',
            'nijora': 'Nijora',
            'bearpaw': 'Bearpaw',
            'aurel': 'Aurel',
            'carbon-impact': 'Carbon Impact',
            'carbon_impact': 'Carbon Impact'
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
            'spine_patterns': {},
            'sample_urls': []
        }
        
        manufacturer_counts = {}
        spine_patterns = {}
        
        for entry in self.sitemap_data:
            url = entry.get('loc', '')
            
            # Extract manufacturer from URL pattern
            match = re.search(r'/marke/([^/]+)/', url)
            if match:
                manufacturer = match.group(1)
                manufacturer_counts[manufacturer] = manufacturer_counts.get(manufacturer, 0) + 1
            
            # Extract spine patterns
            spine_match = re.search(r'(\d{3,4})', url)
            if spine_match:
                spine = spine_match.group(1)
                spine_patterns[spine] = spine_patterns.get(spine, 0) + 1
        
        analysis['manufacturers'] = dict(sorted(manufacturer_counts.items(), key=lambda x: x[1], reverse=True))
        analysis['spine_patterns'] = dict(sorted(spine_patterns.items(), key=lambda x: int(x[0])))
        analysis['sample_urls'] = [entry.get('loc') for entry in self.sitemap_data[:10]]
        
        return analysis
    
    def extract_product_info_from_url(self, url: str) -> Optional[SitemapProduct]:
        """Extract manufacturer, model, and product info from TopHat URL"""
        try:
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
                
                return SitemapProduct(
                    manufacturer=manufacturer,
                    manufacturer_slug=manufacturer_slug,
                    model=model_slug.replace('-', ' ').title(),
                    model_slug=model_slug,
                    product_id=product_id,
                    product_name=product_name,
                    spine=spine,
                    url=url
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting product info from URL {url}: {e}")
            return None
    
    def find_matching_arrows(self, product: SitemapProduct) -> List[Dict]:
        """Find matching arrows in database for retailer product"""
        try:
            # Search with exact manufacturer
            matches = self.db.search_arrows(
                manufacturer=product.manufacturer,
                model_search=product.model,
                limit=10
            )
            
            # If no exact matches, try fuzzy matching
            if not matches:
                # Try variations of manufacturer name
                manufacturer_variations = [
                    product.manufacturer.replace(' ', ''),
                    product.manufacturer.replace('-', ' '),
                    product.manufacturer.split()[0] if ' ' in product.manufacturer else product.manufacturer
                ]
                
                for var_manufacturer in manufacturer_variations:
                    matches = self.db.search_arrows(
                        manufacturer=var_manufacturer,
                        model_search=product.model,
                        limit=10
                    )
                    if matches:
                        break
            
            # If still no matches, try just manufacturer
            if not matches:
                matches = self.db.search_arrows(
                    manufacturer=product.manufacturer,
                    limit=5
                )
            
            # If we have spine info, filter by compatible spine range
            if product.spine and matches:
                compatible_matches = []
                for arrow in matches:
                    min_spine = arrow.get('min_spine', 0)
                    max_spine = arrow.get('max_spine', 9999)
                    
                    if min_spine <= product.spine <= max_spine:
                        compatible_matches.append(arrow)
                
                if compatible_matches:
                    matches = compatible_matches
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding matching arrows: {e}")
            return []
    
    def create_scraping_script(self, urls: List[str], output_file: str) -> str:
        """Create a Python script for crawl4ai to scrape the URLs"""
        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated scraping script for TopHat Archery URLs
Generated at: {datetime.now().isoformat()}
"""

import asyncio
import json
import sys
from pathlib import Path
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

# URLs to scrape
URLS_TO_SCRAPE = {urls}

# DeepSeek API key (should be set in environment)
import os
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

if not DEEPSEEK_API_KEY:
    print("❌ DEEPSEEK_API_KEY not found in environment")
    sys.exit(1)

async def scrape_tophat_products():
    """Scrape product data from TopHat Archery URLs"""
    
    # Define extraction schema for arrow data
    extraction_schema = {{
        "type": "object",
        "properties": {{
            "manufacturer": {{
                "type": "string",
                "description": "Arrow manufacturer (e.g., Easton, Gold Tip, Victory)"
            }},
            "model_name": {{
                "type": "string", 
                "description": "Full arrow model name"
            }},
            "spine": {{
                "type": "integer",
                "description": "Arrow spine value (e.g., 340, 500, 600)"
            }},
            "outer_diameter": {{
                "type": "number",
                "description": "Outer diameter in inches (convert from mm if needed)"
            }},
            "inner_diameter": {{
                "type": "number", 
                "description": "Inner diameter in inches (convert from mm if needed)"
            }},
            "gpi_weight": {{
                "type": "number",
                "description": "Weight in grains per inch (GPI)"
            }},
            "straightness_tolerance": {{
                "type": "string",
                "description": "Straightness tolerance (e.g., ±.006\\", ±.003\\")"
            }},
            "weight_tolerance": {{
                "type": "string",
                "description": "Weight tolerance if specified"
            }},
            "length_options": {{
                "type": "array",
                "items": {{"type": "number"}},
                "description": "Available arrow lengths in inches"
            }},
            "price": {{
                "type": "number",
                "description": "Price as decimal number"
            }},
            "currency": {{
                "type": "string",
                "description": "Currency code (EUR, USD, etc.)"
            }},
            "stock_quantity": {{
                "type": "integer",
                "description": "Available stock quantity"
            }},
            "availability_status": {{
                "type": "string",
                "description": "Stock status (in_stock, out_of_stock, limited, etc.)"
            }},
            "product_description": {{
                "type": "string",
                "description": "Full product description"
            }},
            "technical_notes": {{
                "type": "array",
                "items": {{"type": "string"}},
                "description": "Additional technical specifications and notes"
            }}
        }},
        "required": ["manufacturer", "model_name"]
    }}
    
    # Create extraction strategy
    extraction_strategy = LLMExtractionStrategy(
        provider="openai",
        api_token=DEEPSEEK_API_KEY,
        schema=extraction_schema,
        extraction_type="schema",
        instruction="""
        Extract detailed arrow specifications from this TopHat Archery product page.
        
        Focus on:
        1. Complete technical specifications (spine, diameters, weight, tolerances)
        2. Pricing and availability information
        3. Performance characteristics
        4. Any additional technical details not found on manufacturer sites
        
        Convert metric measurements to inches where needed (1mm = 0.0394 inches).
        Extract all available spine options if multiple are shown.
        Include performance recommendations and technical notes.
        """
    )
    
    results = []
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        for i, url in enumerate(URLS_TO_SCRAPE):
            try:
                print(f"Scraping {{i+1}}/{{len(URLS_TO_SCRAPE)}}: {{url}}")
                
                result = await crawler.arun(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    bypass_cache=True,
                    wait_for="css:.product-details"
                )
                
                if result.success:
                    try:
                        extracted_data = json.loads(result.extracted_content)
                        extracted_data['source_url'] = url
                        extracted_data['scraped_at'] = "{datetime.now().isoformat()}"
                        results.append(extracted_data)
                        print(f"✅ Successfully scraped: {{extracted_data.get('manufacturer', 'Unknown')}} {{extracted_data.get('model_name', 'Unknown')}}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse JSON for {{url}}: {{e}}")
                        results.append({{"error": "JSON decode error", "url": url}})
                else:
                    print(f"❌ Failed to scrape {{url}}: {{result.error_message}}")
                    results.append({{"error": result.error_message, "url": url}})
                
                # Add delay between requests
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Exception scraping {{url}}: {{e}}")
                results.append({{"error": str(e), "url": url}})
    
    # Save results
    output_path = Path("{output_file}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\\n🎉 Scraping completed! Results saved to: {{output_path}}")
    print(f"   Total URLs processed: {{len(URLS_TO_SCRAPE)}}")
    print(f"   Successful extractions: {{len([r for r in results if 'error' not in r])}}")
    print(f"   Errors: {{len([r for r in results if 'error' in r])}}")
    
    return results

if __name__ == "__main__":
    asyncio.run(scrape_tophat_products())
'''
        
        return script_content
    
    def run_crawl4ai_scraping(self, urls: List[str], batch_name: str = "batch") -> Dict[str, any]:
        """Run scraping using crawl4ai virtual environment"""
        try:
            # Create output directory
            output_dir = Path(__file__).parent / "data" / "retailer_scraping"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create script file
            script_file = output_dir / f"scrape_{batch_name}.py"
            output_file = output_dir / f"results_{batch_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            script_content = self.create_scraping_script(urls, str(output_file))
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            logger.info(f"Created scraping script: {script_file}")
            
            # Run the script in crawl4ai environment
            logger.info(f"Running scraping script with crawl4ai...")
            
            # Change to crawl4ai directory and run with venv
            cmd = [
                "bash", "-c",
                f"cd {self.crawl4ai_path} && source venv/bin/activate && python {script_file}"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Scraping completed successfully")
                
                # Load and return results
                if output_file.exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        scraped_data = json.load(f)
                    
                    return {
                        'success': True,
                        'scraped_data': scraped_data,
                        'output_file': str(output_file),
                        'script_file': str(script_file),
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Output file not created',
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
            else:
                logger.error(f"❌ Scraping failed with return code: {result.returncode}")
                return {
                    'success': False,
                    'error': f'Script failed with return code {result.returncode}',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except Exception as e:
            logger.error(f"Error running crawl4ai scraping: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_scraped_data(self, scraped_data: List[Dict]) -> Dict[str, any]:
        """Process scraped data and match with database arrows"""
        results = {
            'total_scraped': len(scraped_data),
            'successful_scrapes': 0,
            'matched_arrows': 0,
            'stored_enhancements': 0,
            'errors': [],
            'enhancements': []
        }
        
        for scraped_item in scraped_data:
            try:
                if 'error' in scraped_item:
                    results['errors'].append(scraped_item)
                    continue
                
                results['successful_scrapes'] += 1
                
                # Extract basic info
                manufacturer = scraped_item.get('manufacturer', '')
                model_name = scraped_item.get('model_name', '')
                source_url = scraped_item.get('source_url', '')
                
                if not manufacturer or not model_name:
                    results['errors'].append(f"Missing manufacturer or model for {source_url}")
                    continue
                
                # Find matching arrows in database
                matches = self.db.search_arrows(
                    manufacturer=manufacturer,
                    model_search=model_name,
                    limit=5
                )
                
                if not matches:
                    results['errors'].append(f"No database match for {manufacturer} {model_name}")
                    continue
                
                results['matched_arrows'] += len(matches)
                
                # Store enhancement for best match
                best_match = matches[0]
                enhancement_stored = self.store_retailer_enhancement(best_match['id'], scraped_item)
                
                if enhancement_stored:
                    results['stored_enhancements'] += 1
                    results['enhancements'].append({
                        'arrow_id': best_match['id'],
                        'arrow_info': f"{best_match['manufacturer']} {best_match['model_name']}",
                        'retailer_data': scraped_item,
                        'source_url': source_url
                    })
                
            except Exception as e:
                results['errors'].append(f"Error processing scraped item: {str(e)}")
        
        return results
    
    def store_retailer_enhancement(self, arrow_id: int, scraped_data: Dict) -> bool:
        """Store enhanced retailer data in database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get TopHat Archery retailer ID
            cursor.execute("SELECT id FROM retailer_sources WHERE retailer_name = ?", ("TopHat Archery",))
            retailer_row = cursor.fetchone()
            if not retailer_row:
                logger.error("TopHat Archery retailer not found in database")
                return False
            
            retailer_id = retailer_row[0]
            
            # Store/update retailer arrow data
            cursor.execute("""
                INSERT OR REPLACE INTO retailer_arrow_data (
                    arrow_id, retailer_id, source_url, price, currency, 
                    stock_quantity, availability_status, straightness_tolerance,
                    weight_tolerance, technical_notes, product_description, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                arrow_id, retailer_id, scraped_data.get('source_url'),
                scraped_data.get('price'), scraped_data.get('currency', 'EUR'),
                scraped_data.get('stock_quantity'), scraped_data.get('availability_status'),
                scraped_data.get('straightness_tolerance'), scraped_data.get('weight_tolerance'),
                json.dumps(scraped_data.get('technical_notes', [])),
                scraped_data.get('product_description'),
                datetime.now().isoformat()
            ))
            
            # Store price history if price available
            if scraped_data.get('price'):
                cursor.execute("""
                    INSERT INTO price_history (
                        arrow_id, retailer_id, price, currency, 
                        stock_quantity, availability_status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    arrow_id, retailer_id, scraped_data.get('price'),
                    scraped_data.get('currency', 'EUR'), 
                    scraped_data.get('stock_quantity'),
                    scraped_data.get('availability_status')
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored retailer enhancement for arrow {arrow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing retailer enhancement: {e}")
            return False
    
    def run_comprehensive_enhancement(self, manufacturers: List[str] = None, urls_per_manufacturer: int = 5) -> Dict[str, any]:
        """Run comprehensive enhancement for multiple manufacturers"""
        if not manufacturers:
            # Get top manufacturers from sitemap
            analysis = self.analyze_sitemap()
            top_manufacturers = list(analysis['manufacturers'].keys())[:3]  # Top 3 for testing
            manufacturers = [m for m in top_manufacturers if m in self.manufacturer_mapping]
        
        logger.info(f"🚀 Starting comprehensive retailer enhancement")
        logger.info(f"   Manufacturers: {manufacturers}")
        logger.info(f"   URLs per manufacturer: {urls_per_manufacturer}")
        
        comprehensive_results = {
            'total_manufacturers': len(manufacturers),
            'manufacturer_results': {},
            'overall_stats': {
                'total_urls_processed': 0,
                'total_successful_scrapes': 0,
                'total_enhancements': 0,
                'total_errors': 0
            },
            'started_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        for manufacturer in manufacturers:
            try:
                logger.info(f"\\n📦 Processing manufacturer: {manufacturer}")
                
                # Get URLs for this manufacturer
                manufacturer_urls = []
                for entry in self.sitemap_data:
                    url = entry.get('loc', '')
                    if f'/marke/{manufacturer}/' in url.lower():
                        manufacturer_urls.append(url)
                
                if urls_per_manufacturer:
                    manufacturer_urls = manufacturer_urls[:urls_per_manufacturer]
                
                if not manufacturer_urls:
                    logger.warning(f"No URLs found for manufacturer: {manufacturer}")
                    continue
                
                logger.info(f"   Found {len(manufacturer_urls)} URLs to process")
                
                # Run scraping with crawl4ai
                scraping_result = self.run_crawl4ai_scraping(
                    manufacturer_urls, 
                    batch_name=f"{manufacturer}_{datetime.now().strftime('%H%M%S')}"
                )
                
                if scraping_result['success']:
                    # Process scraped data
                    processing_result = self.process_scraped_data(scraping_result['scraped_data'])
                    
                    comprehensive_results['manufacturer_results'][manufacturer] = {
                        'success': True,
                        'urls_processed': len(manufacturer_urls),
                        'scraping_result': scraping_result,
                        'processing_result': processing_result
                    }
                    
                    # Update overall stats
                    comprehensive_results['overall_stats']['total_urls_processed'] += len(manufacturer_urls)
                    comprehensive_results['overall_stats']['total_successful_scrapes'] += processing_result['successful_scrapes']
                    comprehensive_results['overall_stats']['total_enhancements'] += processing_result['stored_enhancements']
                    comprehensive_results['overall_stats']['total_errors'] += len(processing_result['errors'])
                    
                else:
                    comprehensive_results['manufacturer_results'][manufacturer] = {
                        'success': False,
                        'error': scraping_result.get('error'),
                        'stderr': scraping_result.get('stderr')
                    }
                
            except Exception as e:
                logger.error(f"Error processing manufacturer {manufacturer}: {e}")
                comprehensive_results['manufacturer_results'][manufacturer] = {
                    'success': False,
                    'error': str(e)
                }
        
        comprehensive_results['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"\\n🎉 Comprehensive enhancement completed!")
        stats = comprehensive_results['overall_stats']
        logger.info(f"   Total URLs processed: {stats['total_urls_processed']}")
        logger.info(f"   Total successful scrapes: {stats['total_successful_scrapes']}")
        logger.info(f"   Total enhancements stored: {stats['total_enhancements']}")
        
        return comprehensive_results

def main():
    """Test the comprehensive sitemap scraper"""
    scraper = ComprehensiveSitemapScraper()
    
    print("🧪 Testing Comprehensive Sitemap Scraper")
    print("=" * 70)
    
    # 1. Analyze sitemap
    print("\\n📊 Analyzing sitemap...")
    analysis = scraper.analyze_sitemap()
    
    print(f"   Total URLs: {analysis['total_urls']:,}")
    print(f"   Manufacturers found: {len(analysis['manufacturers'])}")
    print("   Top manufacturers:")
    for manufacturer, count in list(analysis['manufacturers'].items())[:10]:
        mapped_name = scraper.manufacturer_mapping.get(manufacturer, manufacturer)
        print(f"     {manufacturer} ({mapped_name}): {count} products")
    
    # 2. Test with a single manufacturer (Easton - 2 URLs)
    print("\\n🎯 Testing with Easton manufacturer (2 URLs)...")
    result = scraper.run_comprehensive_enhancement(['easton'], urls_per_manufacturer=2)
    
    print(f"   Overall result:")
    print(f"     URLs processed: {result['overall_stats']['total_urls_processed']}")
    print(f"     Successful scrapes: {result['overall_stats']['total_successful_scrapes']}")
    print(f"     Enhancements stored: {result['overall_stats']['total_enhancements']}")
    
    # Show detailed results
    for manufacturer, manufacturer_result in result['manufacturer_results'].items():
        print(f"\\n   {manufacturer} results:")
        if manufacturer_result['success']:
            processing = manufacturer_result['processing_result']
            print(f"     Scraped items: {processing['successful_scrapes']}")
            print(f"     Matched arrows: {processing['matched_arrows']}")
            print(f"     Stored enhancements: {processing['stored_enhancements']}")
            if processing['errors']:
                print(f"     Errors: {len(processing['errors'])}")
        else:
            print(f"     Error: {manufacturer_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()