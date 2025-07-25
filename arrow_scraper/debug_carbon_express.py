#!/usr/bin/env python3
"""
Debug Carbon Express URL to understand image-based specifications.
Testing: https://www.feradyne.com/product/maxima-sable-rz/

This script will:
1. Crawl the page and examine the content structure
2. Look for images that might contain specification data
3. Find references to specification charts/images
4. Analyze why text extraction is failing
5. Identify image URLs containing spine data
"""

import asyncio
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler

async def debug_carbon_express():
    """Debug Carbon Express page to understand image-based specifications"""
    
    url = "https://www.feradyne.com/product/maxima-sable-rz/"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        print(f"{'='*80}")
        print(f"DEBUGGING CARBON EXPRESS MAXIMA SABLE RZ")
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
        
        # Search for specification-related images
        print(f"\n{'='*60}")
        print("SEARCHING FOR SPECIFICATION IMAGES")
        print(f"{'='*60}")
        
        # Look for image tags with specification-related content
        img_patterns = [
            r'<img[^>]*src="[^"]*\.(?:png|jpg|jpeg|gif|svg)[^"]*"[^>]*>',
            r'<img[^>]*title="[^"]*(?:spec|chart|table|data)[^"]*"[^>]*>',
            r'<img[^>]*alt="[^"]*(?:spec|chart|table|data)[^"]*"[^>]*>'
        ]
        
        all_images = []
        for pattern in img_patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            for match in matches:
                all_images.append(match.group())
        
        # Remove duplicates while preserving order
        unique_images = []
        seen = set()
        for img in all_images:
            if img not in seen:
                unique_images.append(img)
                seen.add(img)
        
        print(f"Found {len(unique_images)} unique images")
        
        # Analyze each image for potential specification data
        spec_images = []
        for i, img_tag in enumerate(unique_images):
            print(f"\nImage {i+1}:")
            print(f"  Tag: {img_tag[:150]}...")
            
            # Extract src URL
            src_match = re.search(r'src="([^"]*)"', img_tag, re.IGNORECASE)
            if src_match:
                src_url = src_match.group(1)
                print(f"  URL: {src_url}")
                
                # Check if URL suggests specification data
                spec_indicators = ['spec', 'chart', 'table', 'data', 'spine', 'gpi', 'maxima', 'triad', 'arrow']
                url_lower = src_url.lower()
                matching_indicators = [ind for ind in spec_indicators if ind in url_lower]
                
                if matching_indicators:
                    print(f"  ✅ Potential spec image (contains: {', '.join(matching_indicators)})")
                    spec_images.append((src_url, img_tag, matching_indicators))
                else:
                    print(f"  ❌ Unlikely spec image")
            else:
                print(f"  ⚠️  No src URL found")
        
        # Look for div containers that might contain spec images
        print(f"\n{'='*60}")
        print("SEARCHING FOR ELEMENTOR WIDGET CONTAINERS")
        print(f"{'='*60}")
        
        elementor_pattern = r'<div class="elementor-widget-container"[^>]*>.*?</div>'
        elementor_matches = re.finditer(elementor_pattern, html_content, re.IGNORECASE | re.DOTALL)
        elementor_list = list(elementor_matches)
        
        if elementor_list:
            print(f"Found {len(elementor_list)} elementor widget containers")
            
            for i, match in enumerate(elementor_list[:10]):  # Show first 10
                container_content = match.group()
                
                # Check if this container has images
                img_in_container = re.findall(r'<img[^>]*>', container_content, re.IGNORECASE)
                
                if img_in_container:
                    print(f"\nElementor Container {i+1} (with {len(img_in_container)} images):")
                    print(f"  Position: {match.start():,}")
                    print(f"  Content preview: {container_content[:300]}...")
                    
                    # Check for spec-related content
                    container_lower = container_content.lower()
                    spec_terms = ['spec', 'spine', 'gpi', 'chart', 'table', 'maxima', 'triad']
                    found_terms = [term for term in spec_terms if term in container_lower]
                    
                    if found_terms:
                        print(f"  ✅ Contains spec terms: {', '.join(found_terms)}")
                    
                    # Show images in this container
                    for j, img in enumerate(img_in_container):
                        src_match = re.search(r'src="([^"]*)"', img)
                        if src_match:
                            print(f"    Image {j+1}: {src_match.group(1)}")
        else:
            print("No elementor widget containers found")
        
        # Search for text-based specifications as fallback
        print(f"\n{'='*60}")
        print("SEARCHING FOR TEXT-BASED SPECIFICATIONS")
        print(f"{'='*60}")
        
        spec_terms = ['spine', 'gpi', 'grain', 'weight', 'diameter', 'deflection', 'stiffness']
        
        for term in spec_terms:
            positions = []
            start = 0
            while True:
                pos = markdown_content.lower().find(term, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            if positions:
                print(f"\n✅ Found '{term}': {len(positions)} occurrences")
                # Show context for first occurrence
                pos = positions[0]
                context_start = max(0, pos - 150)
                context_end = min(len(markdown_content), pos + 150)
                context = markdown_content[context_start:context_end].replace('\n', ' ')
                print(f"  First context: ...{context}...")
            else:
                print(f"❌ Not found: '{term}'")
        
        # Summary and recommendations
        print(f"\n{'='*60}")
        print("ANALYSIS SUMMARY")
        print(f"{'='*60}")
        
        if spec_images:
            print(f"🎯 FOUND {len(spec_images)} POTENTIAL SPECIFICATION IMAGES:")
            for src_url, img_tag, indicators in spec_images:
                print(f"  • {src_url}")
                print(f"    Indicators: {', '.join(indicators)}")
        else:
            print("🔴 No clear specification images found")
        
        print(f"\n📋 RECOMMENDATIONS:")
        if spec_images:
            print("  1. Carbon Express uses image-based specification charts")
            print("  2. Text extraction will not work for this manufacturer")
            print("  3. OCR (Optical Character Recognition) would be needed to extract data from images")
            print("  4. Alternative: Manual data entry or API from manufacturer")
        else:
            print("  1. No obvious specification images found")
            print("  2. Data might be in JavaScript/dynamic content")
            print("  3. Try examining the page with browser developer tools")

if __name__ == "__main__":
    asyncio.run(debug_carbon_express())