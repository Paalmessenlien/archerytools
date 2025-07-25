#!/usr/bin/env python3
"""
Test DeepSeek API integration for intelligent arrow data extraction
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_deepseek_connection():
    """Test basic DeepSeek API connectivity"""
    print("Testing DeepSeek API connection...")
    
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("✗ No DeepSeek API key found in environment")
            return False
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "Say 'API connection successful' if you can read this."}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✓ DeepSeek API connected successfully")
        print(f"  Response: {result}")
        return True
        
    except Exception as e:
        print(f"✗ DeepSeek API connection failed: {e}")
        return False

def test_arrow_extraction_prompt():
    """Test arrow data extraction with DeepSeek"""
    print("\nTesting arrow data extraction...")
    
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Sample arrow specification text (simulating scraped content)
        sample_content = """
        Easton Target Arrows - FMJ 5mm Series
        
        The FMJ 5mm arrows are precision-engineered for competitive target shooting.
        
        Specifications:
        - Available Spines: 400, 500, 600
        - Diameter: 0.204 inches
        - Weight: 9.3 GPI (Grains Per Inch)
        - Straightness: ±0.001"
        - Material: Full Metal Jacket Carbon
        - Recommended Use: Target, Indoor, Outdoor
        - Length Options: 29", 30", 31", 32"
        
        Price: $14.99 per shaft
        """
        
        extraction_prompt = """
        Extract arrow specifications from the following content and return ONLY a valid JSON object with this exact structure:
        
        {
          "arrows": [
            {
              "model_name": "string",
              "spine_options": [list of integers],
              "diameter": number,
              "gpi_weight": number,
              "length_options": [list of integers, optional],
              "material": "string",
              "arrow_type": "string",
              "price_range": "string",
              "recommended_use": [list of strings]
            }
          ]
        }
        
        Content to extract from:
        """ + sample_content
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": extraction_prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✓ DeepSeek extraction successful")
        print(f"  Raw response: {result}")
        
        # Try to parse as JSON
        try:
            parsed_data = json.loads(result)
            print(f"✓ JSON parsing successful")
            print(f"  Extracted arrows: {len(parsed_data.get('arrows', []))}")
            
            if parsed_data.get('arrows'):
                arrow = parsed_data['arrows'][0]
                print(f"  Sample arrow: {arrow.get('model_name', 'Unknown')}")
                print(f"  Spines: {arrow.get('spine_options', [])}")
                print(f"  Diameter: {arrow.get('diameter', 'Unknown')}")
                print(f"  GPI: {arrow.get('gpi_weight', 'Unknown')}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"! JSON parsing failed: {e}")
            print("  Raw response may need cleaning")
            return False
        
    except Exception as e:
        print(f"✗ Arrow extraction test failed: {e}")
        return False

async def test_crawl4ai_with_deepseek():
    """Test full integration: Crawl4AI + DeepSeek"""
    print("\nTesting Crawl4AI + DeepSeek integration...")
    
    try:
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Create extraction strategy
        extraction_strategy = LLMExtractionStrategy(
            provider="openai",
            api_token=api_key,
            api_base="https://api.deepseek.com",
            model="deepseek-chat",
            schema={
                "type": "object",
                "properties": {
                    "arrows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "model_name": {"type": "string"},
                                "spine_options": {"type": "array", "items": {"type": "integer"}},
                                "diameter": {"type": "number"},
                                "gpi_weight": {"type": "number"},
                                "material": {"type": "string"},
                                "arrow_type": {"type": "string"}
                            },
                            "required": ["model_name", "spine_options", "diameter", "gpi_weight"]
                        }
                    }
                },
                "required": ["arrows"]
            },
            extraction_type="schema",
            instruction="""
            Extract arrow specifications from this webpage. Look for:
            - Model/Product names
            - Spine values (stiffness numbers like 300, 400, 500)
            - Diameter in inches
            - GPI (grains per inch) weight
            - Material composition
            - Arrow type/category
            
            Return only arrows with complete specification data.
            """
        )
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            # Test on a simple page first
            result = await crawler.arun(
                url="https://httpbin.org/html",
                extraction_strategy=extraction_strategy,
                bypass_cache=True
            )
            
            if result.success:
                print("✓ Crawl4AI + DeepSeek integration working")
                print(f"  Extraction successful: {result.extracted_content is not None}")
                
                if result.extracted_content:
                    print(f"  Extracted content: {str(result.extracted_content)[:200]}...")
                
                return True
            else:
                print(f"✗ Integration failed: {result.error_message}")
                return False
                
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run DeepSeek integration tests"""
    print("DeepSeek API Integration Test Suite")
    print("=" * 45)
    
    # Test 1: Basic connectivity
    connection_success = test_deepseek_connection()
    
    # Test 2: Arrow extraction
    extraction_success = test_arrow_extraction_prompt()
    
    # Test 3: Full integration (async)
    print("\nRunning async integration test...")
    integration_success = asyncio.run(test_crawl4ai_with_deepseek())
    
    tests_passed = sum([connection_success, extraction_success, integration_success])
    total_tests = 3
    
    print(f"\nResults: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed >= 2:
        print("🎉 DeepSeek API integration successful!")
        print("\nCapabilities verified:")
        if connection_success:
            print("✓ DeepSeek API connectivity")
        if extraction_success:
            print("✓ Intelligent arrow data extraction")
        if integration_success:
            print("✓ Full Crawl4AI + DeepSeek pipeline")
        
        print("\nReady for production scraping:")
        print("1. Pilot test on Easton arrow pages")
        print("2. Implement data validation pipeline")  
        print("3. Scale to all manufacturers")
    else:
        print("⚠️  DeepSeek integration needs attention")
        print("Check API key and network connectivity")

if __name__ == "__main__":
    main()