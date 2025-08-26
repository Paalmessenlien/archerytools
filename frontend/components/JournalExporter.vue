<template>
  <div class="journal-exporter">
    <div class="exporter-header">
      <h3 class="exporter-title">
        <md-icon class="export-icon">download</md-icon>
        Export Journal Entries
      </h3>
      <p class="exporter-subtitle">Export your archery journal in various formats</p>
    </div>

    <!-- Export Options -->
    <div class="export-options">
      <div class="export-format-section">
        <h4 class="section-title">Export Format</h4>
        <div class="format-options">
          <label 
            v-for="format in exportFormats" 
            :key="format.value"
            class="format-option"
            :class="{ selected: selectedFormat === format.value }"
          >
            <input 
              type="radio" 
              :value="format.value"
              v-model="selectedFormat"
              class="format-radio"
            />
            <div class="format-content">
              <md-icon class="format-icon">{{ format.icon }}</md-icon>
              <div class="format-details">
                <span class="format-name">{{ format.name }}</span>
                <span class="format-description">{{ format.description }}</span>
              </div>
            </div>
          </label>
        </div>
      </div>

      <!-- Entry Selection -->
      <div class="entry-selection-section">
        <h4 class="section-title">What to Export</h4>
        <div class="selection-options">
          <label class="selection-option">
            <input 
              type="radio" 
              value="all"
              v-model="exportScope"
              class="selection-radio"
            />
            <div class="selection-content">
              <span class="selection-name">All Entries</span>
              <span class="selection-description">Export all {{ totalEntries }} journal entries</span>
            </div>
          </label>
          
          <label class="selection-option">
            <input 
              type="radio" 
              value="favorites"
              v-model="exportScope"
              class="selection-radio"
            />
            <div class="selection-content">
              <span class="selection-name">Favorites Only</span>
              <span class="selection-description">Export {{ favoriteCount }} starred entries</span>
            </div>
          </label>
          
          <label class="selection-option">
            <input 
              type="radio" 
              value="date_range"
              v-model="exportScope"
              class="selection-radio"
            />
            <div class="selection-content">
              <span class="selection-name">Date Range</span>
              <span class="selection-description">Export entries from a specific period</span>
            </div>
          </label>
          
          <label class="selection-option">
            <input 
              type="radio" 
              value="selected"
              v-model="exportScope"
              class="selection-radio"
            />
            <div class="selection-content">
              <span class="selection-name">Selected Entries</span>
              <span class="selection-description">Choose specific entries to export</span>
            </div>
          </label>
        </div>
      </div>

      <!-- Date Range Selection (when applicable) -->
      <div v-if="exportScope === 'date_range'" class="date-range-section">
        <h4 class="section-title">Date Range</h4>
        <div class="date-inputs">
          <div class="date-field">
            <label class="date-label">From</label>
            <input 
              type="date" 
              v-model="dateRange.start"
              class="date-input"
              :max="dateRange.end || today"
            />
          </div>
          <div class="date-field">
            <label class="date-label">To</label>
            <input 
              type="date" 
              v-model="dateRange.end"
              class="date-input"
              :min="dateRange.start"
              :max="today"
            />
          </div>
        </div>
        <div v-if="dateRangeEntries.length" class="date-range-preview">
          <span class="preview-text">{{ dateRangeEntries.length }} entries in selected range</span>
        </div>
      </div>

      <!-- Entry Selection (when applicable) -->
      <div v-if="exportScope === 'selected'" class="entry-selection-list">
        <h4 class="section-title">Select Entries</h4>
        <div class="entry-search">
          <md-outlined-text-field
            v-model="searchQuery"
            placeholder="Search entries..."
            class="search-input"
          >
            <md-icon slot="leading-icon">search</md-icon>
          </md-outlined-text-field>
        </div>
        <div class="selectable-entries">
          <div class="entries-header">
            <label class="select-all-option">
              <input 
                type="checkbox" 
                :checked="allVisibleSelected"
                @change="toggleAllVisible"
                class="select-checkbox"
              />
              <span>Select All Visible ({{ filteredEntries.length }})</span>
            </label>
          </div>
          <div class="entries-list">
            <label 
              v-for="entry in filteredEntries" 
              :key="entry.id"
              class="entry-option"
            >
              <input 
                type="checkbox" 
                :value="entry.id"
                v-model="selectedEntries"
                class="entry-checkbox"
              />
              <div class="entry-summary">
                <div class="entry-title-row">
                  <span class="entry-title">{{ entry.title }}</span>
                  <span class="entry-date">{{ formatDate(entry.created_at) }}</span>
                </div>
                <div class="entry-meta">
                  <span class="entry-type">{{ formatEntryType(entry.entry_type) }}</span>
                  <span v-if="entry.setup_name" class="entry-setup">{{ entry.setup_name }}</span>
                </div>
              </div>
            </label>
          </div>
        </div>
      </div>

      <!-- Export Settings -->
      <div class="export-settings-section">
        <h4 class="section-title">Export Settings</h4>
        <div class="settings-options">
          <label class="setting-option">
            <input 
              type="checkbox" 
              v-model="exportSettings.includeImages"
              class="setting-checkbox"
            />
            <span>Include Images</span>
          </label>
          
          <label class="setting-option">
            <input 
              type="checkbox" 
              v-model="exportSettings.includeLinkedChanges"
              class="setting-checkbox"
            />
            <span>Include Linked Changes</span>
          </label>
          
          <label class="setting-option">
            <input 
              type="checkbox" 
              v-model="exportSettings.includeTags"
              class="setting-checkbox"
            />
            <span>Include Tags</span>
          </label>
          
          <label class="setting-option">
            <input 
              type="checkbox" 
              v-model="exportSettings.includePrivate"
              class="setting-checkbox"
            />
            <span>Include Private Entries</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Export Preview -->
    <div v-if="previewEntries.length" class="export-preview">
      <h4 class="section-title">Export Preview</h4>
      <div class="preview-stats">
        <div class="preview-stat">
          <span class="stat-value">{{ previewEntries.length }}</span>
          <span class="stat-label">Entries</span>
        </div>
        <div class="preview-stat">
          <span class="stat-value">{{ totalImages }}</span>
          <span class="stat-label">Images</span>
        </div>
        <div class="preview-stat">
          <span class="stat-value">{{ estimatedSize }}</span>
          <span class="stat-label">Est. Size</span>
        </div>
      </div>
      
      <div class="preview-entries">
        <div 
          v-for="entry in previewEntries.slice(0, 3)" 
          :key="entry.id"
          class="preview-entry"
        >
          <span class="preview-entry-title">{{ entry.title }}</span>
          <span class="preview-entry-date">{{ formatDate(entry.created_at) }}</span>
        </div>
        <div v-if="previewEntries.length > 3" class="preview-more">
          +{{ previewEntries.length - 3 }} more entries
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="exporter-actions">
      <CustomButton @click="$emit('close')" variant="outlined">
        Cancel
      </CustomButton>
      <CustomButton 
        @click="startExport" 
        variant="primary"
        :disabled="!canExport || isExporting"
        :class="{ 'is-loading': isExporting }"
      >
        <md-circular-progress v-if="isExporting" indeterminate class="btn-loading"></md-circular-progress>
        <md-icon v-else>download</md-icon>
        <span v-if="!isExporting">Export {{ selectedFormat.toUpperCase() }}</span>
        <span v-else>Exporting...</span>
      </CustomButton>
    </div>

    <!-- Export Progress -->
    <div v-if="isExporting" class="export-progress">
      <div class="progress-header">
        <span class="progress-title">Exporting Journal</span>
        <span class="progress-percentage">{{ exportProgress }}%</span>
      </div>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: exportProgress + '%' }"
        ></div>
      </div>
      <div class="progress-status">{{ exportStatus }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'
import { useGlobalNotifications } from '@/composables/useNotificationSystem'

const props = defineProps({
  entries: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'export-complete'])

// Composables
const api = useApi()
const notifications = useGlobalNotifications()

// Reactive state
const selectedFormat = ref('pdf')
const exportScope = ref('all')
const selectedEntries = ref([])
const searchQuery = ref('')
const dateRange = ref({
  start: '',
  end: ''
})
const exportSettings = ref({
  includeImages: true,
  includeLinkedChanges: true,
  includeTags: true,
  includePrivate: false
})
const isExporting = ref(false)
const exportProgress = ref(0)
const exportStatus = ref('')

// Export format options
const exportFormats = [
  {
    value: 'pdf',
    name: 'PDF Document',
    description: 'Professional document with images and formatting',
    icon: 'picture_as_pdf'
  },
  {
    value: 'html',
    name: 'HTML Archive', 
    description: 'Web page with full formatting and images',
    icon: 'language'
  },
  {
    value: 'markdown',
    name: 'Markdown',
    description: 'Plain text format with basic formatting',
    icon: 'article'
  },
  {
    value: 'json',
    name: 'JSON Data',
    description: 'Raw data for importing into other applications',
    icon: 'data_object'
  }
]

// Computed properties
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const totalEntries = computed(() => props.entries.length)

const favoriteCount = computed(() => {
  return props.entries.filter(entry => entry.is_favorite).length
})

const filteredEntries = computed(() => {
  let entries = props.entries
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    entries = entries.filter(entry => 
      entry.title.toLowerCase().includes(query) ||
      entry.content.toLowerCase().includes(query) ||
      (entry.tags && entry.tags.some(tag => tag.toLowerCase().includes(query)))
    )
  }
  
  return entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const allVisibleSelected = computed(() => {
  return filteredEntries.value.length > 0 && 
         filteredEntries.value.every(entry => selectedEntries.value.includes(entry.id))
})

const dateRangeEntries = computed(() => {
  if (!dateRange.value.start || !dateRange.value.end) return []
  
  const start = new Date(dateRange.value.start)
  const end = new Date(dateRange.value.end)
  end.setHours(23, 59, 59, 999) // End of day
  
  return props.entries.filter(entry => {
    const entryDate = new Date(entry.created_at)
    return entryDate >= start && entryDate <= end
  })
})

const previewEntries = computed(() => {
  let entries = []
  
  switch (exportScope.value) {
    case 'all':
      entries = props.entries
      break
    case 'favorites':
      entries = props.entries.filter(entry => entry.is_favorite)
      break
    case 'date_range':
      entries = dateRangeEntries.value
      break
    case 'selected':
      entries = props.entries.filter(entry => selectedEntries.value.includes(entry.id))
      break
  }
  
  // Filter out private entries if not included
  if (!exportSettings.value.includePrivate) {
    entries = entries.filter(entry => !entry.is_private)
  }
  
  return entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const totalImages = computed(() => {
  if (!exportSettings.value.includeImages) return 0
  
  return previewEntries.value.reduce((total, entry) => {
    return total + (entry.images ? entry.images.length : 0)
  }, 0)
})

const estimatedSize = computed(() => {
  let size = previewEntries.value.length * 5 // Base size per entry (KB)
  
  if (exportSettings.value.includeImages) {
    size += totalImages.value * 500 // Assume 500KB per image
  }
  
  if (size < 1024) {
    return `${Math.round(size)} KB`
  } else {
    return `${(size / 1024).toFixed(1)} MB`
  }
})

const canExport = computed(() => {
  return previewEntries.value.length > 0 && !isExporting.value
})

// Methods
const toggleAllVisible = (event) => {
  if (event.target.checked) {
    const visibleIds = filteredEntries.value.map(entry => entry.id)
    selectedEntries.value = [...new Set([...selectedEntries.value, ...visibleIds])]
  } else {
    const visibleIds = new Set(filteredEntries.value.map(entry => entry.id))
    selectedEntries.value = selectedEntries.value.filter(id => !visibleIds.has(id))
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatEntryType = (type) => {
  const typeLabels = {
    general: 'General',
    setup_change: 'Setup Change',
    equipment_change: 'Equipment',
    arrow_change: 'Arrow',
    tuning_session: 'Tuning',
    shooting_notes: 'Shooting',
    maintenance: 'Maintenance',
    upgrade: 'Upgrade'
  }
  return typeLabels[type] || 'General'
}

const startExport = async () => {
  if (!canExport.value) return
  
  isExporting.value = true
  exportProgress.value = 0
  exportStatus.value = 'Preparing export...'
  
  try {
    const exportData = {
      format: selectedFormat.value,
      entries: previewEntries.value.map(entry => entry.id),
      settings: exportSettings.value,
      scope: exportScope.value
    }
    
    // Update progress
    exportProgress.value = 25
    exportStatus.value = 'Collecting entries...'
    await new Promise(resolve => setTimeout(resolve, 500))
    
    exportProgress.value = 50
    exportStatus.value = 'Processing images...'
    await new Promise(resolve => setTimeout(resolve, 800))
    
    exportProgress.value = 75
    exportStatus.value = `Generating ${selectedFormat.value.toUpperCase()}...`
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Make API call to generate export
    const response = await api.post('/journal/export', exportData)
    
    if (response.success) {
      exportProgress.value = 100
      exportStatus.value = 'Export complete!'
      
      // Trigger download
      if (response.data.download_url) {
        const link = document.createElement('a')
        link.href = response.data.download_url
        link.download = response.data.filename || `journal_export.${selectedFormat.value}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
      
      notifications.showSuccess(`Journal exported successfully as ${selectedFormat.value.toUpperCase()}`)
      emit('export-complete', response.data)
      
      setTimeout(() => {
        emit('close')
      }, 2000)
      
    } else {
      throw new Error(response.error || 'Export failed')
    }
    
  } catch (error) {
    console.error('Export error:', error)
    notifications.showError(`Export failed: ${error.message}`)
    exportStatus.value = 'Export failed'
  } finally {
    setTimeout(() => {
      isExporting.value = false
      exportProgress.value = 0
      exportStatus.value = ''
    }, 3000)
  }
}

// Initialize date range to last 30 days
onMounted(() => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  
  dateRange.value = {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0]
  }
})
</script>

<style scoped>
.journal-exporter {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}

.exporter-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.exporter-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.export-icon {
  color: var(--md-sys-color-primary);
  font-size: 1.5rem;
}

.exporter-subtitle {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.9rem;
}

/* Export Options */
.export-options {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-title {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.format-options,
.selection-options {
  display: grid;
  gap: 1rem;
}

.format-option,
.selection-option {
  display: block;
  cursor: pointer;
}

.format-option {
  border: 2px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  padding: 1rem;
  background: var(--md-sys-color-surface-container-lowest);
  transition: all 0.2s ease;
}

.format-option:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container);
}

.format-option.selected {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
}

.format-radio,
.selection-radio {
  display: none;
}

.format-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.format-icon {
  font-size: 1.5rem;
  color: var(--md-sys-color-primary);
  flex-shrink: 0;
}

.format-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.format-name {
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.format-description {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
}

.selection-option {
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface);
  transition: all 0.2s ease;
}

.selection-option:hover {
  background: var(--md-sys-color-surface-container);
  border-color: var(--md-sys-color-primary);
}

.selection-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-left: 1.5rem;
}

.selection-name {
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
}

.selection-description {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Date Range */
.date-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.date-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.date-label {
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  font-size: 0.875rem;
}

.date-input {
  padding: 0.75rem;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  font-family: inherit;
}

.date-input:focus {
  outline: none;
  border-color: var(--md-sys-color-primary);
}

.date-range-preview {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  border-radius: 6px;
  font-size: 0.875rem;
  text-align: center;
}

/* Entry Selection */
.search-input {
  width: 100%;
  margin-bottom: 1rem;
}

.entries-header {
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.select-all-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.entries-list {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.entry-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.entry-option:hover {
  background: var(--md-sys-color-surface-container);
}

.entry-summary {
  flex: 1;
  min-width: 0;
}

.entry-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.entry-title {
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.entry-date {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
  flex-shrink: 0;
  margin-left: 1rem;
}

.entry-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Settings */
.settings-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.setting-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

/* Export Preview */
.export-preview {
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--md-sys-color-outline-variant);
  margin-top: 2rem;
}

.preview-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.preview-stat {
  text-align: center;
  padding: 1rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--md-sys-color-primary);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

.preview-entries {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-entry {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 6px;
}

.preview-entry-title {
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
}

.preview-entry-date {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

.preview-more {
  text-align: center;
  padding: 0.5rem;
  color: var(--md-sys-color-on-surface-variant);
  font-style: italic;
}

/* Export Progress */
.export-progress {
  background: var(--md-sys-color-primary-container);
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-title {
  font-weight: 500;
  color: var(--md-sys-color-on-primary-container);
}

.progress-percentage {
  font-weight: 600;
  color: var(--md-sys-color-on-primary-container);
}

.progress-bar {
  height: 6px;
  background: var(--md-sys-color-primary);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
  opacity: 0.3;
}

.progress-fill {
  height: 100%;
  background: var(--md-sys-color-on-primary-container);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-status {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-primary-container);
  text-align: center;
}

/* Action Buttons */
.exporter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.btn-loading {
  width: 16px;
  height: 16px;
  margin-right: 0.5rem;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-exporter {
    padding: 1rem;
  }
  
  .date-inputs {
    grid-template-columns: 1fr;
  }
  
  .preview-stats {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .exporter-actions {
    flex-direction: column;
  }
  
  .entry-title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .entry-date {
    margin-left: 0;
  }
}
</style>