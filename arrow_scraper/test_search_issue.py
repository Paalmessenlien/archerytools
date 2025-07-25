#!/usr/bin/env python3
"""
Debug the search issue for compatible arrows
"""

from arrow_database import ArrowDatabase

def test_search_issue():
    """Test what's happening with the search"""
    
    print("🔧 Testing search issue...")
    
    db = ArrowDatabase()
    
    # Test 1: Basic search like the API does
    print("\n🔍 Test 1: Basic search (like API)")
    results = db.search_arrows(manufacturer=None, arrow_type=None, model_search=None, limit=50)
    print(f"   Found {len(results)} arrows")
    
    # Count wood arrows in results
    wood_count = sum(1 for arrow in results if arrow.get('material') and 'wood' in arrow.get('material', '').lower())
    print(f"   Wood arrows in results: {wood_count}")
    
    # Test 2: Search specifically for Traditional Wood
    print("\n🔍 Test 2: Search for Traditional Wood manufacturer")
    wood_results = db.search_arrows(manufacturer="Traditional Wood", limit=50)
    print(f"   Found {len(wood_results)} arrows from Traditional Wood")
    
    # Test 3: Search for Traditional Wood Arrows
    print("\n🔍 Test 3: Search for Traditional Wood Arrows manufacturer") 
    wood_arrows_results = db.search_arrows(manufacturer="Traditional Wood Arrows", limit=50)
    print(f"   Found {len(wood_arrows_results)} arrows from Traditional Wood Arrows")
    
    # Test 4: Show first few arrows from basic search
    print("\n🔍 Test 4: First 10 arrows from basic search")
    for i, arrow in enumerate(results[:10]):
        material = arrow.get('material', 'None')
        is_wood = material and 'wood' in material.lower()
        print(f"   {i+1:2d}. {arrow.get('manufacturer', 'N/A'):20} {arrow.get('model_name', 'N/A')[:30]:30} | {material:15} | Wood: {is_wood}")
    
    # Test 5: Check if wood arrows exist at all
    print(f"\n🔍 Test 5: Raw database query for wood arrows")
    import sqlite3
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM arrows WHERE material LIKE '%Wood%'")
    wood_count_db = cursor.fetchone()[0]
    print(f"   Total wood arrows in database: {wood_count_db}")
    
    # Show some wood arrow examples
    cursor.execute("SELECT manufacturer, model_name, material FROM arrows WHERE material LIKE '%Wood%' LIMIT 5")
    wood_examples = cursor.fetchall()
    print(f"   Wood arrow examples:")
    for example in wood_examples:
        print(f"     {example[0]} | {example[1]} | {example[2]}")

if __name__ == "__main__":
    test_search_issue()