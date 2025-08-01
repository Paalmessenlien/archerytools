#!/usr/bin/env python3
"""
Component Scraper for Arrow Components

This script scrapes arrow component data from suppliers like Tophat Archery.
It extracts detailed specifications from German product pages and translates
them into a standardized English format.

Usage:
    python scrape_components.py --supplier "Tophat Archery" --limit 10
    python scrape_components.py --all --dry-run
    python scrape_components.py --import-from-sitemap docs/sitemap_non_komponentensuche.json
"""

import asyncio
import argparse
import json
import yaml
import logging
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup

# Try to import advanced scraping tools
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

@dataclass
class ComponentSpecification:
    """Data model for arrow component specifications"""
    component_id: str
    supplier: str
    name: str
    category: str
    type: str
    subcategory: Optional[str] = None
    material: Optional[str] = None
    weight_grain: Optional[float] = None
    weight_options: Optional[List[float]] = None
    inner_diameter_inch: Optional[float] = None
    inner_diameter_mm: Optional[float] = None
    outer_diameter_inch: Optional[float] = None
    outer_diameter_mm: Optional[float] = None
    length_mm: Optional[float] = None
    length_inch: Optional[float] = None
    thread_specification: Optional[str] = None
    color: Optional[str] = None
    finish: Optional[str] = None
    compatibility: Optional[List[str]] = None
    usage_type: Optional[str] = None
    price: Optional[str] = None
    availability: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    extracted_at: Optional[str] = None

