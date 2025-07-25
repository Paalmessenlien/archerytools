#!/usr/bin/env python3
"""
Debug BigArchery URL that's failing extraction.
Specifically testing: https://www.bigarchery.com/gb/shafts_304_274_BC9/282-706-cross-x-shaft-ambitionpoint.html

This script will:
1. Crawl the specific URL with Crawl4AI
2. Show the full content structure and length
3. Search for all key detection terms
4. Show content around any found terms
5. Check for tables or specification sections
6. Analyze why extraction might be failing
"""

import asyncio
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler

async def debug_bigarchery():
    """Debug BigArchery page to understand extraction failures"""
    
    url = "https://www.bigarchery.com/gb/shafts_304_274_BC9/282-706-cross-x-shaft-ambitionpoint.html"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        print(f"{'='*80}")
        print(f"DEBUGGING BIGARCHERY AMBITION POINT PAGE")
        print(f"URL: {url}")
        print(f"{'='*80}")
        
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )
        
        if not result.success:
            print(f"❌ Failed to fetch page: {result.error_message}")
            return
        
        # Get both HTML and markdown content
        html_content = result.html or ""
        markdown_content = result.markdown or ""
        
        print(f"✅ Successfully crawled page")
        print(f"HTML content length: {len(html_content):,} characters")
        print(f"Markdown content length: {len(markdown_content):,} characters")
        print(f"Status: {result.status_code}")
        
        # Search for detection terms
        print(f"\n{'='*60}")
        print("SEARCHING FOR KEY DETECTION TERMS")
        print(f"{'='*60}")
        
        detection_terms = [
            "spine", "stiffness", "deflection",
            "gpi", "grain", "weight", "grains per inch",
            "diameter", "outer", "inner", "o.d.", "i.d.",
            "specification", "specs", "technical", "data",
            "table", "chart"
        ]
        
        found_terms = {}
        content_lower = markdown_content.lower()
        
        for term in detection_terms:
            positions = []
            start = 0
            while True:
                pos = content_lower.find(term.lower(), start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            if positions:
                found_terms[term] = positions
                print(f"\n✅ FOUND: '{term}' - {len(positions)} occurrences")
                
                # Show context for first few occurrences
                for i, pos in enumerate(positions[:3]):
                    context_start = max(0, pos - 200)
                    context_end = min(len(markdown_content), pos + 200)
                    context = markdown_content[context_start:context_end]
                    print(f"   Context {i+1} (pos {pos:,}): ...{context}...")
            else:
                print(f"❌ NOT FOUND: '{term}'")
        
        # Search for numeric patterns that might be specs
        print(f"\n{'='*60}")
        print("SEARCHING FOR NUMERIC SPECIFICATION PATTERNS")
        print(f"{'='*60}")
        
        # Look for spine values (300, 340, 400, 500, etc.)
        spine_pattern = r'\b(250|300|340|350|400|450|500|550|600|650|700|750|800|850|900|950|1000|1100|1200)\b'
        spine_matches = re.finditer(spine_pattern, markdown_content)
        spine_list = list(spine_matches)
        
        if spine_list:
            print(f"Found {len(spine_list)} potential spine values:")
            for match in spine_list[:10]:  # Show first 10
                pos = match.start()
                context_start = max(0, pos - 100)
                context_end = min(len(markdown_content), pos + 100)
                context = markdown_content[context_start:context_end].replace('\n', ' ')
                print(f"  {match.group()} at pos {pos:,}: ...{context}...")
        else:
            print("No potential spine values found")
        
        # Look for weight patterns (decimal numbers with possible units)
        weight_pattern = r'\b\d+\.\d+\s*(gpi|grains?|gr|g)\b'
        weight_matches = re.finditer(weight_pattern, markdown_content, re.IGNORECASE)
        weight_list = list(weight_matches)
        
        if weight_list:
            print(f"\nFound {len(weight_list)} potential weight values:")
            for match in weight_list[:10]:
                pos = match.start()
                context_start = max(0, pos - 100)
                context_end = min(len(markdown_content), pos + 100)
                context = markdown_content[context_start:context_end].replace('\n', ' ')
                print(f"  {match.group()} at pos {pos:,}: ...{context}...")
        else:
            print("\nNo potential weight values found")
        
        # Look for diameter patterns
        diameter_pattern = r'\b\d+\.\d+\s*(mm|inch|")\b'
        diameter_matches = re.finditer(diameter_pattern, markdown_content, re.IGNORECASE)
        diameter_list = list(diameter_matches)
        
        if diameter_list:
            print(f"\nFound {len(diameter_list)} potential diameter values:")
            for match in diameter_list[:10]:
                pos = match.start()
                context_start = max(0, pos - 100)
                context_end = min(len(markdown_content), pos + 100)
                context = markdown_content[context_start:context_end].replace('\n', ' ')
                print(f"  {match.group()} at pos {pos:,}: ...{context}...")
        else:
            print("\nNo potential diameter values found")
        
        # Search for tables in HTML
        print(f"\n{'='*60}")
        print("SEARCHING FOR TABLES")
        print(f"{'='*60}")
        
        table_pattern = r'<table[^>]*>.*?</table>'
        tables = re.finditer(table_pattern, html_content, re.IGNORECASE | re.DOTALL)
        table_list = list(tables)
        
        if table_list:
            print(f"Found {len(table_list)} tables")
            
            for i, table_match in enumerate(table_list):
                table_pos = table_match.start()
                table_content = table_match.group()
                
                print(f"\nTable {i+1}:")
                print(f"  Position: {table_pos:,} characters from start")
                print(f"  Length: {len(table_content)} characters")
                
                # Check if this table contains spec-related content
                table_lower = table_content.lower()
                spec_indicators = ['spine', 'gpi', 'weight', 'grain', 'diameter', 'specification']
                matching_indicators = [ind for ind in spec_indicators if ind in table_lower]
                
                if matching_indicators:
                    print(f"  ✅ Likely specs table (contains: {', '.join(matching_indicators)})")
                    
                    # Show the table content (truncated if too long)
                    display_content = table_content if len(table_content) < 2000 else table_content[:2000] + "... [TRUNCATED]"
                    print(f"  Content:")
                    print(f"  {'-'*50}")
                    print(f"  {display_content}")
                    print(f"  {'-'*50}")
                else:
                    print(f"  ❌ No spec indicators found")
        else:
            print("No tables found in HTML content")
        
        # Show raw content sample
        print(f"\n{'='*60}")
        print("RAW CONTENT SAMPLE (First 3000 characters)")
        print(f"{'='*60}")
        print(markdown_content[:3000])
        print("... [TRUNCATED]")
        
        # Show middle section where specs might be
        if len(markdown_content) > 6000:
            print(f"\n{'='*60}")
            print("RAW CONTENT SAMPLE (Middle section 3000-6000)")
            print(f"{'='*60}")
            print(markdown_content[3000:6000])
            print("... [TRUNCATED]")
        
        # Show end section
        if len(markdown_content) > 3000:
            print(f"\n{'='*60}")
            print("RAW CONTENT SAMPLE (Last 1500 characters)")
            print(f"{'='*60}")
            print("..." + markdown_content[-1500:])

if __name__ == "__main__":
    asyncio.run(debug_bigarchery())