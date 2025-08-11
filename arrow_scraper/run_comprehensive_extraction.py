#!/usr/bin/env python3
"""
Run comprehensive extraction using the updated spine-specific model
with direct API calls to avoid Crawl4AI LLM issues
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import requests
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from models import ArrowSpecification, SpineSpecification, ManufacturerData, ScrapingSession, ScrapingResult

class DirectLLMExtractor:
    """Extractor that uses direct API calls to DeepSeek"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Create images directory
        self.images_dir = Path("data/images")
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def download_image(self, image_url: str, manufacturer: str, model_name: str, image_type: str = "primary") -> str:
        """Download image and return local path"""
        try:
            # Create safe filename
            safe_manufacturer = "".join(c for c in manufacturer if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            safe_model = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            
            # Get file extension from URL
            parsed_url = urlparse(image_url)
            file_ext = Path(parsed_url.path).suffix
            if not file_ext:
                file_ext = '.jpg'  # Default extension
            
            # Create local filename
            filename = f"{safe_manufacturer}_{safe_model}_{image_type}{file_ext}"
            local_path = self.images_dir / filename
            
            # Download image
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"📸 Downloaded image: {filename}")
            return str(local_path)
            
        except Exception as e:
            print(f"⚠️ Failed to download image {image_url}: {e}")
            return None
    
    def extract_arrow_data(self, content: str, url: str) -> List[ArrowSpecification]:
        """Extract arrow data using direct API call"""
        
        # Look for table data in content
        content_lower = content.lower()
        has_spine = "spine" in content_lower
        has_weight = "gpi" in content_lower or "grain" in content_lower or "weight" in content_lower
        
        # Gold Tip specific detection
        has_goldtip_specs = "specs specs-loaded" in content_lower or "card-body p-0" in content_lower
        
        # Nijora specific detection (German content)
        has_nijora_table = ("tablepress-" in content_lower or 
                           ("grain/inch" in content_lower and "zoll" in content_lower) or
                           ("woocommerce-tabs-panel--wd_custom_tab" in content_lower and "rundlaufgenauigkeit" in content_lower) or
                           ("technische daten" in content_lower and "rundlaufgenauigkeit" in content_lower))
        
        # DK Bow specific detection (German content)
        has_dk_table = ("offcanvas-body" in content_lower and "rundlaufgenauigkeit" in content_lower and "sw-text-editor-table" in content_lower)
        
        # BigArchery specific detection (Italian/European content)
        has_bigarchery_specs = ("grani" in content_lower and "diameter:" in content_lower) or ("bigarchery.com" in url.lower() and "mm" in content_lower and any(str(spine) in content_lower for spine in [500, 600, 700, 800, 900, 1000]))
        
        # Allow specific manufacturer content even if general detection fails
        if not (has_spine or has_weight or has_goldtip_specs or has_nijora_table or has_dk_table or has_bigarchery_specs):
            print(f"⚠️  No spine/weight data found in content for {url} (spine: {has_spine}, weight: {has_weight}, goldtip: {has_goldtip_specs}, nijora: {has_nijora_table}, dk: {has_dk_table}, bigarchery: {has_bigarchery_specs})")
            return []
        
        # Debug: Show where spine/GPI data is found
        spine_pos = content.lower().find("spine")
        gpi_pos = content.lower().find("gpi")
        specs_pos = content.lower().find("specs specs-loaded")
        tablepress_pos = content.lower().find("tablepress-")
        nijora_tab_pos = content.lower().find("woocommerce-tabs-panel--wd_custom_tab")
        rundlauf_pos = content.lower().find("rundlaufgenauigkeit")
        tech_daten_pos = content.lower().find("technische daten")
        offcanvas_pos = content.lower().find("offcanvas-body")
        sw_table_pos = content.lower().find("sw-text-editor-table")
        print(f"🔍 Debug: Found 'spine' at position {spine_pos}, 'gpi' at position {gpi_pos}, 'specs' at position {specs_pos}, 'tablepress' at position {tablepress_pos}, 'nijora_tab' at position {nijora_tab_pos}, 'rundlauf' at position {rundlauf_pos}, 'tech_daten' at position {tech_daten_pos}, 'offcanvas' at position {offcanvas_pos}, 'sw_table' at position {sw_table_pos}")
        
        # Show the content around the table
        if spine_pos > -1:
            table_content = content[max(0, spine_pos-200):spine_pos+1000]
            print(f"📋 Table content preview:\n{table_content[:500]}...")
        elif specs_pos > -1:
            table_content = content[max(0, specs_pos-200):specs_pos+1000]
            print(f"📋 Specs content preview:\n{table_content[:500]}...")
        elif tablepress_pos > -1:
            table_content = content[max(0, tablepress_pos-200):tablepress_pos+1000]
            print(f"📋 Nijora table preview:\n{table_content[:500]}...")
        elif offcanvas_pos > -1:
            table_content = content[max(0, offcanvas_pos-200):offcanvas_pos+1000]
            print(f"📋 DK offcanvas preview:\n{table_content[:500]}...")
        
        # Special handling for Nijora - target tablepress content or tab content
        if "nijora" in url.lower():
            # Priority 1: Look for tablepress table (any ID)
            if tablepress_pos > -1:
                # Found tablepress table, extract larger content around it
                content_to_send = content[max(0, tablepress_pos-2000):tablepress_pos+25000]
                print(f"🔢 Nijora: Sending {len(content_to_send)} chars from tablepress section (pos {tablepress_pos})")
            # Priority 2: Look for WooCommerce tab content
            elif nijora_tab_pos > -1:
                # Found Nijora tab content, extract large section around it
                content_to_send = content[max(0, nijora_tab_pos-2000):nijora_tab_pos+30000]
                print(f"🔢 Nijora: Sending {len(content_to_send)} chars from tab section (pos {nijora_tab_pos})")
            # Priority 3: Look for "Technische Daten" section
            elif tech_daten_pos > -1:
                # Found technical data section, extract around it
                content_to_send = content[max(0, tech_daten_pos-5000):tech_daten_pos+25000]
                print(f"🔢 Nijora: Sending {len(content_to_send)} chars from tech_daten section (pos {tech_daten_pos})")
            # Priority 4: Look for rundlaufgenauigkeit (German straightness term)
            elif rundlauf_pos > -1:
                # Found rundlaufgenauigkeit, extract large section around it  
                content_to_send = content[max(0, rundlauf_pos-10000):rundlauf_pos+20000]
                print(f"🔢 Nijora: Sending {len(content_to_send)} chars from rundlauf section (pos {rundlauf_pos})")
            else:
                # Fallback: send larger section to catch hidden content
                content_to_send = content[5000:35000] if len(content) > 35000 else content
                print(f"🔢 Nijora: Sending expanded section {len(content_to_send)} chars (comprehensive search)")
        # Special handling for DK Bow - target offcanvas content with sw-text-editor-table
        elif "dk" in url.lower() or "dkbow" in url.lower():
            if offcanvas_pos > -1:
                # Found offcanvas body, extract large content around it
                content_to_send = content[max(0, offcanvas_pos-1000):offcanvas_pos+20000]
                print(f"🔢 DK Bow: Sending {len(content_to_send)} chars from offcanvas section (pos {offcanvas_pos})")
            elif sw_table_pos > -1:
                # Found sw-text-editor-table, extract around it
                content_to_send = content[max(0, sw_table_pos-5000):sw_table_pos+15000]
                print(f"🔢 DK Bow: Sending {len(content_to_send)} chars from sw-table section (pos {sw_table_pos})")
            elif rundlauf_pos > -1:
                # Found rundlaufgenauigkeit, extract around it
                content_to_send = content[max(0, rundlauf_pos-5000):rundlauf_pos+15000]
                print(f"🔢 DK Bow: Sending {len(content_to_send)} chars from rundlauf section (pos {rundlauf_pos})")
            else:
                # Fallback: send middle section
                content_to_send = content[3000:25000] if len(content) > 25000 else content
                print(f"🔢 DK Bow: Sending middle section {len(content_to_send)} chars (looking for tables)")
        # Special handling for Gold Tip - specs are typically at ~117k position
        elif "goldtip.com" in url.lower():
            # Look for specCard or specs sections much further in content
            speccard_pos = content.lower().find('speccard')
            table_striped_pos = content.lower().find('table table-striped')
            
            if speccard_pos > -1:
                # Found specCard, extract content around it
                content_to_send = content[max(0, speccard_pos-1000):speccard_pos+15000]
                print(f"🔢 Gold Tip: Sending {len(content_to_send)} chars from specCard section (pos {speccard_pos})")
            elif table_striped_pos > -1:
                # Found table, extract content around it
                content_to_send = content[max(0, table_striped_pos-2000):table_striped_pos+10000]
                print(f"🔢 Gold Tip: Sending {len(content_to_send)} chars from table section (pos {table_striped_pos})")
            else:
                # Fallback: send larger chunk of content for Gold Tip
                content_to_send = content[-30000:]  # Last 30k chars where specs usually are
                print(f"🔢 Gold Tip: Sending last {len(content_to_send)} chars (specs typically at end)")
        # Special handling for BigArchery - specs around "diameter:" section
        elif "bigarchery.com" in url.lower():
            # Look for diameter section which contains specifications
            diameter_pos = content.lower().find("diameter:")
            grani_pos = content.lower().find("grani")
            
            if diameter_pos > -1:
                # Found diameter section, extract content around it
                content_to_send = content[max(0, diameter_pos-1000):diameter_pos+5000]
                print(f"🔢 BigArchery: Sending {len(content_to_send)} chars from diameter section (pos {diameter_pos})")
            elif grani_pos > -1:
                # Found grani (Italian grains), extract around it
                content_to_send = content[max(0, grani_pos-2000):grani_pos+8000]
                print(f"🔢 BigArchery: Sending {len(content_to_send)} chars from grani section (pos {grani_pos})")
            else:
                # Fallback: send middle section where specs typically are
                content_to_send = content[4000:12000] if len(content) > 12000 else content
                print(f"🔢 BigArchery: Sending middle section {len(content_to_send)} chars (specs search)")
        else:
            # Original logic for other manufacturers
            slice_pos = specs_pos if specs_pos > -1 else spine_pos
            
            # Ensure we include the table data - start from where data begins
            if slice_pos > 10000:
                # Table is far into the content, send from position onwards
                content_to_send = content[max(0, slice_pos-1000):slice_pos+10000]
                print(f"🔢 Adjusted content slice: sending {len(content_to_send)} chars starting near table data")
            else:
                content_to_send = content[:15000]
                spine_check = content_to_send.lower().find('spine')
                specs_check = content_to_send.lower().find('specs specs-loaded')
                print(f"🔢 Sending {len(content_to_send)} chars to API (spine at {spine_check}, specs at {specs_check})")
        
        # Determine manufacturer-specific instructions
        manufacturer_hints = ""
        if "skylonarchery.com" in url.lower():
            manufacturer_hints = """
        SKYLON-SPECIFIC INSTRUCTIONS:
        - Look for <article class="uk-article"> sections
        - Find tables with columns: SPINE, OUTSIDE DIAMETER, GRAIN PER INCH, LENGTH
        - Spine values are in decimal format like 0.500", 0.400", 0.350"
        - Convert spine decimals to integers (0.500" = 500, 0.400" = 400)
        - Diameters are in mm, convert to inches (divide by 25.4)
        - Material info is often listed above the table
        """
        elif "eastonarchery.com" in url.lower():
            manufacturer_hints = """
        EASTON-SPECIFIC INSTRUCTIONS:
        - Look for HTML tables with spine specifications
        - Find columns: Size/Spine, GPI, O.D./Diameter, Length
        - Spine values are integers (250, 300, 340, 400, 500, etc.)
        - Diameters are already in inches
        """
        elif "goldtip.com" in url.lower():
            manufacturer_hints = """
        GOLD TIP-SPECIFIC INSTRUCTIONS:
        - Look for <div class="card-body p-0"> containing <div class="specs specs-loaded">
        - Find HTML tables with columns: SPINE, GPI, OD, LENGTH
        - Spine values are integers (300, 340, 400, 500, etc.)
        - GPI values are decimal (7.3, 8.2, 8.9, etc.)
        - Diameters may be HTML encoded: .291&quot; or .291" (already in inches, decode &quot; to " and remove quotes)
        - Lengths may be HTML encoded: 30&quot; or 30" (decode &quot; to " and remove quotes, convert to float)
        - IMPORTANT: Each spine should have its own length_options array with the LENGTH value from that row
        - Example: spine 500 with length 30" should have "length_options": [30.0]
        - Example: spine 400 with length 32" should have "length_options": [32.0]
        """
        elif "victoryarchery.com" in url.lower():
            manufacturer_hints = """
        VICTORY ARCHERY-SPECIFIC INSTRUCTIONS:
        - Look for technical specifications sections
        - May have spine and weight information in product details
        """
        elif "nijora" in url.lower():
            manufacturer_hints = """
        NIJORA-SPECIFIC INSTRUCTIONS (German website):
        - Look for tabbed content: <div class="woocommerce-Tabs-panel--wd_custom_tab"> containing specification table
        - Find <table id="tablepress-*" class="tablepress"> within the tab content (ID varies: tablepress-1, tablepress-21, etc.)
        - Table structure: 6 columns with headers: Spine, GPI (Grain/Inch), ID (Zoll/mm), AD (mm), Rundlaufgenauigkeit, Länge
        - Content may be in hidden tabs or deep in the page (beyond 100k+ characters)
        - SPINE PARSING: Remove color text in parentheses. Examples:
          * "400 (white)" → spine: 400
          * "500 (yellow, orange, blue, pink)" → spine: 500  
          * "800-S (yellow, orange)" → spine: 800
          * "1000-S (pink, yellow, orange-white, blue, green, red, cyan)" → spine: 1000
          * "1200-S (pink, yellow, orange, cyan)" → spine: 1200
        - GPI VALUES: German decimal comma notation "9,50" = 9.50, "8,80" = 8.80
        - OUTER DIAMETER: "AD (mm)" column contains mm values (7,55 = 7.55mm), convert to inches (÷ 25.4)
        - INNER DIAMETER: "ID (Zoll/mm)" format "0,245 Zoll / 6,22 mm" - use Zoll value (0.245)
        - LENGTH: "Länge" format "32 Zoll / 81,28 cm" - use Zoll value (32.0)
        - STRAIGHTNESS: "Rundlaufgenauigkeit" column shows "0,006\"" straightness tolerance
        - German decimal conversion: Replace commas with dots for JSON: "9,50" → 9.50
        """
        elif "bigarchery.com" in url.lower():
            manufacturer_hints = """
        BIGARCHERY-SPECIFIC INSTRUCTIONS (Italian/European website):
        - Look for product description sections containing specification data
        - Find spine data pattern: spine_value weight_value length" Ø inner_diameter Ø outer_diameter weight_unit
        - Example format: "500 8.1 33" Ø 4.2 mm / .165" Ø 5,86 mm 100 grani Ø 5,95 mm"
        - SPINE VALUES: Direct integers (500, 600, 700, 800, 900, 1000, 1100, 1300, 1500, 1800)
        - WEIGHT VALUES: Decimal values (8.1, 7.0, 6.3, 5.9) - these are GPI weights
        - OUTER DIAMETER: Format like "Ø 5,86 mm" - use European comma notation, convert to inches (÷ 25.4)
        - INNER DIAMETER: Format like "Ø 4.2 mm" - convert to inches (÷ 25.4)
        - LENGTH: Format like "33"" - remove quotes, use as float
        - WEIGHT UNIT: "grani" = Italian for grains = GPI (grains per inch)
        - European decimal conversion: "5,86" → 5.86, "4,2" → 4.2
        - Content includes "Length: 33", diameter: 4.2 mm" followed by spine specifications
        """
        elif "dk" in url.lower() or "dkbow" in url.lower():
            manufacturer_hints = """
        DK BOW-SPECIFIC INSTRUCTIONS (German website):
        - Look for <div class="offcanvas-body"> containing product details and specifications
        - Find <table class="sw-text-editor-table"> within the content
        - Table structure: 3 columns with headers: Spine, outer (outer diameter), GPI
        - Table rows contain: spine value (e.g., 500, 600, 700), outer diameter in mm (e.g., 5,40), GPI weight (e.g., 5,20)
        - SPINE VALUES: Direct integers (500, 600, 700, 800, 900, 1000)
        - OUTER DIAMETER: German decimal comma notation in mm "5,40" = 5.40mm, convert to inches (÷ 25.4)
        - GPI VALUES: German decimal comma notation "5,20" = 5.20 GPI weight
        - German terms: "RUNDLAUFGENAUIGKEIT" = straightness tolerance, "outer" = outer diameter
        - Convert German decimals: "5,40" → 5.40, "4,70" → 4.70
        - Content is in German product descriptions with detailed technical information
        """
        
        prompt = f"""
        Extract arrow specifications from this webpage content for {url}.
        
        INSTRUCTIONS:
        1. Look for tables, specifications, or structured data about arrow models
        2. Find data for: Spine/Stiffness values, Weight (GPI/grains per inch), Diameter, Lengths
        3. Find image URLs for arrow product photos (look for img tags with arrow/product images)
        4. Each spine value should have its own specification entry with its own length_options array
        5. Handle HTML entities: decode &quot; to ", &amp; to &, etc. before parsing values
        6. Return ONLY valid JSON, no markdown formatting
        7. If no spine-specific data is found, return empty arrows array
        
        {manufacturer_hints}
        
        COMMON DATA LOCATIONS:
        - HTML tables with columns: Spine, GPI, Diameter, O.D., Weight, Length
        - Product specification lists within <article> sections
        - Technical specification sections
        - Size/specification charts
        
        CONVERSION NOTES:
        - If spine is in decimal format (0.500"), convert to integer (500)
        - If diameter is in mm, convert to inches (mm ÷ 25.4)
        - If diameter is already in inches, use as-is
        
        Return JSON in this exact format:
        {{
            "arrows": [
                {{
                    "model_name": "Arrow Model Name",
                    "manufacturer": "Manufacturer Name",
                    "spine_specifications": [
                        {{
                            "spine": 500,
                            "gpi_weight": 7.27,
                            "outer_diameter": 0.353,
                            "inner_diameter": null,
                            "length_options": [33.0]
                        }}
                    ],
                    "material": "24-TON 3K Carbon",
                    "arrow_type": "target",
                    "description": "Brief description",
                    "primary_image_url": "https://example.com/arrow-main.jpg",
                    "gallery_images": ["https://example.com/arrow-1.jpg", "https://example.com/arrow-2.jpg"]
                }}
            ]
        }}
        """
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a data extraction specialist. Return only valid JSON, no markdown."},
                {"role": "user", "content": f"{prompt}\n\nWebpage content:\n{content_to_send}"}  # Use adjusted content
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60  # Increased timeout for complex extractions
            )
            
            if response.status_code != 200:
                print(f"❌ API call failed: {response.status_code}")
                return []
            
            result = response.json()
            if 'choices' not in result or len(result['choices']) == 0:
                print("❌ No choices in API response")
                return []
            
            content = result['choices'][0]['message']['content'].strip()
            
            # Remove markdown code block formatting if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            data = json.loads(content)
            arrows = []
            
            for arrow_data in data.get('arrows', []):
                try:
                    # Convert spine specifications with deduplication
                    spine_specs = []
                    seen_spines = set()
                    for spec_data in arrow_data.get('spine_specifications', []):
                        # Validate required fields
                        if not all(key in spec_data and spec_data[key] is not None 
                                 for key in ['spine', 'outer_diameter', 'gpi_weight']):
                            print(f"⚠️  Skipping incomplete spine spec: {spec_data}")
                            continue
                        
                        spine_value = spec_data['spine']
                        if spine_value in seen_spines:
                            print(f"⚠️  Skipping duplicate spine value: {spine_value}")
                            continue
                        
                        seen_spines.add(spine_value)
                        spine_spec = SpineSpecification(
                            spine=spine_value,
                            outer_diameter=spec_data['outer_diameter'],
                            gpi_weight=spec_data['gpi_weight'],
                            inner_diameter=spec_data.get('inner_diameter'),
                            length_options=spec_data.get('length_options')
                        )
                        spine_specs.append(spine_spec)
                    
                    if spine_specs:  # Only create arrow if we have spine specifications
                        # Handle image downloads
                        saved_images = []
                        primary_image_url = arrow_data.get('primary_image_url')
                        gallery_images = arrow_data.get('gallery_images', [])
                        
                        # Download primary image
                        if primary_image_url:
                            # Convert relative URLs to absolute
                            if primary_image_url.startswith('/'):
                                primary_image_url = urljoin(url, primary_image_url)
                            
                            if primary_image_url.startswith('http'):
                                local_path = self.download_image(
                                    primary_image_url, 
                                    arrow_data.get('manufacturer', 'Unknown'),
                                    arrow_data['model_name'],
                                    "primary"
                                )
                                if local_path:
                                    saved_images.append(local_path)
                        
                        # Download gallery images (limit to first 3 to avoid too many downloads)
                        for i, gallery_url in enumerate(gallery_images[:3]):
                            if gallery_url.startswith('/'):
                                gallery_url = urljoin(url, gallery_url)
                            
                            if gallery_url.startswith('http'):
                                local_path = self.download_image(
                                    gallery_url,
                                    arrow_data.get('manufacturer', 'Unknown'),
                                    arrow_data['model_name'],
                                    f"gallery_{i+1}"
                                )
                                if local_path:
                                    saved_images.append(local_path)
                        
                        # Map invalid arrow types to valid ones
                        arrow_type = arrow_data.get('arrow_type')
                        if arrow_type:
                            arrow_type_lower = arrow_type.lower()
                            if 'universal' in arrow_type_lower or 'carbonshaft' in arrow_type_lower:
                                arrow_type = 'target'  # Default for universal carbon shafts
                            elif 'jagd' in arrow_type_lower or 'hunting' in arrow_type_lower:
                                arrow_type = 'hunting'
                            elif 'target' in arrow_type_lower or 'ziel' in arrow_type_lower:
                                arrow_type = 'target'
                            elif '3d' in arrow_type_lower:
                                arrow_type = '3d'
                            elif 'indoor' in arrow_type_lower or 'halle' in arrow_type_lower:
                                arrow_type = 'indoor'
                            elif 'outdoor' in arrow_type_lower:
                                arrow_type = 'outdoor'
                            elif 'recreational' in arrow_type_lower or 'freizeit' in arrow_type_lower:
                                arrow_type = 'recreational'
                            else:
                                arrow_type = 'target'  # Default fallback
                        
                        arrow = ArrowSpecification(
                            model_name=arrow_data['model_name'],
                            manufacturer=arrow_data.get('manufacturer', 'Easton'),
                            spine_specifications=spine_specs,
                            material=arrow_data.get('material'),
                            arrow_type=arrow_type,
                            description=arrow_data.get('description'),
                            primary_image_url=primary_image_url,
                            gallery_images=gallery_images,
                            saved_images=saved_images if saved_images else None,
                            source_url=url
                        )
                        arrows.append(arrow)
                        
                except Exception as e:
                    print(f"⚠️  Error processing arrow data: {e}")
                    continue
            
            return arrows
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Response content: {content[:500]}...")
            return []
        except Exception as e:
            print(f"💥 Extraction error: {e}")
            return []

