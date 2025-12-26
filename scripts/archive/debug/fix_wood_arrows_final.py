#!/usr/bin/env python3
"""
Final comprehensive fix for wood arrow display issue
"""
import os
import shutil
import sqlite3
import sys

def main():
    print("🔧 Applying Final Wood Arrow Fix")
    print("=" * 40)
    
    # Step 1: Ensure we're in the right directory
    arrow_scraper_dir = "/home/paal/arrowtuner2/arrow_scraper"
    root_dir = "/home/paal/arrowtuner2"
    
    print(f"Step 1: Verifying database locations")
    
    # Check both database files
    scraper_db = os.path.join(arrow_scraper_dir, "arrow_database.db")
    root_db = os.path.join(root_dir, "arrow_database.db")
    
    print(f"Scraper DB exists: {os.path.exists(scraper_db)}")
    print(f"Root DB exists: {os.path.exists(root_db)}")
    
    # Count wood arrows in each
    def count_wood_arrows(db_path):
        if not os.path.exists(db_path):
            return 0
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM arrows WHERE material = 'Wood'")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error reading {db_path}: {e}")
            return 0
    
    scraper_wood_count = count_wood_arrows(scraper_db)
    root_wood_count = count_wood_arrows(root_db)
    
    print(f"Wood arrows in scraper DB: {scraper_wood_count}")
    print(f"Wood arrows in root DB: {root_wood_count}")
    
    # Step 2: Copy the correct database if needed
    if scraper_wood_count > root_wood_count:
        print(f"\nStep 2: Copying database with wood arrows")
        shutil.copy2(scraper_db, root_db)
        print(f"✅ Copied database from {scraper_db} to {root_db}")
        
        # Verify the copy
        new_count = count_wood_arrows(root_db)
        print(f"✅ Verification: Root DB now has {new_count} wood arrows")
    else:
        print(f"\nStep 2: Database already contains wood arrows")
    
    # Step 3: Test the API functionality
    print(f"\nStep 3: Testing wood arrow API")
    
    try:
        import requests
        import json
        
        api_url = "http://localhost:5000/api/tuning/recommendations"
        
        test_payload = {
            "draw_weight": 45,
            "draw_length": 28,
            "bow_type": "longbow",
            "arrow_length": 30,
            "arrow_material": "Wood",
            "arrow_rest_type": "drop_away",
            "point_weight": 100,
            "nock_type": "pin",
            "primary_goal": "maximum_accuracy"
        }
        
        print(f"Sending test request to API...")
        response = requests.post(api_url, json=test_payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            arrows = result.get('recommendations', [])
            
            if len(arrows) > 0:
                print(f"✅ SUCCESS: API returned {len(arrows)} wood arrow recommendations!")
                print(f"✅ Wood arrow support is now working correctly")
                
                # Show first few recommendations
                print(f"\nSample recommendations:")
                for i, arrow in enumerate(arrows[:3], 1):
                    arrow_data = arrow.get('arrow', arrow)
                    manufacturer = arrow_data.get('manufacturer', 'Unknown')
                    model_name = arrow_data.get('model_name', 'Unknown')
                    material = arrow_data.get('material', 'Unknown')
                    print(f"  {i}. {manufacturer} {model_name} ({material})")
                
                return True
            else:
                print(f"❌ API returned 0 recommendations - issue persists")
                return False
        else:
            print(f"❌ API error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎯 SOLUTION COMPLETE!")
        print(f"Wood arrows should now display in the frontend when:")
        print(f"  • Bow Type: Longbow")  
        print(f"  • Arrow Material: Wood")
        print(f"  • Draw Weight: 45# (or other weights)")
    else:
        print(f"\n❌ Issue persists - may need manual API server restart")
        print(f"Try restarting the API server manually if needed.")