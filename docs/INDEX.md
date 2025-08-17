# Archery Tools Documentation

Comprehensive documentation for the Archery Tools platform - a professional archery equipment database and tuning system.

## Documentation Overview

This documentation provides everything needed to understand, develop, and maintain the Archery Tools platform.

### 📚 Core Documentation

#### [Database Schema Documentation](DATABASE_SCHEMA.md)
Complete database structure including:
- **Unified Database Architecture**: Single consolidated database (arrow_database.db) with both arrow and user data
- **Database Consolidation**: Automatic migration from separate to unified architecture  
- **Table Structures**: All tables with field definitions, constraints, and relationships
- **Data Types & Formats**: Normalized values, JSON fields, and measurement units
- **Indexes & Performance**: Database optimization and query performance
- **Migration Scripts**: Schema updates, consolidation migrations, and backup procedures

#### [Unified Database Architecture](UNIFIED_DATABASE_ARCHITECTURE.md) ✨ NEW
Comprehensive documentation of the unified database consolidation:
- **Migration History**: From dual-database to unified architecture
- **Migration Process**: Detailed steps for consolidation (migrations 023 & 024)
- **Complete Schema**: All user and arrow tables in unified database
- **Code Updates**: UnifiedDatabase class usage and API updates
- **Benefits**: Performance improvements and simplified architecture
- **Verification**: Data integrity checks and rollback procedures

#### [API Endpoints Documentation](API_ENDPOINTS.md)
Comprehensive REST API reference including:
- **Authentication**: Google OAuth + JWT token system
- **Arrow Database APIs**: Search, filtering, and detailed specifications
- **Bow Setup Management**: CRUD operations for user bow configurations
- **Tuning & Calculations**: Spine calculations and arrow recommendations
- **Admin Panel**: User management, arrow editing, and backup system
- **Request/Response Examples**: Complete examples for all endpoints

#### [Development Guide & Architecture](DEVELOPMENT_GUIDE.md)
Complete development workflow documentation:
- **System Architecture**: High-level overview and technology stack
- **Development Environment**: Setup, prerequisites, and configuration
- **Project Structure**: File organization and component relationships
- **Development Workflows**: Feature development, testing, and deployment
- **Troubleshooting**: Common issues and solutions

#### [Spine Data System Documentation](SPINE_DATA_SYSTEM.md)
Comprehensive spine calculation system documentation:
- **Database Schema**: 7 specialized tables for calculation parameters and material properties
- **Admin Interface**: `/admin/spine-data` management panel for parameter configuration
- **Service Integration**: Unified spine service architecture and API endpoints
- **Automatic Migration**: Startup script integration and data initialization
- **Usage Examples**: Frontend and backend integration patterns

#### [Database Migrations Documentation](DATABASE_MIGRATIONS.md)
Complete guide to the database migration system:
- **Migration Architecture**: Versioned migrations with dependency management
- **Creating Migrations**: Step-by-step guide for new migrations
- **User vs Arrow Database**: Target-specific migration patterns
- **Production Deployment**: Safe migration procedures and rollback strategies
- **Admin Integration**: Web-based migration management and monitoring

#### [Migration Reference Guide](MIGRATION_REFERENCE.md) ⭐
**NEW:** Comprehensive reference for all 16 existing migrations:
- **Complete Migration Catalog**: Detailed documentation of migrations 001-016
- **Migration Dependencies**: Understanding the dependency chain and relationships
- **What Each Migration Does**: Tables created, fields added, data transformations
- **Why Each Migration Exists**: Business logic and technical reasoning
- **Creating New Migrations**: Templates, patterns, and best practices

#### [Migration Quick Reference](MIGRATION_CHEATSHEET.md) ⭐
**NEW:** Quick reference for daily migration tasks:
- **Common Commands**: Status checking, running migrations, troubleshooting
- **Migration Summary Table**: All migrations with purpose and database targets
- **Code Patterns**: Common migration templates and SQL patterns
- **Admin Panel Usage**: Web-based migration management
- **Production Checklist**: Pre-deployment verification steps

#### [Migration System Fixes Documentation](MIGRATION_SYSTEM_FIXES.md) 🔧
**August 2025:** Complete resolution of production migration discovery issues:
- **Problem Analysis**: Why only 11 of 16 migrations were discovered in production
- **Technical Solution**: Enhanced migration manager supporting 4 different migration patterns
- **Docker Integration**: Fixes for containerized deployment migration execution
- **Test Results**: Validation of complete 16-migration discovery system
- **Future Guidelines**: Best practices for consistent migration development

