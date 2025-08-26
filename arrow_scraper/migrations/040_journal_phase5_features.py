#!/usr/bin/env python3
"""
Migration 040: Journal Enhancement Phase 5 Features

Adds advanced journal features including:
- Custom categories system for organizing entries beyond default types
- Change linking system to connect entries with equipment/setup modifications
- Favorites system for starring important entries
- Rich text content format support
- Performance indexes for optimal query performance
"""

import sqlite3
import os
from pathlib import Path

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 40,
        'description': 'Journal Enhancement Phase 5 Features',
        'author': 'System',
        'created_at': '2025-08-26',
        'target_database': 'unified',  # Targets the unified arrow_database.db
        'dependencies': [38, 39],  # Requires journal system and active bow setup
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
    """Add Phase 5 journal features"""
    conn = cursor.connection
    
    try:
        print("🚀 Migration 040: Adding Journal Phase 5 features...")
        
        # 1. Create journal_categories table for custom categories system
        print("📁 Creating journal_categories table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                description TEXT,
                color VARCHAR(20) DEFAULT 'blue' CHECK (color IN (
                    'blue', 'green', 'orange', 'purple', 'red', 'teal', 'indigo', 'pink'
                )),
                icon VARCHAR(30) DEFAULT 'folder' CHECK (icon IN (
                    'folder', 'label', 'bookmark', 'star', 'flag', 'tag', 'category', 
                    'collections', 'local_offer', 'workspace_premium', 'grade', 'psychology'
                )),
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, name)
            )
        ''')
        print("✅ Created journal_categories table")
        
        # 2. Create journal_entry_links table for change linking system
        print("🔗 Creating journal_entry_links table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entry_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_entry_id INTEGER NOT NULL,
                change_log_type VARCHAR(50) NOT NULL CHECK (change_log_type IN (
                    'equipment_change', 'setup_change', 'arrow_change'
                )),
                change_log_id INTEGER NOT NULL,
                link_type VARCHAR(20) DEFAULT 'documents' CHECK (link_type IN (
                    'documents', 'caused_by', 'resulted_in'
                )),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE,
                UNIQUE(journal_entry_id, change_log_type, change_log_id)
            )
        ''')
        print("✅ Created journal_entry_links table")
        
        # 3. Add new columns to existing journal_entries table
        print("📝 Adding new columns to journal_entries table...")
        
        # Add is_favorite column for favorites system
        try:
            cursor.execute('''
                ALTER TABLE journal_entries ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE
            ''')
            print("✅ Added is_favorite column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ is_favorite column already exists")
            else:
                raise e
        
        # Add category_id column for custom categories
        try:
            cursor.execute('''
                ALTER TABLE journal_entries ADD COLUMN category_id INTEGER
                REFERENCES journal_categories(id) ON DELETE SET NULL
            ''')
            print("✅ Added category_id column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ category_id column already exists")
            else:
                raise e
        
        # Add content_format column for rich text support
        try:
            cursor.execute('''
                ALTER TABLE journal_entries ADD COLUMN content_format VARCHAR(20) DEFAULT 'plain'
                CHECK (content_format IN ('plain', 'rich'))
            ''')
            print("✅ Added content_format column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ content_format column already exists")
            else:
                raise e
        
        # 4. Create performance indexes
        print("⚡ Creating performance indexes...")
        
        # Categories indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_categories_user
            ON journal_categories (user_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_categories_name
            ON journal_categories (user_id, name)
        ''')
        
        # Entry links indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entry_links_entry
            ON journal_entry_links (journal_entry_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entry_links_change
            ON journal_entry_links (change_log_type, change_log_id)
        ''')
        
        # Enhanced journal entries indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_favorites
            ON journal_entries (user_id, is_favorite, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_category
            ON journal_entries (category_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_format
            ON journal_entries (content_format, created_at DESC)
        ''')
        
        print("✅ Created all performance indexes")
        
        # 5. Create sample data for demonstration
        print("📋 Creating sample categories...")
        
        # Get the first user for demonstration
        cursor.execute('SELECT id FROM users LIMIT 1')
        user_row = cursor.fetchone()
        
        if user_row:
            user_id = user_row[0]
            
            # Create sample categories
            sample_categories = [
                ('Equipment Reviews', 'Notes and reviews of equipment before purchase', 'blue', 'grade'),
                ('Tuning Progress', 'Documentation of tuning sessions and adjustments', 'green', 'psychology'),
                ('Competition Prep', 'Preparation notes and strategies for competitions', 'orange', 'star'),
                ('Maintenance Log', 'Regular maintenance activities and schedules', 'purple', 'handyman')
            ]
            
            for name, desc, color, icon in sample_categories:
                try:
                    cursor.execute('''
                        INSERT INTO journal_categories (name, description, color, icon, user_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, desc, color, icon, user_id))
                except sqlite3.IntegrityError:
                    # Category already exists, skip
                    pass
            
            print("✅ Created sample categories")
            
            # Update existing journal entries to demonstrate features
            cursor.execute('''
                UPDATE journal_entries 
                SET content_format = 'plain', is_favorite = 0
                WHERE content_format IS NULL
            ''')
            print("✅ Updated existing entries with default values")
        else:
            print("ℹ️  No users found - skipping sample data creation")
        
        # 6. Create triggers for updated_at timestamps
        print("🔧 Creating update triggers...")
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS journal_categories_updated_at
            AFTER UPDATE ON journal_categories
            BEGIN
                UPDATE journal_categories 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        ''')
        
        print("✅ Created update triggers")
        
        conn.commit()
        print("🎉 Migration 040 completed successfully!")
        print("📊 Phase 5 journal features are now active:")
        print("   • Custom categories system with 8 colors and 12 icons")
        print("   • Change linking system connecting entries to equipment modifications")
        print("   • Favorites system for starring important entries")
        print("   • Rich text content format support")
        print("   • Performance indexes for optimal query speed")
        print("   • Sample categories created for immediate use")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 040 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Remove Phase 5 journal features"""
    conn = cursor.connection
    
    try:
        print("🔄 Migration 040: Downgrading Phase 5 features...")
        
        # Drop indexes first
        print("🗑️ Dropping indexes...")
        indexes_to_drop = [
            'idx_journal_categories_user',
            'idx_journal_categories_name', 
            'idx_journal_entry_links_entry',
            'idx_journal_entry_links_change',
            'idx_journal_entries_favorites',
            'idx_journal_entries_category',
            'idx_journal_entries_format'
        ]
        
        for index_name in indexes_to_drop:
            try:
                cursor.execute(f'DROP INDEX IF EXISTS {index_name}')
            except Exception as e:
                print(f"⚠️ Could not drop index {index_name}: {e}")
        
        # Drop triggers
        cursor.execute('DROP TRIGGER IF EXISTS journal_categories_updated_at')
        
        # Drop tables
        print("🗑️ Dropping Phase 5 tables...")
        cursor.execute('DROP TABLE IF EXISTS journal_entry_links')
        cursor.execute('DROP TABLE IF EXISTS journal_categories')
        
        # Note: SQLite doesn't support DROP COLUMN, so we can't remove the added columns
        # from journal_entries without recreating the entire table
        print("⚠️ Note: Added columns to journal_entries will remain (SQLite limitation)")
        
        conn.commit()
        print("✅ Migration 040 downgrade completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 040 downgrade failed: {e}")
        conn.rollback()
        return False

def run_migration():
    """Execute the Phase 5 features migration"""
    db_path = get_database_path()
    print(f"🔄 Running Migration 040: Journal Phase 5 Features")
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