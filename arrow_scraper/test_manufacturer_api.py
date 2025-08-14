#!/usr/bin/env python3
"""
Test script for manufacturer API endpoints
Tests the manufacturer suggestions and status functionality without needing a running server
"""

import json
import sys
import os

# Add arrow_scraper to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_manufacturer_suggestions():
    """Test manufacturer suggestions logic"""
    print("🧪 Testing manufacturer suggestions logic...")
    
    try:
        # Test basic imports
        from arrow_database import ArrowDatabase
        from user_database import UserDatabase
        
        # Simulate the suggestions API logic
        query = "hoy"
        category = "compound_bows"
        limit = 5
        
        suggestions = []
        
        # Test arrow database connection
        try:
            db = ArrowDatabase()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Test manufacturer query (similar to API endpoint)
            cursor.execute('''
                SELECT DISTINCT m.name, mec.category_name
                FROM manufacturers m
                LEFT JOIN manufacturer_equipment_categories mec ON m.id = mec.manufacturer_id
                WHERE m.is_active = 1 
                AND LOWER(m.name) LIKE LOWER(?)
                AND (mec.category_name = ? OR mec.category_name IS NULL)
                ORDER BY 
                    CASE WHEN LOWER(m.name) = LOWER(?) THEN 0 ELSE 1 END,
                    LENGTH(m.name),
                    m.name
                LIMIT ?
            ''', (f'%{query}%', category, query, limit))
            
            results = cursor.fetchall()
            print(f"✅ Arrow database query successful: Found {len(results)} results")
            for row in results:
                print(f"  - {row['name']} (category: {row['category_name']})")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Arrow database query failed: {e}")
        
        # Test user database connection
        try:
            user_db = UserDatabase()
            user_conn = user_db.get_connection()
            user_cursor = user_conn.cursor()
            
            # Test pending manufacturers query
            user_cursor.execute('''
                SELECT name, usage_count, category_context
                FROM pending_manufacturers
                WHERE status = 'pending'
                AND LOWER(name) LIKE LOWER(?)
                ORDER BY usage_count DESC
                LIMIT ?
            ''', (f'%{query}%', limit))
            
            pending_results = user_cursor.fetchall()
            print(f"✅ User database query successful: Found {len(pending_results)} pending manufacturers")
            for row in pending_results:
                categories = json.loads(row['category_context'] or '[]')
                print(f"  - {row['name']} (usage: {row['usage_count']}, categories: {categories})")
            
            user_conn.close()
            
        except Exception as e:
            print(f"⚠️ User database query failed: {e}")
        
        print("✅ Manufacturer suggestions logic test completed\n")
        
    except Exception as e:
        print(f"❌ Manufacturer suggestions test failed: {e}\n")

def test_manufacturer_status():
    """Test manufacturer status logic"""
    print("🧪 Testing manufacturer status logic...")
    
    try:
        # Test with known manufacturer
        test_name = "Hoyt"
        test_category = "compound_bows"
        
        # Test arrow database lookup
        try:
            from arrow_database import ArrowDatabase
            db = ArrowDatabase()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.id, m.name, mec.category_name
                FROM manufacturers m
                LEFT JOIN manufacturer_equipment_categories mec ON m.id = mec.manufacturer_id
                WHERE m.is_active = 1 
                AND LOWER(m.name) = LOWER(?)
                AND (mec.category_name = ? OR ? = '' OR mec.category_name IS NULL)
            ''', (test_name, test_category, test_category))
            
            result = cursor.fetchone()
            
            if result:
                print(f"✅ Found approved manufacturer: {result['name']} (ID: {result['id']}, Category: {result['category_name']})")
                status = 'approved'
            else:
                print("⚠️ Manufacturer not found in approved list")
                status = 'new'
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Arrow database status check failed: {e}")
            status = 'new'
        
        # Test user database lookup for pending
        try:
            from user_database import UserDatabase
            user_db = UserDatabase()
            user_conn = user_db.get_connection()
            user_cursor = user_conn.cursor()
            
            user_cursor.execute('''
                SELECT id, status, category_context, usage_count
                FROM pending_manufacturers
                WHERE LOWER(name) = LOWER(?)
                ORDER BY created_at DESC
                LIMIT 1
            ''', (test_name,))
            
            pending = user_cursor.fetchone()
            
            if pending:
                categories = json.loads(pending['category_context'] or '[]')
                print(f"✅ Found pending manufacturer: {test_name} (Status: {pending['status']}, Categories: {categories})")
            else:
                print("⚠️ No pending manufacturer found")
            
            user_conn.close()
            
        except Exception as e:
            print(f"⚠️ User database pending check failed: {e}")
        
        print(f"✅ Final status for '{test_name}': {status}")
        print("✅ Manufacturer status logic test completed\n")
        
    except Exception as e:
        print(f"❌ Manufacturer status test failed: {e}\n")

def test_equipment_learning_integration():
    """Test equipment learning manager integration"""
    print("🧪 Testing equipment learning integration...")
    
    try:
        from equipment_learning_manager import EquipmentLearningManager
        
        learning = EquipmentLearningManager()
        
        # Test getting pending manufacturers (should work after Phase 2)
        pending = learning.get_pending_manufacturers()
        print(f"✅ Equipment learning integration: Found {len(pending)} pending manufacturers")
        
        # Test learning a new manufacturer
        result = learning.learn_equipment_entry('Test API Manufacturer', 'Test Model', 'String', 1)
        print(f"✅ Learning test result: {result}")
        
        print("✅ Equipment learning integration test completed\n")
        
    except Exception as e:
        print(f"❌ Equipment learning integration test failed: {e}\n")

if __name__ == "__main__":
    print("🔧 Testing Manufacturer API Functionality")
    print("=" * 50)
    
    test_manufacturer_suggestions()
    test_manufacturer_status()
    test_equipment_learning_integration()
    
    print("🎯 All tests completed!")