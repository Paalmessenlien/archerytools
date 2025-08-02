#!/bin/bash

# Production Database Rebuild Script
# Rebuilds all databases from scratch with latest JSON data and migrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗄️ Production Database Rebuild${NC}"
echo -e "${BLUE}===============================${NC}"
echo -e "${YELLOW}This will completely rebuild all databases from scratch${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}$1${NC}"
}

# Navigate to arrow_scraper directory
cd arrow_scraper

# Step 1: Remove all existing databases
print_step "🧹 Step 1: Removing existing databases..."
rm -f arrow_database.db
rm -f user_data.db  
rm -f component_database.db
rm -f *.db
rm -rf logs/*
print_status "All database files removed"

# Step 2: Check for JSON data files
print_step "📋 Step 2: Checking JSON data files..."
JSON_COUNT=$(find data/processed -name "*.json" -not -path "*/archive/*" -not -name "*learn*" | wc -l || echo "0")
LEARN_COUNT=$(find data/processed -name "*learn*.json" -not -path "*/archive/*" | wc -l || echo "0")

echo "   Update files (will import): $JSON_COUNT"
echo "   Learn files (will skip): $LEARN_COUNT"

if [ "$JSON_COUNT" -eq 0 ]; then
    print_warning "No JSON update files found!"
    echo "   Available files:"
    find data/processed -name "*.json" -not -path "*/archive/*" | head -10 | sed 's/^/   /'
    echo ""
    echo "   This might be normal if this is a fresh clone without scraped data."
    echo "   The system will create empty databases that can be populated later."
fi

# Step 3: Initialize Arrow Database
print_step "🏹 Step 3: Creating arrow database..."
python3 -c "
import sys
sys.path.append('.')
from arrow_database import ArrowDatabase

print('Initializing arrow database...')
db = ArrowDatabase()
print('Arrow database initialized successfully')
"

# Step 4: Run Database Import (if JSON files exist)
if [ "$JSON_COUNT" -gt 0 ]; then
    print_step "📦 Step 4: Importing arrow data from JSON files..."
    python3 database_import_manager.py --import-all --force
    print_status "Arrow data imported"
else
    print_step "📦 Step 4: Skipping JSON import (no update files found)..."
    print_warning "Arrow database created but empty - no JSON data to import"
fi

# Step 5: Initialize User Database
print_step "👥 Step 5: Creating user database..."
python3 -c "
import sys
sys.path.append('.')
from user_database import UserDatabase

print('Initializing user database...')
user_db = UserDatabase()
print('User database initialized successfully')
"

# Step 6: Run Component Import (if available)
print_step "🧩 Step 6: Checking for component data..."
COMPONENT_COUNT=$(find data/processed/components -name "*.json" 2>/dev/null | wc -l || echo "0")
echo "   Component files found: $COMPONENT_COUNT"

if [ "$COMPONENT_COUNT" -gt 0 ] && [ -f "component_importer.py" ]; then
    print_step "🧩 Importing component data..."
    python3 component_importer.py --force || {
        print_warning "Component import failed - continuing without components"
    }
else
    print_warning "No component data to import"
fi

# Step 7: Database Verification
print_step "🔍 Step 7: Verifying databases..."

# Check arrow database
if [ -f "arrow_database.db" ]; then
    ARROW_COUNT=$(python3 -c "
import sqlite3
conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM arrows')
count = cursor.fetchone()[0]
print(count)
conn.close()
" 2>/dev/null || echo "0")
    
    MANUFACTURER_COUNT=$(python3 -c "
import sqlite3
conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(DISTINCT manufacturer) FROM arrows')
count = cursor.fetchone()[0]
print(count)
conn.close()
" 2>/dev/null || echo "0")
    
    print_status "Arrow database: $ARROW_COUNT arrows from $MANUFACTURER_COUNT manufacturers"
    
    if [ "$ARROW_COUNT" -gt 100 ]; then
        print_status "Arrow database has good data volume"
    else
        print_warning "Arrow database has low content ($ARROW_COUNT arrows)"
    fi
else
    print_warning "Arrow database file not found!"
fi

# Check user database
if [ -f "user_data.db" ]; then
    USER_DB_SIZE=$(ls -lh user_data.db | awk '{print $5}')
    print_status "User database: $USER_DB_SIZE"
else
    print_warning "User database file not found!"
fi

# Step 8: Test Database Connections
print_step "🔗 Step 8: Testing database connections..."

# Test arrow database connection
python3 -c "
from arrow_database import ArrowDatabase
db = ArrowDatabase()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print(f'Arrow database tables: {len(tables)}')
for table in tables:
    print(f'  - {table[0]}')
conn.close()
" || print_warning "Arrow database connection test failed"

# Test user database connection
python3 -c "
from user_database import UserDatabase
user_db = UserDatabase()
conn = user_db.get_connection()
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print(f'User database tables: {len(tables)}')
for table in tables:
    print(f'  - {table[0]}')
conn.close()
" || print_warning "User database connection test failed"

# Step 9: Apply Latest Migrations
print_step "🔄 Step 9: Ensuring latest migrations..."

# Run any additional migrations
python3 -c "
from user_database import UserDatabase
user_db = UserDatabase()
print('All migrations applied during UserDatabase initialization')
"

# Step 10: Database Statistics
print_step "📊 Step 10: Final database statistics..."

if [ "$ARROW_COUNT" -gt 0 ]; then
    echo ""
    echo "🏭 Top Manufacturers:"
    python3 -c "
import sqlite3
conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT manufacturer, COUNT(*) as count
    FROM arrows 
    GROUP BY manufacturer 
    ORDER BY count DESC 
    LIMIT 5
''')
for row in cursor.fetchall():
    print(f'   {row[0]}: {row[1]} arrows')
conn.close()
" 2>/dev/null || echo "   Unable to retrieve manufacturer statistics"
fi

echo ""
echo -e "${GREEN}🎯 Database rebuild completed!${NC}"
echo -e "${BLUE}===============================${NC}"
echo -e "${GREEN}Summary:${NC}"
echo -e "${BLUE}  Arrow Database: $ARROW_COUNT arrows from $MANUFACTURER_COUNT manufacturers${NC}"
echo -e "${BLUE}  User Database: Ready for user accounts and bow setups${NC}"
echo -e "${BLUE}  Component System: $COMPONENT_COUNT component files processed${NC}"

if [ "$ARROW_COUNT" -eq 0 ]; then
    echo ""
    print_warning "No arrow data imported. This could be because:"
    echo "   1. This is a fresh setup without scraped data"
    echo "   2. JSON files are missing from data/processed/"
    echo "   3. All JSON files are 'learn' files (excluded from import)"
    echo ""
    echo "   To add arrow data later:"
    echo "   1. Run scraper locally to generate JSON files"
    echo "   2. Copy JSON files to data/processed/"
    echo "   3. Run: python3 database_import_manager.py --import-all --force"
fi

echo ""
echo -e "${GREEN}✨ Databases are ready for production deployment!${NC}"

cd ..