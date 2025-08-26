<template>
  <div class="journal-page">
    <!-- Global Notification Container -->
    <ClientOnly>
      <NotificationContainer />
    </ClientOnly>

    <div class="main-container">
      <!-- Header -->
      <PageHeader
        title="Archery Journal"
        subtitle="Document your archery journey with detailed notes and observations"
        size="large"
      >
        <template #actions>
          <CustomButton @click="showCreateDialog = true" variant="primary" icon="fas fa-plus">
            New Entry
          </CustomButton>
        </template>
      </PageHeader>

    <!-- Enhanced Search and Filter Interface -->
    <div :class="['search-filter-section', { 'is-sticky': isFilterSticky }]" ref="filterSection">
      <!-- Main Search Bar -->
      <div class="search-bar-container">
        <div class="search-input-wrapper">
          <!-- Enhanced Search Input with clearer visual hierarchy -->
          <div class="search-input-group">
            <md-outlined-text-field
              :value="filterState.searchQuery || ''"
              placeholder="Search entries by title, content, tags, or setup..."
              class="search-input"
              @input="(e) => handleSearchChange(e.target.value)"
            >
              <i slot="leading-icon" class="fas fa-search search-icon"></i>
            </md-outlined-text-field>
            
            <!-- Enhanced Clear Search Button -->
            <button 
              v-if="filterState.searchQuery"
              @click="clearSearch"
              class="clear-search-btn"
              title="Clear search"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <!-- Enhanced Search Results Count with better visual design -->
          <div v-if="filterState.searchQuery || hasActiveFilters" class="search-results-indicator"
               :class="{ 'is-loading': filteringState.isFiltering, 'has-error': filteringState.hasError }">
            <div class="results-content">
              <div class="results-icon">
                <i v-if="!filteringState.isFiltering && !filteringState.hasError" class="fas fa-search"></i>
                <md-circular-progress v-if="filteringState.isFiltering" indeterminate class="filter-loading-spinner"></md-circular-progress>
                <i v-if="filteringState.hasError" class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="results-text">
                <span v-if="!filteringState.hasError" class="results-count">
                  {{ filteredEntriesCount }} {{ filteredEntriesCount === 1 || filteredEntriesCount === '...' ? 'entry' : 'entries' }}
                </span>
                <span v-if="filteringState.hasError" class="error-text">
                  {{ filteringState.errorMessage }}
                </span>
                <span v-if="!filteringState.hasError" class="results-label">found</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Enhanced Quick Filter Pills with better design -->
        <div class="quick-filters-section" v-if="!showFilters">
          <div class="quick-filters-label">
            <i class="fas fa-bolt mr-1"></i>
            Quick Filters:
          </div>
          <div class="quick-filters">
            <button 
              v-for="quickFilter in quickFilters" 
              :key="quickFilter.id"
              @click="applyQuickFilter(quickFilter)"
              class="quick-filter-pill"
              :class="{ active: isQuickFilterActive(quickFilter) }"
            >
              <div class="pill-icon-wrapper">
                <i :class="quickFilter.icon" class="pill-icon"></i>
              </div>
              <span class="pill-label">{{ quickFilter.label }}</span>
            </button>
          </div>
        </div>

        <!-- Enhanced Filter Toggle & Controls -->
        <div class="filter-controls-header">
          <button @click="showFilters = !showFilters" class="filter-toggle-btn">
            <div class="toggle-content">
              <div class="toggle-icon">
                <i :class="showFilters ? 'fas fa-filter-circle-xmark' : 'fas fa-sliders-h'"></i>
              </div>
              <div class="toggle-text">
                <span class="toggle-label">{{ showFilters ? 'Hide Advanced Filters' : 'Show Advanced Filters' }}</span>
                <span v-if="hasActiveFilters" class="toggle-subtitle">
                  {{ activeFiltersCount }} active filter{{ activeFiltersCount > 1 ? 's' : '' }}
                </span>
              </div>
            </div>
            <div class="toggle-chevron">
              <i :class="showFilters ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </button>

          <div class="filter-control-actions">
            <button 
              v-if="hasActiveFilters" 
              @click="clearAllFilters" 
              class="clear-filters-btn"
            >
              <i class="fas fa-broom mr-2"></i>
              <span>Clear All Filters</span>
            </button>
            <button 
              v-if="hasActiveFilters" 
              @click="showSavePresetDialog = true"
              class="save-preset-btn-header"
            >
              <i class="fas fa-bookmark mr-2"></i>
              <span>Save as Preset</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Enhanced Active Filter Chips -->
      <div v-if="hasActiveFilters" class="active-filters-chips">
        <div class="chips-header">
          <div class="chips-title">
            <i class="fas fa-filter mr-1"></i>
            Active Filters
          </div>
          <div class="chips-count">{{ activeFiltersCount }}</div>
        </div>
        <div class="chips-container">
          <div 
            v-for="chip in activeFilterChips" 
            :key="chip.key"
            class="filter-chip"
          >
            <div class="chip-content">
              <span class="chip-label">{{ chip.label }}</span>
              <span class="chip-separator">:</span>
              <span class="chip-value">{{ chip.value }}</span>
            </div>
            <button @click="removeFilter(chip.key)" class="remove-chip-btn" :title="`Remove ${chip.label} filter`">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Collapsible Filter Panel -->
      <div v-if="showFilters" class="filters-panel">
        <div class="filter-groups">
          <!-- Basic Filters Group -->
          <div class="filter-group">
            <h3 class="filter-group-title">
              <i class="fas fa-filter mr-2"></i>
              Basic Filters
            </h3>
            <div class="filter-group-controls">
              <div class="filter-row">
                <md-outlined-select 
                  :value="filterState.selectedSetup" 
                  @change="(e) => handleFilterChange('bow_setup_id', e.target.value)" 
                  class="filter-control"
                >
                  <span slot="label">Bow Setup</span>
                  <md-select-option value="">All Setups</md-select-option>
                  <md-select-option v-for="setup in bowSetups" :key="setup.id" :value="setup.id.toString()">
                    {{ setup.name }} ({{ setup.bow_type }})
                  </md-select-option>
                </md-outlined-select>

                <md-outlined-select 
                  :value="filterState.selectedType" 
                  @change="(e) => handleFilterChange('entry_type', e.target.value)" 
                  class="filter-control"
                >
                  <span slot="label">Entry Type</span>
                  <md-select-option value="">All Types</md-select-option>
                  <md-select-option v-for="type in entryTypes" :key="type.value" :value="type.value">
                    {{ type.label }}
                  </md-select-option>
                </md-outlined-select>
              </div>
            </div>
          </div>

          <!-- Sorting Group -->
          <div class="filter-group">
            <h3 class="filter-group-title">
              <i class="fas fa-sort mr-2"></i>
              Sort Options
            </h3>
            <div class="filter-group-controls">
              <div class="filter-row">
                <md-outlined-select 
                  :value="filterState.sortBy || ''" 
                  @change="(e) => handleSortChange(e.target.value)" 
                  class="filter-control"
                >
                  <span slot="label">Sort By</span>
                  <md-select-option value="created_at">Date Created</md-select-option>
                  <md-select-option value="updated_at">Date Modified</md-select-option>
                  <md-select-option value="title">Title</md-select-option>
                  <md-select-option value="entry_type">Entry Type</md-select-option>
                </md-outlined-select>

                <md-outlined-select 
                  :value="filterState.sortDirection || 'desc'" 
                  @change="(e) => handleSortDirectionChange(e.target.value)" 
                  class="filter-control"
                >
                  <span slot="label">Direction</span>
                  <md-select-option value="asc">
                    <i class="fas fa-sort-up mr-2"></i>Ascending
                  </md-select-option>
                  <md-select-option value="desc">
                    <i class="fas fa-sort-down mr-2"></i>Descending
                  </md-select-option>
                </md-outlined-select>
              </div>
            </div>
          </div>

          <!-- Advanced Filters Group -->
          <div class="filter-group">
            <h3 class="filter-group-title">
              <i class="fas fa-cog mr-2"></i>
              Advanced Filters
            </h3>
            <div class="filter-group-controls">
              <!-- Tags Filter Row -->
              <div class="filter-row">
                <md-outlined-text-field
                  :value="filterState.selectedTags"
                  placeholder="Filter by tags (comma-separated)"
                  class="filter-control full-width"
                  @input="(e) => handleFilterChange('tags', e.target.value)"
                >
                  <span slot="label">Tags</span>
                  <i slot="leading-icon" class="fas fa-tag"></i>
                </md-outlined-text-field>
              </div>

              <!-- Equipment Filter Row -->
              <div class="filter-row">
                <md-outlined-select 
                  :value="filterState.equipmentType || ''" 
                  @change="(e) => handleFilterChange('equipment_type', e.target.value)" 
                  class="filter-control"
                >
                  <span slot="label">Equipment Type</span>
                  <md-select-option value="">All Equipment</md-select-option>
                  <md-select-option value="bow">Bow</md-select-option>
                  <md-select-option value="arrows">Arrows</md-select-option>
                  <md-select-option value="sight">Sight</md-select-option>
                  <md-select-option value="rest">Rest</md-select-option>
                  <md-select-option value="stabilizer">Stabilizer</md-select-option>
                  <md-select-option value="release">Release</md-select-option>
                  <md-select-option value="quiver">Quiver</md-select-option>
                  <md-select-option value="other">Other</md-select-option>
                </md-outlined-select>

                <md-outlined-text-field
                  :value="filterState.equipmentName"
                  placeholder="Equipment name or manufacturer"
                  class="filter-control"
                  @input="(e) => handleFilterChange('equipment_name', e.target.value)"
                >
                  <span slot="label">Equipment Name</span>
                  <i slot="leading-icon" class="fas fa-wrench"></i>
                </md-outlined-text-field>
              </div>

              <!-- Date Range Filter Row -->
              <div class="filter-row">
                <md-outlined-text-field
                  :value="filterState.dateFrom"
                  type="date"
                  class="filter-control"
                  @input="(e) => handleFilterChange('date_from', e.target.value)"
                >
                  <span slot="label">Date From</span>
                  <i slot="leading-icon" class="fas fa-calendar-alt"></i>
                </md-outlined-text-field>

                <md-outlined-text-field
                  :value="filterState.dateTo"
                  type="date"
                  class="filter-control"
                  @input="(e) => handleFilterChange('date_to', e.target.value)"
                >
                  <span slot="label">Date To</span>
                  <i slot="leading-icon" class="fas fa-calendar-alt"></i>
                </md-outlined-text-field>
              </div>

              <!-- Privacy and Attachment Filters -->
              <div class="filter-row">
                <md-outlined-select 
                  :value="filterState.privacyFilter || ''" 
                  @change="(e) => handleFilterChange('privacy_filter', e.target.value)" 
                  class="filter-control"
                >
                  <span slot="label">Privacy</span>
                  <md-select-option value="">All Entries</md-select-option>
                  <md-select-option value="public">Public Only</md-select-option>
                  <md-select-option value="private">Private Only</md-select-option>
                </md-outlined-select>

                <md-outlined-select 
                  :value="filterState.hasImages || ''" 
                  @change="(e) => handleFilterChange('has_images', e.target.value)" 
                  class="filter-control"
                >
                  <span slot="label">Images</span>
                  <md-select-option value="">All Entries</md-select-option>
                  <md-select-option value="true">With Images</md-select-option>
                  <md-select-option value="false">Without Images</md-select-option>
                </md-outlined-select>
              </div>
            </div>
          </div>

          <!-- Filter Presets Group -->
          <div class="filter-group" v-if="filterPresets.length > 0">
            <h3 class="filter-group-title">
              <i class="fas fa-bookmark mr-2"></i>
              Filter Presets
            </h3>
            <div class="filter-group-controls">
              <div class="filter-presets-row">
                <div class="preset-buttons">
                  <button 
                    v-for="preset in filterPresets" 
                    :key="preset.id"
                    @click="applyFilterPreset(preset)"
                    class="preset-btn"
                    :class="{ active: currentPresetId === preset.id }"
                  >
                    <i :class="preset.icon || 'fas fa-filter'" class="mr-1"></i>
                    {{ preset.name }}
                  </button>
                </div>
                <div class="preset-actions">
                  <button @click="showSavePresetDialog = true" class="save-preset-btn">
                    <i class="fas fa-plus mr-1"></i>
                    Save Current
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="tab-navigation">
      <div class="tab-buttons">
        <button 
          @click="activeTab = 'journal'"
          :class="['tab-btn', { active: activeTab === 'journal' }]"
        >
          <i class="fas fa-book-open mr-2"></i>
          Journal Entries
          <span v-if="entries.length > 0" class="tab-count">({{ entries.length }})</span>
        </button>
        <button 
          @click="activeTab = 'changelog'"
          :class="['tab-btn', { active: activeTab === 'changelog' }]"
        >
          <i class="fas fa-history mr-2"></i>
          Change Log
        </button>
      </div>
    </div>

    <!-- Journal Tab Content -->
    <div v-if="activeTab === 'journal'" class="entries-container">
      <div v-if="journalApi.isLoading.value" class="loading-state">
        <md-circular-progress indeterminate></md-circular-progress>
        <p>Loading journal entries...</p>
      </div>

      <div v-else-if="entries.length === 0" class="empty-state">
        <div class="empty-icon-container">
          <i class="fas fa-book empty-icon"></i>
        </div>
        <div class="empty-content">
          <h3 class="empty-title">No Journal Entries Found</h3>
          <p class="empty-description">
            {{ filterState.searchQuery || filterState.selectedSetup || filterState.selectedType || filterState.selectedTags 
              ? 'No entries match your current filters. Try adjusting your search criteria.' 
              : 'Start documenting your archery journey by creating your first entry.' }}
          </p>
          <CustomButton @click="showCreateDialog = true" variant="primary" icon="fas fa-plus" class="empty-action">
            {{ entries.length === 0 && !filterState.searchQuery ? 'Create First Entry' : 'New Entry' }}
          </CustomButton>
        </div>
      </div>

      <div v-else class="entries-section">
        <div class="entries-header">
          <div class="entries-header-content">
            <div class="entries-title-section">
              <h2 class="entries-title">
                <i class="fas fa-book-open mr-2"></i>
                Journal Entries
                <span class="entries-count">({{ entries.length }})</span>
              </h2>
              <p class="entries-subtitle">Your archery journey documented</p>
            </div>
            
            <!-- View Mode Toggle -->
            <div class="view-mode-controls">
              <div class="view-toggle-group">
                <button 
                  @click="viewMode = 'list'"
                  :class="['view-toggle-btn', { active: viewMode === 'list' }]"
                  aria-label="List view"
                >
                  <i class="fas fa-list"></i>
                </button>
                <button 
                  @click="viewMode = 'grid'"
                  :class="['view-toggle-btn', { active: viewMode === 'grid' }]"
                  aria-label="Grid view"
                >
                  <i class="fas fa-th"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div :class="['entries-list', `entries-${viewMode}`]">
          <JournalEntryCard
            v-for="entry in entries"
            :key="entry.id"
            :entry="entry"
            :view-mode="viewMode"
            @edit="editEntry"
            @delete="deleteEntry"
            @view="viewEntry"
          />
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.state.pages > 1" class="pagination">
        <CustomButton 
          @click="pagination.goToPrevPage()"
          :disabled="!pagination.meta.hasPrevPage"
          variant="outlined"
          icon="fas fa-chevron-left"
        >
          Previous
        </CustomButton>
        
        <div class="pagination-pages">
          <CustomButton
            v-for="page in pagination.meta.visiblePages"
            :key="page"
            @click="pagination.setPage(page)"
            :variant="page === pagination.state.page ? 'primary' : 'text'"
            size="small"
          >
            {{ page }}
          </CustomButton>
        </div>
        
        <span class="page-info">
          {{ pagination.pageInfo }}
        </span>
        
        <CustomButton 
          @click="pagination.goToNextPage()"
          :disabled="!pagination.meta.hasNextPage"
          variant="outlined"
          icon="fas fa-chevron-right"
        >
          Next
        </CustomButton>
      </div>
    </div>

    <!-- Change Log Tab Content -->
    <div v-if="activeTab === 'changelog'" class="changelog-container">
      <JournalChangeLog 
        :bow-setups="bowSetups"
        @journal-create-request="handleJournalFromChangeLog"
      />
    </div>

    <!-- Create/Edit Entry Form -->
    <ClientOnly>
      <JournalEntryForm
        v-if="showCreateDialog || showEditDialog"
        mode="modal"
        :show="showCreateDialog || showEditDialog"
        :entry="editingEntry"
        :bow-setups="bowSetups"
        :entry-types="entryTypes"
        @close="closeDialogs"
        @cancel="closeDialogs"
        @save="saveEntry"
        @auto-save="handleAutoSave"
        @draft-found="handleDraftFound"
      />
    </ClientOnly>

    <!-- View Entry Dialog -->
    <ClientOnly>
      <JournalEntryViewer
        v-if="showViewDialog"
        :show="showViewDialog"
        :entry="viewingEntry"
        @close="showViewDialog = false"
        @edit="editFromViewer"
        @delete="deleteFromViewer"
      />
    </ClientOnly>

    <!-- Draft Restore Dialog -->
    <div v-if="showDraftRestoreDialog" class="modal-overlay" @click="discardDraft">
      <div class="draft-restore-modal" @click.stop>
        <div class="draft-restore-header">
          <h3>Restore Draft</h3>
          <i class="fas fa-file-alt draft-icon"></i>
        </div>
        <div class="draft-restore-content">
          <p>We found an unsaved draft from {{ foundDraft ? formatLastSaved(foundDraft.timestamp) : '' }}:</p>
          <div class="draft-preview">
            <strong>{{ foundDraft?.title || 'Untitled' }}</strong>
            <p>{{ foundDraft?.content?.substring(0, 150) }}{{ foundDraft?.content?.length > 150 ? '...' : '' }}</p>
          </div>
        </div>
        <div class="draft-restore-actions">
          <CustomButton @click="discardDraft" variant="outlined">
            Start Fresh
          </CustomButton>
          <CustomButton @click="restoreDraft" variant="primary">
            Restore Draft
          </CustomButton>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useApi } from '@/composables/useApi'
