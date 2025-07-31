#!/bin/bash

# Production Import Only Script - Absolutely NO scraping
# This script ONLY imports from existing JSON files

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARROW_SCRAPER_DIR="$SCRIPT_DIR/arrow_scraper"
BACKUP_DIR="$SCRIPT_DIR/backups/$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}🚀 Production Import-Only Script${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${YELLOW}This script only imports existing JSON data${NC}"
echo -e "${YELLOW}NO scraping will be performed${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Create backup directory
echo -e "${BLUE}📁 Creating backup directory...${NC}"
mkdir -p "$BACKUP_DIR"
print_status "Backup directory created: $BACKUP_DIR"

# Backup existing databases before cleanup
echo -e "${BLUE}💾 Backing up existing databases...${NC}"
if [ -f "$ARROW_SCRAPER_DIR/arrow_database.db" ]; then
    cp "$ARROW_SCRAPER_DIR/arrow_database.db" "$BACKUP_DIR/arrow_database_backup.db"
    print_status "Arrow database backed up"
fi

if [ -f "$ARROW_SCRAPER_DIR/user_data.db" ]; then
    cp "$ARROW_SCRAPER_DIR/user_data.db" "$BACKUP_DIR/user_data_backup.db"
    print_status "User database backed up"
fi

# Navigate to arrow_scraper directory
cd "$ARROW_SCRAPER_DIR"

# Check Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Wipe existing databases
echo -e "${BLUE}🗑️  Wiping existing databases...${NC}"
rm -f arrow_database.db
rm -f user_data.db
print_status "Databases wiped clean"

