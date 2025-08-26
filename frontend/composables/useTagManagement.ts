/**
 * Universal Tag Management Composable
 * Reusable across the entire system for journal, equipment, setup, and arrow tags
 */

import { ref, reactive, computed, watch } from 'vue'
import { useApi } from './useApi'
import { useGlobalNotifications } from './useNotificationSystem'

export interface TagConfig {
  entityType: 'journal' | 'equipment' | 'setup' | 'arrow' | 'profile'
  entityId?: number
  maxTags?: number
  allowCustom?: boolean
  apiEndpoint?: string
  minQueryLength?: number
  debounceMs?: number
}

export interface Tag {
  id?: number
  name: string
  usage_count?: number
  created_at?: string
  color?: string
  category?: string
  is_custom?: boolean
}

export interface TagSuggestion {
  name: string
  usage_count: number
  confidence: number
  source: 'popular' | 'related' | 'history' | 'ai'
}

export interface TagValidationResult {
  valid: boolean
  error?: string
  suggestions?: string[]
}

export interface TagState {
  tags: Tag[]
  suggestions: TagSuggestion[]
  isLoading: boolean
  isSearching: boolean
  error: string | null
  query: string
  selectedTags: Tag[]
}

const defaultConfig: Partial<TagConfig> = {
  maxTags: 20,
  allowCustom: true,
  minQueryLength: 2,
  debounceMs: 300
}

