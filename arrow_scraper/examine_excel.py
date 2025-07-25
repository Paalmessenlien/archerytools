#!/usr/bin/env python3
"""
Examine the V2 Dynamic Spine Calculator Excel file to extract:
1. Wood arrow data
2. Spine calculation formulas
3. Any other relevant data
"""

import pandas as pd
import xlrd
import os

def examine_excel_file():
    excel_path = "../docs/V2 Dynamic Spine Calculator Rev 12-25-10 v2.xls"
    
    if not os.path.exists(excel_path):
        print(f"❌ Excel file not found: {excel_path}")
        return
    
    print(f"📊 Examining Excel file: {excel_path}")
    
    try:
        # Try to open with xlrd first to see sheet names
        workbook = xlrd.open_workbook(excel_path)
        print(f"\n📋 Found {workbook.nsheets} sheets:")
        
        sheet_names = workbook.sheet_names()
        for i, name in enumerate(sheet_names):
            sheet = workbook.sheet_by_index(i)
            print(f"  {i+1}. {name} ({sheet.nrows} rows, {sheet.ncols} cols)")
        
        # Now try to read with pandas
        print("\n🔍 Examining sheet contents with pandas...")
        
        # Read all sheets
        excel_data = pd.read_excel(excel_path, sheet_name=None, engine='xlrd')
        
        for sheet_name, df in excel_data.items():
            print(f"\n📝 Sheet: {sheet_name}")
            print(f"   Shape: {df.shape}")
            
            # Display first few rows (non-empty)
            non_empty_df = df.dropna(how='all').dropna(axis=1, how='all')
            if not non_empty_df.empty:
                print("   First 5 rows:")
                print(non_empty_df.head().to_string(index=False))
                
                # Look for wood arrow related data
                wood_keywords = ['wood', 'cedar', 'pine', 'sitka', 'douglas']
                for keyword in wood_keywords:
                    # Search in all columns and values
                    matches = non_empty_df.astype(str).apply(
                        lambda x: x.str.lower().str.contains(keyword, na=False)
                    ).any().any()
                    
                    if matches:
                        print(f"   🎯 Found '{keyword}' references in this sheet!")
                        # Show rows containing the keyword
                        mask = non_empty_df.astype(str).apply(
                            lambda x: x.str.lower().str.contains(keyword, na=False)
                        ).any(axis=1)
                        matching_rows = non_empty_df[mask]
                        if not matching_rows.empty:
                            print("   Matching rows:")
                            print(matching_rows.to_string(index=False))
            else:
                print("   (Sheet appears to be empty)")
        
        # Look for spine calculation formulas or tables
        print("\n🧮 Looking for spine calculation data...")
        for sheet_name, df in excel_data.items():
            # Look for numeric spine values (typically 200-1000)
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                spine_values = df[col].dropna()
                potential_spines = spine_values[(spine_values >= 150) & (spine_values <= 1500)]
                
                if len(potential_spines) > 5:  # If we find multiple potential spine values
                    print(f"   🎯 Potential spine data in sheet '{sheet_name}', column '{col}':")
                    print(f"      Values: {sorted(potential_spines.unique())}")
        
        print("\n✅ Excel file examination complete!")
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")

if __name__ == "__main__":
    examine_excel_file()