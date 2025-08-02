#!/usr/bin/env python3
"""
Manual extractor for TopHat Archery using regex patterns
Fallback when LLM extraction doesn't work
"""

import re
import json
from typing import Dict, Optional
from bs4 import BeautifulSoup

class TopHatManualExtractor:
    """Manual extraction using regex and BeautifulSoup"""
    
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
                    # Model is everything except the last part (which might be spine)
                    model_parts = title_parts[1:]
                    if model_parts and model_parts[-1].isdigit():
                        model_parts = model_parts[:-1]  # Remove spine if it's the last part
                    data['model_name'] = ' '.join(model_parts) if model_parts else title_parts[1]
            
            # Extract price
            price_elem = soup.find('span', class_='price--content')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'([\d,]+)', price_text)
                if price_match:
                    data['price'] = price_match.group(1)
            
            return data if data else None
            
        except Exception as e:
            print(f"Error extracting data: {e}")
            return None
    
    def _extract_specifications(self, table) -> Dict:
        """Extract specifications from properties table"""
        specs = {}
        
        # Mapping of German terms to our field names
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
            'Name': 'model_name_alt'
        }
        
        # Find all rows
        rows = table.find_all('tr', class_='product--properties-row')
        
        for row in rows:
            label_elem = row.find('td', class_='product--properties-label')
            value_elem = row.find('td', class_='product--properties-value')
            
            if label_elem and value_elem:
                label = label_elem.get_text(strip=True).rstrip(':')
                value = value_elem.get_text(strip=True)
                
                if label in field_mapping:
                    field_name = field_mapping[label]
                    
                    # Process specific fields
                    if field_name == 'spine':
                        specs['spine'] = value
                    elif field_name == 'inner_diameter_raw':
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
        """Extract diameter in inches from string like '.246\", 6,25mm'"""
        # Look for inch measurement first (more accurate)
        inch_match = re.search(r'(\d*\.\d+)"', value)
        if inch_match:
            return float(inch_match.group(1))
        
        # Fallback to mm measurement
        mm_match = re.search(r'(\d+,\d+)mm', value)
        if mm_match:
            mm_value = float(mm_match.group(1).replace(',', '.'))
            return round(mm_value / 25.4, 3)  # Convert mm to inches
        
        return None
    
    def _extract_number(self, value: str) -> Optional[float]:
        """Extract number from string, handling German decimal format"""
        # Replace German decimal comma with dot
        value = value.replace(',', '.')
        
        # Extract number
        num_match = re.search(r'(\d+\.?\d*)', value)
        if num_match:
            return float(num_match.group(1))
        
        return None

# Test the manual extractor
async def test_manual_extraction():
    """Test manual extraction"""
    import asyncio
    import sys
    import os
    
    # Add crawl4ai to path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'crawl4ai'))
    
    from crawl4ai import AsyncWebCrawler
    
    test_url = "https://tophatarchery.com/search-by-shaft/brands/aurel/7933/aurel-agil-300"
    
    print(f"🧪 Testing manual extraction on: {test_url}")
    
    extractor = TopHatManualExtractor()
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=test_url)
        
        if result.success:
            print(f"✅ Content fetched successfully")
            
            extracted_data = extractor.extract_product_data(result.html, test_url)
            
            if extracted_data:
                print(f"✅ Manual extraction successful!")
                print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Manual extraction failed")
        else:
            print(f"❌ Failed to fetch content: {result.error_message}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_manual_extraction())