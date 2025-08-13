#!/usr/bin/env python3
"""
Detailed diagnostic for form schema endpoint issues
"""
import sys
import os
sys.path.append('/home/paal/archerytools/arrow_scraper')

def test_database_connection():
    """Test database connection and table structure"""
    print("🔧 Testing database connection...")
    
    try:
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print(f"✅ Database connection successful")
        print(f"   Database path: {db.db_path}")
        
        # Check if equipment_field_standards table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='equipment_field_standards'
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ equipment_field_standards table exists")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(equipment_field_standards)")
            columns = cursor.fetchall()
            print("   Table columns:")
            for col in columns:
                print(f"     - {col[1]} ({col[2]})")
            
            # Check categories
            cursor.execute("SELECT DISTINCT category_name FROM equipment_field_standards")
            categories = [row[0] for row in cursor.fetchall()]
            print(f"   Available categories: {categories}")
            
            return True, categories
        else:
            print("❌ equipment_field_standards table does not exist")
            return False, []
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False, []

def test_form_schema_function(category):
    """Test the form schema function directly"""
    print(f"🔧 Testing form schema for category: {category}")
    
    try:
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT field_name, field_type, field_label, field_unit, is_required,
                   validation_rules, dropdown_options, default_value, help_text, field_order
            FROM equipment_field_standards 
            WHERE category_name = ?
            ORDER BY field_order, field_name
        ''', (category,))
        
        rows = cursor.fetchall()
        print(f"   Found {len(rows)} fields for {category}")
        
        if rows:
            print("   Fields:")
            for row in rows:
                print(f"     - {row[0]} ({row[1]}): {row[2]}")
            return True
        else:
            print(f"   No fields found for category '{category}'")
            # Let's check if the category exists with different casing
            cursor.execute("SELECT DISTINCT category_name FROM equipment_field_standards WHERE LOWER(category_name) LIKE ?", (f"%{category.lower()}%",))
            similar = cursor.fetchall()
            if similar:
                print(f"   Similar categories found: {[s[0] for s in similar]}")
            return False
            
    except Exception as e:
        print(f"❌ Form schema function failed for {category}: {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint directly"""
    print("🔧 Testing API endpoint directly...")
    
    try:
        import requests
        
        test_categories = ["String", "Sight", "Stabilizer"]
        
        for category in test_categories:
            url = f"http://localhost:5000/api/equipment/form-schema/{category}"
            print(f"   Testing: {url}")
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    field_count = len(data.get('fields', []))
                    print(f"   ✅ {category}: {field_count} fields")
                else:
                    print(f"   ❌ {category}: HTTP {response.status_code}")
                    print(f"      Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {category}: Request failed - {e}")
                
    except ImportError:
        print("   ⚠️  requests library not available, skipping API test")

if __name__ == "__main__":
    print("🧪 Equipment Form Schema Diagnostic")
    print("=" * 50)
    
    # Test database connection
    db_ok, categories = test_database_connection()
    
    if db_ok and categories:
        print(f"\n📋 Testing form schema for each category:")
        for category in categories:
            test_form_schema_function(category)
    
    print(f"\n🌐 Testing API endpoints:")
    test_api_endpoint()
    
    print("\n" + "=" * 50)
    if db_ok:
        print("🎉 Database connection and table structure look good!")
        print("The issue might be:")
        print("1. Authentication/CORS issue in production")
        print("2. Different database path in production")
        print("3. Missing data in production database")
        print("\nRecommended actions:")
        print("- Check production database has equipment_field_standards table")
        print("- Verify production API endpoint authentication requirements")
        print("- Check production logs for specific error details")
    else:
        print("⚠️  Database issues found - fix database connection first")