#### [Enhanced Equipment Management System](ENHANCED_EQUIPMENT_MANAGEMENT.md) 
**⚡ Latest Update (August 2025)** - Comprehensive equipment management with auto-learning:
- **8 Equipment Categories**: Professional system including Scope, Plunger, and Other categories
- **Smart Auto-Learning**: Intelligent manufacturer detection with fuzzy matching and confidence scoring
- **Dynamic Form Schemas**: 46 field definitions with category-specific validation and help text
- **API Enhancements**: Form schema generation, manufacturer suggestions, and learning endpoints
- **Frontend Integration**: Updated EquipmentSelector with all 8 categories and professional icons
- **Database Evolution**: Enhanced equipment_field_standards with manufacturer_equipment_categories table
- **Comprehensive Testing**: Full test suite validating auto-learning and end-to-end functionality

#### [Custom Equipment Management System](CUSTOM_EQUIPMENT_SYSTEM.md)
**📋 Legacy Documentation** - Original 5-category system documentation:
- **Dynamic Form Generation**: Category-based form fields with validation and autocomplete
- **Database Schema**: Equipment field standards and enhanced bow_equipment table
- **API Endpoints**: Form schema generation and manufacturer suggestions
- **Frontend Components**: CustomEquipmentForm.vue and equipment management integration
- **Equipment Categories**: 5 equipment types with 30+ standardized fields
- **Migration Support**: Database migrations 008 and 009 for custom equipment

#### [Smart Manufacturer Matching System](SMART_MANUFACTURER_MATCHING.md)
Intelligent manufacturer detection and linking system:
- **Fuzzy String Matching**: Multiple algorithms with confidence scoring (0.0-1.0)
- **Manufacturer Aliases**: Recognizes 100+ common name variations and abbreviations
- **Category Specialization**: Prioritizes manufacturers known for specific equipment types
- **Smart Linking**: Automatic high-confidence manufacturer linking (≥80% threshold)
- **Enhanced Autocomplete**: Intelligent suggestions with category-aware ranking
- **Quality Improvement**: Standardizes manufacturer names for data consistency

#### [Chronograph Data System Documentation](CHRONOGRAPH_DATA_SYSTEM.md) ⚡
**NEW (August 2025)** - Comprehensive measured arrow speed integration:
- **Database Schema**: Complete chronograph_data table with measurement tracking
- **API Endpoints**: Full CRUD operations for chronograph data management
- **Frontend Component**: ChronographDataEntry.vue for data collection and display
- **Performance Integration**: Automatic integration with arrow performance calculations
- **Data Priority**: Measured speeds prioritized over estimated calculations
- **Real-time Updates**: Performance recalculation when measurements change

#### [Enhanced Arrow Speed Calculations](ENHANCED_ARROW_SPEED_CALCULATIONS.md) ⚡
**NEW (August 2025)** - Sophisticated arrow velocity estimation system:
- **Calculation Hierarchy**: Chronograph data → Enhanced estimation → Basic fallback
- **String Material Integration**: Speed modifiers for 6 string materials (Dacron to SK75)
- **Bow Type Efficiency**: Compound (95%) to Traditional (70%) efficiency factors
- **IBO-Based Calculations**: Enhanced formulas with weight/length adjustments
- **Weight Adjustment**: Kinetic energy conservation for different arrow weights
- **Confidence Scoring**: 50-100% confidence levels based on data quality

#### [String Equipment Integration](STRING_EQUIPMENT_INTEGRATION.md) ⚡
**NEW (August 2025)** - Complete string equipment management with speed integration:
- **Enhanced Equipment Fields**: 7 string-specific fields including material and speed rating
- **Speed Calculation Integration**: Automatic string material detection for calculations
- **Material Speed Modifiers**: Dacron (-8%) to SK75 Dyneema (+4%) speed effects
- **Equipment Form Enhancement**: Dynamic forms with string-specific validation
- **Database Migration**: Migration 020 for enhanced string equipment fields
- **Frontend Integration**: Automatic material detection in calculator and performance pages

---

## Quick Reference

### Database Locations
- **Development**: `./databases/arrow_database.db` (unified architecture)
- **Production**: `/app/databases/arrow_database.db` (Docker volumes - unified architecture)
- **Legacy**: Separate user_data.db files (automatically migrated to unified)

