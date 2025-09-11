# Image Upload System Documentation

## Overview

The Archery Tools platform features a comprehensive image upload system that allows users to upload and manage images for equipment, bow setups, and journal entries. The system leverages CDN integration for fast, scalable image delivery and storage.

## Architecture

### Universal Image Upload Infrastructure

The image upload system is built on a universal architecture that supports multiple contexts:

- **Equipment Images**: Up to 5 images per equipment item
- **Bow Setup Images**: Up to 3 images per bow setup
- **Journal Images**: Up to 10 images per journal entry (comprehensive integration)
- **Tuning Session Images**: Session-level image storage with automatic journal linking
- **Profile Images**: Single profile picture per user

### Core Components

#### Frontend Components

**`useImageUpload.ts` Composable**
```typescript
export interface ImageUploadConfig {
  context: 'journal' | 'equipment' | 'profile' | 'setup' | 'arrow'
  entityId?: number
  maxFiles?: number
  maxSize?: number // in MB
  allowedTypes?: string[]
  cdnPath?: string
  compressionQuality?: number
}
```

Features:
- Multi-context support with configurable limits
- Drag & drop functionality
- File validation (type, size, limits)
- Progress tracking and error handling
- CDN integration ready
- Real-time preview capabilities

**`ImageUpload.vue` Component**
- Reusable upload component for single image uploads
- Preview functionality with loading states
- Error display and user feedback
- Customizable upload paths and validation rules

#### Backend Infrastructure

**`/api/upload/image` Endpoint**
- JWT authentication required
- File validation (type, size limits)
- CDN integration with fallback to local storage
- Support for multiple upload contexts
- Profile picture database updates

**CDN Integration (`cdn_uploader.py`)**
- Multi-provider CDN system supporting:
  - Bunny CDN (primary)
  - Cloudinary
  - AWS S3
  - Local storage (fallback)
- Automatic fallback mechanisms
- SEO-friendly image naming and organization

### Database Schema

**Migration 041 - Universal Image Upload System**

```sql
-- Universal image tracking table
CREATE TABLE system_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    context TEXT NOT NULL CHECK (context IN ('journal', 'equipment', 'profile', 'setup', 'arrow')),
    entity_id INTEGER,
    image_url TEXT NOT NULL,
    cdn_url TEXT,
    original_name TEXT,
    file_size INTEGER,
    mime_type TEXT,
    alt_text TEXT,
    upload_session_id TEXT,
    uploaded_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users (id)
);

-- Upload progress tracking
CREATE TABLE image_upload_sessions (
    id TEXT PRIMARY KEY,
    context TEXT NOT NULL,
    total_files INTEGER DEFAULT 1,
    uploaded_files INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'uploading', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Context-specific validation rules
CREATE TABLE image_validations (
    context TEXT PRIMARY KEY,
    max_files INTEGER DEFAULT 10,
    max_file_size INTEGER DEFAULT 5242880,
    allowed_types TEXT DEFAULT 'image/jpeg,image/jpg,image/png,image/webp',
    compression_quality REAL DEFAULT 0.8
);
```

### Equipment Image Integration

#### Equipment Creation/Edit Forms (`CustomEquipmentForm.vue`)

**Features:**
- Image upload section with up to 5 images per equipment item
- Integrated `useImageUpload` composable with 'equipment' context
- Image preview grid with remove functionality
- Form data integration - images included in API payload
- Image initialization for editing mode
- Form reset clears images after successful addition

**Implementation:**
```vue
<template>
  <!-- Equipment Images -->
  <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
    <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
      <i class="fas fa-images mr-2 text-purple-600 dark:text-purple-400"></i>
      Equipment Images ({{ attachedImages.length }}/5)
    </h4>
    
    <!-- Current Images Display -->
    <div v-if="attachedImages.length" class="mb-4">
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
        <div v-for="(image, index) in attachedImages" :key="index" class="relative group">
          <img :src="image.url" :alt="image.alt" class="w-full h-24 object-cover rounded-lg" />
          <button @click="removeImage(index)" class="absolute top-1 right-1 p-1 bg-red-600 text-white rounded-full">
            <i class="fas fa-trash text-xs"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Image Upload Component -->
    <ImageUpload
      v-if="attachedImages.length < 5"
      upload-path="equipment"
      @upload-success="handleImageUpload"
      @upload-error="handleImageError"
    />
  </div>
</template>
```

#### Equipment Profile Display (`EquipmentList.vue`)

**Features:**
- Image gallery display showing up to 4 images per equipment item
- Responsive grid layout with "+X more" indicator
- Click-to-expand functionality
- Error handling for broken image links

