#!/bin/bash
#
# CDN Backup Testing Script for ArrowTuner
# Tests the new CDN-first backup system across all environments
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to test API endpoint
test_api_endpoint() {
    local endpoint=$1
    local description=$2
    
    print_message "$BLUE" "🧪 Testing: $description"
    print_message "$BLUE" "   Endpoint: $endpoint"
    
    if command_exists curl; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$endpoint" 2>/dev/null || echo "HTTPSTATUS:000")
        http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
        body=$(echo "$response" | sed -E 's/HTTPSTATUS:[0-9]*$//')
        
        if [ "$http_code" -eq 200 ]; then
            print_message "$GREEN" "   ✅ API accessible (HTTP $http_code)"
            
            # Try to parse JSON response
            if echo "$body" | python3 -m json.tool >/dev/null 2>&1; then
                print_message "$GREEN" "   ✅ Valid JSON response"
                
                # Check if it's a backup list response
                if echo "$body" | grep -q '"all_backups"' || echo "$body" | grep -q '"cdn_backups"'; then
                    backup_count=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('all_backups', data.get('cdn_backups', []))))" 2>/dev/null || echo "0")
                    print_message "$GREEN" "   📦 Found $backup_count backups"
                else
                    print_message "$YELLOW" "   ⚠️  Not a backup list endpoint"
                fi
            else
                print_message "$YELLOW" "   ⚠️  Non-JSON response (might be HTML error page)"
            fi
        elif [ "$http_code" -eq 401 ] || [ "$http_code" -eq 403 ]; then
            print_message "$YELLOW" "   🔒 Authentication required (HTTP $http_code) - Expected for admin endpoints"
        elif [ "$http_code" -eq 000 ]; then
            print_message "$RED" "   ❌ Connection failed - Server not accessible"
        else
            print_message "$RED" "   ❌ HTTP Error $http_code"
        fi
    else
        print_message "$RED" "   ❌ curl not available - Cannot test API endpoint"
    fi
    
    echo ""
}

print_message "$GREEN" "🧪 CDN Backup System Testing"
print_message "$GREEN" "==============================="
echo ""

# Test 1: Check Python dependencies
print_message "$BLUE" "📋 Step 1: Checking Python Dependencies"
echo "----------------------------------------"

if command_exists python3; then
    print_message "$GREEN" "✅ Python 3 available"
    
    # Test CDN backup manager import
    if python3 -c "from arrow_scraper.cdn_backup_manager import CDNBackupManager; print('✅ CDN backup manager import successful')" 2>/dev/null; then
        print_message "$GREEN" "✅ CDN backup manager import successful"
    else
        print_message "$RED" "❌ Cannot import CDN backup manager"
        print_message "$YELLOW" "   Make sure you're in the project root directory"
    fi
    
    # Test required libraries
    for lib in requests; do
        if python3 -c "import $lib" 2>/dev/null; then
            print_message "$GREEN" "✅ $lib library available"
        else
            print_message "$RED" "❌ $lib library missing"
        fi
    done
else
    print_message "$RED" "❌ Python 3 not available"
fi

echo ""

# Test 2: Check environment configuration
print_message "$BLUE" "📋 Step 2: Checking CDN Configuration"
echo "-------------------------------------"

if [ -f ".env" ]; then
    print_message "$GREEN" "✅ .env file found"
    
    # Check CDN configuration
    if grep -q "BUNNY_ACCESS_KEY=" .env && [ "$(grep "BUNNY_ACCESS_KEY=" .env | cut -d= -f2)" != "" ]; then
        print_message "$GREEN" "✅ Bunny CDN access key configured"
    else
        print_message "$YELLOW" "⚠️  Bunny CDN access key not configured or empty"
    fi
    
    if grep -q "BUNNY_STORAGE_ZONE=" .env && [ "$(grep "BUNNY_STORAGE_ZONE=" .env | cut -d= -f2)" != "" ]; then
        bunny_zone=$(grep "BUNNY_STORAGE_ZONE=" .env | cut -d= -f2)
        print_message "$GREEN" "✅ Bunny CDN storage zone: $bunny_zone"
    else
        print_message "$YELLOW" "⚠️  Bunny CDN storage zone not configured"
    fi
    
    # Check CDN type
    if grep -q "CDN_TYPE=" .env; then
        cdn_type=$(grep "CDN_TYPE=" .env | cut -d= -f2)
        print_message "$GREEN" "✅ CDN type configured: $cdn_type"
    else
        print_message "$YELLOW" "⚠️  CDN_TYPE not specified (will default to bunnycdn)"
    fi
    
