<template>
  <div class="unified-journal-list">
    <!-- Header Section -->
    <div class="list-header" v-if="showHeader">
      <div class="header-content">
        <div class="header-info">
          <md-icon :class="`text-${contextColor}-600`">{{ contextIcon }}</md-icon>
          <div class="header-text">
            <h3 class="header-title">{{ title || 'Journal Entries' }}</h3>
            <p class="header-subtitle" v-if="subtitle">{{ subtitle }}</p>
          </div>
        </div>
        
        <!-- Entry count -->
        <div class="entry-count">
          {{ filteredEntries.length }} {{ filteredEntries.length === 1 ? 'entry' : 'entries' }}
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions" v-if="showActions">
        <md-icon-button 
          @click="$emit('create-entry')"
          aria-label="Add new journal entry"
          class="add-entry-btn"
        >
          <md-icon>add</md-icon>
        </md-icon-button>
        
        <md-icon-button 
          v-if="allowFiltering"
          @click="toggleFilters"
          :class="{ 'active': showFilters }"
          aria-label="Toggle filters"
        >
          <md-icon>tune</md-icon>
        </md-icon-button>
      </div>
    </div>

    <!-- Simple Filter Section -->
    <div v-if="showFilters && allowFiltering" class="filters-section">
      <div class="filter-chips">
        <!-- Entry Type Filter -->
        <md-filter-chip
          v-if="availableTypes.length > 1"
          :selected="selectedType !== null"
          :removable="selectedType !== null"
          @click="toggleTypeFilter"
          @remove="clearTypeFilter"
          class="type-filter"
        >
          <md-icon slot="icon">category</md-icon>
          {{ selectedType ? getEntryTypeLabel(selectedType) : 'All Types' }}
        </md-filter-chip>

        <!-- Tuning Sessions Filter -->
        <md-filter-chip
          :selected="showOnlyTuningSessions"
          :removable="showOnlyTuningSessions"
          @click="toggleTuningFilter"
          @remove="clearTuningFilter"
          class="tuning-filter"
        >
          <md-icon slot="icon">tune</md-icon>
          Tuning Sessions
        </md-filter-chip>

        <!-- Recent Filter -->
        <md-filter-chip
          :selected="showOnlyRecent"
          :removable="showOnlyRecent"
          @click="toggleRecentFilter"
          @remove="clearRecentFilter"
          class="recent-filter"
        >
          <md-icon slot="icon">schedule</md-icon>
          Recent (7 days)
        </md-filter-chip>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <md-circular-progress indeterminate></md-circular-progress>
      <span class="loading-text">Loading entries...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredEntries.length === 0" class="empty-state">
      <div class="empty-content">
        <md-icon class="empty-icon">{{ entries.length === 0 ? 'book' : 'filter_list_off' }}</md-icon>
        <h4 class="empty-title">
          {{ entries.length === 0 ? 'No journal entries yet' : 'No entries match filters' }}
        </h4>
        <p class="empty-subtitle">
          {{ entries.length === 0 
            ? (context ? `No journal entries found for this ${context}.` : 'Start tracking your archery journey.')
            : 'Try adjusting your filters to see more entries.'
          }}
        </p>
        
        <md-button 
          v-if="entries.length === 0 && showActions"
          variant="filled"
          @click="$emit('create-entry')"
          class="empty-action"
        >
          <md-icon slot="icon">add</md-icon>
          Add First Entry
        </md-button>
      </div>
    </div>

    <!-- Entries List -->
    <div v-else class="entries-list">
      <div 
        v-for="entry in displayedEntries" 
        :key="entry.id"
        class="entry-item"
        @click="viewEntry(entry)"
      >
        <!-- Entry Card -->
        <div class="entry-card" :class="getEntryClasses(entry)">
          <!-- Entry Header -->
          <div class="entry-header">
            <div class="entry-meta">
              <div class="entry-type-badge" :class="`type-${entry.entry_type}`">
                <md-icon class="type-icon">{{ getEntryTypeIcon(entry.entry_type) }}</md-icon>
                <span class="type-label">{{ getEntryTypeLabel(entry.entry_type) }}</span>
              </div>
              <span class="entry-date">{{ formatRelativeDate(entry.created_at) }}</span>
            </div>
            
            <div class="entry-actions" @click.stop>
              <md-icon-button 
                v-if="entry.is_favorite !== undefined"
                @click="$emit('toggle-favorite', entry)"
                :class="{ 'is-favorite': entry.is_favorite }"
                aria-label="Toggle favorite"
                class="favorite-btn"
              >
                <md-icon>{{ entry.is_favorite ? 'star' : 'star_border' }}</md-icon>
              </md-icon-button>
              
              <md-icon-button 
                v-if="allowEdit"
                @click="$emit('edit-entry', entry)"
                aria-label="Edit entry"
                class="edit-btn"
              >
                <md-icon>edit</md-icon>
              </md-icon-button>
            </div>
          </div>

          <!-- Entry Content Preview -->
          <div class="entry-content">
            <h4 class="entry-title">{{ entry.title }}</h4>
            
            <!-- Special content for tuning sessions -->
            <div v-if="isTuningEntry(entry)" class="tuning-preview">
              <div class="tuning-stats">
                <div class="stat-item" v-if="entry.session_data?.session_quality">
                  <md-icon class="stat-icon">trending_up</md-icon>
                  <span class="stat-value">{{ Math.round(entry.session_data.session_quality) }}% quality</span>
                </div>
                <div class="stat-item" v-if="entry.session_data?.test_results?.length">
                  <md-icon class="stat-icon">science</md-icon>
                  <span class="stat-value">{{ entry.session_data.test_results.length }} tests</span>
                </div>
                <div class="stat-item" v-if="entry.session_data?.most_common_pattern">
                  <md-icon class="stat-icon">my_location</md-icon>
                  <span class="stat-value">{{ entry.session_data.most_common_pattern }}</span>
                </div>
                <div class="stat-item" v-if="entry.session_data?.drift_analysis?.drift_rate_cm_per_m">
                  <md-icon class="stat-icon">timeline</md-icon>
                  <span class="stat-value">{{ entry.session_data.drift_analysis.drift_rate_cm_per_m }} cm/m drift</span>
                </div>
              </div>
            </div>
            
            <!-- Regular content preview -->
            <div v-else class="content-preview">
              <p class="preview-text">{{ getContentPreview(entry.content) }}</p>
            </div>

            <!-- Entry Tags -->
            <div v-if="entry.tags && entry.tags.length" class="entry-tags">
              <md-chip 
                v-for="tag in entry.tags.slice(0, 3)" 
                :key="tag"
                class="entry-tag"
                variant="outline"
                size="small"
              >
                {{ tag }}
              </md-chip>
              <span v-if="entry.tags.length > 3" class="more-tags">
                +{{ entry.tags.length - 3 }} more
              </span>
            </div>
          </div>

          <!-- Equipment Link (if applicable) -->
          <div v-if="entry.bow_setup_name" class="equipment-link">
            <md-icon class="equipment-icon">sports_martial_arts</md-icon>
            <span class="equipment-name">{{ entry.bow_setup_name }}</span>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMoreEntries" class="load-more-section">
        <md-button
          variant="outlined"
          :disabled="loadingMore"
          @click="loadMore"
          class="load-more-btn"
        >
          <md-icon slot="icon" v-if="!loadingMore">expand_more</md-icon>
          <md-circular-progress v-if="loadingMore" indeterminate size="20"></md-circular-progress>
          {{ loadingMore ? 'Loading...' : 'Load More' }}
        </md-button>
      </div>
    </div>

    <!-- Journal Entry Detail Viewer -->
    <JournalEntryDetailViewer
      v-if="selectedEntry"
      :entry="selectedEntry"
      :show="showDetailViewer"
      @close="closeDetailViewer"
      @edit="handleEditFromViewer"
      @delete="handleDeleteFromViewer"
      @favorite="$emit('toggle-favorite', selectedEntry)"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import JournalEntryDetailViewer from './JournalEntryDetailViewer.vue'