async def run_comprehensive_extraction():
    """Run extraction on all manufacturer URLs"""
    print("🚀 Running Comprehensive Arrow Extraction")
    print("=" * 45)
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    # Load all manufacturer URLs from the existing file
    sys.path.append(str(Path(__file__).parent))
    from scrape_all_manufacturers import ComprehensiveArrowScraper
    
    # Create a temporary scraper to get the URLs
    temp_scraper = ComprehensiveArrowScraper(api_key)
    all_urls = []
    
    # Collect all URLs from all manufacturers
    for manufacturer_name, manufacturer_data in temp_scraper.manufacturers.items():
        manufacturer_urls = manufacturer_data.get("product_urls", [])
        print(f"📊 {manufacturer_name}: {len(manufacturer_urls)} URLs")
        all_urls.extend([(url, manufacturer_name) for url in manufacturer_urls])
    
    print(f"\n🎯 Total URLs to process: {len(all_urls)}")
    print(f"🏭 Manufacturers: {len(temp_scraper.manufacturers)}")
    
    # For initial run, process a smaller subset to avoid overwhelming the API
    # You can increase this batch size once confident it's working
    batch_size = 20  # Start with first 20 URLs for stability
    urls_to_process = all_urls[:batch_size]
    print(f"📦 Processing batch of {len(urls_to_process)} URLs")
    
    extractor = DirectLLMExtractor(api_key)
    all_arrows = []
    
    # Statistics tracking
    manufacturer_stats = {}
    failed_urls = []
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        for i, (url, manufacturer_name) in enumerate(urls_to_process, 1):
            print(f"\n🔗 [{i}/{len(urls_to_process)}] {manufacturer_name}: {url}")
            
            # Initialize manufacturer stats
            if manufacturer_name not in manufacturer_stats:
                manufacturer_stats[manufacturer_name] = {"processed": 0, "successful": 0, "arrows": 0}
            
            manufacturer_stats[manufacturer_name]["processed"] += 1
            
            try:
                # Crawl the page
                result = await crawler.arun(url=url, bypass_cache=True)
                
                if not result.success:
                    print(f"❌ Failed to crawl {url}")
                    failed_urls.append((url, manufacturer_name, "Crawl failed"))
                    continue
                
                print(f"✓ Crawled successfully ({len(result.markdown)} chars)")
                
                # Extract arrow data
                arrows = extractor.extract_arrow_data(result.markdown, url)
                
                if arrows:
                    manufacturer_stats[manufacturer_name]["successful"] += 1
                    manufacturer_stats[manufacturer_name]["arrows"] += len(arrows)
                    print(f"🎯 Found {len(arrows)} arrows")
                    for arrow in arrows:
                        print(f"   - {arrow.model_name}: {len(arrow.spine_specifications)} spine options")
                    all_arrows.extend(arrows)
                else:
                    print("❌ No arrows extracted")
                    failed_urls.append((url, manufacturer_name, "No data extracted"))
                
                # Rate limiting - important for large scale
                await asyncio.sleep(5)  # Increased delay for stability
                
            except Exception as e:
                print(f"💥 Error processing {url}: {e}")
                failed_urls.append((url, manufacturer_name, str(e)))
                continue
    
    # Save results
    if all_arrows:
        print(f"\n💾 Saving {len(all_arrows)} total arrows...")
        
        # Save to JSON
        output_data = {
            "extraction_timestamp": datetime.now().isoformat(),
            "total_arrows": len(all_arrows),
            "arrows": [arrow.model_dump(mode='json') for arrow in all_arrows]
        }
        
        output_file = Path("data/processed/comprehensive_extraction_results.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✅ Results saved to {output_file}")
        
        # Summary
        print(f"\n📊 COMPREHENSIVE EXTRACTION SUMMARY:")
        print(f"   Total arrows extracted: {len(all_arrows)}")
        print(f"   Unique models: {len(set(arrow.model_name for arrow in all_arrows))}")
        print(f"   URLs processed: {len(urls_to_process)}")
        print(f"   Failed URLs: {len(failed_urls)}")
        print(f"   Success rate: {((len(urls_to_process) - len(failed_urls)) / len(urls_to_process) * 100):.1f}%")
        
        # Manufacturer breakdown
        print(f"\n🏭 MANUFACTURER BREAKDOWN:")
        for manufacturer, stats in manufacturer_stats.items():
            success_rate = (stats["successful"] / stats["processed"] * 100) if stats["processed"] > 0 else 0
            print(f"   {manufacturer}:")
            print(f"     URLs processed: {stats['processed']}")
            print(f"     Successful extractions: {stats['successful']}")
            print(f"     Arrows found: {stats['arrows']}")
            print(f"     Success rate: {success_rate:.1f}%")
        
        # Spine distribution
        spine_counts = {}
        for arrow in all_arrows:
            count = len(arrow.spine_specifications)
            spine_counts[count] = spine_counts.get(count, 0) + 1
        
        print(f"\n🎯 SPINE SPECIFICATION DISTRIBUTION:")
        for count, freq in sorted(spine_counts.items()):
            print(f"     {count} spine options: {freq} arrows")
        
        # Failed URLs summary
        if failed_urls:
            print(f"\n❌ FAILED URLS SUMMARY:")
            failure_reasons = {}
            for url, manufacturer, reason in failed_urls:
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
            
            for reason, count in failure_reasons.items():
                print(f"     {reason}: {count} URLs")
        
        # Save failed URLs for retry
        if failed_urls:
            failed_file = Path("data/processed/failed_urls.json")
            failed_data = {
                "timestamp": datetime.now().isoformat(),
                "total_failed": len(failed_urls),
                "failed_urls": [{"url": url, "manufacturer": mfr, "reason": reason} for url, mfr, reason in failed_urls]
            }
            with open(failed_file, 'w') as f:
                json.dump(failed_data, f, indent=2)
            print(f"\n💾 Failed URLs saved to {failed_file} for retry")
    else:
        print("\n❌ No arrows extracted")

def main():
    asyncio.run(run_comprehensive_extraction())

if __name__ == "__main__":
    main()