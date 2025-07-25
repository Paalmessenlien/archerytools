#!/usr/bin/env python3
"""
Manufacturer Website Research Tool
Analyzes manufacturer websites to understand structure and data patterns
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from config.settings import MANUFACTURERS, DATA_DIR

class ManufacturerResearcher:
    """Tool for researching manufacturer website structures"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.research_data = {}
    
    def analyze_page(self, url: str) -> dict:
        """Analyze a single webpage for arrow information patterns"""
        try:
            print(f"Analyzing: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'status': 'success',
                'page_structure': self._analyze_structure(soup),
                'potential_arrow_data': self._find_arrow_indicators(soup),
                'navigation_patterns': self._analyze_navigation(soup),
                'product_patterns': self._analyze_products(soup)
            }
            
            return analysis
            
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e)
            }
    
    def _analyze_structure(self, soup) -> dict:
        """Analyze page structure"""
        return {
            'has_nav': bool(soup.find('nav')),
            'main_content_tags': [tag.name for tag in soup.find_all(['main', 'article', 'section'])],
            'table_count': len(soup.find_all('table')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'form_count': len(soup.find_all('form'))
        }
    
    def _find_arrow_indicators(self, soup) -> dict:
        """Look for arrow-related content indicators"""
        text = soup.get_text().lower()
        
        # Key terms that indicate arrow specifications
        arrow_terms = {
            'spine': text.count('spine'),
            'diameter': text.count('diameter'),
            'gpi': text.count('gpi'),
            'grains per inch': text.count('grains per inch'),
            'straightness': text.count('straightness'),
            'carbon': text.count('carbon'),
            'hunting': text.count('hunting'),
            'target': text.count('target'),
            'arrow': text.count('arrow'),
            'shaft': text.count('shaft')
        }
        
        # Look for numeric patterns that might be spine values
        import re
        spine_pattern = r'\b[2-9]\d{2,3}\b'  # 200-9999 range
        potential_spines = re.findall(spine_pattern, text)
        
        # Look for diameter patterns
        diameter_pattern = r'\b0\.\d{3}\b'  # e.g., 0.246
        potential_diameters = re.findall(diameter_pattern, text)
        
        return {
            'term_counts': arrow_terms,
            'potential_spines': list(set(potential_spines))[:10],  # Limit to 10
            'potential_diameters': list(set(potential_diameters))[:10],
            'arrow_relevance_score': sum(arrow_terms.values())
        }
    
    def _analyze_navigation(self, soup) -> dict:
        """Analyze navigation patterns"""
        nav_links = []
        
        # Find navigation elements
        for nav in soup.find_all(['nav', 'ul', 'div'], class_=lambda x: x and any(term in x.lower() for term in ['nav', 'menu', 'category'])):
            links = nav.find_all('a', href=True)
            for link in links[:5]:  # Limit to 5 per nav section
                nav_links.append({
                    'text': link.get_text().strip(),
                    'href': link['href']
                })
        
        return {
            'navigation_links': nav_links[:20],  # Limit total
            'category_indicators': [link for link in nav_links if any(term in link['text'].lower() for term in ['arrow', 'hunting', 'target', 'carbon'])]
        }
    
    def _analyze_products(self, soup) -> dict:
        """Look for product listing patterns"""
        products = []
        
        # Common product container selectors
        product_selectors = [
            '.product',
            '.item',
            '[class*="product"]',
            '[class*="arrow"]',
            'article',
            '.card'
        ]
        
        for selector in product_selectors:
            elements = soup.select(selector)
            for elem in elements[:5]:  # Limit to 5 per selector
                text = elem.get_text().strip()
                if any(term in text.lower() for term in ['arrow', 'shaft', 'spine']):
                    products.append({
                        'selector': selector,
                        'text_preview': text[:100],
                        'has_links': bool(elem.find('a'))
                    })
        
        return {
            'potential_products': products[:10],
            'product_pattern_count': len(products)
        }
    
    def research_manufacturer(self, manufacturer_key: str) -> dict:
        """Research a specific manufacturer"""
        if manufacturer_key not in MANUFACTURERS:
            return {'error': f'Unknown manufacturer: {manufacturer_key}'}
        
        manufacturer = MANUFACTURERS[manufacturer_key]
        research_result = {
            'manufacturer': manufacturer['name'],
            'base_url': manufacturer['base_url'],
            'pages_analyzed': []
        }
        
        # Analyze base URL
        base_analysis = self.analyze_page(manufacturer['base_url'])
        research_result['pages_analyzed'].append(base_analysis)
        
        # Analyze category pages if available
        if 'categories' in manufacturer:
            for category, url in manufacturer['categories'].items():
                analysis = self.analyze_page(url)
                analysis['category'] = category
                research_result['pages_analyzed'].append(analysis)
        
        # Analyze specific arrow pages if available
        if 'arrows' in manufacturer:
            for url in manufacturer['arrows'][:3]:  # Limit to 3
                analysis = self.analyze_page(url)
                analysis['page_type'] = 'specific_arrow'
                research_result['pages_analyzed'].append(analysis)
        
        return research_result
    
    def generate_research_report(self) -> str:
        """Generate a summary research report"""
        report = []
        report.append("MANUFACTURER WEBSITE RESEARCH REPORT")
        report.append("=" * 50)
        
        for manufacturer_key, data in self.research_data.items():
            if 'error' in data:
                report.append(f"\n{manufacturer_key.upper()}: ERROR - {data['error']}")
                continue
                
            report.append(f"\n{data['manufacturer'].upper()}")
            report.append("-" * len(data['manufacturer']))
            report.append(f"Base URL: {data['base_url']}")
            
            successful_pages = [p for p in data['pages_analyzed'] if p.get('status') == 'success']
            report.append(f"Pages analyzed: {len(successful_pages)}/{len(data['pages_analyzed'])}")
            
            if successful_pages:
                # Aggregate arrow relevance scores
                total_relevance = sum(p.get('potential_arrow_data', {}).get('arrow_relevance_score', 0) for p in successful_pages)
                report.append(f"Arrow relevance score: {total_relevance}")
                
                # Find best pages
                best_page = max(successful_pages, key=lambda p: p.get('potential_arrow_data', {}).get('arrow_relevance_score', 0))
                report.append(f"Most relevant page: {best_page['url']}")
                
                # Show common spine values found
                all_spines = []
                for page in successful_pages:
                    all_spines.extend(page.get('potential_arrow_data', {}).get('potential_spines', []))
                common_spines = list(set(all_spines))[:10]
                if common_spines:
                    report.append(f"Potential spine values: {', '.join(common_spines)}")
        
        return '\n'.join(report)
    
    def save_research_data(self):
        """Save detailed research data to JSON"""
        output_file = DATA_DIR / 'manufacturer_research.json'
        with open(output_file, 'w') as f:
            json.dump(self.research_data, f, indent=2)
        print(f"Research data saved to: {output_file}")

def main():
    """Main research function"""
    print("Starting manufacturer website research...")
    
    researcher = ManufacturerResearcher()
    
    # Research each manufacturer
    for manufacturer_key in MANUFACTURERS:
        print(f"\nResearching {manufacturer_key}...")
        try:
            research_result = researcher.research_manufacturer(manufacturer_key)
            researcher.research_data[manufacturer_key] = research_result
        except Exception as e:
            print(f"Error researching {manufacturer_key}: {e}")
            researcher.research_data[manufacturer_key] = {'error': str(e)}
    
    # Generate and display report
    report = researcher.generate_research_report()
    print("\n" + report)
    
    # Save detailed data
    researcher.save_research_data()
    
    print(f"\nResearch completed for {len(MANUFACTURERS)} manufacturers")

if __name__ == "__main__":
    main()