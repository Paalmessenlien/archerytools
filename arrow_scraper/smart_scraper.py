#!/usr/bin/env python3
"""
Smart Arrow Scraper
Two-phase scraping: 1) Extract product links 2) Scrape specifications
"""

import asyncio
import re
import json
import time
from typing import List, Set
from urllib.parse import urljoin, urlparse
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from deepseek_extractor import DeepSeekArrowExtractor
from models import ArrowSpecification, ScrapingResult
from config.settings import MANUFACTURERS

class SmartArrowScraper:
    """Two-phase scraper: extract product links, then scrape specifications"""
    
    def __init__(self, deepseek_api_key: str):
        self.extractor = DeepSeekArrowExtractor(deepseek_api_key)
        self.session_id = f"smart_{int(time.time())}"
    
    async def extract_product_links(self, url: str, base_url: str) -> Set[str]:
        """Extract arrow product page links from a category page"""
        
        print(f"Extracting product links from: {url}")
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, bypass_cache=True)
            
            if not result.success:
                print(f"Failed to fetch category page: {result.error_message}")
                return set()
            
            content = result.html or result.markdown or ""
            
            # Extract all links from the page
            link_patterns = [
                r'href="([^"]*)"',
                r'href=\'([^\']*)\''
            ]
            
            all_links = set()
            for pattern in link_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                all_links.update(matches)
            
            # Filter for arrow-related links
            arrow_keywords = [
                'arrow', 'shaft', 'fmj', 'axis', 'carbon', 'target', 'hunting',
                'indoor', 'outdoor', 'spine', 'product', 'series'
            ]
            
            # Base URL for relative links
            parsed_base = urlparse(base_url)
            base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
            
            product_links = set()
            
            for link in all_links:
                if not link:
                    continue
                
                # Convert relative links to absolute
                if link.startswith('/'):
                    full_link = base_domain + link
                elif link.startswith('http'):
                    full_link = link
                else:
                    full_link = urljoin(url, link)
                
                # Filter for arrow-related links
                link_lower = link.lower()
                if any(keyword in link_lower for keyword in arrow_keywords):
                    # Avoid navigation/category pages, focus on product pages
                    if not any(avoid in link_lower for avoid in ['category', 'tag', 'search', 'cart', 'checkout']):
                        product_links.add(full_link)
            
            # Remove the original URL to avoid circular references
            product_links.discard(url)
            
            print(f"Found {len(product_links)} potential product links")
            return product_links
    
    async def scrape_product_page(self, url: str, manufacturer: str) -> ScrapingResult:
        """Scrape a specific product page for arrow specifications"""
        
        start_time = time.time()
        
        try:
            await asyncio.sleep(1)  # Rate limiting
            
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url, bypass_cache=True, timeout=15)
                
                if result.success:
                    content = result.markdown or result.html or ""
                    
                    if content:
                        # Use DeepSeek to extract arrow specifications
                        arrows = self.extractor.extract_arrows_from_content(
                            content=content,
                            source_url=url,
                            manufacturer=manufacturer
                        )
                        
                        scraping_result = ScrapingResult(
                            success=True,
                            url=url,
                            arrows_found=len(arrows),
                            processed_data=arrows,
                            processing_time=time.time() - start_time
                        )
                        
                        if arrows:
                            print(f"✓ {url} - Found {len(arrows)} arrows")
                        else:
                            print(f"○ {url} - No arrows found")
                    else:
                        scraping_result = ScrapingResult(
                            success=False,
                            url=url,
                            errors=["No content extracted"],
                            processing_time=time.time() - start_time
                        )
                        print(f"! {url} - No content")
                else:
                    scraping_result = ScrapingResult(
                        success=False,
                        url=url,
                        errors=[f"Crawl failed: {result.error_message}"],
                        processing_time=time.time() - start_time
                    )
                    print(f"✗ {url} - Failed")
                
        except Exception as e:
            scraping_result = ScrapingResult(
                success=False,
                url=url,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )
            print(f"✗ {url} - Error: {str(e)}")
        
        return scraping_result
    
    async def smart_scrape_manufacturer(self, manufacturer_key: str, max_products: int = 10) -> List[ScrapingResult]:
        """Smart scrape: extract product links then scrape specifications"""
        
        if manufacturer_key not in MANUFACTURERS:
            raise ValueError(f"Unknown manufacturer: {manufacturer_key}")
        
        manufacturer_config = MANUFACTURERS[manufacturer_key]
        manufacturer_name = manufacturer_config["name"]
        base_url = manufacturer_config["base_url"]
        
        print(f"\n🔍 Smart scraping {manufacturer_name}")
        print("=" * 60)
        
        # Phase 1: Extract product links from category pages
        print("Phase 1: Extracting product links...")
        all_product_links = set()
        
        # Extract from category pages
        if "categories" in manufacturer_config:
            for category, url in manufacturer_config["categories"].items():
                print(f"\nExtracting from {category} category...")
                links = await self.extract_product_links(url, base_url)
                all_product_links.update(links)
        
        # Add pre-defined specific arrow URLs
        if "arrows" in manufacturer_config:
            all_product_links.update(manufacturer_config["arrows"])
        
        # Limit number of products to scrape
        product_links = list(all_product_links)[:max_products]
        
        print(f"\nTotal unique product links found: {len(all_product_links)}")
        print(f"Will scrape: {len(product_links)} products")
        
        # Phase 2: Scrape individual product pages
        print(f"\nPhase 2: Scraping product specifications...")
        results = []
        
        for i, url in enumerate(product_links, 1):
            print(f"[{i}/{len(product_links)}] ", end="")
            result = await self.scrape_product_page(url, manufacturer_name)
            results.append(result)
        
        return results
    
    def save_smart_results(self, manufacturer_key: str, results: List[ScrapingResult]):
        """Save results with enhanced metadata"""
        
        # Collect all arrows
        all_arrows = []
        for result in results:
            if result.processed_data:
                all_arrows.extend(result.processed_data)
        
        if all_arrows:
            from config.settings import PROCESSED_DATA_DIR
            
            output_file = PROCESSED_DATA_DIR / f"{manufacturer_key}_arrows_smart.json"
            
            arrows_data = {
                "manufacturer": MANUFACTURERS[manufacturer_key]["name"],
                "scraping_method": "smart_two_phase",
                "session_id": self.session_id,
                "total_arrows": len(all_arrows),
                "arrows": [arrow.model_dump() for arrow in all_arrows],
                "scraping_summary": {
                    "product_pages_scraped": len(results),
                    "successful_extractions": sum(1 for r in results if r.success and r.arrows_found > 0),
                    "total_arrows_found": len(all_arrows),
                    "success_rate": f"{sum(1 for r in results if r.success)/len(results)*100:.1f}%",
                    "extraction_rate": f"{sum(1 for r in results if r.arrows_found > 0)/len(results)*100:.1f}%"
                },
                "sample_arrows": [arrow.model_dump() for arrow in all_arrows[:3]]
            }
            
            with open(output_file, 'w') as f:
                json.dump(arrows_data, f, indent=2, default=str)
            
            print(f"\n💾 Smart scraping results saved to: {output_file}")
        
        return all_arrows

