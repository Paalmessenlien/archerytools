# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Archery Tools project that scrapes arrow specifications from manufacturer websites and provides professional tuning calculations for archery equipment. The project has completed all development phases (1-9) and is **READY FOR BETA TESTING** with a production-ready full-stack archery tools platform featuring modern UI/UX.

**📚 COMPREHENSIVE DOCUMENTATION AVAILABLE:**
- **[Complete Documentation Index](docs/INDEX.md)** - Overview of all documentation
- **[Database Schema Documentation](docs/DATABASE_SCHEMA.md)** - Complete database structure, tables, relationships
- **[API Endpoints Documentation](docs/API_ENDPOINTS.md)** - All REST endpoints with request/response examples  
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)** - Architecture, workflows, and troubleshooting
- **[Spine Data System Documentation](docs/SPINE_DATA_SYSTEM.md)** - Advanced spine calculation system and admin interface
- **[Spine Chart Management Documentation](docs/SPINE_CHART_MANAGEMENT.md)** - Professional spine chart management with editing capabilities

**🚀 For new developers**: Start with [Development Guide](docs/DEVELOPMENT_GUIDE.md) for environment setup and architecture overview.

**Technology Stack:**
- **Web Scraping**: Crawl4AI + DeepSeek API for intelligent content extraction
- **Database**: SQLite with comprehensive arrow specifications and relationships  
- **Backend**: Flask (Python) API-only server with RESTful endpoints
- **Frontend**: Nuxt 3 (Vue.js) + Tailwind CSS + TypeScript + Pinia state management
- **UI Components**: Material Web Components with custom styling and dark mode support
- **Styling**: Tailwind CSS + Material Design 3 theming with comprehensive dark mode
- **Calculations**: Advanced spine calculation, tuning optimization, and arrow matching engines
- **Architecture**: Modern SPA frontend with API backend (dual deployment)

**Recent Major Updates (2025):**
- ✅ **CDN-First Backup System**: Cross-environment backup access with CDN storage, eliminating data blanking issues
- ✅ **Admin Backup/Restore System**: Complete database backup and restore functionality with CDN integration
- ✅ **Modern UI Overhaul**: Material Web Components integration with custom styling
- ✅ **Dark Mode System**: Complete dark/light theme support with user preference persistence
- ✅ **Enhanced UX**: Improved button styling, responsive layouts, and accessibility
- ✅ **Database Statistics**: Fixed manufacturer counting and database metrics display
- ✅ **Advanced Filtering**: Enhanced manufacturer filtering with diameter range dropdowns
- ✅ **SSR Optimization**: Resolved hydration issues and improved performance
- ✅ **Diameter Categories**: Professional arrow shaft diameter classification system
- ✅ **Arrow Type Filtering**: Added arrow type dropdown with sorting options
- ✅ **Production Ready**: Complete deployment scripts, Docker support, and documentation
- ✅ **Beta Release**: Comprehensive testing, documentation, and deployment preparation
- ✅ **Admin System**: Complete admin authentication with automatic privileges for messenlien@gmail.com
- ✅ **Frontend Fixes**: Resolved state management and string formatting errors across all components
- ✅ **User Management**: Full user profile editing, registration, and admin panel functionality
- ✅ **Enhanced Production Infrastructure**: Comprehensive Docker deployment with verification and health checks
- ✅ **Interactive Tuning Guides**: Complete guided tuning system with step-by-step walkthroughs
- ✅ **Bow Saving Fix**: Resolved production database persistence issues with enhanced infrastructure
- ✅ **Manufacturer Filter Fix**: Resolved 0% match score issue when filtering by specific manufacturers
- ✅ **Spine and Weight Display**: Fixed spine value and total arrow weight calculations in my setup page
- ✅ **UI Accessibility Enhancement**: Filters remain accessible when no recommendations are found
- ✅ **Calculator Navigation**: Added Calculator link to desktop and mobile navigation menus
- ✅ **GitHub Issue #16 Completion**: Complete bow configuration system fixes including 0.5 draw weight increments, point weight validation (40+ gn), arrow length fields, and enhanced form persistence
- ✅ **Rebranding**: Changed from "Arrow Tuning Platform" to "Archery Tools" throughout the system
- ✅ **Navigation Update**: Replaced "Bow Setup" with "Home" in navigation menu
- ✅ **API Authentication**: Added JWT token authentication to all API requests
- ✅ **Custom Length Fields**: Simplified bow setup form to use single field for custom lengths
- ✅ **Multiple Concurrent Tuning Sessions**: Complete support for running multiple tuning sessions simultaneously with pause/resume functionality
- ✅ **Enhanced Scraper Arguments**: Added `--learn`, `--learn-all`, `--limit`, and improved `--manufacturer` support for efficient pattern learning
- ✅ **Pattern Learning System**: Intelligent content extraction that learns from successful scraping to speed up future operations by 46%+
- ✅ **Enhanced JSON Export**: `--learn-all` now saves both pattern data and extracted arrow specifications to `data/processed/` for immediate use
- ✅ **JSON-Based Database Import System**: Automatic database import from JSON files during server startup with smart update detection
- ✅ **Traditional Wood Arrows Support**: Complete database support for traditional wooden arrow shafts including Cedar, Pine, Poplar, Birch, and Fir
- ✅ **German Decimal Conversion**: Automatic conversion of German decimal format (5,40 → 5.40) for European manufacturers
- ✅ **Admin Arrow Editing Fix**: Complete resolution of admin arrow save/update functionality with database schema migration and API enhancements
- ✅ **Advanced Admin Data Tools**: Batch fill missing data functionality and URL-based scraping integration for comprehensive arrow data management
- ✅ **Professional Spine Chart Management System**: Comprehensive manufacturer spine chart integration with editing capabilities, custom chart creation, and enhanced spine calculations using real manufacturer data (August 2025)

## Development Commands

### Python Environment Setup
```bash
# Install dependencies for arrow scraper
cd arrow_scraper
pip install -r requirements.txt

# Test setup
python test_setup.py
```

### Running the Dual Architecture Application

**Option 1: Enhanced Docker Deployment (Recommended)**

**Enhanced Production Deployment (With Comprehensive Verification):**
```bash
# Deploy enhanced production system with full verification
./deploy-enhanced.sh docker-compose.enhanced-ssl.yml

# Quick verification test
python3 test-bow-saving.py

# Enhanced deployment includes:
# - Database integrity verification
# - Build verification for frontend and API
# - Multi-stage health checks with extended timeouts
# - Comprehensive error handling and logging
# - User database persistence with Docker volumes
```

**Standard Deployment (Legacy):**
```bash
# Deploy with default configuration
./docker-deploy.sh

# Deploy with SSL for production
./docker-deploy.sh docker-compose.ssl.yml --build

# Deploy development version
./docker-deploy.sh docker-compose.dev.yml
```

**Manual Docker Commands:**
```bash
# Clean up orphan containers first (if needed)
./docker-cleanup.sh

# API-only testing
docker-compose -f docker-compose.simple.yml up -d --build

# Full development with hot reload (uses override file)
docker-compose up -d --build

# Production testing without domain
docker-compose -f docker-compose.prod.yml up -d --build
```

**For Production with Domain & HTTPS:**
```bash
# HTTP deployment (initial setup)
./deploy-production.sh

# HTTPS deployment (with SSL certificates)
sudo docker-compose -f docker-compose.ssl.yml up -d --build

# Fix mixed content if upgrading from HTTP to HTTPS
./fix-mixed-content.sh
```

**Access URLs:**
- **Development**: http://localhost:3000
- **Production HTTP**: http://yourdomain.com  
- **Production HTTPS**: https://yourdomain.com
- **API**: /api/health endpoint for health checks

**Option 2: Dual Architecture Startup**
```bash
# Start both Nuxt 3 frontend and Flask API backend
./scripts/start-dual-architecture.sh start

# Development mode
NODE_ENV=development ./scripts/start-dual-architecture.sh start

# Frontend: http://localhost:3000
# API Backend: http://localhost:5000
```

**Option 3: Manual Development**
```bash
# Start Flask API Backend
cd arrow_scraper
python api.py

# Start Nuxt 3 Frontend (separate terminal)
cd frontend
npm run dev
```

**Legacy Flask Web Application (deprecated)**
```bash
# Start the original Flask web server (server-side rendered)
cd arrow_scraper
python webapp.py
# Server runs on http://localhost:5000
```

### Running the Scraper

**🏹 Arrow Scraper Operations**

**Enhanced Scraper Usage (2025 Update):**
```bash
# Navigate to scraper directory
cd arrow_scraper

# Activate virtual environment (recommended)
source venv/bin/activate

# 🧠 PATTERN LEARNING MODE - Learn from limited URLs for faster future scraping (NO API calls)
python main.py --learn-all --limit=1                     # Learn from first URL of ALL manufacturers
python main.py --learn-all --limit=2                     # Learn from first 2 URLs of each manufacturer
python main.py --learn --manufacturer=easton --limit=1    # Learn from first URL only
python main.py --learn --manufacturer=easton --limit=3    # Learn from first 3 URLs
python main.py --learn --manufacturer=goldtip --limit=5   # Learn from first 5 Gold Tip URLs

# 🤖 PATTERN LEARNING WITH DATA EXTRACTION - Using DeepSeek API for actual arrow data
python main.py --learn --manufacturer=aurel --limit=1 --use-deepseek     # Extract from first Aurel URL
python main.py --learn-all --limit=1 --use-deepseek                     # Extract from first URL of ALL manufacturers

# 🎯 LIMITED PROCESSING - Process specific number of URLs with data extraction
python main.py --manufacturer=easton --limit=10 --use-deepseek          # Process first 10 Easton URLs
python main.py easton --limit=2 --use-deepseek                         # Backward compatible syntax

# 🚀 FULL MANUFACTURER SCRAPING with data extraction
python main.py easton --use-deepseek                                    # All Easton URLs with API extraction
python main.py --manufacturer=goldtip --use-deepseek                   # All Gold Tip URLs with API extraction

# 🌍 ALL MANUFACTURERS WITH TRANSLATION (RECOMMENDED) - Full data extraction
python main.py --update-all --use-deepseek                             # Update all with API extraction
python main.py --update-all --no-translate --use-deepseek              # Without translation (faster)
python main.py --update-all --force --use-deepseek                     # Force complete rebuild of ALL

# 📋 INFORMATION COMMANDS
python main.py --list-manufacturers                     # List all 13+ manufacturers

# Deactivate virtual environment when done
deactivate
```

