#!/usr/bin/env python3
"""Test script to verify chronograph database path resolution"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Change to project root directory so database path resolution works correctly  
os.chdir(Path(__file__).parent.parent)

from arrow_database import ArrowDatabase

def test_chronograph_database_path():
    """Test that the API can find chronograph data in the correct database"""
    
    print("🔍 Testing database path resolution...")
    
    # Create database instance like the API does
    try:
        db = ArrowDatabase()
        print(f"✅ Database created successfully")
        print(f"📍 Database path: {db.db_path}")
        
        # Test database connection
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check if chronograph_data table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chronograph_data'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ chronograph_data table found")
            
            # Check for our test data (setup_id=2, arrow_id=832)
            print("\n🔍 Debugging chronograph data query...")
            
            # First, check all chronograph data
            cursor.execute('SELECT id, setup_id, arrow_id, measured_speed_fps, verified FROM chronograph_data LIMIT 10')
            all_data = cursor.fetchall()
            print(f"📊 Found {len(all_data)} chronograph records total:")
            for record in all_data:
                print(f"   ID: {record[0]}, Setup: {record[1]}, Arrow: {record[2]}, Speed: {record[3]}, Verified: {record[4]}")
            
            # Now check specific query
            cursor.execute('''
                SELECT id, setup_id, arrow_id, measured_speed_fps, arrow_weight_grains, verified, measurement_date
                FROM chronograph_data 
                WHERE setup_id = 2 AND arrow_id = 832 AND verified = 1
                ORDER BY measurement_date DESC
                LIMIT 1
            ''')
            
            chronograph_data = cursor.fetchone()
            
            if chronograph_data:
                print(f"✅ Chronograph data found:")
                print(f"   ID: {chronograph_data[0]}")
                print(f"   Setup ID: {chronograph_data[1]}")
                print(f"   Arrow ID: {chronograph_data[2]}")
                print(f"   Measured Speed: {chronograph_data[3]} fps")
                print(f"   Arrow Weight: {chronograph_data[4]} gr")
                print(f"   Verified: {chronograph_data[5]}")
                print(f"   Date: {chronograph_data[6]}")
                
                # Test the enhanced speed calculation with the same parameters
                print("\n🧪 Testing enhanced speed calculation...")
                from api import calculate_enhanced_arrow_speed_internal
                
                result = calculate_enhanced_arrow_speed_internal(
                    bow_ibo_speed=320,
                    bow_draw_weight=60,
                    bow_draw_length=28,
                    bow_type='compound',
                    arrow_weight_grains=295,  # This should match the chronograph data weight
                    setup_id=2,
                    arrow_id=832
                )
                
                print(f"🎯 Enhanced speed calculation result: {result} fps")
                print(f"🔍 Expected: ~285 fps (from chronograph data)")
                
                if abs(result - 285.0) < 1.0:
                    print("✅ SUCCESS: Enhanced speed calculation is using chronograph data!")
                else:
                    print("❌ ISSUE: Enhanced speed calculation is not using chronograph data")
                    print(f"   Got: {result} fps, Expected: ~285 fps")
                    
            else:
                print("❌ No chronograph data found for setup_id=2, arrow_id=832")
                
        else:
            print("❌ chronograph_data table not found")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chronograph_database_path()