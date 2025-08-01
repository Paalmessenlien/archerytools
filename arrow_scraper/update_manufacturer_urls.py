#!/usr/bin/env python3
"""
URL Update Script for Manufacturer Configuration

This script automatically discovers and updates product URLs for manufacturers
by scraping their category pages. Helps keep URLs current when manufacturers
change their site structure.

Usage:
    python update_manufacturer_urls.py --manufacturer "Nijora Archery" --category-url "https://nijora.com/product-category/carbonpfeile/carbonschaefte/"
    python update_manufacturer_urls.py --all  # Update all manufacturers with category URLs
    python update_manufacturer_urls.py --dry-run --manufacturer "Nijora Archery" --category-url "..."  # Preview changes
"""

import asyncio
import argparse
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

# Import our existing crawling infrastructure
try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("Warning: Crawl4AI not available, falling back to basic requests")

import requests
from bs4 import BeautifulSoup

class ManufacturerURLUpdater:
    """Updates manufacturer URLs by scraping category pages"""
    
    def __init__(self, config_path: str = "config/manufacturers.yaml"):
        self.config_path = Path(config_path)
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the URL updater"""
        logger = logging.getLogger("url_updater")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def load_config(self) -> Dict:
        """Load the manufacturer configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def save_config(self, config: Dict, backup: bool = True) -> bool:
        """Save the updated configuration with backup"""
        try:
            if backup:
                backup_path = self.config_path.with_suffix('.yaml.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
                self.logger.info(f"Backup saved to {backup_path}")
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
            self.logger.info(f"Configuration updated: {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    async def scrape_category_page_crawl4ai(self, url: str) -> List[str]:
        """Scrape category page using Crawl4AI (preferred method)"""
        if not CRAWL4AI_AVAILABLE:
            return await self.scrape_category_page_requests(url)
        
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    extraction_strategy=LLMExtractionStrategy(
                        provider="openai",  # Can be configured
                        api_token="dummy",  # We'll use content extraction, not LLM
                        schema={
                            "type": "object",
                            "properties": {
                                "product_links": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "All product page URLs found on this category page"
                                }
                            },
                            "required": ["product_links"]
                        },
                        extraction_type="schema",
                        instruction="Extract all product page URLs from this category page"
                    )
                )
                
                if result.success:
                    # Parse links from HTML content instead of using LLM
                    return self._extract_links_from_html(result.html, url)
                else:
                    self.logger.warning(f"Crawl4AI failed for {url}, falling back to requests")
                    return await self.scrape_category_page_requests(url)
                    
        except Exception as e:
            self.logger.warning(f"Crawl4AI error for {url}: {e}, falling back to requests")
            return await self.scrape_category_page_requests(url)
    
    async def scrape_category_page_requests(self, url: str) -> List[str]:
        """Scrape category page using requests and BeautifulSoup (fallback)"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return self._extract_links_from_html(response.text, url)
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return []
    
    def _extract_links_from_html(self, html_content: str, base_url: str) -> List[str]:
        """Extract product links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        base_domain = urlparse(base_url).netloc
        product_links = set()
        
        # Common selectors for product links
        selectors = [
            'a[href*="/product/"]',           # Generic product links
            'a[href*="/produkt/"]',           # German product links
            'a[href*="/item/"]',              # Alternative product links
            '.product-item a',                # Product item containers
            '.woocommerce-loop-product__link', # WooCommerce product links
            '.product-link',                  # Generic product link class
            'h2.woocommerce-loop-product__title a',  # WooCommerce product titles
            '.products .product a'            # Product grid links
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    
                    # Filter for actual product pages
                    if self._is_product_url(full_url, base_domain):
                        product_links.add(full_url)
        
        # If no specific product links found, try broader search
        if not product_links:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if self._is_product_url(full_url, base_domain):
                        product_links.add(full_url)
        
        result = sorted(list(product_links))
        self.logger.info(f"Found {len(result)} product URLs on {base_url}")
        return result
    
    def _is_product_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is likely a product page"""
        parsed = urlparse(url)
        
        # Must be on the same domain
        if parsed.netloc != base_domain:
            return False
        
        path = parsed.path.lower()
        
        # Common product URL patterns
        product_patterns = [
            r'/product/',
            r'/produkt/',
            r'/item/',
            r'/arrows?/',
            r'/pfeil',
            r'/schaft',
            r'/carbon',
        ]
        
        # Exclude patterns
        exclude_patterns = [
            r'/category/',
            r'/cart',
            r'/checkout',
            r'/account',
            r'/login',
            r'/contact',
            r'/about',
            r'/blog',
            r'/news',
            r'\.pdf$',
            r'\.jpg$',
            r'\.png$',
            r'/wp-',
            r'/admin'
        ]
        
        # Check if it matches product patterns
        for pattern in product_patterns:
            if re.search(pattern, path):
                # Make sure it doesn't match exclude patterns
                for exclude in exclude_patterns:
                    if re.search(exclude, path):
                        return False
                return True
        
        return False
    
    def compare_urls(self, old_urls: List[str], new_urls: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """Compare old and new URL lists"""
        old_set = set(old_urls)
        new_set = set(new_urls)
        
        added = sorted(list(new_set - old_set))
        removed = sorted(list(old_set - new_set))
        unchanged = sorted(list(old_set & new_set))
        
        return added, removed, unchanged
    
    async def update_manufacturer_urls(self, manufacturer: str, category_url: str, dry_run: bool = False) -> bool:
        """Update URLs for a specific manufacturer"""
        self.logger.info(f"🔍 Updating URLs for {manufacturer}")
        self.logger.info(f"📄 Scraping category page: {category_url}")
        
        # Load current configuration
        config = self.load_config()
        if not config or 'manufacturers' not in config:
            self.logger.error("Invalid configuration file")
            return False
        
        # Check if manufacturer exists
        if manufacturer not in config['manufacturers']:
            self.logger.error(f"Manufacturer '{manufacturer}' not found in configuration")
            return False
        
        # Scrape new URLs
        new_urls = await self.scrape_category_page_crawl4ai(category_url)
        if not new_urls:
            self.logger.warning("No product URLs found")
            return False
        
        # Get current URLs
        old_urls = config['manufacturers'][manufacturer].get('product_urls', [])
        
        # Compare URLs
        added, removed, unchanged = self.compare_urls(old_urls, new_urls)
        
        # Report changes
        self.logger.info(f"📊 URL Analysis for {manufacturer}:")
        self.logger.info(f"   ✅ Found: {len(new_urls)} total URLs")
        self.logger.info(f"   🆕 New: {len(added)} URLs")
        self.logger.info(f"   ❌ Removed: {len(removed)} URLs")
        self.logger.info(f"   🔄 Unchanged: {len(unchanged)} URLs")
        
        if added:
            self.logger.info("🆕 New URLs:")
            for url in added[:10]:  # Show first 10
                self.logger.info(f"   + {url}")
            if len(added) > 10:
                self.logger.info(f"   ... and {len(added) - 10} more")
        
        if removed:
            self.logger.info("❌ Removed URLs:")
            for url in removed[:10]:  # Show first 10
                self.logger.info(f"   - {url}")
            if len(removed) > 10:
                self.logger.info(f"   ... and {len(removed) - 10} more")
        
        # Update configuration
        if not dry_run:
            config['manufacturers'][manufacturer]['product_urls'] = new_urls
            config['manufacturers'][manufacturer]['last_updated'] = datetime.now().isoformat()
            
            if self.save_config(config):
                self.logger.info(f"✅ Successfully updated {manufacturer} URLs")
                return True
            else:
                self.logger.error(f"❌ Failed to save configuration")
                return False
        else:
            self.logger.info("🔍 Dry run - no changes saved")
            return True
    
    async def update_all_manufacturers(self, dry_run: bool = False) -> bool:
        """Update URLs for all manufacturers that have category URLs defined"""
        config = self.load_config()
        if not config:
            return False
        
        # Define category URLs for manufacturers (can be expanded)
        category_urls = {
            "Nijora Archery": "https://nijora.com/product-category/carbonpfeile/carbonschaefte/",
            # Add more manufacturers and their category pages here
            # "Gold Tip": "https://www.goldtip.com/hunting-arrows/",
            # "Victory Archery": "https://www.victoryarchery.com/arrows-hunting/",
        }
        
        success_count = 0
        total_count = len(category_urls)
        
        for manufacturer, category_url in category_urls.items():
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing {manufacturer} ({success_count + 1}/{total_count})")
            self.logger.info(f"{'='*60}")
            
            try:
                if await self.update_manufacturer_urls(manufacturer, category_url, dry_run):
                    success_count += 1
                    
                # Small delay between manufacturers to be respectful
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error updating {manufacturer}: {e}")
        
        self.logger.info(f"\n🎯 Summary: {success_count}/{total_count} manufacturers updated successfully")
        return success_count == total_count

async def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description="Update manufacturer URLs from category pages")
    parser.add_argument("--manufacturer", help="Specific manufacturer to update")
    parser.add_argument("--category-url", help="Category page URL to scrape")
    parser.add_argument("--all", action="store_true", help="Update all configured manufacturers")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without saving")
    parser.add_argument("--config", default="config/manufacturers.yaml", help="Config file path")
    
    args = parser.parse_args()
    
    updater = ManufacturerURLUpdater(args.config)
    
    if args.all:
        await updater.update_all_manufacturers(args.dry_run)
    elif args.manufacturer and args.category_url:
        await updater.update_manufacturer_urls(args.manufacturer, args.category_url, args.dry_run)
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python update_manufacturer_urls.py --manufacturer "Nijora Archery" --category-url "https://nijora.com/product-category/carbonpfeile/carbonschaefte/"')
        print("  python update_manufacturer_urls.py --all --dry-run")

if __name__ == "__main__":
    asyncio.run(main())