**Environment Setup:**
```bash
# Set up API key (required for scraping)
echo "DEEPSEEK_API_KEY=your_deepseek_api_key_here" > .env

# Install/update dependencies in virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Available Manufacturers:**
- **Primary (English)**: Easton, Gold Tip, Victory, Carbon Express
- **European (German)**: Nijora, DK Bow, Aurel 
- **European (Italian)**: BigArchery/Cross-X  
- **International**: Fivics, Pandarus, Skylon
- **Traditional**: Traditional Wood Arrows (Cedar, Pine, Poplar, Birch, Fir, Sitka Spruce)

### 🌍 Automatic Translation System

**DeepSeek Translation Features:**
- **Smart Language Detection**: Automatically detects German, Italian, French, and Spanish content
- **Technical Preservation**: Maintains spine numbers, diameters, weights, and brand names unchanged
- **Cascading Fallback**: Falls back to original text if translation fails
- **Translation Metadata**: Tracks confidence scores and original text for reference

**Supported Languages:**
- 🇩🇪 **German**: Nijora, DK Bow, Aurel manufacturers
- 🇮🇹 **Italian**: BigArchery/Cross-X manufacturers  
- 🇫🇷 **French**: Future manufacturer support
- 🇪🇸 **Spanish**: Future manufacturer support

**Translation Testing:**
```bash
# Test translation functionality
cd arrow_scraper
python test_translation.py
```

**Translation Workflow:**
1. 🌐 **Language Detection**: Analyzes content for language-specific indicators
2. 🔤 **Content Translation**: Uses DeepSeek API with archery-specialized prompts
3. 🔧 **Technical Preservation**: Maintains specifications, measurements, and product names
4. 💾 **Dual Storage**: Stores both original and translated content
5. 📊 **Metadata Tracking**: Records translation confidence and source language

**Complete Database Update Workflow with Translation:**
```bash
# 1. Update ALL manufacturers with automatic translation (RECOMMENDED)
cd arrow_scraper
source venv/bin/activate
python main.py --update-all

# 2. Check scraped and translated data
ls -la data/processed/

# 3. Verify the update with language info
python show_available_data.py

# 4. Test specific translation results
python test_translation.py

# 5. Deploy to production (if satisfied)
git add . && git commit -m "Update arrow database with latest scraped and translated data"
git push
# On production: git pull && sudo docker-compose -f docker-compose.ssl.yml up -d --build

# Alternative: Update without translation (faster)
python main.py --update-all --no-translate
```

**Virtual Environment Options:**
```bash
# Option 1: With venv (recommended) - already set up
cd arrow_scraper
source venv/bin/activate
python main.py easton

# Option 2: Without venv (system Python)
cd arrow_scraper
python main.py easton

# Option 3: Docker environment (production-like)
docker build -t arrow-scraper ./arrow_scraper
docker run -e DEEPSEEK_API_KEY=your_key arrow-scraper python main.py easton
```

**Scraper Output Structure:**
```
arrow_scraper/
├── data/
│   ├── raw/              # Raw scraped HTML/content
│   └── processed/        # Clean JSON arrow data
│       ├── easton_arrows.json
│       ├── goldtip_arrows.json
│       └── victory_arrows.json
├── arrow_database.db     # SQLite database
└── logs/                 # Scraping logs
```

**Important Notes:**
- Scraper includes respectful delays between requests
- Requires DeepSeek API key for intelligent content extraction
- Large scraping operations may take 30+ minutes
- Always verify scraped data before production deployment

### Database Management

**🔄 JSON-Based Database Import System (2025 Update):**
```bash
# Automatic import during server startup (via start-api-robust.sh)
# JSON files serve as authoritative data source with smart update detection

# Manual database import operations
cd arrow_scraper

# Check if database needs updating from JSON files
python database_import_manager.py --check

# Force import all JSON files to database
python database_import_manager.py --import-all --force

# Standard database operations
python arrow_database.py                    # Initialize or rebuild database
python show_available_data.py               # Show database statistics
python migrate_diameter_categories.py       # Migrate to include diameter categories
```

**Database Import Features:**
- **Automatic Import**: Runs during server startup via `start-api-robust.sh`
- **JSON-First Architecture**: JSON files in `data/processed/` are the authoritative data source
- **Smart Updates**: Only imports when JSON files are newer than database
- **Manufacturer-Level Replacement**: Updates data per manufacturer, preserving other data
- **Traditional Wood Arrows**: Full support for traditional wooden arrow shafts
- **Error Handling**: Continues processing if individual manufacturers fail
- **Production Ready**: No server-side scraping needed in production environments

### CDN Image Management
```bash
# Bunny CDN setup and testing (Recommended)
cd arrow_scraper
python bunny_cdn_setup.py          # Show setup guide
python bunny_cdn_setup.py test     # Test configuration
python bunny_cdn_setup.py migrate  # Migrate existing images
python bunny_cdn_setup.py optimize # Show optimization tips

# General CDN integration
python cdn_integration_example.py test     # Test any CDN
python cdn_integration_example.py migrate  # Migrate existing data
python cdn_integration_example.py setup    # Show setup guide
python cdn_uploader.py                     # Test uploader directly
```

### Database Backup & Restore System

**🌐 CDN-First Backup System (2025 Update):**

**New CDN-First Architecture:**
- **Cross-Environment Access**: All environments (production, development, staging) access the same CDN backup repository
- **No More Data Blanking**: Backups persist independently of local database changes
- **Environment-Aware Naming**: Structured backup filenames with environment and type information
- **Multi-Provider Support**: Bunny CDN, Cloudinary, AWS S3 with automatic fallback

**Admin Panel Backup Management (Recommended):**
```bash
# Use the enhanced admin panel at /admin for backup operations:
# - Visual backup creation with environment tagging
# - Cross-platform backup listing with filtering
# - Environment badges (Production/Development/Staging)
# - Backup type indicators (Full/Arrow-only/User-only)
# - CDN provider integration with download/restore
```

**Testing CDN Backup System:**
```bash
# Test the CDN backup system functionality
./test-cdn-backups.sh

# This will verify:
# - CDN provider configuration (Bunny CDN, Cloudinary, AWS S3)
# - Cross-platform backup compatibility
# - Environment-aware filename parsing
# - API endpoint connectivity
# - Multi-provider fallback system
```

**Legacy Backup Management (Command Line):**
```bash
# Create full backup with auto-generated name
./backup-databases.sh

# Create backup with custom name
./backup-databases.sh --name production_backup_2025_08_04

# Create user database only backup
./backup-databases.sh --user-db-only

# Create backup with cleanup (keep 5 most recent)
./backup-databases.sh --cleanup --keep 5

# List available backups
./restore-databases.sh --list

# Restore from backup (with confirmation)
./restore-databases.sh --file backup.tar.gz

# Restore user database only
./restore-databases.sh --file backup.tar.gz --user-db-only

# Verify backup integrity
./restore-databases.sh --verify --file backup.tar.gz

# Force restore without confirmation
./restore-databases.sh --file backup.tar.gz --force
```

**Direct Backup Manager Usage:**
```bash
# Inside Docker container
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py backup --name test_backup
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py list
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py restore backup.tar.gz
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py cleanup --keep 10
```

**CDN Backup System Features:**
- **Environment Detection**: Automatically tags backups with environment (production/development/staging)
- **Structured Naming**: Uses format `{environment}_{type}_{timestamp}.tar.gz`
- **Smart Metadata Parsing**: Extracts environment and backup type from filenames
- **Cross-Platform Restore**: Restore production backups on development environments
- **Enhanced Admin UI**: Visual environment badges and filtering capabilities
- **Multi-Provider Support**: Configurable CDN providers with automatic failover

### Arrow Tuning System
```bash
# Interactive tuning calculator
cd arrow_scraper
python tuning_calculator.py

# Arrow matching engine
python arrow_matching_engine.py

# Complete tuning system
python arrow_tuning_system.py
```

### Multiple Concurrent Tuning Sessions

**🎯 Advanced Session Management (2025 Update):**

The tuning system now supports multiple concurrent sessions with full pause/resume functionality:

**Key Features:**
- **Multiple Active Sessions**: Run several tuning guides simultaneously with different bow setups
- **Session Pause/Resume**: Pause any active session and resume later with full state preservation
- **Visual Progress Tracking**: Each session displays current step and completion percentage
- **Organized Session History**: Sessions organized by status (active, paused, completed)
- **Enhanced UX**: Intuitive session management with resume buttons and status indicators

**API Endpoints:**
```bash
# Session Management
POST /api/guide-sessions                    # Start new session
POST /api/guide-sessions/<id>/pause         # Pause active session
POST /api/guide-sessions/<id>/resume        # Resume paused session
POST /api/guide-sessions/<id>/complete      # Complete session
GET  /api/guide-sessions                    # Get all user sessions
GET  /api/guide-sessions/<id>               # Get session details
```

**User Workflow:**
1. **Start Multiple Sessions**: Create tuning sessions for different bow setups
2. **Switch Between Sessions**: Use resume buttons to switch between active sessions
3. **Pause/Resume**: Pause sessions to work on others, resume anytime
4. **Track Progress**: Visual indicators show completion status for each session
5. **Manage History**: View all sessions organized by status with action buttons

**Frontend Implementation** (`/frontend/pages/tuning.vue`):
- Enhanced session state management with array-based `activeSessions`
- Visual session cards with progress indicators and resume buttons
- Organized session history with status-based filtering
- Real-time session updates and state synchronization

### Frontend Development & Testing
```bash
# Install frontend dependencies
cd frontend
npm install

# Development server (with hot reload)
npm run dev
# Frontend: http://localhost:3000

# Build for production
npm run build

# Preview production build
npm run preview

# Lint and format code
npm run lint
npm run format

# Type checking
npm run typecheck
```

### Backend Testing
```bash
# Arrow scraper tests
cd arrow_scraper
python test_setup.py
python test_basic.py
python test_deepseek.py

# API testing
python test_api.py
python test_recommendations_api.py

# Admin system testing
python test_admin_api.py
python test_admin_with_auth.py

