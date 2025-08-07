# Documentation Archive Index

This archive contains legacy documentation that has been replaced by the new comprehensive documentation suite. These files are preserved for historical reference and may contain useful information for understanding the project's evolution.

## Archive Organization

### Legacy Production Documentation (`legacy-production/`)
Files related to production deployment, Docker, and operational procedures that have been superseded by the new [Development Guide](../DEVELOPMENT_GUIDE.md).

- `PRODUCTION_DEPLOYMENT.md` - Original production deployment guide
- `PRODUCTION_DEPLOYMENT_SUMMARY.md` - Summary of production setup procedures  
- `PRODUCTION_SETUP.md` - Production environment configuration
- `PRODUCTION_MATERIALS.md` - Production materials and requirements
- `PRODUCTION-RESET-GUIDE.md` - Production reset procedures
- `PRODUCTION_FIXES.md` - Production issue fixes and workarounds
- `PRODUCTION_TROUBLESHOOTING.md` - Production troubleshooting guide
- `PRODUCTION_DATABASE_VERIFICATION.md` - Database verification procedures
- `DOCKER_DEPLOYMENT.md` - Docker deployment procedures
- `DOCKER_TROUBLESHOOTING.md` - Docker troubleshooting guide
- `README-DUAL-ARCHITECTURE.md` - Dual architecture documentation

### Legacy Development Documentation (`legacy-development/`)
Development guides, beta checklists, and migration documentation replaced by the new [Development Guide](../DEVELOPMENT_GUIDE.md).

- `DEVELOPMENT.md` - Original development setup guide
- `BETA-RELEASE-CHECKLIST.md` - Beta release preparation checklist
- `UNIFIED_MIGRATION_GUIDE.md` - Migration procedures
- `ADMIN_PANEL_FIXES.md` - Admin panel bug fixes and improvements
- `BACKUP_RESTORE_DOCUMENTATION.md` - Backup and restore procedures
- `DEEPSEEK_API.md` - DeepSeek API integration documentation
- `guide-illustrations.md` - Guide illustration documentation
- `PROJECT_PLAN.md` - Original project planning documentation
- `SPINE_CALCULATION_ANALYSIS.md` - Spine calculation analysis and testing
- `OLD_README.md` - Original docs README file

### Legacy Database Documentation (`legacy-database/`)
Database-related documentation that has been consolidated into the new [Database Schema Documentation](../DATABASE_SCHEMA.md).

- `COMPONENT_DATABASE.md` - Component database documentation
- `DATABASE_FIXTURES.md` - Database fixtures and test data
- `DATABASE_PERSISTENCE.md` - Database persistence documentation
- `DATABASE_CLEANUP.md` - Database cleanup procedures
- `DATABASE_CLEANER_GUIDE.md` - Database cleaning and maintenance guide
- `DATABASE_IMPORT_SYSTEM.md` - Database import system documentation

### Legacy Scraping Documentation (`legacy-scraping/`)
Web scraping, manufacturer analysis, and data extraction documentation. Core scraping functionality is still active but configuration guides have been archived.

- `SCRAPER_CONFIGURATION.md` - Scraper configuration guide
- `MANUFACTURER_MANAGEMENT.md` - Manufacturer management procedures
- `COMPONENT_SCRAPING_GUIDE.md` - Component scraping guide
- `MANUFACTURER_ANALYSIS.md` - Manufacturer website analysis
- `MANUFACTURER_EXTRACTION_GUIDE.md` - Data extraction procedures
- `SCRAPER_ENHANCEMENT_PLAN.md` - Scraper enhancement planning
- `UPDATE_GUIDE.md` - Scraper update procedures
- `URL_UPDATE_GUIDE.md` - URL update and maintenance guide
- `TOPHAT_ARCHERY_SCRAPER.md` - TopHat Archery scraper documentation
- `TOPHAT_IMPORT_GUIDE.md` - TopHat import procedures

## Current Active Documentation

The following documentation replaces all archived files:

### Primary Documentation
1. **[docs/README.md](../README.md)** - Main documentation index and overview
2. **[docs/DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md)** - Complete database structure
3. **[docs/API_ENDPOINTS.md](../API_ENDPOINTS.md)** - All REST API endpoints
4. **[docs/DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - Architecture and workflows

### Project Context
- **[CLAUDE.md](../../CLAUDE.md)** - Project context for AI assistance
- **[README.md](../../README.md)** - Main project README

## Archive Notes

- **Date Archived**: 2025-08-07
- **Reason**: Replaced by comprehensive documentation suite
- **Migration Status**: All essential information consolidated into new documentation
- **Retention**: Files preserved for historical reference and context

## Accessing Archived Information

If you need information from archived documentation:

1. **Check New Documentation First**: Most information has been migrated and improved
2. **Search Archive**: Use `grep -r "search_term" docs/archive/` to find specific information
3. **Historical Context**: These files show the project's evolution and decision-making process
4. **Troubleshooting**: Some specific fixes or edge cases may only be documented in archived files

## Migration Notes

The new documentation suite provides:
- **Better Organization**: Logical grouping and cross-references
- **Complete Coverage**: All aspects of the system in one place
- **Current Information**: Up-to-date with latest system architecture
- **Developer Focus**: Optimized for new developer onboarding
- **Maintenance**: Easier to keep documentation current with code changes

Legacy documentation was comprehensive but scattered across multiple files with some duplication and outdated information. The new consolidated approach provides a single source of truth for system documentation.