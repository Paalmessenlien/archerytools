#!/usr/bin/env python3
"""
Test Component Workflow - Demonstrates the new component JSON export and import functionality
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

def create_sample_component_data():
    """Create sample component data for testing"""
    return {
        "manufacturer": "Easton Archery",
        "component_type": "points",
        "total_components": 3,
        "scraped_at": datetime.now().isoformat(),
        "source_url": "https://example.com/points",
        "components": [
            {
                "manufacturer": "Easton Archery",
                "model_name": "G-Nock",
                "component_type": "points",
                "specifications": {
                    "weight": "100gr",
                    "thread_type": "8-32",
                    "diameter": 0.246,
                    "material": "brass"
                },
                "description": "Premium field point for target shooting",
                "price_range": "$2-4",
                "scraped_at": datetime.now().isoformat()
            },
            {
                "manufacturer": "Easton Archery", 
                "model_name": "Super Nock",
                "component_type": "nocks",
                "specifications": {
                    "throat_size": "0.236",
                    "color": "blue",
                    "material": "polycarbonate"
                },
                "description": "High-performance target nock",
                "price_range": "$1-2",
                "scraped_at": datetime.now().isoformat()
            },
            {
                "manufacturer": "Easton Archery",
                "model_name": "X-Vanes",
                "component_type": "fletchings", 
                "specifications": {
                    "length": "2.3in",
                    "height": "0.3in",
                    "material": "plastic",
                    "color": "white"
                },
                "description": "Low-profile target vanes",
                "price_range": "$8-12",
                "scraped_at": datetime.now().isoformat()
            }
        ]
    }

def test_component_workflow():
    """Test the complete component workflow"""
    
    print("🧪 Testing Component Data Workflow")
    print("=" * 50)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        components_dir = temp_path / "data" / "processed" / "components"
        components_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Created test directory: {components_dir}")
        
        # 1. Test JSON export (simulating scraper output)
        print("\n1️⃣ Testing JSON Export...")
        sample_data = create_sample_component_data()
        
        json_file = components_dir / "Easton_Archery_points.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Created: {json_file.name}")
        print(f"   📊 Components: {sample_data['total_components']}")
        print(f"   🏭 Manufacturer: {sample_data['manufacturer']}")
        print(f"   🧩 Type: {sample_data['component_type']}")
        
        # 2. Test component import
        print("\n2️⃣ Testing Component Import...")
        
        # Create test database
        test_db = temp_path / "test_components.db"
        
        try:
            # Import the component_importer module
            from component_importer import ComponentImporter
            
            # Create importer with test database
            importer = ComponentImporter(str(test_db))
            
            # Override the processed directory for testing
            importer.processed_dir = components_dir
            
            # Import components
            success = importer.import_all_components(force_rebuild=True)
            
            if success:
                print("   ✅ Component import successful!")
                
                # Verify import
                from component_database import ComponentDatabase
                comp_db = ComponentDatabase(str(test_db))
                
                # Get component statistics
                stats = comp_db.get_component_statistics()
                print(f"   📊 Database contains:")
                print(f"      • Total components: {stats.get('total_components', 0)}")
                print(f"      • Categories: {stats.get('total_categories', 0)}")
                print(f"      • Manufacturers: {stats.get('total_manufacturers', 0)}")
                
                # Get specific components
                points = comp_db.get_components(category_name="points")
                print(f"      • Points found: {len(points)}")
                
                if points:
                    point = points[0]
                    print(f"      • Sample point: {point['manufacturer']} {point['model_name']}")
                
            else:
                print("   ❌ Component import failed")
                
        except Exception as e:
            print(f"   ❌ Import error: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Show file structure
        print("\n3️⃣ Component Data Structure:")
        print(f"   📁 {components_dir.relative_to(temp_path)}/")
        for json_file in components_dir.glob("*.json"):
            print(f"      📄 {json_file.name}")
            # Show file size
            size_kb = json_file.stat().st_size / 1024
            print(f"         Size: {size_kb:.1f} KB")
        
        print(f"   💾 {test_db.relative_to(temp_path)}")
        if test_db.exists():
            size_kb = test_db.stat().st_size / 1024
            print(f"      Size: {size_kb:.1f} KB")
    
    print("\n✅ Component workflow test completed!")
    print("\n📋 Workflow Summary:")
    print("   1. Components scraped → JSON files in data/processed/components/")
    print("   2. Server startup → imports JSON files into database")
    print("   3. Production deployment → JSON files pushed with code")
    print("   4. Easy data management like arrows!")

if __name__ == "__main__":
    test_component_workflow()