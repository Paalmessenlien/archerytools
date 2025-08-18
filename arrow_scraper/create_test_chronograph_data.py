#!/usr/bin/env python3
"""
Create test chronograph data to verify integration with performance calculations

This script creates:
1. Test bow setups with different bow types and IBO speeds
2. Test chronograph data entries linked to the bow setups
3. Verifies that performance calculations can use chronograph data
"""

import sqlite3
import json
from datetime import datetime
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


def create_test_data():
    """Create test bow setups and chronograph data"""
    
    db_path = get_database_path()
    print(f"🎯 Creating test chronograph data in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if chronograph_data table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chronograph_data'")
        if not cursor.fetchone():
            print("⚠️ chronograph_data table doesn't exist. Creating it...")
            
            # Create chronograph_data table (from migration 019)
            cursor.execute("""
                CREATE TABLE chronograph_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER,
                    setup_arrow_id INTEGER,
                    measured_speed_fps REAL NOT NULL,
                    arrow_weight_grains REAL NOT NULL,
                    shot_count INTEGER DEFAULT 3,
                    std_deviation REAL,
                    min_speed_fps REAL,
                    max_speed_fps REAL,
                    temperature_f INTEGER DEFAULT 70,
                    humidity_percent INTEGER DEFAULT 50,
                    chronograph_model TEXT,
                    notes TEXT,
                    verified BOOLEAN DEFAULT 1,
                    measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created chronograph_data table")
        
        # Step 1: Create test bow setups
        test_setups = [
            {
                'name': 'Test Compound Bow',
                'bow_type': 'compound',
                'draw_weight': 60.0,
                'draw_length': 29.0,
                'ibo_speed': 330,
                'user_id': 1
            },
            {
                'name': 'Test Recurve Bow',
                'bow_type': 'recurve',
                'draw_weight': 45.0,
                'draw_length': 28.5,
                'ibo_speed': 180,
                'user_id': 1
            },
            {
                'name': 'Test Traditional Bow',
                'bow_type': 'traditional',
                'draw_weight': 55.0,
                'draw_length': 27.5,
                'ibo_speed': 160,
                'user_id': 1
            }
        ]
        
        created_setups = []
        for setup in test_setups:
            # Check if setup already exists
            cursor.execute("SELECT id FROM bow_setups WHERE name = ?", (setup['name'],))
            existing = cursor.fetchone()
            
            if existing:
                setup_id = existing[0]
                print(f"✅ Using existing setup: {setup['name']} (ID: {setup_id})")
            else:
                cursor.execute("""
                    INSERT INTO bow_setups (user_id, name, bow_type, draw_weight, draw_length, 
                                          arrow_length, point_weight, ibo_speed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (setup['user_id'], setup['name'], setup['bow_type'], setup['draw_weight'], 
                      setup['draw_length'], 32.0, 125.0, setup['ibo_speed']))  # Default arrow specs
                
                setup_id = cursor.lastrowid
                print(f"✅ Created bow setup: {setup['name']} (ID: {setup_id})")
            
            created_setups.append({**setup, 'id': setup_id})
        
        # Step 2: Get test arrows to link chronograph data to
        cursor.execute("SELECT id, manufacturer, model_name FROM arrows LIMIT 3")
        test_arrows = cursor.fetchall()
        
        if not test_arrows:
            print("⚠️ No arrows found in database. Chronograph data will be created without arrow links.")
            test_arrows = [{'id': None, 'manufacturer': 'Test', 'model_name': 'Arrow'}]
        
        # Step 3: Create test chronograph data
        chronograph_entries = [
            {
                'setup_id': created_setups[0]['id'],  # Compound bow
                'arrow_id': test_arrows[0]['id'] if test_arrows[0]['id'] else None,
                'measured_speed_fps': 285.4,
                'arrow_weight_grains': 345,
                'shot_count': 5,
                'std_deviation': 3.2,
                'min_speed_fps': 281.8,
                'max_speed_fps': 289.1,
                'temperature_f': 72,
                'humidity_percent': 45,
                'chronograph_model': 'Caldwell Ballistic Precision',
                'notes': 'Test data for compound bow - 345gr arrow',
                'verified': 1
            },
            {
                'setup_id': created_setups[1]['id'],  # Recurve bow
                'arrow_id': test_arrows[1]['id'] if len(test_arrows) > 1 and test_arrows[1]['id'] else None,
                'measured_speed_fps': 165.8,
                'arrow_weight_grains': 420,
                'shot_count': 3,
                'std_deviation': 2.1,
                'min_speed_fps': 163.2,
                'max_speed_fps': 168.3,
                'temperature_f': 68,
                'humidity_percent': 52,
                'chronograph_model': 'Pro Chrono Digital',
                'notes': 'Test data for recurve bow - 420gr arrow',
                'verified': 1
            },
            {
                'setup_id': created_setups[2]['id'],  # Traditional bow
                'arrow_id': test_arrows[2]['id'] if len(test_arrows) > 2 and test_arrows[2]['id'] else None,
                'measured_speed_fps': 152.6,
                'arrow_weight_grains': 460,
                'shot_count': 3,
                'std_deviation': 4.1,
                'min_speed_fps': 148.9,
                'max_speed_fps': 156.2,
                'temperature_f': 75,
                'humidity_percent': 38,
                'chronograph_model': 'Shooting Chrony Beta Master',
                'notes': 'Test data for traditional bow - 460gr arrow',
                'verified': 1
            }
        ]
        
        created_chrono_data = []
        for entry in chronograph_entries:
            # Check if chronograph data already exists for this setup
            cursor.execute("SELECT id FROM chronograph_data WHERE setup_id = ? AND arrow_weight_grains = ?", 
                          (entry['setup_id'], entry['arrow_weight_grains']))
            existing = cursor.fetchone()
            
            if existing:
                chrono_id = existing[0]
                print(f"✅ Using existing chronograph data: Setup {entry['setup_id']}, {entry['arrow_weight_grains']}gr (ID: {chrono_id})")
            else:
                cursor.execute("""
                    INSERT INTO chronograph_data 
                    (setup_id, arrow_id, measured_speed_fps, arrow_weight_grains, shot_count, 
                     std_deviation, min_speed_fps, max_speed_fps, temperature_f, humidity_percent,
                     chronograph_model, notes, verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (entry['setup_id'], entry['arrow_id'], entry['measured_speed_fps'], 
                      entry['arrow_weight_grains'], entry['shot_count'], entry['std_deviation'],
                      entry['min_speed_fps'], entry['max_speed_fps'], entry['temperature_f'],
                      entry['humidity_percent'], entry['chronograph_model'], entry['notes'], 
                      entry['verified']))
                
                chrono_id = cursor.lastrowid
                print(f"✅ Created chronograph data: Setup {entry['setup_id']}, {entry['arrow_weight_grains']}gr @ {entry['measured_speed_fps']} fps (ID: {chrono_id})")
            
            created_chrono_data.append({**entry, 'id': chrono_id})
        
        # Step 4: Create summary
        cursor.execute("""
            SELECT bs.name, bs.bow_type, bs.draw_weight, bs.draw_length, bs.ibo_speed,
                   cd.measured_speed_fps, cd.arrow_weight_grains, cd.shot_count, cd.chronograph_model
            FROM bow_setups bs
            LEFT JOIN chronograph_data cd ON bs.id = cd.setup_id
            WHERE bs.id IN (?, ?, ?)
        """, (created_setups[0]['id'], created_setups[1]['id'], created_setups[2]['id']))
        
        results = cursor.fetchall()
        
        print("\n📊 Test Data Summary:")
        print("-" * 100)
        print("Setup Name               | Bow Type    | Draw Weight | Draw Length | IBO Speed | Measured Speed | Arrow Weight")
        print("-" * 100)
        
        for row in results:
            name = row[0] or 'Unknown'
            bow_type = row[1] or 'Unknown'
            draw_weight = row[2] or 0
            draw_length = row[3] or 0
            ibo_speed = row[4] or 0
            measured_speed = row[5] or 'No data'
            arrow_weight = row[6] or 'No data'
            
            measured_str = f"{measured_speed} fps" if measured_speed != 'No data' else 'No data'
            weight_str = f"{arrow_weight}gr" if arrow_weight != 'No data' else 'No data'
            
            print(f"{name:24} | {bow_type:11} | {draw_weight:11.1f} | {draw_length:11.1f} | {ibo_speed:9.0f} | {measured_str:14} | {weight_str}")
        
        conn.commit()
        print(f"\n✅ Test chronograph data creation completed!")
        print(f"   Created {len(created_setups)} bow setups and {len(created_chrono_data)} chronograph entries")
        
        # Step 5: Test the enhanced arrow speed calculation
        print("\n🧪 Testing enhanced arrow speed calculation...")
        try:
            # Import the calculation function
            import sys
            sys.path.append(str(Path(__file__).parent))
            from api import calculate_enhanced_arrow_speed_internal
            
            for setup in created_setups:
                test_speed = calculate_enhanced_arrow_speed_internal(
                    bow_ibo_speed=setup['ibo_speed'],
                    bow_draw_weight=setup['draw_weight'],
                    bow_draw_length=setup['draw_length'],
                    bow_type=setup['bow_type'],
                    arrow_weight_grains=350,  # Standard test weight
                    setup_id=setup['id'],
                    arrow_id=test_arrows[0]['id'] if test_arrows[0]['id'] else None
                )
                print(f"  {setup['name']:24} | Calculated speed: {test_speed:.1f} fps")
        
        except Exception as e:
            print(f"⚠️ Could not test calculation function: {e}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Failed to create test data: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


def cleanup_test_data():
    """Remove test chronograph data"""
    
    db_path = get_database_path()
    print(f"🧹 Cleaning up test chronograph data in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Remove test chronograph data
        cursor.execute("DELETE FROM chronograph_data WHERE notes LIKE 'Test data for%'")
        chrono_deleted = cursor.rowcount
        
        # Remove test bow setups
        cursor.execute("DELETE FROM bow_setups WHERE name LIKE 'Test%Bow'")
        setups_deleted = cursor.rowcount
        
        conn.commit()
        print(f"✅ Cleanup completed: Removed {chrono_deleted} chronograph entries and {setups_deleted} bow setups")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Cleanup failed: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        success = cleanup_test_data()
    else:
        success = create_test_data()
    
    sys.exit(0 if success else 1)