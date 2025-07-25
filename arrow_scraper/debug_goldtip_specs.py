#!/usr/bin/env python3
"""
Debug Gold Tip arrow page content structure to locate specifications table.
Specifically looking for:
- <div class="card-body p-0">
- <div class="specs specs-loaded">
"""

import asyncio
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler

async def debug_goldtip_specs():
    """Debug Gold Tip page structure to find specifications table"""
    
    url = "https://www.goldtip.com/hunting-arrows/hunter-series/hunter-hunting-arrows/P01268.html"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        print(f"{'='*80}")
        print(f"DEBUGGING GOLD TIP SPECS PAGE")
        print(f"URL: {url}")
        print(f"{'='*80}")
        
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )
        
        if not result.success:
            print(f"Failed to fetch page: {result.error_message}")
            return
        
        # Get both HTML and markdown content
        html_content = result.html or ""
        markdown_content = result.markdown or ""
        
        print(f"HTML content length: {len(html_content):,} characters")
        print(f"Markdown content length: {len(markdown_content):,} characters")
        print(f"Status: {result.status_code}")
        
        # Search for the specific HTML structures mentioned
        structures_to_find = [
            r'<div class="card-body p-0">',
            r'<div class="specs specs-loaded">',
            r'<div[^>]*class="[^"]*card-body[^"]*"[^>]*>',
            r'<div[^>]*class="[^"]*specs[^"]*"[^>]*>',
            r'<table[^>]*class="[^"]*spec[^"]*"[^>]*>',
            r'<div[^>]*id="[^"]*spec[^"]*"[^>]*>',
        ]
        
        print(f"\n{'='*60}")
        print("SEARCHING FOR SPECIFICATION STRUCTURES")
        print(f"{'='*60}")
        
        found_structures = {}
        
        for pattern in structures_to_find:
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            match_list = list(matches)
            
            if match_list:
                found_structures[pattern] = match_list
                print(f"\n✓ FOUND: {pattern}")
                print(f"  Matches: {len(match_list)}")
                
                for i, match in enumerate(match_list):
                    start_pos = match.start()
                    end_pos = match.end()
                    char_position = start_pos
                    
                    print(f"  Match {i+1}:")
                    print(f"    Position: {char_position:,} characters from start")
                    print(f"    Character limit check: {'WITHIN 15k' if char_position < 15000 else 'BEYOND 15k limit'}")
                    print(f"    Match: {match.group()}")
                    
                    # Show context around the match (500 chars before and after)
                    context_start = max(0, start_pos - 500)
                    context_end = min(len(html_content), end_pos + 500)
                    context = html_content[context_start:context_end]
                    
                    print(f"    Context (500 chars around match):")
                    print(f"    {'-'*50}")
                    print(f"    {context}")
                    print(f"    {'-'*50}")
            else:
                print(f"\n✗ NOT FOUND: {pattern}")
        
        # Search for common specification keywords in HTML
        print(f"\n{'='*60}")
        print("SEARCHING FOR SPECIFICATION KEYWORDS")
        print(f"{'='*60}")
        
        spec_keywords = [
            'specification', 'specs', 'diameter', 'spine', 'gpi', 'grains',
            'weight', 'straightness', 'length', 'carbon', 'shaft'
        ]
        
        keyword_positions = {}
        for keyword in spec_keywords:
            pattern = re.compile(rf'\b{keyword}\b', re.IGNORECASE)
            matches = list(pattern.finditer(html_content))
            
            if matches:
                keyword_positions[keyword] = matches
                print(f"\n✓ '{keyword}': {len(matches)} occurrences")
                
                # Show first few matches with positions
                for i, match in enumerate(matches[:3]):
                    pos = match.start()
                    within_limit = "WITHIN 15k" if pos < 15000 else "BEYOND 15k limit"
                    print(f"    Match {i+1}: Position {pos:,} ({within_limit})")
                    
                    # Show small context
                    context_start = max(0, pos - 100)
                    context_end = min(len(html_content), pos + 100)
                    context = html_content[context_start:context_end].replace('\n', ' ').strip()
                    print(f"    Context: ...{context}...")
        
        # Check if there are tables in the content
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
                within_limit = "WITHIN 15k" if table_pos < 15000 else "BEYOND 15k limit"
                table_content = table_match.group()
                
                print(f"\nTable {i+1}:")
                print(f"  Position: {table_pos:,} ({within_limit})")
                print(f"  Length: {len(table_content)} characters")
                
                # Check if this table contains spec-related content
                table_lower = table_content.lower()
                spec_indicators = ['spec', 'diameter', 'spine', 'gpi', 'weight', 'grain']
                matching_indicators = [ind for ind in spec_indicators if ind in table_lower]
                
                if matching_indicators:
                    print(f"  ✓ Likely specs table (contains: {', '.join(matching_indicators)})")
                    
                    # Show the table content (truncated if too long)
                    display_content = table_content if len(table_content) < 2000 else table_content[:2000] + "... [TRUNCATED]"
                    print(f"  Content:")
                    print(f"  {'-'*40}")
                    print(f"  {display_content}")
                    print(f"  {'-'*40}")
                else:
                    print(f"  - No spec indicators found")
        else:
            print("No tables found in HTML content")
        
        # Show where the 15k character limit falls in the content
        print(f"\n{'='*60}")
        print("15K CHARACTER LIMIT ANALYSIS")
        print(f"{'='*60}")
        
        if len(html_content) > 15000:
            print(f"Content at 15k character mark:")
            print(f"{'-'*50}")
            cutoff_context = html_content[14800:15200]  # Show around the cutoff
            print(cutoff_context)
            print(f"{'-'*50}")
            print(f"Characters beyond 15k limit: {len(html_content) - 15000:,}")
        else:
            print(f"Entire content is within 15k limit ({len(html_content):,} chars)")
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        
        print(f"Total HTML content: {len(html_content):,} characters")
        print(f"Structures found: {len(found_structures)}")
        print(f"Tables found: {len(table_list)}")
        print(f"Spec keywords found: {len([k for k, v in keyword_positions.items() if v])}")
        
        # Check if important content might be beyond the limit
        important_beyond_limit = []
        if found_structures:
            for pattern, matches in found_structures.items():
                for match in matches:
                    if match.start() >= 15000:
                        important_beyond_limit.append(f"Structure '{pattern}' at position {match.start():,}")
        
        if table_list:
            for i, table in enumerate(table_list):
                if table.start() >= 15000:
                    important_beyond_limit.append(f"Table {i+1} at position {table.start():,}")
        
        if important_beyond_limit:
            print(f"\n⚠️  IMPORTANT CONTENT BEYOND 15K LIMIT:")
            for item in important_beyond_limit:
                print(f"  - {item}")
        else:
            print(f"\n✓ All important content appears to be within 15k limit")

if __name__ == "__main__":
    asyncio.run(debug_goldtip_specs())