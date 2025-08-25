/**
 * Reusable Pagination Composable
 * Provides standardized pagination functionality with advanced features
 */

import { ref, computed, reactive, watch } from 'vue'

export interface PaginationConfig {
  defaultPage?: number
  defaultLimit?: number
  availableLimits?: number[]
  maxPagesShown?: number
  showFirstLast?: boolean
  showPrevNext?: boolean
  showPageInfo?: boolean
  showLimitSelector?: boolean
}

export interface PaginationState {
  page: number
  limit: number
  total: number
  pages: number
}

export interface PaginationMeta {
  hasNextPage: boolean
  hasPrevPage: boolean
  isFirstPage: boolean
  isLastPage: boolean
  startItem: number
  endItem: number
  visiblePages: number[]
}

export const usePagination = (config: PaginationConfig = {}) => {
  // Configuration with defaults
  const {
    defaultPage = 1,
    defaultLimit = 20,
    availableLimits = [10, 20, 50, 100],
    maxPagesShown = 5,
    showFirstLast = true,
    showPrevNext = true,
    showPageInfo = true,
    showLimitSelector = true
  } = config

  // Reactive state
  const state = reactive<PaginationState>({
    page: defaultPage,
    limit: defaultLimit,
    total: 0,
    pages: 0
  })

  // Computed pagination metadata
  const meta = computed<PaginationMeta>(() => {
    const hasNextPage = state.page < state.pages
    const hasPrevPage = state.page > 1
    const isFirstPage = state.page === 1
    const isLastPage = state.page === state.pages
    
    // Calculate item range
    const startItem = state.total === 0 ? 0 : (state.page - 1) * state.limit + 1
    const endItem = Math.min(state.page * state.limit, state.total)
    
    // Calculate visible pages
    const visiblePages = calculateVisiblePages(state.page, state.pages, maxPagesShown)
    
    return {
      hasNextPage,
      hasPrevPage,
      isFirstPage,
      isLastPage,
      startItem,
      endItem,
      visiblePages
    }
  })

  // Computed display properties
  const pageInfo = computed(() => {
    if (state.total === 0) {
      return 'No items'
    }
    
    const { startItem, endItem } = meta.value
    return `${startItem}-${endItem} of ${state.total} items`
  })

  const pageInfoShort = computed(() => {
    return `${state.page} of ${state.pages}`
  })

  const progressPercentage = computed(() => {
    return state.pages > 0 ? Math.round((state.page / state.pages) * 100) : 0
  })

  // Utility function to calculate visible page numbers
  const calculateVisiblePages = (currentPage: number, totalPages: number, maxVisible: number): number[] => {
    if (totalPages <= maxVisible) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }

    const half = Math.floor(maxVisible / 2)
    let start = Math.max(1, currentPage - half)
    let end = Math.min(totalPages, start + maxVisible - 1)

    // Adjust if we're near the end
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1)
    }

    return Array.from({ length: end - start + 1 }, (_, i) => start + i)
  }

  // Core pagination functions
  const setPage = (page: number) => {
    if (page >= 1 && page <= state.pages) {
      state.page = page
      return true
    }
    return false
  }

  const setLimit = (limit: number) => {
    if (availableLimits.includes(limit)) {
      const oldOffset = (state.page - 1) * state.limit
      state.limit = limit
      
      // Maintain position in dataset when changing limit
      state.page = Math.floor(oldOffset / limit) + 1
      updatePagesCount()
      
      return true
    }
    return false
  }

  const setTotal = (total: number) => {
    state.total = Math.max(0, total)
    updatePagesCount()
    
    // Ensure current page is valid
    if (state.page > state.pages && state.pages > 0) {
      state.page = state.pages
    }
  }

  const updatePagesCount = () => {
    state.pages = state.total > 0 ? Math.ceil(state.total / state.limit) : 0
  }

  // Navigation functions
  const goToFirstPage = () => setPage(1)
  
  const goToLastPage = () => setPage(state.pages)
  
  const goToNextPage = () => setPage(state.page + 1)
  
  const goToPrevPage = () => setPage(state.page - 1)
  
  const goToPage = (page: number) => setPage(page)

  // Advanced navigation
  const jumpToPage = (page: number | string) => {
    const pageNum = typeof page === 'string' ? parseInt(page) : page
    return setPage(pageNum)
  }

  const jumpPages = (delta: number) => {
    return setPage(state.page + delta)
  }

  const goToOffset = (offset: number) => {
    const page = Math.floor(offset / state.limit) + 1
    return setPage(page)
  }

  // State management
  const reset = () => {
    state.page = defaultPage
    state.limit = defaultLimit
    state.total = 0
    state.pages = 0
  }

  const resetToFirstPage = () => {
    state.page = 1
  }

  const setState = (newState: Partial<PaginationState>) => {
    if (newState.total !== undefined) {
      setTotal(newState.total)
    }
    if (newState.limit !== undefined) {
      setLimit(newState.limit)
    }
    if (newState.page !== undefined) {
      setPage(newState.page)
    }
  }

  const getState = (): PaginationState => {
    return { ...state }
  }

  // URL state synchronization
  const getUrlParams = (): Record<string, string> => {
    const params: Record<string, string> = {}
    
    if (state.page > 1) {
      params.page = state.page.toString()
    }
    
    if (state.limit !== defaultLimit) {
      params.limit = state.limit.toString()
    }
    
    return params
  }

  const setFromUrlParams = (params: Record<string, string>) => {
    if (params.page) {
      const page = parseInt(params.page)
      if (page > 0) state.page = page
    }
    
    if (params.limit) {
      const limit = parseInt(params.limit)
      if (availableLimits.includes(limit)) {
        state.limit = limit
      }
    }
  }

  // Data slicing helpers
  const getSliceIndices = () => {
    const start = (state.page - 1) * state.limit
    const end = start + state.limit
    return { start, end }
  }

  const sliceData = <T>(data: T[]): T[] => {
    const { start, end } = getSliceIndices()
    return data.slice(start, end)
  }

  // Pagination controls generators
  const getPaginationControls = () => {
    const controls = []

    if (showFirstLast && !meta.value.isFirstPage) {
      controls.push({
        type: 'first',
        label: 'First',
        page: 1,
        disabled: false,
        active: false
      })
    }

    if (showPrevNext && meta.value.hasPrevPage) {
      controls.push({
        type: 'prev',
        label: 'Previous',
        page: state.page - 1,
        disabled: false,
        active: false
      })
    }

    // Add visible page numbers
    meta.value.visiblePages.forEach(page => {
      controls.push({
        type: 'page',
        label: page.toString(),
        page,
        disabled: false,
        active: page === state.page
      })
    })

    if (showPrevNext && meta.value.hasNextPage) {
      controls.push({
        type: 'next',
        label: 'Next',
        page: state.page + 1,
        disabled: false,
        active: false
      })
    }

    if (showFirstLast && !meta.value.isLastPage) {
      controls.push({
        type: 'last',
        label: 'Last',
        page: state.pages,
        disabled: false,
        active: false
      })
    }

    return controls
  }

  const getLimitOptions = () => {
    return availableLimits.map(limit => ({
      value: limit,
      label: `${limit} per page`,
      selected: limit === state.limit
    }))
  }

  // Event handlers for UI components
  const handlePageChange = (page: number) => {
    setPage(page)
  }

  const handleLimitChange = (limit: number) => {
    setLimit(limit)
  }

  const handleControlClick = (controlType: string, page?: number) => {
    switch (controlType) {
      case 'first':
        goToFirstPage()
        break
      case 'last':
        goToLastPage()
        break
      case 'prev':
        goToPrevPage()
        break
      case 'next':
        goToNextPage()
        break
      case 'page':
        if (page) setPage(page)
        break
    }
  }

  // Analytics and debugging
  const getAnalytics = () => {
    return {
      currentPage: state.page,
      totalPages: state.pages,
      itemsPerPage: state.limit,
      totalItems: state.total,
      progressPercentage: progressPercentage.value,
      itemsShown: meta.value.endItem - meta.value.startItem + 1,
      pagesShown: meta.value.visiblePages.length
    }
  }

  // Validation
  const isValidState = (): boolean => {
    return (
      state.page >= 1 &&
      state.page <= Math.max(1, state.pages) &&
      state.limit > 0 &&
      availableLimits.includes(state.limit) &&
      state.total >= 0
    )
  }

  // Watch for automatic updates
  watch(() => state.total, (newTotal) => {
    if (newTotal >= 0) {
      updatePagesCount()
    }
  })

  watch(() => state.limit, () => {
    updatePagesCount()
  })

  return {
    // State
    state: readonly(state),
    meta,

    // Display properties
    pageInfo,
    pageInfoShort,
    progressPercentage,

    // Core functions
    setPage,
    setLimit,
    setTotal,
    
    // Navigation
    goToFirstPage,
    goToLastPage,
    goToNextPage,
    goToPrevPage,
    goToPage,
    jumpToPage,
    jumpPages,
    goToOffset,

    // State management
    reset,
    resetToFirstPage,
    setState,
    getState,
    getUrlParams,
    setFromUrlParams,

    // Data helpers
    getSliceIndices,
    sliceData,

    // UI helpers
    getPaginationControls,
    getLimitOptions,
    handlePageChange,
    handleLimitChange,
    handleControlClick,

    // Utilities
    getAnalytics,
    isValidState,

    // Configuration
    config: readonly({
      defaultPage,
      defaultLimit,
      availableLimits,
      maxPagesShown,
      showFirstLast,
      showPrevNext,
      showPageInfo,
      showLimitSelector
    })
  }
}

// Helper function for creating pagination from API responses
export const createPaginationFromResponse = (
  response: any,
  paginationInstance: ReturnType<typeof usePagination>
) => {
  if (response.pagination) {
    const { page, limit, total, pages } = response.pagination
    paginationInstance.setState({ page, limit, total, pages })
  }
}

// Helper for common pagination patterns
export const useSimplePagination = (initialTotal = 0, initialLimit = 20) => {
  const pagination = usePagination({
    defaultLimit: initialLimit,
    showLimitSelector: false,
    maxPagesShown: 3
  })

  pagination.setTotal(initialTotal)

  return pagination
}

export const useAdvancedPagination = (config?: PaginationConfig) => {
  return usePagination({
    availableLimits: [10, 20, 50, 100, 200],
    maxPagesShown: 7,
    showFirstLast: true,
    showPrevNext: true,
    showPageInfo: true,
    showLimitSelector: true,
    ...config
  })
}

// Type exports
export type UsePagination = ReturnType<typeof usePagination>