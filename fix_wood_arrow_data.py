#!/usr/bin/env python3
"""
Fix wood arrow data by importing proper manufacturers and data from wood_arrows_data.json
"""
import sqlite3
import json
import sys
from pathlib import Path

def fix_wood_arrow_data():
    """Replace the 'Unknown' wood arrows with proper 'Traditional Wood' data"""
    print("🏹 Fixing wood arrow manufacturer data...")
    
    # Connect to the arrow database
    db_path = "/home/paal/archerytools/arrow_scraper/arrow_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, let's see what wood arrows we currently have
        cursor.execute("SELECT id, manufacturer, model_name, material FROM arrows WHERE material LIKE '%Wood'")
        current_wood_arrows = cursor.fetchall()
        
        print(f"📊 Current wood arrows in database:")
        for arrow in current_wood_arrows:
            print(f"  • ID {arrow[0]}: {arrow[1]} - {arrow[2]} ({arrow[3]})")
        
        # Update all wood arrows to have proper manufacturer
        wood_materials = [
            'Cedar Wood', 'Pine Wood', 'Ash Wood', 'Birch Wood', 
            'Bamboo Wood', 'Fir Wood', 'Sitka Spruce Wood', 'Douglas Fir Wood',
            'Port Orford Cedar Wood', 'European Ash Wood', 'Baltic Birch Wood', 'Northern Pine Wood'
        ]
        
        updated_count = 0
        for material in wood_materials:
            cursor.execute("""
                UPDATE arrows 
                SET manufacturer = 'Traditional Wood' 
                WHERE material = ? AND manufacturer = 'Unknown'
            """, (material,))
            updated_count += cursor.rowcount
        
        conn.commit()
        print(f"✅ Updated {updated_count} wood arrows to use 'Traditional Wood' manufacturer")
        
        # Verify the changes
        cursor.execute("SELECT manufacturer, model_name, material FROM arrows WHERE material LIKE '%Wood' ORDER BY manufacturer, material")
        updated_arrows = cursor.fetchall()
        
        print(f"\n📊 Updated wood arrows:")
        for arrow in updated_arrows:
            print(f"  • {arrow[0]} - {arrow[1]} ({arrow[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing wood arrow data: {e}")
        return False

if __name__ == "__main__":
    if fix_wood_arrow_data():
        print("\n🎉 Wood arrow manufacturer data fixed successfully!")
        print("✅ All wood arrows now show 'Traditional Wood' as manufacturer")
    else:
        print("\n❌ Failed to fix wood arrow data")
        sys.exit(1)