#!/usr/bin/env python3
"""
Retailer Scraper for Arrow Tuning System
Scrapes complementary arrow data from retailers and distributors to enhance manufacturer data
"""

import sys
import re
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import logging

# Add crawl4ai to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "crawl4ai"))

# Import Crawl4AI components
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

# Import our existing models and database
from models import ArrowSpecification
from arrow_database import ArrowDatabase
from deepseek_extractor import DeepSeekExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RetailerArrowData:
    """Enhanced arrow data from retailer sites"""
    # Basic identification
    manufacturer: str
    model_name: str
    retailer: str
    source_url: str
    
    # Technical specifications (enhanced)
    spine: Optional[int] = None
    outer_diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    gpi_weight: Optional[float] = None
    straightness_tolerance: Optional[str] = None
    weight_tolerance: Optional[str] = None
    length_options: List[float] = field(default_factory=list)
    
    # Retailer-specific data
    price: Optional[float] = None
    currency: str = "EUR"
    stock_quantity: Optional[int] = None
    availability_status: str = "unknown"
    
    # Performance data
    recommended_bow_types: List[str] = field(default_factory=list)
    intended_uses: List[str] = field(default_factory=list)
    performance_notes: List[str] = field(default_factory=list)
    
    # Images and additional data
    retailer_images: List[str] = field(default_factory=list)
    product_description: Optional[str] = None
    technical_notes: List[str] = field(default_factory=list)
    
    # Metadata
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
    scraping_success: bool = True
    scraping_errors: List[str] = field(default_factory=list)

