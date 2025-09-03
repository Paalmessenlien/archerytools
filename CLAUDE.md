# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Archery Tools project that scrapes arrow specifications from manufacturer websites and provides professional tuning calculations for archery equipment. The project has completed all development phases (1-9) and is **READY FOR BETA TESTING** with a production-ready full-stack archery tools platform featuring modern UI/UX.

**📚 COMPREHENSIVE DOCUMENTATION AVAILABLE:**
- **[Complete Documentation Index](docs/INDEX.md)** - Overview of all documentation
- **[Database Schema Documentation](docs/DATABASE_SCHEMA.md)** - Complete database structure, tables, relationships
- **[API Endpoints Documentation](docs/API_ENDPOINTS.md)** - All REST endpoints with request/response examples  
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)** - Architecture, workflows, and troubleshooting
- **[Database Migrations Documentation](docs/DATABASE_MIGRATIONS.md)** - Complete migration system guide with examples
- **[Spine Data System Documentation](docs/SPINE_DATA_SYSTEM.md)** - Advanced spine calculation system and admin interface
- **[Archery Calculations Guide](docs/ARCHERY_CALCULATIONS_GUIDE.md)** - Professional physics calculations and optimization algorithms

**🚀 For new developers**: Start with [Development Guide](docs/DEVELOPMENT_GUIDE.md) for environment setup and architecture overview.

**Technology Stack:**
- **Web Scraping**: Crawl4AI + DeepSeek API for intelligent content extraction
- **Database**: SQLite with comprehensive arrow specifications and relationships  
- **Backend**: Flask (Python) API-only server with RESTful endpoints
- **Frontend**: Nuxt 3 (Vue.js) + Tailwind CSS + TypeScript + Pinia state management
- **UI Components**: Material Web Components with custom styling and dark mode support
- **Calculations**: Advanced spine calculation, tuning optimization, and arrow matching engines
- **Architecture**: Modern SPA frontend with API backend (dual deployment)

## Recent Major Updates (2025):
- ✅ **Per-Bow-Type System Defaults**: Complete implementation of material-aware spine chart defaults specific to each bow type with edit-based management ([Details](docs/SPINE_CHART_SYSTEM_DEFAULTS_IMPLEMENTATION.md))
- ✅ **Manufacturer Active Status Filtering System**: Complete filtering system to hide arrows from inactive manufacturers while preserving admin access and existing configurations ([Details](docs/MANUFACTURER_ACTIVE_STATUS_SYSTEM.md))
- ✅ **Wood Arrow Species Import & Calculator Integration**: Comprehensive import of 6 traditional wood arrow species with 54+ spine specifications, traditional archery calculations, and full calculator integration (Migrations 047-050)
- ✅ **Manufacturer Approval System Fix**: Fixed pending manufacturer creation in bow setup forms not appearing in admin approval queue (August 2025)
- ✅ **Draw Length Unification & Speed System Fix**: Comprehensive fix for draw length management confusion and speed calculation issues ([Details](docs/DRAW_LENGTH_UNIFICATION_FIX.md))
- ✅ **Journal Enhancement Phase 6**: Advanced integration & system consolidation with unified change history ([Details](docs/JOURNAL_ENHANCEMENT_PHASE6.md))
- ✅ **Journal Enhancement Phase 5**: Complete advanced features implementation with templates, analytics, and export ([Details](docs/JOURNAL_ENHANCEMENT_PHASE5.md))
- ✅ **Professional Archery Calculations System**: Complete overhaul with industry-accurate formulas and optimization algorithms ([Details](docs/ARCHERY_CALCULATIONS_GUIDE.md))
- ✅ **Chronograph Data Integration**: Complete system for measured arrow speeds ([Details](docs/CHRONOGRAPH_DATA_SYSTEM.md))
- ✅ **Enhanced Equipment Management**: 8 equipment categories with auto-learning manufacturer detection ([Details](docs/ENHANCED_EQUIPMENT_MANAGEMENT.md))
- ✅ **Unified Database Architecture**: Complete consolidation from dual to single database ([Details](docs/UNIFIED_DATABASE_ARCHITECTURE.md))
- ✅ **Mobile UX Enhancement**: Comprehensive mobile-first design improvements ([Details](docs/MOBILE_UX_PHASE3_COMPLETION.md))
- ✅ **Admin Panel & Database Management**: Complete maintenance interface with health monitoring ([Details](docs/ADMIN_PANEL_DATABASE_MANAGEMENT.md))

## Quick Start Commands

### 🚀 Unified Startup System (Recommended)

**All deployment scenarios are handled by the unified `start-unified.sh` script:**

```bash
./start-unified.sh --help              # Show comprehensive help and documentation
```

**🔧 Development Modes:**
```bash
# Local development (no Docker) - Recommended for frontend development
./start-unified.sh dev start           # Start API and frontend locally
./start-unified.sh dev stop            # Stop local development services

# Docker development - Recommended for backend development  
./start-unified.sh                     # Start full Docker development environment
```

