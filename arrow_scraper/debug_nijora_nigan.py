#!/usr/bin/env python3
"""
Debug Nijora Nigan Pro URL that's failing extraction.
Specifically testing: https://nijora.com/product/nigan-pro/

This script will:
1. Crawl the specific URL with Crawl4AI
2. Show the full content structure and length
3. Search for all key detection terms for Nijora
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

async def debug_nijora_nigan():
    """Debug Nijora Nigan Pro page to understand extraction failures"""
    
    url = "https://nijora.com/product/nigan-pro/"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        print(f"{'='*80}")
        print(f"DEBUGGING NIJORA NIGAN PRO PAGE")
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
        
        # Search for Nijora-specific detection terms
        print(f"\n{'='*60}")
        print("SEARCHING FOR NIJORA KEY DETECTION TERMS")
        print(f"{'='*60}")
        
        detection_terms = [
            "spine",
            "gpi", 
            "grain/inch",
            "zoll",
            "tablepress-1",
            "woocommerce-tabs-panel--wd_custom_tab",
            "rundlaufgenauigkeit"
        ]
        
        found_terms = {}
        content_lower = markdown_content.lower()
        html_lower = html_content.lower()
        
        for term in detection_terms:
            # Search in both markdown and HTML
            md_positions = []
            html_positions = []
            
            # Find all occurrences in markdown
            start = 0
            while True:
                pos = content_lower.find(term.lower(), start)
                if pos == -1:
                    break
                md_positions.append(pos)
                start = pos + 1
            
            # Find all occurrences in HTML
            start = 0
            while True:
                pos = html_lower.find(term.lower(), start)
                if pos == -1:
                    break
                html_positions.append(pos)
                start = pos + 1
            
            if md_positions or html_positions:
                found_terms[term] = {
                    'markdown_positions': md_positions,
                    'html_positions': html_positions
                }
                print(f"\n✅ FOUND: '{term}'")
                print(f"   Markdown occurrences: {len(md_positions)}")
                print(f"   HTML occurrences: {len(html_positions)}")
                
                # Show context for first few occurrences in markdown
                for i, pos in enumerate(md_positions[:3]):
                    context_start = max(0, pos - 200)
                    context_end = min(len(markdown_content), pos + 200)
                    context = markdown_content[context_start:context_end]
                    print(f"   Markdown context {i+1} (pos {pos:,}): ...{context}...")
                
                # Show context for first few occurrences in HTML (for specific terms)
                if term in ["tablepress-1", "woocommerce-tabs-panel--wd_custom_tab"]:
                    for i, pos in enumerate(html_positions[:2]):
                        context_start = max(0, pos - 300)
                        context_end = min(len(html_content), pos + 500)
                        context = html_content[context_start:context_end]
                        print(f"   HTML context {i+1} (pos {pos:,}): ...{context}...")
            else:
                print(f"\n❌ NOT FOUND: '{term}'")
        
        # Search for additional German/Nijora specific terms
        print(f"\n{'='*60}")
        print("SEARCHING FOR ADDITIONAL GERMAN/NIJORA TERMS")
        print(f"{'='*60}")
        
        additional_terms = [
            'spine', 'spinewert', 'dynaspine', 'statisch', 'statischer',
            'gramm', 'gram', 'gewicht', 'weight', 'gpi',
            'durchmesser', 'diameter', 'aussendurchmesser', 'innendurchmesser',
            'spezifikation', 'specification', 'technische', 'daten',
            'tabelle', 'table', 'eigenschaften', 'carbon',
            'pfeil', 'shaft', 'schaft', 'zoll', 'inch',
            'millimeter', 'mm', 'rundlauf', 'genauigkeit',
            'woocommerce', 'tab', 'panel', 'tablepress'
        ]
        
        german_terms_found = {}
        for term in additional_terms:
            positions = []
            start = 0
            while True:
                pos = content_lower.find(term.lower(), start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            if positions:
                german_terms_found[term] = positions
                print(f"✅ '{term}': {len(positions)} occurrences")
                
                # Show context for first occurrence
                pos = positions[0]
                context_start = max(0, pos - 150)
                context_end = min(len(markdown_content), pos + 150)
                context = markdown_content[context_start:context_end].replace('\n', ' ').strip()
                print(f"   First occurrence context: ...{context}...")
        
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
                spec_indicators = ['spine', 'gpi', 'weight', 'gramm', 'zoll', 'durchmesser', 'specification']
                matching_indicators = [ind for ind in spec_indicators if ind in table_lower]
                
                if matching_indicators:
                    print(f"  ✅ Likely specs table (contains: {', '.join(matching_indicators)})")
                    
                    # Show the table content (truncated if too long)
                    display_content = table_content if len(table_content) < 1500 else table_content[:1500] + "... [TRUNCATED]"
                    print(f"  Content:")
                    print(f"  {'-'*50}")
                    print(f"  {display_content}")
                    print(f"  {'-'*50}")
                else:
                    print(f"  ❌ No spec indicators found")
        else:
            print("No tables found in HTML content")
        
        # Search for div containers that might contain specifications
        print(f"\n{'='*60}")
        print("SEARCHING FOR SPECIFICATION CONTAINERS")
        print(f"{'='*60}")
        
        container_patterns = [
            r'<div[^>]*class="[^"]*spec[^"]*"[^>]*>',
            r'<div[^>]*class="[^"]*table[^"]*"[^>]*>',
            r'<div[^>]*class="[^"]*tab[^"]*"[^>]*>',
            r'<div[^>]*id="[^"]*spec[^"]*"[^>]*>',
            r'<div[^>]*id="[^"]*table[^"]*"[^>]*>',
            r'<div[^>]*class="[^"]*woocommerce[^"]*"[^>]*>',
            r'tablepress-1',
            r'woocommerce-tabs-panel--wd_custom_tab'
        ]
        
        for pattern in container_patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            match_list = list(matches)
            
            if match_list:
                print(f"\n✅ FOUND: {pattern}")
                print(f"  Matches: {len(match_list)}")
                
                for i, match in enumerate(match_list):
                    start_pos = match.start()
                    print(f"  Match {i+1}: Position {start_pos:,}")
                    
                    # Show context around the match
                    context_start = max(0, start_pos - 300)
                    context_end = min(len(html_content), start_pos + 800)
                    context = html_content[context_start:context_end]
                    
                    print(f"  Context:")
                    print(f"  {'-'*50}")
                    print(f"  {context}")
                    print(f"  {'-'*50}")
            else:
                print(f"\n❌ NOT FOUND: {pattern}")
        
        # Analyze content structure
        print(f"\n{'='*60}")
        print("CONTENT STRUCTURE ANALYSIS")
        print(f"{'='*60}")
        
        # Count sections in markdown
        sections = markdown_content.split('\n##')
        print(f"Markdown sections (split by ##): {len(sections)}")
        
        # Show section headers
        for i, section in enumerate(sections[:10]):  # Show first 10 sections
            lines = section.split('\n')
            header = lines[0].strip().replace('#', '').strip()
            if header:
                print(f"  Section {i+1}: {header[:100]}...")
        
        # Check for WooCommerce specific content
        woo_patterns = [
            'woocommerce',
            'product-details',
            'product-description',
            'additional-information',
            'specification',
            'technische-daten'
        ]
        
        print(f"\nWooCommerce/Product patterns found:")
        for pattern in woo_patterns:
            count = content_lower.count(pattern)
            if count > 0:
                print(f"  '{pattern}': {count} occurrences")
        
        # Analyze why extraction might be failing
        print(f"\n{'='*60}")
        print("EXTRACTION FAILURE ANALYSIS")
        print(f"{'='*60}")
        
        # Check if key terms are present
        has_spine = any('spine' in pos for pos in [content_lower, html_lower])
        has_weight = any(term in content_lower for term in ['gpi', 'gramm', 'weight', 'grain'])
        has_diameter = any(term in content_lower for term in ['durchmesser', 'diameter', 'zoll'])
        has_nijora_table = 'tablepress-1' in html_lower
        has_nijora_tab = 'woocommerce-tabs-panel--wd_custom_tab' in html_lower
        has_rundlauf = 'rundlaufgenauigkeit' in content_lower
        
        print(f"Key detection results:")
        print(f"  Has spine reference: {'✅' if has_spine else '❌'}")
        print(f"  Has weight reference: {'✅' if has_weight else '❌'}")
        print(f"  Has diameter reference: {'✅' if has_diameter else '❌'}")
        print(f"  Has Nijora table (tablepress-1): {'✅' if has_nijora_table else '❌'}")
        print(f"  Has Nijora tab (woocommerce): {'✅' if has_nijora_tab else '❌'}")
        print(f"  Has rundlaufgenauigkeit: {'✅' if has_rundlauf else '❌'}")
        
        # Check content length and positioning
        total_chars = len(markdown_content)
        if total_chars > 15000:
            print(f"\n⚠️  Content is {total_chars:,} characters (> 15k limit)")
            print(f"Content beyond 15k characters might be truncated in extraction")
            
            # Check where key terms appear relative to 15k limit
            for term, data in found_terms.items():
                md_positions = data['markdown_positions']
                if md_positions:
                    positions_beyond_15k = [pos for pos in md_positions if pos > 15000]
                    if positions_beyond_15k:
                        print(f"  ⚠️  '{term}' appears beyond 15k limit at positions: {positions_beyond_15k}")
        
        # Provide recommendations
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}")
        
        if not (has_spine or has_weight or has_nijora_table or has_nijora_tab):
            print("🔴 CRITICAL: No key detection terms found!")
            print("   This explains why extraction is failing.")
            print("   The page might not contain specification data,")
            print("   or the terms might be in a different format.")
        
        if has_nijora_table or has_nijora_tab:
            print("🟡 Nijora-specific containers found.")
            print("   Extraction should target these specific sections.")
            
        if total_chars > 15000:
            print("🟡 Content exceeds 15k character limit.")
            print("   Consider using targeted extraction around key terms.")
        
        # Show a sample of the raw content for manual inspection
        print(f"\n{'='*60}")
        print("RAW CONTENT SAMPLE (First 2000 characters)")
        print(f"{'='*60}")
        print(markdown_content[:2000])
        print("... [TRUNCATED]")
        
        if total_chars > 2000:
            print(f"\n{'='*60}")
            print("RAW CONTENT SAMPLE (Last 1000 characters)")
            print(f"{'='*60}")
            print("..." + markdown_content[-1000:])

if __name__ == "__main__":
    asyncio.run(debug_nijora_nigan())