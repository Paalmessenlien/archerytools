#!/usr/bin/env python3
"""
Retailer Integration System for Arrow Tuning Platform
Coordinates scraping, matching, and data enhancement from multiple retailers
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3

from retailer_scraper import RetailerScraper, RetailerArrowData
from enhance_database_schema import enhance_database_schema, get_retailer_enhanced_data
from arrow_database import ArrowDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailerIntegrationManager:
    """Manages integration of retailer data with the arrow database"""
    
    def __init__(self, deepseek_api_key: str, db_path: str = "arrow_database.db"):
        self.scraper = RetailerScraper(deepseek_api_key)
        self.db_path = db_path
        self.db = ArrowDatabase(db_path)
        
        # Ensure enhanced schema exists
        enhance_database_schema(db_path)
        
        # Retailer-specific URL patterns and configurations
        self.retailer_patterns = {
            'tophatarchery.com': {
                'name': 'TopHat Archery',
                'search_patterns': [
                    'https://tophatarchery.com/komponentensuche-nach-schaft/marke/{manufacturer}/*/{model}*',
                    'https://tophatarchery.com/product/{manufacturer}-{model}*'
                ],
                'category_urls': {
                    'easton': 'https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton',
                    'goldtip': 'https://tophatarchery.com/komponentensuche-nach-schaft/marke/gold-tip',
                    'victory': 'https://tophatarchery.com/komponentensuche-nach-schaft/marke/victory'
                }
            },
            'lancasterarchery.com': {
                'name': 'Lancaster Archery',
                'search_patterns': [
                    'https://www.lancasterarchery.com/products/arrows/{manufacturer}-{model}*',
                    'https://www.lancasterarchery.com/products/{manufacturer}-{model}-arrows*'
                ],
                'category_urls': {
                    'easton': 'https://www.lancasterarchery.com/products/arrows/easton',
                    'goldtip': 'https://www.lancasterarchery.com/products/arrows/gold-tip'
                }
            }
        }
    
    async def enhance_arrow_with_retailer_data(self, arrow_id: int, retailer_urls: List[str] = None) -> Dict[str, Any]:
        """Enhance a specific arrow with retailer data from multiple sources"""
        try:
            logger.info(f"🔍 Enhancing arrow {arrow_id} with retailer data...")
            
            # Get existing arrow data
            arrow_details = self.db.get_arrow_details(arrow_id)
            if not arrow_details:
                logger.error(f"Arrow {arrow_id} not found in database")
                return {'success': False, 'error': 'Arrow not found'}
            
            manufacturer = arrow_details.get('manufacturer', '')
            model_name = arrow_details.get('model_name', '')
            
            logger.info(f"   Processing: {manufacturer} {model_name}")
            
            # If no specific URLs provided, search for them
            if not retailer_urls:
                retailer_urls = await self.find_retailer_urls(manufacturer, model_name)
            
            if not retailer_urls:
                logger.warning(f"No retailer URLs found for {manufacturer} {model_name}")
                return {'success': False, 'error': 'No retailer URLs found'}
            
            # Scrape data from each retailer
            enhancement_results = []
            for url in retailer_urls:
                try:
                    logger.info(f"   Scraping: {url}")
                    retailer_data = await self.scraper.scrape_retailer_product(url)
                    
                    if retailer_data:
                        # Store retailer data
                        stored = await self.store_retailer_data(arrow_id, retailer_data)
                        enhancement_results.append({
                            'retailer': retailer_data.retailer,
                            'url': url,
                            'success': stored,
                            'data_points': self._count_data_points(retailer_data)
                        })
                    else:
                        enhancement_results.append({
                            'retailer': 'Unknown',
                            'url': url,
                            'success': False,
                            'error': 'Failed to scrape data'
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    enhancement_results.append({
                        'retailer': 'Unknown',
                        'url': url,
                        'success': False,
                        'error': str(e)
                    })
            
            # Update arrow's last enhancement timestamp
            self._update_enhancement_timestamp(arrow_id)
            
            return {
                'success': True,
                'arrow_id': arrow_id,
                'manufacturer': manufacturer,
                'model_name': model_name,
                'retailer_enhancements': enhancement_results,
                'total_sources': len(enhancement_results),
                'successful_sources': len([r for r in enhancement_results if r['success']])
            }
            
        except Exception as e:
            logger.error(f"Error enhancing arrow {arrow_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def find_retailer_urls(self, manufacturer: str, model_name: str) -> List[str]:
        """Find retailer URLs for a specific arrow model"""
        urls = []
        
        # Clean manufacturer and model names for URL construction
        clean_manufacturer = manufacturer.lower().replace(' ', '-').replace('&', 'and')
        clean_model = model_name.lower().replace(' ', '-').replace('®', '').replace('™', '')
        
        # Search known retailer patterns
        for domain, config in self.retailer_patterns.items():
            for pattern in config['search_patterns']:
                # Simple pattern replacement
                url = pattern.format(
                    manufacturer=clean_manufacturer,
                    model=clean_model
                )
                urls.append(url)
        
        # Add specific known URLs (you can expand this with a database of known products)
        known_urls = self._get_known_retailer_urls(manufacturer, model_name)
        urls.extend(known_urls)
        
        logger.info(f"   Found {len(urls)} potential retailer URLs for {manufacturer} {model_name}")
        return urls
    
    def _get_known_retailer_urls(self, manufacturer: str, model_name: str) -> List[str]:
        """Get known retailer URLs from database or configuration"""
        # This could be expanded to check a database of known product URLs
        known_urls = []
        
        # Example hardcoded URLs for testing
        if 'easton' in manufacturer.lower() and 'axis' in model_name.lower():
            known_urls.append('https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton/5mm/7050/easton-5mm-axis-spt-500')
        
        return known_urls
    
    async def store_retailer_data(self, arrow_id: int, retailer_data: RetailerArrowData) -> bool:
        """Store retailer data in the enhanced database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get or create retailer source
            cursor.execute("""
                SELECT id FROM retailer_sources WHERE retailer_name = ?
            """, (retailer_data.retailer,))
            
            retailer_row = cursor.fetchone()
            if retailer_row:
                retailer_id = retailer_row[0]
            else:
                # Create new retailer source
                cursor.execute("""
                    INSERT INTO retailer_sources (retailer_name, base_url, language, currency)
                    VALUES (?, ?, ?, ?)
                """, (retailer_data.retailer, retailer_data.source_url, 'de', retailer_data.currency))
                retailer_id = cursor.lastrowid
            
            # Store/update retailer arrow data
            cursor.execute("""
                INSERT OR REPLACE INTO retailer_arrow_data (
                    arrow_id, retailer_id, source_url, price, currency, 
                    stock_quantity, availability_status, straightness_tolerance,
                    weight_tolerance, recommended_bow_types, intended_uses,
                    performance_notes, technical_notes, retailer_images,
                    product_description, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                arrow_id, retailer_id, retailer_data.source_url,
                retailer_data.price, retailer_data.currency,
                retailer_data.stock_quantity, retailer_data.availability_status,
                retailer_data.straightness_tolerance, retailer_data.weight_tolerance,
                json.dumps(retailer_data.recommended_bow_types),
                json.dumps(retailer_data.intended_uses),
                json.dumps(retailer_data.performance_notes),
                json.dumps(retailer_data.technical_notes),
                json.dumps(retailer_data.retailer_images),
                retailer_data.product_description,
                datetime.now().isoformat()
            ))
            
            # Store price history
            if retailer_data.price:
                cursor.execute("""
                    INSERT INTO price_history (
                        arrow_id, retailer_id, price, currency, 
                        stock_quantity, availability_status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    arrow_id, retailer_id, retailer_data.price,
                    retailer_data.currency, retailer_data.stock_quantity,
                    retailer_data.availability_status
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored retailer data for arrow {arrow_id} from {retailer_data.retailer}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing retailer data: {e}")
            return False
    
    def _count_data_points(self, retailer_data: RetailerArrowData) -> int:
        """Count the number of useful data points scraped"""
        count = 0
        
        # Count non-empty fields
        fields_to_check = [
            'spine', 'outer_diameter', 'inner_diameter', 'gpi_weight',
            'price', 'stock_quantity', 'straightness_tolerance',
            'weight_tolerance', 'product_description'
        ]
        
        for field in fields_to_check:
            if getattr(retailer_data, field) is not None:
                count += 1
        
        # Count array fields
        array_fields = [
            'length_options', 'recommended_bow_types', 'intended_uses',
            'performance_notes', 'technical_notes', 'retailer_images'
        ]
        
        for field in array_fields:
            field_value = getattr(retailer_data, field)
            if field_value and len(field_value) > 0:
                count += 1
        
        return count
    
    def _update_enhancement_timestamp(self, arrow_id: int):
        """Update the last enhancement timestamp for an arrow"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update or create enhancement record
            cursor.execute("""
                INSERT OR REPLACE INTO arrow_enhancements (arrow_id, updated_at)
                VALUES (?, ?)
            """, (arrow_id, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating enhancement timestamp: {e}")
    
    async def batch_enhance_arrows(self, manufacturer: str = None, limit: int = 10) -> Dict[str, Any]:
        """Enhance multiple arrows with retailer data"""
        try:
            logger.info(f"🚀 Starting batch enhancement of arrows...")
            
            # Get arrows to enhance
            search_params = {'limit': limit}
            if manufacturer:
                search_params['manufacturer'] = manufacturer
            
            arrows = self.db.search_arrows(**search_params)
            
            if not arrows:
                return {'success': False, 'error': 'No arrows found to enhance'}
            
            logger.info(f"   Found {len(arrows)} arrows to enhance")
            
            # Process each arrow
            enhancement_results = []
            for arrow in arrows:
                result = await self.enhance_arrow_with_retailer_data(arrow['id'])
                enhancement_results.append(result)
                
                # Add delay to be respectful to retailers
                await asyncio.sleep(2)
            
            # Calculate summary statistics
            successful_enhancements = [r for r in enhancement_results if r.get('success', False)]
            total_retailer_sources = sum(r.get('total_sources', 0) for r in enhancement_results)
            successful_sources = sum(r.get('successful_sources', 0) for r in enhancement_results)
            
            return {
                'success': True,
                'total_arrows_processed': len(arrows),
                'successful_enhancements': len(successful_enhancements),
                'total_retailer_sources_attempted': total_retailer_sources,
                'successful_retailer_sources': successful_sources,
                'enhancement_details': enhancement_results
            }
            
        except Exception as e:
            logger.error(f"Error in batch enhancement: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_enhanced_arrow_data(self, arrow_id: int) -> Dict[str, Any]:
        """Get arrow data enhanced with all retailer information"""
        return get_retailer_enhanced_data(self.db_path, arrow_id)

async def main():
    """Test the retailer integration system"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
    manager = RetailerIntegrationManager(api_key)
    
    print("🧪 Testing Retailer Integration System")
    print("=" * 50)
    
    # Test enhancing a specific arrow (if exists)
    # This would typically be an arrow ID from your database
    test_arrow_id = 1
    
    # Test with specific retailer URL
    test_urls = [
        "https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton/5mm/7050/easton-5mm-axis-spt-500"
    ]
    
    result = await manager.enhance_arrow_with_retailer_data(test_arrow_id, test_urls)
    
    print(f"Enhancement result: {json.dumps(result, indent=2)}")
    
    # Get enhanced data
    enhanced_data = manager.get_enhanced_arrow_data(test_arrow_id)
    print(f"\nEnhanced data summary:")
    print(f"   Retailer sources: {len(enhanced_data.get('retailer_data', []))}")
    print(f"   Price history entries: {len(enhanced_data.get('price_history', []))}")

if __name__ == "__main__":
    asyncio.run(main())