#!/usr/bin/env python3
"""
Component Extractors for Arrow Scraper
Specialized extractors for different component types (points, nocks, fletchings, inserts)
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse
from pathlib import Path

class BaseComponentExtractor(ABC):
    """Base class for component extractors"""
    
    def __init__(self, component_type: str):
        self.component_type = component_type
        self.common_measurements = {
            'weights': r'(\d+(?:\.\d+)?)\s*(?:gr|grain|grains)',
            'diameters': r'(\d+(?:\.\d+)?)\s*(?:"|inch|inches|mm)',
            'lengths': r'(\d+(?:\.\d+)?)\s*(?:"|inch|inches|mm)',
            'thread_sizes': r'(\d+[-/]\d+|M\d+(?:x\d+)?)',
            'prices': r'\$(\d+(?:\.\d+)?)'
        }
    
    @abstractmethod
    def extract_specifications(self, content: str, url: str) -> Dict[str, Any]:
        """Extract component-specific specifications"""
        pass
    
    def extract_component_data(self, html: str, url: str) -> List[Dict[str, Any]]:
        """Extract component data from HTML content"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Get basic information
            manufacturer = self._extract_manufacturer(soup, url)
            components = []
            
            # Look for product containers
            product_containers = self._find_product_containers(soup)
            
            if not product_containers:
                # Try single product page
                component = self._extract_single_product(soup, url, manufacturer)
                if component:
                    components.append(component)
            else:
                # Multiple products page
                for container in product_containers:
                    component = self._extract_product_from_container(container, url, manufacturer)
                    if component:
                        components.append(component)
            
            print(f"🔍 Extracted {len(components)} {self.component_type} from {url}")
            return components
            
        except Exception as e:
            print(f"❌ Error extracting {self.component_type}: {e}")
            return []
    
    def _extract_manufacturer(self, soup: BeautifulSoup, url: str) -> str:
        """Extract manufacturer name from page or URL"""
        # Try meta tags first
        for meta in soup.find_all('meta', {'name': ['author', 'brand', 'manufacturer']}):
            if meta.get('content'):
                return meta['content'].strip()
        
        # Try common selectors
        selectors = [
            '.brand', '.manufacturer', '.company-name',
            '[data-brand]', '[data-manufacturer]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        # Extract from URL
        domain = urlparse(url).netloc
        if domain:
            # Remove common prefixes/suffixes
            domain = domain.replace('www.', '').replace('.com', '').replace('.net', '').replace('.org', '')
            return domain.title()
        
        return "Unknown"
    
    def _find_product_containers(self, soup: BeautifulSoup) -> List:
        """Find containers that hold product information"""
        # Common product container selectors
        selectors = [
            '.product', '.item', '.component',
            '[data-product]', '[data-item]',
            '.product-card', '.product-item', '.product-list-item',
            '.grid-item', '.catalog-item'
        ]
        
        containers = []
        for selector in selectors:
            found = soup.select(selector)
            if found and len(found) > 1:  # Multiple products
                containers.extend(found)
                break
        
        return containers[:20]  # Limit to 20 products per page
    
    def _extract_single_product(self, soup: BeautifulSoup, url: str, manufacturer: str) -> Optional[Dict[str, Any]]:
        """Extract data from single product page"""
        try:
            # Get product title
            title = self._extract_title(soup)
            if not title:
                return None
            
            # Get description
            description = self._extract_description(soup)
            
            # Get specifications using the abstract method
            specifications = self.extract_specifications(soup.get_text(), url)
            
            # Get image
            image_url = self._extract_image(soup, url)
            
            # Get price
            price_range = self._extract_price(soup)
            
            return {
                'manufacturer': manufacturer,
                'model_name': title,
                'specifications': specifications,
                'description': description,
                'image_url': image_url,
                'price_range': price_range,
                'source_url': url,
                'category': self.component_type
            }
            
        except Exception as e:
            print(f"⚠️  Error extracting single product: {e}")
            return None
    
    def _extract_product_from_container(self, container, url: str, manufacturer: str) -> Optional[Dict[str, Any]]:
        """Extract product data from container element"""
        try:
            # Get title from container
            title = self._extract_title_from_container(container)
            if not title:
                return None
            
            # Get description
            description = self._extract_description_from_container(container)
            
            # Get specifications
            specifications = self.extract_specifications(container.get_text(), url)
            
            # Get image
            image_url = self._extract_image_from_container(container, url)
            
            # Get price
            price_range = self._extract_price_from_container(container)
            
            return {
                'manufacturer': manufacturer,
                'model_name': title,
                'specifications': specifications,
                'description': description,
                'image_url': image_url,
                'price_range': price_range,
                'source_url': url,
                'category': self.component_type
            }
            
        except Exception as e:
            print(f"⚠️  Error extracting from container: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title"""
        selectors = [
            'h1', '.product-title', '.product-name', '.title',
            '[data-product-name]', '.name', '.model'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return None
    
    def _extract_title_from_container(self, container) -> Optional[str]:
        """Extract title from product container"""
        selectors = [
            '.title', '.name', '.product-name', '.model',
            'h2', 'h3', 'h4', '.heading'
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description"""
        selectors = [
            '.description', '.product-description', '.details',
            '.summary', '.overview', '.about'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)[:500]  # Limit length
        
        return None
    
    def _extract_description_from_container(self, container) -> Optional[str]:
        """Extract description from container"""
        selectors = [
            '.description', '.details', '.summary', 'p'
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)[:200]  # Shorter for containers
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract product image URL"""
        selectors = [
            '.product-image img', '.main-image img', '.hero-image img',
            '.gallery img', '.thumbnail img', 'img[data-product]'
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                return urljoin(base_url, img['src'])
        
        return None
    
    def _extract_image_from_container(self, container, base_url: str) -> Optional[str]:
        """Extract image from container"""
        img = container.select_one('img')
        if img and img.get('src'):
            return urljoin(base_url, img['src'])
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract price information"""
        selectors = [
            '.price', '.cost', '.msrp', '[data-price]',
            '.product-price', '.price-range'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        return None
    
    def _extract_price_from_container(self, container) -> Optional[str]:
        """Extract price from container"""
        price_element = container.select_one('.price, .cost')
        if price_element:
            return price_element.get_text(strip=True)
        return None
    
    def extract_measurement(self, text: str, measurement_type: str) -> List[str]:
        """Extract measurements from text"""
        pattern = self.common_measurements.get(measurement_type)
        if pattern:
            matches = re.findall(pattern, text, re.IGNORECASE)
            return matches
        return []

class PointExtractor(BaseComponentExtractor):
    """Extractor for arrow points (field points, broadheads, etc.)"""
    
    def __init__(self):
        super().__init__('points')
    
    def extract_specifications(self, content: str, url: str) -> Dict[str, Any]:
        """Extract point-specific specifications"""
        specs = {}
        content_lower = content.lower()
        
        # Extract weight
        weights = self.extract_measurement(content, 'weights')
        if weights:
            specs['weight'] = f"{weights[0]}gr"
        
        # Extract thread type
        thread_matches = re.findall(r'(8-32|5/16-24|M\d+x\d+)', content, re.IGNORECASE)
        if thread_matches:
            specs['thread_type'] = thread_matches[0]
        
        # Extract diameter
        diameters = self.extract_measurement(content, 'diameters')
        if diameters:
            specs['diameter'] = float(diameters[0])
        
        # Extract length
        lengths = self.extract_measurement(content, 'lengths')
        if lengths:
            specs['length'] = float(lengths[0])
        
        # Determine point type
        if 'broadhead' in content_lower:
            specs['point_type'] = 'broadhead'
        elif 'field' in content_lower:
            specs['point_type'] = 'field'
        elif 'blunt' in content_lower:
            specs['point_type'] = 'blunt'
        elif 'judo' in content_lower:
            specs['point_type'] = 'judo'
        else:
            specs['point_type'] = 'unknown'
        
        # Extract material
        if 'stainless' in content_lower:
            specs['material'] = 'stainless_steel'
        elif 'carbon steel' in content_lower:
            specs['material'] = 'carbon_steel'
        elif 'aluminum' in content_lower:
            specs['material'] = 'aluminum'
        
        return specs

class NockExtractor(BaseComponentExtractor):
    """Extractor for arrow nocks"""
    
    def __init__(self):
        super().__init__('nocks')
    
    def extract_specifications(self, content: str, url: str) -> Dict[str, Any]:
        """Extract nock-specific specifications"""
        specs = {}
        content_lower = content.lower()
        
        # Extract nock size (common sizes)
        nock_sizes = re.findall(r'(0\.244|0\.246|0\.300|\.244|\.246|\.300)', content)
        if nock_sizes:
            specs['nock_size'] = nock_sizes[0].replace('.', '0.') if not nock_sizes[0].startswith('0.') else nock_sizes[0]
        
        # Extract fit type
        if 'push in' in content_lower or 'push-in' in content_lower:
            specs['fit_type'] = 'push_in'
        elif 'snap on' in content_lower or 'snap-on' in content_lower:
            specs['fit_type'] = 'snap_on'
        elif 'pin' in content_lower:
            specs['fit_type'] = 'pin'
        
        # Extract material
        if 'plastic' in content_lower:
            specs['material'] = 'plastic'
        elif 'aluminum' in content_lower:
            specs['material'] = 'aluminum'
        
        # Extract weight
        weights = self.extract_measurement(content, 'weights')
        if weights:
            specs['weight'] = f"{weights[0]}gr"
        
        # Extract colors (common nock colors)
        colors = []
        color_keywords = ['red', 'yellow', 'green', 'blue', 'orange', 'white', 'black', 'pink', 'purple']
        for color in color_keywords:
            if color in content_lower:
                colors.append(color)
        if colors:
            specs['colors'] = colors
        
        return specs

class FletchingExtractor(BaseComponentExtractor):
    """Extractor for arrow fletching (vanes and feathers)"""
    
    def __init__(self):
        super().__init__('fletchings')
    
    def extract_specifications(self, content: str, url: str) -> Dict[str, Any]:
        """Extract fletching-specific specifications"""
        specs = {}
        content_lower = content.lower()
        
        # Extract length
        lengths = self.extract_measurement(content, 'lengths')
        if lengths:
            specs['length'] = float(lengths[0])
        
        # Extract height
        height_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:"|inch)?\s*(?:high|height)', content_lower)
        if height_matches:
            specs['height'] = float(height_matches[0])
        
        # Extract material
        if 'feather' in content_lower:
            specs['material'] = 'feather'
        elif 'plastic' in content_lower or 'vane' in content_lower:
            specs['material'] = 'plastic'
        
        # Extract profile
        if 'low profile' in content_lower:
            specs['profile'] = 'low'
        elif 'high profile' in content_lower:
            specs['profile'] = 'high'
        elif 'parabolic' in content_lower:
            specs['profile'] = 'parabolic'
        
        # Extract attachment method
        if 'adhesive' in content_lower:
            specs['attachment'] = 'adhesive'
        elif 'wrap' in content_lower:
            specs['attachment'] = 'wrap'
        
        # Extract colors
        colors = []
        color_keywords = ['white', 'orange', 'yellow', 'red', 'green', 'blue', 'black', 'pink']
        for color in color_keywords:
            if color in content_lower:
                colors.append(color)
        if colors:
            specs['colors'] = colors
        
        # Extract weight
        weights = self.extract_measurement(content, 'weights')
        if weights:
            specs['weight'] = f"{weights[0]}gr"
        
        return specs

class InsertExtractor(BaseComponentExtractor):
    """Extractor for arrow inserts and outserts"""
    
    def __init__(self):
        super().__init__('inserts')
    
    def extract_specifications(self, content: str, url: str) -> Dict[str, Any]:
        """Extract insert-specific specifications"""
        specs = {}
        content_lower = content.lower()
        
        # Extract outer diameter
        outer_diameters = re.findall(r'(?:outer|od).*?(\d+(?:\.\d+)?)', content_lower)
        if outer_diameters:
            specs['outer_diameter'] = float(outer_diameters[0])
        
        # Extract inner diameter
        inner_diameters = re.findall(r'(?:inner|id).*?(\d+(?:\.\d+)?)', content_lower)
        if inner_diameters:
            specs['inner_diameter'] = float(inner_diameters[0])
        
        # Extract thread
        thread_matches = re.findall(r'(8-32|5/16-24|M\d+x\d+)', content, re.IGNORECASE)
        if thread_matches:
            specs['thread'] = thread_matches[0]
        
        # Extract length
        lengths = self.extract_measurement(content, 'lengths')
        if lengths:
            specs['length'] = float(lengths[0])
        
        # Extract weight
        weights = self.extract_measurement(content, 'weights')
        if weights:
            specs['weight'] = f"{weights[0]}gr"
        
        # Extract material
        if 'aluminum' in content_lower:
            specs['material'] = 'aluminum'
        elif 'stainless' in content_lower:
            specs['material'] = 'stainless'
        elif 'brass' in content_lower:
            specs['material'] = 'brass'
        
        # Determine type
        if 'outsert' in content_lower:
            specs['type'] = 'outsert'
        elif 'combo' in content_lower:
            specs['type'] = 'combo'
        else:
            specs['type'] = 'insert'
        
        return specs

class ComponentExtractorFactory:
    """Factory for creating component extractors"""
    
    extractors = {
        'points': PointExtractor,
        'nocks': NockExtractor,
        'fletchings': FletchingExtractor,
        'inserts': InsertExtractor
    }
    
    @classmethod
    def get_extractor(cls, component_type: str) -> Optional[BaseComponentExtractor]:
        """Get extractor for component type"""
        extractor_class = cls.extractors.get(component_type)
        if extractor_class:
            return extractor_class()
        return None
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available component types"""
        return list(cls.extractors.keys())

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Component Extractors")
    print("=" * 50)
    
    # Test content examples
    test_content = {
        'points': """
        Easton G Nock Field Point 100 Grain
        Weight: 100 grains
        Thread: 8-32
        Diameter: 0.945"
        Length: 2.5"
        Material: Stainless Steel
        Field point for target practice
        """,
        
        'nocks': """
        Easton G Nock
        Nock Size: .244"
        Push-in fit
        Material: Plastic
        Weight: 7 grains
        Colors: Red, Yellow, Green
        Throat size: 0.088"
        """,
        
        'fletchings': """
        Bohning Blazer Vanes
        Length: 2"
        Height: 0.57"
        Material: Plastic
        Low profile design
        Adhesive attachment
        Colors: White, Orange, Yellow
        Weight: 5 grains each
        """,
        
        'inserts': """
        Easton Super UNI Insert
        Outer Diameter: 0.244"
        Inner Diameter: 0.166"
        Thread: 8-32
        Length: 0.5"
        Weight: 12 grains
        Material: Aluminum
        Standard insert
        """
    }
    
    # Test each extractor
    for component_type, content in test_content.items():
        print(f"\n🔍 Testing {component_type} extractor:")
        
        extractor = ComponentExtractorFactory.get_extractor(component_type)
        if extractor:
            specs = extractor.extract_specifications(content, f"http://example.com/{component_type}")
            print(f"   Extracted specifications:")
            for key, value in specs.items():
                print(f"     {key}: {value}")
        else:
            print(f"   ❌ No extractor found for {component_type}")
    
    print(f"\n✅ Component extractor test completed!")
    print(f"Available extractors: {ComponentExtractorFactory.get_available_types()}")