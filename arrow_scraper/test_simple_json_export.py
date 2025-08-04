#!/usr/bin/env python3
"""
Test simplified JSON export (no pydantic dependencies)
"""

import json
from pathlib import Path
from datetime import datetime

def test_simple_json_export():
    print("🔍 Testing Simplified JSON Export")
    print("=" * 40)
    
    # Create test data (simulating extracted arrows)
    manufacturer_name = "Test Manufacturer"
    
    # Mock arrow objects (basic class simulation)
    class MockSpineSpec:
        def __init__(self, spine, outer_diameter, gpi_weight):
            self.spine = spine
            self.outer_diameter = outer_diameter
            self.gpi_weight = gpi_weight
    
    class MockArrow:
        def __init__(self, manufacturer, model_name, spine_specs):
            self.manufacturer = manufacturer
            self.model_name = model_name
            self.spine_specifications = spine_specs
            self.material = "Carbon"
            self.arrow_type = "Target"
            self.description = "Test arrow"
    
    # Create sample arrows
    spine1 = MockSpineSpec(350, 0.246, 8.2)
    spine2 = MockSpineSpec(400, 0.246, 7.8)
    arrow1 = MockArrow(manufacturer_name, "Test Arrow 1", [spine1])
    arrow2 = MockArrow(manufacturer_name, "Test Arrow 2", [spine2])
    
    manufacturer_arrows = [arrow1, arrow2]
    
    print(f"✅ Created {len(manufacturer_arrows)} test arrows")
    
    # Test the JSON export logic (copied from main.py)
    try:
        # Save to JSON file using basic JSON structure
        processed_dir = Path("data/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Create safe filename
        safe_manufacturer = "".join(c for c in manufacturer_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"{safe_manufacturer}_test_{timestamp}.json"
        json_path = processed_dir / json_filename
        
        # Convert arrows to basic dict format for JSON serialization
        arrows_data = []
        for arrow in manufacturer_arrows:
            arrow_dict = {
                "manufacturer": arrow.manufacturer,
                "model_name": arrow.model_name,
                "spine_specifications": []
            }
            
            # Convert spine specifications
            for spine_spec in arrow.spine_specifications:
                spine_dict = {
                    "spine": spine_spec.spine,
                    "outer_diameter": spine_spec.outer_diameter,
                    "gpi_weight": spine_spec.gpi_weight
                }
                arrow_dict["spine_specifications"].append(spine_dict)
            
            # Add optional fields if they exist
            if hasattr(arrow, 'material') and arrow.material:
                arrow_dict["material"] = arrow.material
            if hasattr(arrow, 'arrow_type') and arrow.arrow_type:
                arrow_dict["arrow_type"] = arrow.arrow_type
            if hasattr(arrow, 'description') and arrow.description:
                arrow_dict["description"] = arrow.description
                
            arrows_data.append(arrow_dict)
        
        # Create JSON structure
        json_data = {
            "manufacturer": manufacturer_name,
            "total_arrows": len(manufacturer_arrows),
            "scraped_at": datetime.now().isoformat(),
            "extraction_method": "test",
            "arrows": arrows_data
        }
        
        # Export to JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created JSON file: {json_filename}")
        print(f"📁 Full path: {json_path.absolute()}")
        
        # Verify file exists and show content
        if json_path.exists():
            size_kb = json_path.stat().st_size / 1024
            print(f"📊 File size: {size_kb:.1f} KB")
            
            # Show first few lines
            with open(json_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')[:15]
                print("📄 JSON content (first 15 lines):")
                for line in lines:
                    print(f"   {line}")
                if len(content.split('\n')) > 15:
                    print("   ...")
        
        print("\n✅ Simplified JSON export test PASSED!")
        print("The logic should work in --learn-all now.")
        
    except Exception as e:
        print(f"❌ JSON export test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_json_export()