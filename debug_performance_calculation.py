#!/usr/bin/env python3
"""
Debug the performance calculation showing 276.1 fps instead of expected chronograph data
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


def debug_performance_issue():
    """Debug the 276.1 fps vs 285.4 fps issue"""
    
    db_path = get_database_path()
    print(f"🔍 Debugging performance calculation using: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check all setup_arrows entries with performance data
        cursor.execute("""
            SELECT sa.id, sa.setup_id, sa.arrow_id, sa.arrow_length, sa.point_weight,
                   bs.name as setup_name, bs.draw_weight, bs.bow_type, bs.ibo_speed, bs.draw_length,
                   a.manufacturer, a.model_name, a.material,
                   cd.measured_speed_fps, cd.arrow_weight_grains as chrono_weight,
                   ss.gpi_weight
            FROM setup_arrows sa
            JOIN bow_setups bs ON sa.setup_id = bs.id
            LEFT JOIN arrows a ON sa.arrow_id = a.id
            LEFT JOIN chronograph_data cd ON sa.setup_id = cd.setup_id AND sa.arrow_id = cd.arrow_id AND cd.verified = 1
            LEFT JOIN spine_specifications ss ON sa.arrow_id = ss.arrow_id
            ORDER BY sa.id
        """)
        
        setup_arrows = cursor.fetchall()
        
        print("🎯 All Setup Arrows with Potential Chronograph Data:")
        print("-" * 150)
        print("ID | Setup Name            | Arrow                           | Length | Point | GPI  | Chrono Speed | Expected Speed | Status")
        print("-" * 150)
        
        performance_issues = []
        
        for row in setup_arrows:
            arrow_name = f"{row['manufacturer']} {row['model_name']}" if row['manufacturer'] else "Unknown Arrow"
            gpi = row['gpi_weight'] if row['gpi_weight'] else 8.5
            arrow_weight = (gpi * row['arrow_length']) + row['point_weight'] + 25  # Total arrow weight
            chrono_speed = row['measured_speed_fps'] if row['measured_speed_fps'] else 0
            
            # Calculate expected speed using IBO formula (simplified)
            ibo_speed = row['ibo_speed'] if row['ibo_speed'] else 320
            draw_weight = row['draw_weight'] if row['draw_weight'] else 60
            draw_length = row['draw_length'] if row['draw_length'] else 29
            
            # Simplified IBO calculation for comparison
            weight_adj = (draw_weight - 70) * 2
            length_adj = (draw_length - 30) * 10  
            arrow_weight_adj = (350 - arrow_weight) * 0.5
            calculated_speed = ibo_speed + weight_adj + length_adj + arrow_weight_adj
            
            if chrono_speed > 0:
                status = "✅ HAS_CHRONO"
                if abs(chrono_speed - 276.1) < 0.1:
                    status = "🎯 MATCHES_276.1"
                    performance_issues.append(row)
                elif abs(chrono_speed - 285.4) < 0.1:
                    status = "✅ TEST_DATA"
            else:
                status = "⚠️ NO_CHRONO"
            
            print(f"{row['id']:2} | {row['setup_name']:20} | {arrow_name[:30]:30} | {row['arrow_length']:6.1f} | {row['point_weight']:5.0f} | {gpi:4.1f} | {chrono_speed:12.1f} | {calculated_speed:14.1f} | {status}")
        
        # Check for any arrows that might calculate to 276.1 fps
        print(f"\n🔍 Searching for arrows that might calculate to 276.1 fps...")
        
        # Look for arrows with specific characteristics that might produce 276.1 fps
        target_speed = 276.1
        tolerance = 1.0
        
        found_matches = []
        for row in setup_arrows:
            if row['manufacturer']:  # Only check real arrows
                gpi = row['gpi_weight'] if row['gpi_weight'] else 8.5
                arrow_weight = (gpi * row['arrow_length']) + row['point_weight'] + 25
                
                # Try different bow configurations
                for test_ibo in [320, 330, 340]:
                    for test_weight in [50, 60, 70]:
                        for test_length in [28, 29, 30]:
                            weight_adj = (test_weight - 70) * 2
                            length_adj = (test_length - 30) * 10
                            arrow_weight_adj = (350 - arrow_weight) * 0.5
                            calc_speed = test_ibo + weight_adj + length_adj + arrow_weight_adj
                            
                            if abs(calc_speed - target_speed) < tolerance:
                                found_matches.append({
                                    'setup_arrow_id': row['id'],
                                    'arrow': f"{row['manufacturer']} {row['model_name']}",
                                    'ibo': test_ibo,
                                    'weight': test_weight,
                                    'length': test_length,
                                    'arrow_weight': arrow_weight,
                                    'calculated_speed': calc_speed
                                })
        
        if found_matches:
            print(f"\n📊 Found {len(found_matches)} combinations that produce ~276.1 fps:")
            print("-" * 120)
            print("Setup ID | Arrow                           | IBO | Draw Weight | Draw Length | Arrow Weight | Calculated Speed")
            print("-" * 120)
            for match in found_matches[:10]:  # Show first 10 matches
                print(f"{match['setup_arrow_id']:8} | {match['arrow'][:30]:30} | {match['ibo']:3} | {match['weight']:11.0f} | {match['length']:11.1f} | {match['arrow_weight']:12.1f} | {match['calculated_speed']:16.1f}")
        
        # Check if there are any chronograph entries that might be causing confusion
        cursor.execute("""
            SELECT cd.*, bs.name as setup_name, a.manufacturer, a.model_name
            FROM chronograph_data cd
            JOIN bow_setups bs ON cd.setup_id = bs.id
            LEFT JOIN arrows a ON cd.arrow_id = a.id
            WHERE cd.verified = 1
            ORDER BY ABS(cd.measured_speed_fps - 276.1) ASC
            LIMIT 5
        """)
        
        close_chronos = cursor.fetchall()
        
        if close_chronos:
            print(f"\n🎯 Chronograph entries closest to 276.1 fps:")
            print("-" * 100)
            print("Setup Name            | Arrow                           | Speed   | Difference")
            print("-" * 100)
            for chrono in close_chronos:
                arrow_name = f"{chrono['manufacturer']} {chrono['model_name']}" if chrono['manufacturer'] else "Unknown"
                diff = abs(chrono['measured_speed_fps'] - 276.1)
                print(f"{chrono['setup_name']:20} | {arrow_name[:30]:30} | {chrono['measured_speed_fps']:7.1f} | {diff:10.1f}")
        
        print(f"\n📋 Debug Summary:")
        print("-" * 50)
        print(f"✅ Total setup_arrows entries: {len(setup_arrows)}")
        print(f"✅ Entries with chronograph data: {len([r for r in setup_arrows if r['measured_speed_fps']])}")
        print(f"✅ Test data entries (285.4 fps): {len([r for r in setup_arrows if r['measured_speed_fps'] and abs(r['measured_speed_fps'] - 285.4) < 0.1])}")
        print(f"⚠️ Potential 276.1 fps matches: {len(found_matches)}")
        
        if performance_issues:
            print(f"\n⚠️ The 276.1 fps speed suggests the API is using calculated speeds instead of chronograph data.")
            print("   This could be due to:")
            print("   1. Authentication issues (API calls failing)")
            print("   2. Different setup_id/arrow_id than test data")
            print("   3. Frontend not using the correct API endpoint")
            print("   4. Chronograph data not being found for the specific arrow")
        else:
            print(f"\n✅ No obvious issues found. The 276.1 fps might be from a different arrow/setup combination.")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = debug_performance_issue()
    exit(0 if success else 1)