import { useJournalApi } from '@/composables/useJournalApi'
import type { JournalEntry, JournalEntryCreate } from '@/composables/useJournalApi'
import JournalChangeLog from '~/components/JournalChangeLog.vue'
import { useGlobalNotifications } from '@/composables/useNotificationSystem'
// Removed complex filtering composable - using direct filtering instead
import { usePagination, createPaginationFromResponse } from '@/composables/usePagination'
import { debounce } from '~/utils/debounce'

// Page metadata
definePageMeta({
  // middleware: 'auth-check', // Temporarily disabled for testing
  layout: 'default'
})

// Composables
const { isLoggedIn: isAuthenticated, user } = useAuth()
const api = useApi()
const journalApi = useJournalApi()
const notifications = useGlobalNotifications()

// Reactive data
const bowSetups = ref([])

// New UX state
const showFilters = ref(false)
const viewMode = ref('list') // 'list' or 'grid'
const isFilterSticky = ref(false)
const filterSection = ref(null)

// User preferences key
const PREFERENCES_KEY = 'journal_preferences'
const quickFilters = ref([
  {
    id: 'recent',
    label: 'Recent',
    icon: 'fas fa-clock',
    filters: { sortBy: 'created_at', sortOrder: 'desc' }
  },
  {
    id: 'practice',
    label: 'Practice',
    icon: 'fas fa-target',
    filters: { entry_type: 'practice' }
  },
  {
    id: 'tuning',
    label: 'Tuning',
    icon: 'fas fa-cogs',
    filters: { entry_type: 'tuning' }
  },
  {
    id: 'competition',
    label: 'Competition',
    icon: 'fas fa-trophy',
    filters: { entry_type: 'competition' }
  }
])

