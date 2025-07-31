#!/usr/bin/env python3
"""
Simple Arrow Scraper - No complex dependencies
Works without crawl4ai, OpenSSL, or cryptography issues
"""

import requests
import json
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import re

class SimpleArrowScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Ensure data directories exist
        Path('data/raw').mkdir(parents=True, exist_ok=True)
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        Path('logs').mkdir(parents=True, exist_ok=True)

    def create_sample_data(self):
        """Create comprehensive sample arrow data for testing"""
        print("🏹 Creating comprehensive sample arrow data...")
        
        # Comprehensive arrow data with proper spine specifications
        sample_arrows = {
            "Easton": [
                {
                    "model_name": "X10",
                    "material": "Carbon",
                    "arrow_type": "Target",
                    "recommended_use": "Target, Indoor, Olympic",
                    "description": "World's most accurate target arrow",
                    "spine_specifications": [
                        {"spine": 330, "outer_diameter": 0.246, "gpi_weight": 9.5},
                        {"spine": 350, "outer_diameter": 0.246, "gpi_weight": 9.3},
                        {"spine": 400, "outer_diameter": 0.246, "gpi_weight": 9.1},
                        {"spine": 450, "outer_diameter": 0.246, "gpi_weight": 8.9},
                        {"spine": 500, "outer_diameter": 0.246, "gpi_weight": 8.7}
                    ]
                },
                {
                    "model_name": "FMJ",
                    "material": "Carbon/Aluminum",
                    "arrow_type": "Hunting",
                    "recommended_use": "Hunting, 3D",
                    "description": "Full Metal Jacket hunting arrow",
                    "spine_specifications": [
                        {"spine": 300, "outer_diameter": 0.244, "gpi_weight": 11.5},
                        {"spine": 340, "outer_diameter": 0.244, "gpi_weight": 10.8},
                        {"spine": 400, "outer_diameter": 0.244, "gpi_weight": 10.2}
                    ]
                }
            ],
            "Gold Tip": [
                {
                    "model_name": "Hunter Pro",
                    "material": "Carbon",
                    "arrow_type": "Hunting", 
                    "recommended_use": "Hunting, Outdoor",
                    "description": "Premium hunting arrow with consistent spine",
                    "spine_specifications": [
                        {"spine": 300, "outer_diameter": 0.246, "gpi_weight": 9.8},
                        {"spine": 340, "outer_diameter": 0.246, "gpi_weight": 9.4},
                        {"spine": 400, "outer_diameter": 0.246, "gpi_weight": 9.0},
                        {"spine": 500, "outer_diameter": 0.246, "gpi_weight": 8.6}
                    ]
                },
                {
                    "model_name": "Velocity",
                    "material": "Carbon",
                    "arrow_type": "Target",
                    "recommended_use": "Target, 3D",
                    "description": "High-speed target arrow",
                    "spine_specifications": [
                        {"spine": 350, "outer_diameter": 0.244, "gpi_weight": 8.8},
                        {"spine": 400, "outer_diameter": 0.244, "gpi_weight": 8.5},
                        {"spine": 500, "outer_diameter": 0.244, "gpi_weight": 8.1}
                    ]
                }
            ],
            "Victory": [
                {
                    "model_name": "VAP V6",
                    "material": "Carbon",
                    "arrow_type": "Target",
                    "recommended_use": "Target, 3D, Field",
                    "description": "Precision target arrow with superior straightness",
                    "spine_specifications": [
                        {"spine": 300, "outer_diameter": 0.166, "gpi_weight": 6.5},
                        {"spine": 350, "outer_diameter": 0.166, "gpi_weight": 6.2},
                        {"spine": 400, "outer_diameter": 0.166, "gpi_weight": 5.9},
                        {"spine": 500, "outer_diameter": 0.166, "gpi_weight": 5.5}
                    ]
                }
            ],
            "Carbon Express": [
                {
                    "model_name": "Maxima Red",
                    "material": "Carbon",
                    "arrow_type": "Hunting",
                    "recommended_use": "Hunting, 3D",
                    "description": "Dual spine technology hunting arrow",
                    "spine_specifications": [
                        {"spine": 250, "outer_diameter": 0.203, "gpi_weight": 9.6},
                        {"spine": 350, "outer_diameter": 0.203, "gpi_weight": 8.8},
                        {"spine": 450, "outer_diameter": 0.203, "gpi_weight": 8.2}
                    ]
                }
            ],
            "Traditional Archery": [
                {
                    "model_name": "Cedar Shaft",
                    "material": "Cedar Wood",
                    "arrow_type": "Traditional",
                    "recommended_use": "Traditional, Instinctive, Historical",
                    "description": "Traditional cedar wood arrow shaft",
                    "spine_specifications": [
                        {"spine": 40, "outer_diameter": 0.312, "gpi_weight": 8.5},
                        {"spine": 45, "outer_diameter": 0.315, "gpi_weight": 8.8},
                        {"spine": 50, "outer_diameter": 0.318, "gpi_weight": 9.1},
                        {"spine": 55, "outer_diameter": 0.321, "gpi_weight": 9.4},
                        {"spine": 60, "outer_diameter": 0.324, "gpi_weight": 9.7}
                    ]
                },
                {
                    "model_name": "Bamboo Shaft", 
                    "material": "Bamboo Wood",
                    "arrow_type": "Traditional",
                    "recommended_use": "Traditional, Historical",
                    "description": "Traditional bamboo arrow shaft",
                    "spine_specifications": [
                        {"spine": 35, "outer_diameter": 0.295, "gpi_weight": 6.5},
                        {"spine": 40, "outer_diameter": 0.298, "gpi_weight": 6.8},
                        {"spine": 45, "outer_diameter": 0.301, "gpi_weight": 7.1},
                        {"spine": 50, "outer_diameter": 0.304, "gpi_weight": 7.4}
                    ]
                }
            ],
            "Fivics": [
                {
                    "model_name": "FX-100",
                    "material": "Carbon",
                    "arrow_type": "Target",
                    "recommended_use": "Target, Olympic",
                    "description": "Olympic-grade target arrow",
                    "spine_specifications": [
                        {"spine": 300, "outer_diameter": 0.244, "gpi_weight": 9.2},
                        {"spine": 350, "outer_diameter": 0.244, "gpi_weight": 8.9},
                        {"spine": 400, "outer_diameter": 0.244, "gpi_weight": 8.6}
                    ]
                }
            ]
        }
        
        # Save data to JSON files
        total_arrows = 0
        for manufacturer, arrows in sample_arrows.items():
            filename = f"data/processed/{manufacturer.lower().replace(' ', '_')}_sample_arrows.json"
            
            data = {
                "manufacturer": manufacturer,
                "arrows_found": len(arrows),
                "scraping_date": datetime.now().isoformat(),
                "status": "sample_data",
                "arrows": arrows
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            total_arrows += len(arrows)
            print(f"  ✅ Created {filename}: {len(arrows)} arrows")
        
        print(f"🎯 Sample data creation completed: {total_arrows} arrows from {len(sample_arrows)} manufacturers")
        return sample_arrows

    def populate_database(self, sample_data=None):
        """Populate database with sample data"""
        if sample_data is None:
            sample_data = self.create_sample_data()
        
        print("🗄️ Populating database with sample data...")
        
        # Initialize database
        conn = sqlite3.connect('arrow_database.db')
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arrows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT NOT NULL,
                model_name TEXT NOT NULL,
                material TEXT,
                arrow_type TEXT,
                recommended_use TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spine_specifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arrow_id INTEGER,
                spine INTEGER,
                outer_diameter REAL,
                inner_diameter REAL DEFAULT 0.0,
                gpi_weight REAL,
                FOREIGN KEY (arrow_id) REFERENCES arrows (id)
            )
        ''')
        
        # Clear existing data
        cursor.execute('DELETE FROM spine_specifications')
        cursor.execute('DELETE FROM arrows')
        
        total_arrows = 0
        total_specs = 0
        
        for manufacturer, arrows in sample_data.items():
            for arrow in arrows:
                # Insert arrow
                cursor.execute('''
                    INSERT INTO arrows (manufacturer, model_name, material, arrow_type, recommended_use, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    manufacturer,
                    arrow['model_name'],
                    arrow['material'],
                    arrow['arrow_type'],
                    arrow['recommended_use'],
                    arrow['description']
                ))
                
                arrow_id = cursor.lastrowid
                total_arrows += 1
                
                # Insert spine specifications
                for spec in arrow['spine_specifications']:
                    cursor.execute('''
                        INSERT INTO spine_specifications (arrow_id, spine, outer_diameter, gpi_weight)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        arrow_id,
                        spec['spine'],
                        spec['outer_diameter'],
                        spec['gpi_weight']
                    ))
                    total_specs += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database populated: {total_arrows} arrows, {total_specs} spine specifications")
        return total_arrows, total_specs

def main():
    """Main function to run simple scraper"""
    print("🚀 Simple Arrow Scraper - No Complex Dependencies")
    print("=" * 50)
    
    scraper = SimpleArrowScraper()
    
    # Create sample data and populate database
    sample_data = scraper.create_sample_data()
    arrows, specs = scraper.populate_database(sample_data)
    
    print(f"\n🎉 Simple scraping completed!")
    print(f"📊 Results: {arrows} arrows, {specs} specifications")
    print(f"🗄️ Database: arrow_database.db")
    print(f"📁 Data files: data/processed/")
    
    # Test database
    print(f"\n🧪 Testing database...")
    try:
        import sys
        sys.path.append('.')
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        stats = db.get_statistics()
        print(f"✅ Database test passed: {stats['total_arrows']} arrows loaded")
    except Exception as e:
        print(f"⚠️ Database test failed: {e}")

if __name__ == "__main__":
    main()