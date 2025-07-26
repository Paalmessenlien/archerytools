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
```bash
# Simple deployment with embedded database
docker-compose up -d --build

# View logs
docker-compose logs -f

# Test deployment
./test-simple-deployment.sh

# Frontend: http://localhost:3000
# API Backend: http://localhost:5000
```

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
```bash
# Run scraper for specific manufacturer
cd arrow_scraper
python main.py easton

# List available manufacturers (13 supported)
python main.py --list-manufacturers

# Run with virtual environment
source venv/bin/activate
python arrow_scraper/main.py easton
```

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

### Production Deployment (READY FOR BETA)

**Docker Deployment (Recommended)**
```bash
# Quick production deployment
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs
```

**Manual Ubuntu Server Deployment**
```bash
# Step 1: Server setup (Ubuntu 20.04+)
sudo ./deploy/server-setup.sh

# Step 2: Deploy application
sudo ./deploy/deploy.sh yourdomain.com admin@yourdomain.com

# Step 3: Check status
/opt/arrowtuner/status.sh
```

**Production Features:**
- ✅ Nginx reverse proxy with SSL
- ✅ PM2 process management
- ✅ Automated backups and monitoring
- ✅ Security hardening (UFW, fail2ban)
- ✅ Health checks and alerting
- ✅ Log rotation and cleanup

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

# Frontend Configuration
FRONTEND_PORT=3000
NODE_ENV=production
API_BASE_URL=http://localhost:5000

# Production Domain
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

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

### Common Issues & Solutions

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

**Database Statistics:**
- **Issue**: Total manufacturers showing as 0
- **Fixed**: API now calculates `len(stats.get('manufacturers', []))` instead of hardcoded value
- **Location**: `/arrow_scraper/api.py:155`

**Manufacturer Filtering:**
- **Issue**: Required two selections to work properly
- **Fixed**: Enhanced reactivity with proper computed properties and debugging
- **Location**: `/frontend/components/ArrowRecommendationsList.vue`

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