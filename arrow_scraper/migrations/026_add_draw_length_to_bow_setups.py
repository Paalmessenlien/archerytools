#!/usr/bin/env python3
"""
Migration 026: Add draw_length back to bow_setups table and set default IBO speeds

This migration addresses the chronograph data integration requirements:
1. Adds draw_length column to bow_setups (needed per setup, not per user)
2. Sets default IBO speeds based on bow type for performance calculations
3. Migrates any existing user draw_length values to their bow setups
"""

import sqlite3
from pathlib import Path


def get_database_path():
    """Get the path to the user database"""
    # Try multiple possible paths
    paths_to_try = [
        Path("/app/databases/user_data.db"),           # Docker path
        Path(__file__).parent.parent / "databases" / "user_data.db",  # Local databases folder
        Path(__file__).parent.parent / "user_data.db", # Legacy local path
    ]
    
    for path in paths_to_try:
        if path.exists():
            return str(path)
    
    # If none exist, create in the databases folder
    databases_dir = Path(__file__).parent.parent / "databases"
    databases_dir.mkdir(exist_ok=True)
    return str(databases_dir / "user_data.db")


def run_migration():
    """Run the migration to add draw_length to bow_setups and set default IBO speeds"""
    
    db_path = get_database_path()
    print(f"🔄 Running Migration 026 on database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Step 1: Check if draw_length column exists in bow_setups
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'draw_length' not in columns:
            print("🔄 Adding draw_length column to bow_setups table...")
            # For compound bows: "Draw length setting" (module setting)
            # For other bows: "Measured draw length" (physical measurement at draw weight)
            cursor.execute("ALTER TABLE bow_setups ADD COLUMN draw_length REAL DEFAULT 28.0")
            
            # Migrate user draw_length values to their bow setups
            print("🔄 Migrating user draw_length values to bow setups...")
            cursor.execute("""
                UPDATE bow_setups 
                SET draw_length = (
                    SELECT u.draw_length 
                    FROM users u 
                    WHERE u.id = bow_setups.user_id 
                    AND u.draw_length IS NOT NULL
                )
                WHERE EXISTS (
                    SELECT 1 FROM users u 
                    WHERE u.id = bow_setups.user_id 
                    AND u.draw_length IS NOT NULL
                )
            """)
            migrated_count = cursor.rowcount
            print(f"✅ Migrated draw_length for {migrated_count} bow setups")
        else:
            print("✅ draw_length column already exists in bow_setups")
        
        # Step 2: Set default IBO speeds based on bow type
        print("🔄 Setting default IBO speeds based on bow type...")
        
        # Default IBO speeds by bow type (conservative estimates)
        default_ibo_speeds = {
            'compound': 320,     # Modern compound bows average 300-340 fps
            'recurve': 180,      # Olympic recurve bows typically 170-190 fps  
            'traditional': 160,  # Traditional longbows/recurves 150-170 fps
            'barebow': 175,      # Barebow recurves typically 165-185 fps
            'longbow': 150,      # Traditional longbows 140-160 fps
        }
        
        for bow_type, default_ibo in default_ibo_speeds.items():
            cursor.execute("""
                UPDATE bow_setups 
                SET ibo_speed = ? 
                WHERE bow_type = ? AND (ibo_speed IS NULL OR ibo_speed = 0)
            """, (default_ibo, bow_type))
            
            updated_count = cursor.rowcount
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
        print("\n📊 Migration Results Summary:")
        print("-" * 60)
        for row in results:
            print(f"  {row['bow_type']:12} | {row['count']:3} setups | "
                  f"Draw: {row['avg_draw_length']:.1f}\" | IBO: {row['avg_ibo_speed']:.0f} fps")
        
        conn.commit()
        print("\n✅ Migration 026 completed successfully!")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration 026 failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


def rollback_migration():
    """Rollback migration 026 (remove draw_length from bow_setups)"""
    
    db_path = get_database_path()
    print(f"🔄 Rolling back Migration 026 on database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if draw_length column exists
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'draw_length' in columns:
            print("🔄 Removing draw_length column from bow_setups table...")
            
            # Create new table without draw_length
            cursor.execute("""
                CREATE TABLE bow_setups_temp AS 
                SELECT id, user_id, name, bow_type, draw_weight, insert_weight, description,
                       bow_usage, riser_brand, riser_model, riser_length, limb_brand, limb_model, 
                       limb_length, compound_brand, compound_model, ibo_speed, created_at
                FROM bow_setups
            """)
            
            cursor.execute("DROP TABLE bow_setups")
            cursor.execute("ALTER TABLE bow_setups_temp RENAME TO bow_setups")
            
            print("✅ Removed draw_length column from bow_setups")
        else:
            print("✅ draw_length column not found in bow_setups")
        
        conn.commit()
        print("✅ Migration 026 rollback completed!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration 026 rollback failed: {e}")
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