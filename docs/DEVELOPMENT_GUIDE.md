# Development Guide & Architecture Overview

This guide provides a comprehensive overview of the Archery Tools platform architecture, development workflows, and best practices for contributors.

## Table of Contents
- [System Architecture](#system-architecture)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Development Workflows](#development-workflows)
- [Testing Strategy](#testing-strategy)
- [Deployment Process](#deployment-process)
- [Recent Updates](#recent-updates)
- [Troubleshooting](#troubleshooting)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Nuxt 3 SPA)                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │     Pages       │ │   Components    │ │     Stores      │ │
│  │   (Vue.js)      │ │ (Material Web)  │ │   (Pinia)       │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │ HTTP/REST API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (Flask API)                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   API Routes    │ │   Business      │ │   Database      │ │
│  │   (REST)        │ │   Logic         │ │   Models        │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Unified Database System (2025)           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Single Database (arrow_database.db)        │ │
│  │  ┌─────────────────┐     ┌─────────────────────────────┐ │ │
│  │  │  Arrow Data     │     │        User Data            │ │ │
│  │  │  (Arrows, Spine │     │  (Users, Setups, Sessions)  │ │ │
│  │  │   Components)   │     │     (Read/Write)            │ │ │
│  │  └─────────────────┘     └─────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- **Framework**: Nuxt 3 (Vue.js 3 + TypeScript)
- **UI Library**: Material Web Components + Custom Components
- **Styling**: Tailwind CSS + Material Design 3 theming
- **State Management**: Pinia stores
- **Build Tool**: Vite
- **Authentication**: Google OAuth + JWT tokens

**Backend:**
- **Framework**: Flask (Python 3.9+)
- **Database**: SQLite (unified database architecture - August 2025)
- **Authentication**: JWT tokens + Google OAuth validation
- **API Style**: RESTful JSON API
- **File Handling**: Local storage + CDN integration

**Data Sources:**
- **Arrow Data**: JSON files from web scraping (Crawl4AI + DeepSeek API)
- **Components**: Manufacturer specification data
- **User Data**: Real-time database storage

**Infrastructure:**
- **Development**: Local Flask + Nuxt dev servers
- **Production**: Docker containers with Nginx reverse proxy
- **Database Storage**: Docker volumes for persistence
- **Image CDN**: Bunny CDN / Cloudinary / AWS S3

---

## Development Environment

### Prerequisites
```bash
# System Requirements
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- Git
- Docker & Docker Compose (for production testing)

# API Keys
- DeepSeek API key (for scraping)
- Google OAuth credentials
- CDN credentials (optional)
```

### Quick Setup (Unified System - August 2025)
```bash
# 1. Clone repository
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# 2. Backend setup
cd arrow_scraper
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env
# Edit .env with your API keys

# 4. Frontend setup
cd ../frontend
npm install

# 5. Start unified development environment (RECOMMENDED)
./start-unified.sh dev start

# Alternative: Manual startup
# Terminal 1: Backend
cd arrow_scraper && source venv/bin/activate && python api.py

# Terminal 2: Frontend  
cd frontend && npm run dev
```

### Environment Variables

**Root `.env` file:**
```env
# API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SECRET_KEY=your-secret-key-here-change-this
API_PORT=5000
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:3000

# Frontend Configuration
FRONTEND_PORT=3000
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id-here
NODE_ENV=development
NUXT_PUBLIC_API_BASE=http://localhost:5000/api

# Production Domain (for deployment)
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com

# CDN Configuration (optional)
BUNNY_CDN_API_KEY=your_bunny_api_key
BUNNY_STORAGE_ZONE=your_storage_zone
CLOUDINARY_CLOUD_NAME=your_cloud_name
```

---

## Project Structure

```
archerytools/
├── docs/                           # Documentation
│   ├── DATABASE_SCHEMA.md
│   ├── API_ENDPOINTS.md
│   └── DEVELOPMENT_GUIDE.md
├── arrow_scraper/                  # Backend API Server
│   ├── api.py                      # Main Flask API application
│   ├── models.py                   # Data models and validation
│   ├── arrow_database.py           # Arrow database management
│   ├── user_database.py            # User database management
│   ├── spine_calculator.py         # Spine calculation engine
│   ├── arrow_matching_engine.py    # Arrow recommendation system
│   ├── databases/                  # SQLite database files
│   ├── data/processed/             # JSON data files (scraped arrows)
│   ├── scrapers/                   # Web scraping modules
│   └── config/                     # Configuration files
├── frontend/                       # Nuxt 3 SPA Frontend
│   ├── pages/                      # Vue.js pages (file-based routing)
│   │   ├── index.vue              # Home page
│   │   ├── calculator.vue          # Arrow calculator
│   │   ├── database.vue           # Arrow database browser
│   │   ├── my-page.vue            # User profile & bow setups
│   │   └── bow/[id].vue           # Bow detail pages
│   ├── components/                 # Reusable Vue components
│   │   ├── ArrowRecommendationsList.vue
│   │   ├── BowSetupArrowsList.vue
│   │   ├── CustomButton.vue       # Fallback button component
│   │   └── DarkModeToggle.vue
│   ├── composables/               # Vue 3 composition functions
│   │   ├── useApi.ts              # API communication layer
│   │   ├── useAuth.ts             # Authentication management
│   │   └── useDarkMode.js         # Dark mode state
│   ├── stores/                    # Pinia state management
│   │   └── bowConfig.ts           # Bow configuration store
│   ├── types/                     # TypeScript type definitions
│   │   └── arrow.ts               # API response types
│   ├── assets/css/                # Tailwind CSS + Material theming
│   ├── plugins/                   # Nuxt plugins
│   └── nuxt.config.ts             # Nuxt configuration
├── scripts/                       # Legacy deployment scripts (archived)
│   └── archive/                   # Archived legacy startup scripts
├── start-unified.sh               # Unified startup script (ALL deployment modes)
├── stop-unified.sh                # Unified stop script
├── docker-cleanup.sh              # Docker maintenance
├── docker-compose*.yml            # Docker configurations
├── CLAUDE.md                      # Project context for AI assistance
└── README.md                      # Project overview
```

---

## Database Architecture & Locations

### Understanding Database File Locations

The project uses SQLite databases stored in **two locations** depending on the context:

#### Active Database (Used by API)
**Location**: `arrow_scraper/databases/arrow_database.db`
- **Size**: ~1.3 MB (larger, actively maintained)
- **Used by**: Flask API server, all backend operations
- **Contains**: 209 arrows from 18 manufacturers (as of October 2025)
- **Migrations Applied**: 45 migrations via `database_migrations` table
- **Purpose**: This is the **production database** used by the running application

#### Legacy/Testing Database
**Location**: `databases/arrow_database.db`
- **Size**: ~987 KB (smaller, less frequently updated)
- **Used by**: Some standalone scripts and testing
- **Contains**: 206 arrows from 14 manufacturers (slightly outdated)
- **Purpose**: Historical reference, some utility scripts

### Why Two Locations?

The dual-location setup exists due to the evolution of the project structure:
1. **Original**: Database was in `/databases/` directory
2. **Migration**: Backend code moved to `/arrow_scraper/` directory
3. **Current**: Active database moved with backend to keep related files together
4. **Legacy**: Old location kept for compatibility with some scripts

### Which Database Should I Use?

**For Development:**
- **API Development**: Always use `arrow_scraper/databases/arrow_database.db`
- **Database Queries**: Use `arrow_scraper/databases/arrow_database.db`
- **Migration Testing**: Use `arrow_scraper/databases/arrow_database.db`
- **Statistics Verification**: Use `arrow_scraper/databases/arrow_database.db`

**When to Use Legacy Database:**
- Only when explicitly working with legacy scripts
- For historical comparison or reference

### Verifying Active Database

To confirm which database the API is using:

```bash
# Check arrow count in active database
sqlite3 arrow_scraper/databases/arrow_database.db "SELECT COUNT(*) FROM arrows;"
# Should return: 209

# Check via API health endpoint
curl http://localhost:5000/api/health
# Should show: "total_arrows": 209, "total_manufacturers": 18
```

### Database Backup Locations

**Development Backups:**
- Automatically created in `arrow_scraper/databases/`
- Naming pattern: `arrow_database_backup_YYYYMMDD_HHMMSS.db`

**Production Backups:**
- Stored in Docker volumes: `/app/databases/`
- Managed through admin panel backup system
- CDN upload for off-server redundancy

### Avoiding Database Confusion

**Best Practices:**
1. **Always specify full path** when accessing database in code
2. **Use environment detection** to determine correct path
3. **Document which database** is used in new scripts
4. **Consider consolidation** to single location in future refactoring

**Example Code Pattern:**
```python
import os

# Always use arrow_scraper database for API operations
ARROW_SCRAPER_DB = os.path.join(
    os.path.dirname(__file__),
    'arrow_scraper',
    'databases',
    'arrow_database.db'
)
```

---

## Development Workflows

### Feature Development Workflow

1. **Setup Development Environment**
   ```bash
   # Start unified development environment (RECOMMENDED)
   ./start-unified.sh dev start
   
   # Stop development environment
   ./start-unified.sh dev stop
   
   # Alternative manual startup:
   # Terminal 1: Backend
   cd arrow_scraper && source venv/bin/activate && python api.py
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

2. **Database Development**
   ```bash
   # View current data
   cd arrow_scraper
   python show_available_data.py
   
   # Update arrow data (development only)
   python main.py --manufacturer=easton --limit=5 --use-deepseek
   
   # Test database connections
   python test_setup.py
   ```

3. **API Development**
   ```bash
   # Test API endpoints
   python test_api.py
   python test_recommendations_api.py
   
   # Check database integrity
   python verify-databases.py
   
   # Admin functionality testing
   python test_admin_api.py
   ```

4. **Frontend Development**
   ```bash
   cd frontend
   
   # Development with hot reload
   npm run dev
   
   # Type checking
   npm run typecheck
   
   # Linting
   npm run lint
   
   # Build for production testing
   npm run build && npm run preview
   ```

### Equipment Management System Workflow

The equipment management system provides comprehensive equipment tracking with 9 equipment categories:

1. **Equipment Categories (All Tested August 2025)**
   ```bash
   # All 9 categories successfully tested:
   # 1. String         - String materials, strand counts, serving
   # 2. Sight          - Multi/single pin, adjustment types, lighting
   # 3. Scope          - Magnification, reticle types, turret types
   # 4. Stabilizer     - Length, weight, dampening, mounting
   # 5. Arrow Rest     - Drop-away, blade, containment features
   # 6. Plunger        - Spring-loaded, magnetic, tension ranges
   # 7. Weight         - Ounce specifications, mounting locations
   # 8. Peep Sight     - Aperture diameter, mounting styles
   # 9. Other          - Open-ended equipment with custom specs
   ```

2. **Database Schema Fix (Migration 025)**
   ```bash
   # Critical fix for equipment creation
   # Issue: NOT NULL constraint failed: bow_equipment.equipment_id
   # Solution: Made equipment_id nullable for custom equipment
   
   # Apply migration in development
   cd arrow_scraper
   python migrations/025_fix_equipment_id_nullable_unified.py databases/arrow_database.db
   
   # Production deployment will apply automatically
   ```

3. **Testing Equipment Management**
   ```bash
   # Test all equipment categories
   python test_equipment_management.py
   
   # Test custom equipment creation
   python test_custom_equipment_creation.py
   
   # Verify database schema
   sqlite3 databases/arrow_database.db ".schema bow_equipment"
   ```

4. **Key Features**
   - Category-specific form fields with validation
   - Manufacturer suggestion system with approval workflow
   - Custom equipment creation without database constraints
   - Installation tracking with notes and specifications

### Chronograph Data Integration Workflow

The chronograph system provides measured arrow speed data for enhanced performance calculations:

1. **Database Setup**
   ```bash
   # Verify chronograph table exists
   sqlite3 databases/arrow_database.db ".schema chronograph_data"
   
   # Create test chronograph data
   python arrow_scraper/create_test_chronograph_data.py
   
   # Verify chronograph setup
   python arrow_scraper/verify_chronograph_setup.py
   ```

2. **API Development**
   ```bash
   # Test chronograph endpoints
   python arrow_scraper/test_api_chronograph.py
   
   # Test integration with performance calculations
   python arrow_scraper/test_chronograph_integration.py
   
   # Debug speed calculations
   python debug_performance_calculation.py
   ```

3. **Frontend Integration**
   - ChronographDataEntry component in `frontend/components/`
   - Auto-updates performance calculations when data changes
   - Displays confidence levels (measured vs estimated)

4. **Key Features**
   - Prioritizes measured data over estimations
   - Weight-adjusted speed calculations
   - Environmental condition tracking
   - Statistical analysis (std deviation, min/max)

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/bow-detail-improvements

# Make changes and test
# ... development work ...

# Commit with descriptive messages
git add .
git commit -m "🔧 Improve bow detail page navigation

- Fixed arrow listing display issue
- Added proper error handling for API calls
- Enhanced responsive layout for mobile devices

🎯 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push and create PR
git push origin feature/bow-detail-improvements
```

### Code Style Guidelines

**Python (Backend):**
- Follow PEP 8 styling
- Use type hints where appropriate
- Descriptive function and variable names
- Comprehensive error handling
- Database transactions with proper cleanup

**TypeScript/Vue (Frontend):**
- Use Composition API (Vue 3 style)
- TypeScript for all new components
- Props validation and default values
- Consistent naming: camelCase for JS, kebab-case for templates
- Material Web components preferred over custom HTML

**Database:**
- Use transactions for multi-table operations
- Index frequently queried columns
- Normalize data appropriately
- Foreign key constraints for data integrity

---

## Testing Strategy

### Backend Testing
```bash
cd arrow_scraper

# Basic functionality
python test_setup.py
python test_basic.py

# API endpoints
python test_api.py
python test_recommendations_api.py

# Admin functionality
python test_admin_api.py
python test_admin_with_auth.py

# Database operations
python test_diameter_categories.py

# Equipment management system
python test_equipment_management.py
python test_custom_equipment_creation.py

# DeepSeek API integration
python test_deepseek.py
```

### Frontend Testing
```bash
cd frontend

# Type checking
npm run typecheck

# Linting
npm run lint

# Build verification
npm run build

# Manual testing checklist:
# - Authentication flow
# - Arrow search and filtering
# - Bow setup management
# - Calculator functionality
# - Dark mode toggle
# - Responsive design on mobile
```

### Integration Testing
```bash
# Test full workflow
python test-bow-saving.py

# Test container deployment
./deploy-enhanced.sh docker-compose.enhanced-ssl.yml

# Health checks
curl http://localhost:5000/api/health
curl http://localhost:3000/api/health
```

### Production Testing
```bash
# Verify database integrity
python verify-databases.py

# Test backup system
curl http://localhost:5000/api/admin/backup-test

# Performance testing
# - Load test with multiple concurrent users
# - Database query performance
# - Memory usage monitoring
```

---

## Deployment Process

### Local Development (Unified System)
```bash
# Unified development startup (RECOMMENDED)
./start-unified.sh dev start

# Show all available commands
./start-unified.sh --help

# Access:
# Frontend: http://localhost:3000
# API: http://localhost:5000
# API Health: http://localhost:5000/api/health

# Stop development environment
./start-unified.sh dev stop
```

### Production Deployment

**Production Deployment (Unified System):**
```bash
# Clone to production server
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Configure environment
cp .env.example .env
# Edit .env with production values

# Deploy with SSL (RECOMMENDED)
./start-unified.sh ssl yourdomain.com

# Deploy for local production testing
./start-unified.sh production start

# Stop production services
./start-unified.sh production stop

# The unified script handles:
# - SSL certificate verification
# - Environment variable setup
# - Database import and verification  
# - Service health checks
# - Access URL display

# Verify deployment
python3 test-bow-saving.py
curl https://yourdomain.com/api/health
```

### Deployment Checklist

**Pre-deployment:**
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] SSL certificates available (production)
- [ ] DNS configured (production)
- [ ] Database backups completed

**During deployment:**
- [ ] Enhanced deployment script completed successfully
- [ ] Health checks passing
- [ ] Database integrity verified
- [ ] User authentication working
- [ ] Arrow data imported correctly

**Post-deployment:**
- [ ] Monitor logs for errors
- [ ] Test core user workflows
- [ ] Verify backup system functioning
- [ ] Performance monitoring active

---

## Recent Updates

### August 2025: Critical Spine Calculation Fixes

**Major fixes to spine calculation accuracy** - See [Spine Calculation Fixes](SPINE_CALCULATION_FIXES_AUGUST_2025.md) for details:

1. **Arrow Length Direction Fixed**: Longer arrows now correctly require stiffer spines (lower numbers)
   - Fixed backwards length adjustment logic in spine calculations
   - 28"→700, 29"→675, 30"→650, 31"→625 (correctly decreasing)

2. **Wood Arrow System Implemented**: Wood arrows now use proper pound test values
   - Wood arrows return spine values like "40#" instead of deflection values like "700"
   - Proper material_preference parameter handling throughout calculation chain

3. **Database Schema Updates**: Added migrations for new functionality
   - Migration 051: `string_material` column for string type effects
   - Migration 052: `wood_species` column for wood arrow specifications

**Validation**: All fixes validated against German industry standards and real-world archery physics.

---

## Troubleshooting

### Common Development Issues

**Backend Issues:**
```bash
# Database permission errors
python -c "import sqlite3; print('SQLite working')"
ls -la arrow_scraper/databases/

# API import errors
cd arrow_scraper && source venv/bin/activate
python -c "from user_database import UserDatabase; print('Imports working')"

# Port already in use
lsof -ti:5000 | xargs kill -9  # Kill process on port 5000
```

**Frontend Issues:**
```bash
# Node modules issues
rm -rf node_modules package-lock.json
npm install

# TypeScript errors
npm run typecheck

# Build failures
rm -rf .nuxt .output
npm run build
```

**Database Issues:**
```bash
# Check database files exist
ls -la arrow_scraper/databases/

# Verify database integrity
cd arrow_scraper && python verify-databases.py

# Reset user database (development only)
rm databases/user_data.db
python api.py  # Will recreate database
```

**Manufacturer Approval System Issues:**
If new manufacturers created through bow setup forms don't appear in admin pending approval:
```bash
# Check if manufacturer approval tables exist
sqlite3 databases/arrow_database.db ".tables" | grep pending
# Should show: user_pending_manufacturers

# If tables are missing, run migration 046
cd arrow_scraper && python migrations/046_create_manufacturer_approval_system.py

# Verify tables were created
sqlite3 databases/arrow_database.db ".schema pending_manufacturers"

# Check for pending manufacturers
sqlite3 databases/arrow_database.db "SELECT * FROM pending_manufacturers WHERE status = 'pending'"
```
This issue was resolved in August 2025 - migration 046 creates the required manufacturer approval workflow tables.

**Docker Issues:**
```bash
# Clean up orphan containers
./docker-cleanup.sh

# Check container logs
docker-compose logs api
docker-compose logs frontend

# Restart services
docker-compose down
docker-compose up -d --build
```

### Production Issues

**SSL Certificate Problems:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Test SSL configuration
curl -I https://yourdomain.com
```

**Database Persistence:**
```bash
# Check Docker volumes
docker volume ls | grep arrowtuner

# Backup before fixing
./backup-databases.sh

# Verify volume mounts
docker inspect arrowtuner-api-enhanced
```

**Performance Issues:**
```bash
# Check system resources
docker stats

# Database query performance
cd arrow_scraper && python -c "
import time
from arrow_database import ArrowDatabase
db = ArrowDatabase()
start = time.time()
results = db.search_arrows({})
print(f'Query took {time.time() - start:.2f}s, {len(results)} results')
"

# Memory usage
free -h
df -h
```

### Logging and Monitoring

**Development Logs:**
```bash
# Backend logs
tail -f logs/api.log

# Frontend logs (browser console)
# Docker logs
docker-compose logs -f api
docker-compose logs -f frontend
```

**Production Monitoring:**
```bash
# Health check endpoints
curl https://yourdomain.com/api/health
curl https://yourdomain.com/api/simple-health

# System monitoring
htop
docker stats
df -h /var/lib/docker
```

---

## Best Practices

### Security
- Never commit API keys or secrets to Git
- Use environment variables for all configuration
- Validate all user inputs on both frontend and backend
- Implement proper JWT token expiration
- Use HTTPS in production
- Regular security updates for dependencies

### Performance  
- Implement proper database indexing
- Use pagination for large datasets
- Optimize images and use CDN
- Implement caching where appropriate
- Monitor query performance
- Use Docker resource limits

### Maintainability
- Follow consistent code style
- Write descriptive commit messages  
- Document all major functions and classes
- Use TypeScript for type safety
- Implement comprehensive error handling
- Regular dependency updates

### Data Management
- Regular database backups
- Separate user data from application data
- Version control for database schema changes
- Data validation at multiple layers
- Graceful handling of missing data

This development guide should help new developers quickly understand the system architecture and contribute effectively to the Archery Tools platform.