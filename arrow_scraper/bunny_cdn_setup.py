#!/usr/bin/env python3
"""
Bunny CDN Setup Guide and Testing Tool
Complete guide for setting up Bunny CDN with your Arrow Tuner scraper
"""

import os
import requests
from pathlib import Path

# Load environment variables from root .env file
try:
    from dotenv import load_dotenv
    # Load from root .env file which now contains CDN configuration
    root_env_path = Path(__file__).parent.parent / '.env'
    if root_env_path.exists():
        load_dotenv(root_env_path)
        print(f"✅ Loaded environment from: {root_env_path}")
    else:
        print("⚠️ No root .env file found, using system environment variables")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables only")

from cdn_uploader import CDNUploader

def show_bunny_setup_guide():
    """Complete Bunny CDN setup guide"""
    print("🐰 Bunny CDN Setup Guide for Arrow Tuner")
    print("=" * 60)
    
    print("\n🚀 Step 1: Create Bunny CDN Account")
    print("1. Go to: https://bunny.net")
    print("2. Sign up for a free account")
    print("3. Verify your email address")
    print("4. Log in to the Bunny CDN dashboard")
    
    print("\n📦 Step 2: Create a Storage Zone")
    print("1. In the dashboard, go to 'Storage' > 'Storage Zones'")
    print("2. Click 'Add Storage Zone'")
    print("3. Choose a name like 'arrowtuner-images'")
    print("4. Select your preferred region:")
    print("   • 🇩🇪 Germany (de) - Recommended for Europe")
    print("   • 🇺🇸 New York (ny) - East Coast US")
    print("   • 🇺🇸 Los Angeles (la) - West Coast US")
    print("   • 🇸🇬 Singapore (sg) - Asia Pacific")
    print("   • 🇦🇺 Sydney (syd) - Australia")
    print("   • 🇬🇧 London (uk) - United Kingdom")
    print("5. Click 'Create Storage Zone'")
    print("6. Copy the 'Storage Zone Name' and 'Access Key'")
    
    print("\n🌐 Step 3: Create a Pull Zone (CDN)")
    print("1. Go to 'CDN' > 'Pull Zones'")
    print("2. Click 'Add Pull Zone'")
    print("3. Name: 'arrowtuner-cdn' (or similar)")
    print("4. Origin Type: 'Bunny Storage Zone'")
    print("5. Storage Zone: Select your storage zone from Step 2")
    print("6. Enable 'Optimizer' for automatic image optimization")
    print("7. Click 'Create Pull Zone'")
    print("8. Copy the 'CDN Hostname' (e.g., arrowtuner-cdn.b-cdn.net)")
    
    print("\n⚙️ Step 4: Configure Environment Variables")
    print("Add Bunny CDN settings to your root .env file:")
    print("")
    print("CDN_TYPE=bunnycdn")
    print("BUNNY_STORAGE_ZONE=your-storage-zone-name")
    print("BUNNY_ACCESS_KEY=your-storage-access-key")
    print("BUNNY_HOSTNAME=your-pullzone-hostname.b-cdn.net")
    print("BUNNY_REGION=de")
    print("")
    
    print("\n💰 Step 5: Pricing Information")
    print("Bunny CDN is very cost-effective:")
    print("• Storage: $0.01/GB/month")
    print("• Bandwidth: $0.01-0.05/GB (varies by region)")
    print("• No minimum fees or setup costs")
    print("• Free tier: 100GB bandwidth/month")
    
    print("\n🔧 Step 6: Test Your Setup")
    print("Run: python bunny_cdn_setup.py test")

def test_bunny_cdn_config():
    """Test Bunny CDN configuration"""
    print("🧪 Testing Bunny CDN Configuration")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        'BUNNY_STORAGE_ZONE',
        'BUNNY_ACCESS_KEY', 
        'BUNNY_HOSTNAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set these in your .env.cdn file or environment")
        return False
    
    print("✅ Environment variables configured")
    
    # Test CDN uploader initialization
    try:
        uploader = CDNUploader("bunnycdn")
        print("✅ Bunny CDN uploader initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Bunny CDN: {e}")
        return False
    
    # Test with local file first (more reliable)
    test_file_path = "test_image.txt"
    
    print(f"\n🔄 Testing file upload...")
    print(f"   Source: {test_file_path}")
    
    try:
        if not os.path.exists(test_file_path):
            # Create a simple test file
            with open(test_file_path, 'w') as f:
                f.write("Test file for CDN upload")
        
        result = uploader.upload_from_file(
            test_file_path,
            "Test Manufacturer", 
            "Test Arrow Model",
            "test"
        )
        
        if result and result.get('cdn_url'):
            print(f"✅ Upload successful!")
            print(f"   CDN URL: {result['cdn_url']}")
            print(f"   File Size: {result.get('bytes', 0)} bytes")
            print(f"   CDN Type: {result.get('cdn_type')}")
            
            # Test if the CDN URL is accessible
            try:
                response = requests.head(result['cdn_url'], timeout=10)
                if response.status_code == 200:
                    print("✅ CDN URL is accessible")
                else:
                    print(f"⚠️ CDN URL returned status: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Could not verify CDN URL: {e}")
            
            return True
        else:
            print("❌ Upload failed - no CDN URL returned")
            return False
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