// Props
const props = defineProps({
  entries: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingMore: {
    type: Boolean,
    default: false
  },
  hasMoreEntries: {
    type: Boolean,
    default: false
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  allowEdit: {
    type: Boolean,
    default: true
  },
  allowFiltering: {
    type: Boolean,
    default: true
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  context: {
    type: String,
    default: ''
  },
  contextIcon: {
    type: String,
    default: 'book'
  },
  contextColor: {
    type: String,
    default: 'blue'
  },
  maxDisplayed: {
    type: Number,
    default: 50
  },
  filterContext: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits([
  'view-entry', 
  'edit-entry', 
  'delete-entry', 
  'create-entry', 
  'toggle-favorite',
  'load-more'
])

// Reactive state
const showFilters = ref(false)
const selectedType = ref(null)
const showOnlyTuningSessions = ref(false)
const showOnlyRecent = ref(false)
const selectedEntry = ref(null)
const showDetailViewer = ref(false)

// Entry type mapping
const entryTypeMap = {
  general: { label: 'General', icon: 'notes' },
  practice_session: { label: 'Practice', icon: 'sports_martial_arts' },
  equipment_change: { label: 'Equipment', icon: 'build' },
  bareshaft_tuning_session: { label: 'Bareshaft Tuning', icon: 'tune' },
  walkback_tuning_session: { label: 'Walkback Tuning', icon: 'timeline' },
  paper_tuning_session: { label: 'Paper Tuning', icon: 'article' },
  tuning_session: { label: 'Tuning Session', icon: 'tune' },
  competition: { label: 'Competition', icon: 'emoji_events' },
  maintenance: { label: 'Maintenance', icon: 'handyman' },
  observation: { label: 'Observation', icon: 'visibility' }
}

// Computed properties
const availableTypes = computed(() => {
  const types = [...new Set(props.entries.map(entry => entry.entry_type))]
  return types.sort()
})

const filteredEntries = computed(() => {
  let filtered = [...props.entries]
  
  // Filter by context (e.g., bow setup)
  if (props.filterContext.bow_setup_id) {
    filtered = filtered.filter(entry => entry.bow_setup_id === props.filterContext.bow_setup_id)
  }
  
  // Filter by type
  if (selectedType.value) {
    filtered = filtered.filter(entry => entry.entry_type === selectedType.value)
  }
  
  // Filter tuning sessions only
  if (showOnlyTuningSessions.value) {
    filtered = filtered.filter(entry => isTuningEntry(entry))
  }
  
  // Filter recent entries
  if (showOnlyRecent.value) {
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    filtered = filtered.filter(entry => new Date(entry.created_at) >= weekAgo)
  }
  
  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const displayedEntries = computed(() => {
  return filteredEntries.value.slice(0, props.maxDisplayed)
})

// Helper functions
const isTuningEntry = (entry) => {
  return entry.entry_type?.includes('tuning') || entry.session_data?.tuning_type
}

const getEntryTypeIcon = (type) => {
  return entryTypeMap[type]?.icon || 'notes'
}

const getEntryTypeLabel = (type) => {
  return entryTypeMap[type]?.label || type.replace(/_/g, ' ')
}

const getEntryClasses = (entry) => {
  return {
    'tuning-entry': isTuningEntry(entry),
    'has-equipment': !!entry.bow_setup_name,
    'is-favorite': entry.is_favorite
  }
}

const getContentPreview = (content) => {
  if (!content) return 'No content'
  
  // Remove markdown formatting for preview
  const plainText = content
    .replace(/#+\s/g, '') // Remove headers
    .replace(/\*\*([^*]+)\*\*/g, '$1') // Remove bold
    .replace(/\*([^*]+)\*/g, '$1') // Remove italic
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links
    .replace(/`([^`]+)`/g, '$1') // Remove code
    .trim()
  
  return plainText.length > 120 ? plainText.substring(0, 120) + '...' : plainText
}

const formatRelativeDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  
  return date.toLocaleDateString()
}

// Filter functions
const toggleFilters = () => {
  showFilters.value = !showFilters.value
}

const toggleTypeFilter = () => {
  if (selectedType.value) {
    selectedType.value = null
  } else {
    // Show type selection menu or cycle through types
    const types = availableTypes.value
    if (types.length > 0) {
      selectedType.value = types[0]
    }
  }
}

const clearTypeFilter = () => {
  selectedType.value = null
}

const toggleTuningFilter = () => {
  showOnlyTuningSessions.value = !showOnlyTuningSessions.value
}

const clearTuningFilter = () => {
  showOnlyTuningSessions.value = false
}

const toggleRecentFilter = () => {
  showOnlyRecent.value = !showOnlyRecent.value
}

const clearRecentFilter = () => {
  showOnlyRecent.value = false
}

// Entry actions
const viewEntry = (entry) => {
  selectedEntry.value = entry
  showDetailViewer.value = true
  emit('entry:view', entry)
}

const closeDetailViewer = () => {
  showDetailViewer.value = false
  selectedEntry.value = null
}

const handleEditFromViewer = () => {
  if (selectedEntry.value) {
    emit('edit-entry', selectedEntry.value)
    closeDetailViewer()
  }
}

const handleDeleteFromViewer = () => {
  if (selectedEntry.value) {
    emit('delete-entry', selectedEntry.value)
    closeDetailViewer()
  }
}

const loadMore = () => {
  emit('load-more')
}
</script>

<style scoped>
.unified-journal-list {
  @apply w-full;
}

/* Header Styles */
.list-header {
  @apply bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4;
}

.header-content {
  @apply flex items-center justify-between;
}

.header-info {
  @apply flex items-center gap-3;
}

.header-info md-icon {
  @apply text-2xl;
}

.header-text {
  @apply flex flex-col;
}

.header-title {
  @apply text-lg font-semibold text-gray-900 dark:text-gray-100 m-0;
}

.header-subtitle {
  @apply text-sm text-gray-600 dark:text-gray-400 m-0;
}

.entry-count {
  @apply text-sm text-gray-500 dark:text-gray-400 font-medium;
}

.quick-actions {
  @apply flex items-center gap-2;
}

.add-entry-btn {
  @apply text-blue-600 dark:text-blue-400;
}

/* Filters Section */
.filters-section {
  @apply bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 mb-4;
}

.filter-chips {
  @apply flex flex-wrap gap-2;
}

/* Loading and Empty States */
.loading-state {
  @apply flex items-center justify-center gap-3 py-8 text-gray-600 dark:text-gray-400;
}

.loading-text {
  @apply text-sm;
}

.empty-state {
  @apply flex flex-col items-center justify-center py-12 text-center;
}

.empty-content {
  @apply max-w-sm space-y-4;
}

.empty-icon {
  @apply text-4xl text-gray-400 dark:text-gray-500;
}

.empty-title {
  @apply text-lg font-semibold text-gray-900 dark:text-gray-100 m-0;
}

.empty-subtitle {
  @apply text-gray-600 dark:text-gray-400 m-0;
}

.empty-action {
  @apply mt-4;
}

/* Entries List */
.entries-list {
  @apply space-y-3;
}

.entry-item {
  @apply cursor-pointer transform transition-transform hover:scale-[1.01];
}

.entry-card {
  @apply bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-3 
         hover:shadow-md transition-shadow;
}

.entry-card.tuning-entry {
  @apply border-l-4 border-l-orange-400 dark:border-l-orange-500;
}

.entry-card.is-favorite {
  @apply bg-yellow-50 dark:bg-yellow-900/20;
}

/* Entry Header */
.entry-header {
  @apply flex items-center justify-between;
}

.entry-meta {
  @apply flex items-center gap-3;
}

.entry-type-badge {
  @apply flex items-center gap-2 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-xs font-medium;
}

.entry-type-badge.type-bareshaft_tuning_session,
.entry-type-badge.type-walkback_tuning_session,
.entry-type-badge.type-paper_tuning_session {
  @apply bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300;
}

.type-icon {
  @apply text-sm;
}

.entry-date {
  @apply text-xs text-gray-500 dark:text-gray-400;
}

.entry-actions {
  @apply flex items-center gap-1;
}

.favorite-btn.is-favorite {
  @apply text-yellow-500;
}

.edit-btn {
  @apply text-gray-400 hover:text-gray-600 dark:hover:text-gray-300;
}

/* Entry Content */
.entry-content {
  @apply space-y-3;
}

.entry-title {
  @apply text-base font-semibold text-gray-900 dark:text-gray-100 m-0;
}

/* Tuning Preview */
.tuning-preview {
  @apply space-y-2;
}

.tuning-stats {
  @apply flex flex-wrap gap-3;
}

.stat-item {
  @apply flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400;
}

.stat-icon {
  @apply text-sm;
}

.stat-value {
  @apply font-medium;
}

/* Content Preview */
.content-preview {
  @apply text-sm text-gray-600 dark:text-gray-400;
}

.preview-text {
  @apply m-0 line-clamp-2;
}

/* Entry Tags */
.entry-tags {
  @apply flex items-center gap-2 flex-wrap;
}

.entry-tag {
  @apply text-xs;
}

.more-tags {
  @apply text-xs text-gray-500 dark:text-gray-400 font-medium;
}

/* Equipment Link */
.equipment-link {
  @apply flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 
         rounded-full px-3 py-1 w-fit;
}

.equipment-icon {
  @apply text-sm;
}

/* Load More */
.load-more-section {
  @apply flex justify-center mt-6;
}

.load-more-btn {
  @apply px-6;
}

/* Mobile Responsive */
@media (max-width: 640px) {
  .header-content {
    @apply flex-col items-start gap-3;
  }
  
  .quick-actions {
    @apply self-end;
  }
  
  .filter-chips {
    @apply gap-1;
  }
  
  .tuning-stats {
    @apply gap-2;
  }
  
  .stat-item {
    @apply text-xs;
  }
}
</style>