### Bow Setup Image Integration

#### Bow Setup Creation/Edit Forms (`AddBowSetupModal.vue`)

**Features:**
- Image upload section with up to 3 images per bow setup
- Mobile-optimized grid layout for image previews
- Form data integration - images included in save payload
- Image initialization for editing mode via watch function

**Implementation:**
```javascript
// Image Upload Composable
const imageUpload = useImageUpload({
  context: 'bow_setup',
  maxFiles: 3,
  maxSize: 5
});

// Image handling methods
const handleImageUpload = (uploadResult) => {
  if (uploadResult && uploadResult.url) {
    attachedImages.value.push({
      url: uploadResult.url,
      cdnUrl: uploadResult.cdnUrl,
      originalName: uploadResult.originalName || 'bow-setup-image.jpg',
      alt: `${setupData.value.name || 'Bow Setup'} - Setup Image`
    });
  }
};
```

#### Bow Setup Details Display (`BowSetupOverview.vue`)

**Features:**
- Comprehensive image gallery as dedicated card section
- Responsive grid layout (1-3 columns based on screen size)
- Hover effects with expand icon for better UX
- Image count indicator and mobile-friendly design

### Journal Image Integration ✨ **NEW** (September 2025)

#### Comprehensive Journal Entry Image System

**Features:**
- **All Journal Entry Types**: Image upload functionality across all journal entry types (general, tuning_session, shooting_notes, setup_change, etc.)
- **Rich Image Display**: Grid layout with click-to-open modal viewer in `JournalEntryViewer.vue`
- **Legacy Support**: Enhanced `JournalEntryDialog.vue` with complete image upload capability
- **Database Integration**: Images stored as JSON arrays in `journal_entries.images` column (Migration 055)

#### Journal Entry Form Integration (`JournalEntryForm.vue`)

**Implementation:**
```vue
<template>
  <div class="journal-entry-form">
    <!-- Existing form fields -->
    
    <!-- Image Upload Section -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Images
      </label>
      <ImageUpload
        upload-path="journal"
        :max-files="10"
        :existing-images="formData.images || []"
        @upload-success="handleImageUpload"
        @upload-error="handleImageError"
        @image-removed="handleImageRemove"
      />
    </div>
  </div>
</template>

<script setup>
// Image handling methods
const handleImageUpload = (uploadResult) => {
  if (!formData.value.images) {
    formData.value.images = []
  }
  formData.value.images.push({
    url: uploadResult.url,
    cdnUrl: uploadResult.cdnUrl,
    originalName: uploadResult.originalName,
    alt: uploadResult.alt || 'Journal entry image',
    uploadedAt: new Date().toISOString()
  })
}
</script>
```

#### Journal Entry Viewer Enhancement (`JournalEntryViewer.vue`)

**Features:**
- **Image Grid Display**: Responsive grid layout for journal entry images
- **Click-to-Open Modal**: Full-size image viewer with navigation
- **Mobile Responsive**: Optimized for mobile viewing experience
- **Loading States**: Lazy loading with error handling

**Implementation:**
```vue
<template>
  <!-- Entry Images -->
  <div v-if="entry?.images && entry.images.length > 0" class="entry-images-section">
    <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
      <i class="fas fa-images mr-2 text-blue-600 dark:text-blue-400"></i>
      Images ({{ entry.images.length }})
    </h4>
    <div class="images-grid grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      <div v-for="(image, index) in entry.images" :key="index" class="image-item">
        <img 
          :src="image.url" 
          :alt="image.alt || 'Journal image'" 
          class="journal-image w-full h-32 object-cover rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
          @click="openImageModal(image, index)" 
          loading="lazy" 
        />
        <div v-if="image.alt" class="image-caption text-xs text-gray-600 dark:text-gray-400 mt-1 truncate">
          {{ image.alt }}
        </div>
      </div>
    </div>
  </div>
</template>
```

### Tuning Session Image Integration ✨ **NEW** (September 2025)

#### Interactive Tuning Session Image Storage

**Comprehensive Session-Level Image Management:**

All three tuning session types now include session-level image storage that automatically integrates with journal entries:

- **Paper Tuning**: `/pages/tuning-session/paper/[sessionId].vue`
- **Bareshaft Tuning**: `/pages/tuning-session/bareshaft/[sessionId].vue`  
- **Walkback Tuning**: `/pages/tuning-session/walkback/[sessionId].vue`

#### TuningImageUpload Component (`TuningImageUpload.vue`)

