#!/usr/bin/env python3
"""
TopHat Archery Scraper
Scrapes arrow specifications from TopHat Archery German product pages
Uses sitemap_komponentensuche.json as source for URLs
"""

import json
import asyncio
import os
import sys
import re
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime

# Add crawl4ai to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'crawl4ai'))

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    from crawl4ai.async_configs import LLMConfig
except ImportError as e:
    print(f"Error importing crawl4ai: {e}")
    print("Please install crawl4ai dependencies")
    sys.exit(1)

# Add models path for translation
try:
    from models import TranslationService, SpineSpecification
except ImportError:
    # DeepSeek-based translation service
    class TranslationService:
        def __init__(self, api_key):
            self.api_key = api_key
        
        async def translate_text(self, text, source_lang='de', target_lang='en'):
            """Translate text using DeepSeek API"""
            try:
                import httpx
                
                # DeepSeek API endpoint
                url = "https://api.deepseek.com/v1/chat/completions"
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Create translation prompt
                prompt = f"""Translate this German archery text to English. Return ONLY the translated text with no additional comments, notes, or formatting.

RULES:
- Preserve exact measurements and numbers (±.001", 8.4 GPI, spine 300, etc.)
- Keep product names and brand names unchanged  
- Keep archery terms accurate (Target, 3D, Field, etc.)
- Return only the clean English translation

German text: {text}

English translation:"""

                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, headers=headers, json=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            translated_text = result['choices'][0]['message']['content'].strip()
                            
                            # Clean up the response - remove common formatting artifacts
                            # Remove quotes
                            if translated_text.startswith('"') and translated_text.endswith('"'):
                                translated_text = translated_text[1:-1]
                            
                            # Remove "English translation:" prefix if present
                            if translated_text.lower().startswith('english translation:'):
                                translated_text = translated_text[19:].strip()
                            
                            # Remove markdown formatting
                            translated_text = translated_text.replace('**', '').replace('*', '')
                            
                            # Clean up multiple spaces and newlines
                            translated_text = ' '.join(translated_text.split())
                            
                            # Remove any trailing notes or parenthetical comments
                            import re
                            # Remove content after "(Note:" or similar patterns
                            translated_text = re.sub(r'\s*\(Note:.*$', '', translated_text, flags=re.IGNORECASE | re.DOTALL)
                            translated_text = re.sub(r'\s*\*\*Key Notes.*$', '', translated_text, flags=re.IGNORECASE | re.DOTALL)
                            translated_text = re.sub(r'\s*Let me know.*$', '', translated_text, flags=re.IGNORECASE | re.DOTALL)
                            
                            return translated_text.strip()
                    else:
                        print(f"Translation API error: {response.status_code}")
                        return text  # Return original if translation fails
                        
            except Exception as e:
                print(f"Translation error: {e}")
                return text  # Return original text if translation fails
    
    # Simple spine specification for compatibility
    class SpineSpecification:
        pass

# Manual extraction fallback
import re
from bs4 import BeautifulSoup

