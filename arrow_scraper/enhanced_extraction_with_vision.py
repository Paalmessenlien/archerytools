#!/usr/bin/env python3
"""
Enhanced Arrow Extraction with Vision Support

This demonstrates how to integrate OpenAI Vision OCR for image-based manufacturers
like Carbon Express while maintaining text-based extraction for others.
"""

import os
import sys
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from run_comprehensive_extraction import DirectLLMExtractor
from carbon_express_vision_extractor import VisionBasedExtractor
from models import ArrowSpecification

class EnhancedArrowExtractor(DirectLLMExtractor):
    """Enhanced extractor with both text and vision capabilities"""
    
    def __init__(self, deepseek_api_key: str, openai_api_key: str = None):
        super().__init__(deepseek_api_key)
        self.vision_extractor = None
        
        if openai_api_key:
            self.vision_extractor = VisionBasedExtractor(openai_api_key)
            print("✅ Vision extraction enabled (OpenAI GPT-4)")
        else:
            print("⚠️  Vision extraction disabled (no OpenAI API key)")
    
    def extract_arrow_data(self, content: str, url: str, html_content: str = "") -> List[ArrowSpecification]:
        """Enhanced extraction with vision fallback for image-based manufacturers"""
        
        # Try text-based extraction first (works for most manufacturers)
        arrows = super().extract_arrow_data(content, url)
        
        if arrows:
            print(f"✅ Text extraction successful: {len(arrows)} arrows found")
            return arrows
        
        # Check if this is a manufacturer known to use image-based specifications
        image_based_manufacturers = [
            "feradyne.com",  # Carbon Express
            "carbon-express",
            # Add other image-based manufacturers here
        ]
        
        is_image_based = any(manufacturer in url.lower() for manufacturer in image_based_manufacturers)
        
        if is_image_based and self.vision_extractor:
            print("🖼️  Detected image-based manufacturer - attempting vision extraction...")
            
            try:
                vision_arrows = self.vision_extractor.extract_carbon_express_data(
                    html_content, content, url
                )
                
                if vision_arrows:
                    print(f"✅ Vision extraction successful: {len(vision_arrows)} arrows found")
                    return vision_arrows
                else:
                    print("❌ Vision extraction found no specifications")
            
            except Exception as e:
                print(f"💥 Vision extraction error: {e}")
        
        elif is_image_based:
            print("🖼️  Image-based manufacturer detected but vision extraction unavailable")
            print("   Carbon Express likely stores specs in images - need OpenAI API key")
        
        # Return empty list if both methods fail
        print("❌ No specifications found with any extraction method")
        return []

def demonstrate_enhanced_extraction():
    """Demonstrate how the enhanced extractor would work"""
    
    print("🚀 Enhanced Arrow Extraction Demo")
    print("=" * 50)
    
    # This would be the usage in production
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")  # Would use your key when available
    
    if not deepseek_key:
        print("❌ DEEPSEEK_API_KEY required")
        return
    
    extractor = EnhancedArrowExtractor(deepseek_key, openai_key)
    
    # Test URLs for different manufacturer types
    test_cases = [
        {
            "name": "BigArchery (Text-based) ✅",
            "url": "https://www.bigarchery.com/gb/shafts_304_274_BC9/282-706-cross-x-shaft-ambitionpoint.html",
            "type": "text"
        },
        {
            "name": "Carbon Express (Image-based) 🖼️", 
            "url": "https://www.feradyne.com/product/maxima-sable-rz/",
            "type": "vision"
        },
        {
            "name": "DK Bow (Text-based, German) ✅",
            "url": "https://dkbow.de/Pfeile/DK-Carbon-Arrows/DK-Cougar-ID4.2/",
            "type": "text"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 {test_case['name']}")
        print(f"URL: {test_case['url']}")
        print(f"Expected method: {test_case['type']}")
        
        if test_case['type'] == 'vision' and not openai_key:
            print("⚠️  Would use vision extraction (OpenAI API needed)")
        elif test_case['type'] == 'text':
            print("✅ Would use text extraction (working)")
        
    print("\n" + "=" * 50)
    print("📊 EXTRACTION CAPABILITY SUMMARY:")
    print("✅ Text-based manufacturers: BigArchery, DK Bow, Nijora, Easton, Skylon, Gold Tip")
    print("🖼️  Image-based manufacturers: Carbon Express (requires OpenAI API)")
    print("❓ Untested: Victory Archery, Pandarus Archery")
    
    if openai_key:
        print("🎯 Full capability: Both text and vision extraction available")
    else:
        print("⚠️  Limited capability: Only text extraction available")
        print("   Note: Carbon Express and other image-based manufacturers won't work")

if __name__ == "__main__":
    demonstrate_enhanced_extraction()