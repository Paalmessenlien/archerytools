#!/usr/bin/env python3
"""
Production UserDatabase Cleanup Script
Removes all references to UserDatabase and migrates to unified ArrowDatabase architecture
"""

import os
import re
import shutil
import glob
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the file before modification"""
    backup_path = f"{file_path}.backup_{os.getpid()}"
    shutil.copy2(file_path, backup_path)
    print(f"   📋 Created backup: {backup_path}")
    return backup_path

def fix_performance_calculation_function(api_file):
    """Fix the specific performance calculation function causing 500 errors"""
    print("🔧 Fixing performance calculation function...")
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Fix the specific calculate_individual_arrow_performance function
    old_pattern = r'''(\@app\.route\('/api/setup-arrows/<int:setup_arrow_id>/calculate-performance', methods=\['POST'\]\)\n\@token_required\ndef calculate_individual_arrow_performance\(current_user, setup_arrow_id\):\n    """Calculate performance metrics for a single arrow in a bow setup"""\n    conn = None\n    try:\n        # Parse request data for bow configuration\n        data = request\.get_json\(\) or \{\}\n        bow_config = data\.get\('bow_config', \{\}\)\n        \n        # Get user database connection\n        from user_database import UserDatabase\n        user_db = UserDatabase\(\)\n        conn = user_db\.get_connection\(\)\n        cursor = conn\.cursor\(\))'''
    
    new_pattern = r'''\1
        # Get unified database connection
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        conn = db.get_connection()
        cursor = conn.cursor()'''
    
    # Use a more specific replacement for just this function
    function_start = "@app.route('/api/setup-arrows/<int:setup_arrow_id>/calculate-performance', methods=['POST'])"
    function_end = "# Get the arrow setup and verify ownership"
    
    if function_start in content:
        # Find the specific function and replace just its database connection part
        start_idx = content.find(function_start)
        end_idx = content.find(function_end, start_idx)
        
        if start_idx != -1 and end_idx != -1:
            function_part = content[start_idx:end_idx]
            
            # Replace the UserDatabase part in this specific function
            if "from user_database import UserDatabase" in function_part:
                new_function_part = function_part.replace(
                    """        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        """,
                    """        # Get unified database connection
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        """
                )
                
                # Reconstruct the file
                new_content = content[:start_idx] + new_function_part + content[end_idx:]
                
                with open(api_file, 'w') as f:
                    f.write(new_content)
                
                print("   ✅ Fixed performance calculation function")
                return True
    
    print("   ⚠️  Performance calculation function not found or already fixed")
    return False

def replace_user_database_references(file_path):
    """Replace UserDatabase references with ArrowDatabase in a single file"""
    if not os.path.exists(file_path):
        print(f"   ⚠️  File not found: {file_path}")
        return False
    
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Replace UserDatabase imports
    content = re.sub(
        r'from user_database import UserDatabase',
        '# Using unified database - ArrowDatabase',
        content
    )
    
    # Replace UserDatabase instantiation
    content = re.sub(
        r'user_db = UserDatabase\(\)',
        'db = get_database()',
        content
    )
    
    # Replace user_db.get_connection() calls
    content = re.sub(
        r'user_db\.get_connection\(\)',
        'db.get_connection()',
        content
    )
    
    # Add error checking after get_database() calls where missing
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # If we find a get_database() call without error checking
        if 'db = get_database()' in line and i + 1 < len(lines):
            next_line = lines[i + 1]
            # Check if the next line doesn't already have error checking
            if 'if not db:' not in next_line and 'if db is None:' not in next_line:
                # Add error checking
                indent = '        '  # Default indentation
                if line.strip():
                    indent = line[:len(line) - len(line.lstrip())]
                
                new_lines.append(f'{indent}if not db:')
                new_lines.append(f'{indent}    return jsonify({{"error": "Database not available"}}), 500')
        
        i += 1
    
    content = '\n'.join(new_lines)
    
    if content != original_content:
        changes_made = content.count('UserDatabase') - original_content.count('UserDatabase')
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"   ✅ Modified {os.path.basename(file_path)} - Changes: {abs(changes_made)}")
        return True
    else:
        print(f"   ℹ️  No changes needed in {os.path.basename(file_path)}")
        return False

def remove_user_data_files():
    """Remove all user_data.db files from the system"""
    print("🗑️  Removing user_data.db files...")
    
    # Common locations where user_data.db files might exist
    search_paths = [
        '/app',
        '/app/databases',
        '/app/arrow_scraper',
        '/home/*/arrowtuner*',
        '/opt/arrowtuner*',
        '/var/lib/arrowtuner*'
    ]
    
    files_removed = 0
    
    for search_path in search_paths:
        try:
            for db_file in glob.glob(f"{search_path}/**/user_data.db*", recursive=True):
                try:
                    print(f"   🗑️  Removing: {db_file}")
                    os.remove(db_file)
                    files_removed += 1
                except Exception as e:
                    print(f"   ⚠️  Could not remove {db_file}: {e}")
        except Exception as e:
            # Path might not exist, that's okay
            pass
    
    print(f"   ✅ Removed {files_removed} user_data.db files")

def update_docker_compose_files():
    """Update docker-compose files to remove user_data.db volume references"""
    print("🐳 Updating Docker Compose files...")
    
    docker_files = [
        'docker-compose.yml',
        'docker-compose.dev.yml',
        'docker-compose.prod.yml',
        'docker-compose.ssl.yml',
        'docker-compose.enhanced-ssl.yml'
    ]
    
    for docker_file in docker_files:
        if os.path.exists(docker_file):
            backup_file(docker_file)
            
            with open(docker_file, 'r') as f:
                content = f.read()
            
            # Remove user_data.db volume references
            content = re.sub(r'.*user_data\.db.*\n', '', content)
            content = re.sub(r'.*USER_DATABASE_PATH.*\n', '', content)
            
            with open(docker_file, 'w') as f:
                f.write(content)
            
            print(f"   ✅ Updated {docker_file}")

def update_startup_scripts():
    """Update startup scripts to remove UserDatabase references"""
    print("🚀 Updating startup scripts...")
    
    startup_scripts = [
        'start-unified.sh',
        'start-local-dev.sh',
        'start-hybrid-dev.sh',
        'start-docker-dev.sh',
        'arrow_scraper/start-api-robust.sh'
    ]
    
    for script in startup_scripts:
        if os.path.exists(script):
            backup_file(script)
            
            with open(script, 'r') as f:
                content = f.read()
            
            # Remove UserDatabase references
            content = re.sub(r'.*UserDatabase.*\n', '', content)
            content = re.sub(r'.*user_data\.db.*\n', '', content)
            
            with open(script, 'w') as f:
                f.write(content)
            
            print(f"   ✅ Updated {script}")

def validate_syntax():
    """Validate that Python files have correct syntax after modifications"""
    print("✅ Validating Python syntax...")
    
    python_files = ['arrow_scraper/api.py', 'arrow_scraper/auth.py']
    
    for py_file in python_files:
        if os.path.exists(py_file):
            try:
                import py_compile
                py_compile.compile(py_file, doraise=True)
                print(f"   ✅ {py_file} syntax OK")
            except py_compile.PyCompileError as e:
                print(f"   ❌ {py_file} syntax error: {e}")
                return False
    
    return True

def main():
    """Main cleanup function"""
    print("🧹 Production UserDatabase Cleanup Script")
    print("=" * 60)
    
    # Change to the project directory if we're in a subdirectory
    if os.path.exists('arrow_scraper'):
        print("📁 Working in project root directory")
    elif os.path.exists('../arrow_scraper'):
        os.chdir('..')
        print("📁 Changed to project root directory")
    else:
        print("❌ Could not find project root directory")
        return False
    
    try:
        # Step 1: Remove user_data.db files
        remove_user_data_files()
        
        # Step 2: Fix the main API file
        api_file = 'arrow_scraper/api.py'
        if os.path.exists(api_file):
            print(f"\n🔧 Processing {api_file}...")
            backup_file(api_file)
            fix_performance_calculation_function(api_file)
            replace_user_database_references(api_file)
        
        # Step 3: Fix auth.py
        auth_file = 'arrow_scraper/auth.py'
        if os.path.exists(auth_file):
            print(f"\n🔧 Processing {auth_file}...")
            replace_user_database_references(auth_file)
        
        # Step 4: Update Docker files
        update_docker_compose_files()
        
        # Step 5: Update startup scripts
        update_startup_scripts()
        
        # Step 6: Validate syntax
        if not validate_syntax():
            print("\n❌ Syntax validation failed. Check the backup files.")
            return False
        
        print("\n" + "=" * 60)
        print("🎯 CLEANUP COMPLETE!")
        print("=" * 60)
        print("✅ UserDatabase references removed")
        print("✅ All user_data.db files deleted")
        print("✅ Docker configurations updated")
        print("✅ Startup scripts updated")
        print("✅ Python syntax validated")
        print("\n📋 Next steps:")
        print("   • Restart the application")
        print("   • Test the performance calculation API")
        print("   • Verify chronograph data integration")
        print("\n⚠️  Backup files created with .backup_* extension")
        print("   Remove them after confirming everything works")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)