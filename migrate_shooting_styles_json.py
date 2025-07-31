#!/usr/bin/env python3
"""
Migration to convert shooting_style from single value to JSON array
This allows users to select multiple shooting styles
"""
import sqlite3
import json
import sys
from pathlib import Path

# Add arrow_scraper to Python path
sys.path.append(str(Path(__file__).parent / 'arrow_scraper'))

from user_database import UserDatabase

def migrate_shooting_styles():
    """Convert existing shooting_style values to JSON arrays"""
    print("🔧 Migrating shooting_style column to support multiple selections")
    
    # Connect to the user database
    db = UserDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get all users with their current shooting_style
        cursor.execute("SELECT id, shooting_style FROM users")
        users = cursor.fetchall()
        
        print(f"📊 Found {len(users)} users to migrate")
        
        # Convert each user's shooting_style to a JSON array
        for user in users:
            user_id = user['id']
            current_style = user['shooting_style'] or 'target'
            
            # Convert single value to array
            if current_style and not current_style.startswith('['):
                # It's a single value, convert to array
                styles_array = [current_style]
                styles_json = json.dumps(styles_array)
                
                cursor.execute(
                    "UPDATE users SET shooting_style = ? WHERE id = ?",
                    (styles_json, user_id)
                )
                print(f"  • User {user_id}: '{current_style}' → {styles_json}")
            elif current_style and current_style.startswith('['):
                # Already a JSON array, skip
                print(f"  • User {user_id}: Already migrated")
            else:
                # No style set, default to ['target']
                styles_json = json.dumps(['target'])
                cursor.execute(
                    "UPDATE users SET shooting_style = ? WHERE id = ?",
                    (styles_json, user_id)
                )
                print(f"  • User {user_id}: No style → ['target']")
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully migrated {len(users)} users")
        
        # Verify migration
        cursor.execute("SELECT id, email, shooting_style FROM users LIMIT 5")
        sample_users = cursor.fetchall()
        print("\n📋 Sample migrated data:")
        for user in sample_users:
            print(f"  • {user['email']}: {user['shooting_style']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    db = UserDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Test that we can parse the JSON values
        cursor.execute("SELECT id, email, shooting_style FROM users")
        users = cursor.fetchall()
        
        valid_count = 0
        for user in users:
            try:
                styles = json.loads(user['shooting_style'])
                if isinstance(styles, list):
                    valid_count += 1
                else:
                    print(f"  ⚠️ User {user['email']} has invalid format: {user['shooting_style']}")
            except:
                print(f"  ❌ User {user['email']} has unparseable data: {user['shooting_style']}")
        
        print(f"✅ {valid_count}/{len(users)} users have valid JSON array format")
        return valid_count == len(users)
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting shooting_style migration to JSON array format...")
    
    # Run the migration
    if migrate_shooting_styles():
        # Verify the migration worked
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("✅ Users can now select multiple shooting styles")
        else:
            print("\n⚠️ Migration completed but verification failed")
            sys.exit(1)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)