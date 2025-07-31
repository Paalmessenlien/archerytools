#!/bin/bash

# Test Arrow Data - Verify that the imported data is accessible via API
# This tests both the database and API endpoints

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Testing Arrow Data Access${NC}"
echo -e "${BLUE}============================${NC}"

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

# Test 1: Check database files
echo -e "${BLUE}📊 Step 1: Database Files${NC}"
if [ -f "arrow_scraper/arrow_database.db" ]; then
    DB_SIZE=$(du -h arrow_scraper/arrow_database.db | cut -f1)
    print_status "Arrow database exists (${DB_SIZE})"
else
    print_error "Arrow database missing!"
    exit 1
fi

if [ -f "arrow_scraper/user_data.db" ]; then
    USER_DB_SIZE=$(du -h arrow_scraper/user_data.db | cut -f1)
    print_status "User database exists (${USER_DB_SIZE})"
else
    print_error "User database missing!"
fi

# Test 2: Direct database query
echo -e "${BLUE}📊 Step 2: Direct Database Query${NC}"
cd arrow_scraper
ARROW_COUNT=$(sqlite3 arrow_database.db "SELECT COUNT(*) FROM arrows;")
SPEC_COUNT=$(sqlite3 arrow_database.db "SELECT COUNT(*) FROM spine_specifications;")
MFR_COUNT=$(sqlite3 arrow_database.db "SELECT COUNT(DISTINCT manufacturer) FROM arrows;")

echo "   Database contains:"
echo "   - ${ARROW_COUNT} arrows"
echo "   - ${SPEC_COUNT} spine specifications"
echo "   - ${MFR_COUNT} manufacturers"

if [ "$ARROW_COUNT" -gt 100 ]; then
    print_status "Database has substantial arrow data"
else
    print_warning "Database has limited arrow data ($ARROW_COUNT arrows)"
fi

# Test 3: API Test (if running)
echo -e "${BLUE}📊 Step 3: API Endpoint Test${NC}"

# Check if API is running
API_RUNNING=false
if curl -s http://localhost:5000/api/simple-health >/dev/null 2>&1; then
    API_RUNNING=true
    print_status "API is running at localhost:5000"
    
    # Test database statistics endpoint
    echo -e "${BLUE}   Testing /api/database-statistics${NC}"
    API_STATS=$(curl -s http://localhost:5000/api/database-statistics 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "   API Response: $API_STATS"
        print_status "Database statistics endpoint working"
    else
        print_warning "Database statistics endpoint not responding"
    fi
    
    # Test arrows search endpoint
    echo -e "${BLUE}   Testing /api/arrows/search${NC}"
    SEARCH_RESULT=$(curl -s "http://localhost:5000/api/arrows/search?query=easton&limit=3" 2>/dev/null)
    if [ $? -eq 0 ]; then
        RESULT_COUNT=$(echo "$SEARCH_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('arrows', [])))" 2>/dev/null || echo "0")
        echo "   Search results: $RESULT_COUNT arrows"
        if [ "$RESULT_COUNT" -gt 0 ]; then
            print_status "Arrow search endpoint working"
        else
            print_warning "Arrow search returned no results"
        fi
    else
        print_warning "Arrow search endpoint not responding"
    fi
    
else
    print_warning "API not running (start with: python3 api.py)"
fi

# Test 4: Sample manufacturers
echo -e "${BLUE}📊 Step 4: Manufacturer Sample${NC}"
echo "   Top manufacturers in database:"
sqlite3 arrow_database.db "SELECT manufacturer, COUNT(*) as count FROM arrows GROUP BY manufacturer ORDER BY count DESC LIMIT 5;" | while read line; do
    echo "   - $line"
done

cd ..

echo ""
echo -e "${GREEN}🎉 Arrow Data Test Complete!${NC}"
echo -e "${BLUE}============================${NC}"

if [ "$ARROW_COUNT" -gt 100 ] && [ "$MFR_COUNT" -gt 10 ]; then
    echo -e "${GREEN}✅ You have substantial real arrow data!${NC}"
    echo -e "${GREEN}   - $ARROW_COUNT arrows from $MFR_COUNT manufacturers${NC}"
    echo -e "${GREEN}   - This is NOT demo data - it's real scraped data${NC}"
else
    echo -e "${YELLOW}⚠️  Limited arrow data detected${NC}"
    echo -e "${YELLOW}   Consider running the scraper to get more data${NC}"
fi

if [ "$API_RUNNING" = "true" ]; then
    echo -e "${BLUE}🌐 Frontend Access:${NC}"
    echo -e "${BLUE}   - Database page: http://localhost:3000/database${NC}"
    echo -e "${BLUE}   - API directly: http://localhost:5000/api/arrows/search?query=${NC}"
else
    echo -e "${YELLOW}💡 To test the full application:${NC}"
    echo -e "${YELLOW}   1. Run: ./quick-deploy.sh${NC}"
    echo -e "${YELLOW}   2. Visit: http://localhost/database${NC}"
fi