#!/usr/bin/env python3
"""
Debug LLM extraction with comprehensive logging
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

async def debug_extraction():
    """Debug the LLM extraction step by step"""
    print("🔍 Debugging LLM Extraction")
    print("=" * 30)
    
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    print(f"✓ API Key found")
    
    # Very simple schema and prompt
    simple_schema = {
        "type": "object",
        "properties": {
            "test_extraction": {"type": "string"}
        }
    }
    
    simple_prompt = "Extract any text you can find. Return as 'test_extraction'."
    
    try:
        llm_config = LLMConfig(
            provider="openai/deepseek-chat",
            api_token=deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
        print("✓ LLM Config created")
        
        extraction_strategy = LLMExtractionStrategy(
            llm_config=llm_config,
            schema=simple_schema,
            extraction_type="schema",
            instruction=simple_prompt,
            force_json_response=True,
            verbose=True
        )
        print("✓ Extraction strategy created")
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            print("\\n🔗 Testing with Easton arrow URL...")
            
            result = await crawler.arun(
                url="https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/",
                extraction_strategy=extraction_strategy,
                bypass_cache=True
            )
            
            print(f"\\n📊 Crawling Success: {result.success}")
            print(f"📄 Content Length: {len(result.markdown)} chars")
            print(f"🤖 Extracted Content: {result.extracted_content}")
            
            if result.extracted_content is None:
                print("\\n❌ LLM returned None - checking raw response...")
                
                # Let's try a non-LLM extraction to see the content
                result_no_llm = await crawler.arun(
                    url="https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/",
                    bypass_cache=True
                )
                
                print(f"\\n📄 Full content sample (chars 5000-7000):")
                print(result_no_llm.markdown[5000:7000])
                
                # Search for the table data specifically
                content_lower = result_no_llm.markdown.lower()
                table_start = content_lower.find('table')
                if table_start > -1:
                    print(f"\\n📋 Found table at position {table_start}")
                    print(f"Table content sample:")
                    print(result_no_llm.markdown[table_start:table_start+1000])
                else:
                    print("\\n❌ No table found in content")
                    
                    # Look for specific arrow data
                    spine_pos = content_lower.find('spine')
                    if spine_pos > -1:
                        print(f"\\nFound 'spine' at position {spine_pos}:")
                        print(result_no_llm.markdown[spine_pos-100:spine_pos+200])
            
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    asyncio.run(debug_extraction())

if __name__ == "__main__":
    main()