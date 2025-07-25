#!/usr/bin/env python3
"""
Arrow Database Update All - Simple wrapper for --update-all functionality
Usage: python update_all.py [--force]
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from main import update_all_manufacturers

def load_environment():
    """Load environment variables"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        return True
    else:
        print("❌ .env file not found")
        print("Please create a .env file with your DEEPSEEK_API_KEY")
        print()
        print("Example .env file:")
        print("DEEPSEEK_API_KEY=your_api_key_here")
        return False

def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("🏹 ARROW DATABASE - UPDATE ALL MANUFACTURERS")
    print("=" * 70)
    print("🔄 This will update all manufacturer data in the arrow database")
    print("⏱️  Estimated time: 10-15 minutes depending on network speed")
    print("🌐 Will scrape from 9+ manufacturers including:")
    print("   • Easton Archery • Gold Tip • Victory Archery")
    print("   • Skylon Archery • Nijora Archery • DK Bow")
    print("   • Pandarus Archery • BigArchery • Carbon Express")
    print()

async def main():
    """Main update function"""
    force_update = "--force" in sys.argv
    
    print_banner()
    
    if not load_environment():
        sys.exit(1)
    
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        print("Please add your DeepSeek API key to the .env file")
        sys.exit(1)
    
    print("🔑 API Key: Found")
    print(f"🔄 Force update: {'Yes' if force_update else 'No'}")
    print()
    
    # Confirmation prompt
    if not force_update:
        print("ℹ️  This will only add new manufacturers that don't exist in the database.")
        print("   Use --force to update existing manufacturer data.")
    
    response = input("Continue with update? (y/N): ").lower().strip()
    if response not in ['y', 'yes']:
        print("❌ Update cancelled by user")
        sys.exit(0)
    
    print("\n🚀 Starting update process...")
    print("=" * 70)
    
    try:
        success = await update_all_manufacturers(deepseek_api_key, force_update)
        
        if success:
            print("\n🎉 All manufacturers updated successfully!")
            print("💾 Database has been updated with new arrow data")
            print("🌐 You can now use the web interface to browse updated arrows")
            return True
        else:
            print("\n⚠️  Update completed with some issues")
            print("📋 Check the logs above for details")
            return False
            
    except KeyboardInterrupt:
        print("\n\n🛑 Update interrupted by user")
        print("💾 Database may be partially updated")
        return False
    except Exception as e:
        print(f"\n❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        print("Options:")
        print("  --force    Force update existing manufacturer data")
        print("  --help     Show this help message")
        sys.exit(0)
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)