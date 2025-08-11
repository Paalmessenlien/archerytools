#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

def scrape_x10_parallel_pro():
    """Directly test scraping the X10 Parallel Pro URL"""
    
    url = "https://eastonarchery.com/arrows_/x10-parallel-pro/"
    manufacturer = "Easton"
    
    print(f"Scraping URL: {url}")
    print(f"Manufacturer: {manufacturer}")
    print()
    
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=30, headers=headers)
        print(f"HTTP Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch URL: {response.status_code}")
            return
        
        # Parse the content
        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text()
        
        print(f"Page content length: {len(page_text)} characters")
        
        # Try multiple extraction strategies
        print("\n=== Extraction Results ===")
        
        # Strategy 1: Look for spine values
        spine_patterns = [
            r'\b(\d{2,4})\s*spine\b',
            r'\bspine\s*(\d{2,4})\b',
            r'\b(\d{2,4})\s*stiffness\b',
            r'\bstiffness\s*(\d{2,4})\b'
        ]
        
        all_spines = set()
        for pattern in spine_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                print(f"Spine pattern '{pattern}': {matches}")
                all_spines.update(matches)
        
        # Strategy 2: Look for GPI values
        gpi_patterns = [
            r'(\d+\.?\d*)\s*gpi\b',
            r'\bgpi\s*(\d+\.?\d*)\b',
            r'(\d+\.?\d*)\s*grains?\s*per\s*inch',
            r'grains?\s*per\s*inch\s*(\d+\.?\d*)'
        ]
        
        all_gpi = set()
        for pattern in gpi_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                print(f"GPI pattern '{pattern}': {matches}")
                all_gpi.update(matches)
        
        # Strategy 3: Look for diameter values
        diameter_patterns = [
            r'(\d+\.?\d*)\s*(?:inch|") diameter',
            r'diameter\s*(\d+\.?\d*)\s*(?:inch|")?',
            r'(\d+\.?\d*)\s*(?:inch|") OD',
            r'OD\s*(\d+\.?\d*)\s*(?:inch|")?'
        ]
        
        all_diameters = set()
        for pattern in diameter_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                print(f"Diameter pattern '{pattern}': {matches}")
                all_diameters.update(matches)
        
        # Strategy 4: Look for specific text sections
        # Look for tables or specifications sections
        spec_sections = soup.find_all(['table', 'div'], class_=re.compile(r'spec|detail|info', re.I))
        
        print(f"\nFound {len(spec_sections)} potential spec sections")
        
        for i, section in enumerate(spec_sections[:3]):  # Check first 3 sections
            section_text = section.get_text()
            if len(section_text) > 50:  # Only look at substantial sections
                print(f"\nSpec section {i+1} (first 200 chars):")
                print(section_text[:200])
                
                # Look for patterns in this section
                section_spines = re.findall(r'\b(\d{2,4})\s*(?:spine|stiffness)', section_text, re.IGNORECASE)
                section_gpi = re.findall(r'(\d+\.?\d*)\s*gpi', section_text, re.IGNORECASE)
                if section_spines or section_gpi:
                    print(f"  -> Found spines: {section_spines}")
                    print(f"  -> Found GPI: {section_gpi}")
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Total spine values found: {list(all_spines)}")
        print(f"Total GPI values found: {list(all_gpi)}")
        print(f"Total diameter values found: {list(all_diameters)}")
        
        # Check what's currently in the database for this arrow
        print(f"\n=== Current Database Content ===")
        conn = sqlite3.connect('/home/paal/arrowtuner2/databases/arrow_database.db')
        cursor = conn.cursor()
        
        # Find the X10 Parallel Pro arrow
        cursor.execute('''
            SELECT id, model_name, manufacturer 
            FROM arrows 
            WHERE manufacturer LIKE '%Easton%' AND model_name LIKE '%X10 Parallel Pro%'
        ''')
        
        arrow = cursor.fetchone()
        if arrow:
            arrow_id = arrow[0]
            print(f"Found arrow: ID {arrow_id} - {arrow[1]} by {arrow[2]}")
            
            # Get current spine specifications
            cursor.execute('''
                SELECT spine, outer_diameter, gpi_weight 
                FROM spine_specifications 
                WHERE arrow_id = ?
                ORDER BY spine
            ''', (arrow_id,))
            
            current_spines = cursor.fetchall()
            print(f"Current spine specifications ({len(current_spines)}):")
            for spine in current_spines:
                print(f"  Spine: {spine[0]}, Diameter: {spine[1]}, GPI: {spine[2]}")
        else:
            print("X10 Parallel Pro arrow not found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    scrape_x10_parallel_pro()