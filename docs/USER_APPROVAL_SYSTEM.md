# User Approval System

This document describes the comprehensive user approval system implemented for the Archery Tools platform, which enforces invitation-only access through admin-controlled user activation.

## Overview

The User Approval System ensures that all new users require administrator approval before gaining access to the platform. This implements a true invitation-only beta model with proper security controls and user experience considerations.

## Architecture

### Database Schema

**Migration 044: User Approval System**
- **File**: `arrow_scraper/migrations/044_user_approval_system.py`
- **Applied**: August 28, 2025
- **Changes**:
  - Added `status` column to `users` table with values: `active`, `pending`, `suspended`
  - Default status for new users: `pending`
  - Existing users grandfathered to `active` status
  - Admin user always set to `active`

### User Status Values

| Status | Description | Access Level |
|--------|-------------|--------------|
| `active` | Approved user with full access | Full platform access |
| `pending` | New user awaiting admin approval | No platform access |
| `suspended` | Temporarily blocked user | No platform access |

## Implementation Components

### 1. Backend Authentication (auth.py)

**New User Registration Flow:**
```python
if not user:
    user = db.create_user(google_id, email, name, profile_picture_url)
    if email == "messenlien@gmail.com":
        # Admin user is always active
        db.update_user_status(user['id'], 'active')
    else:
        # Regular new users need approval
        db.update_user_status(user['id'], 'pending')
```

**Login Validation:**
```python
# Check if user is approved for access
user_status = user.get('status', 'pending')
if user_status != 'active':
    return None, False  # Deny access for non-active users
```

**Token Validation:**
- `token_required` decorator checks user status on every API call
- Returns 403 status with descriptive message for non-active users

### 2. Database Layer (unified_database.py)

**New Methods:**
- `update_user_status(user_id, status)` - Update user approval status
- `create_user()` - Modified to set default 'pending' status

**Status Management:**
```python
def update_user_status(self, user_id: int, status: str) -> bool:
    """Update user status (active, pending, suspended)"""
    return self.update_user(user_id, status=status)
```

### 3. Frontend Authentication Flow (useAuth.ts)

**Enhanced Error Handling:**
```typescript
if (res.status === 401 && errorData.error && errorData.error.includes('pending')) {
    // Show pending approval message
    router.push('/pending-approval');
}
```

**New User Experience:**
- Pending users redirected to professional waiting page
- Clear feedback about approval status
- Contact information for support

### 4. Admin Panel Enhancement (admin/index.vue)

**User Management Features:**
- **Approve Button**: Green button with check icon for pending users
- **Status Badges**: Color-coded status indicators
  - 🟢 Active: Green badge
  - 🟡 Pending: Yellow badge  
  - 🔴 Suspended: Red badge
- **Conditional Actions**: Different buttons based on user status

**Admin Functions:**
```typescript
const approveUser = async (user) => {
    await updateUserStatus(user.id, 'active')
    user.status = 'active'
    showNotification(`Successfully approved ${user.name}`, 'success')
}
```

### 5. Pending Approval Page (pending-approval.vue)

**User Experience Features:**
- Professional waiting page with clear status information
- Step-by-step explanation of approval process
- Contact support functionality
- Status check button to retry authentication
- Responsive design with dark mode support

## User Flows

### New User Registration

1. **User logs in with Google** → Account created with `pending` status
2. **Authentication attempt** → Redirected to `/pending-approval` page
3. **Admin notification** → New user appears in admin panel with "Approve" button
4. **Admin approval** → User status changed to `active`
5. **User retry** → Authentication succeeds, full platform access granted

### Admin User Flow

1. **Admin login** → Always granted `active` status automatically
2. **Navigate to admin panel** → See all users with status indicators
3. **Review pending users** → Click "Approve" button to activate
4. **User management** → Suspend/activate users as needed

### Existing User Protection

- All existing users automatically grandfathered to `active` status
- No disruption to current user experience
- Admin user (messenlien@gmail.com) always protected with `active` status

## Security Features

### Access Control
- **Authentication Blocking**: Non-active users cannot obtain valid JWT tokens
- **API Protection**: All protected endpoints verify user status via `token_required`
- **Admin Override**: Admin user cannot be suspended or set to pending

### Status Validation
- **Database Constraints**: Status values validated at application layer
- **Cascading Checks**: Status verified on login and every API call
- **Secure Defaults**: New users default to most restrictive status

### Admin Protection
- **Email-based Admin**: Admin status tied to messenlien@gmail.com
- **Status Override**: Admin user status automatically corrected if changed
- **Permanent Access**: Admin cannot be locked out through status changes

