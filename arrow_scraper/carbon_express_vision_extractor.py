#!/usr/bin/env python3
"""
Carbon Express Vision-Based Extractor using OpenAI GPT-4 Vision

This module provides OCR-based extraction for manufacturers like Carbon Express
that store specifications in images rather than text.
"""

import requests
import base64
import json
import re
from typing import List, Optional
from pathlib import Path
from models import ArrowSpecification, SpineSpecification

class VisionBasedExtractor:
    """Extractor for image-based arrow specifications using OpenAI Vision"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
    
    def encode_image_to_base64(self, image_url: str) -> Optional[str]:
        """Download and encode image to base64"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            image_data = response.content
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
            return base64_encoded
        except Exception as e:
            print(f"❌ Failed to download/encode image {image_url}: {e}")
            return None
    
    def analyze_specification_image(self, image_url: str, model_name_hint: str = "") -> Optional[dict]:
        """Analyze specification image using OpenAI Vision"""
        
        base64_image = self.encode_image_to_base64(image_url)
        if not base64_image:
            return None
        
        prompt = f"""
        Analyze this Carbon Express arrow specification image and extract all technical data in JSON format.

        Model hint: {model_name_hint}

        Look for:
        1. SPINE values (e.g., 250, 300, 350, 400, 500, 600, 700, 800, 900, 1000)
        2. GPI weights (grains per inch) - decimal numbers like 6.2, 7.8, 9.1
        3. DIAMETER measurements (outer diameter) - in inches like .244", .294"
        4. LENGTH options if shown (in inches)
        5. Arrow model name from the image
        6. Material information (e.g., "Carbon", "3K Carbon")
        7. Straightness tolerance if shown
        8. Any special technology (RED ZONE, Tri-Spine, etc.)

        Common Carbon Express formats:
        - Tables with columns: Spine, GPI, O.D., Length
        - Sometimes "Weight" instead of "GPI" 
        - Diameters like .244" or 0.244"
        - Multiple spine options in rows
        - RED ZONE or tri-spine technology mentioned

        CRITICAL: Extract EVERY spine value you see with corresponding GPI and diameter.
        If you see a table with multiple rows, extract ALL rows.

        Return ONLY valid JSON:
        {{
            "model_name": "Exact model name from image",
            "spine_specifications": [
                {{
                    "spine": 350,
                    "gpi_weight": 9.07,
                    "outer_diameter": 0.244,
                    "inner_diameter": null,
                    "length_options": [30.0, 31.0]
                }}
            ],
            "material": "Material from image",
            "arrow_type": "hunting or target",
            "description": "Any description text from image",
            "technology": "Special technology if mentioned",
            "straightness_tolerance": "e.g., ±0.003" if shown
        }}

        If no specifications found: {{"error": "No specifications in image"}}
        """
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json=data,
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"❌ OpenAI API Error: {response.text}")
                return None
            
            result = response.json()
            
            if 'choices' not in result or len(result['choices']) == 0:
                print("❌ No choices in OpenAI response")
                return None
            
            content = result['choices'][0]['message']['content'].strip()
            
            # Clean JSON formatting
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error in vision response: {e}")
            return None
        except Exception as e:
            print(f"💥 OpenAI Vision API error: {e}")
            return None
    
    def find_specification_images(self, html_content: str, base_url: str) -> List[str]:
        """Find potential specification images in HTML content"""
        
        # Look for Carbon Express specific image patterns
        image_patterns = [
            r'<img[^>]*src="([^"]*(?:maxima|triad|sable|photon|destroyer|adrenaline|thunder)[^"]*\.(?:png|jpg|jpeg))"[^>]*>',
            r'<img[^>]*src="([^"]*spec[^"]*\.(?:png|jpg|jpeg))"[^>]*>',
            r'<img[^>]*src="([^"]*chart[^"]*\.(?:png|jpg|jpeg))"[^>]*>',
        ]
        
        potential_images = []
        
        for pattern in image_patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            for match in matches:
                img_url = match.group(1)
                
                # Convert relative URLs to absolute
                if img_url.startswith('/'):
                    img_url = base_url.rstrip('/') + img_url
                elif not img_url.startswith('http'):
                    img_url = base_url.rstrip('/') + '/' + img_url
                
                potential_images.append(img_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in potential_images:
            if img not in seen:
                unique_images.append(img)
                seen.add(img)
        
        return unique_images
    
    def extract_carbon_express_data(self, html_content: str, markdown_content: str, url: str) -> List[ArrowSpecification]:
        """Extract Carbon Express arrow data using vision-based OCR"""
        
        print("🖼️  Attempting vision-based extraction for Carbon Express...")
        
        # Extract model name hint from URL or content
        model_hint = ""
        if "maxima" in url.lower():
            model_hint = "Maxima"
        elif "triad" in url.lower():
            model_hint = "Triad"
        elif "sable" in url.lower():
            model_hint = "Sable"
        elif "photon" in url.lower():
            model_hint = "Photon"
        
        # Find specification images
        base_url = f"https://{url.split('/')[2]}"
        spec_images = self.find_specification_images(html_content, base_url)
        
        if not spec_images:
            print("❌ No specification images found")
            return []
        
        print(f"🔍 Found {len(spec_images)} potential specification images")
        
        # Try each image until we get specifications
        for i, image_url in enumerate(spec_images, 1):
            print(f"📊 Analyzing image {i}/{len(spec_images)}: {image_url}")
            
            vision_result = self.analyze_specification_image(image_url, model_hint)
            
            if not vision_result:
                continue
            
            if 'error' in vision_result:
                print(f"⚠️  Image {i}: {vision_result['error']}")
                continue
            
            if 'spine_specifications' not in vision_result or not vision_result['spine_specifications']:
                print(f"⚠️  Image {i}: No spine specifications found")
                continue
            
            # Convert vision result to ArrowSpecification
            try:
                spine_specs = []
                for spec_data in vision_result['spine_specifications']:
                    if all(key in spec_data and spec_data[key] is not None 
                          for key in ['spine', 'outer_diameter', 'gpi_weight']):
                        
                        spine_spec = SpineSpecification(
                            spine=spec_data['spine'],
                            outer_diameter=spec_data['outer_diameter'],
                            gpi_weight=spec_data['gpi_weight'],
                            inner_diameter=spec_data.get('inner_diameter'),
                            length_options=spec_data.get('length_options')
                        )
                        spine_specs.append(spine_spec)
                
                if spine_specs:
                    arrow = ArrowSpecification(
                        model_name=vision_result.get('model_name', 'Carbon Express Model'),
                        manufacturer="Carbon Express",
                        spine_specifications=spine_specs,
                        material=vision_result.get('material'),
                        arrow_type=vision_result.get('arrow_type', 'hunting'),
                        description=vision_result.get('description'),
                        source_url=url,
                        straightness_tolerance=vision_result.get('straightness_tolerance'),
                        primary_image_url=image_url  # Store the spec image URL
                    )
                    
                    print(f"✅ Successfully extracted {len(spine_specs)} spine specifications from image {i}")
                    return [arrow]
                    
            except Exception as e:
                print(f"❌ Error converting vision result to ArrowSpecification: {e}")
                continue
        
        print("❌ No usable specifications found in any images")
        return []

# Example usage for integration
def integrate_vision_extractor_example():
    """Example of how to integrate vision extractor into main extraction logic"""
    
    # This would go in the main DirectLLMExtractor class
    def extract_arrow_data_with_vision(self, content: str, url: str) -> List[ArrowSpecification]:
        """Enhanced extraction with vision support for image-based manufacturers"""
        
        # Try normal text-based extraction first
        arrows = self.extract_arrow_data_text_only(content, url)
        
        if arrows:
            return arrows  # Text extraction worked
        
        # Check if this is a manufacturer known to use images
        if "feradyne.com" in url.lower() or "carbon-express" in url.lower():
            print("🖼️  Detected Carbon Express - trying vision extraction...")
            
            # Initialize vision extractor if available
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                vision_extractor = VisionBasedExtractor(openai_key)
                # Note: would need to pass HTML content here
                return vision_extractor.extract_carbon_express_data("", content, url)
            else:
                print("⚠️  OpenAI API key not available for vision extraction")
        
        return []  # No extraction possible

if __name__ == "__main__":
    print("Carbon Express Vision Extractor Module")
    print("This module provides OCR capability for image-based specifications")
    print("Requires OpenAI API key with GPT-4 Vision access")