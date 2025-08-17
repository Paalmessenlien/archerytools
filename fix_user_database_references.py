#!/usr/bin/env python3
"""
Script to replace all UserDatabase references with unified ArrowDatabase references
"""

import re
import os

def fix_api_file():
    """Fix all UserDatabase references in api.py"""
    api_file = '/home/paal/arrowtuner2/arrow_scraper/api.py'
    
    print("🔧 Fixing UserDatabase references in api.py...")
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Pattern to match UserDatabase import and usage blocks
    pattern = r'        from user_database import UserDatabase\n        user_db = UserDatabase\(\)\n        conn = user_db\.get_connection\(\)\n        cursor = conn\.cursor\(\)'
    
    replacement = '''        # Get unified database connection
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        conn = db.get_connection()
        cursor = conn.cursor()'''
    
    # Replace all occurrences
    new_content = re.sub(pattern, replacement, content)
    
    # Also handle variations with different spacing
    pattern2 = r'from user_database import UserDatabase\n\s*user_db = UserDatabase\(\)'
    replacement2 = '''# Using unified database - get_database() function'''
    
    new_content = re.sub(pattern2, replacement2, new_content)
    
    # Handle specific UserDatabase().get_connection() calls
    pattern3 = r'UserDatabase\(\)\.get_connection\(\)'
    replacement3 = 'get_database().get_connection()'
    
    new_content = re.sub(pattern3, replacement3, new_content)
    
    # Handle user_db.get_connection() calls
    pattern4 = r'user_db\.get_connection\(\)'
    replacement4 = 'get_database().get_connection()'
    
    new_content = re.sub(pattern4, replacement4, new_content)
    
    # Count changes
    changes = content.count('from user_database import UserDatabase') - new_content.count('from user_database import UserDatabase')
    
    with open(api_file, 'w') as f:
        f.write(new_content)
    
    print(f"   ✅ Replaced {changes} UserDatabase references")
    return changes

def fix_auth_file():
    """Fix UserDatabase references in auth.py"""
    auth_file = '/home/paal/arrowtuner2/arrow_scraper/auth.py'
    
    print("🔧 Fixing UserDatabase references in auth.py...")
    
    with open(auth_file, 'r') as f:
        content = f.read()
    
    # Replace UserDatabase with ArrowDatabase
    new_content = content.replace('from user_database import UserDatabase', 'from arrow_database import ArrowDatabase')
    new_content = new_content.replace('user_db = UserDatabase()', 'user_db = ArrowDatabase()')
    new_content = new_content.replace('UserDatabase()', 'ArrowDatabase()')
    
    changes = content.count('UserDatabase') - new_content.count('UserDatabase')
    
    with open(auth_file, 'w') as f:
        f.write(new_content)
    
    print(f"   ✅ Replaced {changes} UserDatabase references")
    return changes

if __name__ == "__main__":
    print("🚀 Starting UserDatabase to ArrowDatabase migration...")
    print("=" * 60)
    
    total_changes = 0
    total_changes += fix_api_file()
    total_changes += fix_auth_file()
    
    print("=" * 60)
    print(f"🎯 Migration complete! Total changes: {total_changes}")
    print("💡 Note: Some files may still need manual review for complex patterns")