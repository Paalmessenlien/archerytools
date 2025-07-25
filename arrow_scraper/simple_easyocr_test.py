#!/usr/bin/env python3
"""
Simple EasyOCR test for Carbon Express images
"""

import requests
import re
import json
from pathlib import Path

def download_and_test_ocr():
    """Download image and test EasyOCR"""
    
    # Download test image
    url = "https://cdn-ilchokf.nitrocdn.com/nqkqluPOLqauqjblimVNksnJtfbWDRlW/assets/images/optimized/rev-c783676/www.feradyne.com/wp-content/uploads/2022/01/Maxima-Sable-RZ.png"
    
    print("🔍 Downloading Carbon Express specification image...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open("carbon_express_test.png", "wb") as f:
            f.write(response.content)
        print("✅ Image downloaded")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return
    
    # Test EasyOCR
    try:
        import easyocr
        
        print("🤖 Initializing EasyOCR...")
        reader = easyocr.Reader(['en'], verbose=False)
        
        print("📝 Extracting text from image...")
        results = reader.readtext("carbon_express_test.png")
        
        print(f"✅ EasyOCR found {len(results)} text elements")
        
        # Extract all text with confidence
        all_text = []
        specs_data = []
        
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Only confident detections
                all_text.append(text)
                print(f"  📖 '{text}' (confidence: {confidence:.2f})")
                
                # Look for spine/GPI patterns
                if re.match(r'^\d{3,4}$', text.strip()):  # Spine values
                    specs_data.append(("spine", text.strip()))
                elif re.match(r'^\d+\.\d+$', text.strip()):  # GPI values
                    specs_data.append(("gpi", text.strip()))
                elif text.lower() in ['spine', 'gpi', 'diameter', 'o.d.', 'weight']:
                    specs_data.append(("header", text.lower()))
        
        print(f"\n📊 Raw OCR Results:")
        print(f"Total text elements: {len(all_text)}")
        print(f"Specification elements: {len(specs_data)}")
        
        # Combine all text
        combined_text = " ".join(all_text)
        print(f"\n📄 Combined text ({len(combined_text)} chars):")
        print(combined_text[:500] + "..." if len(combined_text) > 500 else combined_text)
        
        # Parse for specifications
        spine_values = re.findall(r'\b(300|350|400|450|500|550|600|650|700|750|800|850|900|950|1000)\b', combined_text)
        gpi_values = re.findall(r'\b(\d+\.\d+)\b', combined_text)
        
        print(f"\n🎯 Parsed Results:")
        print(f"Potential spine values: {spine_values}")
        print(f"Potential GPI values: {gpi_values}")
        
        if spine_values and gpi_values:
            print("✅ SUCCESS: Found both spine and GPI data!")
            
            # Try to match them up
            result = {
                "model_name": "Maxima Sable RZ",
                "specifications": []
            }
            
            # Simple pairing (assumes they appear in order)
            for i, spine in enumerate(spine_values[:len(gpi_values)]):
                if i < len(gpi_values):
                    result["specifications"].append({
                        "spine": int(spine),
                        "gpi_weight": float(gpi_values[i])
                    })
            
            print(f"\n📋 Extracted {len(result['specifications'])} specifications:")
            for spec in result["specifications"]:
                print(f"   Spine {spec['spine']}: GPI {spec['gpi_weight']}")
        else:
            print("⚠️  Partial success: OCR worked but couldn't parse specifications clearly")
        
    except ImportError:
        print("❌ EasyOCR not available")
    except Exception as e:
        print(f"❌ EasyOCR error: {e}")
    finally:
        # Clean up
        try:
            Path("carbon_express_test.png").unlink()
            print("🗑️  Cleaned up test image")
        except:
            pass

if __name__ == "__main__":
    download_and_test_ocr()