**Features:**
- **Context-Aware**: Specific to tuning session types (paper, bareshaft, walkback)
- **Quick Action Buttons**: Before/After shot capture buttons
- **Test-Specific Metadata**: Images tagged with test numbers and types
- **Session Integration**: Automatic inclusion in journal entry creation

**Implementation:**
```vue
<template>
  <div class="tuning-image-upload">
    <!-- Context Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <i :class="testTypeIcon" class="text-lg text-primary-600"></i>
        <h3 class="font-medium text-gray-900 dark:text-gray-100">
          {{ testTypeLabel }} Images
        </h3>
      </div>
      <div class="text-sm text-gray-500">
        {{ images.length }}/{{ maxFiles }} images
      </div>
    </div>

    <!-- Quick Action Buttons -->
    <div class="grid grid-cols-2 gap-3 mb-4">
      <button @click="captureImage('before')" class="quick-action-btn before">
        <i class="fas fa-camera text-blue-500"></i>
        <span>Before Shot</span>
      </button>
      <button @click="captureImage('after')" class="quick-action-btn after">
        <i class="fas fa-camera text-green-500"></i>
        <span>After Shot</span>
      </button>
    </div>

    <!-- Upload Area & Gallery -->
    <!-- ... drag & drop upload area ... -->
    <!-- ... uploaded images gallery ... -->
  </div>
</template>
```

#### Session-Level Image Storage Pattern

**All tuning session pages implement:**

```javascript
// Session-level image storage for journal entry
const sessionImages = ref([])

const handleImagesUploaded = (images) => {
  if (Array.isArray(images)) {
    sessionImages.value.push(...images.map(image => ({
      url: image.url,
      uploadedAt: new Date().toISOString(),
      alt: image.alt || `${testType} tuning test ${completedTests.value.length + 1}`,
      testNumber: completedTests.value.length + 1,
      testType: testType, // 'paper', 'bareshaft', 'walkback'
      imageLabel: image.imageLabel || 'Test Image'
    })))
  }
}

// Include images in journal entry creation
const createJournalEntry = async () => {
  const journalData = {
    title: `${testTypeLabel} Tuning Session`,
    content: generateSessionContent(),
    entry_type: 'tuning_session',
    session_type: testType,
    images: sessionImages.value, // ✨ Session images included
    // ... other fields
  }
  
  await journalApi.createEntry(journalData)
}
```

#### Database Schema Enhancement (Migration 055)

**Journal Entries Table Update:**
```sql
ALTER TABLE journal_entries ADD COLUMN images TEXT; -- JSON array of image objects
```

**Image Storage Format:**
```json
[
  {
    "url": "https://cdn.example.com/tuning/paper-test-1.jpg",
    "uploadedAt": "2025-09-11T10:30:00Z",
    "alt": "Paper tuning test 1 - Before adjustment",
    "testNumber": 1,
    "testType": "paper",
    "imageLabel": "Before Shot"
  },
  {
    "url": "https://cdn.example.com/tuning/paper-test-1-after.jpg", 
    "uploadedAt": "2025-09-11T10:35:00Z",
    "alt": "Paper tuning test 1 - After adjustment",
    "testNumber": 1,
    "testType": "paper",
    "imageLabel": "After Shot"
  }
]
```

## CDN Configuration

### Environment Variables

```bash
# CDN Configuration
CDN_PROVIDER=bunny  # Options: bunny, cloudinary, aws, local
BUNNY_CDN_API_KEY=your_bunny_api_key
BUNNY_CDN_BASE_URL=https://your-cdn.b-cdn.net
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
```

### Image Processing

- **Compression**: Automatic image compression (default 80% quality)
- **Format Support**: JPEG, JPG, PNG, WebP
- **Size Limits**: 5MB per image (configurable)
- **Naming**: SEO-friendly naming with context prefixes
- **Fallback**: Automatic local storage if CDN fails

## Usage Examples

### Equipment Image Upload

```javascript
// In equipment form component
import { useImageUpload } from '~/composables/useImageUpload';

const imageUpload = useImageUpload({
  context: 'equipment',
  maxFiles: 5,
  maxSize: 5
});

const handleImageUpload = (result) => {
  // Add to form data
  formData.images.push({
    url: result.url,
    cdnUrl: result.cdnUrl,
    alt: `${equipment.manufacturer} ${equipment.model} - Equipment Image`
  });
};
```

### Bow Setup Image Upload

