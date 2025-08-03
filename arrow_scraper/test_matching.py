#!/usr/bin/env python3
"""
Test TopHat matching logic and show database manufacturers
"""

import sqlite3
import json
from pathlib import Path

def show_database_manufacturers():
    """Show all manufacturers in the database"""
    conn = sqlite3.connect("arrow_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT manufacturer, COUNT(*) as arrow_count
        FROM arrows 
        GROUP BY manufacturer 
        ORDER BY manufacturer
    ''')
    
    print("Database Manufacturers:")
    print("=" * 40)
    for row in cursor.fetchall():
        print(f"  {row['manufacturer']} ({row['arrow_count']} arrows)")
    
    conn.close()

def show_tophat_manufacturers():
    """Show all manufacturers in TopHat data"""
    with open("data/processed/extra/tophat_archery_arrows.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    manufacturers = {}
    for arrow in data['arrows']:
        mfr = arrow['manufacturer']
        if mfr not in manufacturers:
            manufacturers[mfr] = 0
        manufacturers[mfr] += 1
    
    print("\nTopHat Manufacturers:")
    print("=" * 40)
    for mfr, count in sorted(manufacturers.items()):
        print(f"  {mfr} ({count} arrows)")

def test_specific_matches():
    """Test some specific matching cases"""
    from tophat_data_import import TopHatDataImporter
    
    # Create importer
    importer = TopHatDataImporter()
    importer.connect()
    
    # Test cases
    test_cases = [
        {"manufacturer": "Gold", "model_name": "Tip Hunter Pro"},
        {"manufacturer": "Easton", "model_name": "Powerflight"},
        {"manufacturer": "Carbon", "model_name": "Express Maxima Red"},
        {"manufacturer": "Nijora", "model_name": "Elsu Pro"},
        {"manufacturer": "OK", "model_name": "Archery Absolute.15"},
    ]
    
    print("\nTesting Specific Matches:")
    print("=" * 50)
    
    for test_arrow in test_cases:
        print(f"\nTesting: {test_arrow['manufacturer']} {test_arrow['model_name']}")
        match = importer.find_matching_arrow(test_arrow)
        
        if match:
            arrow_id, score = match
            # Get the matched arrow details
            cursor = importer.conn.cursor()
            cursor.execute('SELECT manufacturer, model_name FROM arrows WHERE id = ?', (arrow_id,))
            result = cursor.fetchone()
            print(f"  ✅ Match found: {result['manufacturer']} {result['model_name']} (score: {score:.2f})")
        else:
            print(f"  ❌ No match found")
    
    importer.conn.close()

if __name__ == "__main__":
    show_database_manufacturers()
    show_tophat_manufacturers()
    test_specific_matches()