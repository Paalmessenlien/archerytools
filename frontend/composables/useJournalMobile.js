import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { debounce } from 'lodash-es'

/**
 * Mobile Journal Composable
 * Provides unified journal logic and mobile interactions for journal components
 */
export function useJournalMobile(props, emit) {
  // Mobile state management
  const isMobile = ref(false)
  const showQuickEntry = ref(false)
  const showMobileFilter = ref(false)
  const loadingMore = ref(false)
  
  // Filter state
  const filters = ref({
    search: '',
    entryTypes: [],
    dateRange: 'all',
    customDateStart: null,
    customDateEnd: null,
    favoritesOnly: false,
    hasImages: false,
    hasLinkedChanges: false,
    tags: [],
    ...props.initialFilters
  })
  
  // Quick filters configuration
  const quickFilters = ref([
    {
      key: 'favorites',
      label: 'Favorites',
      icon: 'star',
      active: computed(() => filters.value.favoritesOnly),
      action: () => toggleQuickFilter('favorites')
    },
    {
      key: 'images',
      label: 'With Images',
      icon: 'image',
      active: computed(() => filters.value.hasImages),
      action: () => toggleQuickFilter('images')
    },
    {
      key: 'changes',
      label: 'Linked Changes',
      icon: 'link',
      active: computed(() => filters.value.hasLinkedChanges),
      action: () => toggleQuickFilter('changes')
    },
    {
      key: 'recent',
      label: 'This Week',
      icon: 'schedule',
      active: computed(() => filters.value.dateRange === 'week'),
      action: () => toggleQuickFilter('recent')
    }
  ])
  
  // Pull-to-refresh state
  const pullRefreshActive = ref(false)
  const pullRefreshStartY = ref(0)
  const pullRefreshCurrentY = ref(0)
  const pullRefreshThreshold = 80
  
  // Pagination state
  const currentPage = ref(1)
  const itemsPerPage = 20
  const displayedCount = ref(itemsPerPage)
  
  // Touch/gesture state
  const touchStartTime = ref(0)
  const touchStartY = ref(0)
  const touchCurrentY = ref(0)
  const isScrolling = ref(false)
  
  // Computed properties
  const hasActiveFilters = computed(() => {
    const f = filters.value
    return (
      (f.search && f.search.trim().length > 0) ||
      (f.entryTypes && f.entryTypes.length > 0) ||
      (f.dateRange && f.dateRange !== 'all') ||
      f.favoritesOnly ||
      f.hasImages ||
      f.hasLinkedChanges ||
      (f.tags && f.tags.length > 0)
    )
  })
  
  const activeFiltersCount = computed(() => {
    let count = 0
    const f = filters.value
    
    if (f.search && f.search.trim().length > 0) count++
    if (f.entryTypes && f.entryTypes.length > 0) count++
    if (f.dateRange && f.dateRange !== 'all') count++
    if (f.favoritesOnly) count++
    if (f.hasImages) count++
    if (f.hasLinkedChanges) count++
    if (f.tags && f.tags.length > 0) count++
    
    return count
  })
  
  const filteredEntries = computed(() => {
    if (!props.entries || props.entries.length === 0) {
      return []
    }
    
    let filtered = [...props.entries]
    const f = filters.value
    
    // Search filter
    if (f.search && f.search.trim()) {
      const searchTerm = f.search.toLowerCase().trim()
      filtered = filtered.filter(entry =>
        entry.title?.toLowerCase().includes(searchTerm) ||
        entry.content?.toLowerCase().includes(searchTerm) ||
        (entry.tags && entry.tags.some(tag => 
          tag.toLowerCase().includes(searchTerm)
        ))
      )
    }
    
    // Entry type filter
    if (f.entryTypes && f.entryTypes.length > 0) {
      filtered = filtered.filter(entry => 
        f.entryTypes.includes(entry.entry_type)
      )
    }
    
    // Date range filter
    if (f.dateRange && f.dateRange !== 'all') {
      const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      
      filtered = filtered.filter(entry => {
        const entryDate = new Date(entry.created_at)
        
        switch (f.dateRange) {
          case 'today':
            return entryDate >= today
          case 'week':
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
            return entryDate >= weekAgo
          case 'month':
            const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
            return entryDate >= monthAgo
          case 'quarter':
            const quarterAgo = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000)
            return entryDate >= quarterAgo
          case 'year':
            const yearAgo = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000)
            return entryDate >= yearAgo
          case 'custom':
            if (f.customDateStart && f.customDateEnd) {
              const startDate = new Date(f.customDateStart)
              const endDate = new Date(f.customDateEnd)
              return entryDate >= startDate && entryDate <= endDate
            }
            return true
          default:
            return true
        }
      })
    }
    
    // Favorites filter
    if (f.favoritesOnly) {
      filtered = filtered.filter(entry => entry.is_favorite)
    }
    
    // Images filter
    if (f.hasImages) {
      filtered = filtered.filter(entry => 
        entry.images && entry.images.length > 0
      )
    }
    
    // Linked changes filter
    if (f.hasLinkedChanges) {
      filtered = filtered.filter(entry => 
        entry.linked_changes && entry.linked_changes.length > 0
      )
    }
    
    // Tags filter
    if (f.tags && f.tags.length > 0) {
      filtered = filtered.filter(entry => 
        entry.tags && entry.tags.some(tag => f.tags.includes(tag))
      )
    }
    
    // Sort by created date (newest first)
    return filtered.sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    )
  })
  
  const displayedEntries = computed(() => {
    return filteredEntries.value.slice(0, displayedCount.value)
  })
  
  const hasMoreEntries = computed(() => {
    return filteredEntries.value.length > displayedCount.value
  })
  
  // Mobile detection
  const checkMobile = () => {
    isMobile.value = window.innerWidth < 768
  }
  
  // Quick entry management
  const toggleQuickEntry = () => {
    showQuickEntry.value = !showQuickEntry.value
    
    if (showQuickEntry.value) {
      // Hide mobile filter if open
      hideMobileFilter()
      
      // Focus first input after animation
      nextTick(() => {
        const firstInput = document.querySelector('.quick-entry-content input, .quick-entry-content textarea')
        if (firstInput) {
          firstInput.focus()
        }
      })
    }
  }
  
  const hideQuickEntry = () => {
    showQuickEntry.value = false
  }
  
  // Mobile filter management
  const toggleMobileFilter = () => {
    showMobileFilter.value = !showMobileFilter.value
    
    if (showMobileFilter.value) {
      // Hide quick entry if open
      hideQuickEntry()
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden'
    } else {
      // Restore body scroll
      document.body.style.overflow = ''
    }
  }
  
  const hideMobileFilter = () => {
    showMobileFilter.value = false
    document.body.style.overflow = ''
  }
  
  // Filter management
  const toggleQuickFilter = (filterKey) => {
    switch (filterKey) {
      case 'favorites':
        filters.value.favoritesOnly = !filters.value.favoritesOnly
        break
      case 'images':
        filters.value.hasImages = !filters.value.hasImages
        break
      case 'changes':
        filters.value.hasLinkedChanges = !filters.value.hasLinkedChanges
        break
      case 'recent':
        filters.value.dateRange = filters.value.dateRange === 'week' ? 'all' : 'week'
        break
    }
    
    // Emit filter update
    emit('filters:update', { ...filters.value })
  }
  
  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    emit('filters:update', { ...filters.value })
  }
  
  const clearFilters = () => {
    filters.value = {
      search: '',
      entryTypes: [],
      dateRange: 'all',
      customDateStart: null,
      customDateEnd: null,
      favoritesOnly: false,
      hasImages: false,
      hasLinkedChanges: false,
      tags: []
    }
    
    emit('filters:update', { ...filters.value })
  }
  
  // Load more functionality
  const loadMoreEntries = async () => {
    if (loadingMore.value || !hasMoreEntries.value) return
    
    loadingMore.value = true
    
    try {
      // Simulate loading delay for UX
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Increase displayed count
      displayedCount.value = Math.min(
        displayedCount.value + itemsPerPage,
        filteredEntries.value.length
      )
      
      // Emit load more event for parent to handle if needed
      emit('load-more', {
        currentCount: displayedCount.value,
        totalCount: filteredEntries.value.length
      })
      
    } catch (error) {
      console.error('Error loading more entries:', error)
    } finally {
      loadingMore.value = false
    }
  }
  
  // Pull-to-refresh functionality
  const handlePullStart = (event) => {
    if (!props.pullToRefresh || window.scrollY > 0) return
    
    const touch = event.touches[0]
    pullRefreshStartY.value = touch.clientY
    touchStartTime.value = Date.now()
  }
  
  const handlePullMove = (event) => {
    if (!props.pullToRefresh || window.scrollY > 0) return
    
    const touch = event.touches[0]
    pullRefreshCurrentY.value = touch.clientY
    const deltaY = pullRefreshCurrentY.value - pullRefreshStartY.value
    
    if (deltaY > 0 && deltaY < pullRefreshThreshold * 2) {
      event.preventDefault()
      pullRefreshActive.value = deltaY > pullRefreshThreshold
    }
  }
  
  const handlePullEnd = (event) => {
    if (!props.pullToRefresh) return
    
    const deltaY = pullRefreshCurrentY.value - pullRefreshStartY.value
    const deltaTime = Date.now() - touchStartTime.value
    
    if (deltaY > pullRefreshThreshold && deltaTime > 200) {
      // Trigger refresh
      emit('refresh')
      
      // Haptic feedback if supported
      if ('vibrate' in navigator) {
        navigator.vibrate(50)
      }
      
      // Reset after delay
      setTimeout(() => {
        pullRefreshActive.value = false
      }, 1000)
    } else {
      pullRefreshActive.value = false
    }
    
    // Reset values
    pullRefreshStartY.value = 0
    pullRefreshCurrentY.value = 0
  }
  
  // Setup pull-to-refresh
  const setupPullToRefresh = () => {
    if (!props.pullToRefresh) return
    
    const container = document.querySelector('.base-journal-view')
    if (!container) return
    
    container.addEventListener('touchstart', handlePullStart, { passive: false })
    container.addEventListener('touchmove', handlePullMove, { passive: false })
    container.addEventListener('touchend', handlePullEnd)
    
    return () => {
      container.removeEventListener('touchstart', handlePullStart)
      container.removeEventListener('touchmove', handlePullMove)
      container.removeEventListener('touchend', handlePullEnd)
    }
  }
  
  // Debounced search
  const debouncedSearch = debounce((searchTerm) => {
    filters.value.search = searchTerm
    emit('filters:update', { ...filters.value })
  }, 300)
  
  // Scroll to top helper
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
  
  // Reset pagination when filters change
  watch(() => filters.value, () => {
    displayedCount.value = itemsPerPage
    currentPage.value = 1
  }, { deep: true })
  
  // Setup mobile detection
  onMounted(() => {
    checkMobile()
    window.addEventListener('resize', checkMobile)
    
    // Close mobile filter on escape key
    const handleEscKey = (event) => {
      if (event.key === 'Escape') {
        if (showMobileFilter.value) {
          hideMobileFilter()
        } else if (showQuickEntry.value) {
          hideQuickEntry()
        }
      }
    }
    
    document.addEventListener('keydown', handleEscKey)
    
    // Cleanup function
    return () => {
      window.removeEventListener('resize', checkMobile)
      document.removeEventListener('keydown', handleEscKey)
    }
  })
  
  // Cleanup on unmount
  onUnmounted(() => {
    // Restore body scroll
    document.body.style.overflow = ''
  })
  
  // Public API
  return {
    // State
    isMobile,
    showQuickEntry,
    showMobileFilter,
    loadingMore,
    pullRefreshActive,
    filters,
    
    // Computed
    hasActiveFilters,
    activeFiltersCount,
    filteredEntries,
    displayedEntries,
    quickFilters,
    hasMoreEntries,
    
    // Methods
    toggleQuickEntry,
    hideQuickEntry,
    toggleMobileFilter,
    hideMobileFilter,
    toggleQuickFilter,
    updateFilters,
    clearFilters,
    loadMoreEntries,
    setupPullToRefresh,
    debouncedSearch,
    scrollToTop,
    
    // Mobile helpers
    checkMobile
  }
}

