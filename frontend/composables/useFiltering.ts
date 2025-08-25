/**
 * Reusable Filtering and Search Utilities
 * Provides standardized filtering, searching, and data manipulation functions
 */

import { ref, computed, watch, reactive } from 'vue'
import { debounce } from '~/utils/debounce'

export interface FilterOption {
  value: string | number
  label: string
  count?: number
  disabled?: boolean
  group?: string
}

export interface FilterConfig {
  key: string
  label: string
  type: 'select' | 'multiselect' | 'text' | 'number' | 'date' | 'daterange' | 'boolean'
  options?: FilterOption[]
  placeholder?: string
  defaultValue?: any
  validation?: (value: any) => boolean
  transform?: (value: any) => any
}

export interface SortConfig {
  key: string
  label: string
  direction?: 'asc' | 'desc'
  type?: 'string' | 'number' | 'date'
  defaultDirection?: 'asc' | 'desc'
}

export interface SearchConfig {
  fields: string[]
  placeholder?: string
  minLength?: number
  debounceMs?: number
  caseSensitive?: boolean
  fuzzyMatch?: boolean
}

export interface FilterState {
  searchQuery: string
  filters: Record<string, any>
  sortBy: string
  sortDirection: 'asc' | 'desc'
  page: number
  limit: number
}

