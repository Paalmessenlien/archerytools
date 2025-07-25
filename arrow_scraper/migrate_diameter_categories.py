#!/usr/bin/env python3
"""
Migration script to add diameter categories to existing arrow specifications
"""

import sqlite3
from pathlib import Path
from models import classify_diameter, DiameterCategory

def migrate_diameter_categories(db_path: str = "arrow_database.db"):
    """Add diameter categories to existing spine specifications"""
    
    print(f"🔄 Migrating diameter categories in {db_path}")
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # First, add the diameter_category column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE spine_specifications ADD COLUMN diameter_category TEXT')
            print("✅ Added diameter_category column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  diameter_category column already exists")
            else:
                raise e
        
        # Get all spine specifications that need diameter categories
        cursor.execute('''
        SELECT id, outer_diameter, inner_diameter, diameter_category
        FROM spine_specifications 
        WHERE outer_diameter IS NOT NULL
        ''')
        
        specs = cursor.fetchall()
        print(f"📊 Found {len(specs)} spine specifications to process")
        
        updated_count = 0
        category_counts = {}
        
        for spec in specs:
            spec_id = spec['id']
            outer_diameter = spec['outer_diameter']
            inner_diameter = spec['inner_diameter']
            current_category = spec['diameter_category']
            
            # Use inner diameter if available, otherwise outer diameter
            effective_diameter = inner_diameter or outer_diameter
            
            # Calculate diameter category
            diameter_category = classify_diameter(effective_diameter)
            
            # Count categories for reporting
            if diameter_category.value not in category_counts:
                category_counts[diameter_category.value] = 0
            category_counts[diameter_category.value] += 1
            
            # Update if category is different or missing
            if current_category != diameter_category.value:
                cursor.execute('''
                UPDATE spine_specifications 
                SET diameter_category = ? 
                WHERE id = ?
                ''', (diameter_category.value, spec_id))
                updated_count += 1
        
        # Add index for diameter_category if it doesn't exist
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spine_diameter_category ON spine_specifications (diameter_category)')
            print("✅ Added diameter_category index")
        except sqlite3.OperationalError:
            print("ℹ️  diameter_category index already exists")
        
        conn.commit()
        
        print(f"✅ Migration complete!")
        print(f"📈 Updated {updated_count} specifications")
        print(f"📊 Diameter category distribution:")
        
        # Create human-readable labels
        category_labels = {
            'ultra_thin': 'Ultra-thin (.166")',
            'thin': 'Thin (.204")',
            'small_hunting': 'Small hunting (.244")',
            'standard_target': 'Standard target (.246")',
            'standard_hunting': 'Standard hunting (.300")',
            'large_hunting': 'Large hunting (.340")',
            'heavy_hunting': 'Heavy hunting (.400"+)'
        }
        
        for category, count in sorted(category_counts.items()):
            label = category_labels.get(category, category)
            print(f"   {label}: {count} specifications")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_migration(db_path: str = "arrow_database.db"):
    """Verify the migration was successful"""
    
    print(f"\n🔍 Verifying migration in {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(spine_specifications)")
        columns = [row['name'] for row in cursor.fetchall()]
        
        if 'diameter_category' not in columns:
            print("❌ diameter_category column not found")
            return False
        
        # Check data distribution
        cursor.execute('''
        SELECT 
            diameter_category,
            COUNT(*) as count,
            MIN(outer_diameter) as min_diameter,
            MAX(outer_diameter) as max_diameter
        FROM spine_specifications 
        WHERE diameter_category IS NOT NULL 
        GROUP BY diameter_category 
        ORDER BY MIN(outer_diameter)
        ''')
        
        results = cursor.fetchall()
        
        if not results:
            print("❌ No diameter categories found")
            return False
        
        print("✅ Diameter categories successfully applied:")
        for row in results:
            print(f"   {row['diameter_category']}: {row['count']} specs "
                  f"(diameter range: {row['min_diameter']:.3f}\" - {row['max_diameter']:.3f}\")")
        
        # Check for any missing categories
        cursor.execute('''
        SELECT COUNT(*) as missing_count
        FROM spine_specifications 
        WHERE outer_diameter IS NOT NULL AND diameter_category IS NULL
        ''')
        
        missing = cursor.fetchone()['missing_count']
        if missing > 0:
            print(f"⚠️  {missing} specifications still missing diameter categories")
        else:
            print("✅ All specifications have diameter categories")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🎯 Arrow Database Diameter Category Migration")
    print("=" * 50)
    
    # Run migration
    success = migrate_diameter_categories()
    
    if success:
        # Verify migration
        verify_migration()
        print("\n🎉 Migration completed successfully!")
        print("\nDiameter categories are now available for:")
        print("- Database statistics and filtering")
        print("- API endpoints with category breakdown")
        print("- Enhanced arrow recommendation matching")
    else:
        print("\n❌ Migration failed. Please check the errors above.")