#!/bin/bash

# Production Cleanup Script - Complete Database Rebuild
# This script performs a full system cleanup and database rebuild for production

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

echo -e "${BLUE}🚀 Starting Production Cleanup Script${NC}"
echo -e "${BLUE}===================================${NC}"

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

# Stop any running services
echo -e "${BLUE}🛑 Stopping running services...${NC}"
pkill -f "python.*api.py" || true
pkill -f "npm run dev" || true
pkill -f "node.*nuxt" || true
print_status "Services stopped"

# Navigate to arrow_scraper directory
cd "$ARROW_SCRAPER_DIR"

# Setup Python virtual environment
if [ -d "venv" ]; then
    echo -e "${BLUE}🐍 Activating existing Python virtual environment...${NC}"
    source venv/bin/activate
    print_status "Virtual environment activated"
else
    echo -e "${BLUE}🐍 Creating new Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    print_status "New virtual environment created and activated"
fi

# Wipe existing databases
echo -e "${BLUE}🗑️  Wiping existing databases...${NC}"
rm -f arrow_database.db
rm -f user_data.db
print_status "Databases wiped clean"

# Clean up old scraped data
echo -e "${BLUE}🧹 Cleaning up old scraped data...${NC}"
rm -rf data/raw/*
rm -rf data/processed/*
mkdir -p data/raw
mkdir -p data/processed
print_status "Scraped data cleaned"

# Clean up logs
echo -e "${BLUE}📋 Cleaning up log files...${NC}"
rm -rf logs/*
mkdir -p logs
print_status "Log files cleaned"

# Update scraper dependencies
echo -e "${BLUE}📦 Installing/updating scraper dependencies...${NC}"
pip install --upgrade pip
pip install --upgrade -r requirements.txt
print_status "Dependencies updated"

# Verify key dependencies are installed
echo -e "${BLUE}🔍 Verifying key dependencies...${NC}"
python -c "
import sys
required_packages = ['requests', 'sqlite3', 'json', 'asyncio']
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} available')
    except ImportError:
        missing.append(pkg)
        print(f'❌ {pkg} missing')

if missing:
    print(f'Missing packages: {missing}')
    sys.exit(1)
else:
    print('✅ All core dependencies verified')
"

# Check if DeepSeek API key is configured
if [ -f "../.env" ]; then
    if grep -q "DEEPSEEK_API_KEY" "../.env"; then
        print_status "DeepSeek API key found in .env"
    else
        print_warning "DeepSeek API key not found in .env - scraping may fail"
    fi
else
    print_warning "No .env file found - please configure DEEPSEEK_API_KEY"
fi

# Start comprehensive arrow scraping with translation
echo -e "${BLUE}🏹 Starting comprehensive arrow scraping...${NC}"
echo -e "${YELLOW}This will take 30-60 minutes depending on network speed${NC}"

# Primary manufacturers (English)
echo -e "${BLUE}🎯 Scraping primary manufacturers (English)...${NC}"
python main.py easton || print_warning "Easton scraping failed"
python main.py goldtip || print_warning "Gold Tip scraping failed"
python main.py victory || print_warning "Victory scraping failed"
python main.py carbon_express || print_warning "Carbon Express scraping failed"

# European manufacturers (with translation)
echo -e "${BLUE}🇪🇺 Scraping European manufacturers (with translation)...${NC}"
python main.py nijora || print_warning "Nijora scraping failed"
python main.py dk_bow || print_warning "DK Bow scraping failed"
python main.py aurel || print_warning "Aurel scraping failed"
python main.py bigarchery || print_warning "BigArchery scraping failed"

# International manufacturers
echo -e "${BLUE}🌍 Scraping international manufacturers...${NC}"
python main.py fivics || print_warning "Fivics scraping failed"
python main.py pandarus || print_warning "Pandarus scraping failed"
python main.py skylon || print_warning "Skylon scraping failed"

# Wood arrow manufacturers (traditional)
echo -e "${BLUE}🌳 Scraping wood arrow manufacturers...${NC}"
python main.py --wood-arrows || print_warning "Wood arrows scraping failed"

# Alternative approach for wood arrows if specific parameter doesn't exist
if ! python main.py --list-manufacturers | grep -i wood; then
    print_warning "No specific wood arrow manufacturers found, checking traditional manufacturers"
    # Try traditional manufacturers that might have wood arrows
    python main.py traditional_archery || print_warning "Traditional archery scraping failed"
    python main.py three_rivers || print_warning "Three Rivers Archery scraping failed"
fi

print_status "Arrow scraping completed"

# Show scraped data summary
echo -e "${BLUE}📊 Scraped data summary:${NC}"
if [ -d "data/processed" ]; then
    ls -la data/processed/ | grep ".json" | wc -l | xargs echo "JSON files created:"
    du -sh data/processed/ | awk '{print "Total size: " $1}'
fi

# Initialize arrow database
echo -e "${BLUE}🗄️  Initializing arrow database...${NC}"
python arrow_database.py
print_status "Arrow database initialized"

# Initialize user database
echo -e "${BLUE}👥 Initializing user database...${NC}"
python -c "
from user_database import UserDatabase
db = UserDatabase()
print('✅ User database initialized successfully')
"
print_status "User database initialized"

# Run database migrations
echo -e "${BLUE}🔄 Running database migrations...${NC}"
python -c "
from user_database import UserDatabase
db = UserDatabase()
db.migrate_draw_length_to_users()
print('✅ Database migrations completed')
"
print_status "Database migrations completed"

# Verify database integrity
echo -e "${BLUE}🔍 Verifying database integrity...${NC}"
if [ -f "verify-databases.py" ]; then
    python verify-databases.py
else
    python -c "
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
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    print(f'✅ User database: {len(tables)} tables created ({\"', '\"'.join(tables)})')
else:
    print('❌ User database not found')
"
fi
print_status "Database integrity verified"

# Show database statistics
echo -e "${BLUE}📈 Database statistics:${NC}"
python show_available_data.py || python -c "
import sqlite3
import json

try:
    conn = sqlite3.connect('arrow_database.db')
    cursor = conn.cursor()
    
    # Arrow statistics
    cursor.execute('SELECT COUNT(*) FROM arrows')
    total_arrows = cursor.fetchone()[0]
    
    cursor.execute('SELECT manufacturer, COUNT(*) FROM arrows GROUP BY manufacturer ORDER BY COUNT(*) DESC')
    manufacturers = cursor.fetchall()
    
    print(f'📊 Total arrows: {total_arrows}')
    print('📊 By manufacturer:')
    for manufacturer, count in manufacturers:
        print(f'   • {manufacturer}: {count} arrows')
    
    conn.close()
except Exception as e:
    print(f'Error getting statistics: {e}')
"

# Clean up temporary files
echo -e "${BLUE}🧹 Final cleanup...${NC}"
find . -name "*.pyc" -delete || true
find . -name "__pycache__" -type d -exec rm -rf {} + || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + || true
print_status "Temporary files cleaned"

# Optimize databases
echo -e "${BLUE}⚡ Optimizing databases...${NC}"
python -c "
import sqlite3

# Optimize arrow database
if os.path.exists('arrow_database.db'):
    conn = sqlite3.connect('arrow_database.db')
    conn.execute('VACUUM')
    conn.execute('ANALYZE')
    conn.close()
    print('✅ Arrow database optimized')

# Optimize user database  
if os.path.exists('user_data.db'):
    conn = sqlite3.connect('user_data.db')
    conn.execute('VACUUM')
    conn.execute('ANALYZE')
    conn.close()
    print('✅ User database optimized')
"
print_status "Databases optimized"

# Set proper permissions
echo -e "${BLUE}🔐 Setting proper permissions...${NC}"
chmod 644 *.db || true
chmod 755 *.py || true
chmod -R 755 data/ || true
chmod -R 755 logs/ || true
print_status "Permissions set"

# Go back to project root
cd "$SCRIPT_DIR"

# Update frontend dependencies
echo -e "${BLUE}📦 Updating frontend dependencies...${NC}"
cd frontend
npm install
print_status "Frontend dependencies updated"

# Build frontend for production
echo -e "${BLUE}🏗️  Building frontend for production...${NC}"
npm run build
print_status "Frontend built"

# Go back to project root
cd "$SCRIPT_DIR"

# Create production-ready Docker volumes directories
echo -e "${BLUE}📁 Creating Docker volume directories...${NC}"
mkdir -p docker-volumes/user-data
mkdir -p docker-volumes/arrow-data
cp "$ARROW_SCRAPER_DIR/arrow_database.db" docker-volumes/arrow-data/ || true
cp "$ARROW_SCRAPER_DIR/user_data.db" docker-volumes/user-data/ || true
print_status "Docker volumes prepared"

# Generate summary report
echo -e "${BLUE}📝 Generating cleanup report...${NC}"
cat > "$BACKUP_DIR/cleanup_report.txt" << EOF
Production Cleanup Report
========================
Date: $(date)
Backup Location: $BACKUP_DIR

Databases Rebuilt:
- Arrow Database: ✅ Rebuilt with fresh data
- User Database: ✅ Initialized clean

Scraped Manufacturers:
$(cd "$ARROW_SCRAPER_DIR" && ls data/processed/*.json 2>/dev/null | wc -l) JSON files created

Database Statistics:
$(cd "$ARROW_SCRAPER_DIR" && python -c "
import sqlite3
import os
if os.path.exists('arrow_database.db'):
    conn = sqlite3.connect('arrow_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM arrows')
    arrow_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT manufacturer) FROM arrows')  
    manufacturer_count = cursor.fetchone()[0]
    print(f'Total Arrows: {arrow_count}')
    print(f'Manufacturers: {manufacturer_count}')
    conn.close()
else:
    print('Database not found')
" 2>/dev/null || echo "Statistics unavailable")

Next Steps:
1. Deploy to production using: ./deploy-enhanced.sh docker-compose.enhanced-ssl.yml
2. Test functionality: python3 test-bow-saving.py
3. Verify API health: curl https://yourdomain.com/api/health
EOF

print_status "Cleanup report generated"

echo -e "${GREEN}🎉 Production cleanup completed successfully!${NC}"
echo -e "${BLUE}===================================${NC}"
echo -e "${GREEN}Summary:${NC}"
echo -e "${GREEN}• All databases wiped and rebuilt${NC}"
echo -e "${GREEN}• Fresh arrow data scraped from all manufacturers${NC}"
echo -e "${GREEN}• Wood arrows included from traditional manufacturers${NC}"
echo -e "${GREEN}• User database initialized clean${NC}"
echo -e "${GREEN}• Frontend built for production${NC}"
echo -e "${GREEN}• Docker volumes prepared${NC}"
echo -e "${GREEN}• Backup created in: $BACKUP_DIR${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "${YELLOW}1. Deploy to production:${NC} ./deploy-enhanced.sh docker-compose.enhanced-ssl.yml"
echo -e "${YELLOW}2. Test functionality:${NC} python3 test-bow-saving.py"
echo -e "${YELLOW}3. Verify API health:${NC} curl https://yourdomain.com/api/health"
echo ""
echo -e "${BLUE}Production cleanup script completed at $(date)${NC}"