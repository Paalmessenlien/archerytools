#!/usr/bin/env python3
"""
Migration 022: Add Performance Data Column to Setup Arrows
Adds dedicated performance_data column and cleans up notes field from debug JSON

This migration adds a proper performance_data JSON column to the setup_arrows table
and migrates existing performance data from the notes field where it was temporarily stored.

Date: 2025-08-15
Author: Claude Code Enhancement  
Issue: Raw performance JSON showing in user interface via notes field
Solution: Add dedicated performance_data column and clean up notes display

Database Changes:
- Add performance_data TEXT column to setup_arrows table
- Migrate existing performance JSON from notes to performance_data column
- Clean up notes field to only contain user-friendly information
"""

import sqlite3
import json
import re
from database_migration_manager import BaseMigration

class Migration022AddPerformanceDataColumn(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "022"
        self.description = "Add Performance Data Column - Clean up UI debug information"
        self.dependencies = ["020"]  # Depends on equipment learning tables (user database)
        self.environments = ['all']  # Apply to all environments
        self.target_database = 'user'  # User database contains setup_arrows table
    
    def up(self, db_path: str, environment: str) -> bool:
        """
        Add performance_data column and migrate existing performance JSON from notes
        """
        try:
            print("🧹 Adding performance_data column and cleaning up notes display...")
            
            # Get user database connection
            user_db_path = self._get_user_database_path(db_path)
            if not user_db_path:
                print("❌ Could not find user database")
                return False
            
            conn = sqlite3.connect(user_db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # 1. Add performance_data column to setup_arrows table
            print("📊 Adding performance_data column to setup_arrows table...")
            try:
                cursor.execute('''
                    ALTER TABLE setup_arrows 
                    ADD COLUMN performance_data TEXT DEFAULT NULL
                ''')
                print("✅ performance_data column added successfully")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("✅ performance_data column already exists")
                else:
                    raise e
            
            # 2. Migrate existing performance data from notes to performance_data column
            print("🔄 Migrating performance data from notes field...")
            
            cursor.execute("SELECT id, notes FROM setup_arrows WHERE notes IS NOT NULL")
            arrows_with_notes = cursor.fetchall()
            
            migrated_count = 0
            cleaned_count = 0
            
            for arrow in arrows_with_notes:
                arrow_id = arrow['id']
                notes = arrow['notes'] or ''
                
                # Check if notes contains performance JSON
                if 'Performance: {' in notes:
                    try:
                        # Extract performance JSON
                        performance_json = self._extract_performance_json(notes)
                        
                        if performance_json:
                            # Clean up notes to remove performance JSON
                            clean_notes = self._clean_notes_field(notes)
                            
                            # Update record with separate performance data and cleaned notes
                            cursor.execute('''
                                UPDATE setup_arrows 
                                SET performance_data = ?, 
                                    notes = ?
                                WHERE id = ?
                            ''', (performance_json, clean_notes, arrow_id))
                            
                            migrated_count += 1
                        
                    except Exception as e:
                        print(f"⚠️  Warning: Could not migrate performance data for arrow {arrow_id}: {e}")
                        # Clean up notes anyway to remove broken JSON
                        clean_notes = self._clean_notes_field(notes)
                        cursor.execute('UPDATE setup_arrows SET notes = ? WHERE id = ?', (clean_notes, arrow_id))
                        cleaned_count += 1
            
            conn.commit()
            
            # 3. Verify migration success
            cursor.execute("SELECT COUNT(*) as count FROM setup_arrows WHERE performance_data IS NOT NULL")
            performance_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM setup_arrows WHERE notes LIKE '%Performance: {%'")
            remaining_json_count = cursor.fetchone()['count']
            
            conn.close()
            
            print(f"✅ Migration completed successfully:")
            print(f"   📈 Performance data migrated: {migrated_count} arrows")
            print(f"   🧹 Notes cleaned up: {cleaned_count} arrows")  
            print(f"   📊 Total arrows with performance data: {performance_count}")
            print(f"   🚫 Remaining JSON in notes: {remaining_json_count} (should be 0)")
            
            if remaining_json_count > 0:
                print("⚠️  Warning: Some performance JSON may still be in notes field")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration 022 failed: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """
        Rollback migration - remove performance_data column and restore notes
        """
        try:
            print("⏪ Rolling back performance data column migration...")
            
            user_db_path = self._get_user_database_path(db_path)
            if not user_db_path:
                print("❌ Could not find user database")
                return False
            
            conn = sqlite3.connect(user_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # SQLite doesn't support DROP COLUMN, so we need to recreate the table
            print("🔄 Recreating setup_arrows table without performance_data column...")
            
            # Get existing data
            cursor.execute("SELECT * FROM setup_arrows")
            existing_data = cursor.fetchall()
            
            # Create new table without performance_data column
            cursor.execute('''
                CREATE TABLE setup_arrows_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER NOT NULL,
                    arrow_length REAL NOT NULL,
                    point_weight REAL NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
                )
            ''')
            
            # Restore data (combining performance_data back into notes if needed)
            for row in existing_data:
                # Restore original notes format if performance_data exists
                original_notes = row['notes'] or ''
                performance_data = row.get('performance_data')
                
                if performance_data:
                    # Restore performance JSON to notes (original format)
                    if original_notes:
                        restored_notes = f"{original_notes} | Performance: {performance_data}"
                    else:
                        restored_notes = f"Performance: {performance_data}"
                else:
                    restored_notes = original_notes
                
                cursor.execute('''
                    INSERT INTO setup_arrows_new 
                    (id, setup_id, arrow_id, arrow_length, point_weight, notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['id'], row['setup_id'], row['arrow_id'], 
                    row['arrow_length'], row['point_weight'], restored_notes,
                    row['created_at'], row['updated_at']
                ))
            
            # Replace table atomically
            cursor.execute("DROP TABLE setup_arrows")
            cursor.execute("ALTER TABLE setup_arrows_new RENAME TO setup_arrows")
            
            conn.commit()
            conn.close()
            
            print("✅ Migration 022 rolled back successfully")
            print("⚠️  Performance JSON is now back in notes field (visible to users)")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration 022 rollback failed: {e}")
            return False
    
    def _get_user_database_path(self, arrow_db_path: str) -> str:
        """Find user database path from arrow database path"""
        try:
            from user_database import UserDatabase
            user_db = UserDatabase()
            return user_db.db_path
        except Exception as e:
            print(f"⚠️ Error finding user database: {e}")
            # Fallback path resolution
            if '/app/databases/' in arrow_db_path:
                return arrow_db_path.replace('arrow_database.db', 'user_data.db')
            else:
                import os
                return os.path.join(os.path.dirname(arrow_db_path), 'user_data.db')
    
    def _extract_performance_json(self, notes: str) -> str:
        """Extract performance JSON from notes field"""
        try:
            if 'Performance: {' not in notes:
                return None
            
            # Find start of JSON
            json_start = notes.find('Performance: {') + len('Performance: ')
            json_str = notes[json_start:]
            
            # Handle cases where there might be additional text after JSON
            if ' | Performance:' in json_str:
                json_str = json_str[:json_str.find(' | Performance:')]
            
            # Validate JSON
            json.loads(json_str)  # This will raise exception if invalid
            return json_str
            
        except Exception:
            return None
    
    def _clean_notes_field(self, notes: str) -> str:
        """Clean notes field by removing performance JSON debug information"""
        if not notes:
            return ''
        
        # First, handle the specific case where JSON starts after a comma
        # Pattern: "Added from calculator - 94% match, "detailed_foc": {...}
        if '"detailed_foc":' in notes:
            # Find where the JSON starts (after the match percentage)
            match_end = notes.find('% match')
            if match_end != -1:
                # Extract just the user-friendly part
                clean_notes = notes[:match_end + len('% match')]
                return clean_notes.strip()
        
        # Handle standard Performance JSON patterns
        patterns_to_remove = [
            r',\s*"detailed_foc":.*$',              # , "detailed_foc": {...} to end
            r'\s*\|\s*Performance:\s*\{.*?\}\s*',   # | Performance: {...}
            r'^Performance:\s*\{.*?\}\s*',          # Performance: {...} at start
            r'\s*Performance:\s*\{.*?\}$',          # Performance: {...} at end
            r'\s*Performance:\s*\{.*?\}\s*\|',      # Performance: {...} |
            r',\s*\{.*?\}\s*$',                     # , {...} at end
        ]
        
        clean_notes = notes
        for pattern in patterns_to_remove:
            clean_notes = re.sub(pattern, '', clean_notes, flags=re.DOTALL)
        
        # Clean up extra spaces, commas, and separators
        clean_notes = re.sub(r'\s*,\s*$', '', clean_notes)   # Remove trailing ,
        clean_notes = re.sub(r'\s*\|\s*$', '', clean_notes)  # Remove trailing |
        clean_notes = re.sub(r'^\s*\|\s*', '', clean_notes)  # Remove leading |
        clean_notes = re.sub(r'^\s*,\s*', '', clean_notes)   # Remove leading ,
        clean_notes = re.sub(r'\s+', ' ', clean_notes)       # Normalize spaces
        clean_notes = clean_notes.strip()
        
        return clean_notes if clean_notes else None

# Create the migration instance for discovery
migration = Migration022AddPerformanceDataColumn()