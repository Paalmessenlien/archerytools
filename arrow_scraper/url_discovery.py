#!/usr/bin/env python3
"""
URL Discovery System for Arrow Scraper
Automatically discovers and categorizes URLs from manufacturer pages
"""

import requests
import re
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Set, Tuple
import time
from pathlib import Path
import validators
from url_manager import URLManager

class URLDiscovery:
    """Discovers and categorizes URLs from manufacturer pages"""
    
    def __init__(self):
        self.url_manager = URLManager()
        self.discovered_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ArrowScraperBot/1.0; +info@arrowscraper.com)'
        })
        
        # URL patterns for different content types
        self.url_patterns = {
            'arrow': [
                r'/arrow[s]?/',
                r'/shaft[s]?/', 
                r'/carbon[-_]arrow[s]?/',
                r'/aluminum[-_]arrow[s]?/',
                r'[-_]arrow[-_]',
                r'[-_]shaft[-_]',
                r'/spine[-_]\d+/',
                r'carbon.*shaft',
                r'aluminum.*shaft'
            ],
            'points': [
                r'/point[s]?/',
                r'/tip[s]?/',
                r'/broadhead[s]?/',
                r'/field[-_]point[s]?/',
                r'[-_]point[-_]',
                r'[-_]tip[-_]',
                r'[-_]head[-_]',
                r'/\d+[-_]gr[ain]*/',
                r'grain.*point'
            ],
            'nocks': [
                r'/nock[s]?/',
                r'/knock[s]?/',
                r'[-_]nock[-_]',
                r'string[-_]nock',
                r'push[-_]in[-_]nock',
                r'snap[-_]on[-_]nock'
            ],
            'fletchings': [
                r'/fletching[s]?/',
                r'/vane[s]?/',
                r'/feather[s]?/',
                r'[-_]vane[-_]',
                r'[-_]fletching[-_]',
                r'plastic[-_]vane',
                r'turkey[-_]feather'
            ],
            'inserts': [
                r'/insert[s]?/',
                r'/outsert[s]?/',
                r'[-_]insert[-_]',
                r'arrow[-_]insert',
                r'threaded[-_]insert'
            ],
            'accessories': [
                r'/accessori[es]*/',
                r'/rest[s]?/',
                r'/sight[s]?/',
                r'/stabilizer[s]?/',
                r'/quiver[s]?/',
                r'[-_]rest[-_]',
                r'[-_]sight[-_]'
            ]
        }
        
        # Content indicators for different categories
        self.content_indicators = {
            'arrow': [
                'spine', 'gpi', 'diameter', 'carbon fiber', 'aluminum alloy',
                'straightness', 'weight tolerance', 'shaft length'
            ],
            'points': [
                'grain', 'grains', 'thread', 'cutting diameter', 'blade',
                'field point', 'broadhead', 'tip weight'
            ],
            'nocks': [
                'nock size', 'string groove', 'nock fit', 'throat size',
                'push in', 'snap on', 'nock weight'
            ],
            'fletchings': [
                'vane length', 'feather length', 'helical', 'straight',
                'profile height', 'fletching adhesive'
            ],
            'inserts': [
                'thread size', 'insert weight', 'outer diameter', 'inner diameter',
                '8-32', '5/16-24', 'threaded insert'
            ]
        }
    
    def discover_urls(self, base_url: str, content_type: str = 'auto', 
                     max_depth: int = 2, max_urls: int = 50) -> Dict[str, List[str]]:
        """Discover URLs from a base page"""
        print(f"🔍 Starting URL discovery from: {base_url}")
        print(f"   Content type: {content_type}")
        print(f"   Max depth: {max_depth}, Max URLs: {max_urls}")
        
        discovered = {
            'arrow': [],
            'points': [],
            'nocks': [],
            'fletchings': [],
            'inserts': [],
            'accessories': [],
            'unknown': []
        }
        
        try:
            # Get base page
            response = self.session.get(base_url, timeout=15)
            if response.status_code != 200:
                print(f"❌ Failed to fetch base page: {response.status_code}")
                return discovered
            
            soup = BeautifulSoup(response.content, 'html.parser')
            base_domain = urlparse(base_url).netloc
            
            # Extract all links
            links = soup.find_all('a', href=True)
            print(f"📊 Found {len(links)} links on base page")
            
            processed_urls = set()
            
            for link in links:
                href = link.get('href')
                if not href:
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                # Skip if already processed or external domain
                if full_url in processed_urls or urlparse(full_url).netloc != base_domain:
                    continue
                
                processed_urls.add(full_url)
                
                # Categorize URL
                category = self._categorize_url(full_url, link, content_type)
                if category and category in discovered:
                    discovered[category].append(full_url)
                    print(f"   🎯 Found {category}: {full_url}")
                
                # Stop if we've found enough URLs
                total_found = sum(len(urls) for urls in discovered.values())
                if total_found >= max_urls:
                    break
            
            # If we need more URLs and depth allows, crawl one level deeper
            if max_depth > 1 and total_found < max_urls:
                print(f"🔄 Crawling one level deeper...")
                discovered = self._crawl_deeper(discovered, base_url, content_type, max_urls - total_found)
            
            # Summary
            total_discovered = sum(len(urls) for urls in discovered.values())
            print(f"✅ Discovery complete: {total_discovered} URLs found")
            for category, urls in discovered.items():
                if urls:
                    print(f"   {category}: {len(urls)} URLs")
            
            return discovered
            
        except Exception as e:
            print(f"❌ URL discovery error: {e}")
            return discovered
    
    def _categorize_url(self, url: str, link_element: Any, preferred_type: str = 'auto') -> str:
        """Categorize a URL based on patterns and context"""
        url_lower = url.lower()
        
        # If preferred type is specified and matches, return it
        if preferred_type != 'auto' and preferred_type in self.url_patterns:
            patterns = self.url_patterns[preferred_type]
            if any(re.search(pattern, url_lower) for pattern in patterns):
                return preferred_type
        
        # Check URL patterns for all categories
        for category, patterns in self.url_patterns.items():
            if any(re.search(pattern, url_lower) for pattern in patterns):
                return category
        
        # Check link text and context
        link_text = link_element.get_text(strip=True).lower()
        link_context = self._get_link_context(link_element)
        combined_text = f"{link_text} {link_context}".lower()
        
        # Check content indicators
        for category, indicators in self.content_indicators.items():
            score = sum(1 for indicator in indicators if indicator.lower() in combined_text)
            if score >= 2:  # Require at least 2 indicators
                return category
        
        # Special handling for product pages
        if self._looks_like_product_page(url, combined_text):
            if preferred_type != 'auto':
                return preferred_type
            return 'unknown'  # Will need manual categorization
        
        return None  # Skip this URL
    
    def _get_link_context(self, link_element: Any) -> str:
        """Get context around a link for better categorization"""
        context = ""
        
        # Get parent element text
        parent = link_element.parent
        if parent:
            context += parent.get_text(strip=True)
        
        # Get nearby text (siblings)
        for sibling in link_element.find_next_siblings(limit=2):
            context += " " + sibling.get_text(strip=True)
        
        for sibling in link_element.find_previous_siblings(limit=2):
            context += " " + sibling.get_text(strip=True)
        
        return context[:200]  # Limit context length
    
    def _looks_like_product_page(self, url: str, context: str) -> bool:
        """Check if URL looks like a product page"""
        product_indicators = [
            'product', 'item', 'detail', 'spec', 'buy', 'shop',
            'model', 'part', 'sku', '.html', '/p/', '/product/'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in product_indicators)
    
    def _crawl_deeper(self, current_discovered: Dict[str, List[str]], 
                     base_url: str, content_type: str, remaining_slots: int) -> Dict[str, List[str]]:
        """Crawl one level deeper from category pages"""
        
        category_pages = []
        
        # Look for category/listing pages first
        for category, urls in current_discovered.items():
            if not urls:
                continue
            
            # Find URLs that look like category pages
            for url in urls[:3]:  # Check first 3 URLs per category
                if self._looks_like_category_page(url):
                    category_pages.append((url, category))
        
        discovered_count = 0
        
        for category_url, category in category_pages:
            if discovered_count >= remaining_slots:
                break
            
            try:
                print(f"   🔄 Crawling {category} category: {category_url}")
                response = self.session.get(category_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links[:20]:  # Limit to first 20 links
                        href = link.get('href')
                        if not href:
                            continue
                        
                        full_url = urljoin(base_url, href)
                        
                        # Skip if already found
                        if any(full_url in urls for urls in current_discovered.values()):
                            continue
                        
                        if self._looks_like_product_page(full_url, link.get_text()):
                            current_discovered[category].append(full_url)
                            discovered_count += 1
                            print(f"      🎯 Found {category}: {full_url}")
                            
                            if discovered_count >= remaining_slots:
                                break
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"   ⚠️  Error crawling {category_url}: {e}")
                continue
        
        return current_discovered
    
    def _looks_like_category_page(self, url: str) -> bool:
        """Check if URL looks like a category/listing page"""
        category_indicators = [
            'category', 'products', 'catalog', 'list', 'browse',
            'collection', 'series', 'line', 'family'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in category_indicators)
    
    def validate_discovered_urls(self, discovered: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Validate discovered URLs and remove invalid ones"""
        print(f"🔍 Validating discovered URLs...")
        
        validated = {}
        total_checked = 0
        total_valid = 0
        
        for category, urls in discovered.items():
            if not urls:
                validated[category] = []
                continue
            
            validated[category] = []
            
            for url in urls:
                total_checked += 1
                
                try:
                    # Quick validation - just check if URL responds
                    response = self.session.head(url, timeout=5)
                    if response.status_code in [200, 301, 302]:
                        validated[category].append(url)
                        total_valid += 1
                    else:
                        print(f"   ❌ Invalid {category} URL: {url} ({response.status_code})")
                
                except Exception as e:
                    print(f"   ❌ Failed to validate {category} URL: {url}")
                
                # Rate limiting
                time.sleep(0.5)
        
        print(f"✅ Validation complete: {total_valid}/{total_checked} URLs are valid")
        return validated
    
    def add_discovered_urls_to_config(self, manufacturer: str, discovered: Dict[str, List[str]], 
                                    auto_add: bool = False) -> bool:
        """Add discovered URLs to manufacturer configuration"""
        
        total_added = 0
        
        for category, urls in discovered.items():
            if not urls:
                continue
            
            print(f"\n📋 Found {len(urls)} {category} URLs for {manufacturer}:")
            
            for i, url in enumerate(urls, 1):
                print(f"   {i}. {url}")
                
                if auto_add:
                    success = self.url_manager.add_url(manufacturer, category, url, force=True)
                    if success:
                        total_added += 1
                else:
                    # Interactive mode
                    while True:
                        response = input(f"   Add this {category} URL? (y/n/q): ").lower()
                        if response == 'y':
                            success = self.url_manager.add_url(manufacturer, category, url, force=True)
                            if success:
                                total_added += 1
                            break
                        elif response == 'n':
                            break
                        elif response == 'q':
                            print(f"✅ Added {total_added} URLs to configuration")
                            return True
                        else:
                            print("   Please enter 'y' (yes), 'n' (no), or 'q' (quit)")
        
        print(f"✅ Added {total_added} URLs to {manufacturer} configuration")
        return True

# Example usage and testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="URL Discovery for Arrow Scraper")
    parser.add_argument('--discover', action='store_true', help='Discover URLs from page')
    parser.add_argument('--url', required=True, help='Base URL to discover from')
    parser.add_argument('--type', default='auto', help='Content type to look for')
    parser.add_argument('--manufacturer', help='Manufacturer to add URLs to')
    parser.add_argument('--auto-add', action='store_true', help='Automatically add all discovered URLs')
    parser.add_argument('--max-urls', type=int, default=50, help='Maximum URLs to discover')
    parser.add_argument('--validate', action='store_true', help='Validate discovered URLs')
    
    args = parser.parse_args()
    
    if args.discover:
        discovery = URLDiscovery()
        
        print(f"🚀 Starting URL discovery...")
        discovered = discovery.discover_urls(args.url, args.type, max_urls=args.max_urls)
        
        if args.validate:
            discovered = discovery.validate_discovered_urls(discovered)
        
        if args.manufacturer:
            discovery.add_discovered_urls_to_config(
                args.manufacturer, 
                discovered, 
                args.auto_add
            )
        else:
            print(f"\n📊 Discovery Results:")
            total = sum(len(urls) for urls in discovered.values())
            print(f"Total URLs discovered: {total}")
            
            for category, urls in discovered.items():
                if urls:
                    print(f"\n{category.upper()} ({len(urls)} URLs):")
                    for url in urls[:5]:  # Show first 5
                        print(f"  • {url}")
                    if len(urls) > 5:
                        print(f"  ... and {len(urls) - 5} more")
    
    else:
        print("❌ Please specify --discover")
        print("Example: python url_discovery.py --discover --url=https://example.com --type=arrows")