class RetailerScraper:
    """Scraper for retailer/distributor arrow data"""
    
    def __init__(self, deepseek_api_key: str):
        self.deepseek_extractor = DeepSeekExtractor(deepseek_api_key)
        self.db = ArrowDatabase()
        
        # Retailer-specific configurations
        self.retailer_configs = {
            'tophatarchery.com': {
                'name': 'TopHat Archery',
                'language': 'de',
                'currency': 'EUR',
                'selectors': {
                    'spine': '[data-spine], .spine-value, .product-spine',
                    'diameter': '[data-diameter], .diameter-value',
                    'price': '.price, [data-price], .product-price',
                    'stock': '[data-stock], .stock-status, .availability'
                }
            }
        }
    
    async def scrape_retailer_product(self, url: str) -> Optional[RetailerArrowData]:
        """Scrape a single retailer product page"""
        try:
            logger.info(f"🛒 Scraping retailer product: {url}")
            
            # Determine retailer from URL
            retailer_key = self._get_retailer_key(url)
            if not retailer_key:
                logger.warning(f"Unknown retailer for URL: {url}")
                return None
            
            retailer_config = self.retailer_configs[retailer_key]
            
            # Configure extraction strategy for retailer data
            extraction_schema = {
                "type": "object",
                "properties": {
                    "manufacturer": {
                        "type": "string",
                        "description": "Arrow manufacturer (e.g., Easton, Gold Tip, Victory)"
                    },
                    "model_name": {
                        "type": "string", 
                        "description": "Full arrow model name"
                    },
                    "spine": {
                        "type": "integer",
                        "description": "Arrow spine value (e.g., 340, 500, 600)"
                    },
                    "outer_diameter": {
                        "type": "number",
                        "description": "Outer diameter in inches (convert from mm if needed)"
                    },
                    "inner_diameter": {
                        "type": "number", 
                        "description": "Inner diameter in inches (convert from mm if needed)"
                    },
                    "gpi_weight": {
                        "type": "number",
                        "description": "Weight in grains per inch (GPI)"
                    },
                    "straightness_tolerance": {
                        "type": "string",
                        "description": "Straightness tolerance (e.g., ±.006\", ±.003\")"
                    },
                    "weight_tolerance": {
                        "type": "string",
                        "description": "Weight tolerance if specified"
                    },
                    "length_options": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Available arrow lengths in inches"
                    },
                    "price": {
                        "type": "number",
                        "description": "Price as decimal number"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (EUR, USD, etc.)"
                    },
                    "stock_quantity": {
                        "type": "integer",
                        "description": "Available stock quantity"
                    },
                    "availability_status": {
                        "type": "string",
                        "description": "Stock status (in_stock, out_of_stock, limited, etc.)"
                    },
                    "recommended_bow_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Recommended bow types (compound, recurve, traditional, etc.)"
                    },
                    "intended_uses": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Intended uses (3D, field, hunting, target, etc.)"
                    },
                    "performance_notes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Performance characteristics and notes"
                    },
                    "product_description": {
                        "type": "string",
                        "description": "Full product description"
                    },
                    "technical_notes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional technical specifications and notes"
                    }
                },
                "required": ["manufacturer", "model_name"]
            }
            
            # Create extraction strategy
            extraction_strategy = LLMExtractionStrategy(
                provider="openai",
                api_token=self.deepseek_extractor.api_key,
                schema=extraction_schema,
                extraction_type="schema",
                instruction=f"""
                Extract detailed arrow specifications from this {retailer_config['name']} product page.
                
                Focus on:
                1. Complete technical specifications (spine, diameters, weight, tolerances)
                2. Pricing and availability information
                3. Recommended uses and bow types
                4. Performance characteristics
                5. Any additional technical details not found on manufacturer sites
                
                Convert metric measurements to inches where needed (1mm = 0.0394 inches).
                Extract all available spine options if multiple are shown.
                Include performance recommendations and technical notes.
                """
            )
            
            # Crawl the page
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    bypass_cache=True,
                    js_code=None,  # May need custom JS for dynamic content
                    wait_for="css:.product-details"  # Wait for product details to load
                )
                
                if not result.success:
                    logger.error(f"Failed to crawl {url}: {result.error_message}")
                    return None
                
                # Parse extracted data
                try:
                    extracted_data = json.loads(result.extracted_content)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse extracted data: {e}")
                    return None
                
                # Create RetailerArrowData object
                retailer_data = RetailerArrowData(
                    manufacturer=extracted_data.get('manufacturer', ''),
                    model_name=extracted_data.get('model_name', ''),
                    retailer=retailer_config['name'],
                    source_url=url,
                    spine=extracted_data.get('spine'),
                    outer_diameter=extracted_data.get('outer_diameter'),
                    inner_diameter=extracted_data.get('inner_diameter'),
                    gpi_weight=extracted_data.get('gpi_weight'),
                    straightness_tolerance=extracted_data.get('straightness_tolerance'),
                    weight_tolerance=extracted_data.get('weight_tolerance'),
                    length_options=extracted_data.get('length_options', []),
                    price=extracted_data.get('price'),
                    currency=extracted_data.get('currency', retailer_config['currency']),
                    stock_quantity=extracted_data.get('stock_quantity'),
                    availability_status=extracted_data.get('availability_status', 'unknown'),
                    recommended_bow_types=extracted_data.get('recommended_bow_types', []),
                    intended_uses=extracted_data.get('intended_uses', []),
                    performance_notes=extracted_data.get('performance_notes', []),
                    product_description=extracted_data.get('product_description'),
                    technical_notes=extracted_data.get('technical_notes', [])
                )
                
                logger.info(f"✅ Successfully scraped retailer data for {retailer_data.manufacturer} {retailer_data.model_name}")
                return retailer_data
                
        except Exception as e:
            logger.error(f"Error scraping retailer product {url}: {e}")
            return None
    
    def _get_retailer_key(self, url: str) -> Optional[str]:
        """Get retailer configuration key from URL"""
        for key in self.retailer_configs.keys():
            if key in url:
                return key
        return None
    
    def match_with_existing_arrow(self, retailer_data: RetailerArrowData) -> Optional[Dict[str, Any]]:
        """Match retailer data with existing arrow in database"""
        try:
            # Search for matching arrows in database
            potential_matches = self.db.search_arrows(
                manufacturer=retailer_data.manufacturer,
                model_search=retailer_data.model_name,
                limit=10
            )
            
            if not potential_matches:
                logger.info(f"No existing matches found for {retailer_data.manufacturer} {retailer_data.model_name}")
                return None
            
            # Find best match using fuzzy matching
            best_match = None
            best_score = 0
            
            for arrow in potential_matches:
                score = self._calculate_match_score(retailer_data, arrow)
                if score > best_score:
                    best_score = score
                    best_match = arrow
            
            if best_match and best_score > 0.7:  # 70% similarity threshold
                logger.info(f"✅ Matched with existing arrow: {best_match['manufacturer']} {best_match['model_name']} (score: {best_score:.2f})")
                return best_match
            else:
                logger.info(f"No good match found (best score: {best_score:.2f})")
                return None
                
        except Exception as e:
            logger.error(f"Error matching retailer data: {e}")
            return None
    
    def _calculate_match_score(self, retailer_data: RetailerArrowData, db_arrow: Dict[str, Any]) -> float:
        """Calculate similarity score between retailer data and database arrow"""
        score = 0.0
        
        # Manufacturer match (high weight)
        if retailer_data.manufacturer.lower() == db_arrow.get('manufacturer', '').lower():
            score += 0.4
        
        # Model name similarity (high weight)
        retailer_model = retailer_data.model_name.lower()
        db_model = db_arrow.get('model_name', '').lower()
        
        # Simple substring matching
        if retailer_model in db_model or db_model in retailer_model:
            score += 0.4
        elif any(word in db_model for word in retailer_model.split()):
            score += 0.2
        
        # Spine match (medium weight)
        if retailer_data.spine and db_arrow.get('min_spine'):
            db_min_spine = db_arrow.get('min_spine', 0)
            db_max_spine = db_arrow.get('max_spine', 0)
            if db_min_spine <= retailer_data.spine <= db_max_spine:
                score += 0.2
        
        return score
    
    def enhance_existing_arrow(self, arrow_id: int, retailer_data: RetailerArrowData) -> bool:
        """Add retailer data to existing arrow record"""
        try:
            # Get existing arrow details
            arrow_details = self.db.get_arrow_details(arrow_id)
            if not arrow_details:
                return False
            
            # Enhance with retailer data
            enhancement_data = {
                'retailer_info': {
                    'retailer': retailer_data.retailer,
                    'source_url': retailer_data.source_url,
                    'price': retailer_data.price,
                    'currency': retailer_data.currency,
                    'stock_quantity': retailer_data.stock_quantity,
                    'availability_status': retailer_data.availability_status,
                    'scraped_at': retailer_data.scraped_at
                },
                'enhanced_specs': {
                    'straightness_tolerance': retailer_data.straightness_tolerance,
                    'weight_tolerance': retailer_data.weight_tolerance,
                    'recommended_bow_types': retailer_data.recommended_bow_types,
                    'intended_uses': retailer_data.intended_uses,
                    'performance_notes': retailer_data.performance_notes,
                    'technical_notes': retailer_data.technical_notes
                }
            }
            
            # Store enhancement data (you'll need to extend database schema)
            # For now, we'll store as JSON in a new field
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Add retailer enhancement data
            cursor.execute("""
                UPDATE arrows 
                SET retailer_data = ?
                WHERE id = ?
            """, (json.dumps(enhancement_data), arrow_id))
            
            conn.commit()
            
            logger.info(f"✅ Enhanced arrow {arrow_id} with retailer data from {retailer_data.retailer}")
            return True
            
        except Exception as e:
            logger.error(f"Error enhancing arrow {arrow_id}: {e}")
            return False

async def main():
    """Test the retailer scraper"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
    scraper = RetailerScraper(api_key)
    
    # Test URL
    test_url = "https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton/5mm/7050/easton-5mm-axis-spt-500"
    
    print(f"🧪 Testing retailer scraper with: {test_url}")
    
    retailer_data = await scraper.scrape_retailer_product(test_url)
    
    if retailer_data:
        print(f"✅ Successfully scraped retailer data:")
        print(f"   Manufacturer: {retailer_data.manufacturer}")
        print(f"   Model: {retailer_data.model_name}")
        print(f"   Spine: {retailer_data.spine}")
        print(f"   Price: {retailer_data.price} {retailer_data.currency}")
        print(f"   Stock: {retailer_data.stock_quantity}")
        
        # Try to match with existing data
        match = scraper.match_with_existing_arrow(retailer_data)
        if match:
            print(f"🎯 Found matching arrow in database: {match['manufacturer']} {match['model_name']}")
        else:
            print("❌ No matching arrow found in database")
    else:
        print("❌ Failed to scrape retailer data")

if __name__ == "__main__":
    asyncio.run(main())