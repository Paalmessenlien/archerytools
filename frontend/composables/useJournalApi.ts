/**
 * Reusable Journal API Composable
 * Provides standardized journal operations that can be used across the system
 */

import { ref, computed } from 'vue'
import { useAuth } from './useAuth'
import { useApi } from './useApi'

export interface JournalEntry {
  id: number
  title: string
  content: string
  entry_type: string
  bow_setup_id?: number
  bow_setup_name?: string
  tags: string[]
  is_private: boolean
  created_at: string
  updated_at: string
  user_id: number
}

export interface JournalEntryCreate {
  title: string
  content: string
  entry_type: string
  bow_setup_id?: number
  tags?: string[]
  is_private?: boolean
  // Session-specific fields for tuning sessions
  session_metadata?: any  // JSON object with session details
  session_data?: any      // Alternative field name for session metadata
  session_type?: string   // Type of session (bareshaft, paper, walkback, etc.)
  session_quality_score?: number  // Quality score 0-100
  linked_arrow?: number   // Arrow ID for linking
}

export interface JournalEntryUpdate {
  title?: string
  content?: string
  entry_type?: string
  bow_setup_id?: number
  tags?: string[]
  is_private?: boolean
}

export interface JournalSearchParams {
  page?: number
  limit?: number
  search?: string
  bow_setup_id?: number
  entry_type?: string
  tags?: string
  start_date?: string
  end_date?: string
}

export interface JournalApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

export interface EntryType {
  value: string
  label: string
  description?: string
  icon?: string
}