class TopHatManualExtractor:
    """Manual extraction using regex and BeautifulSoup as fallback"""
    
    def extract_product_data(self, html: str, url: str) -> Optional[Dict]:
        """Extract product data from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            data = {}
            
            # Extract title
            title_elem = soup.find('h1', class_='product--title')
            if title_elem:
                data['title'] = title_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = soup.find('div', class_='product--description')
            if desc_elem:
                data['description'] = desc_elem.get_text(strip=True)
            
            # Extract specifications from properties table
            props_table = soup.find('table', class_='product--properties-table')
            if props_table:
                specs = self._extract_specifications(props_table)
                data.update(specs)
            
            # Extract spine from URL if not found in specs
            if 'spine' not in data:
                spine_match = re.search(r'-(\d{3,4})/?$', url)
                if spine_match:
                    data['spine'] = spine_match.group(1)
            
            # Extract manufacturer and model from title
            if 'title' in data:
                title_parts = data['title'].split()
                if len(title_parts) >= 2:
                    data['manufacturer'] = title_parts[0]
                    model_parts = title_parts[1:]
                    if model_parts and model_parts[-1].isdigit():
                        model_parts = model_parts[:-1]
                    data['model_name'] = ' '.join(model_parts) if model_parts else title_parts[1]
            
            # Extract price
            price_elem = soup.find('span', class_='price--content')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'([\d,]+)', price_text)
                if price_match:
                    data['price'] = price_match.group(1)
            
            # Extract image URL
            image_url = self._extract_image_url(soup)
            if image_url:
                data['image_url'] = image_url
            
            return data if data else None
            
        except Exception as e:
            return None
    
    def _extract_specifications(self, table) -> Dict:
        """Extract specifications from properties table"""
        specs = {}
        field_mapping = {
            'Spinewert': 'spine',
            'Pfeildurchmesser (Innen)': 'inner_diameter_raw',
            'Pfeildurchmesser (Außen)': 'outer_diameter_raw',
            'GPI (Grain per Inch)': 'gpi_weight',
            'Auslieferungslänge': 'length_options',
            'Material': 'material',
            'Geradheit': 'straightness_tolerance',
            'Marke': 'manufacturer',
            'Empfohlener Einsatzweck': 'arrow_type',
        }
        
        rows = table.find_all('tr', class_='product--properties-row')
        for row in rows:
            label_elem = row.find('td', class_='product--properties-label')
            value_elem = row.find('td', class_='product--properties-value')
            
            if label_elem and value_elem:
                label = label_elem.get_text(strip=True).rstrip(':')
                value = value_elem.get_text(strip=True)
                
                if label in field_mapping:
                    field_name = field_mapping[label]
                    
                    if field_name == 'inner_diameter_raw':
                        specs['inner_diameter'] = self._extract_diameter(value)
                    elif field_name == 'outer_diameter_raw':
                        specs['outer_diameter'] = self._extract_diameter(value)
                    elif field_name == 'gpi_weight':
                        specs['gpi_weight'] = self._extract_number(value)
                    elif field_name == 'length_options':
                        specs['length_options'] = [value] if value else []
                    else:
                        specs[field_name] = value
        
        return specs
    
    def _extract_diameter(self, value: str) -> Optional[float]:
        """Extract diameter in inches"""
        inch_match = re.search(r'(\d*\.\d+)"', value)
        if inch_match:
            return float(inch_match.group(1))
        mm_match = re.search(r'(\d+,\d+)mm', value)
        if mm_match:
            mm_value = float(mm_match.group(1).replace(',', '.'))
            return round(mm_value / 25.4, 3)
        return None
    
    def _extract_number(self, value: str) -> Optional[float]:
        """Extract number from string"""
        value = value.replace(',', '.')
        num_match = re.search(r'(\d+\.?\d*)', value)
        if num_match:
            return float(num_match.group(1))
        return None
    
    def _extract_image_url(self, soup) -> Optional[str]:
        """Extract product image URL from various sources"""
        try:
            # Method 1: Look for span.image--element with data attributes (highest quality)
            image_span = soup.find('span', class_='image--element')
            if image_span:
                # Try data-img-large first (highest quality)
                if image_span.get('data-img-large'):
                    return image_span.get('data-img-large')
                # Fallback to data-img-original
                if image_span.get('data-img-original'):
                    return image_span.get('data-img-original')
                # Fallback to data-img-small
                if image_span.get('data-img-small'):
                    return image_span.get('data-img-small')
            
            # Method 2: Look for img tag with itemprop="image"
            main_img = soup.find('img', {'itemprop': 'image'})
            if main_img and main_img.get('src'):
                src = main_img.get('src')
                # Convert relative URLs to absolute
                if src.startswith('/'):
                    src = 'https://tophatarchery.com' + src
                return src
            
            # Method 3: Look for any img in image container
            image_container = soup.find('div', class_='product--image-container')
            if image_container:
                img_tag = image_container.find('img')
                if img_tag and img_tag.get('src'):
                    src = img_tag.get('src')
                    # Convert relative URLs to absolute
                    if src.startswith('/'):
                        src = 'https://tophatarchery.com' + src
                    return src
            
            # Method 4: Look for meta property og:image
            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image and og_image.get('content'):
                return og_image.get('content')
            
            return None
            
        except Exception as e:
            return None

@dataclass
class TopHatProduct:
    """TopHat Archery product data structure"""
    url: str
    title: str
    description: str
    manufacturer: str
    model_name: str
    spine: Optional[str] = None
    outer_diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    gpi_weight: Optional[float] = None
    length_options: Optional[List[str]] = None
    material: Optional[str] = None
    arrow_type: Optional[str] = None
    straightness_tolerance: Optional[str] = None
    weight_tolerance: Optional[str] = None
    price: Optional[str] = None
    image_url: Optional[str] = None

class TopHatArcheryScraper:
    """Scraper for TopHat Archery using crawl4ai"""
    
    def __init__(self, deepseek_api_key: str, sitemap_path: str):
        self.deepseek_api_key = deepseek_api_key
        self.sitemap_path = sitemap_path
        self.translation_service = TranslationService(deepseek_api_key)
        self.manual_extractor = TopHatManualExtractor()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/tophat_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Initialize extraction strategy
        self.extraction_strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="deepseek",
                api_token=deepseek_api_key,
            ),
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Product title from h1.product--title"},
                    "description": {"type": "string", "description": "Product description from div.product--description"},
                    "manufacturer": {"type": "string", "description": "Arrow manufacturer name"},
                    "model_name": {"type": "string", "description": "Arrow model name"},
                    "spine": {"type": "string", "description": "Arrow spine value (e.g. 400, 500, 350)"},
                    "outer_diameter": {"type": "number", "description": "Outer diameter in mm"},
                    "inner_diameter": {"type": "number", "description": "Inner diameter in mm"},
                    "gpi_weight": {"type": "number", "description": "Grains per inch (GPI) weight"},
                    "length_options": {"type": "array", "items": {"type": "string"}, "description": "Available arrow lengths"},
                    "material": {"type": "string", "description": "Arrow material (Carbon, Aluminum, etc.)"},
                    "arrow_type": {"type": "string", "description": "Arrow type (target, hunting, 3D)"},
                    "straightness_tolerance": {"type": "string", "description": "Straightness tolerance specification"},
                    "weight_tolerance": {"type": "string", "description": "Weight tolerance specification"},
                    "price": {"type": "string", "description": "Product price"},
                    "image_url": {"type": "string", "description": "Main product image URL"},
                    "technical_specs": {
                        "type": "object",
                        "description": "Technical specifications from properties table",
                        "properties": {
                            "weight_gpi": {"type": "string"},
                            "diameter": {"type": "string"},
                            "spine": {"type": "string"},
                            "material": {"type": "string"},
                            "straightness": {"type": "string"}
                        }
                    }
                },
                "required": ["title", "manufacturer", "model_name"]
            },
            instruction="""
            Extract arrow specifications from this German TopHat Archery product page.
            
            IMPORTANT: Look for these specific elements in this exact order:
            
            1. TITLE: Extract from <h1 class="product--title" itemprop="name">TITLE_HERE</h1>
            
            2. DESCRIPTION: Extract from <div class="product--description" itemprop="description">DESCRIPTION_HERE</div>
            
            3. SPECIFICATIONS TABLE: Look for table with class "product--properties-table" containing these German terms:
               - "Spinewert" = spine value (extract the number, e.g., "300")
               - "Pfeildurchmesser (Innen)" = inner diameter (extract number in inches, e.g., ".246")
               - "Pfeildurchmesser (Außen)" = outer diameter (extract number in inches, e.g., ".297")
               - "GPI (Grain per Inch)" = gpi_weight (extract number, e.g., "8.4")
               - "Auslieferungslänge" = length (extract length like "33\"")
               - "Material" = material (e.g., "Carbon")
               - "Geradheit" = straightness tolerance
               - "Marke" = manufacturer/brand
               - "Empfohlener Einsatzweck" = arrow type/recommended use
            
            4. PRICE: Look for price in Euro format (e.g., "109,00€")
            
            5. MANUFACTURER: Extract from title or specifications table
            
            6. MODEL NAME: Extract model name from title (remove spine number)
            
            SPECIFIC EXTRACTION RULES:
            - For spine: Extract only the number from "Spinewert" row
            - For diameters: Convert from inches to millimeters if needed (multiply by 25.4)
            - For GPI: Extract as decimal number
            - For manufacturer: Look for brand name in title or "Marke" field
            - For model: Extract model name without spine (e.g., "Aurel Agil" from "Aurel Agil 300")
            
            Return all numeric values as numbers, not strings (except spine which should be string like "300").
            """
        )
    
    def load_sitemap_urls(self) -> List[str]:
        """Load URLs from sitemap JSON file"""
        try:
            with open(self.sitemap_path, 'r', encoding='utf-8') as f:
                sitemap_data = json.load(f)
            
            urls = [entry['loc'] for entry in sitemap_data if 'loc' in entry]
            self.logger.info(f"Loaded {len(urls)} URLs from sitemap")
            return urls
            
        except Exception as e:
            self.logger.error(f"Failed to load sitemap: {e}")
            return []
    
    async def scrape_product(self, url: str, session_crawler: AsyncWebCrawler) -> Optional[TopHatProduct]:
        """Scrape a single product page"""
        try:
            self.logger.info(f"Scraping: {url}")
            
            # Crawl the page
            result = await session_crawler.arun(
                url=url,
                extraction_strategy=self.extraction_strategy,
                bypass_cache=True
            )
            
            if not result.success:
                self.logger.error(f"Failed to crawl {url}: {result.error_message}")
                return None
            
            # Parse extracted data - try LLM first, then manual extraction
            extracted_data = None
            
            if result.extracted_content:
                try:
                    extracted_data = json.loads(result.extracted_content)
                    self.logger.info(f"LLM extraction successful for {url}")
                except json.JSONDecodeError:
                    self.logger.warning(f"LLM extraction failed to parse JSON from {url}, trying manual extraction")
                    extracted_data = None
            
            # Fallback to manual extraction
            if not extracted_data:
                self.logger.info(f"Using manual extraction for {url}")
                extracted_data = self.manual_extractor.extract_product_data(result.html, url)
                
                if not extracted_data:
                    self.logger.error(f"Both LLM and manual extraction failed for {url}")
                    return None
                else:
                    self.logger.info(f"Manual extraction successful for {url}")
            
            # Create product object
            product = TopHatProduct(
                url=url,
                title=extracted_data.get('title', ''),
                description=extracted_data.get('description', ''),
                manufacturer=extracted_data.get('manufacturer', ''),
                model_name=extracted_data.get('model_name', ''),
                spine=extracted_data.get('spine'),
                outer_diameter=extracted_data.get('outer_diameter'),
                inner_diameter=extracted_data.get('inner_diameter'),
                gpi_weight=extracted_data.get('gpi_weight'),
                length_options=extracted_data.get('length_options'),
                material=extracted_data.get('material'),
                arrow_type=extracted_data.get('arrow_type'),
                straightness_tolerance=extracted_data.get('straightness_tolerance'),
                weight_tolerance=extracted_data.get('weight_tolerance'),
                price=extracted_data.get('price'),
                image_url=extracted_data.get('image_url')
            )
            
            # Translate German content if needed
            await self._translate_product_content(product)
            
            return product
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
        
        return None
    
    async def _translate_product_content(self, product: TopHatProduct):
        """Translate German product content to English"""
        try:
            translations_made = []
            
            # Translate title if it contains German
            if product.title and self._is_german_text(product.title):
                self.logger.info(f"Translating title: {product.title[:50]}...")
                translated_title = await self.translation_service.translate_text(
                    product.title, source_lang='de', target_lang='en'
                )
                if translated_title and translated_title != product.title:
                    product.title = translated_title
                    translations_made.append("title")
            
            # Translate description if it contains German
            if product.description and self._is_german_text(product.description):
                self.logger.info(f"Translating description: {product.description[:50]}...")
                translated_desc = await self.translation_service.translate_text(
                    product.description, source_lang='de', target_lang='en'
                )
                if translated_desc and translated_desc != product.description:
                    product.description = translated_desc
                    translations_made.append("description")
            
            # Translate arrow_type if it contains German
            if product.arrow_type and self._is_german_text(product.arrow_type):
                self.logger.info(f"Translating arrow type: {product.arrow_type}")
                translated_type = await self.translation_service.translate_text(
                    product.arrow_type, source_lang='de', target_lang='en'
                )
                if translated_type and translated_type != product.arrow_type:
                    product.arrow_type = translated_type
                    translations_made.append("arrow_type")
            
            if translations_made:
                self.logger.info(f"Successfully translated: {', '.join(translations_made)}")
            else:
                self.logger.debug("No translation needed or no German text detected")
                    
        except Exception as e:
            self.logger.warning(f"Translation failed for product: {e}")
    
    def _is_german_text(self, text: str) -> bool:
        """Enhanced check if text contains German indicators"""
        if not text or len(text.strip()) < 10:
            return False  # Too short to reliably detect language
            
        german_indicators = [
            # Technical archery terms
            'durchmesser', 'gewicht', 'länge', 'toleranz', 'preis', 'material', 'spinewert',
            'geradheit', 'auslieferungslänge', 'einsatzweck', 'zuggewicht', 'bogenschießen',
            'zielscheibe', 'pfeil', 'schaft', 'bogen', 'schützen', 'präzision',
            
            # Common German words
            'für', 'und', 'mit', 'von', 'der', 'die', 'das', 'ist', 'sind', 'eine', 'einen',
            'werden', 'wurde', 'haben', 'wird', 'durch', 'auch', 'sehr', 'oder', 'als',
            'bei', 'auf', 'zu', 'einem', 'einer', 'kann', 'über', 'nach', 'im', 'am',
            
            # German-specific characters and patterns
            'ä', 'ö', 'ü', 'ß', 'dass', 'sich', 'nicht', 'mehr', 'beim', 'zum', 'zur'
        ]
        
        text_lower = text.lower()
        
        # Count German indicators
        german_count = sum(1 for indicator in german_indicators if indicator in text_lower)
        
        # Consider it German if we find multiple indicators
        return german_count >= 2
    
    def convert_to_arrow_format(self, products: List[TopHatProduct]) -> Dict[str, Any]:
        """Convert TopHat products to standard arrow import format"""
        
        # Group products by manufacturer and model
        arrow_specs = {}
        
        for product in products:
            if not product.manufacturer or not product.model_name:
                continue
            
            # Create unique arrow key
            arrow_key = f"{product.manufacturer}_{product.model_name.replace(' ', '_')}"
            
            if arrow_key not in arrow_specs:
                arrow_specs[arrow_key] = {
                    "manufacturer": product.manufacturer,
                    "model_name": product.model_name,
                    "spine_specifications": [],
                    "material": product.material or "Carbon",
                    "arrow_type": product.arrow_type or "target",
                    "description": product.description,
                    "image_url": product.image_url,
                    "price_range": product.price,
                    "straightness_tolerance": product.straightness_tolerance,
                    "weight_tolerance": product.weight_tolerance
                }
            
            # Add spine specification if spine data exists
            if product.spine:
                spine_spec = {
                    "spine": product.spine,
                    "outer_diameter": product.outer_diameter,
                    "inner_diameter": product.inner_diameter,
                    "gpi_weight": product.gpi_weight,
                    "length_options": product.length_options or ["30\"", "31\"", "32\""]  # Default lengths
                }
                
                # Check if this spine spec already exists
                existing_spines = [spec["spine"] for spec in arrow_specs[arrow_key]["spine_specifications"]]
                if product.spine not in existing_spines:
                    arrow_specs[arrow_key]["spine_specifications"].append(spine_spec)
        
        # Convert to list format expected by import system
        result_arrows = []
        for arrow_data in arrow_specs.values():
            if arrow_data["spine_specifications"]:  # Only include arrows with spine data
                result_arrows.append(arrow_data)
        
        return {
            "scraping_metadata": {
                "source": "TopHat Archery",
                "scrape_date": datetime.now().isoformat(),
                "total_products_found": len(products),
                "total_arrows_extracted": len(result_arrows),
                "scraper_version": "1.0.0"
            },
            "arrows": result_arrows
        }
    
    async def scrape_all_products(self, limit: Optional[int] = None) -> List[TopHatProduct]:
        """Scrape all products from sitemap URLs"""
        urls = self.load_sitemap_urls()
        
        if limit:
            urls = urls[:limit]
            self.logger.info(f"Limited to first {limit} URLs for testing")
        
        products = []
        
        async with AsyncWebCrawler() as crawler:
            for i, url in enumerate(urls, 1):
                self.logger.info(f"Processing {i}/{len(urls)}: {url}")
                
                product = await self.scrape_product(url, crawler)
                if product:
                    products.append(product)
                    self.logger.info(f"Successfully extracted: {product.manufacturer} {product.model_name} spine {product.spine}")
                else:
                    self.logger.warning(f"Failed to extract product from {url}")
                
                # Add delay to be respectful
                await asyncio.sleep(2)
                
                # Progress logging
                if i % 100 == 0:
                    self.logger.info(f"Progress: {i}/{len(urls)} URLs processed, {len(products)} products extracted")
        
        self.logger.info(f"Scraping complete: {len(products)} products extracted from {len(urls)} URLs")
        return products
    
    def save_results(self, products: List[TopHatProduct], output_file: str):
        """Save results to JSON file in arrow import format"""
        arrow_data = self.convert_to_arrow_format(products)
        
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(arrow_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {output_file}")
        self.logger.info(f"Total arrows: {len(arrow_data['arrows'])}")
        self.logger.info(f"Scraping metadata: {arrow_data['scraping_metadata']}")

async def main():
    """Main function to run the scraper"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    if not deepseek_api_key:
        print("Error: DEEPSEEK_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Paths
    sitemap_path = "../docs/sitemap_komponentensuche.json"
    output_file = "data/processed/extra/tophat_archery_arrows.json"
    
    # Initialize scraper
    scraper = TopHatArcheryScraper(deepseek_api_key, sitemap_path)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="TopHat Archery Scraper")
    parser.add_argument("--limit", type=int, help="Limit number of URLs to scrape (for testing)")
    parser.add_argument("--test", action="store_true", help="Test mode - scrape only 5 URLs")
    args = parser.parse_args()
    
    # Set limit
    limit = None
    if args.test:
        limit = 5
    elif args.limit:
        limit = args.limit
    
    print(f"🏹 TopHat Archery Scraper Starting...")
    print(f"📂 Sitemap: {sitemap_path}")
    print(f"💾 Output: {output_file}")
    if limit:
        print(f"🔢 Limit: {limit} URLs")
    print()
    
    try:
        # Scrape products
        products = await scraper.scrape_all_products(limit=limit)
        
        if products:
            # Save results
            scraper.save_results(products, output_file)
            
            # Print summary
            print(f"\n✅ Scraping completed successfully!")
            print(f"📊 Total products extracted: {len(products)}")
            print(f"💾 Results saved to: {output_file}")
            
            # Show sample products
            print(f"\n📋 Sample extracted products:")
            for i, product in enumerate(products[:3], 1):
                print(f"   {i}. {product.manufacturer} {product.model_name} - Spine {product.spine}")
            
        else:
            print("❌ No products were successfully extracted")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())