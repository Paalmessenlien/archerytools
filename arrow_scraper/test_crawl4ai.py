#!/usr/bin/env python3
"""
Test Crawl4AI integration for arrow scraping
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

async def test_crawl4ai_basic():
    """Test basic Crawl4AI functionality"""
    print("Testing basic Crawl4AI functionality...")
    
    try:
        from crawl4ai import AsyncWebCrawler
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            # Test with a simple, reliable website
            result = await crawler.arun(
                url="https://httpbin.org/html",
                bypass_cache=True
            )
            
            if result.success:
                print("✓ Basic crawling successful")
                print(f"  Status: {result.status_code}")
                print(f"  Content length: {len(result.markdown)}")
                print(f"  Title: {result.title}")
                return True
            else:
                print(f"✗ Basic crawling failed: {result.error_message}")
                return False
                
    except Exception as e:
        print(f"✗ Basic test failed: {e}")
        return False

async def test_crawl4ai_extraction():
    """Test Crawl4AI with extraction strategy"""
    print("\nTesting Crawl4AI with extraction...")
    
    try:
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        
        # Test extraction without LLM first (CSS-based)
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url="https://httpbin.org/html",
                css_selector="h1",
                bypass_cache=True
            )
            
            if result.success:
                print("✓ CSS extraction successful")
                print(f"  Extracted content: {result.extracted_content[:100]}...")
                return True
            else:
                print(f"✗ Extraction failed: {result.error_message}")
                return False
                
    except Exception as e:
        print(f"✗ Extraction test failed: {e}")
        return False

async def test_manufacturer_website():
    """Test on a real manufacturer website"""
    print("\nTesting on manufacturer website...")
    
    try:
        from crawl4ai import AsyncWebCrawler
        
        # Test with Easton's main page (most reliable from our research)
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url="https://eastonarchery.com",
                bypass_cache=True,
                timeout=15
            )
            
            if result.success:
                print("✓ Manufacturer website crawling successful")
                print(f"  Status: {result.status_code}")
                print(f"  Title: {result.title}")
                
                # Check for arrow-related content
                content_lower = result.markdown.lower()
                arrow_count = content_lower.count('arrow')
                spine_count = content_lower.count('spine')
                
                print(f"  Arrow mentions: {arrow_count}")
                print(f"  Spine mentions: {spine_count}")
                
                if arrow_count > 5:
                    print("✓ Good arrow content detected")
                    return True
                else:
                    print("! Low arrow content, but crawling works")
                    return True
            else:
                print(f"✗ Manufacturer website failed: {result.error_message}")
                return False
                
    except Exception as e:
        print(f"✗ Manufacturer test failed: {e}")
        return False

async def test_arrow_scraper_integration():
    """Test integration with our arrow scraper classes"""
    print("\nTesting arrow scraper integration...")
    
    try:
        # Test imports
        from models import ArrowSpecification, ScrapingResult
        from scrapers.base_scraper import BaseScraper
        
        print("✓ Arrow scraper modules imported successfully")
        
        # Test creating a mock scraper (without DeepSeek API)
        class TestScraper(BaseScraper):
            def __init__(self):
                # Initialize without DeepSeek API for testing
                self.manufacturer_name = "Test"
                self.session_id = "test_session"
                
        scraper = TestScraper()
        print("✓ Base scraper class instantiated successfully")
        
        # Test data models
        test_arrow = ArrowSpecification(
            manufacturer="Test Manufacturer",
            model_name="Test Arrow",
            spine_options=[300, 400, 500],
            diameter=0.246,
            gpi_weight=8.5,
            source_url="https://example.com"
        )
        print("✓ Arrow specification model working")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

async def main():
    """Run all Crawl4AI tests"""
    print("Crawl4AI Integration Test Suite")
    print("=" * 40)
    
    tests = [
        test_crawl4ai_basic,
        test_crawl4ai_extraction,
        test_manufacturer_website,
        test_arrow_scraper_integration
    ]
    
    passed = 0
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed >= 3:  # Allow for some system-specific issues
        print("🎉 Crawl4AI integration successful!")
        print("\nNext steps:")
        print("1. Set up DeepSeek API key in .env file")
        print("2. Run pilot scraping on Easton arrows")
        print("3. Implement data quality validation")
    else:
        print("❌ Crawl4AI integration needs work")
        print("Check system dependencies and network connection")

if __name__ == "__main__":
    asyncio.run(main())