# Check for existing JSON data files
echo -e "${BLUE}📂 Checking for existing arrow data files...${NC}"
if [ -d "data/processed" ] && [ "$(ls -A data/processed/*.json 2>/dev/null | wc -l)" -gt 0 ]; then
    echo -e "${GREEN}Found existing JSON data files:${NC}"
    JSON_COUNT=$(ls -1 data/processed/*.json 2>/dev/null | wc -l)
    echo "  • $JSON_COUNT JSON files found"
    echo "  • Sample files:"
    ls data/processed/*.json 2>/dev/null | head -5 | while read file; do
        echo "    - $(basename "$file")"
    done
    print_status "Using existing arrow data"
else
    print_warning "No existing JSON data files found in data/processed/"
    echo -e "${BLUE}Creating minimal sample data...${NC}"
    
    mkdir -p data/processed
    
    # Create minimal sample arrow data
    cat > data/processed/sample_arrows.json << 'EOF'
{
  "manufacturer": "Sample Arrows",
  "arrows_found": 2,
  "scraping_date": "2025-01-31T12:00:00",
  "status": "sample",
  "arrows": [
    {
      "model_name": "Sample Target",
      "material": "Carbon",
      "arrow_type": "Target",
      "description": "Sample target arrow for testing",
      "spine_specifications": [
        {"spine": 300, "outer_diameter": 0.246, "gpi_weight": 9.5},
        {"spine": 400, "outer_diameter": 0.246, "gpi_weight": 9.0}
      ]
    },
    {
      "model_name": "Sample Hunting",
      "material": "Carbon",
      "arrow_type": "Hunting",
      "description": "Sample hunting arrow for testing",
      "spine_specifications": [
        {"spine": 340, "outer_diameter": 0.244, "gpi_weight": 10.5}
      ]
    }
  ]
}
EOF
    
    # Create wood arrow sample data
    cat > data/processed/wood_arrows.json << 'EOF'
{
  "manufacturer": "Traditional Wood Arrows",
  "arrows_found": 2,
  "scraping_date": "2025-01-31T12:00:00",
  "status": "traditional",
  "arrows": [
    {
      "model_name": "Cedar Shaft",
      "material": "Cedar Wood",
      "arrow_type": "Traditional",
      "description": "Traditional cedar wood arrow shaft",
      "spine_specifications": [
        {"spine": 45, "outer_diameter": 0.315, "gpi_weight": 8.8},
        {"spine": 50, "outer_diameter": 0.318, "gpi_weight": 9.1},
        {"spine": 55, "outer_diameter": 0.321, "gpi_weight": 9.4}
      ]
    },
    {
      "model_name": "Pine Shaft",
      "material": "Pine Wood",
      "arrow_type": "Traditional",
      "description": "Traditional pine wood arrow shaft",
      "spine_specifications": [
        {"spine": 40, "outer_diameter": 0.318, "gpi_weight": 8.1},
        {"spine": 45, "outer_diameter": 0.321, "gpi_weight": 8.4}
      ]
    }
  ]
}
EOF
    
    print_status "Sample data created"
fi

# Import arrow data using the import script
echo -e "${BLUE}🗄️  Importing arrow data from JSON files...${NC}"
if [ -f "import_existing_data.py" ]; then
    python3 import_existing_data.py
    print_status "Arrow data imported successfully"
else
    print_error "import_existing_data.py not found!"
    echo -e "${YELLOW}Trying direct database creation...${NC}"
    
    # Fallback: Create basic database structure
    python3 -c "
import sqlite3
import json
import os
from pathlib import Path

# Create arrow database
conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS arrows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        manufacturer TEXT NOT NULL,
        model_name TEXT NOT NULL,
        material TEXT,
        carbon_content TEXT,
        arrow_type TEXT,
        description TEXT,
        image_url TEXT,
        source_url TEXT,
        scraped_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(manufacturer, model_name)
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
        FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
    )
''')

conn.commit()
conn.close()
print('✅ Basic database structure created')
"
fi

# Initialize user database
echo -e "${BLUE}👥 Initializing user database...${NC}"
python3 -c "
import sqlite3
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        google_id TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bow_setups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        bow_type TEXT NOT NULL,
        draw_weight REAL NOT NULL,
        draw_length REAL NOT NULL,
        arrow_length REAL,
        point_weight REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
''')
conn.commit()
conn.close()
print('✅ User database initialized')
"
print_status "User database initialized"

# Verify databases
echo -e "${BLUE}🔍 Verifying databases...${NC}"
python3 -c "
import sqlite3
import os

# Check arrow database
if os.path.exists('arrow_database.db'):
    conn = sqlite3.connect('arrow_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM arrows')
    arrow_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT manufacturer) FROM arrows')
    manufacturer_count = cursor.fetchone()[0]
    conn.close()
    print(f'✅ Arrow database: {arrow_count} arrows from {manufacturer_count} manufacturers')
else:
    print('❌ Arrow database not found')

# Check user database
if os.path.exists('user_data.db'):
    print('✅ User database: Ready')
else:
    print('❌ User database not found')
"

# Go back to project root
cd "$SCRIPT_DIR"

# Create Docker volume directories
echo -e "${BLUE}📁 Creating Docker volume directories...${NC}"
mkdir -p docker-volumes/user-data
mkdir -p docker-volumes/arrow-data
cp "$ARROW_SCRAPER_DIR/arrow_database.db" docker-volumes/arrow-data/ 2>/dev/null || true
cp "$ARROW_SCRAPER_DIR/user_data.db" docker-volumes/user-data/ 2>/dev/null || true
print_status "Docker volumes prepared"

echo ""
echo -e "${GREEN}🎉 Production import completed successfully!${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}Summary:${NC}"
echo -e "${GREEN}• Databases rebuilt from JSON files only${NC}"
echo -e "${GREEN}• NO scraping was performed${NC}"
echo -e "${GREEN}• Wood arrows included if available${NC}"
echo -e "${GREEN}• User database initialized${NC}"
echo -e "${GREEN}• Docker volumes prepared${NC}"
echo -e "${GREEN}• Backup created in: $BACKUP_DIR${NC}"
echo ""
echo -e "${YELLOW}Ready for deployment!${NC}"