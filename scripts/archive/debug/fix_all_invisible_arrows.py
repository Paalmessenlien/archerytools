#!/usr/bin/env python3
"""
Bulk fix for all invisible arrow search visibility issues
Fixes all arrows that have missing description or arrow_type fields
"""

import sqlite3
import sys
import os
from pathlib import Path

def fix_all_invisible_arrows():
    """Fix all arrows with search visibility issues in bulk"""
    
    # Use the unified database path
    db_path = os.environ.get('ARROW_DATABASE_PATH', './arrow_scraper/databases/arrow_database.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Finding arrows with search visibility issues...")
        
        # Find arrows with missing description or arrow_type
        cursor.execute("""
            SELECT id, manufacturer, model_name, description, arrow_type 
            FROM arrows 
            WHERE description IS NULL 
               OR description = '' 
               OR arrow_type IS NULL 
               OR arrow_type = ''
        """)
        
        invisible_arrows = cursor.fetchall()
        
        if not invisible_arrows:
            print("✅ No invisible arrows found - all arrows have proper search visibility")
            return True
        
        print(f"📋 Found {len(invisible_arrows)} arrows with search visibility issues")
        
        # Bulk fix for missing descriptions
        print("🔧 Fixing missing descriptions...")
        cursor.execute("""
            UPDATE arrows 
            SET description = COALESCE(
                NULLIF(description, ''), 
                manufacturer || ' ' || model_name || ' - High quality arrow'
            )
            WHERE description IS NULL OR description = ''
        """)
        
        description_fixes = cursor.rowcount
        print(f"✅ Fixed descriptions for {description_fixes} arrows")
        
        # Bulk fix for missing arrow_type  
        print("🔧 Fixing missing arrow types...")
        cursor.execute("""
            UPDATE arrows 
            SET arrow_type = CASE
                WHEN model_name LIKE '%target%' OR model_name LIKE '%Target%' THEN 'target'
                WHEN model_name LIKE '%hunt%' OR model_name LIKE '%Hunt%' THEN 'hunting'
                WHEN model_name LIKE '%3D%' OR model_name LIKE '%field%' THEN 'field'
                WHEN model_name LIKE '%trad%' OR model_name LIKE '%traditional%' THEN 'traditional'
                ELSE 'target'
            END
            WHERE arrow_type IS NULL OR arrow_type = ''
        """)
        
        type_fixes = cursor.rowcount
        print(f"✅ Fixed arrow types for {type_fixes} arrows")
        
        # Commit the changes
        conn.commit()
        
        total_fixes = description_fixes + type_fixes
        print(f"🎯 Successfully fixed search visibility for {total_fixes} total field updates")
        print("✅ All arrows should now be visible in search results")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting bulk fix for invisible arrows...")
    success = fix_all_invisible_arrows()
    
    if success:
        print("\n🎉 Bulk fix completed successfully!")
        print("💡 You can now re-run validation to verify all issues are resolved")
    else:
        print("\n❌ Bulk fix failed - check error messages above")
        sys.exit(1)