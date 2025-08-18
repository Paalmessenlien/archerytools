# API Endpoints Documentation

Comprehensive documentation of all REST API endpoints for the Archery Tools platform.

## Base URL
- **Development**: `http://localhost:5000/api`
- **Production**: `https://yourdomain.com/api`

## Authentication

Most endpoints require JWT authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

#### `POST /api/auth/google`
Authenticate user with Google OAuth token.

**Request:**
```json
{
    "token": "google_oauth_token_here"
}
```

**Response:**
```json
{
    "token": "jwt_token_here",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "is_admin": false,
        "draw_length": 28.0
    },
    "needsProfileCompletion": false
}
```

---

## User Management

#### `GET /api/user`
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "profile_picture_url": "https://example.com/photo.jpg",
    "is_admin": false,
    "draw_length": 28.0,
    "skill_level": "intermediate",
    "shooting_style": "target",
    "preferred_manufacturers": ["Easton", "Gold Tip"],
    "created_at": "2025-01-15T10:30:00Z"
}
```

#### `PUT /api/user/profile`
Update user profile information.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "name": "John Smith",
    "draw_length": 29.0,
    "skill_level": "advanced",
    "shooting_style": "hunting",
    "preferred_manufacturers": ["Easton", "Victory", "Carbon Express"]
}
```

**Response:**
```json
{
    "message": "Profile updated successfully",
    "user": { /* updated user object */ }
}
```

---

## Arrow Database

#### `GET /api/arrows`
Search and filter arrows from the database.

**Query Parameters:**
- `search` (string): Search term for manufacturer/model
- `manufacturer` (string): Filter by manufacturer
- `material` (string): Filter by material type
- `diameter_category` (string): Filter by diameter category
- `spine_min` (number): Minimum spine value
- `spine_max` (number): Maximum spine value
- `gpi_min` (number): Minimum GPI weight
- `gpi_max` (number): Maximum GPI weight
- `page` (number): Page number (default: 1)
- `per_page` (number): Results per page (default: 20)
- `sort` (string): Sort field (default: 'manufacturer')
- `order` (string): Sort order ('asc' or 'desc', default: 'asc')

**Example Request:**
```
GET /api/arrows?manufacturer=Easton&material=Carbon&spine_min=300&spine_max=500&page=1&per_page=20
```

**Response:**
```json
{
    "arrows": [
        {
            "id": 1,
            "manufacturer": "Easton",
            "model_name": "FMJ Match Grade",
            "material": "Carbon / Aluminum",
            "description": "Premium hunting arrow...",
            "diameter_category": "Standard hunting",
            "primary_image_url": "https://cdn.example.com/arrow1.jpg",
            "spine_specifications": [
                {
                    "spine": "340",
                    "outer_diameter": 0.340,
                    "inner_diameter": 0.246,
                    "gpi_weight": 9.5,
                    "length_options": ["28", "29", "30", "31", "32"]
                }
            ]
        }
    ],
    "total": 156,
    "page": 1,
    "per_page": 20,
    "total_pages": 8,
    "filters": {
        "manufacturers": ["Easton", "Gold Tip", "Victory"],
        "materials": ["Carbon", "Carbon / Aluminum", "Aluminum"],
        "diameter_categories": ["Ultra-thin", "Thin", "Standard hunting"]
    }
}
```

#### `GET /api/arrows/{id}`
Get detailed information for a specific arrow.

**Response:**
```json
{
    "id": 1,
    "manufacturer": "Easton",
    "model_name": "FMJ Match Grade",
    "material": "Carbon / Aluminum",
    "description": "Premium hunting arrow with carbon core...",
    "recommended_use": "hunting",
    "arrow_type": "carbon-aluminum",
    "straightness_tolerance": "+/- 0.003\"",
    "weight_tolerance": "+/- 2.0 grain",
    "price_range": "$120-150",
    "primary_image_url": "https://cdn.example.com/arrow1.jpg",
    "secondary_images": ["https://cdn.example.com/arrow1-2.jpg"],
    "diameter_category": "Standard hunting",
    "spine_specifications": [
        {
            "id": 1,
            "spine": "340",
            "outer_diameter": 0.340,
            "inner_diameter": 0.246,
            "gpi_weight": 9.5,
            "length_options": ["28", "29", "30", "31", "32"],
            "wall_thickness": 0.047,
            "nock_size": "G"
        }
    ]
}
```

