#!/usr/bin/env python3
"""
Database Schema Enhancement for Retailer Data
Adds tables and fields to store complementary arrow data from retailers
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def enhance_database_schema(db_path: str = "arrow_database.db"):
    """Add retailer data tables and enhance existing schema"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🔧 Enhancing database schema: {db_path}")
    
    try:
        # Add retailer_data column to existing arrows table
        print("   Adding retailer_data column to arrows table...")
        cursor.execute("""
            ALTER TABLE arrows 
            ADD COLUMN retailer_data TEXT DEFAULT NULL
        """)
        print("   ✅ Added retailer_data column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("   ⚠️  retailer_data column already exists")
        else:
            print(f"   ❌ Error adding retailer_data column: {e}")
    
    try:
        # Create retailer_sources table
        print("   Creating retailer_sources table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retailer_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                retailer_name TEXT NOT NULL,
                base_url TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                currency TEXT DEFAULT 'USD',
                scraping_config TEXT,  -- JSON config for scraping
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(retailer_name, base_url)
            )
        """)
        print("   ✅ Created retailer_sources table")
    except sqlite3.Error as e:
        print(f"   ❌ Error creating retailer_sources table: {e}")
    
    try:
        # Create retailer_arrow_data table for detailed retailer information
        print("   Creating retailer_arrow_data table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retailer_arrow_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arrow_id INTEGER NOT NULL,
                retailer_id INTEGER NOT NULL,
                source_url TEXT NOT NULL,
                
                -- Pricing and availability
                price REAL,
                currency TEXT DEFAULT 'USD',
                stock_quantity INTEGER,
                availability_status TEXT,
                
                -- Enhanced specifications
                straightness_tolerance TEXT,
                weight_tolerance TEXT,
                additional_specs TEXT,  -- JSON for extra specs
                
                -- Performance data
                recommended_bow_types TEXT,  -- JSON array
                intended_uses TEXT,          -- JSON array
                performance_notes TEXT,      -- JSON array
                technical_notes TEXT,        -- JSON array
                
                -- Images and description
                retailer_images TEXT,        -- JSON array of image URLs
                product_description TEXT,
                
                -- Metadata
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (arrow_id) REFERENCES arrows (id),
                FOREIGN KEY (retailer_id) REFERENCES retailer_sources (id),
                UNIQUE(arrow_id, retailer_id)
            )
        """)
        print("   ✅ Created retailer_arrow_data table")
    except sqlite3.Error as e:
        print(f"   ❌ Error creating retailer_arrow_data table: {e}")
    
    try:
        # Create arrow_enhancements table for additional specifications
        print("   Creating arrow_enhancements table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arrow_enhancements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arrow_id INTEGER NOT NULL,
                
                -- Enhanced technical specs
                insert_compatibility TEXT,    -- Compatible insert types/weights
                nock_compatibility TEXT,      -- Compatible nock types
                point_compatibility TEXT,     -- Compatible point weights/types
                
                -- Performance characteristics
                penetration_rating INTEGER,  -- 1-10 scale
                accuracy_rating INTEGER,     -- 1-10 scale  
                durability_rating INTEGER,   -- 1-10 scale
                flight_characteristics TEXT, -- JSON with flight data
                
                -- Real-world data
                user_reviews_summary TEXT,   -- Summary of user feedback
                expert_recommendations TEXT, -- Expert opinions
                competition_usage TEXT,      -- Competition/tournament usage
                
                -- Testing data
                test_results TEXT,           -- JSON with test data
                ballistic_coefficient REAL,
                wind_resistance_rating INTEGER,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (arrow_id) REFERENCES arrows (id),
                UNIQUE(arrow_id)
            )
        """)
        print("   ✅ Created arrow_enhancements table")
    except sqlite3.Error as e:
        print(f"   ❌ Error creating arrow_enhancements table: {e}")
    
    try:
        # Create price_history table for tracking price changes
        print("   Creating price_history table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arrow_id INTEGER NOT NULL,
                retailer_id INTEGER NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                stock_quantity INTEGER,
                availability_status TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (arrow_id) REFERENCES arrows (id),
                FOREIGN KEY (retailer_id) REFERENCES retailer_sources (id)
            )
        """)
        print("   ✅ Created price_history table")
    except sqlite3.Error as e:
        print(f"   ❌ Error creating price_history table: {e}")
    
    # Insert default retailer sources
    try:
        print("   Adding default retailer sources...")
        retailer_sources = [
            ("TopHat Archery", "https://tophatarchery.com", "de", "EUR", json.dumps({
                "selectors": {
                    "spine": "[data-spine], .spine-value",
                    "diameter": "[data-diameter], .diameter-value", 
                    "price": ".price, [data-price]",
                    "stock": "[data-stock], .stock-status"
                }
            })),
            ("Lancaster Archery", "https://www.lancasterarchery.com", "en", "USD", json.dumps({
                "selectors": {
                    "spine": ".spine-value, [data-spine]",
                    "price": ".price, .product-price",
                    "stock": ".stock-status, .availability"
                }
            })),
            ("3Rivers Archery", "https://www.3riversarchery.com", "en", "USD", json.dumps({
                "selectors": {
                    "spine": ".spine, [data-spine]",
                    "price": ".price, .product-price", 
                    "stock": ".stock, .availability"
                }
            }))
        ]
        
        for retailer in retailer_sources:
            cursor.execute("""
                INSERT OR IGNORE INTO retailer_sources 
                (retailer_name, base_url, language, currency, scraping_config)
                VALUES (?, ?, ?, ?, ?)
            """, retailer)
        
        print("   ✅ Added default retailer sources")
    except sqlite3.Error as e:
        print(f"   ❌ Error adding retailer sources: {e}")
    
    # Create indexes for performance
    try:
        print("   Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_retailer_arrow_data_arrow_id ON retailer_arrow_data(arrow_id)",
            "CREATE INDEX IF NOT EXISTS idx_retailer_arrow_data_retailer_id ON retailer_arrow_data(retailer_id)", 
            "CREATE INDEX IF NOT EXISTS idx_price_history_arrow_id ON price_history(arrow_id)",
            "CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at)",
            "CREATE INDEX IF NOT EXISTS idx_arrow_enhancements_arrow_id ON arrow_enhancements(arrow_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("   ✅ Created performance indexes")
    except sqlite3.Error as e:
        print(f"   ❌ Error creating indexes: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("✅ Database schema enhancement completed!")
    
    return True

def get_retailer_enhanced_data(db_path: str, arrow_id: int) -> dict:
    """Get enhanced data for an arrow from all retailer sources"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get basic arrow data
    cursor.execute("SELECT * FROM arrows WHERE id = ?", (arrow_id,))
    arrow = cursor.fetchone()
    
    if not arrow:
        return {}
    
    result = dict(arrow)
    
    # Get retailer data
    cursor.execute("""
        SELECT rad.*, rs.retailer_name, rs.currency as default_currency
        FROM retailer_arrow_data rad
        JOIN retailer_sources rs ON rad.retailer_id = rs.id
        WHERE rad.arrow_id = ?
        ORDER BY rad.updated_at DESC
    """, (arrow_id,))
    
    retailer_data = [dict(row) for row in cursor.fetchall()]
    result['retailer_data'] = retailer_data
    
    # Get enhancements
    cursor.execute("SELECT * FROM arrow_enhancements WHERE arrow_id = ?", (arrow_id,))
    enhancement = cursor.fetchone()
    if enhancement:
        result['enhancements'] = dict(enhancement)
    
    # Get price history (last 30 days)
    cursor.execute("""
        SELECT ph.*, rs.retailer_name
        FROM price_history ph
        JOIN retailer_sources rs ON ph.retailer_id = rs.id
        WHERE ph.arrow_id = ? 
        AND ph.recorded_at > datetime('now', '-30 days')
        ORDER BY ph.recorded_at DESC
    """, (arrow_id,))
    
    price_history = [dict(row) for row in cursor.fetchall()]
    result['price_history'] = price_history
    
    conn.close()
    return result

if __name__ == "__main__":
    # Test the schema enhancement
    enhance_database_schema()
    
    # Test data retrieval
    test_data = get_retailer_enhanced_data("arrow_database.db", 1)
    print(f"\n🧪 Test data for arrow ID 1:")
    print(f"   Basic data: {test_data.get('manufacturer', 'N/A')} {test_data.get('model_name', 'N/A')}")
    print(f"   Retailer sources: {len(test_data.get('retailer_data', []))}")
    print(f"   Enhancements: {'Yes' if test_data.get('enhancements') else 'No'}")
    print(f"   Price history entries: {len(test_data.get('price_history', []))}")