"""
Migration 039: Add Active Bow Setup Support
Adds active_bow_setup_id to users table for tracking user's currently active setup
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

def upgrade(db_path):
    """Add active_bow_setup_id to users table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Migration 039: Adding active bow setup support")
        
        # Add active_bow_setup_id column to users table
        try:
            cursor.execute("""
                ALTER TABLE users ADD COLUMN active_bow_setup_id INTEGER
                REFERENCES bow_setups(id) ON DELETE SET NULL
            """)
            logger.info("✅ Added active_bow_setup_id column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logger.info("✅ active_bow_setup_id column already exists")
            else:
                raise e
        
        # Create index for better performance
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_active_bow_setup
                ON users(active_bow_setup_id)
            """)
            logger.info("✅ Created index for active_bow_setup_id")
        except Exception as e:
            logger.warning(f"Failed to create index: {e}")
        
        conn.commit()
        logger.info("✅ Migration 039 completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration 039 failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise e
    finally:
        if 'conn' in locals():
            conn.close()

def downgrade(db_path):
    """Remove active_bow_setup_id from users table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Migration 039: Downgrading active bow setup support")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        # For now, just log that downgrade is not supported
        logger.warning("Downgrade not supported for this migration - column will remain")
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration 039 downgrade failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise e
    finally:
        if 'conn' in locals():
            conn.close()