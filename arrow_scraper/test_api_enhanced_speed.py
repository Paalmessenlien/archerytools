#!/usr/bin/env python3
"""Test the API enhanced speed calculation path exactly as called from browser"""

import os
import sqlite3
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Change to project root directory
os.chdir(Path(__file__).parent.parent)

def test_api_enhanced_speed_path():
    """Test the exact path used in calculate_individual_arrow_performance"""
    
    print("🔍 Testing API enhanced speed calculation path...")
    
    # Import API functions
    from api import calculate_enhanced_arrow_speed_internal, get_database
    
    # Get the actual setup arrow data like the API does
    db = get_database()
    cursor = db.get_connection().cursor()
    
    # Get setup arrow data for ID 1 (like the browser is calling)
    setup_arrow_id = 1
    cursor.execute('''
        SELECT sa.*, bs.user_id, bs.draw_weight, bs.bow_type, bs.ibo_speed,
               a.id as arrow_id, a.manufacturer, a.model_name, a.material, a.arrow_type
        FROM setup_arrows sa
        JOIN bow_setups bs ON sa.setup_id = bs.id
        LEFT JOIN arrows a ON sa.arrow_id = a.id
        WHERE sa.id = ?
    ''', (setup_arrow_id,))
    setup_arrow = cursor.fetchone()
    
    if not setup_arrow:
        print(f"❌ Setup arrow {setup_arrow_id} not found")
        return
    
    print(f"📊 Setup arrow data:")
    print(f"   Setup Arrow ID: {setup_arrow_id}")
    print(f"   Setup ID: {setup_arrow['setup_id']}")
    print(f"   Arrow ID: {setup_arrow['arrow_id']}")
    print(f"   Arrow Length: {setup_arrow['arrow_length']}")
    print(f"   Point Weight: {setup_arrow['point_weight']}")
    print(f"   Manufacturer: {setup_arrow['manufacturer']}")
    print(f"   Model: {setup_arrow['model_name']}")
    
    # Get spine data like the API does
    cursor.execute('''
        SELECT spine, outer_diameter, inner_diameter, gpi_weight
        FROM spine_specifications WHERE arrow_id = ?
        ORDER BY spine ASC LIMIT 1
    ''', (setup_arrow['arrow_id'],))
    spine_data = cursor.fetchone()
    
    if spine_data:
        gpi_weight = spine_data['gpi_weight'] if spine_data['gpi_weight'] and spine_data['gpi_weight'] > 0 else 8.5
    else:
        gpi_weight = 8.5
        
    print(f"   GPI Weight: {gpi_weight}")
    
    # Calculate arrow weight like the API does
    arrow_weight_grains = (gpi_weight * setup_arrow['arrow_length']) + setup_arrow['point_weight'] + 25
    print(f"   Calculated Total Weight: {arrow_weight_grains} gr")
    
    # Prepare parameters exactly like the API does
    speed_request_data = {
        'bow_ibo_speed': setup_arrow['ibo_speed'] if setup_arrow['ibo_speed'] else 320,
        'bow_draw_weight': setup_arrow['draw_weight'] if setup_arrow['draw_weight'] else 50, 
        'bow_draw_length': 29,  # From bow config in API
        'bow_type': setup_arrow['bow_type'] if setup_arrow['bow_type'] else 'compound',
        'arrow_weight_grains': arrow_weight_grains,
        'string_material': 'dacron',
        'setup_id': setup_arrow['setup_id'],
        'arrow_id': setup_arrow['arrow_id']
    }
    
    print(f"\n🧪 Calling calculate_enhanced_arrow_speed_internal with API parameters:")
    for key, value in speed_request_data.items():
        print(f"   {key}: {value}")
    
    try:
        enhanced_speed = calculate_enhanced_arrow_speed_internal(
            bow_ibo_speed=speed_request_data['bow_ibo_speed'],
            bow_draw_weight=speed_request_data['bow_draw_weight'],
            bow_draw_length=speed_request_data['bow_draw_length'],
            bow_type=speed_request_data['bow_type'],
            arrow_weight_grains=speed_request_data['arrow_weight_grains'],
            string_material=speed_request_data['string_material'],
            setup_id=speed_request_data['setup_id'],
            arrow_id=speed_request_data['arrow_id']
        )
        
        print(f"\n✅ Enhanced speed result: {enhanced_speed} fps")
        
        if enhanced_speed:
            print(f"🎯 SUCCESS: API path should return {enhanced_speed} fps")
            
            # Compare with what browser is actually showing
            browser_speed = 290.8
            print(f"🔍 Comparison with browser result:")
            print(f"   Enhanced calculation: {enhanced_speed} fps")
            print(f"   Browser showing: {browser_speed} fps")
            
            if abs(enhanced_speed - browser_speed) > 1.0:
                print(f"❌ MISMATCH: Browser is not using enhanced speed calculation!")
                print(f"   This confirms there's an issue in the API endpoint")
            else:
                print(f"✅ MATCH: Browser is using enhanced speed calculation")
        else:
            print(f"❌ Enhanced speed returned None - fallback will be used")
            
        return enhanced_speed
        
    except Exception as e:
        print(f"❌ Exception in enhanced speed calculation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🔍 Debug: API Enhanced Speed Calculation Path")
    print("=" * 60)
    
    result = test_api_enhanced_speed_path()
    
    if result:
        print(f"\n🎯 The API should be returning {result} fps to the browser")
        print(f"   If browser shows different value, there's an API endpoint issue")
    else:
        print(f"\n❌ Enhanced speed calculation failed - this explains fallback usage")
    
    print("=" * 60)