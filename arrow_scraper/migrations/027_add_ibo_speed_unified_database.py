#!/usr/bin/env python3
"""
Migration 027: Add IBO speed to bow_setups table in unified database

This migration addresses the chronograph data integration requirements:
1. Adds ibo_speed column to bow_setups table in the unified database
2. Sets default IBO speeds based on bow type for performance calculations
3. Updates draw_length field labels for UI (compound = "Draw length setting", others = "Measured draw length")
"""

import sqlite3
from pathlib import Path


def get_database_path():
    """Get the path to the unified database"""
    # Try Docker path first, then local databases folder
    paths_to_try = [
        Path("/app/databases/arrow_database.db"),           # Docker path
        Path(__file__).parent.parent / "databases" / "arrow_database.db",  # Local databases folder
        Path(__file__).parent.parent / "arrow_database.db", # Legacy local path
    ]
    
    for path in paths_to_try:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError("Could not find unified database (arrow_database.db)")


def run_migration():
    """Run the migration to add ibo_speed to bow_setups in unified database"""
    
    db_path = get_database_path()
    print(f"🔄 Running Migration 027 on unified database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Step 1: Check if ibo_speed column exists in bow_setups
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ibo_speed' not in columns:
            print("🔄 Adding ibo_speed column to bow_setups table...")
            cursor.execute("ALTER TABLE bow_setups ADD COLUMN ibo_speed REAL")
            print("✅ Added ibo_speed column to bow_setups table")
        else:
            print("✅ ibo_speed column already exists in bow_setups")
        
        # Step 2: Set default IBO speeds based on bow type
        print("🔄 Setting default IBO speeds based on bow type...")
        
        # Default IBO speeds by bow type (conservative estimates for chronograph integration)
        default_ibo_speeds = {
            'compound': 320,     # Modern compound bows average 300-340 fps
            'recurve': 180,      # Olympic recurve bows typically 170-190 fps  
            'traditional': 160,  # Traditional longbows/recurves 150-170 fps
            'barebow': 175,      # Barebow recurves typically 165-185 fps
            'longbow': 150,      # Traditional longbows 140-160 fps
        }
        
        updated_total = 0
        for bow_type, default_ibo in default_ibo_speeds.items():
            cursor.execute("""
                UPDATE bow_setups 
                SET ibo_speed = ? 
                WHERE bow_type = ? AND (ibo_speed IS NULL OR ibo_speed = 0)
            """, (default_ibo, bow_type))
            
            updated_count = cursor.rowcount
            updated_total += updated_count
            if updated_count > 0:
                print(f"✅ Set default IBO speed {default_ibo} fps for {updated_count} {bow_type} setups")
        
        # Step 3: Update any bow setups with generic bow types
        cursor.execute("""
            UPDATE bow_setups 
            SET ibo_speed = 280 
            WHERE (ibo_speed IS NULL OR ibo_speed = 0) 
            AND bow_type NOT IN ('compound', 'recurve', 'traditional', 'barebow', 'longbow')
        """)
        generic_count = cursor.rowcount
        updated_total += generic_count
        if generic_count > 0:
            print(f"✅ Set default IBO speed 280 fps for {generic_count} other bow types")
        
        # Step 4: Verify migration results
        cursor.execute("""
            SELECT bow_type, COUNT(*) as count, 
                   AVG(draw_length) as avg_draw_length,
                   AVG(ibo_speed) as avg_ibo_speed
            FROM bow_setups 
            GROUP BY bow_type
        """)
        
        results = cursor.fetchall()
        if results:
            print("\n📊 Migration Results Summary:")
            print("-" * 70)
            print("  Bow Type     | Count | Avg Draw Length | Avg IBO Speed")
            print("-" * 70)
            for row in results:
                bow_type = row['bow_type'] or 'Unknown'
                count = row['count']
                avg_draw = row['avg_draw_length'] or 0
                avg_ibo = row['avg_ibo_speed'] or 0
                print(f"  {bow_type:12} | {count:5} | {avg_draw:13.1f}\" | {avg_ibo:11.0f} fps")
        else:
            print("✅ No existing bow setups found - migration ready for new setups")
        
        conn.commit()
        print(f"\n✅ Migration 027 completed successfully! Updated {updated_total} bow setups with IBO speeds.")
        
        # Step 5: Display usage guidance
        print("\n📋 Usage Notes:")
        print("  • Compound bows: draw_length = 'Draw length setting' (cam/module setting)")
        print("  • Other bows: draw_length = 'Measured draw length' (physical measurement at rated draw weight)")
        print("  • IBO speeds are defaults - users can override with actual chronograph measurements")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration 027 failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


def rollback_migration():
    """Rollback migration 027 (remove ibo_speed from bow_setups)"""
    
    db_path = get_database_path()
    print(f"🔄 Rolling back Migration 027 on unified database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if ibo_speed column exists
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ibo_speed' in columns:
            print("🔄 Removing ibo_speed column from bow_setups table...")
            
            # Create new table without ibo_speed
            cursor.execute("""
                CREATE TABLE bow_setups_temp AS 
                SELECT id, user_id, name, bow_type, draw_weight, draw_length, arrow_length, 
                       point_weight, nock_weight, fletching_weight, insert_weight, created_at
                FROM bow_setups
            """)
            
            cursor.execute("DROP TABLE bow_setups")
            cursor.execute("ALTER TABLE bow_setups_temp RENAME TO bow_setups")
            
            print("✅ Removed ibo_speed column from bow_setups")
        else:
            print("✅ ibo_speed column not found in bow_setups")
        
        conn.commit()
        print("✅ Migration 027 rollback completed!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration 027 rollback failed: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        success = rollback_migration()
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1)