# Diameter categories testing
python test_diameter_categories.py

# Crawl4AI tests (comprehensive test suite)
cd crawl4ai
python -m pytest tests/
```

### Admin System Management
```bash
# Admin system is automatically configured via authentication flow
# messenlien@gmail.com receives automatic admin privileges on login

# Admin API endpoints (require authentication):
# GET /api/admin/check - Check current user admin status
# GET /api/admin/users - List all users (admin only)
# PUT /api/admin/users/<id>/admin - Set user admin status (admin only)

# Admin Backup/Restore System:
# GET /api/admin/backup-test - Test backup system accessibility
# GET /api/admin/backups - List all available backups
# POST /api/admin/backup - Create new backup and upload to CDN
# POST /api/admin/backup/<id>/restore - Restore database from backup
# GET /api/admin/backup/<id>/download - Get backup download info
# DELETE /api/admin/backup/<id> - Delete backup

# Admin Data Tools:
# POST /api/admin/batch-fill/preview - Preview batch fill missing data operations
# POST /api/admin/batch-fill/execute - Execute batch fill to propagate data across manufacturer arrows
# GET /api/admin/manufacturers/<manufacturer>/length-stats - Get manufacturer length statistics
# POST /api/admin/scrape-url - Scrape arrow data from specific URLs and update database

# Frontend admin panel:
# Access: /admin (requires admin authentication)
# Features: User management, backup/restore, admin privilege assignment, batch data tools, URL scraping

# Test admin access (after authentication):
cd arrow_scraper
python test_admin_api.py

# Test backup system:
curl http://localhost:5000/api/admin/backup-test
```

### Production Deployment (PRODUCTION READY)

**📚 Complete Documentation:**
- **Development Guide**: See [docs/DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md) for comprehensive deployment instructions, Docker setup, and production server configuration
- **Database Documentation**: See [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for complete database structure and relationships
- **API Documentation**: See [docs/API_ENDPOINTS.md](docs/API_ENDPOINTS.md) for all REST endpoints with examples

**Standard Production Deployment (Legacy)**
```bash
# Step 1: Clone and configure
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Step 2: Configure environment
cp .env.example .env
# Edit .env with your settings

# Step 3: Deploy with standard Docker configuration
./deploy-production.sh

# Note: This method is legacy. Use ./start-unified.sh production for new deployments

# Access URLs after deployment:
# - Frontend: http://localhost:3000
# - API: http://localhost:5000/api/health
# - Nginx: http://localhost
```

**Enhanced Production Deployment (Legacy - SSL + Domain)**
```bash
# Step 1: Clone and configure
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Step 2: Configure environment
cp .env.example .env
# Edit .env with your settings

# Step 3: Deploy with enhanced Docker configuration
./deploy-enhanced.sh docker-compose.enhanced-ssl.yml

# Step 4: Configure DNS (add A record: yourdomain.com -> your-server-ip)

# Step 5: Set up SSL certificates
sudo certbot certonly --standalone -d yourdomain.com

# Step 6: Production deployment with HTTPS
sudo docker-compose -f docker-compose.enhanced-ssl.yml up -d --build

# Note: This method is legacy. Use ./start-unified.sh ssl yourdomain.com for new deployments
```

**Production Features:**
- ✅ Enhanced Docker infrastructure with verification and health checks
- ✅ Import-only data system (NO server-side web scraping)
- ✅ Unified database architecture (arrow_database.db + user_data.db)
- ✅ Nginx reverse proxy with SSL termination and security headers
- ✅ Automatic HTTP to HTTPS redirects with rate limiting
- ✅ Docker containerization with extended health checks and resource limits
- ✅ Persistent user database with Docker volumes
- ✅ Material Design 3 UI with dark mode support
- ✅ Professional arrow tuning calculations and recommendations
- ✅ Component integration (inserts, nocks, points) in unified database
- ✅ Comprehensive backup and monitoring systems

**Unified Production Deployment (Recommended - SSL + Domain)**
```bash
# Step 1: Clone and configure
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Step 2: Configure environment
cp .env.example .env
# Edit .env with your settings

# Step 3: Deploy with unified startup script for SSL production
./start-unified.sh ssl yourdomain.com

# The script will:
# - Check prerequisites and SSL certificates
# - Set up production environment variables
# - Import arrow data automatically on first startup
# - Start services with nginx reverse proxy and backup system
# - Display access URLs and status information

# Access your deployment:
# Frontend: https://yourdomain.com
# API: https://yourdomain.com/api
```

**Key Deployment Scripts:**
- `start-unified.sh` - **RECOMMENDED** Unified startup script for all deployment modes (development, production, SSL) with automatic data import
- `production-import-only.sh` - Manual arrow data import from JSON files (rarely needed)
- `deploy-production.sh` - Legacy standard Docker deployment with Nginx reverse proxy
- `deploy-enhanced.sh` - Legacy enhanced production deployment with verification
- `docker-production-setup.sh` - Legacy automated Docker setup with health checks
- `test-bow-saving.py` - Production functionality testing utility

**⚠️ Important: Production systems only import existing JSON data files and do NOT perform web scraping on the server.**

### Deploying Updates to Production

**🚀 Quick Production Update (Latest Changes)**
```bash
# On your production server
cd /path/to/your/archerytools/project

# Pull latest changes
git pull

# Restart with unified script (recommended)
./start-unified.sh ssl yourdomain.com

# Alternative: Legacy Docker Compose method
# sudo docker-compose -f docker-compose.enhanced-ssl.yml down
# sudo docker-compose -f docker-compose.enhanced-ssl.yml up -d --build

# Verify deployment
curl https://yourdomain.com/api/health
python3 test-bow-saving.py
```

**🏹 Deploying Fresh Arrow Data**
```bash
# Method 1: Local development then production deploy (RECOMMENDED)
# 1. Run scraper locally to update JSON files
cd arrow_scraper
source venv/bin/activate
python main.py easton goldtip victory  # Updates data/processed/*.json files
# DO NOT run python arrow_database.py locally

# 2. Commit and push JSON changes
git add data/processed/
git commit -m "Update arrow database JSON files with latest scraped data"
git push

# 3. Deploy to production (automatic JSON import on startup)
# On production server:
git pull
./start-unified.sh ssl yourdomain.com  # Imports JSON data automatically

# Alternative legacy method:
# sudo docker-compose -f docker-compose.enhanced-ssl.yml up -d --build
```

**⚠️ Critical Production Deployment Notes:**
- **NO Server Scraping**: Production servers NEVER perform web scraping
- **JSON Import Only**: Production only imports from existing JSON files in data/processed/
- **Local Development**: All scraping is done in development environments only
- **Database Persistence**: User database persists through container rebuilds using Docker volumes
- **Unified Deployment**: Use `start-unified.sh ssl yourdomain.com` for production SSL deployment
- **Backup Recommended**: Automated backup system included with `--profile with-backup`
- **Verification**: Use `test-bow-saving.py` to verify production functionality
- **Health Checks**: Extended health monitoring with 120s startup periods

### Production Compatibility Verification

**Admin Backup System Compatibility (August 2025):**
The recent admin backup system fixes are fully compatible with production deployments using `start-unified.sh ssl archerytool.online`:

✅ **API Endpoint Compatibility**: All 7 new backup endpoints handle both string and integer backup IDs:
- `/api/admin/backup/<backup_id>/restore` - Works with `local_*`, `cdn_*`, and integer IDs
- `/api/admin/backup/<backup_id>/download` - Supports all backup sources (local, CDN, database)
- `/api/admin/backup/download-file` - Secure file serving with authentication

✅ **Frontend State Management**: Vue.js conditional rendering fixes prevent UI race conditions across all deployment environments

✅ **Database Persistence**: Enhanced Docker volumes ensure backup metadata persists through container restarts

✅ **SSL Environment**: All backup operations work correctly with HTTPS-enabled production deployments

✅ **Authentication Flow**: JWT token authentication works seamlessly with `GOOGLE_REDIRECT_URI=https://yourdomain.com`

**Environment Variable Compatibility:**
The unified startup script properly sets all required environment variables for production SSL mode:
```bash
export FLASK_ENV="production"
export NODE_ENV="production"
export SSL_ENABLED="true"
export NUXT_PUBLIC_API_BASE="https://yourdomain.com/api"
export GOOGLE_REDIRECT_URI="https://yourdomain.com"
```

**Database Path Resolution:**
Enhanced database classes correctly handle production Docker container paths in `/app/` directory while gracefully falling back to local development paths when needed.

**Backup System Production Features:**
- CDN integration (Bunny CDN, Cloudinary, AWS S3) works with production SSL certificates
- Local file downloads use secure authentication-protected endpoints
- Backup restoration supports both arrow and user database selective restore
- All backup operations logged and tracked in production environment

### Database Architecture

**Unified Database System with Comprehensive Persistence (2025 Update):**
- ✅ **Arrow Database** (`arrow_database.db`): Arrow specifications, spine data, components, and component categories
- ✅ **User Database** (`user_data.db`): User accounts, bow setups, guide sessions, and arrow assignments
- ✅ **Backup System**: Professional-grade backup and restore functionality
- ❌ **Legacy Removed**: `component_database.db` (merged into arrow_database.db)

**Key Features:**
- **Full Persistence**: Both databases persist across Docker container restarts using volumes
- **Environment Path Resolution**: Database classes prioritize environment variables for Docker deployment
- **Production Import Control**: Automatic imports disabled in production for security
- **Comprehensive Backup System**: SQLite backup API with compressed archives and metadata
- **Data Separation**: Arrow/component data separate from user data for clean management
- **Migration Support**: Automatic schema migrations for both databases
- **Component Integration**: Components (inserts, nocks, points) stored with arrows in unified database

**Production Database Architecture:**
```
Docker Volumes:
├── arrowtuner-arrowdata:/app/arrow_data/     # Arrow database persistence
├── arrowtuner-userdata:/app/user_data/      # User database persistence
└── arrowtuner-logs:/app/logs/               # Log persistence

Database Files:
├── /app/arrow_data/arrow_database.db        # Arrow specs, spine data, components
├── /app/user_data/user_data.db             # User accounts, bow setups
└── /app/backups/                           # Backup archive storage
    ├── production_backup.tar.gz
    └── daily_backup_20250804.tar.gz

Source Data:
└── data/processed/                         # Source JSON files for arrow data
    ├── easton_arrows.json
    ├── goldtip_arrows.json
    └── components/
        └── tophat_archery_components_*.json
```

