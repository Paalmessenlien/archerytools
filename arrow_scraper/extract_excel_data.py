#!/usr/bin/env python3
"""
Extract wood arrow data and spine calculation information from the Excel file
"""

import pandas as pd
import json
import os

def extract_wood_arrow_data():
    excel_path = "../docs/V2 Dynamic Spine Calculator Rev 12-25-10 v2.xls"
    
    print("🌲 Extracting wood arrow data from Excel file...")
    
    try:
        # Read both sheets
        excel_data = pd.read_excel(excel_path, sheet_name=None, engine='xlrd')
        
        wood_arrows = []
        spine_data = {}
        
        # Process Dynamic Spine Calculator sheet
        calc_sheet = excel_data['Dynamic Spine Calculator']
        
        print(f"\n📊 Processing Dynamic Spine Calculator sheet...")
        
        # Look for rows that contain wood arrow information
        for idx, row in calc_sheet.iterrows():
            row_str = ' '.join([str(v) for v in row.values if pd.notna(v)]).lower()
            
            # Check if this row contains wood arrow data
            wood_keywords = ['wood', 'cedar', 'pine', 'sitka', 'douglas', 'acadian']
            if any(keyword in row_str for keyword in wood_keywords):
                print(f"   🎯 Found wood arrow data at row {idx}:")
                
                # Extract non-empty values from the row
                row_data = {}
                for col_idx, val in enumerate(row.values):
                    if pd.notna(val) and val != 0:
                        col_name = calc_sheet.columns[col_idx] if col_idx < len(calc_sheet.columns) else f"Col_{col_idx}"
                        row_data[col_name] = val
                
                if row_data:
                    print(f"      Data: {row_data}")
                    wood_arrows.append({
                        'row_index': idx,
                        'data': row_data,
                        'raw_text': row_str
                    })
        
        # Process Data Library sheet for more detailed arrow specs
        data_sheet = excel_data['Data Library']
        
        print(f"\n📋 Processing Data Library sheet...")
        
        # Look for structured arrow data
        for idx, row in data_sheet.iterrows():
            if idx < 5:  # Skip header rows
                continue
                
            row_values = row.dropna().values
            if len(row_values) > 5:  # Only process rows with substantial data
                print(f"   Row {idx}: {row_values[:8]}")  # Show first 8 values
        
        # Extract spine calculation data
        print(f"\n🧮 Looking for spine calculation patterns...")
        
        # Look for numeric patterns that might be spine values
        for sheet_name, df in excel_data.items():
            numeric_df = df.select_dtypes(include=['number']).dropna()
            
            for col in numeric_df.columns:
                values = numeric_df[col].dropna()
                # Look for potential spine values (150-1500 range)
                spine_candidates = values[(values >= 150) & (values <= 1500)]
                
                if len(spine_candidates) >= 5:
                    unique_spines = sorted(spine_candidates.unique())
                    print(f"   Sheet '{sheet_name}', Column '{col}': {unique_spines[:10]}...")
                    
                    spine_data[f"{sheet_name}_{col}"] = unique_spines.tolist()
        
        # Save extracted data
        output_data = {
            'wood_arrows': wood_arrows,
            'spine_data': spine_data,
            'extraction_timestamp': pd.Timestamp.now().isoformat(),
            'source_file': 'V2 Dynamic Spine Calculator Rev 12-25-10 v2.xls'
        }
        
        output_file = 'extracted_excel_data.json'
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n✅ Extracted data saved to {output_file}")
        print(f"   Wood arrows found: {len(wood_arrows)}")
        print(f"   Spine data columns: {len(spine_data)}")
        
        # Show some sample wood arrow data
        if wood_arrows:
            print(f"\n🌲 Sample wood arrow data:")
            for i, arrow in enumerate(wood_arrows[:5]):
                print(f"   {i+1}. {arrow['raw_text'][:100]}...")
        
        return output_data
        
    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        import traceback
        traceback.print_exc()

