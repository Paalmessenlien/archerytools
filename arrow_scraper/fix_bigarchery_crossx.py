#!/usr/bin/env python3
"""
Fix BigArchery/Cross-X manufacturer naming
Merges BigArchery arrows into Cross-X manufacturer
"""

import subprocess
import sys

def main():
    print("🏹 BigArchery → Cross-X Manufacturer Fix")
    print("="*50)
    
    # Show current state
    print("\n1. Current manufacturer statistics:")
    subprocess.run([sys.executable, "database_cleaner.py", "--list-manufacturers"])
    
    print("\n2. Preview the merge operation:")
    result = subprocess.run([
        sys.executable, "database_cleaner.py", 
        "--merge-manufacturers", "BigArchery", "Cross-X", 
        "--dry-run"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    
    # Ask for confirmation
    print("\n3. Execute the merge?")
    response = input("This will merge BigArchery arrows into Cross-X. Continue? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        print("\n4. Executing merge...")
        subprocess.run([
            sys.executable, "database_cleaner.py",
            "--merge-manufacturers", "BigArchery", "Cross-X"
        ])
        
        print("\n5. Updated manufacturer statistics:")
        subprocess.run([sys.executable, "database_cleaner.py", "--list-manufacturers"])
        
        print("\n✅ BigArchery → Cross-X merge completed!")
    else:
        print("\n❌ Merge cancelled.")

if __name__ == "__main__":
    main()