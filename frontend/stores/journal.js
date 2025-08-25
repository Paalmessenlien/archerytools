import { defineStore } from 'pinia'
import { useAuth } from '../composables/useAuth'

export const useJournalStore = defineStore('journal', {
  state: () => ({
    entries: [],
    currentEntry: null,
    entryTypes: [],
    tags: [],
    loading: false,
    error: null
  }),

  getters: {
    allTags: (state) => {
      // Extract unique tags from all entries
      const tagSet = new Set()
      state.entries.forEach(entry => {
        if (entry.tags && Array.isArray(entry.tags)) {
          entry.tags.forEach(tag => tagSet.add(tag))
        }
      })
      return Array.from(tagSet).sort()
    }
  },

  actions: {
    async getEntries(params = {}) {
      const { token } = useAuth()
      const config = useRuntimeConfig()
      
      this.loading = true
      this.error = null

      try {
        const queryParams = new URLSearchParams()
        
        Object.entries(params).forEach(([key, value]) => {
          if (value !== null && value !== undefined && value !== '') {
            queryParams.append(key, value.toString())
          }
        })

        const response = await fetch(`${config.public.apiBase}/journal/entries?${queryParams.toString()}`, {
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        this.entries = data.entries || []
        
        return {
          entries: data.entries || [],
          pagination: data.pagination || { page: 1, limit: 20, total: 0, pages: 0 }
        }
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch journal entries:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async getEntry(entryId) {
      const { token } = useAuth()
      const config = useRuntimeConfig()

      try {
        const response = await fetch(`${config.public.apiBase}/journal/entries/${entryId}`, {
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        this.currentEntry = data.entry
        return data.entry
      } catch (error) {
        console.error('Failed to fetch journal entry:', error)
        throw error
      }
    },

    async createEntry(entryData) {
      const { token } = useAuth()
      const config = useRuntimeConfig()

      try {
        const response = await fetch(`${config.public.apiBase}/journal/entries`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(entryData)
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        return data
      } catch (error) {
        console.error('Failed to create journal entry:', error)
        throw error
      }
    },

    async updateEntry(entryId, entryData) {
      const { token } = useAuth()
      const config = useRuntimeConfig()

      try {
        const response = await fetch(`${config.public.apiBase}/journal/entries/${entryId}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(entryData)
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        
        // Update the current entry if it's the one being edited
        if (this.currentEntry && this.currentEntry.id === entryId) {
          this.currentEntry = { ...this.currentEntry, ...entryData }
        }

        return data
      } catch (error) {
        console.error('Failed to update journal entry:', error)
        throw error
      }
    },

    async deleteEntry(entryId) {
      const { token } = useAuth()
      const config = useRuntimeConfig()

      try {
        const response = await fetch(`${config.public.apiBase}/journal/entries/${entryId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }

        // Remove from local state
        this.entries = this.entries.filter(entry => entry.id !== entryId)
        
        if (this.currentEntry && this.currentEntry.id === entryId) {
          this.currentEntry = null
        }

        return await response.json()
      } catch (error) {
        console.error('Failed to delete journal entry:', error)
        throw error
      }
    },

    async searchEntries(searchQuery, params = {}) {
      const { token } = useAuth()
      const config = useRuntimeConfig()

      try {
        const queryParams = new URLSearchParams({
          q: searchQuery,
          ...params
        })

        const response = await fetch(`${config.public.apiBase}/journal/search?${queryParams.toString()}`, {
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        return data
      } catch (error) {
        console.error('Failed to search journal entries:', error)
        throw error
      }
    },

    async getEntryTypes() {
      const config = useRuntimeConfig()

      try {
        const response = await fetch(`${config.public.apiBase}/journal/entry-types`)

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        this.entryTypes = data.entry_types || []
        return data.entry_types || []
      } catch (error) {
        console.error('Failed to fetch entry types:', error)
        throw error
      }
    },

    async getTags() {
      const { token } = useAuth()
      const config = useRuntimeConfig()

      try {
        const response = await fetch(`${config.public.apiBase}/journal/tags`, {
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        this.tags = data.tags || []
        return data.tags || []
      } catch (error) {
        console.error('Failed to fetch tags:', error)
        throw error
      }
    },

    // Utility methods
    clearError() {
      this.error = null
    },

    clearCurrentEntry() {
      this.currentEntry = null
    }
  }
})