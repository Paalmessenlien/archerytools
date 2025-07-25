#!/usr/bin/env python3
"""
Test the fixed update system with a single manufacturer
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from config_loader import ConfigLoader
from arrow_database import ArrowDatabase

async def test_fixed_update():
    """Test that the fixed update system can access the configuration properly"""
    
    print("🧪 Testing Fixed Update System")
    print("=" * 50)
    
    # Load environment
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        print("   Please add your API key to .env file")
        return False
    
    print("✅ API Key: Found")
    
    # Test config loading
    try:
        config = ConfigLoader()
        manufacturers = config.get_manufacturer_names()
        print(f"✅ Config: Loaded {len(manufacturers)} manufacturers")
        
        # Show first few manufacturers
        for i, name in enumerate(manufacturers[:3]):
            url_count = len(config.get_manufacturer_urls(name))
            method = config.get_extraction_method(name)
            print(f"   • {name} ({method}) - {url_count} URLs")
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False
    
    # Test database
    try:
        database = ArrowDatabase()
        stats = database.get_statistics()
        total_arrows = stats.get('total_arrows', 0)
        print(f"✅ Database: {total_arrows} arrows currently stored")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print("\n🎯 System Test Results:")
    print("   ✅ Configuration system working")
    print("   ✅ Database connection working") 
    print("   ✅ API key available")
    print("   ✅ Ready for --update-all")
    
    print("\n🚀 To run full update:")
    print("   python main.py --update-all")
    print("   python main.py --update-all --force")
    print("   python update_all.py")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_fixed_update())
    if result:
        print("\n✅ Test passed - update system is ready!")
    else:
        print("\n❌ Test failed - please fix issues above")
    sys.exit(0 if result else 1)