// Pagination
const pagination = usePagination({
  defaultLimit: 20,
  availableLimits: [10, 20, 50],
  maxPagesShown: 5
})

// Simple reactive filter state (replacing complex useFiltering)
const filterState = reactive({
  searchQuery: '',
  selectedSetup: '',
  selectedType: '',
  selectedTags: '',
  dateFrom: '',
  dateTo: '',
  equipmentType: '',
  equipmentName: '',
  privacyFilter: '',
  hasImages: '',
  sortBy: 'created_at',
  sortDirection: 'desc',
  showPrivate: true
})

// Filter loading and error states
const filteringState = reactive({
  isFiltering: false,
  hasError: false,
  errorMessage: ''
})

// Direct filtering implementation
const filteredEntries = computed(() => {
  if (!journalApi.entries?.value) return []
  
  let filtered = [...journalApi.entries.value]
  
  // Search filter
  if (filterState.searchQuery?.trim()) {
    const query = filterState.searchQuery.toLowerCase().trim()
    filtered = filtered.filter(entry => {
      const searchableText = [
        entry.title || '',
        entry.content || '',
        entry.setup_name || '',
        ...(entry.tags || [])
      ].join(' ').toLowerCase()
      return searchableText.includes(query)
    })
  }
  
  // Bow setup filter
  if (filterState.selectedSetup) {
    filtered = filtered.filter(entry => 
      entry.bow_setup_id?.toString() === filterState.selectedSetup
    )
  }
  
  // Entry type filter
  if (filterState.selectedType) {
    filtered = filtered.filter(entry => entry.entry_type === filterState.selectedType)
  }
  
  // Tag filter
  if (filterState.selectedTags) {
    const searchTags = filterState.selectedTags.toLowerCase().split(',').map(t => t.trim()).filter(Boolean)
    if (searchTags.length > 0) {
      filtered = filtered.filter(entry => 
        entry.tags?.some(tag => 
          searchTags.some(searchTag => tag.toLowerCase().includes(searchTag))
        )
      )
    }
  }
  
  // Date range filters
  if (filterState.dateFrom) {
    const fromDate = new Date(filterState.dateFrom)
    filtered = filtered.filter(entry => {
      const entryDate = new Date(entry.created_at || entry.updated_at)
      return entryDate >= fromDate
    })
  }
  
  if (filterState.dateTo) {
    const toDate = new Date(filterState.dateTo)
    toDate.setHours(23, 59, 59, 999) // End of day
    filtered = filtered.filter(entry => {
      const entryDate = new Date(entry.created_at || entry.updated_at)
      return entryDate <= toDate
    })
  }
  
  // Equipment type filter - this would require equipment links data
  if (filterState.equipmentType) {
    filtered = filtered.filter(entry => 
      entry.equipment_links?.some(link => 
        link.equipment_type === filterState.equipmentType
      )
    )
  }
  
  // Equipment name filter - this would require equipment links data
  if (filterState.equipmentName) {
    const nameQuery = filterState.equipmentName.toLowerCase().trim()
    filtered = filtered.filter(entry => 
      entry.equipment_links?.some(link => 
        (link.equipment_name?.toLowerCase().includes(nameQuery)) ||
        (link.manufacturer?.toLowerCase().includes(nameQuery)) ||
        (link.model?.toLowerCase().includes(nameQuery))
      )
    )
  }
  
  // Privacy filter
  if (filterState.privacyFilter === 'public') {
    filtered = filtered.filter(entry => !entry.is_private)
  } else if (filterState.privacyFilter === 'private') {
    filtered = filtered.filter(entry => entry.is_private)
  }
  
  // Images filter
  if (filterState.hasImages === 'true') {
    filtered = filtered.filter(entry => entry.images?.length > 0)
  } else if (filterState.hasImages === 'false') {
    filtered = filtered.filter(entry => !entry.images?.length)
  }
  
  // Legacy privacy filter compatibility
  if (!filterState.showPrivate) {
    filtered = filtered.filter(entry => !entry.is_private)
  }
  
  return filtered
})

