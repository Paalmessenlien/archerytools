#!/usr/bin/env python3
"""
Test LLM extraction with TopHat Archery content
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add crawl4ai to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'crawl4ai'))

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.async_configs import LLMConfig

async def test_llm_extraction():
    """Test LLM extraction on TopHat content"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment variables")
        return
    
    print(f"✅ DeepSeek API key found: {deepseek_api_key[:8]}...")
    
    # Test URL
    test_url = "https://tophatarchery.com/search-by-shaft/brands/aurel/7933/aurel-agil-300"
    
    # Create simple extraction strategy
    extraction_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="deepseek",
            api_token=deepseek_api_key,
        ),
        schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Product title"},
                "spine": {"type": "string", "description": "Arrow spine value"},
                "manufacturer": {"type": "string", "description": "Manufacturer name"},
            },
            "required": ["title"]
        },
        instruction="Extract the product title, spine value, and manufacturer from this arrow product page."
    )
    
    print(f"🎯 Testing LLM extraction on: {test_url}")
    
    async with AsyncWebCrawler() as crawler:
        # First, get the content
        result = await crawler.arun(url=test_url)
        
        if not result.success:
            print(f"❌ Failed to fetch content: {result.error_message}")
            return
        
        print(f"✅ Content fetched successfully")
        print(f"📊 HTML length: {len(result.html)}")
        print(f"📊 Markdown length: {len(result.markdown)}")
        
        # Now test with LLM extraction
        print(f"🤖 Testing LLM extraction...")
        
        llm_result = await crawler.arun(
            url=test_url,
            extraction_strategy=extraction_strategy
        )
        
        if llm_result.success:
            print(f"✅ LLM extraction successful!")
            
            if llm_result.extracted_content:
                try:
                    extracted_data = json.loads(llm_result.extracted_content)
                    print(f"📋 Extracted data:")
                    print(json.dumps(extracted_data, indent=2))
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse extracted content as JSON: {e}")
                    print(f"📜 Raw extracted content: {llm_result.extracted_content}")
            else:
                print(f"⚠️  No extracted content returned")
        else:
            print(f"❌ LLM extraction failed: {llm_result.error_message}")
        
        # Check for extraction errors
        if hasattr(llm_result, 'extraction_error'):
            print(f"🔍 Extraction error: {llm_result.extraction_error}")

if __name__ == "__main__":
    asyncio.run(test_llm_extraction())