# Journal and Tuning System Documentation

## Overview

This document provides comprehensive documentation for the ArcheryTools Journal and Tuning System, covering architecture, implementation details, API endpoints, database schema, and integration patterns for future development.

## Table of Contents

- [System Architecture](#system-architecture)
- [Database Schema](#database-schema)
- [Journal System](#journal-system)
- [Tuning System](#tuning-system)
- [API Endpoints](#api-endpoints)
- [Frontend Components](#frontend-components)
- [Integration Patterns](#integration-patterns)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)

## System Architecture

### High-Level Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Layer     │    │   Database      │
│   (Nuxt 3)      │    │   (Flask)       │    │   (SQLite)      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Journal Views │◄──►│ • Journal API   │◄──►│ • journal_entries│
│ • Tuning UI     │    │ • Tuning API    │    │ • guide_sessions │
│ • Components    │    │ • Session Mgmt  │    │ • setup_arrows  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

1. **Journal System**: Unified journaling for all archery activities
2. **Tuning System**: Interactive tuning sessions (paper, bareshaft, walkback)
3. **Session Management**: Persistent tuning sessions with progress tracking
4. **Integration Layer**: Links between arrows, bow setups, and journal entries

## Database Schema

### Core Tables

#### `journal_entries` Table
```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bow_setup_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    entry_type TEXT NOT NULL DEFAULT 'general',
    tags TEXT, -- JSON array
    is_private BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Enhanced columns (added via migrations 055/058/059)
    images TEXT,                         -- JSON array of image objects (Migration 055)
    arrow_id INTEGER,                    -- Links to arrows
    is_favorite BOOLEAN DEFAULT 0,      -- User favorites
    session_metadata TEXT,              -- JSON session data
    session_type TEXT DEFAULT 'general', -- paper/bareshaft/walkback/general
    session_quality_score REAL,         -- 0.0-100.0 score
    equipment_focus TEXT,               -- Equipment category focus
    template_used INTEGER,              -- Template reference
    reading_time_seconds INTEGER,       -- Content reading time
    
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
);
```

#### `guide_sessions` Table
```sql
CREATE TABLE guide_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    guide_type TEXT NOT NULL,           -- paper/bareshaft/walkback
    arrow_id INTEGER,                   -- Linked arrow
    bow_setup_id INTEGER,               -- Linked bow setup
    status TEXT DEFAULT 'active',       -- active/completed/abandoned
    session_data TEXT,                  -- JSON session state
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    test_count INTEGER DEFAULT 0,
    current_step INTEGER DEFAULT 1,
    progress_percentage REAL DEFAULT 0.0,
    
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
);
```

### Relationships

```
users (1) ──────────────── (n) journal_entries
bow_setups (1) ─────────── (n) journal_entries  
arrows (1) ────────────── (n) journal_entries [via arrow_id]
users (1) ──────────────── (n) guide_sessions
bow_setups (1) ─────────── (n) guide_sessions
```

## Journal System

### Core Features

1. **Unified Entry Types**
   - `general`: Basic notes and observations
   - `tuning_session`: Results from interactive tuning
   - `shooting_notes`: Range notes and performance
   - `setup_change`: Equipment modifications

2. **Image Upload System** ✨ **NEW** (Migration 055 - September 2025)
   - **Direct JSON Storage**: Images stored as JSON arrays in `journal_entries.images` column
   - **Session-Level Integration**: Tuning sessions (paper, bareshaft, walkback) automatically store uploaded images
   - **CDN Integration**: Supports Cloudinary, AWS S3, BunnyCD, and other CDN services
   - **Automatic Migration**: Existing `journal_attachments` automatically migrated to new format
   - **Enhanced UI**: Grid display with click-to-open functionality and mobile responsive design

3. **Additional Entry Types**
   - `arrow_change`: Arrow configuration updates
   - `maintenance`: Equipment maintenance logs
   - `upgrade`: Equipment upgrades

4. **Advanced Features**
   - Rich text content with Markdown support
   - Tagging system for organization
   - Favorite entries
   - Template-based entry creation
   - Session metadata integration
   - Equipment linking (arrows, bow setups)

3. **Context Integration**
   - Display on bow setup pages (`/setups/{id}`)
   - Display on arrow pages (`/setup-arrows/{id}`)
   - Unified journal view (`/journal`)
   - Entry detail views (`/journal/{id}`)

### Journal Entry Lifecycle

```
1. Creation Triggers:
   ├─ Manual entry creation
   ├─ Tuning session completion
   ├─ Equipment changes
   └─ Template instantiation

2. Processing:
   ├─ Validation & sanitization
   ├─ Metadata extraction
   ├─ Link generation (arrow_id, bow_setup_id)
   └─ Storage with timestamps

3. Display:
   ├─ Context-filtered views
   ├─ Search & filtering
   ├─ Rich rendering
   └─ Action buttons (edit, delete, favorite)
```

## Tuning System

### Interactive Tuning Sessions

The system supports three types of interactive tuning sessions:

#### 1. Paper Tuning
- **Purpose**: Basic arrow flight analysis
- **Process**: Shoot through paper, analyze tear patterns
- **Recommendations**: Rest adjustments, nocking point changes
- **Difficulty**: Beginner (10-15 minutes)

#### 2. Bareshaft Tuning  
- **Purpose**: Advanced spine matching
- **Process**: Compare fletched vs bare arrow impacts
- **Recommendations**: Bow-specific adjustments, point weight changes
- **Difficulty**: Intermediate (15-20 minutes)

#### 3. Walkback Tuning
- **Purpose**: Consistency across distances
- **Process**: Test at multiple distances, analyze patterns
- **Recommendations**: Fine-tuning for distance consistency  
- **Difficulty**: Advanced (20-30 minutes)

### Session Management

#### Session States
- `active`: Currently in progress
- `paused`: Temporarily stopped
- `completed`: Finished with results
- `abandoned`: Stopped without completion

#### Session Data Structure
```json
{
  "session_id": "uuid",
  "session_type": "bareshaft",
  "bow_setup": {
    "id": 1,
    "name": "Mathews TRX 36"
  },
  "arrow": {
    "id": 2438,
    "name": "Cross-X Fulmen"
  },
  "tests": [
    {
      "test_number": 1,
      "distance": "20 yards",
      "pattern": "left",
      "quality": 95,
      "notes": "Arrows hitting left of center",
      "timestamp": "2025-09-08T13:11:00Z"
    }
  ],
  "recommendations": {
    "priority": "high",
    "adjustments": ["move_rest_left", "add_point_weight"]
  },
  "quality_score": 95.0
}
```

### Dual API Architecture

**⚠️ Critical Implementation Detail**: The system uses two API endpoints for journal creation:

1. **New API** (Recommended): `POST /api/journal/entries`
   - ✅ Creates rich entries with full metadata
   - ✅ Proper arrow linking via `linked_arrow` parameter
   - ✅ Session metadata support

2. **Legacy API** (Deprecated): `POST /api/tuning-guides/sessions/{id}/complete`
   - ❌ Creates basic entries without rich metadata
   - ❌ Limited session data storage
   - ⚠️ Should use `skip_journal_creation: true` to prevent conflicts

## API Endpoints

### Journal API (`/api/journal/`)

#### Create Entry
```http
POST /api/journal/entries
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "Bareshaft Tuning Session",
  "content": "# Session Results\n\nLeft impact pattern observed...",
  "entry_type": "tuning_session",
  "bow_setup_id": 1,
  "linked_arrow": 2438,
  "session_metadata": {
    "session_type": "bareshaft",
    "tests": [...],
    "quality_score": 95
  },
  "session_type": "bareshaft",
  "session_quality_score": 95
}
```

#### Get Entries
```http
GET /api/journal/entries?linked_arrow=2438&page=1&limit=50
Authorization: Bearer {token}
```

#### Entry Detail
```http
GET /api/journal/entries/{id}
Authorization: Bearer {token}
```

### Tuning API (`/api/tuning-guides/`)

#### Create Session
```http
POST /api/tuning-guides/sessions
Content-Type: application/json
Authorization: Bearer {token}

{
  "guide_type": "bareshaft",
  "arrow_id": 2438,
  "bow_setup_id": 1
}
```

#### Complete Session
```http
POST /api/tuning-guides/sessions/{id}/complete
Content-Type: application/json
Authorization: Bearer {token}

{
  "session_quality_score": 95,
  "completion_notes": "Single test completed",
  "linked_arrow": 2438,
  "skip_journal_creation": true  // Prevent duplicate creation
}
```

## Frontend Components

### Core Components

#### `BaseJournalView.vue`
- **Purpose**: Unified journal display component
- **Props**: `context`, `entries`, `stats`, `loading`
- **Features**: Filtering, pagination, entry actions
- **Usage**: Embedded in setup pages and main journal

#### `JournalEntryDetailViewer.vue`
- **Purpose**: Full entry display with rich formatting
- **Features**: Tabbed interface, session data, actions
- **Tabs**: Overview, Technical, Analysis, Full Notes

#### `JournalEntryCard.vue`
- **Purpose**: Entry list item display
- **Features**: Swipe actions removed (as requested)
- **Actions**: View button, favorite toggle

### Integration Examples

#### Arrow Setup Page Integration
```vue
<BaseJournalView
  :context="'arrow'"
  :entries="journalEntries"
  :initial-filters="{ linked_arrow: setupArrowData?.setup_arrow?.arrow_id }"
  @entry:view="handleJournalEntryView"
  @entry:create="handleJournalEntryCreate"
/>
```

#### Tuning Session Pages
```vue
<!-- Bareshaft Tuning: /pages/tuning-session/bareshaft/[sessionId].vue -->
<!-- Walkback Tuning: /pages/tuning-session/walkback/[sessionId].vue -->
```

## Integration Patterns

### Journal-Arrow Linking

**Frontend Request**:
```javascript
const response = await journalApi.getEntries({
  linked_arrow: 2438,  // Setup arrow ID
  page: 1,
  limit: 50
})
```

**API Processing**:
```python
# Extract arrow_id from linked_arrow parameter
arrow_id = None
if data.get('linked_arrow'):
    if isinstance(data['linked_arrow'], int):
        arrow_id = data['linked_arrow']
    elif isinstance(data['linked_arrow'], list):
        arrow_id = data['linked_arrow'][0]

# Store in database
cursor.execute('''
    INSERT INTO journal_entries (..., arrow_id) 
    VALUES (..., ?)
''', (..., arrow_id))
```

**Database Query**:
```sql
SELECT * FROM journal_entries 
WHERE arrow_id = ? AND user_id = ?
ORDER BY created_at DESC
```

### Session Completion Flow

```
1. User completes tuning test
   ├─ Frontend: Submit test data
   ├─ API: Store in guide_sessions
   └─ Generate session_metadata

2. User clicks "Save & Exit"
   ├─ Frontend: Call completion API with skip_journal_creation: true
   ├─ API: Update session status
   └─ Background: Create journal entry via new API

3. Journal Creation
   ├─ Extract arrow_id from linked_arrow
   ├─ Generate rich content with session data
   ├─ Store with proper session_type
   └─ Return journal_entry_id
```

## Development Guide

### Adding New Tuning Types

1. **Create Session Page**
   ```
   /pages/tuning-session/{type}/[sessionId].vue
   ```

2. **Update Session Data**
   ```javascript
   const completionData = {
     session_quality_score: score,
     completion_notes: notes,
     linked_arrow: arrowId,
     skip_journal_creation: true  // Important!
   }
   ```

3. **Add to Entry Types**
   ```javascript
   const journalEntryTypes = [
     { value: 'custom_tuning', label: 'Custom Tuning', icon: 'fas fa-cog' }
   ]
   ```

### Database Migrations

#### Required Migrations
- `058_add_journal_entries_missing_columns.py`: Adds arrow_id, is_favorite
- `059_add_session_metadata_to_journal.py`: Adds session metadata columns

#### Running Migrations
```bash
python3 arrow_scraper/migrations/058_add_journal_entries_missing_columns.py
python3 arrow_scraper/migrations/059_add_session_metadata_to_journal.py
```

### Testing Patterns

#### Journal Creation Test
```javascript
const testEntry = {
  title: "Test Entry",
  content: "Test content",
  entry_type: "tuning_session",
  bow_setup_id: 1,
  linked_arrow: 2438,
  session_type: "bareshaft"
}

const response = await fetch('/api/journal/entries', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}` 
  },
  body: JSON.stringify(testEntry)
})
```

#### Database Verification
```sql
SELECT id, title, arrow_id, session_type 
FROM journal_entries 
WHERE arrow_id = 2438
ORDER BY created_at DESC;
```

## Troubleshooting

### Common Issues

#### 1. Journal Entries Not Showing on Setup Pages

**Problem**: Entries visible in `/journal` but not `/setup-arrows/{id}`

**Cause**: Arrow ID linking mismatch
- Frontend filters by `arrow_id = 2438`
- Database entries have `arrow_id = NULL`

**Solution**:
```sql
-- Check arrow_id distribution
SELECT arrow_id, COUNT(*) FROM journal_entries GROUP BY arrow_id;

-- Update existing entries (if needed)
UPDATE journal_entries 
SET arrow_id = 2438 
WHERE id IN (26, 27, 28) AND session_type = 'bareshaft';
```

#### 2. Duplicate Journal Entries

**Problem**: Two entries created per tuning session

**Cause**: Both old and new APIs creating entries

**Solution**: Ensure `skip_journal_creation: true` in completion calls

#### 3. Session Metadata Missing

**Problem**: Entries show "Missing Session Data"

**Cause**: `session_metadata` field is NULL or malformed

**Solution**: Verify JSON structure and API payload

### Database Health Checks

#### Verify Schema
```sql
PRAGMA table_info(journal_entries);
```

#### Check Data Integrity  
```sql
-- Orphaned entries (missing user)
SELECT COUNT(*) FROM journal_entries 
WHERE user_id NOT IN (SELECT id FROM users);

-- Unlinked arrows
SELECT COUNT(*) FROM journal_entries 
WHERE arrow_id IS NOT NULL 
  AND arrow_id NOT IN (SELECT id FROM arrows);
```

### Performance Monitoring

#### Query Performance
```sql
-- Most accessed entries
SELECT entry_type, COUNT(*) 
FROM journal_entries 
GROUP BY entry_type;

-- Large content entries
SELECT id, title, LENGTH(content) as content_size
FROM journal_entries 
ORDER BY content_size DESC 
LIMIT 10;
```

## Future Development

### Planned Features

1. **Enhanced Session Analytics**
   - Progress tracking across multiple sessions
   - Performance improvement metrics
   - Recommendation accuracy scoring

2. **Advanced Linking**
   - Multi-arrow session support
   - Equipment change correlation
   - Environmental factor tracking

3. **Export & Sharing**
   - PDF report generation
   - Session data export
   - Community sharing features

### API Evolution

1. **Deprecate Legacy API**
   - Phase out `/api/tuning-guides/sessions/{id}/complete`
   - Migrate to unified journal creation

2. **Enhanced Metadata**
   - Structured session schemas
   - Validation frameworks
   - Version management

### Performance Optimizations

1. **Database Indexing**
   ```sql
   CREATE INDEX idx_journal_arrow_user ON journal_entries(arrow_id, user_id);
   CREATE INDEX idx_journal_session_type ON journal_entries(session_type, created_at);
   ```

2. **Query Optimization**
   - Implement pagination cursors
   - Add result caching
   - Optimize complex filters

---

## References

- [Database Schema Documentation](DATABASE_SCHEMA.md)
- [API Endpoints Documentation](API_ENDPOINTS.md)  
- [Development Guide](DEVELOPMENT_GUIDE.md)
- [Journal Enhancement Phase 6](JOURNAL_ENHANCEMENT_PHASE6.md)
- [Bareshaft Tuning Implementation](docs/bareshaft_tuning_implementation.md)

---

*Last Updated: September 8, 2025*  
*Authors: Claude Code Development Team*  
*Version: 1.0.0*