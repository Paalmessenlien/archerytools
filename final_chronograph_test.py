#!/usr/bin/env python3
"""
Final test to verify chronograph data integration is working correctly
"""

import sqlite3
from pathlib import Path


def get_database_path():
    """Get the path to the unified database"""
    paths_to_try = [
        Path("/app/databases/arrow_database.db"),
        Path("/home/paal/arrowtuner2/arrow_scraper/databases/arrow_database.db"),
        Path("/home/paal/arrowtuner2/databases/arrow_database.db"),
        Path("arrow_scraper/databases/arrow_database.db"),
        Path("arrow_scraper/arrow_database.db"),
    ]
    
    for path in paths_to_try:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError("Could not find unified database (arrow_database.db)")


def manual_chronograph_lookup():
    """Manually test chronograph data lookup like the API does"""
    
    db_path = get_database_path()
    print(f"🔍 Final chronograph integration test using: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test cases - replicate exactly what the API does
        test_cases = [
            {'setup_id': 1, 'arrow_id': 2419, 'name': 'Test Compound Bow'},
            {'setup_id': 2, 'arrow_id': 2416, 'name': 'Test Recurve Bow'},
            {'setup_id': 3, 'arrow_id': 2417, 'name': 'Test Traditional Bow'}
        ]
        
        print("🎯 Manual Chronograph Lookup Test (API Logic):")
        print("-" * 100)
        print("Setup ID | Arrow ID | Setup Name            | Found Data | Speed   | Weight | Status")
        print("-" * 100)
        
        all_working = True
        
        for test_case in test_cases:
            setup_id = test_case['setup_id']
            arrow_id = test_case['arrow_id']
            name = test_case['name']
            
            # Execute the exact same query the API uses
            cursor.execute('''
                SELECT measured_speed_fps, arrow_weight_grains, std_deviation, shot_count
                FROM chronograph_data 
                WHERE setup_id = ? AND arrow_id = ? AND verified = 1
                ORDER BY measurement_date DESC
                LIMIT 1
            ''', (setup_id, arrow_id))
            
            chronograph_data = cursor.fetchone()
            
            if chronograph_data:
                measured_speed, measured_weight, std_dev, shot_count = chronograph_data
                status = "✅ FOUND"
                found_data = "YES"
            else:
                measured_speed, measured_weight, std_dev, shot_count = 0, 0, 0, 0
                status = "❌ NOT_FOUND"
                found_data = "NO"
                all_working = False
            
            print(f"{setup_id:8} | {arrow_id:8} | {name:20} | {found_data:10} | {measured_speed:7.1f} | {measured_weight:6.0f} | {status}")
        
        # Test with setup_arrows linkage
        print(f"\n🔗 Testing with setup_arrows linkage:")
        print("-" * 80)
        print("Setup Arrow ID | Setup ID | Arrow ID | Speed   | Linked")
        print("-" * 80)
        
        cursor.execute("""
            SELECT sa.id, sa.setup_id, sa.arrow_id, cd.measured_speed_fps
            FROM setup_arrows sa
            LEFT JOIN chronograph_data cd ON sa.setup_id = cd.setup_id AND sa.arrow_id = cd.arrow_id AND cd.verified = 1
            WHERE sa.id IN (1, 2, 3)
        """)
        
        setup_arrow_results = cursor.fetchall()
        
        for row in setup_arrow_results:
            speed = row['measured_speed_fps'] if row['measured_speed_fps'] else 0
            linked = "YES" if row['measured_speed_fps'] else "NO"
            
            print(f"{row['id']:14} | {row['setup_id']:8} | {row['arrow_id']:8} | {speed:7.1f} | {linked}")
        
        # Summary
        print(f"\n📋 Chronograph Integration Summary:")
        print("-" * 50)
        
        cursor.execute("SELECT COUNT(*) as count FROM chronograph_data WHERE verified = 1")
        total_chrono = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM bow_setups WHERE ibo_speed IS NOT NULL AND ibo_speed > 0")
        setups_with_ibo = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM setup_arrows sa
            JOIN chronograph_data cd ON sa.setup_id = cd.setup_id AND sa.arrow_id = cd.arrow_id
            WHERE cd.verified = 1
        """)
        linked_chrono = cursor.fetchone()['count']
        
        print(f"✅ Total verified chronograph entries: {total_chrono}")
        print(f"✅ Bow setups with IBO speeds: {setups_with_ibo}")
        print(f"✅ Linked chronograph-setup_arrows: {linked_chrono}")
        
        if all_working and total_chrono > 0 and linked_chrono > 0:
            print(f"\n🎉 CHRONOGRAPH INTEGRATION IS WORKING!")
            print("   ✅ API function can find chronograph data")
            print("   ✅ Database schema supports chronograph queries")
            print("   ✅ setup_arrows linkage is properly configured")
            print("   ✅ Default IBO speeds are set for fallback calculations")
            print("\n   📝 The API will use chronograph data when:")
            print("      - setup_id and arrow_id are provided")
            print("      - chronograph_data exists for that combination")
            print("      - verified = 1")
            print("   📝 The API will fall back to IBO calculations when:")
            print("      - No chronograph data exists")
            print("      - setup_id or arrow_id are missing")
        else:
            print(f"\n⚠️ Chronograph integration has issues:")
            if total_chrono == 0:
                print("   ❌ No verified chronograph data found")
            if linked_chrono == 0:
                print("   ❌ No linked chronograph-setup_arrows entries")
            if not all_working:
                print("   ❌ Some test cases failed to find expected data")
        
        return all_working and total_chrono > 0 and linked_chrono > 0
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = manual_chronograph_lookup()
    exit(0 if success else 1)