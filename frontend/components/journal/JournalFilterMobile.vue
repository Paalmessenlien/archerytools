<template>
  <!-- Mobile Filter Drawer/Bottom Sheet -->
  <div class="journal-filter-mobile">
    <!-- Backdrop -->
    <div 
      v-if="show"
      class="filter-backdrop"
      :class="{ 'visible': show }"
      @click="$emit('close')"
    ></div>

    <!-- Filter Bottom Sheet -->
    <div 
      class="filter-sheet"
      :class="{ 'visible': show }"
    >
      <!-- Sheet Header -->
      <div class="sheet-header">
        <div class="header-handle"></div>
        <div class="header-content">
          <div class="header-info">
            <md-icon class="header-icon">tune</md-icon>
            <h3 class="header-title">Filter Journal Entries</h3>
          </div>
          
          <div class="header-actions">
            <md-button
              variant="text"
              @click="clearAllFilters"
              :disabled="!hasActiveFilters"
              class="clear-button"
            >
              Clear All
            </md-button>
            <md-icon-button @click="$emit('close')" aria-label="Close filters">
              <md-icon>close</md-icon>
            </md-icon-button>
          </div>
        </div>
      </div>

      <!-- Filter Content -->
      <div class="sheet-content">
        <!-- Entry Type Filter Section -->
        <div class="filter-section">
          <div class="section-header">
            <md-icon class="section-icon">category</md-icon>
            <h4 class="section-title">Entry Types</h4>
            <md-chip 
              v-if="activeTypeFilters.length"
              :label="`${activeTypeFilters.length} selected`"
              class="active-count-chip"
            ></md-chip>
          </div>
          
          <div class="filter-options">
            <md-chip
              v-for="type in availableEntryTypes"
              :key="type.value"
              :selected="filters.entryTypes?.includes(type.value)"
              @click="toggleEntryType(type.value)"
              class="type-filter-chip"
              :class="`type-${type.value}`"
            >
              <md-icon slot="icon">{{ type.icon }}</md-icon>
              {{ type.label }}
              <md-chip-action 
                v-if="filters.entryTypes?.includes(type.value)"
                @click.stop="toggleEntryType(type.value)"
              >
                <md-icon>close</md-icon>
              </md-chip-action>
            </md-chip>
          </div>
        </div>

        <!-- Date Range Filter Section -->
        <div class="filter-section">
          <div class="section-header">
            <md-icon class="section-icon">date_range</md-icon>
            <h4 class="section-title">Date Range</h4>
            <md-chip 
              v-if="filters.dateRange && filters.dateRange !== 'all'"
              :label="getDateRangeLabel(filters.dateRange)"
              class="active-count-chip"
            ></md-chip>
          </div>
          
          <div class="filter-options">
            <md-chip
              v-for="range in dateRanges"
              :key="range.value"
              :selected="filters.dateRange === range.value"
              @click="updateDateRange(range.value)"
              class="date-filter-chip"
            >
              <md-icon slot="icon">{{ range.icon }}</md-icon>
              {{ range.label }}
            </md-chip>
          </div>

          <!-- Custom Date Range (Expandable) -->
          <div v-if="filters.dateRange === 'custom'" class="custom-date-section">
            <div class="custom-date-inputs">
              <md-outlined-text-field
                :value="customDates.start"
                type="date"
                label="Start Date"
                class="date-input"
                @input="(e) => { customDates.start = e.target.value; updateCustomDateRange(); }"
              >
                <md-icon slot="leading-icon">event</md-icon>
              </md-outlined-text-field>
              
              <md-outlined-text-field
                :value="customDates.end"
                type="date"
                label="End Date"
                class="date-input"
                @input="(e) => { customDates.end = e.target.value; updateCustomDateRange(); }"
              >
                <md-icon slot="leading-icon">event</md-icon>
              </md-outlined-text-field>
            </div>
          </div>
        </div>

        <!-- Favorites Filter Section -->
        <div class="filter-section">
          <div class="section-header">
            <md-icon class="section-icon">star</md-icon>
            <h4 class="section-title">Favorites & Status</h4>
          </div>
          
          <div class="filter-options">
            <md-switch
              :selected="filters.favoritesOnly"
              @change="toggleFavoritesFilter"
              class="favorites-switch"
            >
              <div class="switch-content">
                <md-icon class="switch-icon">star</md-icon>
                <span class="switch-label">Show Favorites Only</span>
              </div>
            </md-switch>
            
            <md-switch
              :selected="filters.hasImages"
              @change="toggleImagesFilter"
              class="images-switch"
            >
              <div class="switch-content">
                <md-icon class="switch-icon">image</md-icon>
                <span class="switch-label">Has Images</span>
              </div>
            </md-switch>
            
            <md-switch
              :selected="filters.hasLinkedChanges"
              @change="toggleLinkedChangesFilter"
              class="changes-switch"
            >
              <div class="switch-content">
                <md-icon class="switch-icon">link</md-icon>
                <span class="switch-label">Has Linked Changes</span>
              </div>
            </md-switch>
          </div>
        </div>

        <!-- Tags Filter Section -->
        <div v-if="availableTags.length" class="filter-section">
          <div class="section-header">
            <md-icon class="section-icon">label</md-icon>
            <h4 class="section-title">Tags</h4>
            <md-chip 
              v-if="filters.tags?.length"
              :label="`${filters.tags.length} selected`"
              class="active-count-chip"
            ></md-chip>
          </div>
          
          <div class="filter-options">
            <md-chip
              v-for="tag in displayedTags"
              :key="tag"
              :selected="filters.tags?.includes(tag)"
              @click="toggleTag(tag)"
              class="tag-filter-chip"
            >
              <md-icon slot="icon">label</md-icon>
              {{ tag }}
              <md-chip-action 
                v-if="filters.tags?.includes(tag)"
                @click.stop="toggleTag(tag)"
              >
                <md-icon>close</md-icon>
              </md-chip-action>
            </md-chip>
            
            <!-- Show More Tags Button -->
            <md-button
              v-if="availableTags.length > maxDisplayedTags && !showAllTags"
              variant="text"
              @click="showAllTags = true"
              class="show-more-tags"
            >
              <md-icon slot="icon">expand_more</md-icon>
              +{{ availableTags.length - maxDisplayedTags }} more
            </md-button>
          </div>
        </div>

        <!-- Context-Specific Filters -->
        <div v-if="contextFilters.length" class="filter-section">
          <div class="section-header">
            <md-icon class="section-icon">{{ contextIcon }}</md-icon>
            <h4 class="section-title">{{ contextTitle }}</h4>
          </div>
          
          <div class="filter-options">
            <component
              v-for="filter in contextFilters"
              :key="filter.key"
              :is="filter.component"
              v-bind="filter.props"
              @update="(value) => updateContextFilter(filter.key, value)"
            />
          </div>
        </div>

        <!-- Search Filter Section -->
        <div class="filter-section">
          <div class="section-header">
            <md-icon class="section-icon">search</md-icon>
            <h4 class="section-title">Search Content</h4>
          </div>
          
          <md-outlined-text-field
            :value="searchQuery"
            label="Search entries..."
            placeholder="Type to search titles, content, and tags"
            @input="(e) => { searchQuery = e.target.value; debouncedSearch(); }"
            class="search-input"
          >
            <md-icon slot="leading-icon">search</md-icon>
            <md-icon-button 
              v-if="searchQuery"
              slot="trailing-icon"
              @click="clearSearch"
              aria-label="Clear search"
            >
              <md-icon>close</md-icon>
            </md-icon-button>
          </md-outlined-text-field>
        </div>
      </div>

      <!-- Sheet Footer (Apply/Reset Actions) -->
      <div class="sheet-footer">
        <div class="footer-actions">
          <md-button
            variant="outlined"
            @click="resetFilters"
            :disabled="!hasActiveFilters"
            class="reset-button"
          >
            <md-icon slot="icon">refresh</md-icon>
            Reset
          </md-button>
          
          <md-button
            variant="filled"
            @click="applyFilters"
            class="apply-button"
          >
            <md-icon slot="icon">check</md-icon>
            Apply Filters
          </md-button>
        </div>
        
        <div class="active-filters-summary" v-if="hasActiveFilters">
          <span class="summary-text">{{ activeFiltersSummary }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { debounce } from 'lodash-es'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  filters: {
    type: Object,
    default: () => ({
      entryTypes: [],
      dateRange: 'all',
      customDateStart: null,
      customDateEnd: null,
      favoritesOnly: false,
      hasImages: false,
      hasLinkedChanges: false,
      tags: [],
      search: ''
    })
  },
  entryTypes: {
    type: Array,
    default: () => []
  },
  availableTags: {
    type: Array,
    default: () => []
  },
  context: {
    type: String,
    default: 'general',
    validator: (value) => ['general', 'setup', 'arrow'].includes(value)
  }
})

