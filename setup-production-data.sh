#!/bin/bash

# Setup Production Data - Copy real manufacturer files to proper location
# This script copies the real data files from production-data/ to arrow_scraper/data/processed/

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏹 Setting up Production Arrow Data${NC}"
echo -e "${BLUE}===================================${NC}"

# Create the processed directory if it doesn't exist
mkdir -p arrow_scraper/data/processed

# Copy all manufacturer data files
echo -e "${BLUE}📄 Copying 14 real manufacturer data files...${NC}"
cp production-data/*.json arrow_scraper/data/processed/

# Verify the copy
COPIED_FILES=$(ls -1 arrow_scraper/data/processed/*.json | wc -l)
echo -e "${GREEN}✅ Copied $COPIED_FILES manufacturer data files${NC}"

# List the files
echo -e "${BLUE}📊 Available manufacturer data:${NC}"
ls -la arrow_scraper/data/processed/*.json | while read line; do
    filename=$(echo "$line" | awk '{print $9}' | xargs basename)
    size=$(echo "$line" | awk '{print $5}')
    echo "   📄 $filename (${size} bytes)"
done

# Calculate total size
TOTAL_SIZE=$(du -sh arrow_scraper/data/processed/ | cut -f1)
echo -e "${GREEN}📊 Total data size: $TOTAL_SIZE${NC}"

echo ""
echo -e "${GREEN}🎉 Production data setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "${YELLOW}1. Run: ./production-import-only.sh${NC}"
echo -e "${YELLOW}2. Deploy: ./quick-deploy.sh${NC}"
echo -e "${YELLOW}3. Verify: Database should show 158+ arrows from 12 manufacturers${NC}"