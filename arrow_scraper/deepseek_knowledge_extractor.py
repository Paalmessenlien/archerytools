#!/usr/bin/env python3
"""
DeepSeek Knowledge-Based Arrow Data Extractor
Fallback system that queries DeepSeek directly for arrow specifications when scraping fails
"""

import json
import re
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from urllib.parse import urlparse

# Handle optional pydantic dependency
try:
    from models import ArrowSpecification, SpineSpecification
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    print("⚠️  Pydantic models not available - using dict fallback")

class DeepSeekKnowledgeExtractor:
    """Extract arrow specifications using DeepSeek's training knowledge as fallback"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def extract_from_knowledge(self, manufacturer: str, model_name: str, url: str) -> List[Any]:
        """
        Extract arrow specifications using DeepSeek's knowledge base
        This is used when web scraping fails to find technical data
        """
        
        print(f"🧠 Querying DeepSeek knowledge base for {manufacturer} {model_name}")
        
        # Extract model name from URL if not provided or unclear
        if not model_name or model_name.strip() == "":
            model_name = self._extract_model_from_url(url)
        
        # Create knowledge-based query prompt
        prompt = self._create_knowledge_prompt(manufacturer, model_name, url)
        
        try:
            # Query DeepSeek API
            response = self._query_deepseek(prompt)
            
            if response:
                # Parse the structured response
                arrows = self._parse_knowledge_response(response, manufacturer, model_name, url)
                
                if arrows:
                    print(f"✅ DeepSeek knowledge found {len(arrows)} arrow(s) with {sum(len(a.spine_specifications) for a in arrows)} spine specifications")
                    return arrows
                else:
                    print("⚠️  DeepSeek knowledge available but no valid specifications parsed")
            else:
                print("❌ DeepSeek knowledge query failed")
                
        except Exception as e:
            print(f"❌ DeepSeek knowledge extraction error: {str(e)[:100]}")
        
        return []
    
    def _extract_model_from_url(self, url: str) -> str:
        """Extract likely model name from URL path"""
        try:
            path = urlparse(url).path
            # Remove common path elements and extract model-like names
            path_parts = [p for p in path.split('/') if p and p not in ['arrows', 'product', 'arrow', 'hunting', 'target']]
            
            # Look for the most model-like part (usually has hyphens, numbers, or specific patterns)
            for part in reversed(path_parts):  # Start from end as model names are often at the end
                # Clean up common URL patterns
                clean_part = part.replace('-', ' ').replace('_', ' ')
                if len(clean_part) > 3 and any(c.isalpha() for c in clean_part):
                    return clean_part.title()
            
            # Fallback to last meaningful path part
            if path_parts:
                return path_parts[-1].replace('-', ' ').replace('_', ' ').title()
                
        except Exception:
            pass
        
        return "Unknown Model"
    
    def _create_knowledge_prompt(self, manufacturer: str, model_name: str, url: str) -> str:
        """Create a prompt to query DeepSeek's knowledge about arrow specifications"""
        
        return f"""You are an archery equipment expert. I need technical specifications for an arrow model.

MANUFACTURER: {manufacturer}
MODEL: {model_name}
SOURCE URL: {url}

Please provide the complete technical specifications for this arrow model if you have knowledge of it. 

REQUIRED OUTPUT FORMAT (JSON only, no explanation):
{{
    "model_name": "exact model name",
    "manufacturer": "{manufacturer}",
    "specifications_found": true/false,
    "spine_specifications": [
        {{
            "spine": 300,
            "outer_diameter": 0.246,
            "gpi_weight": 8.5,
            "inner_diameter": 0.204,
            "length_options": [28, 29, 30, 31, 32]
        }},
        {{
            "spine": 350,
            "outer_diameter": 0.246, 
            "gpi_weight": 7.8,
            "inner_diameter": 0.204,
            "length_options": [28, 29, 30, 31, 32]
        }}
    ],
    "material": "Carbon",
    "carbon_content": "100%",
    "arrow_type": "hunting" or "target",
    "straightness_tolerance": "±0.003\"",
    "weight_tolerance": "±1.0 grain",
    "description": "Brief description of the arrow technology and features"
}}

IMPORTANT:
- Only provide data if you have reliable knowledge of this specific model
- Use actual measured values (GPI in grains per inch, diameter in inches)
- Include all available spine options for this model
- Set specifications_found to false if you're not confident about this specific model
- Spine values should be standard archery spine ratings (150, 200, 250, 300, 340, 350, 400, 500, 600, etc.)
- GPI should be realistic for the arrow type (target arrows: 4-12 GPI, hunting arrows: 8-15+ GPI)
- Diameter should be in decimal inches (e.g., 0.246 for 6.2mm)
- Length options should be realistic arrow lengths in inches (typically 26-34)

JSON OUTPUT:"""

    def _query_deepseek(self, prompt: str) -> Optional[str]:
        """Send query to DeepSeek API"""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # Low temperature for factual accuracy
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                print(f"⚠️  DeepSeek API error {response.status_code}: {response.text[:100]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  DeepSeek API request failed: {str(e)[:100]}")
            return None
    
    def _parse_knowledge_response(self, response_text: str, manufacturer: str, model_name: str, url: str) -> List[Any]:
        """Parse DeepSeek's JSON response into ArrowSpecification objects"""
        
        try:
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                print("⚠️  No JSON found in DeepSeek response")
                return []
            
            json_str = json_match.group()
            data = json.loads(json_str)
            
            # Check if specifications were found
            if not data.get('specifications_found', False):
                print("ℹ️  DeepSeek indicated no reliable knowledge for this model")
                return []
            
            # Validate required fields
            spine_specs = data.get('spine_specifications', [])
            if not spine_specs:
                print("⚠️  No spine specifications in DeepSeek response")
                return []
            
            if not MODELS_AVAILABLE:
                # Fallback: return dict format when pydantic models unavailable
                return [{
                    'manufacturer': manufacturer,
                    'model_name': data.get('model_name', model_name),
                    'spine_specifications': spine_specs,
                    'material': data.get('material', 'Carbon'),
                    'carbon_content': data.get('carbon_content'),
                    'arrow_type': data.get('arrow_type', 'hunting'),
                    'description': f"Technical data from DeepSeek knowledge base. {data.get('description', '')}".strip(),
                    'source_url': url,
                    'scraper_version': "deepseek-knowledge-1.0"
                }]
            
            # Create spine specification objects
            spine_objects = []
            for spec in spine_specs:
                try:
                    spine_obj = SpineSpecification(
                        spine=int(spec.get('spine', 0)),
                        outer_diameter=float(spec.get('outer_diameter', 0.0)) if spec.get('outer_diameter') else None,
                        gpi_weight=float(spec.get('gpi_weight', 0.0)) if spec.get('gpi_weight') else None,
                        inner_diameter=float(spec.get('inner_diameter', 0.0)) if spec.get('inner_diameter') else None,
                        length_options=spec.get('length_options', [])
                    )
                    
                    # Basic validation
                    if spine_obj.spine > 0:
                        spine_objects.append(spine_obj)
                    
                except (ValueError, TypeError) as e:
                    print(f"⚠️  Invalid spine specification: {e}")
                    continue
            
            if not spine_objects:
                print("⚠️  No valid spine specifications parsed from DeepSeek response")
                return []
            
            # Create arrow specification
            from datetime import datetime
            arrow = ArrowSpecification(
                manufacturer=manufacturer,
                model_name=data.get('model_name', model_name),
                spine_specifications=spine_objects,
                material=data.get('material', 'Carbon'),
                carbon_content=data.get('carbon_content'),
                arrow_type=data.get('arrow_type', 'hunting'),
                description=f"Technical data from DeepSeek knowledge base. {data.get('description', '')}".strip(),
                straightness_tolerance=data.get('straightness_tolerance'),
                weight_tolerance=data.get('weight_tolerance'),
                source_url=url,
                scraped_at=datetime.now(),
                scraper_version="deepseek-knowledge-1.0"
            )
            
            return [arrow]
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error: {e}")
            print(f"Raw response: {response_text[:200]}")
            return []
        except Exception as e:
            print(f"⚠️  Response parsing error: {str(e)[:100]}")
            return []
    
    def can_help_with_manufacturer(self, manufacturer: str) -> bool:
        """Check if this extractor can potentially help with a manufacturer"""
        
        # DeepSeek likely has knowledge of major manufacturers
        major_manufacturers = [
            'easton', 'carbon express', 'gold tip', 'victory', 'black eagle',
            'trophy taker', 'axis', 'maxima', 'bloodline', 'superdrive'
        ]
        
        manufacturer_lower = manufacturer.lower()
        return any(major in manufacturer_lower for major in major_manufacturers)
    
    def extract_from_failed_url(self, url: str, manufacturer: str = None) -> List[Any]:
        """
        Extract arrow data for a URL that failed conventional scraping
        Attempts to infer manufacturer and model from URL if not provided
        """
        
        if not manufacturer:
            manufacturer = self._infer_manufacturer_from_url(url)
        
        model_name = self._extract_model_from_url(url)
        
        return self.extract_from_knowledge(manufacturer, model_name, url)
    
    def _infer_manufacturer_from_url(self, url: str) -> str:
        """Infer manufacturer from URL domain"""
        
        try:
            domain = urlparse(url).netloc.lower()
            
            # Common manufacturer domain patterns
            domain_mappings = {
                'eastonarchery.com': 'Easton Archery',
                'goldtip.com': 'Gold Tip',
                'victoryarchery.com': 'Victory Archery',
                'feradyne.com': 'Carbon Express',
                'carbon-express.com': 'Carbon Express',
                'blackeagle.com': 'Black Eagle',
                'skylonarchery.com': 'Skylon Archery',
                'nijora.com': 'Nijora Archery',
                'dkbow.de': 'DK Bow',
                'bigarchery.com': 'BigArchery'
            }
            
            for domain_part, manufacturer in domain_mappings.items():
                if domain_part in domain:
                    return manufacturer
            
            # Generic extraction from domain
            domain_clean = domain.replace('www.', '').split('.')[0]
            return domain_clean.replace('-', ' ').replace('_', ' ').title()
            
        except Exception:
            return "Unknown Manufacturer"

# Example usage and testing
if __name__ == "__main__":
    import os
    
    # Test with a known arrow model
    api_key = os.getenv("DEEPSEEK_API_KEY", "test_key")
    extractor = DeepSeekKnowledgeExtractor(api_key)
    
    # Test knowledge extraction
    test_cases = [
        ("Easton Archery", "X10", "https://eastonarchery.com/arrows_/x10/"),
        ("Carbon Express", "Maxima Red", "https://www.feradyne.com/product/maxima-red/"),
        ("Victory Archery", "VAP-SS", "https://victoryarchery.com/arrows-hunting/vap-ss/"),
        ("Gold Tip", "Kinetic Pierce", "https://goldtip.com/arrow/kinetic-pierce/")
    ]
    
    print("🧪 Testing DeepSeek Knowledge Extractor")
    print("=" * 50)
    
    for manufacturer, model, url in test_cases:
        print(f"\n🎯 Testing: {manufacturer} {model}")
        
        if extractor.can_help_with_manufacturer(manufacturer):
            print("✅ Manufacturer supported")
            # In real usage, would call extract_from_knowledge here
            print("📋 Would query DeepSeek knowledge base")
        else:
            print("⚠️  Manufacturer not in major list")