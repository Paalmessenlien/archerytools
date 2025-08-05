#!/usr/bin/env python3
"""
Auto-generated scraping script for TopHat Archery URLs
Generated at: 2025-08-04T06:45:05.432939
"""

import asyncio
import json
import sys
from pathlib import Path
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

# URLs to scrape
URLS_TO_SCRAPE = ['https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton/xx75/7260/easton-xx75-camo-hunter-2016', 'https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton/xx75/7261/easton-xx75-camo-hunter-2018']

# DeepSeek API key (should be set in environment)
import os
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

if not DEEPSEEK_API_KEY:
    print("❌ DEEPSEEK_API_KEY not found in environment")
    sys.exit(1)

async def scrape_tophat_products():
    """Scrape product data from TopHat Archery URLs"""
    
    # Define extraction schema for arrow data
    extraction_schema = {
        "type": "object",
        "properties": {
            "manufacturer": {
                "type": "string",
                "description": "Arrow manufacturer (e.g., Easton, Gold Tip, Victory)"
            },
            "model_name": {
                "type": "string", 
                "description": "Full arrow model name"
            },
            "spine": {
                "type": "integer",
                "description": "Arrow spine value (e.g., 340, 500, 600)"
            },
            "outer_diameter": {
                "type": "number",
                "description": "Outer diameter in inches (convert from mm if needed)"
            },
            "inner_diameter": {
                "type": "number", 
                "description": "Inner diameter in inches (convert from mm if needed)"
            },
            "gpi_weight": {
                "type": "number",
                "description": "Weight in grains per inch (GPI)"
            },
            "straightness_tolerance": {
                "type": "string",
                "description": "Straightness tolerance (e.g., ±.006\", ±.003\")"
            },
            "weight_tolerance": {
                "type": "string",
                "description": "Weight tolerance if specified"
            },
            "length_options": {
                "type": "array",
                "items": {"type": "number"},
                "description": "Available arrow lengths in inches"
            },
            "price": {
                "type": "number",
                "description": "Price as decimal number"
            },
            "currency": {
                "type": "string",
                "description": "Currency code (EUR, USD, etc.)"
            },
            "stock_quantity": {
                "type": "integer",
                "description": "Available stock quantity"
            },
            "availability_status": {
                "type": "string",
                "description": "Stock status (in_stock, out_of_stock, limited, etc.)"
            },
            "product_description": {
                "type": "string",
                "description": "Full product description"
            },
            "technical_notes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Additional technical specifications and notes"
            }
        },
        "required": ["manufacturer", "model_name"]
    }
    
    # Create extraction strategy
    extraction_strategy = LLMExtractionStrategy(
        provider="openai",
        api_token=DEEPSEEK_API_KEY,
        schema=extraction_schema,
        extraction_type="schema",
        instruction="""
        Extract detailed arrow specifications from this TopHat Archery product page.
        
        Focus on:
        1. Complete technical specifications (spine, diameters, weight, tolerances)
        2. Pricing and availability information
        3. Performance characteristics
        4. Any additional technical details not found on manufacturer sites
        
        Convert metric measurements to inches where needed (1mm = 0.0394 inches).
        Extract all available spine options if multiple are shown.
        Include performance recommendations and technical notes.
        """
    )
    
    results = []
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        for i, url in enumerate(URLS_TO_SCRAPE):
            try:
                print(f"Scraping {i+1}/{len(URLS_TO_SCRAPE)}: {url}")
                
                result = await crawler.arun(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    bypass_cache=True,
                    wait_for="css:.product-details"
                )
                
                if result.success:
                    try:
                        extracted_data = json.loads(result.extracted_content)
                        extracted_data['source_url'] = url
                        extracted_data['scraped_at'] = "2025-08-04T06:45:05.432944"
                        results.append(extracted_data)
                        print(f"✅ Successfully scraped: {extracted_data.get('manufacturer', 'Unknown')} {extracted_data.get('model_name', 'Unknown')}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse JSON for {url}: {e}")
                        results.append({"error": "JSON decode error", "url": url})
                else:
                    print(f"❌ Failed to scrape {url}: {result.error_message}")
                    results.append({"error": result.error_message, "url": url})
                
                # Add delay between requests
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Exception scraping {url}: {e}")
                results.append({"error": str(e), "url": url})
    
    # Save results
    output_path = Path("/root/archerytools/arrow_scraper/data/retailer_scraping/results_easton_064505_20250804_064505.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Scraping completed! Results saved to: {output_path}")
    print(f"   Total URLs processed: {len(URLS_TO_SCRAPE)}")
    print(f"   Successful extractions: {len([r for r in results if 'error' not in r])}")
    print(f"   Errors: {len([r for r in results if 'error' in r])}")
    
    return results

if __name__ == "__main__":
    asyncio.run(scrape_tophat_products())