async def test_smart_scraper():
    """Test the smart scraper"""
    print("Smart Arrow Scraper Test")
    print("=" * 40)
    
    import os
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("✗ DeepSeek API key not found")
        return
    
    try:
        scraper = SmartArrowScraper(api_key)
        
        # Test on Easton with limited products
        results = await scraper.smart_scrape_manufacturer("easton", max_products=5)
        
        # Save and analyze results
        arrows = scraper.save_smart_results("easton", results)
        
        # Print comprehensive summary
        successful_scrapes = sum(1 for r in results if r.success)
        arrows_found = sum(1 for r in results if r.arrows_found > 0)
        
        print(f"\n📊 Smart Scraping Summary:")
        print(f"   Product pages scraped: {len(results)}")
        print(f"   Successful scrapes: {successful_scrapes}/{len(results)} ({successful_scrapes/len(results)*100:.1f}%)")
        print(f"   Pages with arrows: {arrows_found}/{len(results)} ({arrows_found/len(results)*100:.1f}%)")
        print(f"   Total arrows extracted: {len(arrows)}")
        
        if arrows:
            print(f"\n🏹 Sample arrows extracted:")
            for i, arrow in enumerate(arrows[:3], 1):
                print(f"   {i}. {arrow.model_name}")
                print(f"      Spines: {arrow.spine_options}")
                print(f"      Diameter: {arrow.diameter}\" | GPI: {arrow.gpi_weight}")
        
        if len(arrows) > 0:
            print(f"\n🎉 Smart scraping successful!")
            print(f"Ready for production deployment!")
        else:
            print(f"\n⚠️  No arrows extracted - may need further tuning")
        
    except Exception as e:
        print(f"✗ Smart scraper test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_smart_scraper())