#### `GET /api/database/stats`
Get database statistics and overview.

**Response:**
```json
{
    "arrow_count": 1143,
    "manufacturer_count": 13,
    "manufacturers": [
        {"name": "Easton", "count": 234, "arrow_types": ["target", "hunting"]},
        {"name": "Gold Tip", "count": 178, "arrow_types": ["hunting", "target"]}
    ],
    "materials": [
        {"material": "Carbon", "count": 567},
        {"material": "Carbon / Aluminum", "count": 298}
    ],
    "diameter_categories": [
        {"category": "Standard hunting", "count": 324},
        {"category": "Thin", "count": 156}
    ]
}
```

#### `GET /api/manufacturers`
Get list of all manufacturers with counts.

**Response:**
```json
[
    {
        "manufacturer": "Easton",
        "count": 234,
        "arrow_types": ["target", "hunting", "field"]
    },
    {
        "manufacturer": "Gold Tip",
        "count": 178,
        "arrow_types": ["hunting", "target"]
    }
]
```

---

## Tuning and Calculations

#### `POST /api/tuning/calculate-spine`
Calculate recommended spine based on bow configuration.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "bow_type": "compound",
    "draw_weight": 50,
    "draw_length": 28,
    "arrow_length": 29,
    "point_weight": 125,
    "arrow_material": "carbon",
    "arrow_rest_type": "drop-away",
    "nock_type": "pin",
    "vane_type": "plastic",
    "vane_length": 4,
    "number_of_vanes": 3,
    "insert_weight": 0,
    "vane_weight_per": 5,
    "vane_weight_override": false,
    "bushing_weight": 0,
    "nock_weight": 10
}
```

**Response:**
```json
{
    "recommended_spine": 400,
    "spine_range": {
        "min": 350,
        "max": 450
    },
    "calculations": {
        "base_spine": 625,
        "adjustments": {
            "arrow_length": 25,
            "point_weight": 0,
            "bow_type": 0
        },
        "final_spine": 400
    }
}
```

#### `POST /api/tuning/recommendations`
Get arrow recommendations based on bow configuration.

**Headers:** `Authorization: Bearer <token>`

**Request:** Same as calculate-spine

**Response:**
```json
{
    "recommended_arrows": [
        {
            "id": 45,
            "manufacturer": "Easton",
            "model_name": "Aftermath",
            "spine_match": 400,
            "compatibility_score": 95.5,
            "spine_specifications": {
                "spine": "400",
                "outer_diameter": 0.340,
                "gpi_weight": 8.7
            },
            "total_arrow_weight": 425,
            "foc_percentage": 12.8,
            "match_reasons": ["Perfect spine match", "Optimal diameter for bow type"]
        }
    ],
    "total_compatible": 23,
    "recommended_spine": 400,
    "bow_config": { /* echoed bow config */ }
}
```

#### `POST /api/calculator/arrow-speed-estimate`
Calculate estimated arrow speed with chronograph data integration.

**Request:**
```json
{
    "bow_ibo_speed": 320,
    "bow_draw_weight": 70,
    "bow_draw_length": 29,
    "bow_type": "compound",
    "arrow_weight_grains": 420,
    "string_material": "dyneema",
    "setup_id": 1,          // Optional: for chronograph data lookup
    "arrow_id": 42          // Optional: for chronograph data lookup
}
```

**Response with Chronograph Data:**
```json
{
    "estimated_speed_fps": 285.3,
    "calculation_method": "chronograph_data",
    "confidence_percent": 95,
    "chronograph_data": {
        "measured_speed_fps": 287.1,
        "measured_weight_grains": 425,
        "shot_count": 10,
        "std_deviation": 3.2
    },
    "string_material": "dyneema"
}
```

**Response with Estimation:**
```json
{
    "estimated_speed_fps": 282.4,
    "calculation_method": "compound_estimation_with_string_material",
    "confidence_percent": 75,
    "bow_ibo_speed": 320,
    "arrow_weight_grains": 420,
    "string_material": "dyneema",
    "factors": {
        "base_speed_estimate": 276.9,
        "string_modifier": 1.02,
        "string_speed_effect": "+2.0%",
        "bow_type": "compound"
    }
}
```

---

## Bow Setup Management

#### `GET /api/bow-setups`
Get all bow setups for authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
    {
        "id": 1,
        "name": "Competition Setup",
        "bow_type": "compound",
        "draw_weight": 50,
        "arrow_length": 29,
        "point_weight": 125,
        "compound_brand": "Mathews",
        "compound_model": "TRX 38",
        "ibo_speed": 345,
        "bow_usage": ["target", "field"],
        "description": "My competition bow setup",
        "created_at": "2025-01-15T10:30:00Z"
    }
]
```

#### `GET /api/bow-setups/{id}`
Get specific bow setup details.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "id": 1,
    "name": "Competition Setup",
    "bow_type": "compound",
    "draw_weight": 50,
    "arrow_length": 29,
    "point_weight": 125,
    "insert_weight": 12,
    "nock_weight": 10,
    "fletching_weight": 15,
    "compound_brand": "Mathews",
    "compound_model": "TRX 38",
    "ibo_speed": 345,
    "bow_usage": ["target", "field"],
    "description": "My competition bow setup",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-16T14:20:00Z"
}
```

#### `POST /api/bow-setups`
Create a new bow setup.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "name": "Hunting Setup",
    "bow_type": "compound",
    "draw_weight": 60,
    "arrow_length": 28,
    "point_weight": 150,
    "compound_brand": "Hoyt",
    "compound_model": "RX-7",
    "ibo_speed": 338,
    "bow_usage": ["hunting"],
    "description": "My hunting bow configuration"
}
```

**Response:**
```json
{
    "id": 2,
    "message": "Bow setup created successfully",
    "setup": { /* full setup object */ }
}
```

#### `PUT /api/bow-setups/{id}`
Update existing bow setup.

**Headers:** `Authorization: Bearer <token>`

**Request:** Same fields as POST (partial updates allowed)

**Response:**
```json
{
    "message": "Bow setup updated successfully",
    "setup": { /* updated setup object */ }
}
```

#### `DELETE /api/bow-setups/{id}`
Delete bow setup.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "message": "Bow setup deleted successfully"
}
```

---

## Arrow Selection Management

#### `GET /api/bow-setups/{setup_id}/arrows`
Get arrows selected for a specific bow setup.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "arrows": [
        {
            "id": 1,
            "setup_id": 1,
            "arrow_id": 45,
            "arrow_length": 29,
            "point_weight": 125,
            "calculated_spine": "400",
            "compatibility_score": 95.5,
            "notes": "Perfect match for target shooting",
            "arrow": {
                "manufacturer": "Easton",
                "model_name": "Aftermath",
                "material": "Carbon",
                "spine_specifications": [
                    {
                        "spine": "400",
                        "outer_diameter": 0.340,
                        "gpi_weight": 8.7
                    }
                ]
            },
            "created_at": "2025-01-15T12:00:00Z"
        }
    ]
}
```

#### `POST /api/bow-setups/{setup_id}/arrows`
Add arrow to bow setup.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "arrow_id": 45,
    "arrow_length": 29,
    "point_weight": 125,
    "notes": "Selected based on spine calculation"
}
```

**Response:**
```json
{
    "message": "Arrow added to setup successfully",
    "setup_arrow": { /* created setup_arrow object */ }
}
```

#### `PUT /api/setup-arrows/{setup_arrow_id}`
Update arrow configuration in setup.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "arrow_length": 28.5,
    "point_weight": 150,
    "notes": "Updated for hunting configuration"
}
```

#### `DELETE /api/setup-arrows/{setup_arrow_id}`
Remove arrow from setup.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "message": "Arrow removed from setup successfully"
}
```

---

## Component Management

#### `GET /api/components`
Get arrow components (nocks, inserts, points, etc.).

**Query Parameters:**
- `category` (string): Filter by component type
- `manufacturer` (string): Filter by manufacturer
- `diameter` (number): Filter by compatible diameter
- `weight_min` (number): Minimum weight in grains
- `weight_max` (number): Maximum weight in grains

**Response:**
```json
{
    "components": [
        {
            "id": 1,
            "manufacturer": "Easton",
            "model_name": "G Nock",
            "component_type": "nock",
            "description": "Standard G nock for carbon arrows",
            "weight_grains": 10.2,
            "diameter_compatibility": [0.244, 0.246],
            "material": "Plastic",
            "color_options": ["Red", "Green", "Blue", "White"],
            "price_range": "$15-20"
        }
    ],
    "total": 234
}
```

#### `GET /api/arrows/{arrow_id}/compatible-components`
Get components compatible with specific arrow.

**Query Parameters:**
- `category` (string): Filter by component type

**Response:**
```json
{
    "arrow_id": 45,
    "compatible_components": [
        {
            "id": 1,
            "manufacturer": "Easton",
            "model_name": "G Nock",
            "component_type": "nock",
            "weight_grains": 10.2,
            "compatibility_score": 100,
            "compatibility_reasons": ["Perfect diameter match", "Manufacturer recommended"]
        }
    ],
    "total": 12
}
```

---

## Tuning Session Management

#### `POST /api/tuning/sessions`
Create tuning session.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "archer_name": "John Doe",
    "bow_config": { /* complete bow configuration */ },
    "recommended_spine": 400,
    "recommended_arrows": [ /* array of recommended arrows */ ],
    "notes": "Initial tuning session"
}
```

**Response:**
```json
{
    "id": "session_uuid",
    "message": "Tuning session created successfully"
}
```

#### `GET /api/tuning/sessions`
Get user's tuning sessions.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
    {
        "id": "session_uuid",
        "session_name": "Competition Tuning",
        "bow_config": { /* bow configuration */ },
        "recommended_spine": 400,
        "notes": "Great results with paper tuning",
        "created_at": "2025-01-15T10:30:00Z"
    }
]
```

---

## Interactive Guide Management

#### `GET /api/guides`
Get available tuning guides.

**Response:**
```json
[
    {
        "id": "paper_tuning",
        "name": "Paper Tuning Guide",
        "description": "Step-by-step paper tuning process",
        "estimated_time": "30 minutes",
        "difficulty": "intermediate",
        "total_steps": 8
    }
]
```

#### `POST /api/guide-sessions`
Start new guide session.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "guide_type": "paper_tuning",
    "bow_config": { /* bow configuration */ },
    "notes": "Starting paper tuning process"
}
```

**Response:**
```json
{
    "id": 1,
    "guide_type": "paper_tuning",
    "status": "active",
    "current_step": 0,
    "total_steps": 8,
    "message": "Guide session started successfully"
}
```

#### `POST /api/guide-sessions/{id}/pause`
Pause active guide session.

#### `POST /api/guide-sessions/{id}/resume`
Resume paused guide session.

#### `POST /api/guide-sessions/{id}/complete`
Mark guide session as completed.

#### `GET /api/guide-sessions`
Get user's guide sessions.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
    {
        "id": 1,
        "guide_type": "paper_tuning",
        "status": "active",
        "current_step": 3,
        "total_steps": 8,
        "progress_percentage": 37.5,
        "created_at": "2025-01-15T14:00:00Z"
    }
]
```

---

## Chronograph Data Management

#### `POST /api/chronograph-data`
Create new chronograph measurement data.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "setup_id": 1,
    "setup_arrow_id": 5,
    "measured_speed_fps": 285.3,
    "arrow_weight_grains": 420,
    "temperature_f": 72,
    "humidity_percent": 45,
    "chronograph_model": "Competition Electronics ProChrono",
    "shot_count": 10,
    "std_deviation": 3.2,
    "min_speed_fps": 281.1,
    "max_speed_fps": 289.7,
    "notes": "Indoor range, consistent form"
}
```

**Response:**
```json
{
    "id": 1,
    "setup_id": 1,
    "setup_arrow_id": 5,
    "measured_speed_fps": 285.3,
    "arrow_weight_grains": 420,
    "temperature_f": 72,
    "humidity_percent": 45,
    "measurement_date": "2025-08-18T14:30:00Z",
    "chronograph_model": "Competition Electronics ProChrono",
    "shot_count": 10,
    "std_deviation": 3.2,
    "min_speed_fps": 281.1,
    "max_speed_fps": 289.7,
    "verified": false,
    "notes": "Indoor range, consistent form",
    "created_at": "2025-08-18T14:30:00Z"
}
```

#### `GET /api/chronograph-data/setup/{setup_id}`
Get all chronograph data for a specific bow setup.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
    {
        "id": 1,
        "setup_id": 1,
        "arrow_id": 42,
        "setup_arrow_id": 5,
        "measured_speed_fps": 285.3,
        "arrow_weight_grains": 420,
        "temperature_f": 72,
        "humidity_percent": 45,
        "measurement_date": "2025-08-18T14:30:00Z",
        "chronograph_model": "Competition Electronics ProChrono",
        "shot_count": 10,
        "std_deviation": 3.2,
        "min_speed_fps": 281.1,
        "max_speed_fps": 289.7,
        "verified": true,
        "notes": "Indoor range, consistent form",
        "arrow_name": "Easton X10",
        "arrow_length": 29.5,
        "point_weight": 120,
        "calculated_spine": 410
    }
]
```

#### `PUT /api/chronograph-data/{data_id}`
Update existing chronograph data.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "measured_speed_fps": 287.2,
    "std_deviation": 2.8,
    "verified": true,
    "notes": "Re-measured with improved form"
}
```

**Response:**
```json
{
    "message": "Chronograph data updated successfully",
    "chronograph_data": { /* updated data object */ }
}
```

#### `DELETE /api/chronograph-data/{data_id}`
Delete chronograph data entry.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "message": "Chronograph data deleted successfully"
}
```

---

## Admin Endpoints

All admin endpoints require `is_admin: true` in user profile.

#### `GET /api/admin/check`
Check if current user has admin privileges.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "is_admin": true,
    "user": { /* admin user object */ }
}
```

#### `GET /api/admin/users`
Get all users (admin only).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
    {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "is_admin": false,
        "created_at": "2025-01-15T10:30:00Z",
        "last_login": "2025-01-16T09:15:00Z"
    }
]
```

#### `PUT /api/admin/users/{user_id}/admin`
Grant/revoke admin privileges.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
    "is_admin": true
}
```

### Admin Arrow Management

#### `GET /api/admin/arrows`
Get arrows for admin management with full details.

#### `PUT /api/admin/arrows/{id}`
Update arrow specifications (admin only).

#### `DELETE /api/admin/arrows/{id}`
Delete arrow from database (admin only).

#### `POST /api/admin/arrows`
Create new arrow specification (admin only).

### Admin Backup System

#### `GET /api/admin/backups`
List all available backups.

**Response:**
```json
[
    {
        "id": "local_abc123",
        "backup_name": "production_backup_2025_01_15",
        "file_size": 15728640,
        "backup_type": "full",
        "include_arrow_db": true,
        "include_user_db": true,
        "created_at": "2025-01-15T10:30:00Z"
    }
]
```

#### `POST /api/admin/backup`
Create new backup.

**Request:**
```json
{
    "backup_name": "manual_backup_2025_01_15",
    "include_arrow_db": true,
    "include_user_db": true,
    "upload_to_cdn": true
}
```

#### `POST /api/admin/backup/{backup_id}/restore`
Restore from backup.

**Request:**
```json
{
    "restore_arrow_db": true,
    "restore_user_db": true,
    "confirm": true
}
```

#### `GET /api/admin/backup/{backup_id}/download`
Get backup download URL or initiate download.

---

## Health and Monitoring

#### `GET /api/health`
Comprehensive health check.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-01-15T10:30:00Z",
    "version": "2.1.0",
    "database_status": "connected",
    "arrow_database": {
        "status": "healthy",
        "arrow_count": 1143,
        "last_updated": "2025-01-10T08:00:00Z"
    },
    "user_database": {
        "status": "healthy",
        "user_count": 45,
        "setup_count": 123
    }
}
```

#### `GET /api/simple-health`
Simple health check for load balancers.

**Response:**
```json
{
    "status": "ok"
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
    "error": "Error message",
    "details": "Additional error details",
    "timestamp": "2025-01-15T10:30:00Z",
    "status": 400
}
```

### Common HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized (missing/invalid token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **409**: Conflict (duplicate data)
- **422**: Validation Error
- **500**: Internal Server Error

### Rate Limiting
- Most endpoints: 100 requests/minute per user
- Auth endpoints: 10 requests/minute per IP
- Admin endpoints: 50 requests/minute per admin user

This API documentation covers all major endpoints in the Archery Tools platform. Each endpoint includes proper authentication, validation, and error handling.