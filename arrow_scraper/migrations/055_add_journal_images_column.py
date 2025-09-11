#!/usr/bin/env python3
"""
Migration 055: Add Images Column to Journal Entries

Adds an images column to the journal_entries table to support direct JSON storage
of image arrays for journal entries, particularly for tuning session images.

This migration supports the enhanced journal system where images can be stored
directly as JSON in the journal entry for simplified access and display.
"""

import sqlite3
import os
import json
from pathlib import Path

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 55,
        'description': 'Add Images Column to Journal Entries',
        'author': 'System',
        'created_at': '2025-09-10',
        'target_database': 'unified',  # Targets the unified arrow_database.db
        'dependencies': [38, 41],  # Requires journal system and image upload system
        'environments': ['all']
    }

def get_database_path():
    """Get the correct unified database path"""
    # Check for environment variable first (Docker deployment)
    env_db_path = os.environ.get('ARROW_DATABASE_PATH')
    if env_db_path:
        print(f"🔧 Using ARROW_DATABASE_PATH: {env_db_path}")
        return env_db_path
    
    # Unified database paths
    possible_paths = [
        Path("/app/databases/arrow_database.db"),  # Docker path
        Path(__file__).parent.parent / "databases" / "arrow_database.db",  # Local development
        Path(__file__).parent.parent / "arrow_database.db",  # Legacy local path
    ]
    
    for p in possible_paths:
        if p.exists():
            print(f"📁 Found unified database at: {p}")
            return str(p)
    
    # Default to first option for new installations
    return str(possible_paths[0])

