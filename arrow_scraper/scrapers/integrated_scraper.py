#!/usr/bin/env python3
"""
Integrated Arrow Scraper
Combines Crawl4AI web crawling with DeepSeek intelligent extraction
"""

import asyncio
import json
import time
from typing import List, Dict, Any
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from crawl4ai import AsyncWebCrawler
from deepseek_extractor import DeepSeekArrowExtractor
from models import ArrowSpecification, ScrapingResult, ScrapingSession
from config.settings import CRAWL_SETTINGS, MANUFACTURERS

class IntegratedArrowScraper:
    """Complete arrow scraper combining Crawl4AI + DeepSeek"""
    
    def __init__(self, deepseek_api_key: str):
        """Initialize scraper with DeepSeek API key"""
        self.extractor = DeepSeekArrowExtractor(deepseek_api_key)
        self.session_id = f"integrated_{int(time.time())}"
        
    async def scrape_single_url(self, url: str, manufacturer: str) -> ScrapingResult:
        """Scrape a single URL and extract arrow specifications"""
        start_time = time.time()
        
        try:
            print(f"Scraping: {url}")
            
            # Add delay for respectful crawling
            await asyncio.sleep(1.5)
            
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(
                    url=url,
                    bypass_cache=True,
                    timeout=CRAWL_SETTINGS["timeout"]
                )
                
                if result.success:
                    # Extract content for processing
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
                        
                        print(f"✓ Success: {url} - Found {len(arrows)} arrows")
                        
                    else:
                        scraping_result = ScrapingResult(
                            success=False,
                            url=url,
                            errors=["No content extracted"],
                            processing_time=time.time() - start_time
                        )
                        print(f"! Warning: {url} - No content extracted")
                else:
                    scraping_result = ScrapingResult(
                        success=False,
                        url=url,
                        errors=[f"Crawl failed: {result.error_message}"],
                        processing_time=time.time() - start_time
                    )
                    print(f"✗ Failed: {url} - {result.error_message}")
                
        except Exception as e:
            scraping_result = ScrapingResult(
                success=False,
                url=url,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )
            print(f"✗ Error: {url} - {str(e)}")
        
        return scraping_result
    
    async def scrape_manufacturer(self, manufacturer_key: str, limit: int = None) -> List[ScrapingResult]:
        """Scrape all URLs for a specific manufacturer"""
        
        if manufacturer_key not in MANUFACTURERS:
            raise ValueError(f"Unknown manufacturer: {manufacturer_key}")
        
        manufacturer_config = MANUFACTURERS[manufacturer_key]
        manufacturer_name = manufacturer_config["name"]
        
        print(f"\nStarting scrape of {manufacturer_name}")
        print("-" * 50)
        
        # Collect URLs to scrape
        urls_to_scrape = []
        
        # Add category URLs
        if "categories" in manufacturer_config:
            urls_to_scrape.extend(manufacturer_config["categories"].values())
        
        # Add specific arrow URLs
        if "arrows" in manufacturer_config:
            urls_to_scrape.extend(manufacturer_config["arrows"])
        
        # Apply limit if specified
        if limit:
            urls_to_scrape = urls_to_scrape[:limit]
        
        print(f"URLs to scrape: {len(urls_to_scrape)}")
        
        # Scrape each URL
        results = []
        for i, url in enumerate(urls_to_scrape, 1):
            print(f"\n[{i}/{len(urls_to_scrape)}] ", end="")
            result = await self.scrape_single_url(url, manufacturer_name)
            results.append(result)
        
        return results
    
    def save_results(self, manufacturer_key: str, results: List[ScrapingResult]):
        """Save scraping results to files"""
        
        # Collect all arrows
        all_arrows = []
        for result in results:
            if result.processed_data:
                all_arrows.extend(result.processed_data)
        
        # Save arrows to JSON
        if all_arrows:
            from config.settings import PROCESSED_DATA_DIR
            
            output_file = PROCESSED_DATA_DIR / f"{manufacturer_key}_arrows_integrated.json"
            
            # Convert to dict format for JSON serialization
            arrows_data = {
                "manufacturer": MANUFACTURERS[manufacturer_key]["name"],
                "scraping_session": self.session_id,
                "total_arrows": len(all_arrows),
                "arrows": [arrow.model_dump() for arrow in all_arrows],
                "scraping_summary": {
                    "urls_scraped": len(results),
                    "successful_scrapes": sum(1 for r in results if r.success),
                    "total_arrows_found": len(all_arrows),
                    "avg_processing_time": sum(r.processing_time for r in results) / len(results) if results else 0
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(arrows_data, f, indent=2, default=str)
            
            print(f"\n💾 Results saved to: {output_file}")
            print(f"   Total arrows: {len(all_arrows)}")
        
        return all_arrows

async def test_integrated_scraper():
    """Test the integrated scraper on a manufacturer"""
    print("Integrated Arrow Scraper Test")
    print("=" * 40)
    
    import os
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("✗ DeepSeek API key not found in environment")
        return
    
    try:
        scraper = IntegratedArrowScraper(api_key)
        
        # Test on Easton (limit to 2 URLs for testing)
        print("Testing on Easton Archery (limited to 2 URLs)...")
        results = await scraper.scrape_manufacturer("easton", limit=2)
        
        # Save results
        arrows = scraper.save_results("easton", results)
        
        # Print summary
        successful_scrapes = sum(1 for r in results if r.success)
        total_arrows = len(arrows)
        
        print(f"\n📊 Scraping Summary:")
        print(f"   URLs processed: {len(results)}")
        print(f"   Successful scrapes: {successful_scrapes}/{len(results)}")
        print(f"   Total arrows found: {total_arrows}")
        print(f"   Success rate: {successful_scrapes/len(results)*100:.1f}%")
        
        # Show sample arrows
        if arrows:
            print(f"\n🏹 Sample arrows found:")
            for i, arrow in enumerate(arrows[:3], 1):
                print(f"   {i}. {arrow.model_name}")
                print(f"      Spines: {arrow.spine_options}")
                print(f"      Diameter: {arrow.diameter}\"")
                print(f"      GPI: {arrow.gpi_weight}")
        
        if total_arrows > 0:
            print(f"\n🎉 Integration test successful!")
            print(f"Ready for full-scale scraping!")
        else:
            print(f"\n⚠️  No arrows extracted - may need prompt tuning")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_integrated_scraper())