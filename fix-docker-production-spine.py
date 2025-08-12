#!/usr/bin/env python3
"""
Docker Production Spine Data Fix Script
Imports spine calculator data directly into running Docker container databases
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_docker_command(container_name, command):
    """Run a command inside a Docker container"""
    try:
        result = subprocess.run([
            'docker', 'exec', '-i', container_name
        ] + command, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return None, e.stderr

def find_api_container():
    """Find the API container name"""
    try:
        result = subprocess.run([
            'docker', 'ps', '--format', '{{.Names}}'
        ], capture_output=True, text=True, check=True)
        
        containers = result.stdout.strip().split('\n')
        
        # Look for API container patterns
        api_patterns = ['api', 'arrowtuner-api', 'archerytools-api', 'arrow-api']
        
        for container in containers:
            for pattern in api_patterns:
                if pattern in container.lower():
                    return container
        
        # If no specific API container found, return the first container
        if containers and containers[0]:
            return containers[0]
            
        return None
        
    except subprocess.CalledProcessError:
        return None

def check_container_database(container_name):
    """Check the database inside the container"""
    print(f"🔍 Checking database in container: {container_name}")
    
    # Check if database exists and get info
    stdout, stderr = run_docker_command(container_name, [
        'python3', '-c', '''
import sqlite3
import os
import json

try:
    db_path = "/app/databases/arrow_database.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get arrow count
        cursor.execute("SELECT COUNT(*) FROM arrows")
        arrow_count = cursor.fetchone()[0]
        
        # Check for spine tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%spine%'")
        spine_tables = [row[0] for row in cursor.fetchall()]
        
        # Check enhanced table specifically
        has_enhanced = "manufacturer_spine_charts_enhanced" in spine_tables
        enhanced_count = 0
        
        if has_enhanced:
            cursor.execute("SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced")
            enhanced_count = cursor.fetchone()[0]
        
        conn.close()
        
        result = {
            "exists": True,
            "path": db_path,
            "arrow_count": arrow_count,
            "spine_tables": spine_tables,
            "has_enhanced": has_enhanced,
            "enhanced_count": enhanced_count
        }
    else:
        result = {"exists": False, "path": db_path}
    
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))
'''
    ])
    
    if stdout:
        try:
            return json.loads(stdout.strip())
        except json.JSONDecodeError:
            print(f"❌ Error parsing container database info: {stdout}")
            return None
    
    print(f"❌ Error checking container database: {stderr}")
    return None

def copy_spine_data_to_container(container_name):
    """Copy spine calculator data files to container"""
    print("📁 Copying spine calculator data to container...")
    
    try:
        # Copy the spinecalculatordata directory to container
        subprocess.run([
            'docker', 'cp', 
            './arrow_scraper/spinecalculatordata',
            f'{container_name}:/app/spinecalculatordata'
        ], check=True)
        
        # Copy the importer script to container
        subprocess.run([
            'docker', 'cp',
            './arrow_scraper/spine_calculator_data_importer.py',
            f'{container_name}:/app/spine_calculator_data_importer.py'
        ], check=True)
        
        print("✅ Data files copied to container")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error copying files to container: {e}")
        return False

def run_spine_import_in_container(container_name):
    """Run spine calculator import inside the container"""
    print("🎯 Running spine calculator import in container...")
    
    stdout, stderr = run_docker_command(container_name, [
        'python3', '/app/spine_calculator_data_importer.py'
    ])
    
    if stdout:
        print("✅ Spine import completed!")
        print(stdout)
        return True
    else:
        print("❌ Spine import failed!")
        print(f"Error: {stderr}")
        return False

def main():
    print("🐳 Docker Production Spine Data Fix")
    print("=" * 40)
    
    # Find API container
    container_name = find_api_container()
    if not container_name:
        print("❌ Could not find API container!")
        print("Run 'docker ps' to see running containers")
        sys.exit(1)
    
    print(f"✅ Found API container: {container_name}")
    
    # Check container database
    db_info = check_container_database(container_name)
    if not db_info:
        print("❌ Could not check container database")
        sys.exit(1)
    
    if not db_info.get("exists", False):
        print("❌ Database not found in container at /app/databases/arrow_database.db")
        sys.exit(1)
    
    print(f"📊 Container database info:")
    print(f"   Arrows: {db_info.get('arrow_count', 0)}")
    print(f"   Spine tables: {len(db_info.get('spine_tables', []))}")
    print(f"   Enhanced spine table: {'✅' if db_info.get('has_enhanced', False) else '❌'}")
    
    if db_info.get('has_enhanced', False) and db_info.get('enhanced_count', 0) > 0:
        print("✅ Container already has spine data!")
        print("The API should work correctly now. Try refreshing your browser.")
        return
    
    # Copy files to container
    if not copy_spine_data_to_container(container_name):
        sys.exit(1)
    
    # Run import in container
    if not run_spine_import_in_container(container_name):
        sys.exit(1)
    
    # Verify import
    print("\n🔍 Verifying import...")
    db_info_after = check_container_database(container_name)
    if db_info_after and db_info_after.get('enhanced_count', 0) > 0:
        print(f"✅ SUCCESS! {db_info_after['enhanced_count']} spine charts imported to container database")
        print("\n🎯 Your production spine chart system should now work!")
        print("Refresh your browser and try accessing the admin spine charts.")
    else:
        print("❌ Import verification failed")

if __name__ == "__main__":
    main()