def migrate_up(cursor):
    """Add images column to journal_entries table"""
    conn = cursor.connection
    
    try:
        print("🚀 Migration 055: Adding images column to journal_entries...")
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(journal_entries)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'images' not in columns:
            # Add images column to journal_entries table
            print("📸 Adding images column to journal_entries table...")
            
            # SQLite requires special handling for adding columns to tables with constraints
            cursor.execute('PRAGMA foreign_keys=OFF')
            
            # Create new table with images column
            cursor.execute('''
                CREATE TABLE journal_entries_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bow_setup_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    entry_type TEXT NOT NULL DEFAULT 'general' CHECK (entry_type IN (
                        'general', 'setup_change', 'equipment_change', 'arrow_change',
                        'tuning_session', 'shooting_notes', 'maintenance', 'upgrade'
                    )),
                    tags TEXT,  -- JSON array of searchable tags
                    is_private BOOLEAN DEFAULT 0,
                    images TEXT,  -- JSON array of image objects
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    -- Constraints
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
                )
            ''')
            
            # Copy data from old table
            cursor.execute('''
                INSERT INTO journal_entries_new (
                    id, user_id, bow_setup_id, title, content, entry_type, tags,
                    is_private, created_at, updated_at
                )
                SELECT id, user_id, bow_setup_id, title, content, entry_type, tags,
                       is_private, created_at, updated_at
                FROM journal_entries
            ''')
            
            # Drop old table
            cursor.execute('DROP TABLE journal_entries')
            
            # Rename new table
            cursor.execute('ALTER TABLE journal_entries_new RENAME TO journal_entries')
            
            # Recreate indexes
            cursor.execute('''
                CREATE INDEX idx_journal_entries_user_date 
                ON journal_entries (user_id, created_at DESC)
            ''')
            cursor.execute('''
                CREATE INDEX idx_journal_entries_setup_date 
                ON journal_entries (bow_setup_id, created_at DESC)
            ''')
            cursor.execute('''
                CREATE INDEX idx_journal_entries_type 
                ON journal_entries (entry_type, created_at DESC)
            ''')
            
            # Recreate triggers if they exist
            try:
                cursor.execute('''
                    CREATE TRIGGER journal_ai AFTER INSERT ON journal_entries BEGIN
                        INSERT INTO journal_fts(rowid, title, content, tags) 
                        VALUES (new.id, new.title, new.content, COALESCE(new.tags, ''));
                    END
                ''')
                cursor.execute('''
                    CREATE TRIGGER journal_ad AFTER DELETE ON journal_entries BEGIN
                        INSERT INTO journal_fts(journal_fts, rowid, title, content, tags) 
                        VALUES('delete', old.id, old.title, old.content, COALESCE(old.tags, ''));
                    END
                ''')
                cursor.execute('''
                    CREATE TRIGGER journal_au AFTER UPDATE ON journal_entries BEGIN
                        INSERT INTO journal_fts(journal_fts, rowid, title, content, tags) 
                        VALUES('delete', old.id, old.title, old.content, COALESCE(old.tags, ''));
                        INSERT INTO journal_fts(rowid, title, content, tags) 
                        VALUES (new.id, new.title, new.content, COALESCE(new.tags, ''));
                    END
                ''')
            except sqlite3.OperationalError:
                # FTS table might not exist, skip triggers
                pass
            
            cursor.execute('PRAGMA foreign_keys=ON')
            print("✅ Added images column to journal_entries")
        else:
            print("✅ Images column already exists in journal_entries")
        
        # Create index for querying entries with images
        print("⚡ Creating index for entries with images...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_with_images
            ON journal_entries (user_id, images) 
            WHERE images IS NOT NULL
        ''')
        print("✅ Created index for entries with images")
        
        # Migrate existing journal_attachments to images column if needed
        print("🔄 Checking for existing journal attachments to migrate...")
        cursor.execute('''
            SELECT ja.journal_entry_id, 
                   GROUP_CONCAT(
                       json_object(
                           'url', COALESCE(ja.cdn_url, ja.file_path),
                           'alt', COALESCE(ja.description, ja.original_filename),
                           'uploadedAt', ja.created_at,
                           'originalFilename', ja.original_filename,
                           'fileType', ja.file_type,
                           'fileSize', ja.file_size,
                           'isPrimary', ja.is_primary
                       )
                   ) as images_json
            FROM journal_attachments ja
            WHERE ja.file_type = 'image'
            GROUP BY ja.journal_entry_id
        ''')
        
        attachments_to_migrate = cursor.fetchall()
        
        if attachments_to_migrate:
            print(f"📦 Found {len(attachments_to_migrate)} journal entries with attachments to migrate...")
            
            for entry_id, images_json in attachments_to_migrate:
                try:
                    # Convert the GROUP_CONCAT result to proper JSON array
                    images_list = f"[{images_json}]"
                    
                    # Update the journal entry with the images
                    cursor.execute('''
                        UPDATE journal_entries 
                        SET images = ?
                        WHERE id = ? AND (images IS NULL OR images = '')
                    ''', (images_list, entry_id))
                    
                except Exception as e:
                    print(f"⚠️ Could not migrate images for entry {entry_id}: {e}")
                    continue
            
            print("✅ Migrated existing journal attachments to images column")
        else:
            print("ℹ️ No existing journal attachments to migrate")
        
        conn.commit()
        print("🎉 Migration 055 completed successfully!")
        print("📊 Journal entries now support direct image storage:")
        print("   • Added images column for JSON image array storage")
        print("   • Created performance index for image queries")
        print("   • Migrated existing journal attachments")
        print("   • Maintains backward compatibility with journal_attachments")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 055 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Remove images column from journal_entries table"""
    conn = cursor.connection
    
    try:
        print("🔄 Migration 055: Downgrading journal images column...")
        
        # Drop index
        print("🗑️ Dropping images index...")
        cursor.execute('DROP INDEX IF EXISTS idx_journal_entries_with_images')
        
        # SQLite doesn't support dropping columns directly, so we need to recreate the table
        print("🔄 Recreating journal_entries table without images column...")
        
        # Create backup table
        cursor.execute('''
            CREATE TABLE journal_entries_backup AS
            SELECT id, user_id, bow_setup_id, title, content, entry_type, tags, 
                   is_private, created_at, updated_at
            FROM journal_entries
        ''')
        
        # Drop original table
        cursor.execute('DROP TABLE journal_entries')
        
        # Recreate original table structure
        cursor.execute('''
            CREATE TABLE journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bow_setup_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                entry_type TEXT NOT NULL DEFAULT 'general' CHECK (entry_type IN (
                    'general', 'setup_change', 'equipment_change', 'arrow_change',
                    'tuning_session', 'shooting_notes', 'maintenance', 'upgrade'
                )),
                tags TEXT,  -- JSON array of searchable tags
                is_private BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Constraints
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
            )
        ''')
        
        # Restore data
        cursor.execute('''
            INSERT INTO journal_entries (
                id, user_id, bow_setup_id, title, content, entry_type, tags,
                is_private, created_at, updated_at
            )
            SELECT id, user_id, bow_setup_id, title, content, entry_type, tags,
                   is_private, created_at, updated_at
            FROM journal_entries_backup
        ''')
        
        # Drop backup table
        cursor.execute('DROP TABLE journal_entries_backup')
        
        # Recreate original indexes
        cursor.execute('''
            CREATE INDEX idx_journal_entries_user_date 
            ON journal_entries (user_id, created_at DESC)
        ''')
        cursor.execute('''
            CREATE INDEX idx_journal_entries_setup_date 
            ON journal_entries (bow_setup_id, created_at DESC)
        ''')
        cursor.execute('''
            CREATE INDEX idx_journal_entries_type 
            ON journal_entries (entry_type, created_at DESC)
        ''')
        
        conn.commit()
        print("✅ Migration 055 downgrade completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 055 downgrade failed: {e}")
        conn.rollback()
        return False

def run_migration():
    """Execute the journal images column migration"""
    db_path = get_database_path()
    print(f"🔄 Running Migration 055: Add Journal Images Column")
    print(f"📁 Database path: {db_path}")
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        success = migrate_up(cursor)
        if success:
            print("✅ Migration completed successfully")
        else:
            print("❌ Migration failed")
            return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'down':
        # Run downgrade migration
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        success = migrate_down(conn.cursor())
        conn.close()
        
        if success:
            print("✅ Downgrade completed successfully")
        else:
            print("❌ Downgrade failed")
            sys.exit(1)
    else:
        # Run upgrade migration
        success = run_migration()
        if not success:
            sys.exit(1)