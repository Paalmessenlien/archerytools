#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

def extract_x10_specifications():
    """Extract X10 Parallel Pro specifications from the table"""
    
    url = "https://eastonarchery.com/arrows_/x10-parallel-pro/"
    manufacturer = "Easton Archery"
    
    print(f"Extracting specifications from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=30, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch URL: {response.status_code}")
            return []
        
        # Parse the content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table with specifications
        table = soup.find('table', {'id': 'tablepress-19'})
        
        if not table:
            print("Could not find specifications table")
            return []
        
        print("Found specifications table!")
        
        # Extract data from table rows
        rows = table.find('tbody').find_all('tr')
        specifications = []
        
        print(f"Found {len(rows)} data rows")
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                spine = cells[0].get_text().strip()  # Column 1: Size (spine)
                gpi = cells[1].get_text().strip()    # Column 2: GPI
                diameter = cells[2].get_text().strip()  # Column 3: O.D.
                
                try:
                    # Convert to proper numeric values
                    spine_num = int(spine)
                    gpi_num = float(gpi)
                    diameter_num = float(diameter)
                    
                    specifications.append({
                        'spine': spine_num,
                        'gpi': gpi_num,
                        'diameter': diameter_num
                    })
                    
                    print(f"  Spine {spine_num}: GPI={gpi_num}, Diameter={diameter_num}")
                    
                except ValueError as e:
                    print(f"  Skipping invalid row: {spine}, {gpi}, {diameter} - {e}")
                    continue
        
        print(f"Successfully extracted {len(specifications)} specifications")
        return specifications
        
    except Exception as e:
        print(f"Error extracting specifications: {e}")
        import traceback
        traceback.print_exc()
        return []

def update_database_with_specs(specifications):
    """Update the X10 Parallel Pro arrow in the database with extracted specifications"""
    
    if not specifications:
        print("No specifications to update")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect('/home/paal/arrowtuner2/databases/arrow_database.db')
        cursor = conn.cursor()
        
        # Find the X10 Parallel Pro arrow
        cursor.execute('''
            SELECT id, model_name 
            FROM arrows 
            WHERE manufacturer LIKE '%Easton%' AND model_name LIKE '%X10 Parallel Pro%'
        ''')
        
        arrow = cursor.fetchone()
        if not arrow:
            print("X10 Parallel Pro arrow not found in database")
            return
        
        arrow_id = arrow[0]
        arrow_name = arrow[1]
        
        print(f"Found arrow: {arrow_name} (ID: {arrow_id})")
        
        # Get current spine specifications
        cursor.execute('SELECT spine FROM spine_specifications WHERE arrow_id = ?', (arrow_id,))
        existing_spines = set(row[0] for row in cursor.fetchall())
        
        print(f"Existing spines in database: {sorted(existing_spines)}")
        
        # Add new spine specifications
        added_count = 0
        updated_count = 0
        
        for spec in specifications:
            spine = spec['spine']
            gpi = spec['gpi']
            diameter = spec['diameter']
            
            if spine in existing_spines:
                # Update existing specification
                cursor.execute('''
                    UPDATE spine_specifications 
                    SET gpi_weight = ?, outer_diameter = ?
                    WHERE arrow_id = ? AND spine = ?
                ''', (gpi, diameter, arrow_id, spine))
                updated_count += 1
                print(f"  Updated spine {spine}: GPI={gpi}, Diameter={diameter}")
            else:
                # Insert new specification
                cursor.execute('''
                    INSERT INTO spine_specifications 
                    (arrow_id, spine, gpi_weight, outer_diameter)
                    VALUES (?, ?, ?, ?)
                ''', (arrow_id, spine, gpi, diameter))
                added_count += 1
                print(f"  Added spine {spine}: GPI={gpi}, Diameter={diameter}")
        
        # Update the arrow's source_url and scraped_at timestamp
        cursor.execute('''
            UPDATE arrows 
            SET source_url = ?, scraped_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', ("https://eastonarchery.com/arrows_/x10-parallel-pro/", arrow_id))
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"\nDatabase update complete:")
        print(f"  Added {added_count} new spine specifications")
        print(f"  Updated {updated_count} existing spine specifications")
        
        return {'added': added_count, 'updated': updated_count}
        
    except Exception as e:
        print(f"Error updating database: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=== X10 Parallel Pro Specification Extraction ===")
    
    # Extract specifications from website
    specs = extract_x10_specifications()
    
    if specs:
        print(f"\n=== Database Update ===")
        result = update_database_with_specs(specs)
        
        if result:
            print(f"\n=== Success! ===")
            print(f"Successfully updated X10 Parallel Pro with {result['added']} new and {result['updated']} updated spine specifications")
    else:
        print("No specifications extracted, skipping database update")