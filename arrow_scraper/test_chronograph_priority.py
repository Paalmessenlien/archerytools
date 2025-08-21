#!/usr/bin/env python3
"""Test that chronograph data takes priority over estimated speed"""

import os
import sqlite3
from pathlib import Path

def test_chronograph_priority():
    """Test that chronograph data is used instead of estimates"""
    
    # Use the correct database path
    db_path = "/home/paal/archerytools/databases/arrow_database.db"
    
    print("🔍 Testing chronograph data priority...")
    print(f"📍 Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing chronograph data
        cursor.execute('''
            SELECT cd.id, cd.setup_id, cd.arrow_id, cd.setup_arrow_id, 
                   cd.measured_speed_fps, cd.verified, a.manufacturer, a.model_name
            FROM chronograph_data cd
            LEFT JOIN arrows a ON cd.arrow_id = a.id
            WHERE cd.verified = 1
            ORDER BY cd.measurement_date DESC
        ''')
        
        chronograph_records = cursor.fetchall()
        print(f"📊 Found {len(chronograph_records)} verified chronograph records:")
        
        for record in chronograph_records:
            print(f"   Setup: {record[1]}, Arrow: {record[2]}, Speed: {record[4]} fps")
            print(f"   Arrow: {record[6]} {record[7]}")
            
            # For each chronograph record, check what the performance analysis shows
            cursor.execute('''
                SELECT performance_data 
                FROM setup_arrows 
                WHERE setup_id = ? AND arrow_id = ?
            ''', (record[1], record[2]))
            
            perf_data = cursor.fetchone()
            if perf_data and perf_data[0]:
                import json
                try:
                    performance = json.loads(perf_data[0])
                    estimated_speed = performance.get('performance_summary', {}).get('estimated_speed_fps', 'N/A')
                    speed_source = performance.get('performance_summary', {}).get('speed_source', 'unknown')
                    
                    print(f"   Performance shows: {estimated_speed} fps (source: {speed_source})")
                    
                    # Check if performance matches chronograph
                    measured_speed = record[4]  # measured_speed_fps
                    if abs(float(estimated_speed) - float(measured_speed)) < 1.0:
                        print(f"   ✅ Performance uses chronograph data!")
                    else:
                        print(f"   ❌ Performance NOT using chronograph data!")
                        print(f"      Expected: {measured_speed} fps (chronograph)")
                        print(f"      Got: {estimated_speed} fps (performance)")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid performance data JSON")
            else:
                print(f"   ⚠️  No performance data calculated yet")
            print()
        
        conn.close()
        
        if len(chronograph_records) == 0:
            print("❌ No verified chronograph data found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chronograph_priority()