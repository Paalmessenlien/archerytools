#!/usr/bin/env python3
"""
Test script for retailer scraping functionality
Demonstrates how to enhance arrow data with retailer information
"""

import asyncio
import json
import os
from dotenv import load_dotenv

from retailer_integration import RetailerIntegrationManager
from enhance_database_schema import enhance_database_schema

async def test_retailer_scraping():
    """Test the complete retailer scraping workflow"""
    
    print("🧪 Retailer Scraping Test Suite")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
    # Initialize the system
    print("🔧 Initializing retailer integration system...")
    
    # Ensure database schema is enhanced
    enhance_database_schema()
    
    manager = RetailerIntegrationManager(api_key)
    
    # Test 1: Enhance a specific arrow with known retailer URL
    print("\n📦 Test 1: Single Arrow Enhancement")
    print("-" * 30)
    
    test_arrow_id = 1  # Adjust based on your database
    test_retailer_urls = [
        "https://tophatarchery.com/komponentensuche-nach-schaft/marke/easton/5mm/7050/easton-5mm-axis-spt-500"
    ]
    
    print(f"   Enhancing arrow ID {test_arrow_id} with retailer data...")
    result = await manager.enhance_arrow_with_retailer_data(test_arrow_id, test_retailer_urls)
    
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Sources processed: {result['total_sources']}")
        print(f"   Successful sources: {result['successful_sources']}")
        
        # Show enhanced data
        enhanced_data = manager.get_enhanced_arrow_data(test_arrow_id)
        print(f"   Enhanced data available:")
        print(f"     - Retailer sources: {len(enhanced_data.get('retailer_data', []))}")
        print(f"     - Price history entries: {len(enhanced_data.get('price_history', []))}")
        
        # Show sample retailer data
        retailer_data = enhanced_data.get('retailer_data', [])
        if retailer_data:
            sample = retailer_data[0]
            print(f"     - Sample data from {sample.get('retailer_name', 'Unknown')}:")
            print(f"       * Price: {sample.get('price', 'N/A')} {sample.get('currency', '')}")
            print(f"       * Stock: {sample.get('stock_quantity', 'N/A')}")
            print(f"       * Straightness: {sample.get('straightness_tolerance', 'N/A')}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Test 2: Batch enhancement (small batch for testing)
    print("\n📦 Test 2: Batch Enhancement")
    print("-" * 30)
    
    print("   Running batch enhancement for Easton arrows (limit: 2)...")
    batch_result = await manager.batch_enhance_arrows(manufacturer="Easton", limit=2)
    
    print(f"   Batch result: {batch_result['success']}")
    if batch_result['success']:
        print(f"   Arrows processed: {batch_result['total_arrows_processed']}")
        print(f"   Successful enhancements: {batch_result['successful_enhancements']}")
        print(f"   Total retailer sources attempted: {batch_result['total_retailer_sources_attempted']}")
        print(f"   Successful retailer sources: {batch_result['successful_retailer_sources']}")
    else:
        print(f"   Error: {batch_result.get('error', 'Unknown error')}")
    
    # Test 3: Database queries
    print("\n📊 Test 3: Enhanced Data Queries")
    print("-" * 30)
    
    # Check how many arrows now have retailer data
    import sqlite3
    conn = sqlite3.connect('arrow_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM retailer_arrow_data")
    retailer_data_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM price_history")
    price_history_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT arrow_id) FROM retailer_arrow_data")
    enhanced_arrows_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT rs.retailer_name, COUNT(rad.id) as arrow_count
        FROM retailer_sources rs
        LEFT JOIN retailer_arrow_data rad ON rs.id = rad.retailer_id
        GROUP BY rs.id
        ORDER BY arrow_count DESC
    """)
    retailer_stats = cursor.fetchall()
    
    conn.close()
    
    print(f"   Database Statistics:")
    print(f"     - Total retailer data entries: {retailer_data_count}")
    print(f"     - Total price history entries: {price_history_count}")
    print(f"     - Arrows with retailer data: {enhanced_arrows_count}")
    print(f"     - Retailer sources:")
    for retailer_name, arrow_count in retailer_stats:
        print(f"       * {retailer_name}: {arrow_count} arrows")
    
    # Test 4: API endpoint simulation
    print("\n🌐 Test 4: API Data Format")
    print("-" * 30)
    
    if enhanced_arrows_count > 0:
        # Get enhanced data for the first enhanced arrow
        enhanced_data = manager.get_enhanced_arrow_data(test_arrow_id)
        
        # Show what the API would return
        api_response = {
            'arrow_id': test_arrow_id,
            'basic_data': {
                'manufacturer': enhanced_data.get('manufacturer'),
                'model_name': enhanced_data.get('model_name'),
                'material': enhanced_data.get('material')
            },
            'retailer_data': enhanced_data.get('retailer_data', []),
            'price_history': enhanced_data.get('price_history', []),
            'total_retailer_sources': len(enhanced_data.get('retailer_data', [])),
            'has_pricing': any(d.get('price') for d in enhanced_data.get('retailer_data', []))
        }
        
        print(f"   Sample API response structure:")
        print(f"     - Basic data: {bool(api_response['basic_data']['manufacturer'])}")
        print(f"     - Retailer sources: {api_response['total_retailer_sources']}")
        print(f"     - Has pricing: {api_response['has_pricing']}")
        print(f"     - Price history: {len(api_response['price_history'])}")
        
        # Show sample pricing if available
        if api_response['has_pricing']:
            for retailer_data in api_response['retailer_data']:
                if retailer_data.get('price'):
                    print(f"     - Sample price: {retailer_data['price']} {retailer_data.get('currency', 'EUR')} from {retailer_data.get('retailer_name', 'Unknown')}")
                    break
    
    print(f"\n✅ Retailer scraping test completed!")
    print(f"   The system can now enhance arrow data with:")
    print(f"   - Detailed technical specifications")
    print(f"   - Real-time pricing and availability")
    print(f"   - Performance recommendations")
    print(f"   - Additional technical notes")
    print(f"   - Price history tracking")

def show_usage_examples():
    """Show usage examples for the retailer scraping system"""
    
    print("\n📚 Usage Examples")
    print("=" * 50)
    
    print("1. Enhance single arrow via API:")
    print("   POST /api/arrows/1/enhance-retailer-data")
    print("   {")
    print('     "retailer_urls": [')
    print('       "https://tophatarchery.com/product/easton-5mm-axis-500"')
    print('     ]')
    print("   }")
    
    print("\n2. Batch enhance arrows:")
    print("   POST /api/arrows/batch-enhance-retailer-data")
    print("   {")
    print('     "manufacturer": "Easton",')
    print('     "limit": 10')
    print("   }")
    
    print("\n3. Get enhanced arrow data:")
    print("   GET /api/arrows/1/retailer-data")
    
    print("\n4. Get arrows with pricing:")
    print("   GET /api/arrows/with-retailer-data?has_pricing=true")
    
    print("\n5. Get supported retailers:")
    print("   GET /api/retailers")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_retailer_scraping())
    
    # Show usage examples
    show_usage_examples()