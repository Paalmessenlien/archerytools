<template>
  <div class="base-journal-view">
    <!-- Mobile-First Journal Header -->
    <div class="journal-header" :class="headerClasses">
      <!-- Header Content -->
      <div class="header-content">
        <div class="header-info">
          <div class="header-icon" :class="contextColorClasses">
            <md-icon>{{ contextIcon }}</md-icon>
          </div>
          <div class="header-text">
            <h3 class="header-title">{{ title }}</h3>
            <p class="header-subtitle" v-if="subtitle">{{ subtitle }}</p>
          </div>
        </div>
        
        <!-- Mobile Action Button -->
        <div class="header-actions">
          <md-fab
            variant="primary"
            size="small"
            @click="toggleQuickEntry"
            :class="{ 'active': showQuickEntry }"
            aria-label="Add journal entry"
          >
            <md-icon>{{ showQuickEntry ? 'close' : 'add' }}</md-icon>
          </md-fab>
        </div>
      </div>

      <!-- Stats Pills (Mobile-Optimized) -->
      <div v-if="stats && Object.keys(stats).length" class="stats-container">
        <div class="stats-pills">
          <div 
            v-for="(stat, key) in stats" 
            :key="key"
            class="stat-pill"
            :class="`stat-${key}`"
          >
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Entry Form (Collapsible with Smooth Animation) -->
    <div class="quick-entry-container" :class="{ 'expanded': showQuickEntry }">
      <div class="quick-entry-content">
        <JournalEntryForm
          v-if="showQuickEntry"
          mode="mobile-inline"
          :entry="null"
          :bow-setups="bowSetups"
          :entry-types="entryTypes"
          :context="context"
          @save="handleQuickEntrySave"
          @cancel="hideQuickEntry"
          @auto-save="handleAutoSave"
        />
      </div>
    </div>

    <!-- Mobile-Optimized Filter Section -->
    <div class="filter-section" :class="{ 'has-filters': hasActiveFilters }">
      <div class="filter-header">
        <div class="filter-info">
          <span class="entry-count">{{ filteredEntries.length }} {{ filteredEntries.length === 1 ? 'entry' : 'entries' }}</span>
          <span v-if="hasActiveFilters" class="active-filters-indicator">
            {{ activeFiltersCount }} filter{{ activeFiltersCount === 1 ? '' : 's' }} active
          </span>
        </div>
        
        <div class="filter-actions">
          <md-icon-button 
            @click="toggleMobileFilter"
            :class="{ 'active': showMobileFilter }"
            aria-label="Toggle filters"
          >
            <md-icon>tune</md-icon>
          </md-icon-button>
        </div>
      </div>

      <!-- Quick Filter Pills -->
      <div v-if="quickFilters.length" class="quick-filters">
        <div class="quick-filter-pills">
          <md-chip
            v-for="filter in quickFilters"
            :key="filter.key"
            :selected="filter.active"
            :removable="filter.active"
            @click="toggleQuickFilter(filter.key)"
            @remove="toggleQuickFilter(filter.key)"
            class="quick-filter-chip"
          >
            <md-icon slot="icon">{{ filter.icon }}</md-icon>
            {{ filter.label }}
          </md-chip>
        </div>
      </div>
    </div>

    <!-- Mobile Filter Drawer -->
    <JournalFilterMobile
      :show="showMobileFilter"
      :filters="filters"
      :entry-types="entryTypes"
      :context="context"
      @update:filters="updateFilters"
      @close="hideMobileFilter"
    />

    <!-- Journal Entries List (Mobile-Optimized) -->
    <div class="entries-container">
      <!-- Loading State -->
      <div v-if="loading && entries.length === 0" class="loading-state">
        <div class="loading-content">
          <md-circular-progress indeterminate></md-circular-progress>
          <p class="loading-text">Loading journal entries...</p>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && filteredEntries.length === 0" class="empty-state">
        <div class="empty-content">
          <md-icon class="empty-icon">{{ entries.length === 0 ? 'book' : 'filter_list_off' }}</md-icon>
          <h4 class="empty-title">
            {{ entries.length === 0 ? 'No journal entries yet' : 'No entries match your filters' }}
          </h4>
          <p class="empty-subtitle">
            {{ entries.length === 0 
              ? 'Start tracking your archery journey by adding your first entry.' 
              : 'Try adjusting your filters or clear them to see more entries.'
            }}
          </p>
          <md-button 
            v-if="entries.length === 0"
            variant="filled"
            @click="toggleQuickEntry"
            class="empty-action"
          >
            <md-icon slot="icon">add</md-icon>
            Add First Entry
          </md-button>
          <md-button 
            v-else
            variant="outlined"
            @click="clearFilters"
            class="empty-action"
          >
            <md-icon slot="icon">clear</md-icon>
            Clear Filters
          </md-button>
        </div>
      </div>

      <!-- Journal Entries -->
      <div v-else class="entries-list">
        <JournalEntryCard
          v-for="entry in displayedEntries"
          :key="entry.id"
          :entry="entry"
          :view-mode="isMobile ? 'mobile' : 'list'"
          :context="context"
          @view="viewEntry"
          @edit="editEntry"
          @delete="deleteEntry"
          @toggle-favorite="toggleFavorite"
          @view-change="viewLinkedChange"
          @show-all-changes="showAllLinkedChanges"
          class="entry-item"
        />

        <!-- Load More Button -->
        <div v-if="hasMoreEntries" class="load-more-container">
          <md-button
            variant="outlined"
            :disabled="loadingMore"
            @click="loadMoreEntries"
            class="load-more-button"
          >
            <md-icon slot="icon" v-if="!loadingMore">expand_more</md-icon>
            <md-circular-progress 
              v-if="loadingMore" 
              indeterminate 
              size="20"
            ></md-circular-progress>
            {{ loadingMore ? 'Loading...' : 'Load More Entries' }}
          </md-button>
        </div>
      </div>
    </div>

    <!-- Pull-to-Refresh Indicator (Mobile) -->
    <div v-if="pullToRefresh" class="pull-refresh-indicator" :class="{ 'active': pullRefreshActive }">
      <md-circular-progress indeterminate size="24"></md-circular-progress>
      <span class="refresh-text">Pull to refresh</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useJournalMobile } from '~/composables/useJournalMobile'
