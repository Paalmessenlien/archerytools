#!/usr/bin/env python3
"""
Identify the source of the 276.1 fps calculation
"""

import sqlite3
from pathlib import Path


def get_database_path():
    """Get the path to the unified database"""
    paths_to_try = [
        Path("/app/databases/arrow_database.db"),
        Path("/home/paal/arrowtuner2/arrow_scraper/databases/arrow_database.db"),
        Path("/home/paal/arrowtuner2/databases/arrow_database.db"),
    ]
    
    for path in paths_to_try:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError("Could not find unified database (arrow_database.db)")


def calculate_enhanced_arrow_speed_internal_simulation(bow_ibo_speed, bow_draw_weight, bow_draw_length, bow_type, arrow_weight_grains, string_material='dacron', setup_id=None, arrow_id=None):
    """Simulate the enhanced arrow speed calculation to see what might return 276.1 fps"""
    
    # First check chronograph data
    if setup_id and arrow_id:
        db_path = get_database_path()
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
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
                print(f"    Chronograph data found: {measured_speed} fps (weight: {measured_weight}g, shots: {shot_count})")
                return measured_speed
            else:
                print(f"    No chronograph data found for setup_id={setup_id}, arrow_id={arrow_id}")
                
        except Exception as e:
            print(f"    Chronograph lookup error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    # Fall back to IBO calculation
    print(f"    Using IBO calculation fallback")
    
    # String material speed adjustments
    string_adjustments = {
        'dacron': -20,      # Slowest
        'fastflight': -5,   # Moderate  
        'dyneema': 0,       # Fast
        'vectran': 5,       # Fastest
    }
    string_adj = string_adjustments.get(string_material.lower(), -20)
    
    # Draw weight adjustment (2 fps per pound from 70 lb reference)
    weight_adj = (bow_draw_weight - 70) * 2
    
    # Draw length adjustment (10 fps per inch from 30" reference)
    length_adj = (bow_draw_length - 30) * 10
    
    # Arrow weight adjustment (roughly 0.5 fps per grain from 350 grain reference)
    arrow_weight_adj = (350 - arrow_weight_grains) * 0.5
    
    estimated_speed = bow_ibo_speed + weight_adj + length_adj + arrow_weight_adj + string_adj
    
    print(f"    IBO calculation: {bow_ibo_speed} + {weight_adj} + {length_adj} + {arrow_weight_adj} + {string_adj} = {estimated_speed}")
    
    return max(estimated_speed, 100)  # Minimum realistic speed


def find_276_fps_source():
    """Find what combination of parameters produces 276.1 fps"""
    
    db_path = get_database_path()
    print(f"🔍 Identifying source of 276.1 fps calculation using: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all setup_arrows and calculate speeds
        cursor.execute("""
            SELECT sa.id, sa.setup_id, sa.arrow_id, sa.arrow_length, sa.point_weight,
                   bs.name as setup_name, bs.draw_weight, bs.bow_type, bs.ibo_speed, bs.draw_length,
                   a.manufacturer, a.model_name,
                   ss.gpi_weight
            FROM setup_arrows sa
            JOIN bow_setups bs ON sa.setup_id = bs.id
            LEFT JOIN arrows a ON sa.arrow_id = a.id
            LEFT JOIN spine_specifications ss ON sa.arrow_id = ss.arrow_id
            ORDER BY sa.id
        """)
        
        setup_arrows = cursor.fetchall()
        
        print("🎯 Testing all setup_arrows to find 276.1 fps source:")
        print("-" * 120)
        print("ID | Setup Name            | Arrow                    | Speed   | Matches 276.1 | Details")
        print("-" * 120)
        
        target_speed = 276.1
        tolerance = 0.5
        
        for row in setup_arrows:
            # Calculate arrow weight
            gpi = row['gpi_weight'] if row['gpi_weight'] else 8.5
            arrow_weight = (gpi * row['arrow_length']) + row['point_weight'] + 25  # Total arrow weight
            
            # Get bow parameters
            ibo_speed = row['ibo_speed'] if row['ibo_speed'] else 320
            draw_weight = row['draw_weight'] if row['draw_weight'] else 60
            draw_length = row['draw_length'] if row['draw_length'] else 29
            bow_type = row['bow_type'] if row['bow_type'] else 'compound'
            
            print(f"\n{row['id']:2} | {row['setup_name']:20} | {row['manufacturer'] or 'Unknown'} {row['model_name'] or ''}")
            print(f"    Parameters: IBO={ibo_speed}, Draw={draw_weight}lbs, Length={draw_length}\", Weight={arrow_weight:.1f}gr")
            
            # Calculate using the enhanced function simulation
            calculated_speed = calculate_enhanced_arrow_speed_internal_simulation(
                bow_ibo_speed=ibo_speed,
                bow_draw_weight=draw_weight,
                bow_draw_length=draw_length,
                bow_type=bow_type,
                arrow_weight_grains=arrow_weight,
                string_material='dacron',
                setup_id=row['setup_id'],
                arrow_id=row['arrow_id']
            )
            
            matches_276 = abs(calculated_speed - target_speed) < tolerance
            status = "✅ MATCH!" if matches_276 else "⚪ Different"
            
            print(f"    Result: {calculated_speed:.1f} fps | {status}")
            
            if matches_276:
                print(f"    🎯 FOUND THE SOURCE OF 276.1 FPS!")
                print(f"       Setup Arrow ID: {row['id']}")
                print(f"       Setup: {row['setup_name']}")
                print(f"       Arrow: {row['manufacturer']} {row['model_name']}")
                print(f"       This explains why the frontend shows 276.1 fps")
                
                # Check if this setup has chronograph data that should override
                cursor.execute('''
                    SELECT measured_speed_fps
                    FROM chronograph_data 
                    WHERE setup_id = ? AND arrow_id = ? AND verified = 1
                    ORDER BY measurement_date DESC
                    LIMIT 1
                ''', (row['setup_id'], row['arrow_id']))
                
                chrono_check = cursor.fetchone()
                if chrono_check:
                    print(f"       ⚠️ BUT this setup HAS chronograph data: {chrono_check['measured_speed_fps']} fps")
                    print(f"       The frontend should show {chrono_check['measured_speed_fps']} fps, not {calculated_speed:.1f} fps")
                    print(f"       This indicates a potential API or authentication issue!")
                else:
                    print(f"       ✅ No chronograph data for this setup, so 276.1 fps calculation is correct")
        
        print(f"\n📋 Summary:")
        print("   If a setup with chronograph data is showing 276.1 fps, it indicates:")
        print("   1. API authentication might be failing")
        print("   2. Different setup_arrow_id being used than expected")
        print("   3. Chronograph data lookup might be failing in the actual API call")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = find_276_fps_source()
    exit(0 if success else 1)