**Database Persistence Documentation**: See [DATABASE_PERSISTENCE.md](DATABASE_PERSISTENCE.md) for complete persistence and backup system documentation.

### Environment Configuration
**Development:** Create `.env` file in `arrow_scraper/` directory:
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**Dual Architecture:** Create `.env` file in root directory:
```
# API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SECRET_KEY=your-secret-key-here-change-this
API_PORT=5000
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=https://yourdomain.com

# Frontend Configuration
FRONTEND_PORT=3000
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id-here
NODE_ENV=production
NUXT_PUBLIC_API_BASE=http://localhost:5000

# Production Domain
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

**Simplified Configuration:** All environment variables are now consolidated into the single root `.env` file, including:
- Google OAuth credentials
- CDN configuration (Bunny CDN, Cloudinary, AWS S3)
- API keys and secrets
- Development and production settings

No additional `.env` files are needed. The root `.env` file contains all necessary configuration.

**Legacy Production:** Edit `deploy/config/production.env`:
```
SECRET_KEY=your-secret-key-here-change-this
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

## Architecture Overview

### Project Structure
- `arrow_scraper/` - Complete arrow tuning platform (Python)
  - `api.py` - Flask API-only server with RESTful endpoints
  - `webapp.py` - Legacy server-side rendered Flask application (deprecated)
  - `Dockerfile.enhanced` - Enhanced production Dockerfile with verification
  - `start-api-robust.sh` - Robust startup script with database verification
  - `verify-databases.py` - Comprehensive database integrity checking
- `frontend/` - Modern Nuxt 3 SPA frontend application
  - `pages/` - Vue.js pages (index/bow-setup, database, arrow-details, tuning guides)
  - `components/` - Reusable Vue components with Material Web integration
    - `ArrowRecommendationsList.vue` - Advanced filtering and recommendation display
    - `DarkModeToggle.vue` - Theme switching component
    - `CustomButton.vue` - Fallback button component with Material Design styling
    - `GuideWalkthrough.vue` - Interactive tuning guide component
  - `composables/` - Vue 3 composition functions
    - `useApi.ts` - API communication layer
    - `useDarkMode.js` - Dark mode state management
    - `useMaterialWeb.ts` - Material Web component utilities
  - `stores/` - Pinia state management (bow configuration, user preferences)
  - `types/` - TypeScript type definitions for arrows and API responses
  - `plugins/` - Nuxt plugins for Material Web and button styling fixes
  - `assets/css/` - Tailwind CSS with Material Design 3 theming
  - `Dockerfile.enhanced` - Enhanced frontend Dockerfile with build verification
- `crawl4ai/` - Custom fork of Crawl4AI web crawling library
- `deploy/` - Legacy production deployment system
- `scripts/` - Dual architecture deployment scripts
- `deploy-enhanced.sh` - Comprehensive enhanced production deployment script
- `docker-compose.enhanced-ssl.yml` - Enhanced Docker Compose with verification
- `test-bow-saving.py` - Production bow saving functionality test utility
- `docs/` - Project documentation and phase plans
- `venv/` - Python virtual environment

### Production Deployment Structure
- `deploy/scripts/` - Deployment and maintenance scripts
  - `server-setup.sh` - Ubuntu server initialization and hardening
  - `deploy.sh` - Application deployment with zero-downtime
  - `health-check.sh` - System health monitoring and alerting
  - `backup.sh` - Automated database and application backups
  - `update.sh` - Application updates with rollback capability
  - `logs.sh` - Log management and analysis tools
  - `status.sh` - Comprehensive system status dashboard
- `deploy/config/` - Production configuration files
  - `production.env` - Environment variables for production
  - `production.py` - Flask production configuration with security hardening
- `deploy/nginx/` - Nginx reverse proxy configuration with SSL and security
- `deploy/systemd/` - Systemd service files for process management

### Modern Frontend Architecture (Nuxt 3 + Material Web)

**Core Pages & Routing:**
- `/` (index.vue) - Bow Setup & Configuration with interactive tuning wizard
- `/database` - Arrow Database with advanced search, filtering, and statistics
- `/arrows/[id]` - Individual arrow detail pages with specifications
- `/tuning` - Interactive tuning guide system with step-by-step walkthroughs
- `/guides/[slug]` - Individual tuning guides (sight setup, paper tuning, etc.)
- `/my-page` - User profile and bow setup management
- `/admin` - Admin panel for user management (admin users only)

**UI Component System:**
- **Material Web Components**: Google's official web components with Material Design 3
- **Custom Components**: Fallback components for enhanced compatibility
- **Dark Mode System**: Complete theme switching with user preference persistence
- **Responsive Design**: Mobile-first approach with Tailwind CSS

**State Management:**
- **Pinia Stores**: Reactive state management for bow configuration and user preferences
- **Composables**: Reusable logic for API calls, dark mode, and Material Web integration
- **Type Safety**: Full TypeScript support for enhanced developer experience

**Styling Architecture:**
- **Tailwind CSS**: Utility-first CSS framework with custom Material Design 3 theme
- **CSS Custom Properties**: Material Web component theming and dark mode variables
- **Component Scoped Styles**: Isolated styling for individual components
- **Responsive Breakpoints**: Mobile, tablet, and desktop optimized layouts

### Legacy Web Application Structure (Deprecated)
- `webapp.py` - Legacy Flask web application (server-side rendered)
- `templates/` - Jinja2 templates (replaced by Vue.js components)
- `static/` - Legacy web assets (replaced by modern build system)

### Key Backend Components

**Arrow Scraper System (`arrow_scraper/`):**
- `main.py` - Entry point for scraping operations
- `models.py` - Pydantic data models for arrow specifications and scraping results
- `scrapers/base_scraper.py` - Base scraper class with common functionality
- `scrapers/easton_scraper.py` - Manufacturer-specific scraper implementations
- `config/settings.py` - Configuration for manufacturers, URLs, and scraping parameters
- `config/manufacturers.yaml` - Comprehensive manufacturer configuration (13 manufacturers)
- `data/` - Output directory for scraped data (raw/ and processed/)

**Database & Calculation Engines:**
- `arrow_database.py` - SQLite database management with search and filtering
- `spine_calculator.py` - Professional spine calculation system
- `tuning_calculator.py` - Advanced tuning optimization with FOC and KE calculations
- `arrow_matching_engine.py` - Intelligent arrow recommendation system
- `arrow_tuning_system.py` - Complete tuning workflow with session management

**Data Models:**
- `ArrowSpecification` - Core arrow data model with validation
- `ScrapingResult` - Individual scrape operation results
- `ScrapingSession` - Complete scraping session tracking
- `ManufacturerData` - Container for all arrows from one manufacturer

**Manufacturer Configuration:**
The system supports 13 manufacturers with comprehensive URL patterns and scraping strategies:

**Primary Manufacturers:**
- Easton Archery (multiple product categories)
- Gold Tip (hunting and target arrows)
- Victory Archery (hunting and target arrows)
- Carbon Express (vision-based extraction)

**European Manufacturers:**
- Nijora Archery (German - extensive product line)
- DK Bow (German - traditional and modern arrows)
- Aurel Archery (German - precision arrows)
- BigArchery/Cross-X (Italian - competition arrows)

**International Manufacturers:**
- Fivics (Korean - Olympic-level target arrows)
- Pandarus Archery (precision target arrows)
- Skylon Archery (European target arrows)

**Additional Brands:**
- Plus 2 more manufacturers with defined extraction strategies

### System Workflows

**Data Collection Workflow:**
1. Load manufacturer configuration from `config/manufacturers.yaml`
2. Initialize scraper with DeepSeek API credentials
3. Use Crawl4AI to fetch web content (with image capture for vision-based extraction)
4. Apply LLM extraction strategy with structured JSON schema
5. Validate and process extracted data using Pydantic models
6. Save results to JSON files in `data/processed/`
7. Load processed data into SQLite database

**Arrow Tuning Workflow:**
1. Collect archer profile (bow specs, preferences, intended use)
2. Calculate optimal spine range using professional formulas
3. Search database for matching arrows with spine calculator integration
4. Score arrows based on multiple criteria (spine accuracy, availability, performance)
5. Generate detailed tuning recommendations with FOC optimization
6. Provide session tracking and comparison tools

### Data Schema

**Enhanced Arrow Specification Model:**
- Uses `SpineSpecification` objects for detailed spine-specific data
- Each arrow can have multiple spine options with unique diameters and GPI weights
- Comprehensive validation and relationship management

**Required fields:**
- manufacturer, model_name, spine_specifications (array of spine objects)
- Each spine specification includes: spine, outer_diameter, gpi_weight

**Optional fields:**
- length_options, material, carbon_content, arrow_type, recommended_use
- price_range, straightness_tolerance, weight_tolerance, description
- image URLs and local image paths for visual reference

## Project Phases

**Phase 1 (Complete):** Data Scraping & Collection
- ✅ Web scraping infrastructure with Crawl4AI
- ✅ DeepSeek API integration for intelligent data extraction
- ✅ JSON data storage and validation
- ✅ Support for 13 manufacturers with 400+ product images

**Phase 2 (Complete):** Database Design & Migration
- ✅ SQLite database with arrow and spine specification tables
- ✅ Comprehensive search and filtering capabilities
- ✅ Data migration from JSON extraction files
- ✅ Database statistics and reporting

**Phase 3 (Complete):** Web Application
- ✅ Flask web application with responsive design
- ✅ Arrow browsing, search, and detailed specification views
- ✅ Interactive tuning wizard with guided arrow selection
- ✅ API endpoints for AJAX functionality

**Phase 4 (Complete):** Arrow Tuning Calculator
- ✅ Professional spine calculation engine
- ✅ Advanced tuning optimization with FOC calculations
- ✅ Intelligent arrow matching and recommendation system
- ✅ Complete tuning workflow with session management

**Phase 5 (Complete):** System Integration & Testing
- ✅ Integrated platform combining all components
- ✅ Session tracking and report generation
- ✅ Comprehensive testing across multiple manufacturers
- ✅ Production-ready deployment capabilities

