#!/bin/bash

# Manual Setup Script - Works around externally managed Python environments
# This script manually sets up the environment without using pip in the system Python

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Manual Setup for Externally Managed Environment${NC}"
echo -e "${BLUE}=================================================${NC}"

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

# Check if we're in the right directory
if [ ! -d "arrow_scraper" ]; then
    print_error "Please run this script from the archerytools root directory"
    exit 1
fi

# Navigate to arrow_scraper
cd arrow_scraper

# Step 1: Install system packages if needed
echo -e "${BLUE}📦 Installing system packages...${NC}"
if command -v apt >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y python3-full python3-venv python3-pip
    print_status "System packages installed"
elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y python3 python3-venv python3-pip
    print_status "System packages installed (yum)"
else
    print_warning "Package manager not detected, assuming packages are installed"
fi

# Step 2: Create virtual environment
echo -e "${BLUE}🐍 Setting up virtual environment...${NC}"
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

python3 -m venv venv
print_status "Virtual environment created"

# Step 3: Activate and install packages
echo -e "${BLUE}🔧 Installing Python packages in virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install minimal requirements
if [ -f "requirements-minimal.txt" ]; then
    echo -e "${BLUE}Installing minimal requirements...${NC}"
    pip install -r requirements-minimal.txt
    print_status "Minimal requirements installed"
elif [ -f "requirements.txt" ]; then
    echo -e "${BLUE}Installing from requirements.txt...${NC}"
    pip install -r requirements.txt || print_warning "Some packages may have failed to install"
else
    # Fallback to manual package installation
    PACKAGES=(
        "requests"
        "python-dotenv"
        "pydantic"
    )

    for package in "${PACKAGES[@]}"; do
        echo -e "${BLUE}Installing $package...${NC}"
        if pip install "$package"; then
            print_status "$package installed"
        else
            print_warning "$package installation failed, continuing..."
        fi
    done
fi

# Try to install crawl4ai (might fail, that's OK)
echo -e "${BLUE}Attempting to install crawl4ai...${NC}"
if pip install crawl4ai; then
    print_status "crawl4ai installed"
else
    print_warning "crawl4ai installation failed - will use alternative methods"
fi

# Step 4: Test the environment
echo -e "${BLUE}🧪 Testing environment...${NC}"
python -c "
import sys
import sqlite3
import json
import os
from pathlib import Path

print(f'Python version: {sys.version}')
print('✅ Core Python modules available')

# Test sqlite3
try:
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE test (id INTEGER PRIMARY KEY)')
    conn.close()
    print('✅ SQLite3 working')
except Exception as e:
    print(f'❌ SQLite3 error: {e}')

# Test requests if available
try:
    import requests
    print('✅ Requests module available')
except ImportError:
    print('⚠️  Requests module not available')

# Test pathlib
try:
    from pathlib import Path
    test_path = Path('.')
    print('✅ Pathlib working')
except Exception as e:
    print(f'❌ Pathlib error: {e}')

print('\\n🎯 Environment test completed')
"

# Step 5: Initialize databases with basic structure
echo -e "${BLUE}🗄️  Initializing basic database structure...${NC}"
python -c "
import sqlite3
import os
from pathlib import Path

# Create data directories
Path('data/raw').mkdir(parents=True, exist_ok=True)
Path('data/processed').mkdir(parents=True, exist_ok=True)
Path('logs').mkdir(parents=True, exist_ok=True)

# Initialize basic arrow database
conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()

# Create basic arrows table
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

# Create spine_specifications table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS spine_specifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arrow_id INTEGER,
        spine INTEGER,
        outer_diameter REAL,
        inner_diameter REAL,
        gpi_weight REAL,
        FOREIGN KEY (arrow_id) REFERENCES arrows (id)
    )
''')

conn.commit()
conn.close()

print('✅ Basic arrow database structure created')

# Initialize user database
from pathlib import Path
sys.path.append(str(Path.cwd()))

try:
    exec(open('user_database.py').read())
    print('✅ User database initialized')
except Exception as e:
    print(f'⚠️  User database initialization failed: {e}')
    # Create basic user database manually
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
    conn.commit()
    conn.close()
    print('✅ Basic user database structure created')
"

# Step 6: Create some sample data
echo -e "${BLUE}📝 Creating sample arrow data...${NC}"
python -c "
import sqlite3
import json

# Add sample arrows
conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()

sample_arrows = [
    ('Easton', 'X10', 'Carbon', 'Target', 'Target, Indoor', 'Premium target arrow'),
    ('Gold Tip', 'Hunter Pro', 'Carbon', 'Hunting', 'Hunting, Outdoor', 'Reliable hunting arrow'),
    ('Victory', 'VAP V6', 'Carbon', 'Target', 'Target, 3D', 'Precision target arrow'),
    ('Traditional Archery', 'Cedar Shaft', 'Wood', 'Traditional', 'Traditional, Instinctive', 'Traditional cedar wood arrow'),
]

for manufacturer, model, material, arrow_type, use, desc in sample_arrows:
    cursor.execute('''
        INSERT INTO arrows (manufacturer, model_name, material, arrow_type, recommended_use, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (manufacturer, model, material, arrow_type, use, desc))
    
    arrow_id = cursor.lastrowid
    
    # Add sample spine specifications
    if material == 'Wood':
        spines = [40, 45, 50, 55, 60]
        base_gpi = 8.5
        base_diameter = 0.312
    else:
        spines = [300, 330, 350, 400, 500]
        base_gpi = 9.5
        base_diameter = 0.246
    
    for spine in spines:
        gpi = base_gpi + (spine - spines[0]) * 0.5 / 100
        diameter = base_diameter + (spine - spines[0]) * 0.001 / 100
        
        cursor.execute('''
            INSERT INTO spine_specifications (arrow_id, spine, outer_diameter, gpi_weight)
            VALUES (?, ?, ?, ?)
        ''', (arrow_id, spine, diameter, gpi))

conn.commit()
conn.close()

print('✅ Sample arrow data created')
"

# Step 7: Create activation script
echo -e "${BLUE}📜 Creating activation script...${NC}"
cat > activate.sh << 'EOF'
#!/bin/bash
# Activation script for the virtual environment
cd arrow_scraper
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "Python path: $(which python)"
echo "Python version: $(python --version)"
echo ""
echo "To run scripts:"
echo "  python arrow_database.py"
echo "  python api.py"
echo ""
echo "To deactivate:"
echo "  deactivate"
EOF

chmod +x activate.sh
print_status "Activation script created"

# Step 8: Test database
echo -e "${BLUE}🔍 Testing database...${NC}"
python arrow_database.py || print_warning "Database test had issues but continuing..."

echo -e "${GREEN}🎉 Manual setup completed!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo -e "1. ${YELLOW}Activate environment:${NC} cd arrow_scraper && source venv/bin/activate"
echo -e "2. ${YELLOW}Or use helper:${NC} ./activate.sh"
echo -e "3. ${YELLOW}Test database:${NC} python arrow_database.py"
echo -e "4. ${YELLOW}Start API:${NC} python api.py"
echo -e "5. ${YELLOW}Deactivate when done:${NC} deactivate"
echo ""
echo -e "${BLUE}Files created:${NC}"
echo -e "• arrow_scraper/venv/ - Virtual environment"
echo -e "• arrow_scraper/arrow_database.db - Arrow database with sample data"
echo -e "• arrow_scraper/user_data.db - User database"
echo -e "• activate.sh - Easy activation script"
echo ""
echo -e "${YELLOW}Note: This setup bypasses the externally managed environment restriction${NC}"
echo -e "${YELLOW}by using a proper virtual environment with isolated packages.${NC}"