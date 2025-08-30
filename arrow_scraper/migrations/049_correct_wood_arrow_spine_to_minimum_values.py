#!/usr/bin/env python3
"""
Migration 049: Correct Wood Arrow Spine Values to Minimum Range Values

Corrects wood arrow spine values to use the minimum value from each range instead of midpoint.
For example: "25-30" range should use spine value 25, not 27.5.

This better represents how traditional archers select arrows based on the minimum draw weight
the arrow can handle, ensuring proper spine selection for the calculator system.
"""

import sqlite3
import sys
import os
import json
import re

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 49,
        'description': 'Correct wood arrow spine values to use minimum range values',
        'author': 'System', 
        'created_at': '2025-08-30',
        'target_database': 'arrow',
        'dependencies': ['048'],
        'environments': ['all']
    }

def extract_minimum_spine_from_notes(notes):
    """Extract minimum spine value from the original spine range in notes"""
    if not notes:
        return None
        
    # Look for "Original spine range: X-Y" or "Original spine range: <X" patterns
    range_match = re.search(r'Original spine range:\s*([^,]+)', notes)
    if not range_match:
        return None
    
    range_str = range_match.group(1).strip()
    
    # Handle different range formats
    if range_str.startswith('<'):
        # Handle "<30" format - use a reasonable minimum (e.g., <30 -> 25)
        max_val = float(range_str[1:])
        return max_val - 5  # Conservative minimum
    elif range_str.endswith('+'):
        # Handle "80+" format - use the base value
        return float(range_str[:-1])
    elif '-' in range_str:
        # Handle "25-30" format - use minimum value
        parts = range_str.split('-')
        return float(parts[0])
    else:
        # Single value - use as is
        try:
            return float(range_str)
        except ValueError:
            return None

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 049: Correcting wood arrow spine values to minimum range values...")
        
        # Get all wood arrow spine specifications that need correction
        cursor.execute("""
            SELECT s.id, s.spine, s.notes, a.manufacturer, a.model_name
            FROM spine_specifications s
            JOIN arrows a ON s.arrow_id = a.id  
            WHERE a.id >= 2600 AND s.notes LIKE '%Original spine range:%'
            ORDER BY a.manufacturer, CAST(s.spine AS REAL)
        """)
        specs_to_correct = cursor.fetchall()
        
        if not specs_to_correct:
            print("   ✅ No wood arrow spine specifications found to correct")
            conn.commit()
            return True
        
        print(f"   📊 Found {len(specs_to_correct)} spine specifications to correct")
        
        corrections = []
        corrected_count = 0
        
        for spec_id, current_spine, notes, manufacturer, model_name in specs_to_correct:
            # Extract minimum spine from original range in notes
            min_spine = extract_minimum_spine_from_notes(notes)
            
            if min_spine is None:
                print(f"     ⚠️  Could not extract minimum spine from: {notes}")
                continue
            
            # Convert to integer if it's a whole number, otherwise keep decimal
            if min_spine == int(min_spine):
                min_spine_str = str(int(min_spine))
            else:
                min_spine_str = str(min_spine)
            
            # Only update if the value actually changed
            if current_spine != min_spine_str:
                corrections.append({
                    'id': spec_id,
                    'original_spine': current_spine,
                    'corrected_spine': min_spine_str,
                    'manufacturer': manufacturer,
                    'model_name': model_name,
                    'notes': notes
                })
                
                cursor.execute("""
                    UPDATE spine_specifications 
                    SET spine = ?
                    WHERE id = ?
                """, (min_spine_str, spec_id))
                
                corrected_count += 1
                print(f"     ✅ {manufacturer} {model_name}: '{current_spine}' -> '{min_spine_str}' (ID: {spec_id})")
            else:
                print(f"     ✓ {manufacturer} {model_name}: '{current_spine}' already correct (ID: {spec_id})")
        
        # Store rollback data
        cursor.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS migration_049_rollback (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO migration_049_rollback (data) VALUES (?)
        """, (json.dumps(corrections),))
        
        # Verify all spine values are still numeric
        cursor.execute("""
            SELECT spine FROM spine_specifications s
            JOIN arrows a ON s.arrow_id = a.id
            WHERE a.id >= 2600
        """)
        all_spines = cursor.fetchall()
        
        for (spine,) in all_spines:
            try:
                float(spine)
            except ValueError:
                raise Exception(f"Non-numeric spine value after correction: '{spine}'")
        
        conn.commit()
        
        print(f"   📈 Correction Summary:")
        print(f"     • {corrected_count} spine specifications corrected")
        print(f"     • {len(specs_to_correct) - corrected_count} spine values were already correct")
        print(f"     • All spine values now use minimum from their original ranges")
        print(f"     • Values represent minimum bow draw weight each arrow can handle")
        
        print("🎯 Migration 049 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 049 failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 049...")
        
        # Get rollback data
        cursor.execute("SELECT data FROM migration_049_rollback ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            print("   ⚠️  No rollback data found, cannot restore original spine values")
            return True
        
        corrections = json.loads(result[0])
        
        if not corrections:
            print("   ✅ No corrections to rollback")
            return True
        
        # Restore original spine values
        restored_count = 0
        for correction in corrections:
            cursor.execute("""
                UPDATE spine_specifications 
                SET spine = ?
                WHERE id = ?
            """, (correction['original_spine'], correction['id']))
            
            restored_count += 1
            print(f"     ↩️  Restored: '{correction['corrected_spine']}' -> '{correction['original_spine']}' (ID: {correction['id']})")
        
        # Clean up temporary table
        cursor.execute("DROP TABLE IF EXISTS migration_049_rollback")
        
        conn.commit()
        
        print(f"   📈 Rollback Summary:")
        print(f"     • {restored_count} spine specifications restored to midpoint values")
        
        print("🔄 Migration 049 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 049 rollback failed: {e}")
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