**Phase 6 (Complete):** Production Deployment System
- ✅ Enterprise-grade Ubuntu server deployment scripts
- ✅ Nginx reverse proxy with SSL termination and security hardening
- ✅ Automated backup system with restore capabilities
- ✅ Health monitoring and alerting system
- ✅ Log management and analysis tools
- ✅ Zero-downtime application updates with rollback
- ✅ System status dashboard and maintenance scripts
- ✅ Security features: UFW firewall, fail2ban, rate limiting

**Phase 7 (Complete - 2025):** Modern UI/UX Overhaul
- ✅ Nuxt 3 SPA frontend with Material Web Components
- ✅ Complete dark mode system with theme persistence
- ✅ Material Design 3 styling with custom Tailwind CSS integration
- ✅ Enhanced responsive design for all device types
- ✅ Advanced filtering system with diameter range dropdowns
- ✅ Fixed database statistics and manufacturer filtering
- ✅ SSR optimization and hydration issue resolution
- ✅ Comprehensive button styling fixes and fallback components
- ✅ Improved accessibility and keyboard navigation
- ✅ Custom button component system for enhanced compatibility

**Phase 8 (Complete - 2025):** Enhanced Diameter Classification System
- ✅ Professional arrow shaft diameter categorization system
- ✅ Seven standard diameter categories based on industry standards
- ✅ Automatic classification using inner diameter when available
- ✅ Database schema updates with migration scripts
- ✅ API endpoints enhanced with diameter category statistics
- ✅ Search and filtering by diameter categories
- ✅ Comprehensive testing suite for diameter classification
- ✅ Integration with existing arrow matching and recommendation systems

**Phase 9 (Complete - 2025):** Admin System & User Management
- ✅ Complete admin authentication system with automatic privilege assignment
- ✅ Automatic admin access for messenlien@gmail.com on first login
- ✅ Full admin API endpoints for user management and privilege control
- ✅ Admin panel frontend with user management interface
- ✅ User profile editing and registration system with persistent storage
- ✅ Google OAuth integration with secure JWT token authentication
- ✅ Bow setup management with user-specific configuration tracking
- ✅ Enhanced user database with admin functionality and relationship management

**Phase 10 (Complete - August 2025):** Enhanced Data Infrastructure & Traditional Arrow Support
- ✅ JSON-based database import system with automatic server startup integration
- ✅ Pattern learning system for 46%+ faster scraping operations
- ✅ Traditional wood arrow support (Cedar, Pine, Poplar, Birch, Fir, Sitka Spruce)
- ✅ German decimal conversion system for European manufacturers
- ✅ Enhanced scraper arguments with `--learn`, `--learn-all`, `--limit` support
- ✅ Smart update detection based on file timestamps
- ✅ Manufacturer-level data replacement strategy
- ✅ Production-ready import system with comprehensive error handling

**Phase 11 (Complete - August 2025):** CDN-First Backup System & Cross-Environment Access
- ✅ Centralized CDN backup manager with multi-provider support (Bunny CDN, Cloudinary, AWS S3)
- ✅ Cross-environment backup access eliminating local database dependency issues  
- ✅ Environment-aware backup naming with structured filenames (`production_full_20250812.tar.gz`)
- ✅ Enhanced admin UI with environment badges, backup type indicators, and smart filtering
- ✅ CDN-first backup listing with graceful fallback to legacy methods
- ✅ Intelligent backup metadata extraction from filenames for cross-platform compatibility
- ✅ Comprehensive testing framework for CDN backup system validation
- ✅ Production-ready cross-platform restore functionality enabling development environment restoration from production backups

## Important Notes

### Current Platform Status (2025)
- **Production-Ready Platform:** Complete archery tools solution with modern UI/UX and admin system
- **Modern Architecture:** Nuxt 3 SPA frontend + Flask API backend with dual deployment
- **Material Design 3:** Professional UI with Google's latest design system and dark mode
- **Enhanced UX:** Improved accessibility, responsive design, and user interaction
- **Advanced Filtering:** Sophisticated search with manufacturer, spine, diameter, and weight filters
- **Database Statistics:** Real-time metrics showing 13 manufacturers with 197+ arrow models
- **Admin System:** Complete user management with automatic admin privileges for messenlien@gmail.com
- **User Authentication:** Google OAuth integration with secure JWT tokens and profile management
- **Enhanced Production Infrastructure:** Comprehensive Docker deployment with verification and health checks
- **Interactive Tuning System:** Complete guided tuning with step-by-step walkthroughs for all tuning aspects
- **Bow Saving Resolution:** Production database persistence issues resolved with enhanced infrastructure

### Technical Capabilities
- **Multi-language Support:** Handles English, German, and Italian manufacturer websites
- **Vision Integration:** Uses OCR and computer vision for complex product images
- **Professional Calculations:** Implements industry-standard spine and tuning formulas
- **Comprehensive Database:** Contains 400+ arrow specifications across 13 manufacturers
- **Session Management:** Persistent tuning sessions with detailed recommendations
- **Custom Crawl4AI:** Includes enhanced fork of Crawl4AI in the `crawl4ai/` directory
- **Respectful Scraping:** Follows ethical crawling practices with rate limiting
- **Data Quality:** Comprehensive validation ensures accuracy across manufacturers
- **CDN Integration:** Automatic image upload to Cloudinary, AWS S3, or other CDNs for optimized delivery

### Deployment & Operations
- **Dual Architecture:** Modern SPA frontend + API backend deployment options
- **Enhanced Production Infrastructure:** Comprehensive Docker deployment with verification pipeline
- **Legacy Support:** Original Flask web application still available (deprecated)
- **Production Deployment:** Enterprise-ready deployment system with automated setup and health checks
- **Security Hardening:** UFW firewall, fail2ban, SSL certificates, rate limiting
- **Monitoring & Maintenance:** Health checks, automated backups, log management
- **Docker Support:** Complete containerization with enhanced docker-compose configuration
- **Database Reliability:** Persistent user data with Docker volumes and integrity verification
- **Build Verification:** Frontend and API build integrity checking during deployment
- **Extended Health Checks:** Multi-stage health monitoring with 120s startup periods

### UI/UX Features (2025 Updates)
- **Dark Mode:** Complete theme system with user preference persistence
- **Material Web Components:** Google's official web components with custom styling
- **Responsive Design:** Optimized for mobile, tablet, and desktop experiences
- **Advanced Filtering:** Diameter range dropdowns and enhanced manufacturer filtering
- **SSR Optimization:** Resolved hydration issues for better performance
- **Accessibility:** Improved keyboard navigation and screen reader support

