#!/bin/bash

# Virtual Environment Setup Script
# Handles externally managed Python environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐍 Python Virtual Environment Setup${NC}"
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

# Navigate to arrow_scraper directory
cd arrow_scraper

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if python3-venv is available
if ! python3 -c "import venv" &> /dev/null; then
    print_warning "python3-venv not available, trying to install..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3-venv python3-full
        print_status "python3-venv installed"
    else
        print_error "Cannot install python3-venv automatically. Please install it manually."
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}🏗️  Creating virtual environment...${NC}"
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
echo -e "${BLUE}🚀 Activating virtual environment...${NC}"
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo -e "${BLUE}📦 Upgrading pip...${NC}"
pip install --upgrade pip
print_status "Pip upgraded"

# Install requirements
echo -e "${BLUE}📋 Installing requirements...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Requirements installed"
else
    print_warning "requirements.txt not found, installing basic packages..."
    pip install requests crawl4ai python-dotenv
    print_status "Basic packages installed"
fi

# Test installation
echo -e "${BLUE}🧪 Testing installation...${NC}"
python -c "
import sys
import requests
import sqlite3
import asyncio
import json
import os
from pathlib import Path

print(f'Python version: {sys.version}')
print('✅ All core modules imported successfully')

# Test database connection
try:
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE test (id INTEGER)')
    conn.close()
    print('✅ SQLite database test passed')
except Exception as e:
    print(f'❌ SQLite test failed: {e}')

print('✅ Virtual environment setup completed successfully')
"

echo -e "${GREEN}🎉 Virtual environment setup completed!${NC}"
echo -e "${BLUE}===================================${NC}"
echo -e "${GREEN}To use the virtual environment:${NC}"
echo -e "  cd arrow_scraper"
echo -e "  source venv/bin/activate"
echo -e "  python your_script.py"
echo ""
echo -e "${GREEN}To deactivate:${NC}"
echo -e "  deactivate"
echo ""
echo -e "${YELLOW}Virtual environment path:${NC} $(pwd)/venv"