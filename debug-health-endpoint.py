#!/usr/bin/env python3
"""
Debug the database health endpoint to find the exact serialization issue
"""

import sys
import os
sys.path.append('/home/paal/archerytools/arrow_scraper')

try:
    from database_health_checker import run_health_check
    import json
    from pathlib import Path
    
    print("🔍 Testing Database Health Checker")
    print("=" * 50)
    
    # Test the health check function directly
    try:
        health_report = run_health_check()
        print("✅ Health check completed successfully")
        print("📊 Report keys:", list(health_report.keys()))
        
        # Try to find the problematic data
        def find_path_objects(obj, path=""):
            """Recursively find Path objects that can't be serialized"""
            if hasattr(obj, '__fspath__') or str(type(obj)).find('Path') != -1:
                print(f"🚨 Found Path object at {path}: {obj} (type: {type(obj)})")
                return True
            elif isinstance(obj, dict):
                found = False
                for key, value in obj.items():
                    if find_path_objects(value, f"{path}.{key}"):
                        found = True
                return found
            elif isinstance(obj, list):
                found = False
                for i, item in enumerate(obj):
                    if find_path_objects(item, f"{path}[{i}]"):
                        found = True
                return found
            return False
        
        print("\n🔍 Scanning for Path objects...")
        has_paths = find_path_objects(health_report)
        
        if not has_paths:
            print("✅ No Path objects found")
        
        # Try JSON serialization
        print("\n🧪 Testing JSON serialization...")
        try:
            json_str = json.dumps(health_report)
            print("✅ JSON serialization successful")
        except Exception as e:
            print(f"❌ JSON serialization failed: {e}")
            print(f"   Error type: {type(e)}")
            
            # Try to identify the exact problematic field
            for key, value in health_report.items():
                try:
                    json.dumps(value)
                    print(f"✅ {key}: OK")
                except Exception as field_error:
                    print(f"❌ {key}: {field_error}")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory")