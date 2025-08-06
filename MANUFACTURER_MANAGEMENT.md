# Manufacturer Management System

## Overview

The Manufacturer Management System provides comprehensive CRUD (Create, Read, Update, Delete) operations for managing arrow manufacturers through the admin panel. This system includes cascade delete functionality, real-time statistics, and a responsive user interface.

## Features

### Admin Panel Integration
- **Navigation Tab**: Added "Manufacturers" tab to admin navigation with factory icon
- **Statistics Dashboard**: Real-time display of manufacturer count, total arrows, and averages
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Dark Mode Support**: Complete theming compatibility

### CRUD Operations

#### Create Manufacturer
- **Endpoint**: `POST /api/admin/manufacturers`
- **Functionality**: Creates new manufacturer with placeholder arrow
- **UI**: Modal form with validation and success feedback

#### Read Manufacturers
- **Endpoint**: `GET /api/admin/manufacturers`
- **Functionality**: Lists all manufacturers with statistics
- **Data Includes**:
  - Manufacturer name
  - Arrow count per manufacturer
  - First added date
  - Last updated date

#### Update Manufacturer
- **Endpoint**: `PUT /api/admin/manufacturers/<name>`
- **Functionality**: Updates manufacturer name across all associated arrows
- **Safety**: Shows impact warning with affected arrow count
- **URL Encoding**: Handles manufacturer names with special characters

#### Delete Manufacturer
- **Endpoint**: `DELETE /api/admin/manufacturers/<name>`
- **Functionality**: Cascade deletion of manufacturer and all associated data
- **Safety Features**:
  - Confirmation modal with detailed impact warning
  - Shows exact count of arrows to be deleted
  - Lists all data types that will be removed
  - Transaction rollback on any failure

## Technical Implementation

### Database Architecture
```sql
-- Manufacturers are stored as text values in the arrows table
-- No separate manufacturers table exists
-- Relationships managed through text matching

-- Cascade deletion order:
1. spine_specifications (foreign key: arrow_id)
2. arrows (manufacturer field)
```

### API Endpoints

#### GET /api/admin/manufacturers
```json
{
  "manufacturers": [
    {
      "name": "Easton",
      "arrow_count": 45,
      "first_added": "2024-01-15T10:30:00Z",
      "last_added": "2024-08-01T14:22:00Z"
    }
  ],
  "total_manufacturers": 19,
  "total_arrows": 121
}
```

#### POST /api/admin/manufacturers
```json
{
  "name": "New Manufacturer Name"
}
```

#### PUT /api/admin/manufacturers/<encoded_name>
```json
{
  "new_name": "Updated Manufacturer Name"
}
```

#### DELETE /api/admin/manufacturers/<encoded_name>
- Returns success/error status and affected record counts

### Frontend Component

#### AdminManufacturersTable.vue
- **Location**: `frontend/components/AdminManufacturersTable.vue`
- **Features**:
  - Statistics cards with real-time data
  - Data table with sortable columns
  - Create/Edit modals with form validation
  - Delete confirmation with cascade warnings
  - Loading states and error handling
  - Responsive design with dark mode

### Error Handling

#### Database Integrity
- **Foreign Key Constraints**: Proper cleanup of spine_specifications before arrow deletion
- **Transaction Safety**: Rollback on any failure during cascade operations
- **Error Messages**: Detailed error reporting for debugging

#### User Interface
- **Loading States**: Visual indicators for all async operations
- **Notifications**: Toast messages for success/error feedback
- **Validation**: Form validation with required field checking
- **Confirmation**: Multi-step confirmation for destructive operations

## Usage Instructions

### Accessing Manufacturer Management
1. Log in as an admin user
2. Navigate to Admin Panel (`/admin`)
3. Click on "Manufacturers" tab

### Creating a New Manufacturer
1. Click "Add Manufacturer" button
2. Enter manufacturer name in modal form
3. Click "Create" to save
4. System creates manufacturer with placeholder arrow

### Editing a Manufacturer
1. Click "Edit" button next to manufacturer
2. Modify name in edit modal
3. Review impact warning showing affected arrow count
4. Click "Update" to save changes

### Deleting a Manufacturer
1. Click "Delete" button next to manufacturer
2. Review cascade delete warning showing:
   - Number of arrows to be deleted
   - Spine specifications to be removed
   - Other associated data
3. Confirm deletion by clicking "Delete Permanently"

## Security Considerations

### Authentication
- **Admin Only**: All manufacturer endpoints require admin authentication
- **JWT Tokens**: Secure token-based authentication system
- **Permission Checks**: Server-side admin status verification

### Data Integrity
- **Transaction Safety**: Database operations wrapped in transactions
- **Cascade Constraints**: Proper handling of foreign key relationships
- **Input Validation**: Server-side validation of all input data
- **URL Encoding**: Safe handling of special characters in manufacturer names

## Future Enhancements

### Planned Features
- **Bulk Operations**: Multi-select for batch manufacturer operations
- **Import/Export**: CSV import/export functionality
- **Audit Trail**: Track changes with user and timestamp
- **Manufacturer Metadata**: Additional fields like country, website, contact info

### Performance Optimizations
- **Pagination**: For large manufacturer datasets
- **Caching**: Statistics caching for improved performance
- **Search/Filter**: Advanced filtering and search capabilities

## Troubleshooting

### Common Issues

#### CORS Errors
- **Symptom**: Authentication failures in development
- **Solution**: Ensure `NUXT_PUBLIC_API_BASE=http://localhost:5000/api` in `.env`

#### Permission Denied
- **Symptom**: Cannot access manufacturer management
- **Solution**: Verify admin status through `/api/admin/check` endpoint

#### Database Errors
- **Symptom**: Foreign key constraint violations
- **Solution**: Check spine_specifications cleanup in cascade delete operations

### Debug Information
- **API Logs**: Check `arrow_scraper/api.py` console output
- **Browser Console**: Check for JavaScript errors in admin panel
- **Network Tab**: Verify API requests and responses

## Related Documentation

- [Admin System Documentation](ADMIN_SYSTEM.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Database Architecture](DATABASE_PERSISTENCE.md)
- [Frontend Components](FRONTEND_COMPONENTS.md)