// Sorted entries
const sortedEntries = computed(() => {
  if (!filteredEntries.value.length) return []
  
  return [...filteredEntries.value].sort((a, b) => {
    let aValue = a[filterState.sortBy]
    let bValue = b[filterState.sortBy]
    
    if (filterState.sortBy === 'created_at' || filterState.sortBy === 'updated_at') {
      aValue = new Date(aValue).getTime()
      bValue = new Date(bValue).getTime()
    } else if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase()
      bValue = bValue?.toLowerCase() || ''
    }
    
    let comparison = 0
    if (aValue < bValue) comparison = -1
    else if (aValue > bValue) comparison = 1
    
    return filterState.sortDirection === 'desc' ? -comparison : comparison
  })
})

// Dialog states
const activeTab = ref('journal')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const showDraftRestoreDialog = ref(false)
const editingEntry = ref(null)
const viewingEntry = ref(null)
const foundDraft = ref(null)

// Computed properties
const entries = computed(() => pagination.sliceData(sortedEntries.value || []))
const entryTypes = computed(() => journalApi.defaultEntryTypes?.value || [])

// Enhanced UX computed properties with loading state
const filteredEntriesCount = computed(() => {
  if (filteringState.isFiltering) return '...'
  return filteredEntries.value?.length || 0
})

const hasActiveFilters = computed(() => {
  return !!(filterState.selectedSetup || filterState.selectedType || filterState.selectedTags || filterState.searchQuery || filterState.sortBy !== 'created_at')
})

const activeFiltersCount = computed(() => {
  let count = 0
  if (filterState.selectedSetup) count++
  if (filterState.selectedType) count++
  if (filterState.selectedTags) count++
  if (filterState.searchQuery) count++
  if (filterState.sortBy !== 'created_at') count++
  return count
})