class ComponentScraper:
    """Scraper for arrow component specifications"""
    
    def __init__(self, config_path: str = "config/components.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the component scraper"""
        logger = logging.getLogger("component_scraper")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def _load_config(self) -> Dict:
        """Load component configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def analyze_component_url(self, url: str, supplier_config: Dict) -> Dict[str, str]:
        """Analyze URL to determine component category and type"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        analysis = {
            'category': 'unknown',
            'subcategory': None,
            'usage_type': None,
            'component_type': 'unknown'
        }
        
        # Match against known categories
        categories = supplier_config.get('categories', {})
        for cat_name, cat_config in categories.items():
            pattern = cat_config.get('path_pattern', '')
            if pattern and pattern in path:
                analysis['category'] = cat_name
                analysis['component_type'] = cat_config.get('english_name', cat_name)
                
                # Check for subcategories
                subcats = cat_config.get('subcategories', {})
                for subcat_name, subcat_pattern in subcats.items():
                    if subcat_pattern in path:
                        analysis['subcategory'] = subcat_name
                        break
                break
        
        # Determine usage type from path
        if 'target' in path:
            analysis['usage_type'] = 'target'
        elif 'jagd' in path or 'hunt' in path:
            analysis['usage_type'] = 'hunting'
        elif 'field' in path:
            analysis['usage_type'] = 'field'
            
        return analysis
    
    async def scrape_component_page(self, url: str, supplier: str) -> Optional[ComponentSpecification]:
        """Scrape a single component page"""
        try:
            self.logger.info(f"🔍 Scraping component: {url}")
            
            supplier_config = self.config['component_suppliers'][supplier]
            
            # Get page content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Analyze URL for category information
            url_analysis = self.analyze_component_url(url, supplier_config)
            
            # Extract product name
            name = self._extract_product_name(soup)
            if not name:
                self.logger.warning(f"Could not extract product name from {url}")
                return None
            
            # Extract specifications from the properties table
            specifications = self._extract_specifications_table(soup, supplier_config)
            
            # Create component ID from URL
            component_id = self._generate_component_id(url, name)
            
            # Build component specification
            component = ComponentSpecification(
                component_id=component_id,
                supplier=supplier,
                name=name,
                category=url_analysis['category'],
                type=url_analysis['component_type'],
                subcategory=url_analysis['subcategory'],
                usage_type=url_analysis['usage_type'],
                source_url=url,
                extracted_at=datetime.now().isoformat()
            )
            
            # Apply extracted specifications
            self._apply_specifications(component, specifications, supplier_config)
            
            # Extract image URL
            component.image_url = self._extract_image_url(soup, url)
            
            # Extract description
            component.description = self._extract_description(soup)
            
            self.logger.info(f"✅ Successfully extracted: {component.name}")
            return component
            
        except Exception as e:
            self.logger.error(f"❌ Error scraping {url}: {e}")
            return None
    
    def _extract_product_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product name from page"""
        # Try multiple selectors for product name
        selectors = [
            'h1.product--title',
            '.product--title',
            'h1',
            '.product-name',
            '.product-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_specifications_table(self, soup: BeautifulSoup, supplier_config: Dict) -> Dict[str, str]:
        """Extract specifications from the product properties table"""
        specifications = {}
        
        # Find the properties table
        table = soup.select_one('.product--properties-table')
        if not table:
            return specifications
        
        # Extract all rows
        rows = table.select('.product--properties-row')
        for row in rows:
            label_elem = row.select_one('.product--properties-label')
            value_elem = row.select_one('.product--properties-value')
            
            if label_elem and value_elem:
                label = label_elem.get_text(strip=True).rstrip(':')
                value = value_elem.get_text(strip=True)
                
                if label and value:
                    specifications[label] = value
        
        return specifications
    
    def _apply_specifications(self, component: ComponentSpecification, specs: Dict[str, str], supplier_config: Dict):
        """Apply extracted specifications to component object"""
        translations = supplier_config.get('field_translations', {})
        material_trans = supplier_config.get('material_translations', {})
        color_trans = supplier_config.get('color_translations', {})
        
        for german_field, value in specs.items():
            english_field = translations.get(german_field)
            if not english_field:
                continue
                
            # Process different field types
            if english_field == 'type':
                component.type = value
            elif english_field == 'material':
                component.material = material_trans.get(value, value)
            elif english_field == 'color':
                component.color = color_trans.get(value, value)
            elif english_field == 'weight':
                weights = self._parse_weights(value)
                if len(weights) == 1:
                    component.weight_grain = weights[0]
                elif len(weights) > 1:
                    component.weight_options = weights
                    component.weight_grain = weights[0]  # Use first as primary
            elif english_field in ['inner_diameter', 'outer_diameter']:
                inch_val, mm_val = self._parse_diameter(value)
                if english_field == 'inner_diameter':
                    component.inner_diameter_inch = inch_val 
                    component.inner_diameter_mm = mm_val
                else:
                    component.outer_diameter_inch = inch_val
                    component.outer_diameter_mm = mm_val
            elif english_field == 'size':
                # Size often contains compatibility info
                if not component.compatibility:
                    component.compatibility = [value]
    
    def _parse_weights(self, weight_str: str) -> List[float]:
        """Parse weight values from German text"""
        # Pattern matches: "30, 50", "30gn", "120 grain", etc.
        pattern = r'(\d+(?:\.\d+)?)'
        matches = re.findall(pattern, weight_str)
        return [float(match) for match in matches]
    
    def _parse_diameter(self, diameter_str: str) -> Tuple[Optional[float], Optional[float]]:
        """Parse diameter values from strings like '.360", 9,14mm'"""
        inch_val = None
        mm_val = None
        
        # Match inch values like .360" or 0.360"
        inch_match = re.search(r'(\d*\.?\d+)"', diameter_str)
        if inch_match:
            inch_val = float(inch_match.group(1))
        
        # Match mm values like 9,14mm or 9.14mm
        mm_match = re.search(r'(\d+[,.]?\d*)\s*mm', diameter_str)
        if mm_match:
            mm_str = mm_match.group(1).replace(',', '.')
            mm_val = float(mm_str)
        
        return inch_val, mm_val
    
    def _generate_component_id(self, url: str, name: str) -> str:
        """Generate unique component ID"""
        # Extract ID from URL if present
        url_parts = url.split('/')
        if url_parts and url_parts[-1].isdigit():
            return f"tophat_{url_parts[-1]}"
        
        # Generate from name
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        return f"tophat_{clean_name}"[:50]
    
    def _extract_image_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract product image URL"""
        selectors = [
            '.product--image img',
            '.product-image img',
            '.product img',
            'img[alt*="product"]'
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                return urljoin(base_url, img['src'])
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description"""
        selectors = [
            '.product--description',
            '.product-description',
            '.description'
        ]
        
        for selector in selectors:
            desc = soup.select_one(selector)
            if desc:
                return desc.get_text(strip=True)[:500]  # Limit length
        
        return None
    
    def load_urls_from_sitemap(self, sitemap_path: str) -> List[str]:
        """Load component URLs from sitemap JSON file"""
        try:
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                sitemap_data = json.load(f)
            
            urls = []
            for entry in sitemap_data:
                url = entry.get('loc', '')
                # Filter for component URLs
                if 'komponenten-fuer-carbonpfeile' in url:
                    urls.append(url)
            
            self.logger.info(f"📂 Loaded {len(urls)} component URLs from sitemap")
            return urls
            
        except Exception as e:
            self.logger.error(f"Error loading sitemap: {e}")
            return []
    
    async def scrape_components(self, supplier: str, urls: List[str], limit: Optional[int] = None) -> List[ComponentSpecification]:
        """Scrape multiple component pages"""
        if limit:
            urls = urls[:limit]
        
        self.logger.info(f"🏗️ Scraping {len(urls)} components from {supplier}")
        
        components = []
        for i, url in enumerate(urls, 1):
            self.logger.info(f"📦 Processing component {i}/{len(urls)}")
            
            component = await self.scrape_component_page(url, supplier)
            if component:
                components.append(component)
            
            # Rate limiting
            settings = self.config.get('settings', {})
            delay = settings.get('rate_limit_delay', 2.0)
            await asyncio.sleep(delay)
        
        self.logger.info(f"✅ Successfully scraped {len(components)} components")
        return components
    
    def save_components(self, components: List[ComponentSpecification], supplier: str) -> bool:
        """Save components to JSON file"""
        try:
            # Create output directory
            settings = self.config.get('settings', {})
            output_dir = Path(settings.get('output', {}).get('directory', 'data/processed/components'))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create output structure
            output_data = {
                'supplier': supplier,
                'extracted_at': datetime.now().isoformat(),
                'total_components': len(components),
                'categories': {},
                'components': []
            }
            
            # Group by category for statistics
            for component in components:
                category = component.category
                if category not in output_data['categories']:
                    output_data['categories'][category] = 0
                output_data['categories'][category] += 1
                
                # Convert to dict
                output_data['components'].append(asdict(component))
            
            # Save to file
            filename = f"{supplier.lower().replace(' ', '_')}_components_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved {len(components)} components to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving components: {e}")
            return False

async def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description="Scrape arrow component specifications")
    parser.add_argument("--supplier", default="Tophat Archery", help="Component supplier name")
    parser.add_argument("--limit", type=int, help="Limit number of components to scrape")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be scraped")
    parser.add_argument("--import-from-sitemap", help="Import URLs from sitemap JSON file")
    parser.add_argument("--config", default="config/components.yaml", help="Config file path")
    
    args = parser.parse_args()
    
    scraper = ComponentScraper(args.config)
    
    # Get URLs
    if args.import_from_sitemap:
        urls = scraper.load_urls_from_sitemap(args.import_from_sitemap)
    else:
        # For now, we'll use sitemap as primary source
        urls = scraper.load_urls_from_sitemap("../docs/sitemap_non_komponentensuche.json")
    
    if not urls:
        print("No URLs found to scrape")
        return
    
    if args.dry_run:
        print(f"Would scrape {len(urls)} components:")
        for i, url in enumerate(urls[:10], 1):
            print(f"  {i}. {url}")
        if len(urls) > 10:
            print(f"  ... and {len(urls) - 10} more")
        return
    
    # Scrape components
    components = await scraper.scrape_components(args.supplier, urls, args.limit)
    
    if components:
        # Save results
        scraper.save_components(components, args.supplier)
        
        # Show summary
        print(f"\n📊 Component Scraping Summary:")
        print(f"   Supplier: {args.supplier}")
        print(f"   Total Components: {len(components)}")
        
        # Category breakdown
        categories = {}
        for comp in components:
            cat = comp.category
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"   Categories:")
        for cat, count in categories.items():
            print(f"     {cat}: {count} components")

if __name__ == "__main__":
    asyncio.run(main())