**🚀 Production Modes:**
```bash
# Production HTTP mode (for local testing)
./start-unified.sh production start    # Start production environment locally
./start-unified.sh production stop     # Stop production services

# Production SSL mode (for live deployment)
./start-unified.sh ssl yourdomain.com  # Deploy with SSL certificates
```

**🛑 Stopping Services:**
```bash
./start-unified.sh dev stop            # Stop local development
./start-unified.sh production stop     # Stop production services
./stop-unified.sh                      # Stop any unified mode services
```

**🌐 Access URLs:**
- **Local Development**: http://localhost:3000 (frontend), http://localhost:5000/api (API)
- **Production SSL**: https://yourdomain.com (frontend), https://yourdomain.com/api (API)

## Environment Configuration

Create `.env` file in root directory:
```
# API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SECRET_KEY=your-secret-key-here-change-this
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# Frontend Configuration
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id-here
NUXT_PUBLIC_API_BASE=http://localhost:5000

# Production Domain
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

## Database Architecture

**Unified Database System (August 2025):**
- ✅ **Single Database** (`arrow_database.db`): ALL data consolidated - arrows, users, bow setups, equipment, and components
- ✅ **UnifiedDatabase Class**: Single interface for all database operations
- ✅ **Migration Complete**: User data successfully consolidated from user_data.db
- ✅ **Backup System**: Professional-grade backup and restore functionality for single database

**Key Locations:**
- **Development**: `./databases/arrow_database.db` (unified architecture)
- **Production**: `/app/databases/arrow_database.db` (Docker volumes - unified architecture)

## Important Notes

### Current Platform Status (2025)
- **Production-Ready Platform:** Complete archery tools solution with modern UI/UX and admin system
- **Modern Architecture:** Nuxt 3 SPA frontend + Flask API backend with dual deployment
- **Material Design 3:** Professional UI with Google's latest design system and dark mode
- **Advanced Filtering:** Sophisticated search with manufacturer, spine, diameter, and weight filters
- **Database Statistics:** Real-time metrics showing 13 manufacturers with 197+ arrow models
- **Admin System:** Complete user management with automatic admin privileges for messenlien@gmail.com
- **User Authentication:** Google OAuth integration with secure JWT tokens and profile management

### Technical Capabilities
- **Multi-language Support:** Handles English, German, and Italian manufacturer websites
- **Professional Calculations:** Implements industry-standard spine and tuning formulas
- **Comprehensive Database:** Contains 400+ arrow specifications across 13 manufacturers
- **Session Management:** Persistent tuning sessions with detailed recommendations
- **CDN Integration:** Automatic image upload to Cloudinary, AWS S3, or other CDNs for optimized delivery

### System Capabilities
The Archery Tools platform provides:
1. **Professional spine calculations** based on bow specifications and shooting style
2. **Intelligent arrow recommendations** with confidence scoring and alternatives  
3. **Advanced tuning optimization** including FOC, kinetic energy, and momentum calculations
4. **Comprehensive database search** with filtering by manufacturer, spine, diameter, and GPI
5. **Visual arrow comparison** with detailed specification analysis
6. **Multiple concurrent tuning sessions** with pause/resume functionality and progress tracking
7. **Advanced journal system** with templates, rich text editing, equipment linking, and change history integration
8. **Unified change history** tracking all equipment, setup, and arrow modifications with statistics
9. **Professional content creation** with CDN image uploads, universal tag management, and advanced filtering
10. **Modern web interface** with Material Design 3 components and dark mode
11. **API endpoints** for integration with other archery tools
12. **Complete admin system** with automatic privilege assignment and user management
13. **Enhanced equipment management** with 8 equipment categories and auto-learning capabilities

## Development & Troubleshooting

For detailed information on:
- **Environment Setup**: See [Development Guide](docs/DEVELOPMENT_GUIDE.md)
- **Database Operations**: See [Database Schema](docs/DATABASE_SCHEMA.md) and [Migration Guide](docs/DATABASE_MIGRATIONS.md)
- **API Usage**: See [API Endpoints Documentation](docs/API_ENDPOINTS.md)
- **Journal System**: See [Phase 6 Enhancements](docs/JOURNAL_ENHANCEMENT_PHASE6.md) and [Phase 5 Features](docs/JOURNAL_ENHANCEMENT_PHASE5.md)
- **Production Deployment**: See [CI/CD Deployment Guide](docs/CICD_DEPLOYMENT_GUIDE.md)
- **Troubleshooting**: See individual documentation files for specific issues
- **Mobile Development**: See [Mobile UX Documentation](docs/MOBILE_UX_PHASE3_COMPLETION.md)
- **Admin Panel**: See [Admin Panel Documentation](docs/ADMIN_PANEL_DATABASE_MANAGEMENT.md)

## Project Status

**READY FOR BETA TESTING** - Complete archery tools platform with modern UI/UX, professional calculations, and comprehensive admin system. All development phases completed with production-ready deployment infrastructure.

---

*This is a streamlined reference guide. For detailed documentation, see the comprehensive docs folder starting with [docs/INDEX.md](docs/INDEX.md).*