/**
 * Journal Entry Management Composable
 * Provides CRUD operations for journal entries
 */
export function useJournalEntries(api) {
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)
  
  const createEntry = async (entryData) => {
    saving.value = true
    error.value = null
    
    try {
      const response = await api.post('/journal/entries', entryData)
      return response
    } catch (err) {
      error.value = err.message || 'Failed to create journal entry'
      throw err
    } finally {
      saving.value = false
    }
  }
  
  const updateEntry = async (entryId, entryData) => {
    saving.value = true
    error.value = null
    
    try {
      const response = await api.put(`/journal/entries/${entryId}`, entryData)
      return response
    } catch (err) {
      error.value = err.message || 'Failed to update journal entry'
      throw err
    } finally {
      saving.value = false
    }
  }
  
  const deleteEntry = async (entryId) => {
    saving.value = true
    error.value = null
    
    try {
      await api.delete(`/journal/entries/${entryId}`)
      return true
    } catch (err) {
      error.value = err.message || 'Failed to delete journal entry'
      throw err
    } finally {
      saving.value = false
    }
  }
  
  const toggleFavorite = async (entry) => {
    try {
      const response = await api.patch(`/journal/entries/${entry.id}/favorite`, {
        is_favorite: !entry.is_favorite
      })
      return response
    } catch (err) {
      error.value = err.message || 'Failed to update favorite status'
      throw err
    }
  }
  
  return {
    loading,
    saving,
    error,
    createEntry,
    updateEntry,
    deleteEntry,
    toggleFavorite
  }
}

export default useJournalMobile