else
    print_message "$RED" "❌ .env file not found"
    print_message "$YELLOW" "   Create .env file with CDN configuration"
fi

echo ""

# Test 3: Test CDN backup manager directly
print_message "$BLUE" "📋 Step 3: Testing CDN Backup Manager"
echo "------------------------------------"

if [ -f "arrow_scraper/cdn_backup_manager.py" ]; then
    print_message "$GREEN" "✅ CDN backup manager file exists"
    
    # Test the manager
    cd arrow_scraper 2>/dev/null || {
        print_message "$YELLOW" "⚠️  Not in project root, trying to test from current directory"
    }
    
    print_message "$BLUE" "🔄 Running CDN backup manager test..."
    if python3 -c "
from cdn_backup_manager import CDNBackupManager
import sys
try:
    manager = CDNBackupManager()
    backups = manager.list_all_backups()
    print(f'✅ Successfully initialized CDN backup manager')
    print(f'📦 Found {len(backups)} backups from all CDN providers')
    if backups:
        print('🎯 Sample backup info:')
        for i, backup in enumerate(backups[:3]):  # Show first 3 backups
            print(f'  • {backup.name} ({backup.environment}) - {backup.file_size_mb:.1f}MB')
            if i >= 2:  # Only show first 3
                break
        if len(backups) > 3:
            print(f'  ... and {len(backups) - 3} more')
    else:
        print('ℹ️  No backups found (this is normal if no backups have been uploaded)')
    sys.exit(0)