## API Endpoints

### User Status Management

**Update User Status** (Admin Only)
```http
PUT /api/admin/users/{userId}/status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "active" | "pending" | "suspended"
}
```

**Get All Users** (Admin Only)
```http
GET /api/admin/users
Authorization: Bearer {admin_token}
```

**Delete User** (Admin Only, Non-Admin Users)
```http
DELETE /api/admin/users/{userId}
Authorization: Bearer {admin_token}
```

## Error Handling

### Authentication Errors
- **401 Unauthorized**: Invalid credentials or pending approval
- **403 Forbidden**: Account suspended or insufficient privileges
- **User-friendly Messages**: Clear explanations of access restrictions

### Frontend Error Handling
```typescript
// Pending user handling
if (errorData.error && errorData.error.includes('pending')) {
    router.push('/pending-approval');
}

// Generic error handling  
alert('Authentication failed: ' + errorData.error);
```

## Database Migration Details

### Migration 044 Implementation

**Migration Script**: `migrations/044_user_approval_system.py`

**Key Operations:**
1. Add `status` column with `DEFAULT 'pending'`
2. Update existing users to `'active'` status (grandfather clause)
3. Ensure admin user has `'active'` status
4. Proper rollback functionality

**Migration Test:**
```python
# Creates test database and verifies:
# - Status column added successfully
# - Default values applied correctly
# - Admin user protection working
```

### Database Path Resolution

**Issue Resolution:**
- Migration initially applied to wrong database path
- Fixed by applying to UnifiedDatabase path: `/arrow_scraper/databases/arrow_database.db`
- Verified with existing user grandfathering

## Configuration

### Environment Variables
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret  
- `SECRET_KEY`: JWT signing secret

### Admin Configuration
- Admin email: `messenlien@gmail.com` (hardcoded for security)
- Admin status: Always `active`, automatically restored on login
- Admin privileges: Cannot be removed or suspended

## Testing

### Manual Test Cases

1. **New User Registration**
   - ✅ Create Google account, attempt login
   - ✅ Verify redirect to pending-approval page
   - ✅ Check user appears in admin panel with pending status

2. **Admin Approval Process**
   - ✅ Login as admin, navigate to admin panel
   - ✅ Find pending user, click "Approve" button
   - ✅ Verify status changes to active with success notification

3. **User Access After Approval**
   - ✅ Approved user can login successfully
   - ✅ Full platform access granted
   - ✅ All protected routes accessible

4. **Suspension Functionality**
   - ✅ Admin can suspend active users
   - ✅ Suspended users blocked from login
   - ✅ Suspended users can be reactivated

### Automated Verification
```python
# Database status verification
cursor.execute('SELECT status FROM users WHERE email = ?', (email,))
assert cursor.fetchone()[0] == 'active'

# API endpoint testing  
response = client.post('/api/admin/users/123/status', 
                      json={'status': 'active'})
assert response.status_code == 200
```

## Deployment Considerations

### Production Deployment
- Database migration automatically applied via migration system
- Existing users unaffected (grandfathered to active)
- Admin user protection ensures no lockout scenarios

### Monitoring
- Track pending user registrations via admin panel
- Monitor failed authentication attempts
- Log user status changes for audit trail

## Maintenance

### Regular Tasks
- Review pending users in admin panel
- Clean up old suspended accounts if needed
- Monitor system for unauthorized access attempts

### Troubleshooting
- **"No such column: status"**: Check migration applied to correct database
- **Admin locked out**: Verify admin email configuration and status
- **Users can't login**: Check user status in admin panel

## Security Considerations

### Best Practices Implemented
- ✅ Secure defaults (new users pending)
- ✅ Admin protection (cannot be locked out)
- ✅ Token validation on every request
- ✅ Clear user feedback and error handling
- ✅ Proper database migrations with rollback

### Future Enhancements
- Email notifications for approval status changes
- Batch user approval functionality  
- User registration requests with metadata
- Approval workflow with multiple admin levels
- Audit logging for all user status changes

---

## Summary

The User Approval System successfully implements invitation-only platform access through:

- **Database-backed status management** with proper migrations
- **Secure authentication flow** blocking non-approved users  
- **Professional user experience** with clear feedback
- **Comprehensive admin controls** for user management
- **Existing user protection** through grandfathering
- **Admin safety measures** preventing lockout scenarios

The system ensures platform quality and security while maintaining excellent user experience for both new users awaiting approval and administrators managing access.