const emit = defineEmits(['update:filters', 'close', 'apply', 'reset'])

// Local filter state
const localFilters = ref({ ...props.filters })
const searchQuery = ref(props.filters.search || '')
const customDates = ref({
  start: props.filters.customDateStart || '',
  end: props.filters.customDateEnd || ''
})
const showAllTags = ref(false)
const maxDisplayedTags = 8

// Available entry types with icons
const availableEntryTypes = computed(() => {
  const defaultTypes = [
    { value: 'general', label: 'General', icon: 'notes' },
    { value: 'shooting_notes', label: 'Shooting', icon: 'center_focus_strong' },
    { value: 'tuning_session', label: 'Tuning', icon: 'tune' },
    { value: 'equipment_change', label: 'Equipment', icon: 'build' },
    { value: 'setup_change', label: 'Setup', icon: 'settings' },
    { value: 'arrow_change', label: 'Arrow', icon: 'arrow_forward' },
    { value: 'maintenance', label: 'Maintenance', icon: 'handyman' },
    { value: 'upgrade', label: 'Upgrade', icon: 'upgrade' }
  ]
  
  // Filter based on provided entry types or show all
  if (props.entryTypes.length) {
    return defaultTypes.filter(type => 
      props.entryTypes.some(et => et.value === type.value)
    )
  }
  
  return defaultTypes
})

// Date range options
const dateRanges = [
  { value: 'all', label: 'All Time', icon: 'all_inclusive' },
  { value: 'today', label: 'Today', icon: 'today' },
  { value: 'week', label: 'This Week', icon: 'date_range' },
  { value: 'month', label: 'This Month', icon: 'calendar_month' },
  { value: 'quarter', label: 'Last 3 Months', icon: 'calendar_view_month' },
  { value: 'year', label: 'This Year', icon: 'calendar_view_year' },
  { value: 'custom', label: 'Custom Range', icon: 'date_range' }
]

// Context-specific configuration
const contextIcon = computed(() => {
  switch (props.context) {
    case 'setup': return 'sports'
    case 'arrow': return 'arrow_forward'
    default: return 'tune'
  }
})

const contextTitle = computed(() => {
  switch (props.context) {
    case 'setup': return 'Setup Filters'
    case 'arrow': return 'Arrow Filters'
    default: return 'Advanced Filters'
  }
})

const contextFilters = computed(() => {
  // Return context-specific filter components
  const filters = []
  
  if (props.context === 'setup') {
    // Setup-specific filters could go here
  } else if (props.context === 'arrow') {
    // Arrow-specific filters could go here
  }
  
  return filters
})

// Computed properties
const activeTypeFilters = computed(() => localFilters.value.entryTypes || [])

const displayedTags = computed(() => {
  if (showAllTags.value || props.availableTags.length <= maxDisplayedTags) {
    return props.availableTags
  }
  return props.availableTags.slice(0, maxDisplayedTags)
})

const hasActiveFilters = computed(() => {
  const f = localFilters.value
  return (
    (f.entryTypes && f.entryTypes.length > 0) ||
    (f.dateRange && f.dateRange !== 'all') ||
    f.favoritesOnly ||
    f.hasImages ||
    f.hasLinkedChanges ||
    (f.tags && f.tags.length > 0) ||
    (f.search && f.search.trim().length > 0)
  )
})

const activeFiltersSummary = computed(() => {
  const parts = []
  const f = localFilters.value
  
  if (f.entryTypes && f.entryTypes.length) {
    parts.push(`${f.entryTypes.length} type${f.entryTypes.length === 1 ? '' : 's'}`)
  }
  
  if (f.dateRange && f.dateRange !== 'all') {
    parts.push(getDateRangeLabel(f.dateRange))
  }
  
  if (f.favoritesOnly) parts.push('favorites only')
  if (f.hasImages) parts.push('with images')
  if (f.hasLinkedChanges) parts.push('with changes')
  
  if (f.tags && f.tags.length) {
    parts.push(`${f.tags.length} tag${f.tags.length === 1 ? '' : 's'}`)
  }
  
  if (f.search && f.search.trim()) {
    parts.push('search active')
  }
  
  return parts.length ? `${parts.join(', ')}` : 'No active filters'
})

// Methods
const toggleEntryType = (type) => {
  const types = localFilters.value.entryTypes || []
  const index = types.indexOf(type)
  
  if (index > -1) {
    types.splice(index, 1)
  } else {
    types.push(type)
  }
  
  localFilters.value.entryTypes = [...types]
}

const updateDateRange = (range) => {
  localFilters.value.dateRange = range
  
  if (range !== 'custom') {
    localFilters.value.customDateStart = null
    localFilters.value.customDateEnd = null
    customDates.value = { start: '', end: '' }
  }
}

const getDateRangeLabel = (range) => {
  const rangeObj = dateRanges.find(r => r.value === range)
  return rangeObj ? rangeObj.label : 'Custom'
}

const updateCustomDateRange = () => {
  localFilters.value.customDateStart = customDates.value.start || null
  localFilters.value.customDateEnd = customDates.value.end || null
}

const toggleFavoritesFilter = (value) => {
  localFilters.value.favoritesOnly = value
}

const toggleImagesFilter = (value) => {
  localFilters.value.hasImages = value
}

const toggleLinkedChangesFilter = (value) => {
  localFilters.value.hasLinkedChanges = value
}

const toggleTag = (tag) => {
  const tags = localFilters.value.tags || []
  const index = tags.indexOf(tag)
  
  if (index > -1) {
    tags.splice(index, 1)
  } else {
    tags.push(tag)
  }
  
  localFilters.value.tags = [...tags]
}

const updateContextFilter = (key, value) => {
  localFilters.value[key] = value
}

const debouncedSearch = debounce((event) => {
  localFilters.value.search = event.target.value
}, 300)

const clearSearch = () => {
  searchQuery.value = ''
  localFilters.value.search = ''
}

const clearAllFilters = () => {
  localFilters.value = {
    entryTypes: [],
    dateRange: 'all',
    customDateStart: null,
    customDateEnd: null,
    favoritesOnly: false,
    hasImages: false,
    hasLinkedChanges: false,
    tags: [],
    search: ''
  }
  searchQuery.value = ''
  customDates.value = { start: '', end: '' }
  showAllTags.value = false
}

const resetFilters = () => {
  clearAllFilters()
  applyFilters()
}

const applyFilters = () => {
  emit('update:filters', { ...localFilters.value })
  emit('apply', { ...localFilters.value })
  emit('close')
}

// Watch for prop changes
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
  searchQuery.value = newFilters.search || ''
  customDates.value = {
    start: newFilters.customDateStart || '',
    end: newFilters.customDateEnd || ''
  }
}, { deep: true })

// Watch for show changes to handle backdrop clicks
watch(() => props.show, async (show) => {
  if (show) {
    await nextTick()
    // Focus trap or other accessibility features could be added here
  }
})
</script>

<style scoped>
/* Journal Filter Mobile - Bottom Sheet Pattern */

.journal-filter-mobile {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  pointer-events: none;
}

/* Backdrop */
.filter-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

.filter-backdrop.visible {
  opacity: 1;
  pointer-events: all;
}

/* Bottom Sheet */
.filter-sheet {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 90vh;
  background: var(--md-sys-color-surface-container);
  border-radius: 1.5rem 1.5rem 0 0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(100%);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-sheet.visible {
  transform: translateY(0);
  pointer-events: all;
}

/* Sheet Header */
.sheet-header {
  flex-shrink: 0;
  background: var(--md-sys-color-surface-container-high);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.header-handle {
  width: 2rem;
  height: 0.25rem;
  background: var(--md-sys-color-on-surface-variant);
  border-radius: 0.125rem;
  margin: 0.75rem auto 0;
  opacity: 0.6;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem 1.25rem;
  gap: 1rem;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.header-icon {
  color: var(--md-sys-color-primary);
  font-size: 1.5rem;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.clear-button {
  color: var(--md-sys-color-error);
}

/* Sheet Content */
.sheet-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.5rem 1rem;
  scrollbar-width: thin;
  scrollbar-color: var(--md-sys-color-outline-variant) transparent;
}

.sheet-content::-webkit-scrollbar {
  width: 4px;
}

.sheet-content::-webkit-scrollbar-track {
  background: transparent;
}

.sheet-content::-webkit-scrollbar-thumb {
  background: var(--md-sys-color-outline-variant);
  border-radius: 2px;
}

/* Filter Sections */
.filter-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.filter-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.section-icon {
  color: var(--md-sys-color-primary);
  font-size: 1.25rem;
  flex-shrink: 0;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 0;
  flex: 1;
}

.active-count-chip {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  font-size: 0.75rem;
  height: 1.5rem;
  flex-shrink: 0;
}

/* Filter Options */
.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

/* Entry Type Filter Chips */
.type-filter-chip {
  transition: all 0.2s ease;
  min-height: 2.5rem;
  touch-action: manipulation;
}

.type-filter-chip:active {
  transform: scale(0.98);
}

/* Date Filter Chips */
.date-filter-chip {
  transition: all 0.2s ease;
  min-height: 2.5rem;
  touch-action: manipulation;
}

.date-filter-chip:active {
  transform: scale(0.98);
}

/* Custom Date Section */
.custom-date-section {
  width: 100%;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.custom-date-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.date-input {
  width: 100%;
}

/* Switch Controls */
.filter-options md-switch {
  width: 100%;
  margin: 0.25rem 0;
}

.switch-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.switch-icon {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1.25rem;
  flex-shrink: 0;
}

.switch-label {
  font-size: 0.9375rem;
  color: var(--md-sys-color-on-surface);
  font-weight: 500;
  flex: 1;
}

/* Tag Filter Chips */
.tag-filter-chip {
  transition: all 0.2s ease;
  min-height: 2.5rem;
  touch-action: manipulation;
}

.tag-filter-chip:active {
  transform: scale(0.98);
}

.show-more-tags {
  color: var(--md-sys-color-primary);
  font-size: 0.875rem;
  min-height: 2.5rem;
}

/* Search Input */
.search-input {
  width: 100%;
  margin-top: 0.5rem;
}

/* Sheet Footer */
.sheet-footer {
  flex-shrink: 0;
  background: var(--md-sys-color-surface-container-high);
  border-top: 1px solid var(--md-sys-color-outline-variant);
  padding: 1rem 1.5rem;
  padding-bottom: calc(1rem + env(safe-area-inset-bottom));
}

.footer-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.reset-button,
.apply-button {
  min-height: 2.75rem;
  font-weight: 600;
  touch-action: manipulation;
}

.reset-button:active,
.apply-button:active {
  transform: scale(0.98);
}

.active-filters-summary {
  text-align: center;
}

.summary-text {
  font-size: 0.8125rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 480px) {
  .header-content {
    padding: 0.75rem 1rem 1rem;
  }
  
  .sheet-content {
    padding: 0 1rem 0.75rem;
  }
  
  .sheet-footer {
    padding: 0.75rem 1rem;
    padding-bottom: calc(0.75rem + env(safe-area-inset-bottom));
  }
  
  .custom-date-inputs {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    gap: 0.5rem;
  }
  
  .header-title {
    font-size: 1.125rem;
  }
}

@media (min-width: 768px) {
  .filter-sheet {
    max-height: 80vh;
    left: 50%;
    right: auto;
    width: 32rem;
    transform: translateX(-50%) translateY(100%);
    border-radius: 1.5rem;
    bottom: 2rem;
  }
  
  .filter-sheet.visible {
    transform: translateX(-50%) translateY(0);
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .filter-sheet {
    border: 2px solid var(--md-sys-color-outline);
  }
  
  .sheet-header {
    border-bottom-width: 2px;
  }
  
  .sheet-footer {
    border-top-width: 2px;
  }
  
  .filter-section {
    border-bottom-width: 2px;
  }
}

/* Focus management */
.filter-sheet:focus-within {
  outline: none;
}

/* Touch feedback */
@media (hover: none) {
  .type-filter-chip:active,
  .date-filter-chip:active,
  .tag-filter-chip:active {
    transform: scale(0.96);
    transition: transform 0.1s ease;
  }
}
</style>