# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Arrow Database & Tuning Calculator project that scrapes arrow specifications from manufacturer websites and provides professional tuning calculations for archery equipment. The project has completed all development phases (1-6) and is **READY FOR BETA TESTING** with a production-ready full-stack arrow tuning platform featuring modern UI/UX.

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

**Option 1: Docker Deployment (Recommended)**

**Quick Deployment (Handles cleanup automatically):**
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

**Basic Scraper Usage:**
```bash
# Navigate to scraper directory
cd arrow_scraper

# Activate virtual environment (recommended)
source venv/bin/activate

# Run scraper for specific manufacturer (English-only)
python main.py easton

# Update ALL manufacturers with automatic translation (RECOMMENDED)
python main.py --update-all

# Update all manufacturers without translation (faster but English-only)
python main.py --update-all --no-translate

# Force update existing data with translation
python main.py --update-all --force

# List all available manufacturers (13+ supported with language info)
python main.py --list-manufacturers

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
- **Traditional**: Wood arrow manufacturers

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
```bash
# Initialize or rebuild database from JSON files
cd arrow_scraper
python arrow_database.py

# Show database statistics
python show_available_data.py

# Migrate existing database to include diameter categories
python migrate_diameter_categories.py
```

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

# Diameter categories testing
python test_diameter_categories.py

# Crawl4AI tests (comprehensive test suite)
cd crawl4ai
python -m pytest tests/
```

### Production Deployment (PRODUCTION READY)

**Quick Start Production Deployment**
```bash
# Step 1: Clone and configure
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Step 2: Configure environment
cp .env.example .env
# Edit .env with your settings

# Step 3: Deploy with HTTP
./deploy-production.sh

# Step 4: Configure DNS
# Add A record: yourdomain.com -> your-server-ip

# Step 5: Set up SSL certificates
sudo certbot certonly --standalone -d yourdomain.com
./enable-https.sh

# Step 6: Deploy with HTTPS
sudo docker-compose -f docker-compose.ssl.yml up -d --build
```

**Production Features:**
- ✅ Nginx reverse proxy with SSL termination
- ✅ Automatic HTTP to HTTPS redirects
- ✅ Docker containerization with health checks
- ✅ Embedded database (no external dependencies)
- ✅ Material Design 3 UI with dark mode
- ✅ Professional arrow tuning calculations
- ✅ Modern security headers and TLS configuration

**Deployment Scripts:**
- `deploy-production.sh` - Automated production deployment
- `enable-https.sh` - SSL certificate setup and HTTPS enablement
- `fix-mixed-content.sh` - Fix HTTP/HTTPS mixed content issues
- `diagnose-domain-access.sh` - Domain and networking diagnostics

### Deploying Scraper Updates to Production

**🚀 Quick Production Update (Latest Changes)**
```bash
# On your production server
cd /path/to/your/arrowtuner/project

# Pull latest changes
git pull

# Rebuild and restart containers with latest code
sudo docker-compose -f docker-compose.ssl.yml down
sudo docker-compose -f docker-compose.ssl.yml up -d --build

# Verify deployment
curl https://yourdomain.com/api/health
```

**🏹 Deploying Fresh Arrow Data**
```bash
# Method 1: Local scraping then production deploy
# 1. Run scraper locally
cd arrow_scraper
source venv/bin/activate
python main.py easton goldtip victory
python arrow_database.py

# 2. Commit and push changes
git add .
git commit -m "Update arrow database with latest scraped data"
git push

# 3. Deploy to production
# On production server:
git pull
sudo docker-compose -f docker-compose.ssl.yml up -d --build

# Method 2: Direct production scraping (advanced)
# Run scraper in production Docker container
sudo docker exec -it arrowtuner-api bash
cd /app
python main.py easton goldtip victory
python arrow_database.py
exit
sudo docker-compose restart api
```

**⚠️ Production Deployment Notes:**
- **Database Persistence**: Arrow database persists through container rebuilds
- **HTTPS Required**: Always use `docker-compose.ssl.yml` for production
- **Backup Recommended**: Backup database before major scraper updates
- **Verification**: Always test API health endpoint after deployment
- **Zero Downtime**: Rebuild process maintains service availability

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
- `frontend/` - Modern Nuxt 3 SPA frontend application
  - `pages/` - Vue.js pages (index/bow-setup, database, arrow-details)
  - `components/` - Reusable Vue components with Material Web integration
    - `ArrowRecommendationsList.vue` - Advanced filtering and recommendation display
    - `DarkModeToggle.vue` - Theme switching component
    - `CustomButton.vue` - Fallback button component with Material Design styling
  - `composables/` - Vue 3 composition functions
    - `useApi.ts` - API communication layer
    - `useDarkMode.js` - Dark mode state management
    - `useMaterialWeb.ts` - Material Web component utilities
  - `stores/` - Pinia state management (bow configuration, user preferences)
  - `types/` - TypeScript type definitions for arrows and API responses
  - `plugins/` - Nuxt plugins for Material Web and button styling fixes
  - `assets/css/` - Tailwind CSS with Material Design 3 theming
- `crawl4ai/` - Custom fork of Crawl4AI web crawling library
- `deploy/` - Legacy production deployment system
- `scripts/` - Dual architecture deployment scripts
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

## Important Notes

### Current Platform Status (2025)
- **Production-Ready Platform:** Complete arrow tuning solution with modern UI/UX
- **Modern Architecture:** Nuxt 3 SPA frontend + Flask API backend with dual deployment
- **Material Design 3:** Professional UI with Google's latest design system and dark mode
- **Enhanced UX:** Improved accessibility, responsive design, and user interaction
- **Advanced Filtering:** Sophisticated search with manufacturer, spine, diameter, and weight filters
- **Database Statistics:** Real-time metrics showing 13 manufacturers with 197+ arrow models

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
- **Legacy Support:** Original Flask web application still available (deprecated)
- **Production Deployment:** Enterprise-ready deployment system with automated setup
- **Security Hardening:** UFW firewall, fail2ban, SSL certificates, rate limiting
- **Monitoring & Maintenance:** Health checks, automated backups, log management
- **Docker Support:** Complete containerization with docker-compose configuration

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

The Arrow Tuning Platform provides:
1. **Professional spine calculations** based on bow specifications and shooting style
2. **Intelligent arrow recommendations** with confidence scoring and alternatives  
3. **Advanced tuning optimization** including FOC, kinetic energy, and momentum calculations
4. **Comprehensive database search** with filtering by manufacturer, spine, diameter, and GPI
5. **Visual arrow comparison** with detailed specification analysis
6. **Session tracking** for tuning progress and recommendation history
7. **Modern web interface** with Material Design 3 components and dark mode
8. **Responsive design** optimized for desktop, tablet, and mobile devices
9. **API endpoints** for integration with other archery tools
10. **Real-time database statistics** with manufacturer and arrow count metrics

## Troubleshooting & Development Notes

### Docker Issues

**Orphan Container Errors:**
- **Issue**: `ERROR: for arrowtuner-api 'ContainerConfig'` or needing `--remove-orphans` flag every time
- **Cause**: Multiple Docker Compose files creating conflicting container configurations
- **Solution**: Use the automated cleanup scripts:
  ```bash
  # Clean up before deployment (automatic)
  ./docker-deploy.sh
  
  # Manual cleanup if needed
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

### Recent Fixes & Enhancements (July 2025)

This section details recent fixes and improvements to common development and deployment issues.

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