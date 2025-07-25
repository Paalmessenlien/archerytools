#!/usr/bin/env python3
"""
EasyOCR-based Carbon Express Extractor

This module provides free, local OCR extraction for Carbon Express
specification images using EasyOCR.
"""

import requests
import re
import json
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from models import ArrowSpecification, SpineSpecification

class EasyOCRCarbonExpressExtractor:
    """Free OCR extractor for Carbon Express using EasyOCR"""
    
    def __init__(self):
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initialize EasyOCR reader"""
        try:
            import easyocr
            print("🤖 Initializing EasyOCR...")
            self.reader = easyocr.Reader(['en'], verbose=False)
            print("✅ EasyOCR ready")
        except ImportError:
            print("❌ EasyOCR not available (pip install easyocr)")
            self.reader = None
        except Exception as e:
            print(f"❌ EasyOCR initialization error: {e}")
            self.reader = None
    
    def download_image(self, image_url: str) -> Optional[bytes]:
        """Download image and return bytes"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"❌ Failed to download image {image_url}: {e}")
            return None
    
    def extract_text_from_image(self, image_data: bytes) -> List[Tuple[str, float]]:
        """Extract text from image using EasyOCR"""
        if not self.reader:
            return []
        
        try:
            # Save image temporarily
            temp_path = "temp_carbon_express.png"
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            # Extract text
            results = self.reader.readtext(temp_path)
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            
            # Return text with confidence
            text_results = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Only confident detections
                    text_results.append((text.strip(), confidence))
            
            return text_results
            
        except Exception as e:
            print(f"❌ OCR extraction error: {e}")
            return []
    
    def parse_image_specifications(self, text_results: List[Tuple[str, float]], model_hint: str = "", manufacturer: str = "Unknown") -> Dict:
        """Parse OCR text results to extract arrow specifications from images"""
        
        # Combine all text
        all_text = [text for text, conf in text_results]
        combined_text = " ".join(all_text)
        
        print(f"📝 Parsing {len(text_results)} OCR detections for {manufacturer}")
        print(f"Combined text: {combined_text[:200]}...")
        
        # Extract model name based on manufacturer
        if "Victory" in manufacturer:
            model_name = "Victory Archery"
            if model_hint:
                model_name = f"Victory Archery {model_hint}"
            
            # Look for Victory model names in OCR text
            for text, conf in text_results:
                text_lower = text.lower()
                if any(model in text_lower for model in ['vap', 'rip', '3dhv', 'tac', 'vxt', 'tko']):
                    model_name = f"Victory Archery {text}"
                    break
                    
        else:  # Carbon Express or other
            model_name = "Carbon Express"
            if model_hint:
                model_name = f"Carbon Express {model_hint}"
            
            # Look for Carbon Express model names in OCR text
            for text, conf in text_results:
                text_lower = text.lower()
                if any(model in text_lower for model in ['maxima', 'triad', 'sable', 'photon', 'destroyer']):
                    model_name = f"Carbon Express {text}"
                    break
        
        # Extract spine values (3-4 digit numbers)
        spine_pattern = r'\b(250|300|340|350|400|450|500|550|600|650|700|750|800|850|900|950|1000|1100|1200|1300|1400|1500)\b'
        spine_values = []
        
        for text, conf in text_results:
            if re.match(spine_pattern, text):
                spine_values.append(int(text))
        
        # Extract GPI values (decimal numbers with reasonable range)
        gpi_values = []
        for text, conf in text_results:
            # Look for decimal numbers in reasonable GPI range (3.0 - 15.0)
            if re.match(r'^\d+\.\d+$', text):
                try:
                    value = float(text)
                    if 3.0 <= value <= 15.0:  # Reasonable GPI range
                        gpi_values.append(value)
                except ValueError:
                    continue
        
        # Extract diameter values
        diameter_values = []
        for text, conf in text_results:
            # Victory format: decimal like 0.166, 0.256, 0.249
            decimal_match = re.search(r'0\.(\d{3})', text)
            if decimal_match:
                try:
                    diameter_inches = float(f"0.{decimal_match.group(1)}")
                    if 0.1 <= diameter_inches <= 0.5:  # Reasonable diameter range
                        diameter_values.append(diameter_inches)
                        continue
                except ValueError:
                    pass
            
            # Carbon Express format: look for diameter patterns like .244" or 244"
            thousandths_match = re.search(r'\.?(\d+)["″]', text)
            if thousandths_match:
                try:
                    # Convert from thousandths to decimal inches
                    thousandths = int(thousandths_match.group(1))
                    if 200 <= thousandths <= 400:  # Reasonable diameter range
                        diameter_inches = thousandths / 1000.0
                        diameter_values.append(diameter_inches)
                except ValueError:
                    continue
        
        # Extract lengths
        length_values = []
        for text, conf in text_results:
            length_match = re.search(r'(\d+)["″]', text)
            if length_match:
                try:
                    length = int(length_match.group(1))
                    if 28 <= length <= 36:  # Reasonable arrow length range
                        length_values.append(float(length))
                except ValueError:
                    continue
        
        # Extract straightness tolerance
        straightness = None
        for text, conf in text_results:
            if 'straightness' in text.lower() or re.search(r'0\.\d+', text):
                straightness_match = re.search(r'(0\.\d+)', text)
                if straightness_match:
                    try:
                        straightness = f"±{straightness_match.group(1)}\""
                    except:
                        pass
        
        print(f"🎯 Extracted:")
        print(f"   Spines: {spine_values}")
        print(f"   GPI values: {gpi_values}")
        print(f"   Diameters: {diameter_values}")
        print(f"   Lengths: {length_values}")
        print(f"   Straightness: {straightness}")
        
        # Create spine specifications by pairing data
        specifications = []
        
        # Method 1: If we have equal numbers, pair them in order
        if len(spine_values) == len(gpi_values):
            print("📋 Method 1: Pairing spines and GPI in order")
            for i, spine in enumerate(spine_values):
                spec = {
                    "spine": spine,
                    "gpi_weight": gpi_values[i],
                    "outer_diameter": diameter_values[i] if i < len(diameter_values) else None,
                    "inner_diameter": None,
                    "length_options": length_values if length_values else None
                }
                specifications.append(spec)
        
        # Method 2: If unequal, try to match closest values
        elif spine_values and gpi_values:
            print("📋 Method 2: Matching available data")
            # Use most common diameter/length for all
            common_diameter = diameter_values[0] if diameter_values else None
            common_length = length_values[0] if length_values else None
            
            # Create specs for each spine, cycling through GPI values
            for i, spine in enumerate(spine_values):
                gpi_idx = i % len(gpi_values)
                spec = {
                    "spine": spine,
                    "gpi_weight": gpi_values[gpi_idx],
                    "outer_diameter": common_diameter,
                    "inner_diameter": None,
                    "length_options": [common_length] if common_length else None
                }
                specifications.append(spec)
        
        return {
            "model_name": model_name,
            "spine_specifications": specifications,
            "material": "Carbon",
            "arrow_type": "hunting",
            "description": f"Extracted from Carbon Express specification image using EasyOCR",
            "straightness_tolerance": straightness,
            "technology": "RED ZONE" if "red" in combined_text.lower() else None
        }
    
    def find_specification_images(self, html_content: str, base_url: str) -> List[str]:
        """Find specification images for various manufacturers (Carbon Express, Victory Archery, etc.)"""
        
        potential_images = []
        
        # Detect manufacturer based on URL
        if "feradyne.com" in base_url.lower() or "carbon express" in base_url.lower():
            print("🔍 Looking for Carbon Express specification images in elementor containers...")
            
            # Look specifically for elementor-widget-container with images
            elementor_pattern = r'<div class="elementor-widget-container"[^>]*>\s*<img[^>]*src="([^"]*)"[^>]*>\s*</div>'
            
            matches = re.finditer(elementor_pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            for i, match in enumerate(matches, 1):
                img_url = self._normalize_url(match.group(1), base_url)
                
                # Check if this looks like a Carbon Express specification image
                img_url_lower = img_url.lower()
                is_spec_image = any(indicator in img_url_lower for indicator in [
                    'maxima', 'triad', 'sable', 'photon', 'destroyer', 'express',
                    'spec', 'chart', 'data', 'tech'
                ])
                
                # Also include if it's a PNG (most spec charts are PNG)
                is_png = img_url_lower.endswith('.png')
                
                if is_spec_image or is_png:
                    potential_images.append(img_url)
                    print(f"   📊 Found Carbon Express elementor image {i}: {img_url.split('/')[-1]}")
            
            print(f"📋 Carbon Express elementor search found {len(potential_images)} images")
        
        elif "victoryarchery.com" in base_url.lower():
            print("🔍 Looking for Victory Archery specification images...")
            
            # Victory uses WordPress CDN with date-based structure for spec images
            victory_patterns = [
                # WordPress CDN images (primary pattern based on your example)
                r'<img[^>]*src="(https://i[0-9]\.wp\.com/www\.victoryarchery\.com/wp-content/uploads/[^"]*\.(?:png|jpg|jpeg)[^"]*)"[^>]*>',
                # Direct wp-content uploads  
                r'<img[^>]*src="([^"]*victoryarchery\.com/wp-content/uploads/[^"]*\.(?:png|jpg|jpeg))"[^>]*>',
                # Current year spine charts (2025, 2024, etc.)
                r'<img[^>]*src="([^"]*wp-content/uploads/202[4-9]/[^"]*\.(?:png|jpg|jpeg))"[^>]*>',
                # Model-specific images that might be specs (like 3DHV.jpg, VAP-SS.jpg, etc.)
                r'<img[^>]*src="([^"]*wp-content/uploads/[^"]*(?:[A-Z]{2,}[^"/]*|spec|chart|table|tech)[^"]*\.(?:png|jpg|jpeg))"[^>]*>',
                # General fallback for wp-content images
                r'<img[^>]*src="([^"]*wp-content/uploads/[^"]*\.(?:png|jpg|jpeg))"[^>]*>'
            ]
            
            for pattern in victory_patterns:
                matches = re.finditer(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    img_url = self._normalize_url(match.group(1), base_url)
                    img_url_lower = img_url.lower()
                    
                    # Filter for likely specification images, exclude common non-spec images
                    if not any(skip in img_url_lower for skip in ['logo', 'icon', 'banner', 'header', 'nav', 'menu', 'footer']):
                        # Victory-specific filtering for specification images
                        filename = img_url.split('/')[-1].split('?')[0].lower()  # Get clean filename
                        
                        # Priority 1: Obvious spec-related keywords
                        high_priority = any(keyword in img_url_lower for keyword in ['spine', 'chart', 'spec', 'tech', 'fitting'])
                        
                        # Priority 2: Model names or current year (likely spec images)
                        medium_priority = any(indicator in img_url_lower for indicator in ['2025', '2024', '3dhv', 'vap', 'rip', 'tac', 'vxt', 'tko'])
                        
                        # Priority 3: WordPress CDN with recent date structure
                        low_priority = 'i0.wp.com' in img_url_lower or 'wp-content/uploads/202' in img_url_lower
                        
                        if high_priority or medium_priority or low_priority:
                            potential_images.append(img_url)
                            priority_label = "HIGH" if high_priority else "MED" if medium_priority else "LOW"
                            print(f"   📊 Found Victory spec image ({priority_label}): {filename}")
            
            print(f"📋 Victory Archery search found {len(potential_images)} images")
            if potential_images:
                for j, img in enumerate(potential_images, 1):
                    filename = img.split('/')[-1].split('?')[0]
                    print(f"     🖼️  {j}. {filename}")
        
        else:
            print(f"🔍 Looking for general specification images for {base_url}...")
            # Generic fallback for other manufacturers
            general_patterns = [
                r'<img[^>]*src="([^"]*(?:spec|chart|table|tech)[^"]*\.(?:png|jpg|jpeg))"[^>]*>',
            ]
            
            for pattern in general_patterns:
                matches = re.finditer(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    img_url = self._normalize_url(match.group(1), base_url)
                    potential_images.append(img_url)
            
            print(f"📋 General search found {len(potential_images)} images")
        
        # Generic fallback if no specific images found
        if len(potential_images) == 0:
            print("⚠️  No specific images found, trying generic fallback patterns...")
            fallback_patterns = [
                r'<img[^>]*src="([^"]*(?:spec|chart|table|tech)[^"]*\.(?:png|jpg|jpeg))"[^>]*>',
                r'<img[^>]*src="([^"]*\.png)"[^>]*>'  # Last resort - any PNG
            ]
            
            for pattern in fallback_patterns:
                matches = re.finditer(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    img_url = self._normalize_url(match.group(1), base_url)
                    potential_images.append(img_url)
            
            print(f"📋 Fallback search found {len(potential_images)} additional images")
        
        # Remove duplicates and return
        unique_images = list(set(potential_images))
        print(f"📊 Total unique images found: {len(unique_images)}")
        return unique_images
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Convert relative URLs to absolute URLs"""
        url = url.strip()
        
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return base_url.rstrip('/') + url
        elif not url.startswith('http'):
            return base_url.rstrip('/') + '/' + url
        else:
            return url
    
    def extract_vision_based_data(self, html_content: str, markdown_content: str, url: str) -> List[ArrowSpecification]:
        """Extract arrow data from images using EasyOCR (Carbon Express, Victory Archery, etc.)"""
        
        if not self.reader:
            print("❌ EasyOCR not available")
            return []
        
        # Detect manufacturer from URL
        if "victoryarchery.com" in url.lower():
            print("🖼️  Attempting EasyOCR extraction for Victory Archery...")
            manufacturer = "Victory Archery"
        elif "feradyne.com" in url.lower() or "carbon express" in url.lower():
            print("🖼️  Attempting EasyOCR extraction for Carbon Express...")
            manufacturer = "Carbon Express"
        else:
            print("🖼️  Attempting EasyOCR extraction...")
            manufacturer = "Unknown"
        
        # Extract model hint from URL
        model_hint = ""
        url_lower = url.lower()
        if "maxima" in url_lower:
            model_hint = "Maxima"
        elif "triad" in url_lower:
            model_hint = "Triad"
        elif "vap" in url_lower:
            model_hint = "VAP"
        elif "rip" in url_lower:
            model_hint = "RIP"
        elif "3dhv" in url_lower:
            model_hint = "3DHV"
        elif "sable" in url_lower:
            model_hint = "Sable"
        elif "photon" in url_lower:
            model_hint = "Photon"
        
        # Find specification images
        base_url = f"https://{url.split('/')[2]}"
        spec_images = self.find_specification_images(html_content, base_url)
        
        if not spec_images:
            print("❌ No specification images found")
            return []
        
        print(f"🔍 Found {len(spec_images)} potential specification images")
        
        # Debug: Show all images being processed
        for i, img_url in enumerate(spec_images, 1):
            filename = img_url.split('/')[-1].split('?')[0]
            print(f"   📋 {i}. {filename} → {img_url}")
        print()
        
        # Try each image (process all images, don't return early)
        all_arrows = []
        successful_extractions = 0
        
        for i, image_url in enumerate(spec_images, 1):
            filename = image_url.split('/')[-1].split('?')[0]
            print(f"📊 Processing image {i}/{len(spec_images)}: {filename}")
            
            try:
                # Download image
                image_data = self.download_image(image_url)
                if not image_data:
                    print(f"❌ Failed to download image {i}: {filename}")
                    continue
                
                print(f"✓ Downloaded {len(image_data)} bytes")
                
                # Extract text using OCR
                print(f"🤖 Starting OCR on {filename}...")
                text_results = self.extract_text_from_image(image_data)
                if not text_results:
                    print(f"⚠️  No OCR text extracted from image {i}")
                    # Debug: Check if reader is available
                    if not self.reader:
                        print(f"❌ EasyOCR reader not initialized!")
                    continue
                
                print(f"✓ OCR extracted {len(text_results)} text elements")
                # Debug: Show what text was found
                for j, (text, conf) in enumerate(text_results[:5], 1):  # Show first 5
                    print(f"   {j}. '{text}' (confidence: {conf:.2f})")
                if len(text_results) > 5:
                    print(f"   ... and {len(text_results) - 5} more elements")
                
                # Parse specifications
                parsed_data = self.parse_image_specifications(text_results, model_hint, manufacturer)
                
                if not parsed_data.get('spine_specifications'):
                    print(f"⚠️  No spine specifications parsed from image {i}")
                    continue
                
                print(f"✓ Parsed {len(parsed_data['spine_specifications'])} spine specifications")
                # Debug: Show what was parsed
                for j, spec in enumerate(parsed_data['spine_specifications'], 1):
                    print(f"   Spec {j}: Spine {spec.get('spine')}, GPI {spec.get('gpi_weight')}, OD {spec.get('outer_diameter')}")
                
                # Convert to ArrowSpecification objects
                spine_specs = []
                for spec_data in parsed_data['spine_specifications']:
                    if all(key in spec_data and spec_data[key] is not None 
                          for key in ['spine', 'gpi_weight']):
                        
                        # Ensure outer_diameter is a valid float or None
                        outer_diameter = spec_data.get('outer_diameter')
                        if outer_diameter is not None:
                            try:
                                outer_diameter = float(outer_diameter)
                            except (ValueError, TypeError):
                                outer_diameter = None
                        
                        spine_spec = SpineSpecification(
                            spine=int(spec_data['spine']),
                            outer_diameter=outer_diameter,
                            gpi_weight=float(spec_data['gpi_weight']),
                            inner_diameter=spec_data.get('inner_diameter'),
                            length_options=spec_data.get('length_options', [])
                        )
                        spine_specs.append(spine_spec)
                
                if spine_specs:
                    arrow = ArrowSpecification(
                        model_name=parsed_data['model_name'],
                        manufacturer=manufacturer,  # Use detected manufacturer
                        spine_specifications=spine_specs,
                        material=parsed_data.get('material'),
                        arrow_type=parsed_data.get('arrow_type', 'hunting'),
                        description=parsed_data.get('description'),
                        source_url=url,
                        straightness_tolerance=parsed_data.get('straightness_tolerance'),
                        primary_image_url=image_url
                    )
                    
                    all_arrows.append(arrow)
                    successful_extractions += 1
                    print(f"✅ Successfully extracted {len(spine_specs)} specifications from image {i}")
                else:
                    print(f"⚠️  No valid spine specifications created from image {i}")
                    
            except Exception as e:
                print(f"❌ Error processing image {i} ({filename}): {str(e)[:100]}")
                continue
        
        # Return all successful extractions
        if all_arrows:
            print(f"🎯 Extraction complete: {successful_extractions}/{len(spec_images)} images successful")
            return all_arrows
        
        print("❌ No usable specifications found in any images")
        return []

# Example usage
if __name__ == "__main__":
    extractor = EasyOCRCarbonExpressExtractor()
    
    if extractor.reader:
        print("✅ EasyOCR Carbon Express Extractor ready")
        print("📋 Usage: extractor.extract_carbon_express_data(html_content, markdown_content, url)")
    else:
        print("❌ EasyOCR not available - install with: pip install easyocr")