```javascript
// In bow setup form component
const imageUpload = useImageUpload({
  context: 'bow_setup',
  maxFiles: 3,
  maxSize: 5
});

const payload = {
  // ... other setup data
  images: attachedImages.value.map(img => ({
    url: img.url,
    cdnUrl: img.cdnUrl,
    originalName: img.originalName,
    alt: img.alt
  }))
};
```

### Journal Entry Image Upload ✨ **NEW**

```javascript
// In journal entry form component  
import { useImageUpload } from '~/composables/useImageUpload';

const imageUpload = useImageUpload({
  context: 'journal',
  maxFiles: 10,
  maxSize: 5
});

const createJournalEntry = async () => {
  const payload = {
    title: 'My Shooting Session',
    content: 'Great session today...',
    entry_type: 'shooting_notes',
    images: attachedImages.value.map(img => ({
      url: img.url,
      cdnUrl: img.cdnUrl,
      originalName: img.originalName,
      alt: img.alt || 'Shooting session image',
      uploadedAt: new Date().toISOString()
    }))
  };
  
  await journalApi.createEntry(payload);
};
```

### Tuning Session Image Integration ✨ **NEW**

```javascript
// In tuning session component (paper/bareshaft/walkback)
const sessionImages = ref([]);

const handleImagesUploaded = (images) => {
  sessionImages.value.push(...images.map(image => ({
    url: image.url,
    uploadedAt: new Date().toISOString(),
    alt: `Bareshaft tuning test ${currentTestNumber.value}`,
    testNumber: currentTestNumber.value,
    testType: 'bareshaft',
    imageLabel: image.imageLabel || 'Test Image'
  })));
};

const saveAndCreateJournal = async () => {
  // Complete tuning session first
  await completeSession();
  
  // Create journal entry with session images
  const journalData = {
    title: 'Bareshaft Tuning Session',
    content: generateSessionSummary(),
    entry_type: 'tuning_session',
    session_type: 'bareshaft',
    images: sessionImages.value, // ✨ Automatic image inclusion
    session_metadata: {
      tests: completedTests.value,
      quality_score: sessionQuality.value
    }
  };
  
  await journalApi.createEntry(journalData);
};
```

## Best Practices

### Frontend
- Always validate file types and sizes before upload
- Provide visual feedback during upload process
- Implement error handling for failed uploads
- Use responsive image grids for mobile compatibility
- Include alt text for accessibility

### Backend
- Validate file types and sizes server-side
- Implement rate limiting for upload endpoints
- Use JWT authentication for all upload operations
- Store CDN URLs as fallback for local URLs
- Implement proper error logging

### Database
- Store both original and CDN URLs
- Include metadata (file size, mime type, upload session)
- Link images to appropriate entities via foreign keys
- Implement soft deletes for image cleanup

## Security Considerations

- **Authentication**: JWT required for all uploads
- **File Validation**: Server-side type and size validation
- **Rate Limiting**: Prevent abuse of upload endpoints
- **CDN Security**: Use signed URLs where applicable
- **Data Privacy**: Respect user privacy settings for images

## Performance Optimization

- **CDN Distribution**: Global CDN for fast image delivery
- **Image Compression**: Automatic compression during upload
- **Lazy Loading**: Implement lazy loading for image galleries
- **Caching**: Browser and CDN caching headers
- **Responsive Images**: Serve appropriate sizes for different devices

## Troubleshooting

### Common Issues

**Upload Failures**
- Check CDN configuration and API keys
- Verify file size and type restrictions
- Ensure JWT token is valid
- Check network connectivity

**Image Display Issues**
- Verify CDN URLs are accessible
- Check image error handling implementation
- Ensure proper alt text is provided
- Validate responsive grid layouts

**Performance Issues**
- Implement image lazy loading
- Optimize image compression settings
- Use appropriate CDN regions
- Monitor upload file sizes

## Migration Notes

**From Previous System**
- Legacy image URLs maintained for backward compatibility
- Automatic migration of existing equipment/setup images
- Database schema updates via migration 041
- CDN URL backfilling for existing images

**Recent Updates (September 2025)**
- **Migration 055**: Added images column to journal_entries table
- **Table Recreation Approach**: Handled SQLite foreign key constraints properly
- **Journal Image Integration**: All journal entry types now support comprehensive image upload
- **Tuning Session Image Storage**: Session-level images automatically linked to journal entries
- **Data Preservation**: All existing journal entries maintained during schema update

**Future Enhancements**
- Image editing capabilities (crop, rotate, filters)
- Batch upload functionality
- Advanced image search and tagging
- Integration with AI-powered image analysis
- Cross-session image correlation for tuning progress tracking
- Automatic before/after image comparison for tuning sessions