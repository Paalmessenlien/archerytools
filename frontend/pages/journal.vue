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
          <md-outlined-text-field
            :value="filterState.searchQuery || ''"
            placeholder="Search journal entries..."
            class="search-input"
            @input="(e) => handleSearchChange(e.target.value)"
          >
            <i slot="leading-icon" class="fas fa-search"></i>
          </md-outlined-text-field>
          
          <!-- Search Results Count -->
          <div v-if="filterState.searchQuery || hasActiveFilters" class="search-results-count"
               :class="{ 'is-loading': filteringState.isFiltering, 'has-error': filteringState.hasError }">
            <i v-if="!filteringState.isFiltering" class="fas fa-list-alt mr-1"></i>
            <md-circular-progress v-if="filteringState.isFiltering" indeterminate class="filter-loading"></md-circular-progress>
            <i v-if="filteringState.hasError" class="fas fa-exclamation-triangle mr-1"></i>
            <span v-if="!filteringState.hasError">
              {{ filteredEntriesCount }} {{ filteredEntriesCount === 1 || filteredEntriesCount === '...' ? 'entry' : 'entries' }} found
            </span>
            <span v-if="filteringState.hasError" class="error-text">
              {{ filteringState.errorMessage }}
            </span>
          </div>
        </div>

        <!-- Quick Filter Pills -->
        <div class="quick-filters" v-if="!showFilters">
          <button 
            v-for="quickFilter in quickFilters" 
            :key="quickFilter.id"
            @click="applyQuickFilter(quickFilter)"
            class="quick-filter-pill"
            :class="{ active: isQuickFilterActive(quickFilter) }"
          >
            <i :class="quickFilter.icon" class="mr-1"></i>
            {{ quickFilter.label }}
          </button>
        </div>

        <!-- Filter Toggle & Controls -->
        <div class="filter-controls-header">
          <button @click="showFilters = !showFilters" class="filter-toggle-btn">
            <i :class="showFilters ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="mr-2"></i>
            {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
            <span v-if="hasActiveFilters && !showFilters" class="active-filters-badge">
              {{ activeFiltersCount }}
            </span>
          </button>

          <button 
            v-if="hasActiveFilters" 
            @click="clearAllFilters" 
            class="clear-filters-btn"
          >
            <i class="fas fa-times mr-1"></i>
            Clear All
          </button>
        </div>
      </div>

      <!-- Active Filter Chips -->
      <div v-if="hasActiveFilters" class="active-filters-chips">
        <div class="chips-container">
          <span 
            v-for="chip in activeFilterChips" 
            :key="chip.key"
            class="filter-chip"
          >
            {{ chip.label }}: {{ chip.value }}
            <button @click="removeFilter(chip.key)" class="remove-chip-btn">
              <i class="fas fa-times"></i>
            </button>
          </span>
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
              Advanced
            </h3>
            <div class="filter-group-controls">
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
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Journal Entries List -->
    <div class="entries-container">
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
  
  // Privacy filter
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

const viewEntry = async (entry: JournalEntry) => {
  const response = await journalApi.getEntry(entry.id)
  
  if (response.success && response.data) {
    viewingEntry.value = response.data
    showViewDialog.value = true
  } else {
    notifications.showError(response.error || 'Failed to load entry details')
  }
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
    if (key === 'bow_setup_id') {
      filterState.selectedSetup = value
    } else if (key === 'entry_type') {
      filterState.selectedType = value
    } else if (key === 'tags') {
      filterState.selectedTags = value
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
  filterState.sortBy = 'created_at'
  filterState.sortDirection = 'desc'
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
      loadEntryTypes()
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

/* Enhanced Search and Filter Interface */
.search-filter-section {
  background: var(--md-sys-color-surface-container);
  border-radius: 20px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid var(--md-sys-color-outline-variant);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  z-index: 100;
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

.search-input {
  flex: 1;
  min-width: 300px;
}

.search-results-count {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
  background: var(--md-sys-color-surface-container-highest);
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.search-results-count.is-loading {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.search-results-count.has-error {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

.filter-loading {
  width: 16px;
  height: 16px;
  margin-right: 0.5rem;
}

.error-text {
  color: var(--md-sys-color-error);
  font-weight: 500;
}

/* Quick Filter Pills */
.quick-filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.quick-filter-pill {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background: var(--md-sys-color-surface);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.quick-filter-pill:hover {
  background: var(--md-sys-color-surface-container-highest);
  transform: translateY(-1px);
}

.quick-filter-pill.active {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  border-color: var(--md-sys-color-primary);
}

/* Filter Controls Header */
.filter-controls-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.filter-toggle-btn {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--md-sys-color-surface);
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.filter-toggle-btn:hover {
  background: var(--md-sys-color-surface-container-highest);
}

.active-filters-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.clear-filters-btn {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
  border: none;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filters-btn:hover {
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
}

/* Active Filter Chips */
.active-filters-chips {
  padding: 1rem 0;
  border-top: 1px solid var(--md-sys-color-outline-variant);
  margin-top: 1rem;
}

.chips-container {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 500;
}

.remove-chip-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  transition: background 0.2s ease;
}

.remove-chip-btn:hover {
  background: rgba(0, 0, 0, 0.1);
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
</style>