const activeFilterChips = computed(() => {
  const chips = []
  
  if (filterState.searchQuery) {
    chips.push({
      key: 'searchQuery',
      label: 'Search',
      value: filterState.searchQuery
    })
  }
  
  if (filterState.selectedSetup && bowSetups.value?.length) {
    const setup = bowSetups.value.find(s => s.id.toString() === filterState.selectedSetup)
    if (setup) {
      chips.push({
        key: 'bow_setup_id',
        label: 'Setup',
        value: `${setup.name} (${setup.bow_type})`
      })
    }
  }
  
  if (filterState.selectedType && entryTypes.value?.length) {
    const type = entryTypes.value.find(t => t.value === filterState.selectedType)
    if (type) {
      chips.push({
        key: 'entry_type',
        label: 'Type',
        value: type.label
      })
    }
  }
  
  if (filterState.selectedTags) {
    chips.push({
      key: 'tags',
      label: 'Tags',
      value: filterState.selectedTags
    })
  }
  
  if (filterState.sortBy && filterState.sortBy !== 'created_at') {
    const sortLabels = {
      'created_at': 'Date Created',
      'updated_at': 'Date Modified', 
      'title': 'Title',
      'entry_type': 'Entry Type'
    }
    
    chips.push({
      key: 'sort',
      label: 'Sort',
      value: `${sortLabels[filterState.sortBy]} (${filterState.sortDirection === 'desc' ? 'Desc' : 'Asc'})`
    })
  }
  
  return chips
})

// Update pagination when filtered data changes
watch(
  () => filteredEntries.value?.length || 0,
  (newTotal) => {
    pagination.setTotal(newTotal)
  },
  { immediate: true }
)

// Methods
const loadEntries = async () => {
  if (!isAuthenticated.value) return

  try {
    const params = {
      page: pagination.state.page,
      limit: pagination.state.limit
    }

    if (filterState.selectedSetup) params.bow_setup_id = filterState.selectedSetup
    if (filterState.selectedType) params.entry_type = filterState.selectedType
    if (filterState.searchQuery) params.search = filterState.searchQuery
    if (filterState.selectedTags) params.tags = filterState.selectedTags

    const response = await journalApi.getEntries(params)
    
    if (response.success && response.data) {
      // Update pagination from API response
      if (response.pagination) {
        createPaginationFromResponse(response, pagination)
      }
    } else if (response.error) {
      notifications.showError(response.error)
    }
  } catch (error) {
    console.error('Failed to load journal entries:', error)
    notifications.showError('Failed to load journal entries')
  }
}

const loadPage = (page) => {
  pagination.setPage(page)
  loadEntries()
}

// Search handling with direct state management and loading feedback
const handleSearchChange = (query: string) => {
  filteringState.isFiltering = true
  filteringState.hasError = false
  
  // Use debounced update to prevent excessive filtering
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    filterState.searchQuery = query
    pagination.resetToFirstPage()
    filteringState.isFiltering = false
  }, 300)
}

// Search timeout for debouncing
let searchTimeout = null

// Clear search functionality
const clearSearch = () => {
  filterState.searchQuery = ''
  pagination.resetToFirstPage()
}

const loadBowSetups = async () => {
  try {
    const response = await api.get('/bow-setups')
    bowSetups.value = response
    
    // Update bow setup filter options
    const bowSetupOptions = response.map(setup => ({
      value: setup.id,
      label: `${setup.name} (${setup.bow_type})`
    }))
    
    // Bow setups loaded successfully
  } catch (error) {
    console.error('Failed to load bow setups:', error)
    notifications.showError('Failed to load bow setups')
    bowSetups.value = []
  }
}

const loadEntryTypes = async () => {
  try {
    const response = await journalApi.getEntryTypes()
    
    if (response.success && response.data) {
      // Update entry type filter options
      const typeOptions = response.data.map(type => ({
        value: type.value,
        label: type.label
      }))
      
      // Entry types loaded successfully
    }
  } catch (error) {
    console.error('Failed to load entry types:', error)
    notifications.showError('Failed to load entry types')
  }
}

const editEntry = (entry: JournalEntry) => {
  editingEntry.value = { ...entry }
  showEditDialog.value = true
}

const handleJournalFromChangeLog = (journalData) => {
  // Switch to journal tab
  activeTab.value = 'journal'
  
  // Open journal creation form with pre-filled data from change log
  editingEntry.value = {
    ...journalData,
    id: null // Ensure it's a new entry
  }
  showCreateDialog.value = true
}

const viewEntry = (entry: JournalEntry) => {
  // Navigate to full-page journal entry viewer
  navigateTo(`/journal/${entry.id}`)
}

const editFromViewer = () => {
  editingEntry.value = { ...viewingEntry.value }
  showViewDialog.value = false
  showEditDialog.value = true
}

const deleteFromViewer = async () => {
  if (viewingEntry.value) {
    await deleteEntry(viewingEntry.value)
    showViewDialog.value = false
  }
}

const deleteEntry = async (entry: JournalEntry) => {
  // Use notification system for confirmation
  return new Promise((resolve) => {
    notifications.showConfirmation(
      `Are you sure you want to delete "${entry.title}"?`,
      async () => {
        const response = await journalApi.deleteEntry(entry.id)
        
        if (response.success) {
          notifications.showJournalSuccess('deleted', entry.title)
          await loadEntries()
          resolve(true)
        } else {
          notifications.showJournalError('delete', response.error)
          resolve(false)
        }
      },
      () => resolve(false)
    )
  })
}

const saveEntry = async (entryData: JournalEntryCreate) => {
  let response
  
  if (editingEntry.value?.id) {
    response = await journalApi.updateEntry(editingEntry.value.id, entryData)
    
    if (response.success) {
      notifications.showJournalSuccess('updated', entryData.title)
    } else {
      notifications.showJournalError('update', response.error)
      return
    }
  } else {
    response = await journalApi.createEntry(entryData)
    
    if (response.success) {
      notifications.showJournalSuccess('created', entryData.title)
    } else {
      notifications.showJournalError('create', response.error)
      return
    }
  }
  
  closeDialogs()
  await loadEntries()
}

// Auto-save handler
const handleAutoSave = (draftData) => {
  // Auto-save is handled in the form component via localStorage
  // This could be extended to save to server if needed
  console.log('Draft auto-saved:', draftData.title)
}

// Draft restore functionality
const handleDraftFound = (draftData) => {
  foundDraft.value = draftData
  showDraftRestoreDialog.value = true
}

const restoreDraft = () => {
  // The form will handle restoring the draft data
  showDraftRestoreDialog.value = false
  foundDraft.value = null
}

const discardDraft = () => {
  // Clear the draft from localStorage
  if (foundDraft.value) {
    const key = `journal_draft_new`
    localStorage.removeItem(key)
  }
  showDraftRestoreDialog.value = false
  foundDraft.value = null
}

const closeDialogs = () => {
  showCreateDialog.value = false
  showEditDialog.value = false
  editingEntry.value = null
}

