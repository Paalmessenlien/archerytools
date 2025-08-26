#!/usr/bin/env python3
"""
Migration 043: Journal Enhancement Templates System

Creates database support for journal entry templates, equipment linking, 
and advanced filtering to complete the journal enhancement requirements.

Features:
- Journal entry templates with customizable fields
- Equipment and arrow linking to specific bow setups
- Advanced filtering system with saved filter presets
- Template categories and user-specific templates
- Equipment change tracking integration
- Performance optimizations for journal queries
"""

import sqlite3
import os
from pathlib import Path

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 43,
        'description': 'Journal Enhancement Templates System',
        'author': 'System',
        'created_at': '2025-08-26',
        'target_database': 'unified',  # Targets the unified arrow_database.db
        'dependencies': [42],  # Requires universal tag management system
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
    """Add journal enhancement templates system"""
    conn = cursor.connection
    
    try:
        print("🚀 Migration 043: Adding Journal Enhancement Templates System...")
        
        # 1. Create journal_templates table for reusable templates
        print("📝 Creating journal_templates table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                category VARCHAR(30) DEFAULT 'general' CHECK (category IN (
                    'general', 'tuning', 'practice', 'competition', 'equipment', 'maintenance'
                )),
                template_data TEXT NOT NULL, -- JSON: title, content, entry_type, suggested_tags
                is_system_template BOOLEAN DEFAULT FALSE,
                is_public BOOLEAN DEFAULT FALSE,
                created_by INTEGER,
                usage_count INTEGER DEFAULT 0,
                last_used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        print("✅ Created journal_templates table")
        
        # 2. Create equipment_journal_links table for linking equipment to journal entries
        print("🔗 Creating equipment_journal_links table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment_journal_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_entry_id INTEGER NOT NULL,
                equipment_type VARCHAR(30) NOT NULL CHECK (equipment_type IN (
                    'bow', 'arrows', 'sight', 'rest', 'stabilizer', 'release', 'quiver', 'other'
                )),
                equipment_id INTEGER, -- Reference to specific equipment if available
                equipment_name TEXT NOT NULL,
                manufacturer TEXT,
                model TEXT,
                specifications TEXT, -- JSON: spine, length, weight, etc.
                link_type VARCHAR(20) DEFAULT 'used_with' CHECK (link_type IN (
                    'used_with', 'changed_from', 'changed_to', 'tested', 'reviewed'
                )),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Created equipment_journal_links table")
        
        # 3. Create journal_filter_presets table for saved filter configurations
        print("🔍 Creating journal_filter_presets table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_filter_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name VARCHAR(50) NOT NULL,
                description TEXT,
                filter_config TEXT NOT NULL, -- JSON: entry_types, date_range, tags, bow_setups, etc.
                is_default BOOLEAN DEFAULT FALSE,
                sort_order VARCHAR(20) DEFAULT 'newest' CHECK (sort_order IN (
                    'newest', 'oldest', 'most_relevant', 'title_asc', 'title_desc'
                )),
                usage_count INTEGER DEFAULT 0,
                last_used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, name)
            )
        ''')
        print("✅ Created journal_filter_presets table")
        
        # 4. Create change_log_entries table for tracking equipment changes
        print("📋 Creating change_log_entries table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS change_log_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bow_setup_id INTEGER,
                change_type VARCHAR(30) NOT NULL CHECK (change_type IN (
                    'equipment_change', 'setup_change', 'arrow_change', 'tuning_change'
                )),
                change_category VARCHAR(20) NOT NULL CHECK (change_category IN (
                    'added', 'removed', 'modified', 'tuned', 'replaced'
                )),
                item_type VARCHAR(30) NOT NULL,
                item_name TEXT NOT NULL,
                old_value TEXT, -- JSON: previous specifications
                new_value TEXT, -- JSON: new specifications
                reason TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups(id) ON DELETE SET NULL
            )
        ''')
        print("✅ Created change_log_entries table")
        
        # 5. Add new columns to existing journal_entries table
        print("📝 Enhancing journal_entries table...")
        
        # Add equipment_focus column for better filtering
        try:
            cursor.execute('''
                ALTER TABLE journal_entries ADD COLUMN equipment_focus TEXT
            ''')
            print("✅ Added equipment_focus column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ equipment_focus column already exists")
            else:
                raise e
        
        # Add template_used column to track template usage
        try:
            cursor.execute('''
                ALTER TABLE journal_entries ADD COLUMN template_used INTEGER
                REFERENCES journal_templates(id) ON DELETE SET NULL
            ''')
            print("✅ Added template_used column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ template_used column already exists")
            else:
                raise e
        
        # Add reading_time_seconds for content analysis
        try:
            cursor.execute('''
                ALTER TABLE journal_entries ADD COLUMN reading_time_seconds INTEGER DEFAULT 0
            ''')
            print("✅ Added reading_time_seconds column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ reading_time_seconds column already exists")
            else:
                raise e
        
        # 6. Create performance indexes
        print("⚡ Creating performance indexes...")
        
        # Journal templates indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_templates_category
            ON journal_templates (category, is_system_template, usage_count DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_templates_public
            ON journal_templates (is_public, category, usage_count DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_templates_user
            ON journal_templates (created_by, category, created_at DESC)
        ''')
        
        # Equipment journal links indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_equipment_journal_links_entry
            ON equipment_journal_links (journal_entry_id, equipment_type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_equipment_journal_links_equipment
            ON equipment_journal_links (equipment_type, equipment_name, created_at DESC)
        ''')
        
        # Filter presets indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_filter_presets_user
            ON journal_filter_presets (user_id, is_default, usage_count DESC)
        ''')
        
        # Change log indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_change_log_entries_user_date
            ON change_log_entries (user_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_change_log_entries_setup
            ON change_log_entries (bow_setup_id, change_type, created_at DESC)
        ''')
        
        # Enhanced journal entries indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_equipment_focus
            ON journal_entries (equipment_focus, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_template
            ON journal_entries (template_used, created_at DESC)
        ''')
        
        print("✅ Created all performance indexes")
        
        # 7. Insert system journal templates
        print("📚 Creating system journal templates...")
        
        system_templates = [
            ('Quick Tuning Note', 'Fast note about tuning adjustments', 'tuning', '''{
                "title": "Tuning Session - {date}",
                "content": "## Tuning Adjustments\\n\\n**Current Setup:**\\n- Bow: \\n- Arrows: \\n- Distance: \\n\\n**Issue:**\\n\\n**Adjustments Made:**\\n- \\n\\n**Results:**\\n\\n**Next Steps:**\\n",
                "entry_type": "Tuning Session",
                "suggested_tags": ["tuning", "adjustment", "improvement"],
                "equipment_focus": "sight,rest,arrows"
            }'''),
            
            ('Practice Session', 'Record practice results and observations', 'practice', '''{
                "title": "Practice - {date}",
                "content": "## Practice Session\\n\\n**Setup:**\\n- Distance: \\n- Rounds: \\n- Arrows per end: \\n\\n**Scores:**\\n\\n**What worked well:**\\n- \\n\\n**Areas for improvement:**\\n- \\n\\n**Focus for next session:**\\n",
                "entry_type": "Shooting Notes",
                "suggested_tags": ["practice", "scoring", "technique"],
                "equipment_focus": "bow,arrows,sight"
            }'''),
            
            ('Equipment Change', 'Log equipment modifications and upgrades', 'equipment', '''{
                "title": "Equipment Change - {equipment_type}",
                "content": "## Equipment Modification\\n\\n**Item Changed:** \\n\\n**From:** \\n\\n**To:** \\n\\n**Reason for change:**\\n\\n**Installation notes:**\\n\\n**Initial impression:**\\n\\n**Tuning required:**\\n- [ ] Paper tuning\\n- [ ] Walk back tuning\\n- [ ] Fine adjustments",
                "entry_type": "Equipment Change",
                "suggested_tags": ["equipment", "upgrade", "installation"],
                "equipment_focus": "varies"
            }'''),
            
            ('Competition Preparation', 'Plan and track competition readiness', 'competition', '''{
                "title": "Competition Prep - {event_name}",
                "content": "## Competition: {event_name}\\n\\n**Date:** \\n**Venue:** \\n**Format:** \\n\\n**Equipment Check:**\\n- [ ] Bow inspection\\n- [ ] Arrow condition\\n- [ ] Sight settings verified\\n- [ ] Spare parts packed\\n\\n**Practice Plan:**\\n\\n**Goals:**\\n- \\n\\n**Strategy:**\\n",
                "entry_type": "Competition",
                "suggested_tags": ["competition", "preparation", "goals"],
                "equipment_focus": "bow,arrows,sight,rest"
            }'''),
            
            ('Maintenance Log', 'Track regular maintenance activities', 'maintenance', '''{
                "title": "Maintenance - {date}",
                "content": "## Maintenance Session\\n\\n**Items Serviced:**\\n\\n**String/Cable:**\\n- Condition: \\n- Wax applied: \\n- Serving checked: \\n\\n**Bow:**\\n- Limbs checked: \\n- Screws tightened: \\n- Cleaning: \\n\\n**Accessories:**\\n- Sight: \\n- Rest: \\n- Stabilizers: \\n\\n**Next maintenance due:**",
                "entry_type": "Maintenance",
                "suggested_tags": ["maintenance", "cleaning", "inspection"],
                "equipment_focus": "bow,string,accessories"
            }'''),
            
            ('New Equipment Review', 'Review and evaluate new equipment', 'equipment', '''{
                "title": "Review: {equipment_name}",
                "content": "## Equipment Review\\n\\n**Product:** \\n**Manufacturer:** \\n**Model:** \\n**Purchase Date:** \\n\\n**First Impressions:**\\n\\n**Installation Experience:**\\n- Difficulty: \\n- Time required: \\n- Tools needed: \\n\\n**Performance:**\\n\\n**Pros:**\\n- \\n\\n**Cons:**\\n- \\n\\n**Rating:** ⭐⭐⭐⭐⭐\\n\\n**Would I recommend?**",
                "entry_type": "Upgrade",
                "suggested_tags": ["review", "new-equipment", "evaluation"],
                "equipment_focus": "varies"
            }''')
        ]
        
        for name, desc, category, template_data in system_templates:
            try:
                cursor.execute('''
                    INSERT INTO journal_templates (
                        name, description, category, template_data, is_system_template, is_public
                    ) VALUES (?, ?, ?, ?, TRUE, TRUE)
                ''', (name, desc, category, template_data))
            except sqlite3.IntegrityError:
                # Template already exists, skip
                pass
        
        print("✅ Created system journal templates")
        
        # 8. Create default filter presets for users
        print("🔍 Creating sample filter presets...")
        
        # Get the first user for demonstration
        cursor.execute('SELECT id FROM users LIMIT 1')
        user_row = cursor.fetchone()
        
        if user_row:
            user_id = user_row[0]
            
            default_filters = [
                ('Recent Entries', 'Last 30 days of entries', '{"date_range": "30_days", "sort_order": "newest"}', True),
                ('Tuning Sessions', 'All tuning-related entries', '{"entry_types": ["Tuning Session"], "sort_order": "newest"}', False),
                ('Practice Notes', 'Practice and shooting notes', '{"entry_types": ["Shooting Notes"], "sort_order": "newest"}', False),
                ('Equipment Changes', 'Equipment modifications and upgrades', '{"entry_types": ["Equipment Change", "Upgrade"], "sort_order": "newest"}', False),
                ('Competition Prep', 'Competition-related entries', '{"entry_types": ["Competition"], "sort_order": "newest"}', False)
            ]
            
            for name, desc, filter_config, is_default in default_filters:
                try:
                    cursor.execute('''
                        INSERT INTO journal_filter_presets (
                            user_id, name, description, filter_config, is_default
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, name, desc, filter_config, is_default))
                except sqlite3.IntegrityError:
                    # Filter preset already exists, skip
                    pass
            
            print("✅ Created sample filter presets")
        else:
            print("ℹ️  No users found - skipping sample filter presets creation")
        
        # 9. Create triggers for automatic updates
        print("🔧 Creating automated triggers...")
        
        # Trigger to update template usage count
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS journal_templates_increment_usage
            AFTER INSERT ON journal_entries
            WHEN NEW.template_used IS NOT NULL
            BEGIN
                UPDATE journal_templates 
                SET usage_count = usage_count + 1, 
                    last_used_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.template_used;
            END
        ''')
        
        # Trigger to update filter preset usage count
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS filter_presets_update_usage
            AFTER UPDATE ON journal_filter_presets
            WHEN NEW.last_used_at > OLD.last_used_at
            BEGIN
                UPDATE journal_filter_presets 
                SET usage_count = usage_count + 1 
                WHERE id = NEW.id;
            END
        ''')
        
        # Trigger for updated_at timestamps
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS journal_templates_updated_at
            AFTER UPDATE ON journal_templates
            BEGIN
                UPDATE journal_templates 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        ''')
        
        print("✅ Created automated triggers")
        
        conn.commit()
        print("🎉 Migration 043 completed successfully!")
        print("📊 Journal Enhancement Templates System is now active:")
        print("   • Reusable journal entry templates with 6 system templates")
        print("   • Equipment and arrow linking to specific bow setups")
        print("   • Advanced filtering system with saved filter presets")
        print("   • Equipment change tracking and integration")
        print("   • Template usage analytics and recommendations")
        print("   • Performance optimizations for journal queries")
        print("   • Automatic template and filter usage tracking")
        print("   • Enhanced journal entry metadata and categorization")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 043 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Remove journal enhancement templates system"""
    conn = cursor.connection
    
    try:
        print("🔄 Migration 043: Downgrading Journal Enhancement Templates System...")
        
        # Drop triggers first
        print("🗑️ Dropping triggers...")
        cursor.execute('DROP TRIGGER IF EXISTS journal_templates_increment_usage')
        cursor.execute('DROP TRIGGER IF EXISTS filter_presets_update_usage')
        cursor.execute('DROP TRIGGER IF EXISTS journal_templates_updated_at')
        
        # Drop indexes
        print("🗑️ Dropping indexes...")
        indexes_to_drop = [
            'idx_journal_templates_category',
            'idx_journal_templates_public',
            'idx_journal_templates_user',
            'idx_equipment_journal_links_entry',
            'idx_equipment_journal_links_equipment',
            'idx_journal_filter_presets_user',
            'idx_change_log_entries_user_date',
            'idx_change_log_entries_setup',
            'idx_journal_entries_equipment_focus',
            'idx_journal_entries_template'
        ]
        
        for index_name in indexes_to_drop:
            try:
                cursor.execute(f'DROP INDEX IF EXISTS {index_name}')
            except Exception as e:
                print(f"⚠️ Could not drop index {index_name}: {e}")
        
        # Drop tables in dependency order
        print("🗑️ Dropping journal enhancement tables...")
        cursor.execute('DROP TABLE IF EXISTS change_log_entries')
        cursor.execute('DROP TABLE IF EXISTS journal_filter_presets')
        cursor.execute('DROP TABLE IF EXISTS equipment_journal_links')
        cursor.execute('DROP TABLE IF EXISTS journal_templates')
        
        # Note: SQLite doesn't support DROP COLUMN, so we can't remove the added columns
        # from journal_entries without recreating the entire table
        print("⚠️ Note: Added columns to journal_entries will remain (SQLite limitation)")
        
        conn.commit()
        print("✅ Migration 043 downgrade completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 043 downgrade failed: {e}")
        conn.rollback()
        return False

def run_migration():
    """Execute the journal enhancement templates system migration"""
    db_path = get_database_path()
    print(f"🔄 Running Migration 043: Journal Enhancement Templates System")
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