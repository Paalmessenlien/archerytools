#!/usr/bin/env python3
"""
CDN Integration Example for Arrow Scraper
Shows how to integrate CDN upload with the existing scraping workflow
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from image_handler import ImageHandler
from models import ArrowSpecification

class CDNIntegratedScraper:
    """Example scraper with CDN integration"""
    
    def __init__(self, manufacturer: str):
        self.manufacturer = manufacturer
        self.image_handler = ImageHandler(
            local_storage_dir=f"./data/images/{manufacturer.lower()}",
            cdn_enabled=True  # Auto-detect CDN config
        )
    
    def process_arrow_with_cdn(self, arrow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process arrow data and upload images to CDN"""
        
        # Extract basic arrow information
        manufacturer = arrow_data.get('manufacturer', self.manufacturer)
        model_name = arrow_data.get('model_name', 'Unknown Model')
        
        # Process images if they exist
        cdn_images = []
        
        # Process primary image
        if 'image_url' in arrow_data and arrow_data['image_url']:
            primary_result = self.image_handler.process_image(
                arrow_data['image_url'],
                manufacturer,
                model_name,
                "primary"
            )
            cdn_images.append(primary_result)
        
        # Process additional images
        if 'additional_images' in arrow_data:
            for i, image_url in enumerate(arrow_data['additional_images']):
                detail_result = self.image_handler.process_image(
                    image_url,
                    manufacturer,
                    model_name,
                    f"detail_{i+1}"
                )
                cdn_images.append(detail_result)
        
        # Update arrow data with CDN information
        enhanced_arrow_data = arrow_data.copy()
        
        # Set primary image URL (CDN if available, otherwise original)
        if cdn_images and cdn_images[0]['status'] == 'success':
            enhanced_arrow_data['image_url'] = cdn_images[0]['image_url']
            enhanced_arrow_data['local_image_path'] = cdn_images[0].get('local_path')
            
            # Add CDN metadata
            if 'cdn_url' in cdn_images[0]:
                enhanced_arrow_data['cdn_image_url'] = cdn_images[0]['cdn_url']
                enhanced_arrow_data['cdn_type'] = cdn_images[0].get('cdn_type')
        
        # Store all processed image information
        enhanced_arrow_data['processed_images'] = cdn_images
        
        return enhanced_arrow_data
    
    def batch_process_arrows(self, arrows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple arrows with CDN integration"""
        enhanced_arrows = []
        
        for i, arrow_data in enumerate(arrows_data):
            print(f"Processing arrow {i+1}/{len(arrows_data)}: {arrow_data.get('model_name', 'Unknown')}")
            
            try:
                enhanced_arrow = self.process_arrow_with_cdn(arrow_data)
                enhanced_arrows.append(enhanced_arrow)
                
                # Show progress
                if enhanced_arrow.get('cdn_image_url'):
                    print(f"  ✅ CDN: {enhanced_arrow['cdn_image_url']}")
                elif enhanced_arrow.get('image_url'):
                    print(f"  📁 Local: {enhanced_arrow['image_url']}")
                else:
                    print(f"  ❌ No images processed")
                    
            except Exception as e:
                print(f"  ❌ Error processing arrow: {e}")
                enhanced_arrows.append(arrow_data)  # Keep original data
            
            # Small delay to be respectful
            import time
            time.sleep(0.5)
        
        return enhanced_arrows

def migrate_existing_data_to_cdn():
    """Migrate existing scraped data to CDN"""
    print("🔄 Migrating Existing Data to CDN")
    print("=" * 50)
    
    # Find all processed JSON files
    data_dir = Path("./data/processed")
    if not data_dir.exists():
        print("❌ No processed data directory found")
        return
    
    for json_file in data_dir.glob("*.json"):
        print(f"\n📁 Processing: {json_file.name}")
        
        try:
            # Load existing data
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract manufacturer from filename
            manufacturer = json_file.stem.split('_')[0].replace('_', ' ')
            
            # Initialize scraper for this manufacturer
            scraper = CDNIntegratedScraper(manufacturer)
            
            # Process arrows in the file
            if 'arrows' in data:
                print(f"  Processing {len(data['arrows'])} arrows...")
                enhanced_arrows = scraper.batch_process_arrows(data['arrows'])
                
                # Update data with enhanced arrows
                data['arrows'] = enhanced_arrows
                data['cdn_migration_completed'] = True
                data['cdn_migration_timestamp'] = time.time()
                
                # Save enhanced data
                enhanced_filename = json_file.stem + "_cdn_enhanced.json"
                enhanced_path = data_dir / enhanced_filename
                
                with open(enhanced_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"  ✅ Enhanced data saved: {enhanced_filename}")
            
        except Exception as e:
            print(f"  ❌ Error processing {json_file}: {e}")

def test_cdn_integration():
    """Test CDN integration with sample data"""
    print("🧪 Testing CDN Integration")
    print("=" * 50)
    
    # Sample arrow data
    sample_arrows = [
        {
            "manufacturer": "Easton Archery",
            "model_name": "FMJ 5MM",
            "image_url": "https://www.eastonarchery.com/uploads/image/field/2024-01/FMJ-5mm-arrow.png",
            "spine_specifications": [
                {"spine": 340, "outer_diameter": 0.204, "gpi_weight": 9.5}
            ]
        },
        {
            "manufacturer": "Gold Tip",
            "model_name": "Hunter Pro",
            "image_url": "https://goldtip.com/images/arrows/hunter-pro-main.jpg",
            "additional_images": [
                "https://goldtip.com/images/arrows/hunter-pro-detail1.jpg",
                "https://goldtip.com/images/arrows/hunter-pro-detail2.jpg"
            ],
            "spine_specifications": [
                {"spine": 400, "outer_diameter": 0.246, "gpi_weight": 8.8}
            ]
        }
    ]
    
    # Initialize scraper
    scraper = CDNIntegratedScraper("Test Manufacturer")
    
    # Process sample arrows
    enhanced_arrows = scraper.batch_process_arrows(sample_arrows)
    
    # Show results
    print(f"\n📋 Processing Results:")
    for i, arrow in enumerate(enhanced_arrows):
        print(f"\n  Arrow {i+1}: {arrow['model_name']}")
        print(f"    Original URL: {arrow.get('image_url', 'None')}")
        
        if arrow.get('cdn_image_url'):
            print(f"    CDN URL: {arrow['cdn_image_url']}")
            print(f"    CDN Type: {arrow.get('cdn_type', 'Unknown')}")
        
        processed_images = arrow.get('processed_images', [])
        print(f"    Processed Images: {len(processed_images)}")
        
        for img in processed_images:
            if img['status'] == 'success':
                print(f"      ✅ {img.get('image_type', 'unknown')}: {img.get('cdn_url', img.get('image_url'))}")
            else:
                print(f"      ❌ {img.get('image_type', 'unknown')}: {img.get('error', 'Failed')}")

def show_cdn_setup_guide():
    """Show setup guide for CDN integration"""
    print("📖 CDN Setup Guide")
    print("=" * 50)
    
    print("\n🚀 Quick Setup for Cloudinary (Recommended):")
    print("1. Sign up at: https://cloudinary.com (free tier available)")
    print("2. Get your credentials from the dashboard")
    print("3. Set environment variables:")
    print("   export CLOUDINARY_CLOUD_NAME='your-cloud-name'")
    print("   export CLOUDINARY_API_KEY='your-api-key'")
    print("   export CLOUDINARY_API_SECRET='your-api-secret'")
    print("   export CDN_TYPE='cloudinary'")
    
    print("\n🔧 Setup for AWS S3 + CloudFront:")
    print("1. Create S3 bucket in AWS console")
    print("2. Create CloudFront distribution")
    print("3. Set environment variables:")
    print("   export AWS_S3_BUCKET='your-bucket-name'")
    print("   export AWS_CLOUDFRONT_DOMAIN='d123456789.cloudfront.net'")
    print("   export CDN_TYPE='s3'")
    
    print("\n💾 Local Storage (Development):")
    print("1. Set environment variables:")
    print("   export CDN_TYPE='local'")
    print("   export LOCAL_CDN_PATH='./static/images'")
    print("   export LOCAL_CDN_URL='http://localhost:5000/images'")
    
    print("\n📦 Install CDN Dependencies:")
    print("pip install cloudinary boto3 Pillow")
    
    print("\n✅ Benefits of CDN Integration:")
    print("• 🚀 Faster image loading worldwide")
    print("• 💾 Reduced server storage costs")  
    print("• 🔄 Automatic image optimization")
    print("• 📱 Responsive image delivery")
    print("• 🛡️ Built-in backup and redundancy")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_cdn_integration()
        elif command == "migrate":
            migrate_existing_data_to_cdn()
        elif command == "setup":
            show_cdn_setup_guide()
        else:
            print(f"Unknown command: {command}")
    else:
        print("🖼️ CDN Integration for Arrow Scraper")
        print("=" * 50)
        print("Available commands:")
        print("  python cdn_integration_example.py test     - Test CDN integration")
        print("  python cdn_integration_example.py migrate  - Migrate existing data")
        print("  python cdn_integration_example.py setup    - Show setup guide")
        print("")
        show_cdn_setup_guide()