// Filter handlers with loading feedback
const handleFilterChange = (key: string, value: any) => {
  filteringState.isFiltering = true
  filteringState.hasError = false
  
  try {
    switch (key) {
      case 'bow_setup_id':
        filterState.selectedSetup = value
        break
      case 'entry_type':
        filterState.selectedType = value
        break
      case 'tags':
        filterState.selectedTags = value
        break
      case 'equipment_type':
        filterState.equipmentType = value
        break
      case 'equipment_name':
        filterState.equipmentName = value
        break
      case 'date_from':
        filterState.dateFrom = value
        break
      case 'date_to':
        filterState.dateTo = value
        break
      case 'privacy_filter':
        filterState.privacyFilter = value
        break
      case 'has_images':
        filterState.hasImages = value
        break
      default:
        console.warn(`Unknown filter key: ${key}`)
    }
    
    pagination.resetToFirstPage()
  } catch (error) {
    filteringState.hasError = true
    filteringState.errorMessage = 'Failed to apply filter'
    console.error('Filter error:', error)
  } finally {
    filteringState.isFiltering = false
  }
}

// Sort handlers with loading feedback
const handleSortChange = (sortBy: string) => {
  filteringState.isFiltering = true
  
  try {
    filterState.sortBy = sortBy || 'created_at'
    pagination.resetToFirstPage()
  } catch (error) {
    filteringState.hasError = true
    filteringState.errorMessage = 'Failed to apply sort'
  } finally {
    filteringState.isFiltering = false
  }
}

const handleSortDirectionChange = (sortOrder: string) => {
  filteringState.isFiltering = true
  
  try {
    filterState.sortDirection = sortOrder || 'desc'
    pagination.resetToFirstPage()
  } catch (error) {
    filteringState.hasError = true
    filteringState.errorMessage = 'Failed to apply sort direction'
  } finally {
    filteringState.isFiltering = false
  }
}

// Enhanced UX methods
const clearAllFilters = () => {
  filterState.searchQuery = ''
  filterState.selectedSetup = ''
  filterState.selectedType = ''
  filterState.selectedTags = ''
  filterState.dateFrom = ''
  filterState.dateTo = ''
  filterState.equipmentType = ''
  filterState.equipmentName = ''
  filterState.privacyFilter = ''
  filterState.hasImages = ''
  filterState.sortBy = 'created_at'
  filterState.sortDirection = 'desc'
  currentPresetId.value = null
  pagination.resetToFirstPage()
}

const removeFilter = (key: string) => {
  if (key === 'bow_setup_id') {
    filterState.selectedSetup = ''
  } else if (key === 'entry_type') {
    filterState.selectedType = ''
  } else if (key === 'tags') {
    filterState.selectedTags = ''
  } else if (key === 'sort') {
    filterState.sortBy = 'created_at'
    filterState.sortDirection = 'desc'
  } else if (key === 'searchQuery') {
    filterState.searchQuery = ''
  }
  pagination.resetToFirstPage()
}

const applyQuickFilter = (quickFilter: any) => {
  // Clear existing filters first
  clearAllFilters()
  
  // Apply quick filter settings
  Object.entries(quickFilter.filters).forEach(([key, value]) => {
    if (key === 'sortBy') {
      filterState.sortBy = value as string
    } else if (key === 'sortOrder') {
      filterState.sortDirection = value as string
    } else if (key === 'entry_type') {
      filterState.selectedType = value as string
    }
  })
  
  pagination.resetToFirstPage()
}

const isQuickFilterActive = (quickFilter: any) => {
  return Object.entries(quickFilter.filters).every(([key, value]) => {
    if (key === 'sortBy') {
      return filterState.sortBy === value
    } else if (key === 'sortOrder') {
      return filterState.sortDirection === value
    } else if (key === 'entry_type') {
      return filterState.selectedType === value
    }
    return false
  })
}

// User preference persistence
const loadUserPreferences = () => {
  if (!process.client) return
  
  try {
    const saved = localStorage.getItem(PREFERENCES_KEY)
    if (saved) {
      const preferences = JSON.parse(saved)
      viewMode.value = preferences.viewMode || 'list'
      showFilters.value = preferences.showFilters || false
      
      // Restore filter preferences
      if (preferences.lastSort?.sortBy) {
        filterState.sortBy = preferences.lastSort.sortBy
      }
      if (preferences.lastSort?.sortOrder) {
        filterState.sortDirection = preferences.lastSort.sortOrder
      }
    }
  } catch (error) {
    console.warn('Failed to load user preferences:', error)
  }
}

const saveUserPreferences = () => {
  if (!process.client) return
  
  try {
    const preferences = {
      viewMode: viewMode.value,
      showFilters: showFilters.value,
      lastSort: {
        sortBy: filterState.sortBy || 'created_at',
        sortOrder: filterState.sortDirection || 'desc'
      },
      lastUpdated: new Date().toISOString()
    }
    localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences))
  } catch (error) {
    console.warn('Failed to save user preferences:', error)
  }
}

// Filter presets functionality
const filterPresets = ref([])
const currentPresetId = ref(null)
const showSavePresetDialog = ref(false)

