#!/usr/bin/env python3
"""
Test script for the --update-all functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from main import update_all_manufacturers
from dotenv import load_dotenv
import os

async def test_update_all():
    """Test the update all functionality"""
    
    # Load environment
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        print("Please create a .env file with your API key")
        return False
    
    print("🧪 Testing --update-all functionality...")
    print("-" * 50)
    
    try:
        # Run in test mode (no force update)
        success = await update_all_manufacturers(deepseek_api_key, force_update=False)
        
        if success:
            print("✅ Test completed successfully!")
            return True
        else:
            print("⚠️  Test completed with warnings")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_update_all())
    sys.exit(0 if result else 1)