export const useFiltering = <T = any>(
  data: Ref<T[]> | (() => T[]),
  config: {
    search?: SearchConfig
    filters?: FilterConfig[]
    sorts?: SortConfig[]
    defaultState?: Partial<FilterState>
  } = {}
) => {
  // Configuration defaults
  const searchConfig = reactive({
    fields: config.search?.fields || [],
    placeholder: config.search?.placeholder || 'Search...',
    minLength: config.search?.minLength || 2,
    debounceMs: config.search?.debounceMs || 300,
    caseSensitive: config.search?.caseSensitive || false,
    fuzzyMatch: config.search?.fuzzyMatch || true,
    ...config.search
  })

  const filterConfigs = ref<FilterConfig[]>(config.filters || [])
  const sortConfigs = ref<SortConfig[]>(config.sorts || [])

  // Filter state
  const state = reactive<FilterState>({
    searchQuery: '',
    filters: {},
    sortBy: sortConfigs.value[0]?.key || '',
    sortDirection: sortConfigs.value[0]?.defaultDirection || 'asc',
    page: 1,
    limit: 20,
    ...config.defaultState
  })

  // Initialize default filter values
  filterConfigs.value.forEach(filter => {
    if (filter.defaultValue !== undefined) {
      state.filters[filter.key] = filter.defaultValue
    }
  })

  // Computed properties
  const rawData = computed(() => {
    return typeof data === 'function' ? data() : data.value
  })

  const searchableData = computed(() => {
    if (!state.searchQuery || state.searchQuery.length < searchConfig.minLength) {
      return rawData.value
    }

    const query = searchConfig.caseSensitive 
      ? state.searchQuery 
      : state.searchQuery.toLowerCase()

    return rawData.value.filter(item => {
      return searchConfig.fields.some(field => {
        const value = getNestedValue(item, field)
        if (value == null) return false

        const searchableValue = searchConfig.caseSensitive 
          ? String(value) 
          : String(value).toLowerCase()

        if (searchConfig.fuzzyMatch) {
          return searchableValue.includes(query)
        } else {
          return searchableValue === query
        }
      })
    })
  })

  const filteredData = computed(() => {
    return searchableData.value.filter(item => {
      return Object.entries(state.filters).every(([key, value]) => {
        if (value == null || value === '' || 
            (Array.isArray(value) && value.length === 0)) {
          return true
        }

        const filterConfig = filterConfigs.value.find(f => f.key === key)
        const itemValue = getNestedValue(item, key)

        if (filterConfig?.validation && !filterConfig.validation(value)) {
          return true
        }

        const transformedValue = filterConfig?.transform 
          ? filterConfig.transform(value) 
          : value

        return applyFilter(itemValue, transformedValue, filterConfig?.type || 'select')
      })
    })
  })

  const sortedData = computed(() => {
    if (!state.sortBy) return filteredData.value

    const sortConfig = sortConfigs.value.find(s => s.key === state.sortBy)
    const sortType = sortConfig?.type || 'string'

    return [...filteredData.value].sort((a, b) => {
      const aValue = getNestedValue(a, state.sortBy)
      const bValue = getNestedValue(b, state.sortBy)

      let comparison = 0

      switch (sortType) {
        case 'number':
          comparison = (Number(aValue) || 0) - (Number(bValue) || 0)
          break
        case 'date':
          comparison = new Date(aValue).getTime() - new Date(bValue).getTime()
          break
        case 'string':
        default:
          const aStr = String(aValue || '').toLowerCase()
          const bStr = String(bValue || '').toLowerCase()
          comparison = aStr.localeCompare(bStr)
          break
      }

      return state.sortDirection === 'desc' ? -comparison : comparison
    })
  })

  const paginatedData = computed(() => {
    const start = (state.page - 1) * state.limit
    const end = start + state.limit
    return sortedData.value.slice(start, end)
  })

  const totalItems = computed(() => sortedData.value.length)
  const totalPages = computed(() => Math.ceil(totalItems.value / state.limit))
  const hasNextPage = computed(() => state.page < totalPages.value)
  const hasPrevPage = computed(() => state.page > 1)

  // Utility functions
  const getNestedValue = (obj: any, path: string): any => {
    return path.split('.').reduce((current, key) => {
      return current && typeof current === 'object' ? current[key] : undefined
    }, obj)
  }

  const applyFilter = (itemValue: any, filterValue: any, filterType: string): boolean => {
    switch (filterType) {
      case 'multiselect':
        return Array.isArray(filterValue) 
          ? filterValue.includes(itemValue)
          : itemValue === filterValue

      case 'text':
        if (!filterValue) return true
        const searchText = String(filterValue).toLowerCase()
        const itemText = String(itemValue || '').toLowerCase()
        return itemText.includes(searchText)

      case 'number':
        return Number(itemValue) === Number(filterValue)

      case 'date':
        return new Date(itemValue).toDateString() === new Date(filterValue).toDateString()

      case 'daterange':
        if (!Array.isArray(filterValue) || filterValue.length !== 2) return true
        const itemDate = new Date(itemValue)
        const [startDate, endDate] = filterValue.map(d => new Date(d))
        return itemDate >= startDate && itemDate <= endDate

      case 'boolean':
        return Boolean(itemValue) === Boolean(filterValue)

      case 'select':
      default:
        return itemValue === filterValue
    }
  }

  // Search functions
  const debouncedSearch = debounce((query: string) => {
    state.searchQuery = query
    state.page = 1 // Reset to first page on search
  }, searchConfig.debounceMs)

  const setSearchQuery = (query: string) => {
    if (searchConfig.debounceMs > 0) {
      debouncedSearch(query)
    } else {
      state.searchQuery = query
      state.page = 1
    }
  }

  const clearSearch = () => {
    state.searchQuery = ''
    state.page = 1
  }

  // Filter functions
  const setFilter = (key: string, value: any) => {
    state.filters[key] = value
    state.page = 1 // Reset to first page on filter change
  }

  const clearFilter = (key: string) => {
    delete state.filters[key]
    state.page = 1
  }

  const clearAllFilters = () => {
    state.filters = {}
    state.page = 1
  }

  const toggleFilter = (key: string, value: any) => {
    const filterConfig = filterConfigs.value.find(f => f.key === key)
    
    if (filterConfig?.type === 'multiselect') {
      const currentValue = state.filters[key] || []
      if (Array.isArray(currentValue)) {
        const index = currentValue.indexOf(value)
        if (index > -1) {
          currentValue.splice(index, 1)
        } else {
          currentValue.push(value)
        }
        state.filters[key] = [...currentValue]
      } else {
        state.filters[key] = [value]
      }
    } else {
      state.filters[key] = state.filters[key] === value ? undefined : value
    }
    
    state.page = 1
  }

  // Sort functions
  const setSortBy = (key: string, direction?: 'asc' | 'desc') => {
    const sortConfig = sortConfigs.value.find(s => s.key === key)
    
    if (state.sortBy === key && !direction) {
      // Toggle direction if same key
      state.sortDirection = state.sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
      state.sortBy = key
      state.sortDirection = direction || sortConfig?.defaultDirection || 'asc'
    }
  }

  const clearSort = () => {
    state.sortBy = ''
    state.sortDirection = 'asc'
  }

  // Pagination functions
  const setPage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      state.page = page
    }
  }

  const nextPage = () => {
    if (hasNextPage.value) {
      state.page++
    }
  }

  const prevPage = () => {
    if (hasPrevPage.value) {
      state.page--
    }
  }

  const setLimit = (limit: number) => {
    state.limit = limit
    state.page = 1 // Reset to first page
  }

  // Advanced filtering
  const addDynamicFilter = (config: FilterConfig) => {
    filterConfigs.value.push(config)
    if (config.defaultValue !== undefined) {
      state.filters[config.key] = config.defaultValue
    }
  }

  const removeDynamicFilter = (key: string) => {
    filterConfigs.value = filterConfigs.value.filter(f => f.key !== key)
    delete state.filters[key]
  }

  const getFilterOptions = (key: string): FilterOption[] => {
    const filterConfig = filterConfigs.value.find(f => f.key === key)
    
    if (filterConfig?.options) {
      return filterConfig.options
    }

    // Auto-generate options from data
    const uniqueValues = new Set<any>()
    rawData.value.forEach(item => {
      const value = getNestedValue(item, key)
      if (value != null) {
        uniqueValues.add(value)
      }
    })

    return Array.from(uniqueValues)
      .sort()
      .map(value => ({
        value,
        label: String(value)
      }))
  }

  // State management
  const getFilterState = (): FilterState => {
    return { ...state }
  }

  const setFilterState = (newState: Partial<FilterState>) => {
    Object.assign(state, newState)
  }

  const resetToDefaults = () => {
    state.searchQuery = ''
    state.filters = {}
    state.sortBy = sortConfigs.value[0]?.key || ''
    state.sortDirection = sortConfigs.value[0]?.defaultDirection || 'asc'
    state.page = 1

    // Apply default filter values
    filterConfigs.value.forEach(filter => {
      if (filter.defaultValue !== undefined) {
        state.filters[filter.key] = filter.defaultValue
      }
    })
  }

  // URL state synchronization helpers
  const getUrlParams = (): Record<string, string> => {
    const params: Record<string, string> = {}
    
    if (state.searchQuery) params.search = state.searchQuery
    if (state.sortBy) params.sort = state.sortBy
    if (state.sortDirection !== 'asc') params.dir = state.sortDirection
    if (state.page > 1) params.page = state.page.toString()
    if (state.limit !== 20) params.limit = state.limit.toString()

    Object.entries(state.filters).forEach(([key, value]) => {
      if (value != null && value !== '') {
        params[key] = Array.isArray(value) ? value.join(',') : String(value)
      }
    })

    return params
  }

  const setFromUrlParams = (params: Record<string, string>) => {
    if (params.search) state.searchQuery = params.search
    if (params.sort) state.sortBy = params.sort
    if (params.dir) state.sortDirection = params.dir as 'asc' | 'desc'
    if (params.page) state.page = parseInt(params.page) || 1
    if (params.limit) state.limit = parseInt(params.limit) || 20

    // Parse filters
    filterConfigs.value.forEach(config => {
      if (params[config.key]) {
        const value = params[config.key]
        if (config.type === 'multiselect') {
          state.filters[config.key] = value.split(',')
        } else if (config.type === 'number') {
          state.filters[config.key] = parseFloat(value)
        } else if (config.type === 'boolean') {
          state.filters[config.key] = value === 'true'
        } else {
          state.filters[config.key] = value
        }
      }
    })
  }

  return {
    // Reactive state
    state: readonly(state),
    
    // Computed data
    rawData,
    searchableData,
    filteredData,
    sortedData,
    paginatedData,
    
    // Computed metadata
    totalItems,
    totalPages,
    hasNextPage,
    hasPrevPage,
    
    // Search functions
    setSearchQuery,
    clearSearch,
    
    // Filter functions
    setFilter,
    clearFilter,
    clearAllFilters,
    toggleFilter,
    getFilterOptions,
    addDynamicFilter,
    removeDynamicFilter,
    
    // Sort functions
    setSortBy,
    clearSort,
    
    // Pagination functions
    setPage,
    nextPage,
    prevPage,
    setLimit,
    
    // State management
    getFilterState,
    setFilterState,
    resetToDefaults,
    getUrlParams,
    setFromUrlParams,
    
    // Configuration
    searchConfig: readonly(searchConfig),
    filterConfigs: readonly(filterConfigs),
    sortConfigs: readonly(sortConfigs)
  }
}

// Utility functions for common filtering patterns
export const createTextFilter = (
  key: string, 
  label: string, 
  placeholder?: string
): FilterConfig => ({
  key,
  label,
  type: 'text',
  placeholder: placeholder || `Filter by ${label.toLowerCase()}...`
})

export const createSelectFilter = (
  key: string,
  label: string,
  options: FilterOption[],
  defaultValue?: any
): FilterConfig => ({
  key,
  label,
  type: 'select',
  options,
  defaultValue
})

export const createMultiSelectFilter = (
  key: string,
  label: string,
  options: FilterOption[],
  defaultValue?: any[]
): FilterConfig => ({
  key,
  label,
  type: 'multiselect',
  options,
  defaultValue: defaultValue || []
})

export const createDateRangeFilter = (
  key: string,
  label: string
): FilterConfig => ({
  key,
  label,
  type: 'daterange'
})

export const createNumberFilter = (
  key: string,
  label: string,
  placeholder?: string
): FilterConfig => ({
  key,
  label,
  type: 'number',
  placeholder: placeholder || `Enter ${label.toLowerCase()}...`,
  validation: (value) => !isNaN(Number(value)),
  transform: (value) => Number(value)
})

export type UseFiltering = ReturnType<typeof useFiltering>