// Load filter presets from API
const loadFilterPresets = async () => {
  try {
    const response = await $fetch('/api/journal/filter-presets', {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    filterPresets.value = response.data || []
  } catch (error) {
    console.error('Failed to load filter presets:', error)
  }
}

// Apply a filter preset
const applyFilterPreset = (preset) => {
  const config = JSON.parse(preset.filter_configuration)
  
  // Apply all filter settings from preset
  Object.keys(config).forEach(key => {
    if (key in filterState) {
      filterState[key] = config[key]
    }
  })
  
  currentPresetId.value = preset.id
}

// Save current filter state as a preset
const saveFilterPreset = async (presetName) => {
  try {
    const filterConfig = {
      selectedSetup: filterState.selectedSetup,
      selectedType: filterState.selectedType,
      selectedTags: filterState.selectedTags,
      dateFrom: filterState.dateFrom,
      dateTo: filterState.dateTo,
      equipmentType: filterState.equipmentType,
      equipmentName: filterState.equipmentName,
      privacyFilter: filterState.privacyFilter,
      hasImages: filterState.hasImages,
      sortBy: filterState.sortBy,
      sortDirection: filterState.sortDirection
    }
    
    await $fetch('/api/journal/filter-presets', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}` },
      body: {
        name: presetName,
        filter_configuration: JSON.stringify(filterConfig),
        icon: 'fas fa-filter' // Default icon
      }
    })
    
    await loadFilterPresets()
    showSavePresetDialog.value = false
  } catch (error) {
    console.error('Failed to save filter preset:', error)
  }
}

// Sticky filter functionality
const handleScroll = () => {
  if (!filterSection.value) return
  
  const rect = filterSection.value.getBoundingClientRect()
  const stickyThreshold = 80 // Distance from top before becoming sticky
  
  isFilterSticky.value = rect.top <= stickyThreshold && rect.bottom > 0
}

// Lifecycle
onMounted(async () => {
  // Load user preferences first
  loadUserPreferences()
  
  if (isAuthenticated.value) {
    await Promise.all([
      loadBowSetups(),
      loadEntryTypes(),
      loadFilterPresets()
    ])
    await loadEntries()
  }
  
  // Add scroll listener for sticky behavior
  if (process.client) {
    window.addEventListener('scroll', handleScroll)
    handleScroll() // Initial check
  }
})

// Cleanup scroll listener
onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('scroll', handleScroll)
  }
})

// Watchers
watch(isAuthenticated, async (newValue) => {
  if (newValue) {
    await Promise.all([
      loadBowSetups(),
      loadEntryTypes()
    ])
    await loadEntries()
  }
})

// Watch pagination changes
watch(
  () => pagination.state.page,
  () => loadEntries()
)

watch(
  () => pagination.state.limit,
  () => loadEntries()
)

// Watch for preference changes and save them
watch(viewMode, () => {
  saveUserPreferences()
})

watch(showFilters, () => {
  saveUserPreferences()
})

watch([
  () => filterState.sortBy,
  () => filterState.sortDirection
], () => {
  saveUserPreferences()
})
</script>

<style scoped>
.journal-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Enhanced Search and Filter Interface with improved visual hierarchy */
.search-filter-section {
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 24px;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid var(--md-sys-color-outline-variant);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 100;
  backdrop-filter: blur(10px);
}

/* Sticky state */
.search-filter-section.is-sticky {
  position: sticky;
  top: 80px;
  border-radius: 0;
  margin-bottom: 0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  background: var(--md-sys-color-surface-container);
  backdrop-filter: blur(20px);
  border-left: none;
  border-right: none;
  border-top: 1px solid var(--md-sys-color-outline-variant);
  border-bottom: 2px solid var(--md-sys-color-primary);
}

/* Condensed sticky view */
.search-filter-section.is-sticky .search-bar-container {
  padding: 0.5rem 0;
}

.search-filter-section.is-sticky .quick-filters {
  display: none; /* Hide quick filters in sticky mode for space */
}

.search-filter-section.is-sticky .search-results-count {
  font-size: 0.8rem;
  padding: 0.375rem 0.5rem;
}

/* Search Bar Container */
.search-bar-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Enhanced Search Input Group */
.search-input-group {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-input {
  width: 100%;
  transition: all 0.2s ease;
}

.search-input:focus-within {
  --md-outlined-text-field-container-color: var(--md-sys-color-primary-container);
}

.search-icon {
  color: var(--md-sys-color-primary);
  font-size: 1.1rem;
}

.clear-search-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--md-sys-color-surface-container-high);
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--md-sys-color-on-surface-variant);
  transition: all 0.2s ease;
  z-index: 10;
}

.clear-search-btn:hover {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
  transform: translateY(-50%) scale(1.1);
}

/* Enhanced Search Results Indicator */
.search-results-indicator {
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 16px;
  padding: 1rem 1.25rem;
  border: 1px solid var(--md-sys-color-outline-variant);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 200px;
}

.search-results-indicator.is-loading {
  background: var(--md-sys-color-primary-container);
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 0 0 2px var(--md-sys-color-primary-container);
}

.search-results-indicator.has-error {
  background: var(--md-sys-color-error-container);
  border-color: var(--md-sys-color-error);
  box-shadow: 0 0 0 2px var(--md-sys-color-error-container);
}

.results-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.results-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-primary);
  font-size: 1rem;
}

.search-results-indicator.is-loading .results-icon {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.search-results-indicator.has-error .results-icon {
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
}

.results-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.results-count {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
}

.results-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-loading-spinner {
  width: 20px;
  height: 20px;
}

.error-text {
  color: var(--md-sys-color-on-error-container);
  font-weight: 600;
}

/* Enhanced Quick Filter Pills */
.quick-filters-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.quick-filters-label {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.quick-filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.quick-filter-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--md-sys-color-surface-container);
  border: 2px solid var(--md-sys-color-outline-variant);
  border-radius: 24px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.quick-filter-pill::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.quick-filter-pill:hover::before {
  transform: translateX(100%);
}

.quick-filter-pill:hover {
  background: var(--md-sys-color-surface-container-highest);
  border-color: var(--md-sys-color-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-filter-pill.active {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.pill-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--md-sys-color-primary-container);
}

.quick-filter-pill.active .pill-icon-wrapper {
  background: var(--md-sys-color-on-primary);
}

.pill-icon {
  font-size: 0.875rem;
  color: var(--md-sys-color-primary);
}

.quick-filter-pill.active .pill-icon {
  color: var(--md-sys-color-primary);
}

.pill-label {
  font-weight: 600;
  letter-spacing: 0.025em;
}

/* Enhanced Filter Controls Header */
.filter-controls-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.filter-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--md-sys-color-surface-container);
  border: 2px solid var(--md-sys-color-outline-variant);
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  min-width: 240px;
  overflow: hidden;
}

.filter-toggle-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--md-sys-color-primary-container), var(--md-sys-color-tertiary-container));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.filter-toggle-btn:hover::before {
  opacity: 0.1;
}

.filter-toggle-btn:hover {
  background: var(--md-sys-color-surface-container-high);
  border-color: var(--md-sys-color-primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.toggle-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  position: relative;
  z-index: 1;
}

.toggle-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  font-size: 1rem;
  transition: all 0.2s ease;
}

.toggle-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.125rem;
}

.toggle-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  line-height: 1.2;
}

.toggle-subtitle {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--md-sys-color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.toggle-chevron {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  transition: transform 0.3s ease;
  position: relative;
  z-index: 1;
}

.filter-control-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.clear-filters-btn, .save-preset-btn-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 2px solid;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.clear-filters-btn {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
  border-color: var(--md-sys-color-error);
}

.clear-filters-btn:hover {
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--md-sys-color-error), 0.2);
}

.save-preset-btn-header {
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
  border-color: var(--md-sys-color-tertiary);
}

.save-preset-btn-header:hover {
  background: var(--md-sys-color-tertiary);
  color: var(--md-sys-color-on-tertiary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--md-sys-color-tertiary), 0.2);
}

/* Enhanced Active Filter Chips */
.active-filters-chips {
  padding: 1.5rem 0;
  border-top: 2px solid var(--md-sys-color-outline-variant);
  margin-top: 1.5rem;
  background: var(--md-sys-color-surface-container-low);
  border-radius: 16px;
  padding: 1.5rem;
}

.chips-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.chips-title {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chips-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0 8px;
}

.chips-container {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  border: 2px solid var(--md-sys-color-secondary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.filter-chip::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.filter-chip:hover::before {
  opacity: 1;
}

.filter-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chip-content {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.chip-label {
  font-weight: 700;
  color: var(--md-sys-color-on-secondary-container);
}

.chip-separator {
  opacity: 0.6;
  margin: 0 0.25rem;
}

.chip-value {
  font-weight: 500;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  padding: 0.125rem 0.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
}

.remove-chip-btn {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  transition: all 0.2s ease;
  position: relative;
  z-index: 1;
}

.remove-chip-btn:hover {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
  border-color: var(--md-sys-color-error);
  transform: scale(1.1);
}

/* Collapsible Filter Panel */
.filters-panel {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filter-groups {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.filter-group {
  background: var(--md-sys-color-surface);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 16px;
  padding: 1.5rem;
}

.filter-group-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
}

.filter-group-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-control {
  flex: 1;
  min-width: 200px;
}

.filter-control.full-width {
  width: 100%;
  min-width: unset;
}

/* Entries Container Styling */
.entries-container {
  min-height: 400px;
}

.entries-section {
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.entries-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.entries-header-content {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.entries-title-section {
  flex: 1;
}

.entries-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
}

.entries-count {
  font-size: 1rem;
  font-weight: 500;
  color: var(--md-sys-color-primary);
  margin-left: 0.5rem;
}

.entries-subtitle {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  margin: 0;
}

/* View Mode Controls */
.view-mode-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-toggle-group {
  display: flex;
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  padding: 4px;
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: var(--md-sys-color-on-surface-variant);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 40px;
  height: 40px;
  font-size: 1rem;
}

.view-toggle-btn:hover {
  background: var(--md-sys-color-surface-container-highest);
}

.view-toggle-btn.active {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Entries List Layouts */
.entries-list {
  display: flex;
  gap: 1.5rem;
}

/* List View (default) */
.entries-list.entries-list {
  flex-direction: column;
}

/* Grid View */
.entries-list.entries-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

/* Loading and Empty States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  text-align: center;
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  text-align: center;
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.empty-icon-container {
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 50%;
  padding: 2rem;
  margin-bottom: 2rem;
}

.empty-icon {
  font-size: 3rem;
  color: var(--md-sys-color-primary);
}

.empty-content {
  max-width: 500px;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 1rem;
}

.empty-description {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 2rem;
}

.empty-action {
  margin-top: 1rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1.5rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 12px;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.pagination-pages {
  display: flex;
  gap: 0.5rem;
}

.page-info {
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
  font-size: 0.875rem;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-page {
    padding: 1rem;
  }

  .filters-section {
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .filters-title {
    font-size: 1.125rem;
  }

  .search-input {
    max-width: none;
  }

  .filter-controls {
    flex-direction: column;
    gap: 1rem;
  }

  /* Enhanced mobile responsiveness for new interface */
  .search-filter-section {
    padding: 1rem;
  }
  
  .search-input-wrapper {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .search-input {
    min-width: unset;
    width: 100%;
  }
  
  .search-results-count {
    order: 1;
    align-self: center;
  }
  
  .quick-filters {
    justify-content: center;
  }
  
  .quick-filter-pill {
    flex: 1;
    justify-content: center;
    min-width: 0;
    font-size: 0.8rem;
    padding: 0.4rem 0.6rem;
  }
  
  .filter-controls-header {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .filter-toggle-btn,
  .clear-filters-btn {
    width: 100%;
    justify-content: center;
    padding: 1rem;
  }
  
  .filter-group {
    padding: 1rem;
  }
  
  .filter-row {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .filter-control {
    min-width: unset;
    width: 100%;
  }
  
  .chips-container {
    justify-content: center;
    gap: 0.4rem;
  }
  
  .filter-chip {
    font-size: 0.8rem;
    padding: 0.4rem 0.6rem;
  }

  .entries-section {
    padding: 1.5rem;
  }
  
  .entries-header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .view-mode-controls {
    align-self: center;
  }

  .entries-title {
    font-size: 1.25rem;
  }

  .entries-list {
    gap: 1.25rem;
  }
  
  /* Grid view adjustments for mobile */
  .entries-list.entries-grid {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 0.75rem;
    padding: 1rem;
  }

  .empty-state {
    padding: 3rem 2rem;
  }

  .empty-icon-container {
    padding: 1.5rem;
  }

  .empty-title {
    font-size: 1.25rem;
  }
}

/* Draft Restore Dialog Styling */
.draft-restore-modal {
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  max-width: 500px;
  width: 90%;
  overflow: hidden;
  border: 1px solid var(--md-sys-color-outline-variant);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.draft-restore-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.draft-restore-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.draft-icon {
  font-size: 1.5rem;
  opacity: 0.8;
}

.draft-restore-content {
  padding: 1.5rem;
}

.draft-restore-content p {
  margin: 0 0 1rem 0;
  color: var(--md-sys-color-on-surface-variant);
}

.draft-preview {
  background: var(--md-sys-color-surface-container);
  border-radius: 12px;
  padding: 1rem;
  border-left: 4px solid var(--md-sys-color-primary);
}

.draft-preview strong {
  display: block;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.draft-preview p {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  line-height: 1.4;
}

.draft-restore-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface-container-low);
}

/* Filter Presets Styles */
.filter-presets-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.preset-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
}

.preset-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 20px;
  background: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-on-surface);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.preset-btn:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container-high);
  transform: translateY(-1px);
}

.preset-btn.active {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.save-preset-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px dashed var(--md-sys-color-primary);
  border-radius: 20px;
  background: transparent;
  color: var(--md-sys-color-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.save-preset-btn:hover {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

/* Tab Navigation Styles */
.tab-navigation {
  margin-bottom: 2rem;
}

.tab-buttons {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid var(--md-sys-color-outline-variant);
  padding-bottom: 0;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  border-radius: 8px 8px 0 0;
}

.tab-btn:hover {
  background: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-on-surface);
}

.tab-btn.active {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  border-bottom-color: var(--md-sys-color-primary);
}

.tab-count {
  background: var(--md-sys-color-outline);
  color: var(--md-sys-color-on-surface);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.tab-btn.active .tab-count {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

/* Change Log Container */
.changelog-container {
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid var(--md-sys-color-outline-variant);
}
</style>