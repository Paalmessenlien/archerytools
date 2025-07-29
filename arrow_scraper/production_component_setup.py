#!/usr/bin/env python3
"""
Production Component Database Setup
Run this on production server to populate component database
"""

import os
import sys
from pathlib import Path

def setup_production_components():
    """Set up component database for production deployment"""
    print("🚀 Production Component Database Setup")
    print("=" * 50)
    
    # Import after adding current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from component_database import ComponentDatabase
        from populate_components import populate_component_database
        
        # Initialize component database
        print("🗄️  Initializing component database...")
        db = ComponentDatabase()
        
        # Check current state
        stats = db.get_component_statistics()
        current_total = stats.get('total_components', 0)
        
        print(f"📊 Current components in database: {current_total}")
        
        if current_total < 30:  # Threshold for considering database "empty"
            print("🔄 Database appears empty, populating with components...")
            stats = populate_component_database()
        else:
            print("✅ Database already contains components")
            print("📋 Current breakdown:")
            for category in stats.get('categories', []):
                print(f"   {category['name']}: {category['count']} components")
        
        print(f"\n🎯 Component database ready for production!")
        print(f"   Total components: {stats['total_components']}")
        print(f"   Categories: {len(stats['categories'])}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure you're running from the arrow_scraper directory")
        return False
    except Exception as e:
        print(f"❌ Error setting up components: {e}")
        return False

if __name__ == "__main__":
    success = setup_production_components()
    sys.exit(0 if success else 1)