#!/usr/bin/env python3
"""
Production DeepSeek Arrow Extractor
Intelligent extraction of arrow specifications using DeepSeek API
"""

import json
import re
import os
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from models import ArrowSpecification, ArrowType

# Load environment variables
load_dotenv()

class DeepSeekArrowExtractor:
    """Production-ready arrow specification extractor using DeepSeek API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the extractor with DeepSeek API key"""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
    
    def clean_json_response(self, response_text: str) -> str:
        """Clean JSON response by removing markdown formatting"""
        # Remove markdown code blocks
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        return cleaned
    
    def normalize_arrow_type(self, arrow_type: str) -> Optional[str]:
        """Normalize arrow type to match our enum values"""
        if not arrow_type:
            return None
        
        arrow_type_lower = arrow_type.lower()
        
        # Mapping common variations to our enum values
        type_mapping = {
            'target': 'target',
            'hunting': 'hunting', 
            'indoor': 'indoor',
            'outdoor': 'outdoor',
            '3d': '3d',
            'recreational': 'recreational',
            'competition': 'target',
            'field': 'outdoor',
            'bowhunting': 'hunting',
            'practice': 'recreational'
        }
        
        for key, value in type_mapping.items():
            if key in arrow_type_lower:
                return value
        
        # Default fallback
        return 'target'
    
    def _extract_main_content(self, content: str) -> str:
        """Extract the main product content, skipping navigation and headers"""
        
        # Split content into chunks
        lines = content.split('\n')
        
        # Look for content sections that likely contain specifications
        spec_keywords = [
            'specification', 'specs', 'technical', 'diameter', 'spine', 'gpi', 
            'weight', 'grains', 'carbon', 'straightness', 'tolerance', 'material',
            'length', 'features', 'performance', 'description', 'details'
        ]
        
        # Find sections with high concentration of spec keywords
        relevant_sections = []
        current_section = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Skip obvious navigation content
            if any(nav in line_lower for nav in ['menu', 'nav', 'header', 'footer', 'login', 'cart', 'checkout']):
                continue
            
            # Check if line contains specification keywords
            has_spec_keywords = any(keyword in line_lower for keyword in spec_keywords)
            
            # Look for numeric patterns that suggest specifications
            import re
            has_spine_pattern = bool(re.search(r'\b[2-7]\d{2}\b', line))  # 200-799
            has_diameter_pattern = bool(re.search(r'\b0\.[2-4]\d{2}\b', line))  # 0.2xx
            has_gpi_pattern = bool(re.search(r'\d+\.\d+\s*gpi\b', line_lower))
            
            if has_spec_keywords or has_spine_pattern or has_diameter_pattern or has_gpi_pattern:
                # Include some context around specification lines
                start_context = max(0, i-3)
                end_context = min(len(lines), i+4)
                relevant_sections.extend(lines[start_context:end_context])
        
        # If we found relevant sections, use them
        if relevant_sections:
            main_content = '\n'.join(relevant_sections)
            # Limit to reasonable size
            return main_content[:6000] if len(main_content) > 6000 else main_content
        
        # Fallback: skip first 2000 chars (navigation) and take next 4000
        if len(content) > 2000:
            return content[2000:6000]
        else:
            return content[:4000]
    
    def extract_arrows_from_content(self, content: str, source_url: str, manufacturer: str) -> List[ArrowSpecification]:
        """Extract arrow specifications from webpage content"""
        
        # Find the main content by skipping navigation and focusing on product details
        content_excerpt = self._extract_main_content(content)
        
        extraction_prompt = f"""
        You are an expert arrow specification extractor. Analyze the webpage content and extract detailed arrow specifications.

        Return ONLY a valid JSON object with this exact structure:

        {{
          "arrows": [
            {{
              "model_name": "Complete Arrow Model Name",
              "spine_options": [300, 340, 400, 500],
              "diameter": 0.246,
              "inner_diameter": 0.204,
              "gpi_weight": 8.5,
              "length_options": [28, 29, 30, 31, 32],
              "material": "Carbon Fiber",
              "arrow_type": "target",
              "recommended_use": ["target", "indoor", "outdoor"],
              "description": "Brief description of arrow features and purpose"
            }}
          ]
        }}

        EXTRACTION REQUIREMENTS:
        
        🏹 REQUIRED FIELDS (must have all to include arrow):
        - model_name: Full product name
        - spine_options: List of spine stiffness values (numbers like 300, 340, 400)
        - diameter: Outer diameter in inches (like 0.246, 0.204)
        - gpi_weight: Grains per inch weight (like 8.5, 9.3)

        📏 MEASUREMENT FIELDS:
        - inner_diameter: Inside diameter if mentioned (ID)
        - length_options: Available shaft lengths in inches [28, 29, 30, 31, 32]

        🎯 USAGE CLASSIFICATION:
        - arrow_type: Primary category from: target, hunting, indoor, outdoor, 3d, recreational
        - recommended_use: Array of all mentioned uses like ["target", "indoor", "field", "3d"]

        📝 DESCRIPTION:
        - Extract key features, technology, or selling points in 1-2 sentences
        - Focus on what makes this arrow special or its intended purpose

        EXTRACTION RULES:
        1. Look for technical specifications, charts, tables, product details
        2. Spine values are typically 200-900 range (300, 340, 400, 500, etc.)
        3. Diameter often shown as "OD" (outer) or "ID" (inner) 
        4. GPI = Grains Per Inch weight measurement
        5. Length usually 28"-32" for target, 30"-33" for hunting
        6. Usage keywords: target, hunting, indoor, outdoor, 3d, field, recreational, competition
        7. If ranges like "300-500 spine", extract as [300, 340, 400, 500]
        8. Skip arrows without complete technical specs
        9. Return empty array if no valid arrows found

        CONTENT TO ANALYZE:
        {content_excerpt}
        
        Extract all arrow models with complete specifications. Focus on technical data and usage descriptions.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            cleaned_result = self.clean_json_response(result)
            
            # Parse JSON response
            try:
                data = json.loads(cleaned_result)
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                print(f"Raw response: {result[:200]}...")
                return []
            
            # Convert to ArrowSpecification objects
            arrows = []
            for arrow_data in data.get('arrows', []):
                try:
                    # Normalize arrow type
                    arrow_type = self.normalize_arrow_type(arrow_data.get('arrow_type', ''))
                    if arrow_type:
                        arrow_data['arrow_type'] = arrow_type
                    else:
                        arrow_data.pop('arrow_type', None)
                    
                    # Validate and clean numeric fields
                    if 'inner_diameter' in arrow_data and arrow_data['inner_diameter'] is None:
                        arrow_data.pop('inner_diameter', None)
                    
                    # Ensure spine_options is a list of integers
                    if 'spine_options' in arrow_data:
                        spines = arrow_data['spine_options']
                        if isinstance(spines, list):
                            arrow_data['spine_options'] = [int(s) for s in spines if isinstance(s, (int, str)) and str(s).isdigit()]
                    
                    # Ensure length_options is a list of integers if present
                    if 'length_options' in arrow_data and arrow_data['length_options']:
                        lengths = arrow_data['length_options']
                        if isinstance(lengths, list):
                            arrow_data['length_options'] = [int(l) for l in lengths if isinstance(l, (int, str)) and str(l).replace('.', '').isdigit()]
                    
                    # Create arrow specification
                    arrow = ArrowSpecification(
                        manufacturer=manufacturer,
                        source_url=source_url,
                        **arrow_data
                    )
                    arrows.append(arrow)
                    
                except Exception as e:
                    print(f"Warning: Failed to create arrow specification: {e}")
                    print(f"Data: {arrow_data}")
                    continue
            
            return arrows
            
        except Exception as e:
            print(f"Error during extraction: {e}")
            return []
    
    def test_extraction(self) -> bool:
        """Test the extractor with sample content"""
        test_content = """
        Easton Legacy Carbon Arrows
        
        The Legacy series offers exceptional performance for target shooting and competition.
        Features precision construction and consistent performance.
        
        Technical Specifications:
        - Available Spines: 400, 500, 600, 700
        - Outer Diameter (OD): 0.246 inches
        - Inner Diameter (ID): 0.204 inches
        - Weight: 8.1 GPI (Grains Per Inch) 
        - Straightness: ±0.003"
        - Weight Tolerance: ±1.0 grain
        - Material: 100% Carbon Fiber Construction
        - Recommended Use: Target, Field, 3D, Indoor, Outdoor Competition
        - Available Lengths: 28", 29", 30", 31", 32"
        - Price: $11.50 per shaft
        
        Perfect for target archery, indoor competitions, outdoor field courses, and 3D tournaments.
        """
        
        arrows = self.extract_arrows_from_content(
            content=test_content,
            source_url="https://test.com",
            manufacturer="Easton"
        )
        
        if arrows:
            print(f"✓ Test extraction successful: {len(arrows)} arrows found")
            arrow = arrows[0]
            print(f"  Model: {arrow.model_name}")
            print(f"  Spines: {arrow.spine_options}")
            print(f"  Outer Diameter: {arrow.diameter}")
            print(f"  Inner Diameter: {arrow.inner_diameter}")
            print(f"  GPI Weight: {arrow.gpi_weight}")
            print(f"  Lengths: {arrow.length_options}")
            print(f"  Type: {arrow.arrow_type}")
            print(f"  Uses: {arrow.recommended_use}")
            print(f"  Description: {arrow.description}")
            return True
        else:
            print("✗ Test extraction failed: no arrows found")
            return False

def main():
    """Test the production extractor"""
    print("DeepSeek Arrow Extractor Test")
    print("=" * 35)
    
    try:
        extractor = DeepSeekArrowExtractor()
        success = extractor.test_extraction()
        
        if success:
            print("\n🎉 DeepSeek extractor ready for production!")
            print("\nNext steps:")
            print("1. Integrate with Crawl4AI pipeline")
            print("2. Test on real manufacturer pages")
            print("3. Implement batch processing")
        else:
            print("\n⚠️  Extractor needs refinement")
            
    except Exception as e:
        print(f"✗ Extractor initialization failed: {e}")

if __name__ == "__main__":
    main()