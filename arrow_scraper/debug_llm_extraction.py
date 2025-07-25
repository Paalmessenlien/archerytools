#!/usr/bin/env python3
"""
Debug LLM extraction to see what's happening
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from scrapers.base_scraper import BaseScraper
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

async def debug_llm_extraction():
    """Debug the LLM extraction process"""
    print("Debug LLM Extraction")
    print("=" * 30)
    
    # Load environment
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    # Test URL
    test_url = "https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/"
    print(f"🔗 Testing URL: {test_url}")
    
    # Create base scraper to get prompt and schema
    scraper = BaseScraper("Easton", deepseek_api_key)
    extraction_prompt = scraper.get_extraction_prompt("Easton specific instructions")
    schema = scraper._get_extraction_schema()
    
    print("✓ Extraction prompt and schema created")
    print(f"📄 Prompt length: {len(extraction_prompt)} chars")
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        # First, let's just crawl the page and see the content
        print("\n1. Basic crawling...")
        result = await crawler.arun(url=test_url, bypass_cache=True)
        
        if result.success:
            print(f"✅ Page crawled successfully")
            print(f"📄 Content length: {len(result.markdown)} chars")
            print(f"📋 Sample content (first 500 chars):")
            print("-" * 40)
            print(result.markdown[:500])
            print("-" * 40)
            
            # Now try LLM extraction
            print("\n2. Testing LLM extraction...")
            
            try:
                llm_config = LLMConfig(
                    provider="openai/deepseek-chat",
                    api_token=deepseek_api_key,
                    base_url="https://api.deepseek.com"
                )
                
                extraction_strategy = LLMExtractionStrategy(
                    llm_config=llm_config,
                    schema=schema,
                    extraction_type="schema",
                    instruction=extraction_prompt,
                    force_json_response=True,
                    verbose=True
                )
                
                print("✓ LLM extraction strategy created")
                
                # Try extraction
                result_with_extraction = await crawler.arun(
                    url=test_url,
                    extraction_strategy=extraction_strategy,
                    bypass_cache=True
                )
                
                if result_with_extraction.success:
                    print("✅ LLM extraction completed")
                    print(f"📊 Extracted content type: {type(result_with_extraction.extracted_content)}")
                    print(f"📊 Extracted content: {result_with_extraction.extracted_content}")
                    
                    if result_with_extraction.extracted_content:
                        # Try to process it
                        processed_arrows = scraper._process_extracted_data(
                            result_with_extraction.extracted_content, 
                            test_url
                        )
                        print(f"✅ Processing successful: Found {len(processed_arrows)} arrows")
                        
                        for arrow in processed_arrows:
                            print(f"   🎯 {arrow.model_name}: {len(arrow.spine_specifications)} spine options")
                    else:
                        print("⚠️  LLM returned no extracted content")
                else:
                    print(f"❌ LLM extraction failed: {result_with_extraction.error_message}")
                    
            except Exception as e:
                print(f"💥 LLM extraction error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Failed to crawl page: {result.error_message}")

def main():
    """Run the debug"""
    asyncio.run(debug_llm_extraction())

if __name__ == "__main__":
    main()