export const useTagManagement = (config: TagConfig) => {
  const api = useApi()
  const notifications = useGlobalNotifications()
  
  const mergedConfig = { ...defaultConfig, ...config }
  const apiEndpoint = config.apiEndpoint || `/api/${config.entityType}/tags`

  const state = reactive<TagState>({
    tags: [],
    suggestions: [],
    isLoading: false,
    isSearching: false,
    error: null,
    query: '',
    selectedTags: []
  })

  // Computed properties
  const canAddMore = computed(() => {
    return state.selectedTags.length < (mergedConfig.maxTags || 20)
  })

  const hasReachedLimit = computed(() => {
    return state.selectedTags.length >= (mergedConfig.maxTags || 20)
  })

  const popularTags = computed(() => 
    state.suggestions.filter(s => s.source === 'popular').slice(0, 10)
  )

  const relatedTags = computed(() => 
    state.suggestions.filter(s => s.source === 'related').slice(0, 5)
  )

  const uniqueSelectedTags = computed(() => {
    const seen = new Set()
    return state.selectedTags.filter(tag => {
      const key = tag.name.toLowerCase()
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  })

  // Validation functions
  const validateTag = (tagName: string): TagValidationResult => {
    const name = tagName.trim()
    
    if (!name) {
      return { valid: false, error: 'Tag name cannot be empty' }
    }

    if (name.length < 2) {
      return { valid: false, error: 'Tag must be at least 2 characters long' }
    }

    if (name.length > 50) {
      return { valid: false, error: 'Tag cannot exceed 50 characters' }
    }

    // Check for special characters (allow letters, numbers, hyphens, underscores, spaces)
    if (!/^[a-zA-Z0-9\s\-_]+$/.test(name)) {
      return { 
        valid: false, 
        error: 'Tag can only contain letters, numbers, spaces, hyphens, and underscores' 
      }
    }

    // Check if already selected
    const isAlreadySelected = state.selectedTags.some(
      tag => tag.name.toLowerCase() === name.toLowerCase()
    )
    if (isAlreadySelected) {
      return { valid: false, error: 'Tag already added' }
    }

    // Check if at limit
    if (hasReachedLimit.value) {
      return { 
        valid: false, 
        error: `Cannot add more than ${mergedConfig.maxTags} tags` 
      }
    }

    return { valid: true }
  }

  const normalizeTag = (tagName: string): string => {
    return tagName.trim().toLowerCase().replace(/\s+/g, ' ')
  }

  // Core tag operations
  const addTag = async (tagName: string, options: { silent?: boolean } = {}): Promise<boolean> => {
    const validation = validateTag(tagName)
    if (!validation.valid) {
      if (!options.silent) {
        notifications.showError(validation.error || 'Invalid tag')
      }
      return false
    }

    const normalizedName = normalizeTag(tagName)
    const tag: Tag = {
      name: tagName.trim(),
      is_custom: !state.suggestions.some(s => s.name.toLowerCase() === normalizedName),
      created_at: new Date().toISOString()
    }

    try {
      // If we have an entityId, save to backend immediately
      if (mergedConfig.entityId) {
        const response = await api.post<{ success: boolean; tag?: Tag; error?: string }>(
          `${apiEndpoint}/${mergedConfig.entityId}`,
          { tag_name: tag.name }
        )

        if (response.success && response.tag) {
          tag.id = response.tag.id
          tag.usage_count = response.tag.usage_count
        } else {
          throw new Error(response.error || 'Failed to save tag')
        }
      }

      // Add to selected tags
      state.selectedTags.push(tag)

      if (!options.silent) {
        notifications.showSuccess(`Tag "${tagName}" added`)
      }

      // Clear search query
      state.query = ''

      return true
    } catch (error) {
      console.error('Error adding tag:', error)
      if (!options.silent) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to add tag'
        notifications.showError(errorMessage)
      }
      return false
    }
  }

  const removeTag = async (tagName: string): Promise<boolean> => {
    const index = state.selectedTags.findIndex(
      tag => tag.name.toLowerCase() === tagName.toLowerCase()
    )
    
    if (index === -1) return false

    const tag = state.selectedTags[index]

    try {
      // If we have an entityId and tag has an ID, remove from backend
      if (mergedConfig.entityId && tag.id) {
        const response = await api.delete<{ success: boolean; error?: string }>(
          `${apiEndpoint}/${mergedConfig.entityId}/${tag.id}`
        )

        if (!response.success) {
          throw new Error(response.error || 'Failed to remove tag')
        }
      }

      // Remove from selected tags
      state.selectedTags.splice(index, 1)
      notifications.showInfo(`Tag "${tagName}" removed`)

      return true
    } catch (error) {
      console.error('Error removing tag:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to remove tag'
      notifications.showError(errorMessage)
      return false
    }
  }

  const clearAllTags = (): void => {
    state.selectedTags = []
    notifications.showInfo('All tags cleared')
  }

  // Search and suggestions
  const searchTags = async (query: string): Promise<void> => {
    if (!query || query.length < (mergedConfig.minQueryLength || 2)) {
      state.suggestions = []
      return
    }

    state.isSearching = true
    
    try {
      const response = await api.get<{
        success: boolean
        suggestions?: TagSuggestion[]
        popular?: TagSuggestion[]
        error?: string
      }>(`${apiEndpoint}/search`, {
        q: query,
        entity_type: mergedConfig.entityType,
        entity_id: mergedConfig.entityId,
        limit: 20
      })

      if (response.success) {
        state.suggestions = [
          ...(response.suggestions || []),
          ...(response.popular || [])
        ].sort((a, b) => b.confidence - a.confidence || b.usage_count - a.usage_count)
      } else {
        throw new Error(response.error || 'Search failed')
      }

    } catch (error) {
      console.error('Error searching tags:', error)
      // Don't show error notification for search failures - just log them
      state.suggestions = []
    } finally {
      state.isSearching = false
    }
  }

  const loadPopularTags = async (): Promise<void> => {
    try {
      const response = await api.get<{
        success: boolean
        popular?: TagSuggestion[]
        error?: string
      }>(`${apiEndpoint}/popular`, {
        entity_type: mergedConfig.entityType,
        limit: 15
      })

      if (response.success && response.popular) {
        const popularSuggestions = response.popular.map(tag => ({
          ...tag,
          source: 'popular' as const
        }))
        
        // Add popular tags to suggestions if not already there
        const existingNames = new Set(state.suggestions.map(s => s.name.toLowerCase()))
        const newSuggestions = popularSuggestions.filter(
          tag => !existingNames.has(tag.name.toLowerCase())
        )
        
        state.suggestions = [...state.suggestions, ...newSuggestions]
      }

    } catch (error) {
      console.error('Error loading popular tags:', error)
      // Don't show error for popular tags loading failure
    }
  }

  const loadExistingTags = async (): Promise<void> => {
    if (!mergedConfig.entityId) return

    state.isLoading = true
    
    try {
      const response = await api.get<{
        success: boolean
        tags?: Tag[]
        error?: string
      }>(`${apiEndpoint}/${mergedConfig.entityId}`)

      if (response.success && response.tags) {
        state.selectedTags = response.tags
      } else {
        throw new Error(response.error || 'Failed to load existing tags')
      }

    } catch (error) {
      console.error('Error loading existing tags:', error)
      state.error = error instanceof Error ? error.message : 'Failed to load tags'
    } finally {
      state.isLoading = false
    }
  }

  // Utility functions
  const getTagsForSubmission = (): string[] => {
    return uniqueSelectedTags.value.map(tag => tag.name)
  }

  const initializeTags = (existingTags: string[] | Tag[]): void => {
    if (!existingTags?.length) return

    state.selectedTags = existingTags.map(tag => {
      if (typeof tag === 'string') {
        return {
          name: tag,
          created_at: new Date().toISOString()
        }
      }
      return tag
    })
  }

  const exportTags = (): { 
    selected: Tag[], 
    popular: TagSuggestion[], 
    totalSelected: number 
  } => {
    return {
      selected: uniqueSelectedTags.value,
      popular: popularTags.value,
      totalSelected: uniqueSelectedTags.value.length
    }
  }

  // Batch operations
  const addMultipleTags = async (tagNames: string[]): Promise<{ added: number; failed: string[] }> => {
    const results = { added: 0, failed: [] as string[] }
    
    for (const tagName of tagNames) {
      const success = await addTag(tagName, { silent: true })
      if (success) {
        results.added++
      } else {
        results.failed.push(tagName)
      }
    }

    if (results.added > 0) {
      notifications.showSuccess(`Added ${results.added} tag${results.added > 1 ? 's' : ''}`)
    }

    if (results.failed.length > 0) {
      notifications.showWarning(`Failed to add: ${results.failed.join(', ')}`)
    }

    return results
  }

  // Debounced search
  let searchTimeout: NodeJS.Timeout
  const debouncedSearch = (query: string): void => {
    clearTimeout(searchTimeout)
    state.query = query
    
    if (query.length >= (mergedConfig.minQueryLength || 2)) {
      searchTimeout = setTimeout(() => {
        searchTags(query)
      }, mergedConfig.debounceMs || 300)
    } else {
      state.suggestions = []
    }
  }

  // Watchers
  watch(() => mergedConfig.entityId, (newEntityId) => {
    if (newEntityId) {
      loadExistingTags()
    }
  }, { immediate: true })

  return {
    // State
    state: readonly(state),
    
    // Computed
    canAddMore,
    hasReachedLimit,
    popularTags,
    relatedTags,
    uniqueSelectedTags,
    
    // Core operations
    addTag,
    removeTag,
    clearAllTags,
    addMultipleTags,
    
    // Search and suggestions
    searchTags,
    debouncedSearch,
    loadPopularTags,
    
    // Data management
    loadExistingTags,
    initializeTags,
    getTagsForSubmission,
    exportTags,
    
    // Validation
    validateTag,
    normalizeTag
  }
}