import JournalEntryForm from '~/components/JournalEntryForm.vue'
import JournalEntryCard from '~/components/JournalEntryCard.vue'
import JournalFilterMobile from '~/components/journal/JournalFilterMobile.vue'

const props = defineProps({
  // Context Configuration
  context: {
    type: String,
    default: 'general',
    validator: (value) => ['general', 'setup', 'arrow'].includes(value)
  },
  title: {
    type: String,
    default: 'Journal'
  },
  subtitle: {
    type: String,
    default: null
  },
  
  // Data Props
  entries: {
    type: Array,
    default: () => []
  },
  bowSetups: {
    type: Array,
    default: () => []
  },
  entryTypes: {
    type: Array,
    default: () => []
  },
  stats: {
    type: Object,
    default: () => ({})
  },
  
  // Behavior Props
  loading: {
    type: Boolean,
    default: false
  },
  hasMoreEntries: {
    type: Boolean,
    default: false
  },
  pullToRefresh: {
    type: Boolean,
    default: true
  },
  
  // Filter Props
  initialFilters: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits([
  'entry:view',
  'entry:edit',
  'entry:delete',
  'entry:create',
  'entry:favorite',
  'filters:update',
  'load-more',
  'refresh',
  'linked-change:view',
  'linked-changes:show-all'
])

// Mobile detection
const isMobile = ref(false)

// Use mobile journal composable
const {
  showQuickEntry,
  showMobileFilter,
  filters,
  filteredEntries,
  displayedEntries,
  quickFilters,
  hasActiveFilters,
  activeFiltersCount,
  loadingMore,
  pullRefreshActive,
  toggleQuickEntry,
  hideQuickEntry,
  toggleMobileFilter,
  hideMobileFilter,
  toggleQuickFilter,
  updateFilters,
  clearFilters,
  loadMoreEntries,
  setupPullToRefresh
} = useJournalMobile(props, emit)

// Context-specific styling
const contextIcon = computed(() => {
  switch (props.context) {
    case 'setup': return 'sports'
    case 'arrow': return 'arrow_forward'
    default: return 'book'
  }
})

const contextColorClasses = computed(() => {
  switch (props.context) {
    case 'setup': return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
    case 'arrow': return 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
    default: return 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400'
  }
})

const headerClasses = computed(() => [
  'mobile-optimized',
  `context-${props.context}`,
  { 'has-stats': props.stats && Object.keys(props.stats).length }
])

// Event handlers
const handleQuickEntrySave = (entry) => {
  hideQuickEntry()
  emit('entry:create', entry)
}

const handleAutoSave = (draft) => {
  // Auto-save draft functionality
  console.log('Auto-saving draft:', draft)
}

const viewEntry = (entry) => {
  emit('entry:view', entry)
}

const editEntry = (entry) => {
  emit('entry:edit', entry)
}

const deleteEntry = (entry) => {
  emit('entry:delete', entry)
}

const toggleFavorite = (entry) => {
  emit('entry:favorite', entry)
}

const viewLinkedChange = (change) => {
  emit('linked-change:view', change)
}

const showAllLinkedChanges = (entry) => {
  emit('linked-changes:show-all', entry)
}

// Mobile responsiveness detection
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  
  // Setup mobile features
  if (props.pullToRefresh) {
    setupPullToRefresh()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// Watch for entries changes
watch(() => props.entries, (newEntries) => {
  // Update filtered entries when data changes
  console.log('Entries updated:', newEntries.length)
}, { deep: true })
</script>

<style scoped>
/* Base Journal View Styles - Mobile First */

.base-journal-view {
  width: 100%;
  min-height: 100vh;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
}

/* Journal Header - Mobile Optimized */
.journal-header {
  background: var(--md-sys-color-surface-container-lowest);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding: 1rem;
  position: sticky;
  top: 0;
  z-index: 10;
  transition: all 0.3s ease;
}

.header-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.header-info {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.header-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.header-text {
  flex: 1;
  min-width: 0;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 0 0 0.25rem 0;
  line-height: 1.4;
}

.header-subtitle {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  margin: 0;
  line-height: 1.4;
}

.header-actions {
  flex-shrink: 0;
}

/* Stats Container - Mobile Horizontal Scroll */
.stats-container {
  margin-top: 1rem;
}

.stats-pills {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 0.25rem 0;
}

.stats-pills::-webkit-scrollbar {
  display: none;
}

.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  min-width: 4rem;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.stat-value {
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 500;
  opacity: 0.8;
  margin-top: 0.25rem;
  text-align: center;
  line-height: 1.2;
}

/* Quick Entry Container - Smooth Expand/Collapse */
.quick-entry-container {
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  max-height: 0;
  background: var(--md-sys-color-surface-container);
}

.quick-entry-container.expanded {
  max-height: 80vh;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.quick-entry-content {
  padding: 1rem;
}

/* Filter Section - Mobile Optimized */
.filter-section {
  background: var(--md-sys-color-surface);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding: 1rem 1rem 0.5rem;
  position: sticky;
  top: var(--journal-header-height, 120px);
  z-index: 9;
  transition: all 0.3s ease;
}

.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.filter-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.entry-count {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.active-filters-indicator {
  font-size: 0.75rem;
  color: var(--md-sys-color-primary);
  font-weight: 500;
}

.filter-actions md-icon-button.active {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

/* Quick Filters */
.quick-filters {
  margin-bottom: 0.75rem;
}

.quick-filter-pills {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 0.25rem 0;
}

.quick-filter-pills::-webkit-scrollbar {
  display: none;
}

.quick-filter-chip {
  flex-shrink: 0;
  transition: all 0.2s ease;
}

/* Entries Container */
.entries-container {
  padding: 1rem;
  min-height: 60vh;
}

/* Loading State */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-text {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  margin: 0;
}

/* Empty State */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  text-align: center;
}

.empty-content {
  max-width: 20rem;
}

.empty-icon {
  font-size: 3rem;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 0 0 0.5rem 0;
}

.empty-subtitle {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.5;
  margin: 0 0 1.5rem 0;
}

.empty-action {
  margin-top: 0.5rem;
}

/* Entries List */
.entries-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.entry-item {
  transition: all 0.2s ease;
}

/* Load More Container */
.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
  padding: 1rem;
}

.load-more-button {
  min-width: 12rem;
}

/* Pull to Refresh */
.pull-refresh-indicator {
  position: fixed;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--md-sys-color-surface-container-high);
  padding: 0.75rem 1rem;
  border-radius: 2rem;
  color: var(--md-sys-color-on-surface);
  font-size: 0.875rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
}

.pull-refresh-indicator.active {
  top: 2rem;
}

.refresh-text {
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 480px) {
  .journal-header {
    padding: 0.75rem;
  }
  
  .header-title {
    font-size: 1.125rem;
  }
  
  .stat-pill {
    min-width: 3.5rem;
    padding: 0.5rem 0.75rem;
  }
  
  .entries-container {
    padding: 0.75rem;
  }
}

@media (min-width: 768px) {
  .journal-header {
    padding: 1.5rem 2rem;
  }
  
  .quick-entry-content {
    padding: 1.5rem 2rem;
  }
  
  .filter-section {
    padding: 1rem 2rem;
  }
  
  .entries-container {
    padding: 1.5rem 2rem;
  }
  
  .stats-pills {
    justify-content: flex-start;
    overflow-x: visible;
  }
  
  .quick-filter-pills {
    overflow-x: visible;
    flex-wrap: wrap;
  }
}

/* Context-specific stat pill colors */
.stat-pill.stat-total {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.stat-pill.stat-recent {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.stat-pill.stat-favorites {
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
}

.stat-pill.stat-changes {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

/* Touch feedback for mobile */
@media (hover: none) {
  .header-icon:active {
    transform: scale(0.98);
  }
  
  .stat-pill:active {
    transform: scale(0.98);
  }
  
  .quick-filter-chip:active {
    transform: scale(0.96);
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .journal-header {
    border-bottom-width: 2px;
  }
  
  .filter-section {
    border-bottom-width: 2px;
  }
  
  .quick-entry-container.expanded {
    border-bottom-width: 2px;
  }
}
</style>