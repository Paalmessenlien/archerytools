#!/usr/bin/env python3
"""
Analyze page content to see if it contains arrow specifications
"""

import asyncio
from crawl4ai import AsyncWebCrawler

async def analyze_page_content():
    """Analyze the content of an arrow page to see what's there"""
    print("Analyzing Arrow Page Content")
    print("=" * 40)
    
    test_url = "https://eastonarchery.com/arrows_/4mm-axis-long-range-match-grade/"
    print(f"🔗 Analyzing: {test_url}")
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(url=test_url, bypass_cache=True)
        
        if result.success:
            content = result.markdown
            print(f"✅ Page crawled: {len(content)} characters")
            
            # Look for arrow-related keywords
            keywords = [
                "spine", "gpi", "grains", "diameter", "inches", 
                "specifications", "tech spec", "features",
                "carbon", "hunting", "target", "indoor", "outdoor"
            ]
            
            print("\n🔍 Keyword Analysis:")
            for keyword in keywords:
                count = content.lower().count(keyword.lower())
                if count > 0:
                    print(f"   {keyword}: {count} occurrences")
            
            # Look for numbers that might be spine values
            import re
            spine_pattern = r'\b(150|200|250|300|340|400|500|600|700|800|900|1000)\b'
            spine_matches = re.findall(spine_pattern, content)
            if spine_matches:
                print(f"\n🎯 Potential spine values found: {set(spine_matches)}")
            
            # Look for diameter measurements
            diameter_pattern = r'\b0\.\d{3}\b'
            diameter_matches = re.findall(diameter_pattern, content)
            if diameter_matches:
                print(f"📏 Potential diameter values: {set(diameter_matches)}")
            
            # Look for GPI values
            gpi_pattern = r'\b\d+\.\d+\s*gpi\b'
            gpi_matches = re.findall(gpi_pattern, content, re.IGNORECASE)
            if gpi_matches:
                print(f"⚖️  Potential GPI values: {set(gpi_matches)}")
            
            # Show sections that might contain specs
            spec_sections = []
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if any(word in line.lower() for word in ['specification', 'tech spec', 'features', 'details']):
                    # Get surrounding context
                    start = max(0, i-2)
                    end = min(len(lines), i+10)
                    section = '\n'.join(lines[start:end])
                    spec_sections.append(section)
            
            if spec_sections:
                print(f"\n📋 Found {len(spec_sections)} potential specification sections:")
                for i, section in enumerate(spec_sections[:2]):  # Show first 2
                    print(f"\nSection {i+1}:")
                    print("-" * 30)
                    print(section[:500])
                    print("-" * 30)
            else:
                print("\n⚠️  No obvious specification sections found")
                
                # Show a sample of the content to understand structure
                print("\n📄 Sample content (middle section):")
                print("-" * 40)
                mid_point = len(content) // 2
                sample = content[mid_point:mid_point+1000]
                print(sample)
                print("-" * 40)
        else:
            print(f"❌ Failed to crawl: {result.error_message}")

def main():
    """Run the analysis"""
    asyncio.run(analyze_page_content())

if __name__ == "__main__":
    main()