#!/usr/bin/env python3
"""
Migration 038: Journal System

Adds comprehensive journal system for documenting bow setup changes including:
- User-created journal entries with rich text descriptions
- Photo attachments and documentation  
- Integration with existing change log system
- Searchable tags and categories
- Cross-references to specific equipment and setups
"""

import sqlite3
import os
from pathlib import Path

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

def run_migration():
    """Execute the journal system migration"""
    db_path = get_database_path()
    print(f"🔄 Running Migration 038: Journal System")
    print(f"📁 Database path: {db_path}")
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("📋 Creating journal tables...")
        
        # Create journal_entries table - main journal system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
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
        print("✅ Created journal_entries table")
        
        # Create journal_attachments table for photos and files
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_entry_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_type TEXT NOT NULL, -- 'image', 'document', 'video'
                file_size INTEGER,
                mime_type TEXT,
                file_path TEXT NOT NULL, -- Local storage path
                cdn_url TEXT, -- CDN URL if uploaded
                description TEXT,
                is_primary BOOLEAN DEFAULT 0, -- Primary image for entry
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Constraints
                FOREIGN KEY (journal_entry_id) REFERENCES journal_entries (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Created journal_attachments table")
        
        # Create journal_equipment_references table for linking to specific equipment
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_equipment_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_entry_id INTEGER NOT NULL,
                bow_equipment_id INTEGER,
                arrow_id INTEGER,
                reference_type TEXT NOT NULL CHECK (reference_type IN (
                    'mentioned', 'modified', 'installed', 'removed', 'compared'
                )),
                notes TEXT,
                -- Constraints
                FOREIGN KEY (journal_entry_id) REFERENCES journal_entries (id) ON DELETE CASCADE,
                FOREIGN KEY (bow_equipment_id) REFERENCES bow_equipment (id) ON DELETE CASCADE,
                FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE SET NULL,
                -- At least one reference must be provided
                CHECK ((bow_equipment_id IS NOT NULL) OR (arrow_id IS NOT NULL))
            )
        ''')
        print("✅ Created journal_equipment_references table")
        
        # Create journal_change_links table to connect with existing change log system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_change_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_entry_id INTEGER NOT NULL,
                change_log_type TEXT NOT NULL CHECK (change_log_type IN (
                    'equipment', 'setup', 'arrow'
                )),
                change_log_id INTEGER NOT NULL,
                link_type TEXT DEFAULT 'documents' CHECK (link_type IN (
                    'documents', 'caused_by', 'resulted_in'
                )),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Constraints
                FOREIGN KEY (journal_entry_id) REFERENCES journal_entries (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Created journal_change_links table")
        
        # Create performance indexes
        print("🔧 Creating performance indexes...")
        
        # Journal entries indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_user_date 
            ON journal_entries (user_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_setup_date 
            ON journal_entries (bow_setup_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_type 
            ON journal_entries (entry_type, created_at DESC)
        ''')
        
        # FTS (Full Text Search) for journal content
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS journal_fts USING fts5 (
                title, content, tags,
                content='journal_entries',
                content_rowid='id'
            )
        ''')
        
        # Populate FTS table with any existing entries
        cursor.execute('''
            INSERT INTO journal_fts(rowid, title, content, tags) 
            SELECT id, title, content, COALESCE(tags, '') FROM journal_entries
        ''')
        
        # Attachment indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_attachments_entry 
            ON journal_attachments (journal_entry_id, is_primary DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_attachments_type 
            ON journal_attachments (file_type, created_at DESC)
        ''')
        
        # Equipment reference indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_equipment_ref_entry 
            ON journal_equipment_references (journal_entry_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_equipment_ref_equipment 
            ON journal_equipment_references (bow_equipment_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_equipment_ref_arrow 
            ON journal_equipment_references (arrow_id)
        ''')
        
        # Change link indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_change_links_entry 
            ON journal_change_links (journal_entry_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_change_links_change 
            ON journal_change_links (change_log_type, change_log_id)
        ''')
        
        print("✅ Created all performance indexes")
        
        # Create triggers for FTS maintenance
        print("🔧 Creating FTS maintenance triggers...")
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS journal_ai AFTER INSERT ON journal_entries BEGIN
                INSERT INTO journal_fts(rowid, title, content, tags) 
                VALUES (new.id, new.title, new.content, COALESCE(new.tags, ''));
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS journal_ad AFTER DELETE ON journal_entries BEGIN
                INSERT INTO journal_fts(journal_fts, rowid, title, content, tags) 
                VALUES('delete', old.id, old.title, old.content, COALESCE(old.tags, ''));
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS journal_au AFTER UPDATE ON journal_entries BEGIN
                INSERT INTO journal_fts(journal_fts, rowid, title, content, tags) 
                VALUES('delete', old.id, old.title, old.content, COALESCE(old.tags, ''));
                INSERT INTO journal_fts(rowid, title, content, tags) 
                VALUES (new.id, new.title, new.content, COALESCE(new.tags, ''));
            END
        ''')
        
        print("✅ Created FTS maintenance triggers")
        
        # Create sample journal entry for demonstration
        print("📝 Creating sample journal entry...")
        
        # Get the first user for demonstration
        cursor.execute('SELECT id FROM users LIMIT 1')
        user_row = cursor.fetchone()
        
        if user_row:
            user_id = user_row[0]
            
            # Get first bow setup
            cursor.execute('SELECT id FROM bow_setups WHERE user_id = ? LIMIT 1', (user_id,))
            setup_row = cursor.fetchone()
            
            setup_id = setup_row[0] if setup_row else None
            
            cursor.execute('''
                INSERT INTO journal_entries 
                (user_id, bow_setup_id, title, content, entry_type, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                setup_id,
                'Welcome to Your Archery Journal',
                '''This is your new archery journal where you can document all changes, upgrades, and observations about your equipment.

Use this journal to:
• Record equipment changes and the reasons behind them
• Document tuning sessions and their results  
• Note shooting observations and performance changes
• Track maintenance activities
• Plan future upgrades

Your journal entries will automatically link to your change history, making it easy to follow the evolution of your setup over time.''',
                'general',
                '["welcome", "getting_started", "documentation"]'
            ))
            print("✅ Created welcome journal entry")
        else:
            print("ℹ️  No users found - skipping sample entry creation")
        
        conn.commit()
        print("🎉 Migration 038 completed successfully!")
        print("📊 Journal system is now active")
        print("   • Users can create rich journal entries with photos")
        print("   • Full-text search enabled for finding entries")
        print("   • Equipment and change log integration available")
        print("   • Multiple entry types support different use cases")
        print("   • Tags and categories for organization")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()