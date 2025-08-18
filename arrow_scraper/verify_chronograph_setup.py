#!/usr/bin/env python3
"""
Verify the chronograph setup and create setup_arrows if needed
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


def verify_chronograph_setup():
    """Verify chronograph setup and create setup_arrows if needed"""
    
    db_path = get_database_path()
    print(f"🔍 Verifying chronograph setup in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check current setup_arrows
        cursor.execute("""
            SELECT sa.id, sa.setup_id, sa.arrow_id, sa.arrow_length, sa.point_weight,
                   bs.name as setup_name, a.manufacturer, a.model_name
            FROM setup_arrows sa
            JOIN bow_setups bs ON sa.setup_id = bs.id
            LEFT JOIN arrows a ON sa.arrow_id = a.id
            WHERE sa.setup_id IN (1, 2, 3)
        """)
        
        setup_arrows = cursor.fetchall()
        
        print(f"📊 Current setup_arrows entries for test setups:")
        print("-" * 100)
        print("Setup ID | Arrow ID | Setup Name            | Arrow                           | Length | Point Weight")
        print("-" * 100)
        
        for row in setup_arrows:
            arrow_name = f"{row['manufacturer']} {row['model_name']}" if row['manufacturer'] else "No arrow"
            print(f"{row['setup_id']:8} | {row['arrow_id']:8} | {row['setup_name']:20} | {arrow_name:30} | {row['arrow_length']:6.1f} | {row['point_weight']:12.1f}")
        
        # Check chronograph data again
        cursor.execute("""
            SELECT cd.id, cd.setup_id, cd.arrow_id, cd.measured_speed_fps, cd.arrow_weight_grains,
                   bs.name as setup_name
            FROM chronograph_data cd
            JOIN bow_setups bs ON cd.setup_id = bs.id
            WHERE cd.verified = 1
        """)
        
        chrono_data = cursor.fetchall()
        
        print(f"\n🎯 Chronograph data entries:")
        print("-" * 80)
        print("Setup ID | Arrow ID | Setup Name            | Speed   | Weight")
        print("-" * 80)
        
        for row in chrono_data:
            print(f"{row['setup_id']:8} | {row['arrow_id']:8} | {row['setup_name']:20} | {row['measured_speed_fps']:7.1f} | {row['arrow_weight_grains']:6.0f}")
        
        # Check for missing setup_arrows entries
        missing_entries = []
        for chrono in chrono_data:
            setup_id = chrono['setup_id']
            arrow_id = chrono['arrow_id']
            
            # Check if setup_arrow exists for this combination
            cursor.execute("SELECT id FROM setup_arrows WHERE setup_id = ? AND arrow_id = ?", (setup_id, arrow_id))
            if not cursor.fetchone():
                missing_entries.append((setup_id, arrow_id))
        
        if missing_entries:
            print(f"\n⚠️ Missing setup_arrows entries for chronograph data:")
            for setup_id, arrow_id in missing_entries:
                cursor.execute("SELECT name FROM bow_setups WHERE id = ?", (setup_id,))
                setup_name = cursor.fetchone()['name']
                
                print(f"  Setup {setup_id} ({setup_name}) + Arrow {arrow_id}")
                
                # Create missing setup_arrows entry
                cursor.execute("""
                    INSERT INTO setup_arrows (setup_id, arrow_id, arrow_length, point_weight)
                    VALUES (?, ?, 32.0, 125.0)
                """, (setup_id, arrow_id))
                
                print(f"    ✅ Created setup_arrows entry")
            
            conn.commit()
            print(f"\n✅ Created {len(missing_entries)} missing setup_arrows entries")
        else:
            print(f"\n✅ All chronograph data has corresponding setup_arrows entries")
        
        # Final verification - test the linkage
        cursor.execute("""
            SELECT cd.setup_id, cd.arrow_id, cd.measured_speed_fps, sa.id as setup_arrow_id
            FROM chronograph_data cd
            JOIN setup_arrows sa ON cd.setup_id = sa.setup_id AND cd.arrow_id = sa.arrow_id
            WHERE cd.verified = 1
        """)
        
        linked_data = cursor.fetchall()
        
        print(f"\n🔗 Verified chronograph-to-setup_arrows linkage:")
        print("-" * 60)
        print("Setup ID | Arrow ID | Speed   | Setup_Arrow ID")
        print("-" * 60)
        
        for row in linked_data:
            print(f"{row['setup_id']:8} | {row['arrow_id']:8} | {row['measured_speed_fps']:7.1f} | {row['setup_arrow_id']:14}")
        
        print(f"\n✅ Chronograph setup verification completed!")
        print(f"   Found {len(linked_data)} properly linked chronograph entries")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Verification failed: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = verify_chronograph_setup()
    exit(0 if success else 1)