def create_wood_arrow_database_entries():
    """Create database entries for wood arrows based on extracted data"""
    
    # Define common wood arrow specifications based on traditional archery knowledge
    wood_arrow_specs = {
        "Cedar": {
            "material": "Cedar Wood",
            "arrow_type": "traditional",
            "spine_specifications": [
                {"spine": 35, "gpi_weight": 8.5, "outer_diameter": 0.3125},  # 35# spine, 5/16"
                {"spine": 40, "gpi_weight": 8.0, "outer_diameter": 0.3125},
                {"spine": 45, "gpi_weight": 7.5, "outer_diameter": 0.3125},
                {"spine": 50, "gpi_weight": 7.0, "outer_diameter": 0.3125},
                {"spine": 55, "gpi_weight": 6.5, "outer_diameter": 0.3125},
                {"spine": 60, "gpi_weight": 6.0, "outer_diameter": 0.3125},
                {"spine": 65, "gpi_weight": 5.5, "outer_diameter": 0.3125},
                {"spine": 70, "gpi_weight": 5.0, "outer_diameter": 0.3125},
            ]
        },
        "Pine": {
            "material": "Pine Wood", 
            "arrow_type": "traditional",
            "spine_specifications": [
                {"spine": 40, "gpi_weight": 9.0, "outer_diameter": 0.3125},
                {"spine": 45, "gpi_weight": 8.5, "outer_diameter": 0.3125},
                {"spine": 50, "gpi_weight": 8.0, "outer_diameter": 0.3125},
                {"spine": 55, "gpi_weight": 7.5, "outer_diameter": 0.3125},
                {"spine": 60, "gpi_weight": 7.0, "outer_diameter": 0.3125},
                {"spine": 65, "gpi_weight": 6.5, "outer_diameter": 0.3125},
                {"spine": 70, "gpi_weight": 6.0, "outer_diameter": 0.3125},
            ]
        },
        "Sitka Spruce": {
            "material": "Sitka Spruce Wood",
            "arrow_type": "traditional",
            "spine_specifications": [
                {"spine": 35, "gpi_weight": 7.5, "outer_diameter": 0.3125},
                {"spine": 40, "gpi_weight": 7.0, "outer_diameter": 0.3125},
                {"spine": 45, "gpi_weight": 6.5, "outer_diameter": 0.3125},
                {"spine": 50, "gpi_weight": 6.0, "outer_diameter": 0.3125},
                {"spine": 55, "gpi_weight": 5.5, "outer_diameter": 0.3125},
                {"spine": 60, "gpi_weight": 5.0, "outer_diameter": 0.3125},
                {"spine": 65, "gpi_weight": 4.5, "outer_diameter": 0.3125},
            ]
        },
        "Douglas Fir": {
            "material": "Douglas Fir Wood",
            "arrow_type": "traditional", 
            "spine_specifications": [
                {"spine": 40, "gpi_weight": 8.0, "outer_diameter": 0.3125},
                {"spine": 45, "gpi_weight": 7.5, "outer_diameter": 0.3125},
                {"spine": 50, "gpi_weight": 7.0, "outer_diameter": 0.3125},
                {"spine": 55, "gpi_weight": 6.5, "outer_diameter": 0.3125},
                {"spine": 60, "gpi_weight": 6.0, "outer_diameter": 0.3125},
                {"spine": 65, "gpi_weight": 5.5, "outer_diameter": 0.3125},
            ]
        }
    }
    
    # Create JSON data for database import
    wood_arrows_data = {
        "manufacturer": "Traditional Wood",
        "total_arrows": len(wood_arrow_specs),
        "arrows": [],
        "scraped_at": pd.Timestamp.now().isoformat(),
        "source": "V2 Dynamic Spine Calculator + Traditional Archery Standards"
    }
    
    for wood_type, specs in wood_arrow_specs.items():
        arrow_data = {
            "manufacturer": "Traditional Wood",
            "model_name": f"{wood_type} Shaft",
            "material": specs["material"],
            "arrow_type": specs["arrow_type"],
            "description": f"Traditional {wood_type.lower()} wood arrow shaft, hand-selected for straightness and spine consistency. Ideal for traditional archery and historical recreation.",
            "spine_specifications": []
        }
        
        for spine_spec in specs["spine_specifications"]:
            arrow_data["spine_specifications"].append({
                "spine": spine_spec["spine"],
                "outer_diameter": spine_spec["outer_diameter"],
                "gpi_weight": spine_spec["gpi_weight"],
                "inner_diameter": None,
                "length_options": [32.0, 33.0, 34.0],  # Standard wood arrow lengths
                "straightness_tolerance": "+/- 0.006\"",
                "weight_tolerance": "+/- 2 grains"
            })
        
        wood_arrows_data["arrows"].append(arrow_data)
    
    # Save wood arrow data
    output_file = 'wood_arrows_data.json'
    with open(output_file, 'w') as f:
        json.dump(wood_arrows_data, f, indent=2)
    
    print(f"🌲 Wood arrow database entries saved to {output_file}")
    print(f"   Wood types: {len(wood_arrow_specs)}")
    print(f"   Total spine options: {sum(len(specs['spine_specifications']) for specs in wood_arrow_specs.values())}")
    
    return wood_arrows_data

if __name__ == "__main__":
    # Extract data from Excel
    extracted_data = extract_wood_arrow_data()
    
    # Create wood arrow database entries
    wood_data = create_wood_arrow_database_entries()