def show_bunny_optimization_tips():
    """Show Bunny CDN optimization tips"""
    print("🚀 Bunny CDN Optimization Tips")
    print("=" * 50)
    
    print("\n📸 Image Optimization:")
    print("• Enable 'Optimizer' in your Pull Zone settings")
    print("• Automatic WebP conversion for modern browsers")
    print("• Automatic compression and resizing")
    print("• Query parameters for on-the-fly transformations:")
    print("  - ?width=400&height=300 (resize)")
    print("  - ?quality=80 (compression)")
    print("  - ?format=webp (format conversion)")
    
    print("\n⚡ Performance:")
    print("• Enable 'Browser Cache' (recommended: 1 year)")
    print("• Enable 'Edge Cache' (recommended: 1 month)")
    print("• Use 'Vary Cache' for different device types")
    print("• Enable 'GZIP Compression'")
    
    print("\n🛡️ Security:")
    print("• Enable 'Hotlink Protection' to prevent bandwidth theft")
    print("• Set up 'Token Authentication' for private content")
    print("• Configure 'CORS Headers' if needed")
    
    print("\n🌍 Geographic Distribution:")
    print("• Bunny CDN has 114+ edge locations worldwide")
    print("• Automatic routing to closest edge server")
    print("• Consider multiple storage zones for global coverage")

def get_bunny_storage_info():
    """Get storage zone information from Bunny API"""
    print("📊 Bunny CDN Storage Information")
    print("=" * 50)
    
    access_key = os.getenv('BUNNY_ACCESS_KEY')
    if not access_key:
        print("❌ BUNNY_ACCESS_KEY not found in environment")
        return
    
    try:
        # Get storage zones (requires API key, not storage access key)
        print("💡 To get detailed storage info, you need your main API key")
        print("   (different from storage access key)")
        print("   Find it in: Account > API > API Key")
        
    except Exception as e:
        print(f"❌ Error getting storage info: {e}")

def migrate_existing_images():
    """Helper to migrate existing local images to Bunny CDN"""
    print("🔄 Migrating Existing Images to Bunny CDN")
    print("=" * 50)
    
    # Look for existing image directories
    data_dir = Path("./data/images")
    if not data_dir.exists():
        print("❌ No existing images found in ./data/images")
        print("💡 Run this from the arrow_scraper directory")
        return
    
    try:
        uploader = CDNUploader("bunnycdn")
        
        total_uploaded = 0
        total_failed = 0
        
        for manufacturer_dir in data_dir.iterdir():
            if manufacturer_dir.is_dir():
                manufacturer = manufacturer_dir.name.replace('_', ' ').title()
                print(f"\n📁 Processing {manufacturer}...")
                
                results = uploader.batch_upload_from_directory(
                    str(manufacturer_dir), 
                    manufacturer
                )
                
                uploaded = len([r for r in results if r.get('cdn_url')])
                failed = len(results) - uploaded
                
                total_uploaded += uploaded
                total_failed += failed
                
                print(f"   ✅ Uploaded: {uploaded}")
                print(f"   ❌ Failed: {failed}")
        
        print(f"\n📊 Migration Summary:")
        print(f"   Total Uploaded: {total_uploaded}")
        print(f"   Total Failed: {total_failed}")
        print(f"   Success Rate: {total_uploaded/(total_uploaded+total_failed)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            success = test_bunny_cdn_config()
            if success:
                print("\n🎉 Bunny CDN is configured correctly!")
                print("You can now use CDN_TYPE=bunnycdn in your scraper")
            else:
                print("\n❌ Bunny CDN configuration needs fixing")
                print("Run: python bunny_cdn_setup.py")
                
        elif command == "optimize":
            show_bunny_optimization_tips()
            
        elif command == "info":
            get_bunny_storage_info()
            
        elif command == "migrate":
            migrate_existing_images()
            
        else:
            print(f"Unknown command: {command}")
            print("Available commands: test, optimize, info, migrate")
    else:
        show_bunny_setup_guide()
        print("\n🔧 Available Commands:")
        print("  python bunny_cdn_setup.py test     - Test your configuration")
        print("  python bunny_cdn_setup.py optimize - Show optimization tips")
        print("  python bunny_cdn_setup.py migrate  - Migrate existing images")
        print("  python bunny_cdn_setup.py info     - Show storage information")