### Key API Endpoints
- **Health Check**: `GET /api/health`
- **Arrow Search**: `GET /api/arrows?manufacturer=Easton&spine_min=300`
- **User Profile**: `GET /api/user`
- **Bow Setups**: `GET /api/bow-setups`
- **Spine Calculation**: `POST /api/tuning/calculate-spine`
- **Admin Spine Data**: `GET /api/admin/spine-data/parameters`

### Development Commands
```bash
# Start development environment
./start-local-dev.sh start

# Stop development environment
./start-local-dev.sh stop

# Check service status
./start-local-dev.sh status

# Test backend
cd arrow_scraper && python test_api.py

# Test frontend
cd frontend && npm run dev
```

### Production Deployment
```bash
# Deploy with SSL
./start-unified.sh ssl yourdomain.com

# Verify deployment
python3 test-bow-saving.py
curl https://yourdomain.com/api/health
```

---

## Database Architecture Overview

### Unified Database Architecture (`arrow_database.db`)

**🎯 Consolidated Database (August 2025)**: All data in single unified database for improved performance and simplified management.

#### Arrow Data Tables
- **arrows**: Main arrow specifications (1,143+ models)
- **spine_specifications**: Detailed spine data for each arrow
- **components**: Arrow components (nocks, inserts, points)
- **component_categories**: Component organization
- **manufacturers**: Manufacturer information with enhanced metadata

#### User Data Tables (Consolidated)
- **users**: User accounts, authentication, and admin privileges
- **bow_setups**: User bow configurations with complete specifications
- **setup_arrows**: Arrow selections for each bow setup
- **guide_sessions**: Interactive guide progress and session data
- **bow_equipment**: Equipment configurations with enhanced string fields
- **chronograph_data**: Measured arrow speeds with environmental data
- **backup_metadata**: Backup system tracking and CDN integration

#### Spine Calculation Tables
- **calculation_parameters**: Admin-configurable calculation coefficients
- **arrow_material_properties**: Material characteristics and factors
- **manufacturer_spine_charts**: Brand-specific recommendations
- **flight_problem_diagnostics**: Troubleshooting guidance
- **tuning_methodologies**: Step-by-step tuning procedures

#### Migration & System Tables
- **schema_migrations**: Database migration tracking and versioning
- **equipment_field_standards**: Dynamic equipment form generation (46 field definitions)

---

## System Features

### Core Functionality
- **Arrow Database**: 1,143+ arrows from 13 manufacturers
- **Professional Calculations**: Industry-standard spine calculations with advanced parameter system
- **Spine Data System**: Admin-configurable calculation parameters and material properties
- **Intelligent Matching**: Arrow recommendations with compatibility scoring
- **User Management**: Google OAuth + JWT authentication
- **Bow Setup Management**: Personal equipment configurations
- **Interactive Guides**: Step-by-step tuning walkthroughs

### Technical Capabilities
- **Multi-language Support**: English, German, Italian manufacturers
- **Dark Mode**: Complete theme system with persistence
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: Live calculations and recommendations
- **Admin System**: Complete management interface
- **Backup & Restore**: Professional-grade data protection

---

## Recent Updates (2025)

### Major Enhancements
- ✅ **Bow Detail Pages**: Dedicated pages for bow setup management
- ✅ **Enhanced Navigation**: Seamless flow between calculator and setup pages
- ✅ **Arrow Management**: Add/remove arrows from bow setups with configuration
- ✅ **Admin System**: Complete user and arrow management interface
- ✅ **Backup System**: Professional database backup and restore functionality
- ✅ **Material Web Components**: Modern UI with Google's Material Design 3
- ✅ **Mobile/Tablet UX Optimization**: Comprehensive mobile-first design improvements
- ✅ **Calculator Interface Redesign**: Consolidated advanced filters and improved spacing
- ✅ **Documentation Consolidation**: Streamlined documentation with comprehensive INDEX.md

### Latest UI/UX Improvements (August 2025)
- ✅ **Spine Conversion Widget**: Fixed double header display issue in calculator
- ✅ **Advanced Filters Consolidation**: Moved all filters into Calculated Specifications section
- ✅ **Match Summary Optimization**: Compact design with reduced spacing and consistent styling
- ✅ **Calculator Spacing**: Systematic spacing optimization throughout calculator interface
- ✅ **Mobile Navigation**: Enhanced bottom navigation and touch-friendly interactions
- ✅ **Responsive Design**: Improved mobile/tablet experience across all components

