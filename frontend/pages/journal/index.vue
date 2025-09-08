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

    <!-- Mobile-First Unified Journal Interface -->

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

    <!-- Mobile-First Journal Interface -->
    <BaseJournalView
      v-if="activeTab === 'journal'"
      :context="'general'"
      :title="'Journal'"
      :subtitle="'Your archery journey documented'"
      :entries="sortedEntries"
      :bow-setups="bowSetups"
      :entry-types="entryTypes"
      :stats="journalStats"
      :loading="journalApi.isLoading.value"
      :has-more-entries="hasMoreEntriesFromPagination"
      :initial-filters="mobileFriendlyFilters"
      @entry:edit="editEntry"
      @entry:delete="deleteEntry"
      @entry:create="handleCreateEntry"
      @entry:favorite="handleToggleFavorite"
      @filters:update="handleMobileFiltersUpdate"
      @load-more="handleLoadMore"
      @refresh="handleRefresh"
      class="mobile-journal-container"
    />

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
import BaseJournalView from '~/components/journal/BaseJournalView.vue'
import JournalEntryDetailViewer from '~/components/journal/JournalEntryDetailViewer.vue'
import { useGlobalNotifications } from '@/composables/useNotificationSystem'
// Removed complex filtering composable - using direct filtering instead
import { usePagination, createPaginationFromResponse } from '@/composables/usePagination'
import { debounce } from '~/utils/debounce'

// Page metadata
definePageMeta({
  middleware: ['auth-check'],
  layout: 'default'
})

// Composables
const { isLoggedIn: isAuthenticated, user, token } = useAuth()
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
const showDraftRestoreDialog = ref(false)
const editingEntry = ref(null)
const foundDraft = ref(null)

// Computed properties
const entries = computed(() => pagination.sliceData(sortedEntries.value || []))
const entryTypes = computed(() => journalApi.defaultEntryTypes?.value || [])

// Mobile-first computed properties
const journalStats = computed(() => {
  const totalEntries = journalApi.entries?.value?.length || 0
  const recentEntries = (journalApi.entries?.value || []).filter(entry => {
    const entryDate = new Date(entry.created_at)
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    return entryDate >= weekAgo
  }).length
  
  const favoriteEntries = (journalApi.entries?.value || []).filter(entry => entry.is_favorite).length
  const entriesWithChanges = (journalApi.entries?.value || []).filter(entry => 
    entry.linked_changes && entry.linked_changes.length > 0
  ).length

  return {
    total: { value: totalEntries, label: 'Total' },
    recent: { value: recentEntries, label: 'This Week' },
    favorites: { value: favoriteEntries, label: 'Favorites' },
    changes: { value: entriesWithChanges, label: 'With Changes' }
  }
})

const mobileFriendlyFilters = computed(() => {
  return {
    search: filterState.searchQuery || '',
    entryTypes: filterState.selectedType ? [filterState.selectedType] : [],
    dateRange: 'all',
    customDateStart: filterState.dateFrom || null,
    customDateEnd: filterState.dateTo || null,
    favoritesOnly: false,
    hasImages: filterState.hasImages === 'true',
    hasLinkedChanges: false,
    tags: filterState.selectedTags ? filterState.selectedTags.split(',').map(t => t.trim()).filter(Boolean) : []
  }
})

const hasMoreEntriesFromPagination = computed(() => {
  return pagination.meta.hasNextPage
})

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

// Mobile-first event handlers
const handleCreateEntry = (entryData) => {
  editingEntry.value = entryData
  showCreateDialog.value = true
}

const handleToggleFavorite = async (entry) => {
  try {
    const response = await journalApi.toggleFavorite(entry)
    if (response.success) {
      await loadEntries() // Refresh entries to show updated favorite status
      notifications.showSuccess(`Entry ${entry.is_favorite ? 'removed from' : 'added to'} favorites`)
    } else {
      notifications.showError('Failed to update favorite status')
    }
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
    notifications.showError('Failed to update favorite status')
  }
}

const handleMobileFiltersUpdate = (filters) => {
  // Update legacy filter state from mobile filters
  filterState.searchQuery = filters.search || ''
  filterState.selectedType = filters.entryTypes?.length ? filters.entryTypes[0] : ''
  filterState.selectedTags = filters.tags?.join(', ') || ''
  filterState.dateFrom = filters.customDateStart || ''
  filterState.dateTo = filters.customDateEnd || ''
  filterState.hasImages = filters.hasImages ? 'true' : ''
  
  // Reset pagination when filters change
  pagination.resetToFirstPage()
}

const handleLoadMore = ({ currentCount, totalCount }) => {
  // Load more entries if using client-side pagination
  console.log('Load more requested:', currentCount, 'of', totalCount)
}

const handleRefresh = async () => {
  try {
    await loadEntries()
    notifications.showSuccess('Journal refreshed')
  } catch (error) {
    console.error('Failed to refresh:', error)
    notifications.showError('Failed to refresh journal')
  }
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
    const response = await api.get('/journal/filter-presets')
    filterPresets.value = response.data || []
  } catch (error) {
    console.warn('Filter presets not available:', error.message)
    // Filter presets are optional - journal works without them
    filterPresets.value = []
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
    
    await api.post('/journal/filter-presets', {
      name: presetName,
      filter_configuration: JSON.stringify(filterConfig),
      icon: 'fas fa-filter' // Default icon
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
      loadEntryTypes()
      // loadFilterPresets() - optional feature, load separately
    ])
    // Load filter presets separately - disabled due to API issues
    // loadFilterPresets()
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
/* Mobile-First Journal Page Styles */
.journal-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.5rem;
}

@media (min-width: 640px) {
  .journal-page {
    padding: 1rem;
  }
}

@media (min-width: 1024px) {
  .journal-page {
    padding: 2rem;
  }
}

/* Mobile Journal Container */
.mobile-journal-container {
  background: var(--md-sys-color-surface);
  border-radius: 1rem;
  overflow: hidden;
  margin-bottom: 1rem;
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
  touch-action: manipulation;
  min-height: var(--mobile-touch-target-min, 44px);
}

.tab-btn:hover {
  background: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-on-surface);
}

.tab-btn:active {
  transform: scale(0.98);
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

/* Change Log Container */
.changelog-container {
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid var(--md-sys-color-outline-variant);
}

/* Pagination */
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
    padding: 0.75rem;
  }
  
  .mobile-journal-container {
    border-radius: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .tab-btn {
    padding: 0.75rem 1rem;
    font-size: 0.8125rem;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 0.75rem;
    padding: 1rem;
  }
  
  .changelog-container {
    padding: 1.5rem;
  }
  
  .draft-restore-modal {
    width: 95%;
  }
  
  .draft-restore-header {
    padding: 1rem;
  }
  
  .draft-restore-content {
    padding: 1rem;
  }
  
  .draft-restore-actions {
    padding: 1rem;
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .journal-page {
    padding: 0.5rem;
  }
  
  .mobile-journal-container {
    border-radius: 0.25rem;
  }
  
  .tab-buttons {
    gap: 0.25rem;
  }
  
  .tab-btn {
    padding: 0.625rem 0.75rem;
    font-size: 0.75rem;
    flex: 1;
    justify-content: center;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .mobile-journal-container,
  .draft-restore-modal,
  .changelog-container {
    border-width: 2px;
  }
  
  .tab-buttons {
    border-bottom-width: 3px;
  }
  
  .tab-btn.active {
    border-bottom-width: 3px;
  }
}
</style>