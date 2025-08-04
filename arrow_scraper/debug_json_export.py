#!/usr/bin/env python3
"""
Debug JSON export functionality
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_json_export():
    print("🔍 Debugging JSON Export")
    print("=" * 40)
    
    # Test 1: Check if we can import models
    try:
        from models import ManufacturerData, ArrowSpecification, SpineSpecification
        print("✅ Successfully imported models")
    except Exception as e:
        print(f"❌ Failed to import models: {e}")
        return
    
    # Test 2: Check if processed directory exists/can be created
    try:
        processed_dir = Path("data/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created/verified directory: {processed_dir.absolute()}")
    except Exception as e:
        print(f"❌ Failed to create directory: {e}")
        return
    
    # Test 3: Create sample arrow data
    try:
        # Create sample spine specification
        spine_spec = SpineSpecification(
            spine=1000,
            outer_diameter=0.204,
            gpi_weight=5.5
        )
        
        # Create sample arrow
        arrow = ArrowSpecification(
            manufacturer="Test Manufacturer",
            model_name="Test Arrow",
            spine_specifications=[spine_spec]
        )
        
        print("✅ Created sample arrow data")
    except Exception as e:
        print(f"❌ Failed to create arrow data: {e}")
        return
    
    # Test 4: Create ManufacturerData and export
    try:
        manufacturer_data = ManufacturerData(
            manufacturer="Test Manufacturer",
            total_arrows=1,
            arrows=[arrow],
            scraped_at=datetime.now().isoformat(),
            extraction_method="test"
        )
        
        # Create test filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"Test_Manufacturer_debug_{timestamp}.json"
        json_path = processed_dir / json_filename
        
        # Export to JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(manufacturer_data.model_dump(), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created test JSON file: {json_filename}")
        print(f"📁 Full path: {json_path.absolute()}")
        
        # Verify file exists
        if json_path.exists():
            size_kb = json_path.stat().st_size / 1024
            print(f"📊 File size: {size_kb:.1f} KB")
            
            # Show first few lines
            with open(json_path, 'r') as f:
                lines = f.readlines()[:10]
                print("📄 First few lines:")
                for line in lines:
                    print(f"   {line.rstrip()}")
        
    except Exception as e:
        print(f"❌ Failed to create JSON file: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎯 Test completed successfully!")
    print("If this works but --learn-all doesn't create files,")
    print("the issue is in the --learn-all logic, not the export functionality.")

if __name__ == "__main__":
    test_json_export()