### Admin Panel & Database Management (August 2025)
- ✅ **Unified Database Architecture**: Complete migration from dual to single database system
- ✅ **Enhanced Admin Panel**: Comprehensive maintenance interface with architecture detection
- ✅ **Database Health Monitoring**: Real-time performance scoring and integrity checking
- ✅ **Schema Verification**: Advanced verification supporting unified and separate architectures
- ✅ **Migration Management**: Visual migration status with applied/pending tracking
- ✅ **Database Maintenance**: VACUUM, ANALYZE, and optimization operations
- ✅ **Production Diagnostic Tools**: Robust scripts for production database troubleshooting

#### [Admin Panel & Database Management Documentation](ADMIN_PANEL_DATABASE_MANAGEMENT.md) 🔧
**NEW (August 2025)** - Comprehensive admin system and database management documentation:
- **Admin Panel Interface**: Complete web-based database management with Material Design 3
- **Database Health Monitoring**: Real-time performance scoring (0-100) with integrity checking
- **Migration Management System**: Visual migration control with dependency resolution
- **Schema Verification**: Advanced verification supporting unified and separate architectures
- **Maintenance Operations**: VACUUM, ANALYZE, and optimization with real-time progress
- **Production Diagnostic Tools**: Robust scripts for troubleshooting production database issues

### New Calculation System (August 2025)
- ✅ **Chronograph Data Integration**: Complete system for storing and utilizing measured arrow speeds
- ✅ **Enhanced Speed Calculations**: Sophisticated 3-tier calculation hierarchy with data priority
- ✅ **String Equipment Integration**: Automatic string material detection with speed modifiers
- ✅ **Performance Integration**: Real-time arrow performance updates with measured data
- ✅ **Database Migrations**: Migrations 019 & 020 for chronograph and string equipment enhancements
- ✅ **Frontend Components**: ChronographDataEntry.vue with full measurement management

### Bug Fixes & Improvements
- ✅ **UserDatabase Import Errors**: Fixed API endpoint import issues
- ✅ **Arrow Listing Display**: Fixed data extraction from API responses
- ✅ **Navigation Issues**: Corrected Add/Find Arrow button navigation
- ✅ **Authentication Flow**: Enhanced JWT token management
- ✅ **Database Persistence**: Improved Docker volume configuration
- ✅ **Component Header Duplication**: Resolved double "Spine Conversion Tool" headers
- ✅ **UI Component Organization**: Better separation of concerns between calculator and recommendation components

---

## Getting Started

### For Developers
1. Read [Development Guide](DEVELOPMENT_GUIDE.md) for environment setup
2. Review [Database Schema](DATABASE_SCHEMA.md) for data structure
3. Reference [API Documentation](API_ENDPOINTS.md) for endpoint usage
4. Check project structure in `/frontend/` and `/arrow_scraper/`

### For Administrators  
1. Use admin panel at `/admin` (requires admin privileges)
2. Review [API Documentation](API_ENDPOINTS.md) admin endpoints
3. Monitor system health via `/api/health` endpoint
4. Manage backups through admin interface

### For Users
1. Access platform at production URL
2. Authenticate via Google OAuth
3. Create bow setups in "My Page"
4. Use calculator for arrow recommendations
5. Browse database for arrow specifications

---

## Support & Maintenance

### Production Monitoring
- Health checks: `/api/health` and `/api/simple-health`
- Database integrity: `python verify-databases.py`
- Backup system: Admin panel backup interface
- Performance monitoring: Docker stats and resource usage

### Development Support
- Issue tracking: GitHub Issues
- Code style: Follow guidelines in Development Guide
- Testing: Comprehensive test suite included
- Documentation: Keep docs updated with code changes

### Data Updates
- Arrow data: JSON files in `data/processed/`
- Database migrations: Scripts in `arrow_scraper/`
- User data persistence: Docker volumes
- Backup procedures: Admin backup system

---

## Documentation Changes

### August 2025 Documentation Updates
- **Documentation Consolidation**: Removed outdated `README.md` file in favor of comprehensive `INDEX.md`
- **Recent Updates Section**: Added detailed changelog of latest UI/UX improvements
- **Mobile Optimization Documentation**: Documented recent mobile-first design enhancements
- **Component Architecture Updates**: Reflected recent calculator interface reorganization

---

This documentation is maintained alongside the codebase and should be updated with any significant system changes. For specific implementation details, refer to the individual documentation files linked above.