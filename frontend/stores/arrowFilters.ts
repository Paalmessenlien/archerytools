import { defineStore } from 'pinia'

interface ArrowFilters {
  search: string
  manufacturer: string
  match_quality: string
  weight_min: string
  weight_max: string
  diameter_range: string
  diameter_min: string
  diameter_max: string
  wood_species: string
  sortBy: string
}

export const useArrowFiltersStore = defineStore('arrowFilters', () => {
  // State
  const filters = ref<ArrowFilters>({
    search: '',
    manufacturer: '',
    match_quality: '',
    weight_min: '',
    weight_max: '',
    diameter_range: '',
    diameter_min: '',
    diameter_max: '',
    wood_species: '',
    sortBy: 'compatibility'
  })

  const showAdvancedFilters = ref(false)

  // Actions
  const updateFilter = <K extends keyof ArrowFilters>(key: K, value: ArrowFilters[K]) => {
    filters.value[key] = value
    // Persist to localStorage
    if (process.client) {
      localStorage.setItem('arrowFilters', JSON.stringify(filters.value))
    }
  }

  const updateAllFilters = (newFilters: Partial<ArrowFilters>) => {
    filters.value = { ...filters.value, ...newFilters }
    // Persist to localStorage
    if (process.client) {
      localStorage.setItem('arrowFilters', JSON.stringify(filters.value))
    }
  }

  const clearFilters = () => {
    filters.value = {
      search: '',
      manufacturer: '',
      match_quality: '',
      weight_min: '',
      weight_max: '',
      diameter_range: '',
      diameter_min: '',
      diameter_max: '',
      wood_species: '',
      sortBy: 'compatibility'
    }
    // Clear from localStorage
    if (process.client) {
      localStorage.removeItem('arrowFilters')
    }
  }

  const toggleAdvancedFilters = () => {
    showAdvancedFilters.value = !showAdvancedFilters.value
  }

  const openAdvancedFilters = () => {
    showAdvancedFilters.value = true
  }

  const closeAdvancedFilters = () => {
    showAdvancedFilters.value = false
  }

  // Initialize from localStorage
  const initializeFilters = () => {
    if (process.client) {
      const saved = localStorage.getItem('arrowFilters')
      if (saved) {
        try {
          const parsed = JSON.parse(saved)
          filters.value = { ...filters.value, ...parsed }
        } catch (e) {
          console.error('Error parsing saved arrow filters:', e)
        }
      }
    }
  }

  // Initialize on mount
  onMounted(() => {
    initializeFilters()
  })

  return {
    // State
    filters: readonly(filters),
    showAdvancedFilters: readonly(showAdvancedFilters),

    // Actions
    updateFilter,
    updateAllFilters,
    clearFilters,
    toggleAdvancedFilters,
    openAdvancedFilters,
    closeAdvancedFilters,
    initializeFilters
  }
})