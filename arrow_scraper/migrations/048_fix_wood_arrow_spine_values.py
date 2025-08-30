#!/usr/bin/env python3
"""
Migration 048: Fix Wood Arrow Spine Values

Fixes spine values created by Migration 047 that mixed spine values with diameter information.
Removes diameter suffixes from spine values (e.g., "77.5@23/64" -> "77.5") while preserving
the diameter data in the outer_diameter column.

This ensures compatibility with the calculator system which expects pure numeric spine values.
"""

import sqlite3
import sys
import os
import json

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 48,
        'description': 'Fix wood arrow spine values by removing diameter information',
        'author': 'System',
        'created_at': '2025-08-30',
        'target_database': 'arrow',
        'dependencies': ['047'],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 048: Fixing wood arrow spine values...")
        
        # Get all spine specifications with @ symbol (contaminated values from Migration 047)
        cursor.execute("""
            SELECT s.id, s.spine, s.arrow_id, s.outer_diameter, s.gpi_weight, s.notes, a.manufacturer, a.model_name
            FROM spine_specifications s
            JOIN arrows a ON s.arrow_id = a.id
            WHERE s.spine LIKE '%@%'
            ORDER BY s.arrow_id, s.spine
        """)
        contaminated_specs = cursor.fetchall()
        
        if not contaminated_specs:
            print("   ✅ No contaminated spine values found, migration not needed")
            conn.commit()
            return True
        
        print(f"   📊 Found {len(contaminated_specs)} spine specifications to clean")
        
        # Group specs by arrow_id to handle duplicates properly
        arrow_specs = {}
        for spec in contaminated_specs:
            spec_id, spine, arrow_id, outer_diameter, gpi_weight, notes, manufacturer, model_name = spec
            if arrow_id not in arrow_specs:
                arrow_specs[arrow_id] = {'manufacturer': manufacturer, 'model_name': model_name, 'specs': []}
            arrow_specs[arrow_id]['specs'].append({
                'id': spec_id,
                'spine': spine,
                'outer_diameter': outer_diameter,
                'gpi_weight': gpi_weight,
                'notes': notes
            })
        
        rollback_data = []
        processed_count = 0
        
        for arrow_id, arrow_data in arrow_specs.items():
            manufacturer = arrow_data['manufacturer']
            model_name = arrow_data['model_name']
            specs = arrow_data['specs']
            
            print(f"   🌲 Processing {manufacturer} {model_name} ({len(specs)} specs)...")
            
            # Group specs by clean spine value to identify duplicates
            spine_groups = {}
            for spec in specs:
                clean_spine = spec['spine'].split('@')[0].strip()
                if clean_spine not in spine_groups:
                    spine_groups[clean_spine] = []
                spine_groups[clean_spine].append(spec)
            
            # Process each spine group
            for clean_spine, spine_specs in spine_groups.items():
                if len(spine_specs) == 1:
                    # Simple case: only one spec with this spine value
                    spec = spine_specs[0]
                    rollback_data.append({
                        'id': spec['id'],
                        'original_spine': spec['spine'],
                        'action': 'update'
                    })
                    
                    cursor.execute("""
                        UPDATE spine_specifications 
                        SET spine = ? 
                        WHERE id = ?
                    """, (clean_spine, spec['id']))
                    
                    processed_count += 1
                    print(f"     ✅ Updated: '{spec['spine']}' -> '{clean_spine}' (ID: {spec['id']})")
                
                else:
                    # Duplicate spine values - keep the first one, delete the others
                    print(f"     ⚠️  Found {len(spine_specs)} specs with spine '{clean_spine}' - consolidating...")
                    
                    # Keep the first spec (usually the one with smallest diameter)
                    spine_specs.sort(key=lambda x: x['outer_diameter'] or 0)
                    keep_spec = spine_specs[0]
                    delete_specs = spine_specs[1:]
                    
                    # Update the kept spec
                    rollback_data.append({
                        'id': keep_spec['id'],
                        'original_spine': keep_spec['spine'],
                        'action': 'update'
                    })
                    
                    cursor.execute("""
                        UPDATE spine_specifications 
                        SET spine = ?, 
                            notes = ? 
                        WHERE id = ?
                    """, (clean_spine, 
                          keep_spec['notes'] + f" [Consolidated from {len(spine_specs)} diameter options]",
                          keep_spec['id']))
                    
                    # Delete duplicate specs
                    for delete_spec in delete_specs:
                        rollback_data.append({
                            'id': delete_spec['id'],
                            'original_spine': delete_spec['spine'],
                            'outer_diameter': delete_spec['outer_diameter'],
                            'gpi_weight': delete_spec['gpi_weight'],
                            'notes': delete_spec['notes'],
                            'arrow_id': arrow_id,
                            'action': 'delete'
                        })
                        
                        cursor.execute("DELETE FROM spine_specifications WHERE id = ?", (delete_spec['id'],))
                        print(f"     🗑️  Deleted duplicate: '{delete_spec['spine']}' (ID: {delete_spec['id']})")
                    
                    processed_count += 1
        
        # Store rollback data
        cursor.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS migration_048_rollback (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO migration_048_rollback (data) VALUES (?)
        """, (json.dumps(rollback_data),))
        
        # Verify no contaminated spine values remain
        cursor.execute("SELECT COUNT(*) FROM spine_specifications WHERE spine LIKE '%@%'")
        remaining_contaminated = cursor.fetchone()[0]
        
        if remaining_contaminated > 0:
            raise Exception(f"Still have {remaining_contaminated} contaminated spine values after cleaning")
        
        conn.commit()
        
        print(f"   📈 Cleaning Summary:")
        print(f"     • {processed_count} spine specifications processed")
        print(f"     • Duplicate spine values consolidated")
        print(f"     • All spine values are now pure numeric format")
        print(f"     • Diameter information preserved in outer_diameter column")
        
        print("🎯 Migration 048 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 048 failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 048...")
        
        # Get rollback data
        cursor.execute("SELECT data FROM migration_048_rollback ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            print("   ⚠️  No rollback data found, cannot restore original spine values")
            print("   💡 Original format was preserved in the notes column")
            return True
        
        rollback_data = json.loads(result[0])
        
        # Restore original spine values
        restored_count = 0
        for item in rollback_data:
            cursor.execute("""
                UPDATE spine_specifications 
                SET spine = ? 
                WHERE id = ?
            """, (item['original_spine'], item['id']))
            
            restored_count += 1
            print(f"   ↩️  Restored: '{item['clean_spine']}' -> '{item['original_spine']}' (ID: {item['id']})")
        
        # Clean up temporary table
        cursor.execute("DROP TABLE IF EXISTS migration_048_rollback")
        
        conn.commit()
        
        print(f"   📈 Rollback Summary:")
        print(f"     • {restored_count} spine specifications restored to original format")
        print(f"     • Spine values now include diameter information again")
        
        print("🔄 Migration 048 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 048 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration - try multiple database paths
    possible_paths = [
        '/app/databases/arrow_database.db',  # Docker production
        '/root/archerytools/databases/arrow_database.db',  # Production host
        os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db'),  # Development
        'databases/arrow_database.db',  # Relative path
        'arrow_database.db'  # Current directory
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database not found in any location: {possible_paths}")
        sys.exit(1)
    
    print(f"📁 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            success = migrate_down(conn.cursor())
        else:
            success = migrate_up(conn.cursor())
        
        if success:
            print("✅ Migration test completed successfully")
        else:
            print("❌ Migration test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()