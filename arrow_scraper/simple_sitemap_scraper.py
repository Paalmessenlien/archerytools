#!/usr/bin/env python3
"""
Simple Sitemap-Based Retailer Data Enhancement
Uses sitemap data to systematically enhance existing arrow database with retailer URLs
"""

import json
import logging
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

class SimpleSitemapProcessor:
    """Simple sitemap processor that matches URLs with database arrows"""
    
    def __init__(self, db_path: str = "arrow_database.db"):
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
    
    def extract_product_info_from_url(self, url: str) -> Optional[SitemapProduct]:
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
            
            # If we have spine info, filter by compatible spine range
            if product.spine and matches:
                compatible_matches = []
                for arrow in matches:
                    # Check if spine falls within arrow's spine range
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
    
    def store_retailer_url_mapping(self, arrow_id: int, product: SitemapProduct) -> bool:
        """Store retailer URL mapping in database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get or create retailer source
            cursor.execute("""
                SELECT id FROM retailer_sources WHERE retailer_name = ?
            """, ("TopHat Archery",))
            
            retailer_row = cursor.fetchone()
            if retailer_row:
                retailer_id = retailer_row[0]
            else:
                # Create new retailer source
                cursor.execute("""
                    INSERT INTO retailer_sources (retailer_name, base_url, language, currency)
                    VALUES (?, ?, ?, ?)
                """, ("TopHat Archery", "https://tophatarchery.com", "de", "EUR"))
                retailer_id = cursor.lastrowid
            
            # Store/update retailer arrow data with basic info
            cursor.execute("""
                INSERT OR REPLACE INTO retailer_arrow_data (
                    arrow_id, retailer_id, source_url, 
                    product_description, updated_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                arrow_id, retailer_id, product.url,
                f"{product.manufacturer} {product.model} {product.product_name}",
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored URL mapping for arrow {arrow_id}: {product.url}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing retailer URL mapping: {e}")
            return False
    
    def process_manufacturer_urls(self, manufacturer_filter: str = None, limit: int = None) -> Dict[str, any]:
        """Process URLs for a specific manufacturer"""
        logger.info(f"🎯 Processing URLs for manufacturer: {manufacturer_filter}")
        
        # Filter URLs by manufacturer
        filtered_urls = []
        for entry in self.sitemap_data:
            url = entry.get('loc', '')
            if manufacturer_filter:
                if f'/marke/{manufacturer_filter.lower()}/' in url.lower():
                    filtered_urls.append(url)
            else:
                filtered_urls.append(url)
        
        if limit:
            filtered_urls = filtered_urls[:limit]
        
        logger.info(f"   Found {len(filtered_urls)} URLs to process")
        
        results = {
            'manufacturer': manufacturer_filter,
            'total_urls': len(filtered_urls),
            'processed_urls': 0,
            'matched_arrows': 0,
            'stored_mappings': 0,
            'errors': [],
            'successful_mappings': []
        }
        
        for i, url in enumerate(filtered_urls):
            try:
                logger.info(f"   Processing URL {i+1}/{len(filtered_urls)}: {url}")
                
                # Extract product info
                product = self.extract_product_info_from_url(url)
                if not product:
                    results['errors'].append(f"Could not extract product info from {url}")
                    continue
                
                # Find matching arrows
                matching_arrows = self.find_matching_arrows(product)
                if not matching_arrows:
                    logger.info(f"     No matching arrows found for {product.manufacturer} {product.model}")
                    results['errors'].append(f"No database match for {product.manufacturer} {product.model}")
                    continue
                
                # Store mapping for best match
                best_match = matching_arrows[0]
                logger.info(f"     Found matching arrow: {best_match['manufacturer']} {best_match['model_name']} (ID: {best_match['id']})")
                
                if self.store_retailer_url_mapping(best_match['id'], product):
                    results['stored_mappings'] += 1
                    results['successful_mappings'].append({
                        'url': url,
                        'product': {
                            'manufacturer': product.manufacturer,
                            'model': product.model,
                            'spine': product.spine
                        },
                        'matched_arrow': {
                            'id': best_match['id'],
                            'manufacturer': best_match['manufacturer'],
                            'model_name': best_match['model_name']
                        }
                    })
                
                results['matched_arrows'] += len(matching_arrows)
                
            except Exception as e:
                error_msg = f"Error processing {url}: {str(e)}"
                logger.error(f"     ❌ {error_msg}")
                results['errors'].append(error_msg)
            
            finally:
                results['processed_urls'] += 1
        
        # Calculate success rates
        results['match_rate'] = results['matched_arrows'] / results['processed_urls'] if results['processed_urls'] > 0 else 0
        results['storage_rate'] = results['stored_mappings'] / results['matched_arrows'] if results['matched_arrows'] > 0 else 0
        
        logger.info(f"✅ Completed processing for {manufacturer_filter}:")
        logger.info(f"   URLs processed: {results['processed_urls']}")
        logger.info(f"   Arrows matched: {results['matched_arrows']}")
        logger.info(f"   Mappings stored: {results['stored_mappings']}")
        logger.info(f"   Match rate: {results['match_rate']:.1%}")
        logger.info(f"   Storage rate: {results['storage_rate']:.1%}")
        
        return results
    
    def get_database_statistics(self) -> Dict[str, any]:
        """Get statistics about retailer data in database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Count retailer data entries
            cursor.execute("SELECT COUNT(*) FROM retailer_arrow_data")
            retailer_data_count = cursor.fetchone()[0]
            
            # Count unique arrows with retailer data
            cursor.execute("SELECT COUNT(DISTINCT arrow_id) FROM retailer_arrow_data")
            enhanced_arrows_count = cursor.fetchone()[0]
            
            # Get retailer sources
            cursor.execute("""
                SELECT rs.retailer_name, COUNT(rad.id) as arrow_count
                FROM retailer_sources rs
                LEFT JOIN retailer_arrow_data rad ON rs.id = rad.retailer_id
                GROUP BY rs.id
                ORDER BY arrow_count DESC
            """)
            retailer_stats = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_retailer_data_entries': retailer_data_count,
                'arrows_with_retailer_data': enhanced_arrows_count,
                'retailer_sources': [
                    {'name': name, 'arrow_count': count} 
                    for name, count in retailer_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            return {}

def main():
    """Test the simple sitemap processor"""
    processor = SimpleSitemapProcessor()
    
    print("🧪 Testing Simple Sitemap Processor")
    print("=" * 60)
    
    # 1. Analyze sitemap
    print("\n📊 Analyzing sitemap...")
    analysis = processor.analyze_sitemap()
    
    print(f"   Total URLs: {analysis['total_urls']:,}")
    print(f"   Manufacturers found: {len(analysis['manufacturers'])}")
    print("   Top manufacturers:")
    for manufacturer, count in list(analysis['manufacturers'].items())[:10]:
        print(f"     {manufacturer}: {count} products")
    
    # 2. Test URL parsing
    print("\n🔍 Testing URL parsing...")
    sample_urls = [
        "https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton/xx75/7260/easton-xx75-camo-hunter-2016",
        "https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton/axis/5mm/7050/easton-5mm-axis-spt-500"
    ]
    
    for url in sample_urls:
        product = processor.extract_product_info_from_url(url)
        if product:
            print(f"   URL: {url}")
            print(f"     Manufacturer: {product.manufacturer}")
            print(f"     Model: {product.model}")
            print(f"     Spine: {product.spine}")
            print(f"     Product: {product.product_name}")
    
    # 3. Test processing a small batch
    print("\n📦 Testing Easton manufacturer processing (5 URLs)...")
    result = processor.process_manufacturer_urls('easton', limit=5)
    
    print(f"   URLs processed: {result['processed_urls']}")
    print(f"   Arrows matched: {result['matched_arrows']}")
    print(f"   Mappings stored: {result['stored_mappings']}")
    
    if result['successful_mappings']:
        print("   Sample successful mappings:")
        for mapping in result['successful_mappings'][:3]:
            print(f"     {mapping['product']['manufacturer']} {mapping['product']['model']} -> Arrow ID {mapping['matched_arrow']['id']}")
    
    # 4. Show database statistics
    print("\n📊 Database statistics after processing...")
    stats = processor.get_database_statistics()
    
    print(f"   Total retailer data entries: {stats.get('total_retailer_data_entries', 0)}")
    print(f"   Arrows with retailer data: {stats.get('arrows_with_retailer_data', 0)}")
    print("   Retailer sources:")
    for retailer in stats.get('retailer_sources', []):
        print(f"     {retailer['name']}: {retailer['arrow_count']} arrows")

if __name__ == "__main__":
    main()