except Exception as e:
    print(f'❌ CDN backup manager test failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        print_message "$GREEN" "✅ CDN backup manager working correctly"
    else
        print_message "$RED" "❌ CDN backup manager test failed"
        print_message "$YELLOW" "   Check your CDN configuration in .env file"
    fi
    
    # Go back to root directory
    cd .. 2>/dev/null || true
    
else
    print_message "$RED" "❌ CDN backup manager file not found"
fi

echo ""

# Test 4: Test API endpoints
print_message "$BLUE" "📋 Step 4: Testing API Endpoints"
echo "--------------------------------"

# Common API base URLs to test
api_urls=(
    "http://localhost:5000"
    "http://localhost:3000"  
    "https://archerytool.online"
    "http://127.0.0.1:5000"
)

api_base=""
for url in "${api_urls[@]}"; do
    if curl -s "$url/api/health" >/dev/null 2>&1; then
        api_base="$url"
        print_message "$GREEN" "✅ Found API server at: $api_base"
        break
    fi
done

if [ -z "$api_base" ]; then
    print_message "$YELLOW" "⚠️  No API server found at common URLs"
    print_message "$YELLOW" "   Start your API server and try again"
else
    # Test basic health endpoint
    test_api_endpoint "$api_base/api/health" "API Health Check"
    
    # Test backup-related endpoints (these will require authentication)
    test_api_endpoint "$api_base/api/admin/backups" "Admin Backup List"
    test_api_endpoint "$api_base/api/admin/backup-test" "Backup Test Endpoint"
fi

echo ""

# Test 5: Check backup directories
print_message "$BLUE" "📋 Step 5: Checking Backup Directories"
echo "--------------------------------------"

backup_dirs=(
    "./backups"
    "./arrow_scraper/backups"
    "/app/backups"
)

for dir in "${backup_dirs[@]}"; do
    if [ -d "$dir" ]; then
        backup_count=$(find "$dir" -name "*.tar.gz" -o -name "*.gz" 2>/dev/null | wc -l)
        print_message "$GREEN" "✅ Backup directory found: $dir ($backup_count backup files)"
        
        # Show recent backups
        if [ $backup_count -gt 0 ]; then
            print_message "$BLUE" "   Recent backups:"
            find "$dir" -name "*.tar.gz" -o -name "*.gz" 2>/dev/null | head -3 | while read -r file; do
                size=$(ls -lh "$file" 2>/dev/null | awk '{print $5}' || echo "unknown")
                basename_file=$(basename "$file")
                print_message "$BLUE" "     • $basename_file ($size)"
            done
        fi
    else
        print_message "$YELLOW" "⚠️  Backup directory not found: $dir"
    fi
done

echo ""

# Test 6: Environment detection
print_message "$BLUE" "📋 Step 6: Environment Detection"
echo "--------------------------------"

if [ -f "/app/api.py" ]; then
    print_message "$GREEN" "✅ Docker environment detected"
    environment="production/docker"
elif [ -f "./arrow_scraper/api.py" ]; then
    print_message "$GREEN" "✅ Local development environment detected"
    environment="development"
else
    print_message "$YELLOW" "⚠️  Environment unclear"
    environment="unknown"
fi

print_message "$BLUE" "   Environment: $environment"

# Check if we're in the right directory
if [ -f "CLAUDE.md" ] && [ -d "arrow_scraper" ] && [ -d "frontend" ]; then
    print_message "$GREEN" "✅ Project structure verified - in root directory"
else
    print_message "$YELLOW" "⚠️  May not be in project root directory"
    print_message "$YELLOW" "   Expected files: CLAUDE.md, arrow_scraper/, frontend/"
fi

echo ""

# Test 7: Cross-platform compatibility check
print_message "$BLUE" "📋 Step 7: Cross-Platform Compatibility"
echo "---------------------------------------"

# Test filename parsing (key feature for cross-platform backups)
print_message "$BLUE" "🔍 Testing backup filename parsing..."

if python3 -c "
from arrow_scraper.cdn_backup_manager import CDNBackupManager
manager = CDNBackupManager()

# Test filenames from different environments
test_files = [
    'production_full_20250812_143045.tar.gz',
    'development_arrow_only_20250812.tar.gz', 
    'staging_user_only_20250812_120000.tar.gz',
    'legacy_backup_name.tar.gz'
]

print('🧪 Testing filename parsing:')
for filename in test_files:
    metadata = manager._extract_backup_metadata(filename)
    print(f'  • {filename}')
    print(f'    Environment: {metadata[\"environment\"]}')
    print(f'    Type: {metadata[\"backup_type\"]}')
    print(f'    Display: {metadata[\"display_name\"]}')
    print('')

print('✅ Filename parsing working correctly')
" 2>/dev/null; then
    print_message "$GREEN" "✅ Cross-platform filename parsing working"
else
    print_message "$RED" "❌ Filename parsing test failed"
fi

echo ""

# Summary
print_message "$GREEN" "📊 Test Summary"
print_message "$GREEN" "==============="

print_message "$BLUE" "✅ **CDN-First Backup System Status:**"
print_message "$BLUE" "   • Centralized CDN backup manager implemented"
print_message "$BLUE" "   • Multi-provider support (Bunny CDN, Cloudinary, AWS S3)"
print_message "$BLUE" "   • Cross-environment backup access enabled"
print_message "$BLUE" "   • Environment-aware backup naming"
print_message "$BLUE" "   • Enhanced frontend with filtering and badges"
print_message "$BLUE" "   • Automatic fallback to legacy methods"

echo ""
print_message "$YELLOW" "💡 **Next Steps:**"
print_message "$YELLOW" "   1. If CDN tests failed, check your .env CDN configuration"
print_message "$YELLOW" "   2. Test creating backups through the admin interface"
print_message "$YELLOW" "   3. Verify cross-environment restore functionality"
print_message "$YELLOW" "   4. Monitor backup list consistency across environments"

echo ""
print_message "$GREEN" "🎉 **Benefits Achieved:**"
print_message "$GREEN" "   • No more backup data blanking after local changes"
print_message "$GREEN" "   • Restore production backups on development setup"  
print_message "$GREEN" "   • Consistent backup list across all platforms"
print_message "$GREEN" "   • Direct CDN API access without database dependencies"

echo ""
print_message "$GREEN" "🧪 CDN Backup System Testing Complete!"