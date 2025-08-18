#!/usr/bin/env python3
"""
Test chronograph data integration with performance calculations
"""

import sqlite3
from pathlib import Path


def get_database_path():
    """Get the path to the unified database"""
    paths_to_try = [
        Path("/app/databases/arrow_database.db"),
        Path(__file__).parent / "databases" / "arrow_database.db",
        Path(__file__).parent / "arrow_database.db",
    ]
    
    for path in paths_to_try:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError("Could not find unified database (arrow_database.db)")


def test_chronograph_integration():
    """Test that chronograph data is properly integrated"""
    
    db_path = get_database_path()
    print(f"🧪 Testing chronograph integration in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test 1: Verify chronograph data exists
        cursor.execute("SELECT COUNT(*) as count FROM chronograph_data WHERE verified = 1")
        chrono_count = cursor.fetchone()['count']
        print(f"✅ Found {chrono_count} verified chronograph measurements")
        
        # Test 2: Verify bow setups have IBO speeds
        cursor.execute("SELECT bow_type, COUNT(*) as count, AVG(ibo_speed) as avg_ibo FROM bow_setups WHERE ibo_speed IS NOT NULL GROUP BY bow_type")
        bow_stats = cursor.fetchall()
        
        print(f"\n📊 Bow setups with IBO speeds:")
        for row in bow_stats:
            print(f"  {row['bow_type']:12} | {row['count']:3} setups | Avg IBO: {row['avg_ibo']:.0f} fps")
        
        # Test 3: Show actual chronograph data with bow setups
        cursor.execute("""
            SELECT bs.name, bs.bow_type, bs.draw_weight, bs.draw_length, bs.ibo_speed,
                   cd.measured_speed_fps, cd.arrow_weight_grains, cd.shot_count, cd.chronograph_model
            FROM bow_setups bs
            JOIN chronograph_data cd ON bs.id = cd.setup_id
            WHERE cd.verified = 1
            ORDER BY bs.bow_type
        """)
        
        results = cursor.fetchall()
        
        print(f"\n🎯 Chronograph Data Integration Test:")
        print("-" * 120)
        print("Setup Name               | Bow Type    | IBO Speed | Measured Speed | Arrow Weight | Shots | Chronograph")
        print("-" * 120)
        
        for row in results:
            name = row['name'] or 'Unknown'
            bow_type = row['bow_type'] or 'Unknown'
            ibo_speed = row['ibo_speed'] or 0
            measured_speed = row['measured_speed_fps'] or 0
            arrow_weight = row['arrow_weight_grains'] or 0
            shot_count = row['shot_count'] or 0
            chronograph = row['chronograph_model'] or 'Unknown'
            
            print(f"{name:24} | {bow_type:11} | {ibo_speed:9.0f} | {measured_speed:14.1f} | {arrow_weight:12.0f} | {shot_count:5} | {chronograph}")
        
        # Test 4: Simple performance calculation
        print(f"\n🧮 Manual Performance Calculation Test:")
        print("-" * 80)
        
        for row in results:
            # Simplified arrow speed calculation using chronograph data
            chronograph_speed = row['measured_speed_fps']
            calculated_speed = estimate_speed_from_ibo(
                row['ibo_speed'], 
                row['draw_weight'], 
                row['draw_length'], 
                row['arrow_weight_grains']
            )
            
            accuracy = "GOOD" if abs(chronograph_speed - calculated_speed) < 20 else "NEEDS IMPROVEMENT"
            
            print(f"  {row['name']:24} | Measured: {chronograph_speed:6.1f} fps | Calculated: {calculated_speed:6.1f} fps | {accuracy}")
        
        print(f"\n✅ Chronograph integration test completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


def estimate_speed_from_ibo(ibo_speed, draw_weight, draw_length, arrow_weight_grains):
    """
    Simplified arrow speed estimation from IBO speed
    This is a basic approximation for testing purposes
    """
    if not all([ibo_speed, draw_weight, draw_length, arrow_weight_grains]):
        return 0
    
    # Basic IBO formula adjustments
    weight_adjustment = (draw_weight - 70) * 2.0  # 2 fps per pound difference from 70#
    length_adjustment = (draw_length - 30) * 10   # 10 fps per inch difference from 30"
    arrow_weight_adjustment = (350 - arrow_weight_grains) * 0.5  # 0.5 fps per grain difference from 350gr
    
    estimated_speed = ibo_speed + weight_adjustment + length_adjustment + arrow_weight_adjustment
    
    return max(estimated_speed, 50)  # Minimum reasonable speed


if __name__ == "__main__":
    success = test_chronograph_integration()
    exit(0 if success else 1)