export const useJournalApi = () => {
  const { isLoggedIn } = useAuth()
  const api = useApi()

  // Reactive state
  const loading = ref(false)
  const error = ref<string | null>(null)
  const entries = ref<JournalEntry[]>([])
  const currentEntry = ref<JournalEntry | null>(null)
  
  // Default entry types - can be extended
  const defaultEntryTypes = ref<EntryType[]>([
    { value: 'general', label: 'General Entry', icon: 'fas fa-book' },
    { value: 'setup_change', label: 'Setup Change', icon: 'fas fa-crosshairs' },
    { value: 'equipment_change', label: 'Equipment Change', icon: 'fas fa-tools' },
    { value: 'arrow_change', label: 'Arrow Change', icon: 'fas fa-bullseye' },
    { value: 'tuning_session', label: 'Tuning Session', icon: 'fas fa-adjust' },
    { value: 'shooting_notes', label: 'Shooting Notes', icon: 'fas fa-target' },
    { value: 'maintenance', label: 'Maintenance', icon: 'fas fa-wrench' },
    { value: 'upgrade', label: 'Upgrade', icon: 'fas fa-arrow-up' }
  ])

  // Computed properties
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)
  const entryCount = computed(() => entries.value.length)
  const uniqueTags = computed(() => {
    const tagSet = new Set<string>()
    entries.value.forEach(entry => {
      entry.tags?.forEach(tag => tagSet.add(tag.trim()))
    })
    return Array.from(tagSet).sort()
  })

  // Utility functions
  const clearError = () => {
    error.value = null
  }

  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const handleError = (err: any, context = 'Journal operation') => {
    const message = err?.message || err?.toString() || 'Unknown error occurred'
    error.value = `${context}: ${message}`
    console.error(`${context}:`, err)
    return message
  }

  // Core API functions
  const getEntries = async (params: JournalSearchParams = {}): Promise<JournalApiResponse<JournalEntry[]>> => {
    if (!isLoggedIn.value) {
      return { success: false, error: 'Authentication required' }
    }

    setLoading(true)
    clearError()

    try {
      const queryParams = new URLSearchParams()
      
      // Add valid parameters to query
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, value.toString())
        }
      })

      const response = await api.get(`/journal/entries?${queryParams.toString()}`)
      
      if (response.entries) {
        entries.value = response.entries
      }

      return {
        success: true,
        data: response.entries || [],
        pagination: response.pagination
      }
    } catch (err) {
      const errorMessage = handleError(err, 'Failed to fetch journal entries')
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const getEntry = async (entryId: number): Promise<JournalApiResponse<JournalEntry>> => {
    if (!isLoggedIn.value) {
      return { success: false, error: 'Authentication required' }
    }

    setLoading(true)
    clearError()

    try {
      const response = await api.get(`/journal/entries/${entryId}`)
      
      if (response.entry) {
        currentEntry.value = response.entry
      }

      return {
        success: true,
        data: response.entry
      }
    } catch (err) {
      const errorMessage = handleError(err, 'Failed to fetch journal entry')
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const createEntry = async (entryData: JournalEntryCreate): Promise<JournalApiResponse<JournalEntry>> => {
    if (!isLoggedIn.value) {
      return { success: false, error: 'Authentication required' }
    }

    setLoading(true)
    clearError()

    try {
      // Validate required fields
      if (!entryData.title?.trim()) {
        throw new Error('Entry title is required')
      }
      if (!entryData.content?.trim()) {
        throw new Error('Entry content is required')
      }

      const response = await api.post('/journal/entries', entryData)
      
      // Add to local state if successful
      if (response.entry) {
        entries.value.unshift(response.entry)
      }

      return {
        success: true,
        data: response.entry
      }
    } catch (err) {
      const errorMessage = handleError(err, 'Failed to create journal entry')
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const updateEntry = async (entryId: number, entryData: JournalEntryUpdate): Promise<JournalApiResponse<JournalEntry>> => {
    if (!isLoggedIn.value) {
      return { success: false, error: 'Authentication required' }
    }

    setLoading(true)
    clearError()

    try {
      const response = await api.put(`/journal/entries/${entryId}`, entryData)
      
      // Update local state
      if (response.entry) {
        const index = entries.value.findIndex(entry => entry.id === entryId)
        if (index !== -1) {
          entries.value[index] = { ...entries.value[index], ...response.entry }
        }
        
        if (currentEntry.value?.id === entryId) {
          currentEntry.value = { ...currentEntry.value, ...response.entry }
        }
      }

      return {
        success: true,
        data: response.entry
      }
    } catch (err) {
      const errorMessage = handleError(err, 'Failed to update journal entry')
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const deleteEntry = async (entryId: number): Promise<JournalApiResponse<void>> => {
    if (!isLoggedIn.value) {
      return { success: false, error: 'Authentication required' }
    }

    setLoading(true)
    clearError()

    try {
      await api.delete(`/journal/entries/${entryId}`)
      
      // Remove from local state
      entries.value = entries.value.filter(entry => entry.id !== entryId)
      
      if (currentEntry.value?.id === entryId) {
        currentEntry.value = null
      }

      return { success: true }
    } catch (err) {
      const errorMessage = handleError(err, 'Failed to delete journal entry')
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const searchEntries = async (query: string, params: JournalSearchParams = {}): Promise<JournalApiResponse<JournalEntry[]>> => {
    if (!isLoggedIn.value) {
      return { success: false, error: 'Authentication required' }
    }

    setLoading(true)
    clearError()

    try {
      const searchParams = {
        search: query,
        ...params
      }

      return await getEntries(searchParams)
    } catch (err) {
      const errorMessage = handleError(err, 'Failed to search journal entries')
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const getEntryTypes = async (): Promise<JournalApiResponse<EntryType[]>> => {
    setLoading(true)
    clearError()

    try {
      // Try to fetch from API first
      try {
        const response = await api.get('/journal/entry-types')
        if (response.entry_types && Array.isArray(response.entry_types)) {
          return {
            success: true,
            data: response.entry_types
          }
        }
      } catch (apiError) {
        console.log('API entry types not available, using defaults')
      }

      // Fallback to default entry types
      return {
        success: true,
        data: defaultEntryTypes.value
      }
    } catch (err) {
      const errorMessage = handleError(err, 'Failed to fetch entry types')
      return { 
        success: false, 
        error: errorMessage,
        data: defaultEntryTypes.value // Still provide defaults on error
      }
    } finally {
      setLoading(false)
    }
  }

  const getTags = async (): Promise<JournalApiResponse<string[]>> => {
    if (!isLoggedIn.value) {
      return { success: false, error: 'Authentication required' }
    }

    setLoading(true)
    clearError()

    try {
      const response = await api.get('/journal/tags')
      
      return {
        success: true,
        data: response.tags || []
      }
    } catch (err) {
      const errorMessage = handleError(err, 'Failed to fetch tags')
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  // Utility methods for entry management
  const formatEntryDate = (dateString: string, options?: Intl.DateTimeFormatOptions) => {
    const defaultOptions: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }
    
    try {
      return new Date(dateString).toLocaleDateString('en-US', options || defaultOptions)
    } catch {
      return dateString
    }
  }

  const getEntryTypeInfo = (entryType: string): EntryType | undefined => {
    return defaultEntryTypes.value.find(type => type.value === entryType)
  }

  const parseTags = (tagString: string): string[] => {
    if (!tagString) return []
    return tagString
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0)
  }

  const formatTags = (tags: string[]): string => {
    return tags.join(', ')
  }

  // Export all functions and state
  return {
    // State
    loading: readonly(loading),
    error: readonly(error),
    entries: readonly(entries),
    currentEntry: readonly(currentEntry),
    
    // Computed
    isLoading,
    hasError,
    entryCount,
    uniqueTags,
    
    // Core API functions
    getEntries,
    getEntry,
    createEntry,
    updateEntry,
    deleteEntry,
    searchEntries,
    getEntryTypes,
    getTags,
    
    // Utility functions
    clearError,
    formatEntryDate,
    getEntryTypeInfo,
    parseTags,
    formatTags,
    
    // Constants
    defaultEntryTypes: readonly(defaultEntryTypes)
  }
}

// Type exports for use in other modules
export type UseJournalApi = ReturnType<typeof useJournalApi>