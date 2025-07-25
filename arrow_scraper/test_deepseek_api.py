#!/usr/bin/env python3
"""
Test DeepSeek API directly to verify it's working
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

async def test_deepseek_api():
    """Test DeepSeek API with a simple extraction"""
    print("Testing DeepSeek API Directly")
    print("=" * 35)
    
    # Load environment
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    print(f"✓ API Key: {deepseek_api_key[:10]}...")
    
    # Simple test content
    test_content = """
    4MM Axis Long Range Match Grade Arrow
    
    Specifications:
    - Spine: 250, 300, 340, 400
    - Diameter: 0.244 inches
    - GPI Weight: 9.8 grains per inch
    - Material: 100% Carbon Fiber
    - Type: Hunting Arrow
    - Length: 32-33 inches available
    
    Perfect for long-range hunting applications.
    """
    
    # Simple schema
    simple_schema = {
        "type": "object",
        "properties": {
            "arrows": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "model_name": {"type": "string"},
                        "spine_values": {"type": "array", "items": {"type": "integer"}},
                        "diameter": {"type": "number"},
                        "gpi_weight": {"type": "number"}
                    }
                }
            }
        }
    }
    
    # Simple prompt
    simple_prompt = """
    Extract arrow specifications from this content.
    Look for model name, spine values, diameter, and GPI weight.
    Return in the specified JSON format.
    """
    
    try:
        # Create LLM config
        llm_config = LLMConfig(
            provider="openai/deepseek-chat",
            api_token=deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
        
        print("✓ LLM Config created")
        
        # Create extraction strategy
        extraction_strategy = LLMExtractionStrategy(
            llm_config=llm_config,
            schema=simple_schema,
            extraction_type="schema",
            instruction=simple_prompt,
            force_json_response=True,
            verbose=True
        )
        
        print("✓ Extraction strategy created")
        
        # Test with simple HTML content
        test_html = f"<html><body><h1>Test Content</h1><p>{test_content}</p></body></html>"
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            # Test with a simple URL first
            print("\n1. Testing with simple example.com...")
            result = await crawler.arun(
                url="https://example.com",
                extraction_strategy=extraction_strategy,
                bypass_cache=True
            )
            
            if result.success:
                print(f"✅ Basic extraction test successful")
                print(f"📊 Extracted: {result.extracted_content}")
            else:
                print(f"❌ Basic extraction failed: {result.error_message}")
            
            # Test with arrow URL
            print("\n2. Testing with real arrow URL...")
            arrow_result = await crawler.arun(
                url="https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/",
                extraction_strategy=extraction_strategy,
                bypass_cache=True
            )
            
            if arrow_result.success:
                print(f"✅ Arrow URL extraction successful")
                print(f"📊 Extracted: {arrow_result.extracted_content}")
                
                # Show raw content for debugging
                print(f"\n📄 Raw content (first 2000 chars):")
                print(f"{arrow_result.markdown[:2000]}...")
                
                if arrow_result.extracted_content:
                    print("🎉 LLM successfully returned data!")
                else:
                    print("⚠️  LLM returned None - possible content issue")
                    
                    # Test a simple manual extraction without LLM
                    print("\n🔍 Looking for table data in raw content...")
                    if "tablepress" in arrow_result.markdown.lower():
                        print("✓ Found 'tablepress' in content")
                    if "spine" in arrow_result.markdown.lower():
                        print("✓ Found 'spine' in content")
                    if "gpi" in arrow_result.markdown.lower():
                        print("✓ Found 'gpi' in content")
                    if "diameter" in arrow_result.markdown.lower():
                        print("✓ Found 'diameter' in content")
            else:
                print(f"❌ Arrow URL extraction failed: {arrow_result.error_message}")
                
    except Exception as e:
        print(f"💥 API test error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the API test"""
    asyncio.run(test_deepseek_api())

if __name__ == "__main__":
    main()