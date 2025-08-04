#!/bin/bash
# Populate Demo Arrow Data for Production Systems
# Creates a minimal set of arrow data for testing and demonstration

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏹 Populating Demo Arrow Data${NC}"
echo "============================="

# Check if running in Docker
if [ -f "/.dockerenv" ]; then
    echo -e "${BLUE}🐳 Running inside Docker container${NC}"
    IN_DOCKER=true
    ARROW_DB="/app/arrow_data/arrow_database.db"
else
    echo -e "${BLUE}💻 Running on host system${NC}"
    IN_DOCKER=false
    ARROW_DB="$SCRIPT_DIR/arrow_scraper/arrow_database.db"
fi

# Check if database exists
if [ ! -f "$ARROW_DB" ]; then
    echo -e "${RED}❌ Arrow database not found at: $ARROW_DB${NC}"
    echo -e "${BLUE}💡 Make sure the ArrowTuner system is running first${NC}"
    exit 1
fi

echo -e "${BLUE}📊 Database: $ARROW_DB${NC}"

# Function to add arrow data
add_arrow_data() {
    local manufacturer="$1"
    local model="$2"
    local spine="$3"
    local diameter="$4"
    local gpi="$5"
    
    sqlite3 "$ARROW_DB" << EOF
-- Insert arrow if it doesn't exist
INSERT OR IGNORE INTO arrows (manufacturer, model_name, created_at) 
VALUES ('$manufacturer', '$model', datetime('now'));

-- Get the arrow ID
INSERT OR IGNORE INTO spine_specifications (arrow_id, spine, outer_diameter, gpi_weight) 
SELECT id, $spine, $diameter, $gpi 
FROM arrows 
WHERE manufacturer = '$manufacturer' AND model_name = '$model';
EOF
}

echo -e "\n${YELLOW}📦 Adding demo arrow data...${NC}"

# Add some basic arrow data for testing
echo "   Adding Easton arrows..."
add_arrow_data "Easton Archery" "Axis 5mm" 340 0.204 8.2
add_arrow_data "Easton Archery" "Axis 5mm" 400 0.204 8.2
add_arrow_data "Easton Archery" "Axis 5mm" 500 0.204 8.2
add_arrow_data "Easton Archery" "Carbon One" 350 0.244 7.8
add_arrow_data "Easton Archery" "Carbon One" 400 0.244 7.8
add_arrow_data "Easton Archery" "Carbon One" 500 0.244 7.8

echo "   Adding Gold Tip arrows..."
add_arrow_data "Gold Tip" "Hunter XT" 340 0.246 8.5
add_arrow_data "Gold Tip" "Hunter XT" 400 0.246 8.5
add_arrow_data "Gold Tip" "Hunter XT" 500 0.246 8.5
add_arrow_data "Gold Tip" "Velocity" 300 0.244 7.2
add_arrow_data "Gold Tip" "Velocity" 340 0.244 7.2
add_arrow_data "Gold Tip" "Velocity" 400 0.244 7.2

echo "   Adding Victory arrows..."
add_arrow_data "Victory Archery" "VAP TKO" 300 0.204 6.9
add_arrow_data "Victory Archery" "VAP TKO" 350 0.204 6.9
add_arrow_data "Victory Archery" "VAP TKO" 400 0.204 6.9
add_arrow_data "Victory Archery" "RIP XV" 250 0.166 5.8
add_arrow_data "Victory Archery" "RIP XV" 300 0.166 5.8
add_arrow_data "Victory Archery" "RIP XV" 350 0.166 5.8

echo "   Adding Carbon Express arrows..."
add_arrow_data "Carbon Express" "Maxima RED" 250 0.203 8.0
add_arrow_data "Carbon Express" "Maxima RED" 350 0.203 8.0
add_arrow_data "Carbon Express" "Maxima RED" 450 0.203 8.0
add_arrow_data "Carbon Express" "PileDriver" 300 0.300 9.8
add_arrow_data "Carbon Express" "PileDriver" 400 0.300 9.8

# Check results
ARROW_COUNT=$(sqlite3 "$ARROW_DB" "SELECT COUNT(*) FROM arrows;")
SPINE_COUNT=$(sqlite3 "$ARROW_DB" "SELECT COUNT(*) FROM spine_specifications;")

echo -e "\n${GREEN}✅ Demo data populated successfully!${NC}"
echo -e "${BLUE}📊 Database statistics:${NC}"
echo -e "   Arrows: $ARROW_COUNT"
echo -e "   Spine specifications: $SPINE_COUNT"

# Show some sample data
echo -e "\n${BLUE}📋 Sample arrow data:${NC}"
sqlite3 -header -column "$ARROW_DB" << 'EOF'
SELECT 
    a.manufacturer,
    a.model_name,
    s.spine,
    s.outer_diameter,
    s.gpi_weight
FROM arrows a
JOIN spine_specifications s ON a.id = s.arrow_id
ORDER BY a.manufacturer, a.model_name, s.spine
LIMIT 10;
EOF

echo -e "\n${GREEN}🎉 Demo data setup completed!${NC}"
echo -e "${BLUE}💡 You can now test the ArrowTuner system with this arrow data${NC}"
echo -e "${BLUE}💡 Use the backup system to save this data: ./backup-databases.sh${NC}"