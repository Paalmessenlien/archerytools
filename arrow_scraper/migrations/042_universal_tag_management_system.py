#!/usr/bin/env python3
"""
Migration 042: Universal Tag Management System

Creates database support for the universal useTagManagement composable system.
Provides tag functionality across all entity types with autocomplete, validation, and analytics.

Features:
- Universal tag system for all entity types (journal, equipment, setup, arrows)
- Tag popularity tracking and autocomplete suggestions
- Tag validation and normalization rules
- Batch tag operations and management
- Tag analytics and usage statistics
- Performance indexes for fast tag queries
"""

import sqlite3
import os
from pathlib import Path

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 42,
        'description': 'Universal Tag Management System',
        'author': 'System',
        'created_at': '2025-08-26',
        'target_database': 'unified',  # Targets the unified arrow_database.db
        'dependencies': [41],  # Requires modular image upload system
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
    """Add universal tag management system"""
    conn = cursor.connection
    
    try:
        print("🚀 Migration 042: Adding Universal Tag Management System...")
        
        # 1. Create system_tags table for universal tag storage
        print("🏷️ Creating system_tags table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                normalized_name VARCHAR(50) NOT NULL, -- lowercase, trimmed, spaces replaced with hyphens
                description TEXT,
                color VARCHAR(20) DEFAULT 'blue' CHECK (color IN (
                    'blue', 'green', 'orange', 'purple', 'red', 'teal', 'indigo', 'pink', 
                    'amber', 'lime', 'cyan', 'rose'
                )),
                is_global BOOLEAN DEFAULT FALSE, -- system-wide tags vs user-specific
                created_by INTEGER, -- user_id who created the tag
                usage_count INTEGER DEFAULT 0,
                last_used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
                UNIQUE(normalized_name)
            )
        ''')
        print("✅ Created system_tags table")
        
        # 2. Create entity_tags table for linking tags to entities
        print("🔗 Creating entity_tags table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entity_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN (
                    'journal', 'equipment', 'profile', 'setup', 'arrow', 'bow_setup', 'user'
                )),
                entity_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tag_id) REFERENCES system_tags(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(entity_type, entity_id, tag_id)
            )
        ''')
        print("✅ Created entity_tags table")
        
        # 3. Create tag_suggestions table for autocomplete and recommendations
        print("💡 Creating tag_suggestions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tag_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type VARCHAR(20) NOT NULL,
                suggested_tag VARCHAR(50) NOT NULL,
                context_tags TEXT, -- JSON array of related tags
                suggestion_score DECIMAL(3,2) DEFAULT 1.0,
                suggestion_type VARCHAR(20) DEFAULT 'related' CHECK (suggestion_type IN (
                    'popular', 'related', 'seasonal', 'trending', 'autocomplete'
                )),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Created tag_suggestions table")
        
        # 4. Create tag_analytics table for usage tracking
        print("📊 Creating tag_analytics table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tag_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_id INTEGER NOT NULL,
                entity_type VARCHAR(20) NOT NULL,
                user_id INTEGER,
                analytics_date DATE NOT NULL, -- YYYY-MM-DD for daily aggregation
                usage_count INTEGER DEFAULT 0,
                unique_entities INTEGER DEFAULT 0,
                unique_users INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tag_id) REFERENCES system_tags(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                UNIQUE(tag_id, entity_type, analytics_date, user_id)
            )
        ''')
        print("✅ Created tag_analytics table")
        
        # 5. Create tag_validation_rules table for tag validation
        print("✅ Creating tag_validation_rules table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tag_validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type VARCHAR(20) NOT NULL,
                max_tags INTEGER DEFAULT 20,
                min_tag_length INTEGER DEFAULT 2,
                max_tag_length INTEGER DEFAULT 30,
                allowed_characters VARCHAR(100) DEFAULT 'a-zA-Z0-9\\s\\-_',
                forbidden_words TEXT, -- JSON array of forbidden words
                require_approval BOOLEAN DEFAULT FALSE,
                auto_suggest BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(entity_type)
            )
        ''')
        print("✅ Created tag_validation_rules table")
        
        # 6. Create performance indexes
        print("⚡ Creating performance indexes...")
        
        # System tags indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_system_tags_normalized
            ON system_tags (normalized_name)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_system_tags_usage
            ON system_tags (usage_count DESC, last_used_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_system_tags_global
            ON system_tags (is_global, usage_count DESC)
        ''')
        
        # Entity tags indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_entity_tags_entity
            ON entity_tags (entity_type, entity_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_entity_tags_tag
            ON entity_tags (tag_id, entity_type, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_entity_tags_user
            ON entity_tags (user_id, entity_type, created_at DESC)
        ''')
        
        # Tag suggestions indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tag_suggestions_entity
            ON tag_suggestions (entity_type, suggested_tag, is_active)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tag_suggestions_score
            ON tag_suggestions (entity_type, suggestion_score DESC, is_active)
        ''')
        
        # Tag analytics indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tag_analytics_date
            ON tag_analytics (analytics_date DESC, entity_type, tag_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tag_analytics_usage
            ON tag_analytics (tag_id, usage_count DESC, analytics_date DESC)
        ''')
        
        print("✅ Created all performance indexes")
        
        # 7. Insert default validation rules
        print("📋 Creating default validation rules...")
        
        default_validations = [
            ('journal', 10, 2, 30, 'a-zA-Z0-9\\s\\-_', '["spam","test","dummy"]', False, True),
            ('equipment', 8, 2, 25, 'a-zA-Z0-9\\s\\-_', '["spam","test"]', False, True),
            ('setup', 12, 2, 35, 'a-zA-Z0-9\\s\\-_', '["spam","test"]', False, True),
            ('arrow', 6, 2, 25, 'a-zA-Z0-9\\s\\-_', '["spam","test"]', False, True),
            ('bow_setup', 12, 2, 35, 'a-zA-Z0-9\\s\\-_', '["spam","test"]', False, True),
            ('user', 5, 2, 20, 'a-zA-Z0-9\\s\\-_', '["admin","system","root"]', True, False)
        ]
        
        for entity_type, max_tags, min_len, max_len, allowed_chars, forbidden_words, require_approval, auto_suggest in default_validations:
            try:
                cursor.execute('''
                    INSERT INTO tag_validation_rules (
                        entity_type, max_tags, min_tag_length, max_tag_length, 
                        allowed_characters, forbidden_words, require_approval, auto_suggest
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (entity_type, max_tags, min_len, max_len, allowed_chars, forbidden_words, require_approval, auto_suggest))
            except sqlite3.IntegrityError:
                # Validation rule already exists, skip
                pass
        
        print("✅ Created default validation rules")
        
        # 8. Insert popular archery tags for suggestions
        print("🏹 Creating archery-specific tag suggestions...")
        
        archery_tags = [
            # Equipment tags
            ('equipment', 'bow', '["recurve","compound","traditional"]', 1.0, 'popular'),
            ('equipment', 'arrows', '["carbon","aluminum","wood"]', 1.0, 'popular'),
            ('equipment', 'sight', '["single-pin","multi-pin","adjustable"]', 0.9, 'popular'),
            ('equipment', 'rest', '["drop-away","whisker-biscuit","plunger"]', 0.9, 'popular'),
            ('equipment', 'stabilizer', '["front","side","back-bar"]', 0.8, 'popular'),
            
            # Journal tags  
            ('journal', 'practice', '["indoor","outdoor","target"]', 1.0, 'popular'),
            ('journal', 'tuning', '["paper","walk-back","french"]', 1.0, 'popular'),
            ('journal', 'competition', '["3d","field","target","indoor"]', 0.9, 'popular'),
            ('journal', 'maintenance', '["string","limbs","cleaning"]', 0.8, 'popular'),
            ('journal', 'upgrade', '["new-equipment","improvement"]', 0.7, 'popular'),
            
            # Setup tags
            ('setup', 'indoor', '["18m","25m","vegas","nfaa"]', 0.9, 'popular'),
            ('setup', 'outdoor', '["70m","50m","field","3d"]', 0.9, 'popular'),
            ('setup', 'hunting', '["broadhead","practice","setup"]', 0.8, 'popular'),
            
            # Arrow tags
            ('arrow', 'spine', '["300","350","400","500","600"]', 1.0, 'popular'),
            ('arrow', 'length', '["28","29","30","31","32"]', 0.9, 'popular'),
            ('arrow', 'point', '["100gr","125gr","150gr"]', 0.9, 'popular')
        ]
        
        for entity_type, tag_name, context_tags, score, suggestion_type in archery_tags:
            try:
                cursor.execute('''
                    INSERT INTO tag_suggestions (
                        entity_type, suggested_tag, context_tags, suggestion_score, suggestion_type
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (entity_type, tag_name, context_tags, score, suggestion_type))
            except sqlite3.IntegrityError:
                # Suggestion already exists, skip
                pass
        
        print("✅ Created archery-specific tag suggestions")
        
        # 9. Create triggers for automatic tag analytics and normalization
        print("🔧 Creating automated triggers...")
        
        # Trigger to normalize tag names on insert
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS system_tags_normalize_name
            BEFORE INSERT ON system_tags
            BEGIN
                UPDATE NEW SET normalized_name = lower(trim(replace(NEW.name, ' ', '-')));
            END
        ''')
        
        # Trigger to update tag usage count when entity_tags is created
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS entity_tags_increment_usage
            AFTER INSERT ON entity_tags
            BEGIN
                UPDATE system_tags 
                SET usage_count = usage_count + 1, 
                    last_used_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.tag_id;
            END
        ''')
        
        # Trigger to decrement tag usage count when entity_tags is deleted
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS entity_tags_decrement_usage
            AFTER DELETE ON entity_tags
            BEGIN
                UPDATE system_tags 
                SET usage_count = CASE 
                    WHEN usage_count > 0 THEN usage_count - 1 
                    ELSE 0 
                END 
                WHERE id = OLD.tag_id;
            END
        ''')
        
        # Trigger for updated_at timestamps
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS system_tags_updated_at
            AFTER UPDATE ON system_tags
            BEGIN
                UPDATE system_tags 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        ''')
        
        print("✅ Created automated triggers")
        
        conn.commit()
        print("🎉 Migration 042 completed successfully!")
        print("📊 Universal Tag Management System is now active:")
        print("   • Universal tag system across all entity types")
        print("   • Tag popularity tracking and autocomplete suggestions")
        print("   • Flexible validation rules per entity type")
        print("   • Tag analytics and usage statistics")
        print("   • Batch tag operations and management")
        print("   • Performance indexes for fast tag queries")
        print("   • Automatic tag normalization and usage tracking")
        print("   • Pre-loaded archery-specific tag suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 042 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Remove universal tag management system"""
    conn = cursor.connection
    
    try:
        print("🔄 Migration 042: Downgrading Universal Tag Management System...")
        
        # Drop triggers first
        print("🗑️ Dropping triggers...")
        cursor.execute('DROP TRIGGER IF EXISTS system_tags_normalize_name')
        cursor.execute('DROP TRIGGER IF EXISTS entity_tags_increment_usage')
        cursor.execute('DROP TRIGGER IF EXISTS entity_tags_decrement_usage')
        cursor.execute('DROP TRIGGER IF EXISTS system_tags_updated_at')
        
        # Drop indexes
        print("🗑️ Dropping indexes...")
        indexes_to_drop = [
            'idx_system_tags_normalized',
            'idx_system_tags_usage',
            'idx_system_tags_global',
            'idx_entity_tags_entity',
            'idx_entity_tags_tag',
            'idx_entity_tags_user',
            'idx_tag_suggestions_entity',
            'idx_tag_suggestions_score',
            'idx_tag_analytics_date',
            'idx_tag_analytics_usage'
        ]
        
        for index_name in indexes_to_drop:
            try:
                cursor.execute(f'DROP INDEX IF EXISTS {index_name}')
            except Exception as e:
                print(f"⚠️ Could not drop index {index_name}: {e}")
        
        # Drop tables in dependency order
        print("🗑️ Dropping universal tag management tables...")
        cursor.execute('DROP TABLE IF EXISTS tag_analytics')
        cursor.execute('DROP TABLE IF EXISTS tag_suggestions')
        cursor.execute('DROP TABLE IF EXISTS tag_validation_rules')
        cursor.execute('DROP TABLE IF EXISTS entity_tags')
        cursor.execute('DROP TABLE IF EXISTS system_tags')
        
        conn.commit()
        print("✅ Migration 042 downgrade completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 042 downgrade failed: {e}")
        conn.rollback()
        return False

def run_migration():
    """Execute the universal tag management system migration"""
    db_path = get_database_path()
    print(f"🔄 Running Migration 042: Universal Tag Management System")
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