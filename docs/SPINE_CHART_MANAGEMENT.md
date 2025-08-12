# Spine Chart Management System

## Overview

The Spine Chart Management System provides comprehensive administration capabilities for managing manufacturer spine charts and creating custom spine charts with full editing capabilities. This system enables archery professionals to maintain accurate spine recommendations and create specialized charts for specific needs.

## Table of Contents

- [System Architecture](#system-architecture)
- [Admin Interface](#admin-interface)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Frontend Components](#frontend-components)
- [Production Deployment](#production-deployment)
- [Migration Guide](#migration-guide)

## System Architecture

### Database Tables

The spine chart system uses two primary tables:

1. **`manufacturer_spine_charts_enhanced`** - Read-only manufacturer spine chart data
2. **`custom_spine_charts`** - User-created and editable spine charts

### Key Features

- **View & Edit Functionality**: Comprehensive modal interfaces for chart inspection and modification
- **Spine Grid Editor**: Interactive table editor for individual spine entries
- **Manufacturer Overrides**: Create editable copies of manufacturer charts
- **Permission System**: Role-based access with admin authentication
- **Data Validation**: Form validation and confirmation dialogs

## Admin Interface

### Access
- **URL**: `/admin` (requires admin authentication)
- **Tab**: "Spine Calculator Data"
- **Permissions**: Admin users only (JWT token authentication required)

### Features

#### Chart Library Management
- **Filter System**: Filter by chart type, manufacturer, bow type, and search terms
- **Statistics Dashboard**: View chart counts and distribution
- **Action Buttons**: View, Edit, Copy (override), and Delete operations

#### View Modal
- **Chart Information**: Complete chart metadata display
- **Spine Grid Visualization**: Interactive table showing all spine recommendations
- **Chart Notes & Provenance**: Source information and detailed notes
- **Professional Presentation**: Clean layout with color-coded sections

#### Edit Modal
- **Basic Chart Info**: Edit manufacturer, model, bow type, spine system
- **Chart Notes**: Multi-line text editing for detailed descriptions
- **Active Status**: Toggle chart availability for calculations
- **Spine Grid Editor**: Full CRUD operations on individual spine entries

#### Spine Grid Editor
- **Add Entry**: Create new spine recommendations with default values
- **Edit Inline**: Direct table editing of draw weights, lengths, and spine values
- **Remove Entry**: Delete individual entries with confirmation
- **Sort Entries**: Automatic sorting by draw weight ranges
- **Clear All**: Bulk delete with confirmation dialog
- **Data Validation**: Input validation for professional archery standards

## API Endpoints

### Authentication Required
All admin endpoints require JWT token authentication with admin privileges.

### Chart Management

#### `GET /api/admin/spine-charts`
Get all spine charts (manufacturer + custom) for admin interface.

**Response Format:**
```json
{
  "manufacturer_charts": [
    {
      "chart_type": "manufacturer",
      "id": 1,
      "manufacturer": "Easton",
      "model": "X10 Protour",
      "bow_type": "compound", 
      "spine_system": "standard_deflection",
      "chart_notes": "Professional target arrows...",
      "provenance": "Easton Official Charts 2025",
      "is_active": true,
      "created_at": "2025-08-12T10:00:00",
      "spine_grid": [
        {
          "draw_weight_range_lbs": "40-45",
          "arrow_length_in": 28,
          "spine": "400",
          "arrow_size": "2014"
        }
      ],
      "grid_definition": {
        "length_unit": "in",
        "spine_system": "standard_deflection",
        "unit": "lbs"
      }
    }
  ],
  "custom_charts": [...],
  "total_charts": 25
}
```

#### `PUT /api/admin/spine-charts/custom/<int:chart_id>`
Update custom spine chart data including spine grid entries.

**Request Body:**
```json
{
  "manufacturer": "Custom Archery",
  "model": "Pro Series",
  "bow_type": "compound",
  "spine_system": "standard_deflection", 
  "chart_notes": "Custom spine chart for...",
  "is_active": true,
  "spine_grid": [
    {
      "draw_weight_range_lbs": "45-50",
      "arrow_length_in": 29,
      "spine": "350-400",
      "arrow_size": ""
    }
  ],
  "grid_definition": {
    "length_unit": "in", 
    "unit": "lbs"
  }
}
```

#### `DELETE /api/admin/spine-charts/custom/<int:chart_id>`
Delete a custom spine chart (manufacturer charts cannot be deleted).

#### `POST /api/admin/spine-charts/manufacturer/<int:chart_id>/override`
Create an editable custom chart based on manufacturer chart data.

**Response:**
```json
{
  "message": "Custom override chart created successfully",
  "custom_chart_id": 15
}
```

## Database Schema

### manufacturer_spine_charts_enhanced

```sql
CREATE TABLE manufacturer_spine_charts_enhanced (
    id INTEGER PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    bow_type TEXT NOT NULL,
    grid_definition TEXT,  -- JSON
    spine_grid TEXT,       -- JSON array
    provenance TEXT,
    spine_system TEXT,
    chart_notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### custom_spine_charts

```sql
CREATE TABLE custom_spine_charts (
    id INTEGER PRIMARY KEY,
    chart_name TEXT NOT NULL,
    manufacturer TEXT,
    model TEXT,
    bow_type TEXT NOT NULL,
    grid_definition TEXT,  -- JSON
    spine_grid TEXT,       -- JSON array  
    spine_system TEXT,
    chart_notes TEXT,
    created_by TEXT,
    overrides_manufacturer_chart BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Spine Grid JSON Format

```json
[
  {
    "draw_weight_range_lbs": "40-50",
    "arrow_length_in": 28,
    "spine": "400",
    "arrow_size": "2014"
  },
  {
    "draw_weight_range_lbs": "51-60", 
    "arrow_length_in": 28,
    "spine": "350-370",
    "arrow_size": "2016"
  }
]
```

## Frontend Components

### SpineChartLibrary.vue
Main admin component for spine chart management.

**Key Features:**
- Chart library with filtering and search
- Statistics dashboard with chart counts
- Action buttons for CRUD operations
- Modal interfaces for view and edit

**Props:**
- No required props (self-contained)

**Events:**
- Chart operations handled internally via API calls
- Auto-refresh after modifications

### Modal Interfaces

#### View Modal
- **Purpose**: Display complete chart information
- **Features**: Spine grid visualization, metadata display
- **Access**: Available for all charts (manufacturer + custom)

#### Edit Modal  
- **Purpose**: Edit chart metadata and spine grid data
- **Features**: Form validation, permission-based editing
- **Access**: Full editing for custom charts, read-only for manufacturer charts

### Spine Grid Editor

**Interactive Table Features:**
- Direct inline editing of spine entries
- Add/remove individual entries  
- Sort and bulk operations
- Input validation and formatting

**Data Validation:**
- Draw weight format: "40-50" or "45" 
- Arrow length: Decimal precision (28.0, 28.5)
- Spine values: Single (400) or range (350-400)
- Arrow size: Optional aluminum codes (2314, 1916)

## Production Deployment

### Migration Requirements

The spine chart system requires database migrations to be applied during production updates.

#### Required Migrations:
1. **Enhanced Spine Tables**: Create manufacturer_spine_charts_enhanced and custom_spine_charts tables
2. **Spine Calculator Data Import**: Import manufacturer spine charts from JSON files
3. **Conversion Tables**: Import spine conversion data for carbon/aluminum/wood systems

### Deployment Command
```bash
./start-unified.sh ssl archerytool.online
```

The unified deployment script automatically handles:
- Database schema migrations
- Spine calculator data import
- Frontend build with new components
- API server restart with new endpoints

### Migration Verification

The system includes automatic migration detection:
- Checks for required tables on startup
- Imports spine calculator data if tables are missing
- Verifies data integrity before starting services

## Migration Guide

### Development to Production

When deploying spine chart updates to production:

1. **Local Development**
   ```bash
   # Import spine calculator data locally
   cd arrow_scraper
   python spine_calculator_data_importer.py
   ```

2. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add comprehensive spine chart management system with editing capabilities"
   git push
   ```

3. **Production Deployment**
   ```bash
   # On production server
   git pull
   ./start-unified.sh ssl archerytool.online
   ```

### New Installation

For fresh installations, the spine calculator data is automatically imported during first startup.

### Data Backup

Before major updates, create a backup:
```bash
# Create backup with spine chart data
./backup-databases.sh --name spine_chart_system_backup
```

## Troubleshooting

### Common Issues

#### API 500 Errors
- **Cause**: Missing spine calculator tables
- **Solution**: Run `python spine_calculator_data_importer.py`

#### Missing Spine Grid Data
- **Cause**: API not returning spine_grid field
- **Solution**: Verify enhanced tables exist and contain data

#### Permission Errors
- **Cause**: Non-admin users accessing admin endpoints
- **Solution**: Verify JWT token and admin privileges

### Debug Commands

```bash
# Check spine tables exist
python -c "import sqlite3; conn=sqlite3.connect('databases/arrow_database.db'); print([t[0] for t in conn.execute(\"SELECT name FROM sqlite_master WHERE name LIKE '%spine%'\").fetchall()])"

# Verify spine calculator data
python -c "import sqlite3; conn=sqlite3.connect('databases/arrow_database.db'); print(f'Charts: {conn.execute(\"SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced\").fetchone()[0]}')"

# Test API endpoints
curl -s http://localhost:5000/api/calculator/manufacturers
```

## Performance Considerations

### Database Optimization
- **Indexes**: Added on manufacturer, bow_type, and is_active columns
- **JSON Queries**: Efficient spine_grid searching using SQLite JSON functions
- **Connection Pooling**: Proper connection management for concurrent access

### Frontend Performance
- **Lazy Loading**: Chart data loaded on-demand
- **Virtual Scrolling**: Large chart lists use virtual scrolling
- **Caching**: Chart library data cached during session

### API Performance
- **Query Optimization**: Efficient SQL queries with minimal data transfer
- **Response Compression**: JSON responses compressed for large datasets
- **Error Handling**: Comprehensive error handling prevents system slowdowns

## Security

### Authentication
- **JWT Tokens**: Secure token-based authentication
- **Admin Requirements**: All spine chart operations require admin privileges
- **Session Management**: Proper token expiration and renewal

### Data Validation
- **Input Sanitization**: All user inputs properly sanitized
- **SQL Injection Protection**: Parameterized queries throughout
- **XSS Prevention**: Frontend input validation and escaping

### Access Control
- **Role-Based Access**: Admin-only functionality properly protected
- **Read-Only Protection**: Manufacturer charts cannot be modified
- **Audit Trail**: All chart modifications logged with user information