### Arrow Diameter Classification System (2025)
- **Professional Categories:** Seven industry-standard diameter classifications
  - **Ultra-thin (.166")**: High-end target arrows for reduced wind drift
  - **Thin (.204")**: Popular for 3D archery and target applications  
  - **Small hunting (.244")**: Good penetration for hunting applications
  - **Standard target (.246")**: Very common for both target and hunting
  - **Standard hunting (.300")**: Widely used standard hunting diameter
  - **Large hunting (.340")**: Larger hunting diameter applications
  - **Heavy hunting (.400"+)**: Heavy arrows for traditional bows
- **Smart Classification:** Uses inner diameter when available for accurate categorization
- **Database Integration:** All 1,143+ arrow specifications automatically categorized
- **API Support:** Category-based filtering and statistics through REST endpoints
- **Search Enhancement:** Filter arrows by specific diameter categories for precision matching

## Production Management Commands

### Service Management
```bash
# Check system status
./deploy/scripts/status.sh

# Health monitoring
./deploy/scripts/health-check.sh

# Log management
./deploy/scripts/logs.sh tail                 # Follow live logs
./deploy/scripts/logs.sh error               # Show recent errors

# Service control (choose one method)
sudo supervisorctl start/stop/restart arrowtuner
# OR
sudo systemctl start/stop/restart arrowtuner
```

### Backup & Recovery
```bash
# Create backup
./deploy/scripts/backup.sh

# List backups
./deploy/scripts/backup.sh list

# Restore from backup
./deploy/scripts/backup.sh restore /path/to/backup.tar.gz

# Verify backup integrity
./deploy/scripts/backup.sh verify /path/to/backup.tar.gz
```

### Application Updates
```bash
# Check for updates
./deploy/scripts/update.sh check

# Apply updates (with automatic backup)
./deploy/scripts/update.sh update

# Rollback to previous version
./deploy/scripts/update.sh rollback

# Show current version info
./deploy/scripts/update.sh version
```

## Current System Capabilities

The Archery Tools platform provides:
1. **Professional spine calculations** based on bow specifications and shooting style
2. **Intelligent arrow recommendations** with confidence scoring and alternatives  
3. **Advanced tuning optimization** including FOC, kinetic energy, and momentum calculations
4. **Comprehensive database search** with filtering by manufacturer, spine, diameter, and GPI
5. **Visual arrow comparison** with detailed specification analysis
6. **Multiple concurrent tuning sessions** with pause/resume functionality and progress tracking
7. **Advanced session management** for tuning progress and recommendation history
8. **Modern web interface** with Material Design 3 components and dark mode
9. **Responsive design** optimized for desktop, tablet, and mobile devices
10. **API endpoints** for integration with other archery tools
11. **Real-time database statistics** with manufacturer and arrow count metrics
12. **Complete admin system** with automatic privilege assignment and user management
13. **User authentication** with Google OAuth integration and profile management
14. **Bow setup management** with persistent storage and configuration tracking

## Troubleshooting & Development Notes

### Docker Issues

**Enhanced Production Infrastructure (2025):**
- **New Solution**: Use the enhanced deployment system for production reliability:
  ```bash
  # Deploy with comprehensive verification
  ./deploy-enhanced.sh docker-compose.enhanced-ssl.yml
  
  # Test bow saving functionality
  python3 test-bow-saving.py
  
  # Enhanced system includes:
  # - Database integrity verification at startup
  # - Multi-stage health checks with extended timeouts
  # - User database persistence with Docker volumes
  # - Build verification for both frontend and API
  # - Comprehensive error handling and logging
  ```

**Orphan Container Errors:**
- **Issue**: `ERROR: for arrowtuner-api 'ContainerConfig'` or needing `--remove-orphans` flag every time
- **Cause**: Multiple Docker Compose files creating conflicting container configurations
- **Solution**: Use the automated cleanup scripts:
  ```bash
  # Enhanced deployment (automatically handles cleanup)
  ./deploy-enhanced.sh docker-compose.enhanced-ssl.yml
  
  # Legacy cleanup if needed
  ./docker-cleanup.sh
  
  # Then deploy normally
  docker-compose up -d
  ```

**Container Permission Issues:**
- **Issue**: `permission denied while trying to connect to the Docker daemon socket`
- **Solution**: Add user to docker group or use sudo:
  ```bash
  # Add user to docker group (logout/login required)
  sudo usermod -aG docker $USER
  
  # Or use sudo for Docker commands
  sudo ./docker-cleanup.sh
  sudo ./docker-deploy.sh
  ```

**Container Restart Loops:**
- **Issue**: API container keeps restarting
- **Cause**: Missing environment variables or database connection issues
- **Solution**: Check logs and environment configuration:
  ```bash
  # Check container logs
  docker-compose logs api
  
  # Verify environment variables
  docker-compose config
  
  # Test API health endpoint
  curl http://localhost:5000/api/simple-health
  ```

### Recent Fixes & Enhancements (August 2025)

This section details recent fixes and improvements to common development and deployment issues.

**Admin Panel Display Race Condition Fix (August 2025):**
- **Issue**: Admin panel showing both admin content and "Access Denied" message simultaneously despite admin functionality working correctly
- **Root Cause**: Vue.js conditional rendering race condition where `isCheckingAdmin` would become false before `isAdmin` was properly set
- **Solution**: Updated conditional rendering logic in `/home/paal/archerytools/frontend/pages/admin.vue` to prevent race conditions:
  - Modified `checkAndLoadAdminData()` function to ensure proper state sequencing
  - Updated template conditions to be more explicit: `v-else-if="!isCheckingAdmin && isAdmin"` for admin content and `v-else-if="!isCheckingAdmin && !isAdmin"` for access denied
  - Enhanced state management to prevent simultaneous display of conflicting UI states
- **Files**: `frontend/pages/admin.vue`
- **Status**: ✅ **RESOLVED** - Admin panel now correctly shows only appropriate content based on user authentication status

**Admin Backup System Download Fix (August 2025):**
- **Issue**: "Error downloading backup: TypeError: NetworkError when attempting to fetch resource." when trying to download backups
- **Root Cause**: Frontend calling string backup ID endpoints (e.g., `/api/admin/backup/local_8ba17867/download`) but endpoints only supported integer IDs
- **Solution**: Added comprehensive backup download system:
  - New download endpoint `/api/admin/backup/<backup_id>/download` that handles string backup IDs (local_*, cdn_*, and legacy integer IDs)
  - New file serving endpoint `/api/admin/backup/download-file` for secure local file downloads with authentication checks
  - Updated frontend `downloadBackup` function to handle different response types (CDN URLs vs local file downloads)
  - Enhanced backup ID parsing and routing for backward compatibility
- **Files**: `arrow_scraper/api.py`, `frontend/pages/admin.vue`
- **Status**: ✅ **RESOLVED** - All backup download functionality now works correctly across all backup sources

**Admin Backup System Restore Fix (August 2025):**
- **Issue**: "Error restoring backup: TypeError: NetworkError when attempting to fetch resource." when trying to restore backups
- **Root Cause**: Frontend calling string backup ID endpoints (e.g., `/api/admin/backup/local_8ba17867/restore`) but endpoints only supported integer IDs
- **Solution**: Added new restore endpoint `/api/admin/backup/<backup_id>/restore` that handles string backup IDs and delegates to appropriate restore logic based on ID format
- **Files**: `arrow_scraper/api.py`
- **Status**: ✅ **RESOLVED** - Backup restoration now works correctly with all backup ID formats

**Admin Panel Restore Modal Button Fix (August 2025):**
- **Issue**: "the restore backup button is not clickable" - restore confirmation modal button was disabled despite user selecting restore options
- **Root Cause**: Backup objects lacked proper `include_arrow_db` and `include_user_db` properties, causing both checkboxes to be unchecked and triggering the disabled condition `(!restoreForm.restoreArrowDb && !restoreForm.restoreUserDb)`
- **Solution**: Implemented intelligent backup detection in `showRestoreModal` function:
  ```javascript
  const hasArrowDb = backup.include_arrow_db || backup.includes?.arrow_database || 
                     backup.arrow_db_stats || backup.backup_name?.includes('arrows') ||
                     !backup.backup_name?.includes('users')
  const hasUserDb = backup.include_user_db || backup.includes?.user_database || 
                    backup.user_db_stats || backup.backup_name?.includes('users')
  ```
  - Enhanced backup metadata normalization across different sources (local files, CDN, database metadata)
  - Ensured at least one restore option is selected by default based on backup content detection
- **Files**: `frontend/pages/admin.vue`
- **Status**: ✅ **RESOLVED** - Restore modal buttons now function correctly with proper content detection

**Admin Backup/Restore System Implementation (August 2025):**
- **Feature**: Complete admin backup and restore system with CDN integration
- **Implementation**: 
  - 7 new authenticated API endpoints for backup operations (`/api/admin/backup*`)
  - Database schema enhancements with backup metadata and operations tracking
  - CDN integration supporting Bunny CDN, Cloudinary, AWS S3, and local storage
  - Admin panel UI components for intuitive backup management
- **Critical Bug Fix**: Flask routing issue resolved by moving backup endpoints to proper location in `api.py`
- **Files**: `arrow_scraper/api.py`, `arrow_scraper/user_database.py`, `frontend/pages/admin.vue`
- **Status**: ✅ **PRODUCTION READY** - Complete backup/restore functionality available in admin panel

**Admin Arrow Editing 500 Internal Server Error Fix (August 2025):**
- **Issue**: Admin arrow editing failing with 500 Internal Server Error when trying to save material changes (e.g., "Carbon" → "Carbon / Aluminum")
- **Root Cause**: Two critical issues:
  1. Database schema mismatch - API trying to update non-existent columns (`recommended_use`, `straightness_tolerance`, `weight_tolerance`)
  2. Field name mismatch - Frontend sends `primary_image_url`, backend expects `image_url`
- **Solution**: 
  - Fixed `allowed_fields` in admin API to only include columns that exist in arrows table
  - Added `primary_image_url` → `image_url` field mapping for frontend compatibility
  - Removed database imports from Docker startup process (`start-api-robust.sh`) for faster container boot
  - Updated both `create_arrow_admin` and `update_arrow_admin` endpoints
- **Files**: `arrow_scraper/api.py`, `arrow_scraper/start-api-robust.sh`
- **Status**: ✅ **RESOLVED** - All admin arrow editing now works correctly, material changes save successfully

**Advanced Admin Data Tools Implementation (August 2025):**
- **Feature**: Complete admin data management system with batch fill and URL scraping capabilities
- **Implementation**: 
  - **Batch Fill System**: Propagates missing length data from complete reference arrows to other arrows from same manufacturer
    - Preview functionality shows exactly what data will be copied before execution
    - Manufacturer selection with automatic reference arrow detection
    - Smart matching based on existing complete arrow specifications
  - **URL Scraping Integration**: Extracts arrow specifications directly from manufacturer websites
    - Intelligent table extraction from HTML specification tables (e.g., Easton format)
    - Fallback text-based extraction for unstructured content
    - Updates existing arrows with missing spine specifications, GPI weights, and diameters
    - Successfully tested with Easton X10 Parallel Pro (added 13 new spine specs from website table)
- **API Endpoints**: 
  - `POST /api/admin/batch-fill/preview` - Preview batch operations
  - `POST /api/admin/batch-fill/execute` - Execute batch fill operations
  - `POST /api/admin/scrape-url` - Scrape specifications from manufacturer URLs
- **Frontend**: Complete "Data Tools" tab in admin panel with intuitive UI for both batch operations and URL scraping
- **Files**: `arrow_scraper/api.py`, `frontend/pages/admin.vue`
- **Status**: ✅ **PRODUCTION READY** - Comprehensive data management tools for maintaining and expanding arrow database

**Previous Admin Arrow Save/Update API Error Fix (August 2025):**
- **Issue**: Admin arrow editing functionality failing with API errors when trying to save or update arrows with spine specifications
- **Root Cause**: Database schema mismatch - `spine_specifications` table missing 7 columns that AdminArrowEditModal expected
- **Solution**: 
  - Created `migrate_spine_specifications.py` migration script to add missing columns (length_options, wall_thickness, insert_weight_range, nock_size, notes, straightness_tolerance, weight_tolerance)
  - Updated admin API functions (`create_arrow_admin` and `update_arrow_admin`) to use complete spine specifications schema
  - Enhanced SQL insert queries to handle all 14 columns in spine_specifications table
- **Files**: `arrow_scraper/migrate_spine_specifications.py`, `arrow_scraper/api.py`, `arrow_scraper/test_admin_arrow_save.py`
- **Status**: ✅ **RESOLVED** - Admin arrow creation and editing now works correctly with complete spine specification support

**Database Permission Errors Fix (August 2025):**
- **Issue**: Scraper failing with `[Errno 13] Permission denied: '/app'` when running locally, caused by database classes trying to access Docker container paths
- **Root Cause**: Database path resolution logic attempting to create directories in `/app` which requires root permissions in local development
- **Solution**: 
  - Enhanced `_resolve_db_path()` methods in both `ArrowDatabase` and `UserDatabase` classes
  - Added proper exception handling for `PermissionError` when accessing Docker paths
  - Graceful fallback to accessible local development paths (`arrow_scraper/` directory)
  - Fixed destructor safety in `ArrowDatabase.__del__()` to handle incomplete initialization
- **Files**: `arrow_scraper/arrow_database.py`, `arrow_scraper/user_database.py`
- **Testing**: Verified with `python main.py --manufacturer=aurel --limit=1 --use-deepseek`
- **Status**: ✅ **RESOLVED** - Scraper now works correctly in local development environments

**Manufacturer Filter Match Scoring Fix (August 2025):**
- **Issue**: Manufacturer dropdown filtering showing 0% match scores while "All Manufacturers" showed proper 90-95% scores
- **Root Cause**: Two different API flows - manufacturer filtering was using database API instead of tuning API
- **Solution**: 
  - Fixed manufacturer name mapping in arrow matching engine (Easton → Easton Archery)
  - Added `preferred_manufacturers` parameter to archer profile in API
  - Unified all filtering to use tuning API with proper bow configuration matching
  - Removed `loadArrowsFromManufacturer` function that was bypassing proper scoring
- **Files**: `arrow_scraper/arrow_matching_engine.py`, `arrow_scraper/api.py`, `frontend/components/ArrowRecommendationsList.vue`
- **Status**: ✅ **RESOLVED** - All manufacturer filtering now shows proper match scores

**Spine and Weight Display Fix (August 2025):**
- **Issue**: My setup page showing "Spine: N/A" and missing total arrow weight calculations
- **Root Cause**: API not returning spine specifications needed for calculations
- **Solution**:
  - Enhanced setup arrows API to include spine specifications with GPI weights
  - Added `getDisplaySpine()` function with proper fallback logic
  - Improved `calculateTotalArrowWeight()` with better spine specification matching
- **Files**: `arrow_scraper/api.py`, `frontend/components/BowSetupArrowsList.vue`
- **Status**: ✅ **RESOLVED** - Spine values and total weights now display correctly

**UI Accessibility Enhancement (August 2025):**
- **Issue**: When no recommendations found, filters become inaccessible, creating UX dead ends
- **Solution**: Restructured component to keep filters always visible with "No Recommendations" message below
- **Benefits**: Users can adjust manufacturer, weight, search terms without clearing all filters
- **Files**: `frontend/components/ArrowRecommendationsList.vue`
- **Status**: ✅ **ENHANCED** - Better discoverability and user experience

**Calculator Navigation Addition (August 2025):**
- **Issue**: Calculator page missing from main navigation menus
- **Solution**: Added Calculator links to both desktop and mobile navigation
- **Files**: `frontend/layouts/default.vue`
- **Status**: ✅ **ADDED** - Calculator now accessible from all pages

**Admin Spine Data Navigation Fix (August 2025):**
- **Issue**: Spine data link in admin panel navigation not working, resulting in 404 or navigation failures
- **Root Cause**: Nuxt 3 routing conflict between `admin.vue` and `admin/spine-data.vue` - having both a page file and directory with the same name prevents nested routes from being accessible
- **Solution**: Moved `admin.vue` to `admin/index.vue` to resolve routing conflict and enable proper nested admin route structure
- **Files**: `frontend/pages/admin.vue` → `frontend/pages/admin/index.vue`
- **Status**: ✅ **RESOLVED** - Admin spine data navigation now works correctly with proper nested routing

**Spine Data Database Path Mismatch Fix (August 2025):**
- **Issue**: API returning 500 Internal Server Error with "Failed to get manufacturer spine charts" and "no such table" errors
- **Root Cause**: Database path mismatch - spine calculation tables were created in `/databases/arrow_database.db` but API was looking in `/arrow_scraper/databases/arrow_database.db`
- **Solution**: 
  - Ran `migrate_spine_calculation_data.py` on correct database file used by API
  - Imported spine calculator sample data into API's database with 23 records across 6 tables
  - Created spine calculation tables: `calculation_parameters`, `arrow_material_properties`, `manufacturer_spine_charts`, etc.
- **Files**: Database migration affects `arrow_scraper/databases/arrow_database.db`
- **Status**: ✅ **RESOLVED** - Spine data API endpoints now have proper database tables and data

**Automatic Spine Data Migration Integration (August 2025):**
- **Feature**: Added automatic spine calculation data migration to all startup scripts
- **Implementation**:
  - `start-unified.sh` - Production startup now automatically checks and creates spine calculation tables
  - `start-local-dev.sh` - Local development startup includes spine migration before API start
  - Automatic detection using sqlite3 to check for required tables
  - Only runs migration if tables are missing (calculation_parameters, arrow_material_properties, manufacturer_spine_charts)
  - Automatically imports sample spine calculation data on first run
- **Benefits**: 
  - New deployments automatically get spine calculation functionality
  - No manual migration steps required for production or development
  - Graceful error handling if migration fails
  - Works with both unified database architecture and local development
- **Files**: `start-unified.sh`, `start-local-dev.sh`
- **Status**: ✅ **IMPLEMENTED** - Spine data migration now runs automatically on server startup

### Legacy Fixes & Enhancements (July 2025)

**GitHub Issue #16 - Bow Configuration Form Fixes:**
- **Issue**: Draw weight increments not set to 0.5 steps, missing arrow length and point weight fields in add modal, bow setup editing not persisting changes properly.
- **Solution**: 
  - Fixed draw weight increments to 0.5 steps in both `AddBowSetupModal.vue` and `setups/index.vue`
  - Added missing arrow length and point weight fields to `AddBowSetupModal.vue` with proper validation (point weight min: 40, step: 0.5)
  - Enhanced numeric field conversion in save/edit functions with `parseFloat()` for proper database storage
  - Improved error handling with detailed API response logging
- **Files**: `frontend/components/AddBowSetupModal.vue`, `frontend/pages/setups/index.vue`
- **Status**: ✅ **COMPLETED** - All bow setup form issues resolved

**Frontend `localStorage` Access on Server:**
- **Issue**: `localStorage is not defined` errors during Server-Side Rendering (SSR).
- **Solution**: Implemented `process.client` checks in `frontend/composables/useAuth.ts` and `frontend/composables/useDarkMode.js` to ensure `localStorage` is only accessed in the browser environment.

**Google Client ID Configuration:**
- **Issue**: `Error 401: invalid_client` or `Prop client id required` for Google login.
- **Cause**: Frontend not correctly picking up `NUXT_PUBLIC_GOOGLE_CLIENT_ID`.
- **Solution**:
    - Ensured `NUXT_PUBLIC_GOOGLE_CLIENT_ID` is explicitly exposed via `runtimeConfig.public` in `frontend/nuxt.config.ts`.
    - **Updated**: Environment variables are now consolidated in the root `.env` file for simplified configuration.
    - Verified `GOOGLE_CLIENT_SECRET` is set in the root `.env` for backend authentication.

**Cross-Origin-Opener-Policy (COOP) Conflicts:**
- **Issue**: Browser security policy blocking communication between main window and Google login pop-up (`Cross-Origin-Opener-Policy policy would block the window.closed call`).
- **Solution**: Set `Cross-Origin-Opener-Policy: unsafe-none` in `frontend/nuxt.config.ts` under `nitro.headers` for development environments.

**`await` Outside `async` Function Errors:**
- **Issue**: `await` keyword used in non-`async` functions in `frontend/composables/useAuth.ts`.
- **Solution**: Correctly marked `loginWithGoogle` and its internal `.then()` callback as `async`.

**Incorrect API Base URL (Double `/api/`):**
- **Issue**: Frontend making requests to `http://localhost:3000/api/api/auth/google` (404 Not Found).
- **Cause**: `config.public.apiBase` already included `/api`, and `/api/auth/google` was appended.
- **Solution**: Modified `fetch` calls in `frontend/composables/useAuth.ts` to use `config.public.apiBase` directly with `/auth/google` and `/user` (e.g., `${config.public.apiBase}/auth/google`).

**Missing Python Dependencies in Backend:**
- **Issue**: `ModuleNotFoundError: No module named 'httplib2'` or similar for backend dependencies.
- **Cause**: Dependencies not correctly installed in the active Python virtual environment for the Flask API.
- **Solution**:
    - Added missing dependencies (e.g., `httplib2`) to `arrow_scraper/requirements.txt`.
    - Emphasized running `source venv/bin/activate && pip install -r arrow_scraper/requirements.txt` from the project root to ensure installation into the correct virtual environment.

**Missing `.env` Loading in Flask API:**
- **Issue**: Flask backend not picking up environment variables (e.g., `CLIENT_ID: None`, `CLIENT_SECRET: NOT SET`).
- **Cause**: `python-dotenv`'s `load_dotenv()` was not called in `api.py`.
- **Solution**: Added `from dotenv import load_dotenv` and `load_dotenv()` at the top of `arrow_scraper/api.py`.

**`NameError: name 'timedelta' is not defined` in Flask API:**
- **Issue**: Error during JWT creation in `api.py`.
- **Cause**: `timedelta` was used without being imported from `datetime`.
- **Solution**: Modified `from datetime import datetime` to `from datetime import datetime, timedelta` in `arrow_scraper/api.py`.

**`TypeError: Object of type Row is not JSON serializable` in Flask API:**
- **Issue**: Backend failing to return user data from `/api/user` endpoint.
- **Cause**: `sqlite3.Row` object (returned by `cursor.fetchone()`) cannot be directly JSON serialized by Flask's `jsonify`.
- **Solution**: Converted `current_user` (a `sqlite3.Row` object) to a standard Python dictionary using `dict(current_user)` before passing it to `jsonify` in `api.py`'s `get_user` function.
- **Status**: ✅ **FIXED** - Authentication flow now works correctly after user login.

**`DeprecationWarning: datetime.datetime.utcnow()` in Flask API:**
- **Issue**: `datetime.utcnow()` is deprecated and scheduled for removal in future Python versions.
- **Cause**: Using deprecated `datetime.utcnow()` for JWT token expiration timestamps.
- **Solution**: Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)` in JWT token creation (compatible with Python 3.7+).
- **Status**: ✅ **FIXED** - No more deprecation warnings in logs.

**`AttributeError: type object 'datetime.datetime' has no attribute 'UTC'` in Flask API:**
- **Issue**: `datetime.UTC` not available in Python versions < 3.11, causing authentication to fail.
- **Cause**: Using `datetime.now(datetime.UTC)` which was introduced in Python 3.11.
- **Solution**: Changed to `datetime.now(timezone.utc)` for backward compatibility with Python 3.7+.
- **Status**: ✅ **FIXED** - Google authentication now works on all Python versions.

**Improved `start-dual-architecture.sh` Script:**
- **Issue**: Script not stopping services reliably, or requiring `Ctrl+C` to exit the terminal.
- **Solution**:
    - Removed `wait` command from `start` action to allow the script to exit immediately after launching background services.
    - Removed `EXIT` from `trap` command to prevent immediate shutdown upon script exit.
    - Implemented more robust process termination in `stop_services` using `kill -- -PGID` and `pgrep -g` for process group management, along with better PID checks (`kill -0 $PID`).
    - Added `PYTHONUNBUFFERED=1` to Flask startup command to ensure immediate log writes to `api.log`.

### User Management & Profile Editing

This section details the newly implemented user authentication and profile management features.

**Persistent User Database:**
- **Issue**: User data (accounts, profiles) was previously stored in the main `arrow_database.db`, which is frequently rebuilt during scraping, leading to data loss.
- **Solution**: Implemented a separate SQLite database file (`user_data.db`) dedicated solely to user accounts. This ensures user data persists across database rebuilds and application updates.
- **Files**: `arrow_scraper/user_database.py` (new), `arrow_scraper/auth.py`, `arrow_scraper/api.py`.

**Optional User Registration (Full Name):**
- **Feature**: After initial Google login, new users are optionally redirected to a registration page to provide their full name. This allows for a more personalized experience.
- **Backend (`arrow_scraper/auth.py`, `arrow_scraper/api.py`):**
    - `get_user_from_google_token` now returns a `needs_profile_completion` flag, which is `True` for all newly created users.
    - The `/api/auth/google` endpoint includes this flag in the JWT response.
- **Frontend (`frontend/composables/useAuth.ts`, `frontend/layouts/default.vue`, `frontend/pages/register.vue`):**
    - `useAuth.ts`'s `loginWithGoogle` now resolves with the `needsProfileCompletion` flag.
    - `frontend/layouts/default.vue` checks this flag after login and redirects to `/register` if `True`.
    - `frontend/pages/register.vue` provides a form for users to enter their full name.

**User Profile Editing on "My Page":**
- **Feature**: Authenticated users can now edit their full name directly from their "My Page".
- **Backend (`arrow_scraper/api.py`):**
    - New `PUT /api/user/profile` endpoint added, allowing authenticated users to update their `name`. This endpoint uses the dedicated `user_database.py`.
- **Frontend (`frontend/pages/my-page.vue`, `frontend/composables/useAuth.ts`):**
    - `frontend/pages/my-page.vue` now displays an "Edit Profile" button.
    - A modal form allows users to input a new name, which is sent via `updateUserProfile` in `useAuth.ts`.
    - `useAuth.ts`'s `updateUserProfile` sends the `PUT` request and refreshes the local user state.

**Frontend Reactivity & Display Fixes (My Page / Edit Button):**
- **Issue**: After login, "My Page" sometimes required a manual refresh to display user data or the "Edit Profile" button.
- **Cause**: Reactivity issues where the `user` object was not consistently updated or watched by `my-page.vue` after asynchronous login operations.
- **Solution**:
    - Removed `await fetchUser()` from `loginWithGoogle` in `useAuth.ts` to prevent premature state updates.
    - Explicitly called `fetchUser()` in `frontend/layouts/default.vue` after login (if no redirection to `/register` is needed).
    - Added explicit `fetchUser()` call within `onMounted` of `frontend/pages/my-page.vue` to ensure data is always fresh when the component mounts.
    - Added a `watch` listener on the `user` ref in `frontend/pages/my-page.vue` to reactively update the UI when user data changes.

**`start-dual-architecture.sh` Script `ps` Error Fix:**
- **Issue**: Recurring `error: process ID list syntax error` messages in the console when running `start-dual-architecture.sh`.
- **Cause**: Problematic `ps` command syntax (`ps -o pgid= -p $ | awk '{print $1}'`) used to retrieve the script's process group ID, likely due to shell variable expansion or `ps` version differences.
- **Solution**: Replaced the problematic `ps` command with a more robust Python one-liner: `python -c "import os; print(os.getpgrp())"`. This directly retrieves the process group ID using Python's `os` module, bypassing shell-specific `ps` issues.
- **Status**: ✅ **FIXED** - Script output is now clean.

**Admin System Implementation (July 2025):**
- **Feature**: Complete admin authentication system with automatic privilege assignment
- **Implementation**: 
  - Automatic admin access for `messenlien@gmail.com` on first login or database reset
  - Full admin API endpoints for user management (`/api/admin/*`)
  - Admin panel accessible at `/admin` frontend route
  - Admin check functionality with proper authentication flow
- **Files Modified**: `arrow_scraper/auth.py`, `arrow_scraper/api.py`, `arrow_scraper/user_database.py`, `frontend/pages/admin.vue`
- **Status**: ✅ **PRODUCTION READY** - Admin system fully functional

**Global State Management Fix:**
- **Issue**: Admin access not working properly on frontend despite backend authentication success
- **Cause**: `useAuth.ts` composable creating new reactive state instead of sharing global state
- **Solution**: Moved `token` and `user` refs to global scope outside the composable function
- **Files**: `frontend/composables/useAuth.ts`
- **Status**: ✅ **FIXED** - Admin authentication now works end-to-end

**String Formatting TypeError Fixes:**
- **Issue**: `TypeError: Cannot read properties of undefined (reading 'charAt')` in arrow type formatting
- **Cause**: `formatArrowType` functions calling `.charAt(0)` on potentially empty/null strings
- **Solution**: Added defensive programming with null checks before charAt() calls
- **Files Fixed**: 
  - `frontend/pages/index.vue` (formatArrowType function)
  - `frontend/pages/database.vue` (formatArrowType function)
  - `frontend/components/SavedArrowSetups.vue` (formatArrowType function)
- **Status**: ✅ **FIXED** - All string formatting errors resolved

**Enhanced Production Infrastructure Implementation (July 2025):**
- **Feature**: Comprehensive production Docker infrastructure with verification and health checks
- **Implementation**:
  - `deploy-enhanced.sh` - Automated deployment script with comprehensive verification pipeline
  - `docker-compose.enhanced-ssl.yml` - Enhanced Docker Compose with health checks and resource limits
  - `arrow_scraper/Dockerfile.enhanced` - API Dockerfile with database verification and build integrity
  - `frontend/Dockerfile.enhanced` - Frontend Dockerfile with build verification and health checks
  - `arrow_scraper/start-api-robust.sh` - Robust startup script with database initialization
  - `arrow_scraper/verify-databases.py` - Comprehensive database integrity checking
  - `test-bow-saving.py` - Production functionality testing utility
- **Key Features**:
  - Database integrity verification at container startup
  - Multi-stage health checks with extended timeouts (120s start period)
  - User database persistence with Docker volumes
  - Build verification ensuring frontend and API integrity
  - Comprehensive error handling and logging throughout deployment
  - Resource limits and security hardening for production
  - Database backup and migration support
- **Status**: ✅ **PRODUCTION READY** - Enhanced infrastructure resolves bow saving issues and provides production reliability

### Production Deployment Issues

**Docker Permission Errors:**
- **Issue**: `permission denied while trying to connect to the Docker daemon socket`
- **Solution**: Add user to docker group: `sudo usermod -aG docker $USER && newgrp docker`
- **Alternative**: Use `sudo` with docker commands

**Frontend "nuxt: not found" Error:**
- **Issue**: Container running `npm run dev` but nuxt CLI not available in production build
- **Cause**: `docker-compose.override.yml` forces development mode
- **Solution**: Use production configs or disable override file temporarily
- **Script**: `./deploy-production.sh` handles this automatically

**Mixed Content Error (HTTPS):**
- **Issue**: "Blocked loading mixed active content" when frontend makes HTTP API calls from HTTPS
- **Cause**: Frontend configured with `http://api:5000/api` instead of HTTPS URL
- **Solution**: Update `NUXT_PUBLIC_API_BASE` to use `https://yourdomain.com/api`
- **Script**: `./fix-mixed-content.sh` fixes this automatically

**Database Schema Mismatch:**
- **Issue**: `no such column: a.primary_image_url` API errors
- **Cause**: Database built with `image_url` but API expects `primary_image_url`
- **Solution**: Query uses `image_url as primary_image_url` for compatibility
- **Location**: `/arrow_scraper/arrow_database.py:488`

**Container Networking Issues:**
- **Issue**: Frontend cannot reach API (ECONNREFUSED)
- **Cause**: Wrong environment variable name (`API_BASE_URL` vs `NUXT_PUBLIC_API_BASE`)
- **Solution**: All Docker Compose files now use correct `NUXT_PUBLIC_API_BASE`
- **Verification**: `./test-container-network.sh` diagnoses connectivity

**Domain Access Problems:**
- **Issue**: Site not accessible via domain name
- **Diagnosis**: `./diagnose-domain-access.sh` checks DNS, ports, containers
- **Common causes**: DNS not pointing to server, nginx not running, firewall blocking ports
- **Solution**: Use full `docker-compose.yml` with nginx, not `docker-compose.prod.yml`

### Development Issues

**Material Web Component Styling:**
- **Issue**: Buttons showing purple background with invisible text/icons
- **Solution**: Multiple CSS layers implemented with fallback CustomButton component
- **Files**: `/frontend/assets/css/main.css`, `/frontend/plugins/fix-material-buttons.client.ts`, `/frontend/components/CustomButton.vue`

**Hydration Mismatches:**
- **Issue**: Server-side rendering conflicts with client-side styling
- **Solution**: Simplified CSS approach with post-hydration styling injection
- **Prevention**: Avoid aggressive `!important` declarations in SSR-rendered content

**Dark Mode UI Issues:**
- **Issue**: Sidebar menu and page background remaining light in dark mode
- **Fixed**: Added comprehensive dark mode CSS for all UI components
- **Solution**: Enhanced CSS with `.dark` variants for cards, navigation tabs, input fields, badges, and compatibility indicators
- **Files**: `/frontend/assets/css/main.css` (dark mode component styling), `/frontend/layouts/default.vue` (loading indicator fix)

### Performance Optimizations

**Frontend Build:**
- Vite-based build system for fast development and optimized production builds
- Tree-shaking for Material Web components to reduce bundle size
- CSS optimization with Tailwind CSS purging

**API Response Caching:**
- Database statistics cached to reduce query overhead
- Arrow recommendations cached per bow configuration

**Responsive Image Loading:**
- Lazy loading for arrow specification images
- WebP format support with fallbacks

### Development Environment Setup

**Prerequisites:**
- Node.js 18+ for frontend development
- Python 3.9+ with virtual environment for backend
- DeepSeek API key for web scraping functionality

**Common Development Commands:**
```bash
# Quick dual-architecture startup
./scripts/start-dual-architecture.sh start

# Frontend development with hot reload
cd frontend && npm run dev

# Backend API development
cd arrow_scraper && source venv/bin/activate && python api.py
```