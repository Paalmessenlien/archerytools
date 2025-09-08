<template>
  <div class="journal-entry-page">
    <!-- Loading State -->
    <div v-if="pending" class="loading-container">
      <md-circular-progress indeterminate></md-circular-progress>
      <p>Loading journal entry...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <md-icon class="error-icon">error</md-icon>
      <h2>Failed to Load Entry</h2>
      <p>{{ error.message }}</p>
      <md-filled-button @click="goBack">
        <md-icon slot="icon">arrow_back</md-icon>
        Go Back
      </md-filled-button>
      <md-outlined-button @click="loadEntry">
        <md-icon slot="icon">refresh</md-icon>
        Retry
      </md-outlined-button>
    </div>

    <!-- Journal Entry Content -->
    <div v-else-if="entry" class="entry-container">
      <!-- Enhanced Entry Display with Integrated Header -->
      <JournalEntryDetailViewer
        :entry="entry"
        :show="true"
        :is-full-page="true"
        @close="goBack"
        @edit="editEntry"
        @delete="deleteEntry"
        @toggle-favorite="toggleFavorite"
        @view-session="handleViewSession"
        @start-similar="handleStartSimilar"
      />
    </div>

    <!-- Delete Confirmation Dialog -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold mb-4">Delete Journal Entry</h3>
        <p class="mb-6">Are you sure you want to delete "{{ entry?.title }}"? This action cannot be undone.</p>
        <div class="flex gap-3 justify-end">
          <md-outlined-button @click="showDeleteConfirm = false">Cancel</md-outlined-button>
          <md-filled-button @click="confirmDelete" class="bg-red-600">Delete</md-filled-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
console.log('🔍🔍🔍 JOURNAL DETAIL PAGE SCRIPT IS LOADING!!! 🔍🔍🔍')
console.log('🔍 Current URL:', window?.location?.href || 'SSR')
import { ref, computed, onMounted, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '~/composables/useAuth'
import { useApi } from '~/composables/useApi'
import JournalEntryDetailViewer from '~/components/journal/JournalEntryDetailViewer.vue'

// Set page meta
definePageMeta({
  title: 'Journal Entry',
  middleware: ['auth-check']
})

// Composables
console.log('🔍 Setting up composables...')
const route = useRoute()
const router = useRouter()
const { token } = useAuth()
const { get, delete: apiDelete } = useApi()
console.log('🔍 Composables set up, route params:', route.params)

// Reactive state
const entry = ref(null)
const pending = ref(true)
const error = ref(null)
const showDeleteConfirm = ref(false)

// Get entry ID from route
const entryId = computed(() => route.params.id)

// Load entry data
const loadEntry = async () => {
  console.log('loadEntry called with entryId:', entryId.value)
  
  if (!entryId.value) {
    console.error('No entry ID provided')
    error.value = { message: 'Invalid entry ID' }
    pending.value = false
    return
  }

  try {
    pending.value = true
    error.value = null
    
    console.log('Fetching journal entry from API:', `/journal/entries/${entryId.value}`)
    const response = await get(`/journal/entries/${entryId.value}`)
    console.log('API response:', response)
    
    if (response.entry) {
      entry.value = response.entry
      console.log('Entry loaded successfully:', entry.value.title)
    } else {
      console.error('API returned error:', response.error)
      error.value = { message: response.error || 'Failed to load entry' }
    }
  } catch (err) {
    console.error('Error loading journal entry:', err)
    error.value = { message: 'Failed to load journal entry' }
  } finally {
    pending.value = false
    console.log('loadEntry completed, pending:', pending.value, 'error:', error.value)
  }
}

// Navigation methods
const goBack = () => {
  router.push('/journal')
}

const editEntry = () => {
  // Navigate to edit mode (you might want to pass entry data)
  router.push(`/journal?edit=${entryId.value}`)
}

// Action methods
const shareEntry = () => {
  if (navigator.share) {
    navigator.share({
      title: entry.value.title,
      text: `Check out this journal entry: ${entry.value.title}`,
      url: window.location.href
    })
  } else {
    // Fallback - copy to clipboard
    navigator.clipboard.writeText(window.location.href)
    // You might want to show a toast notification here
  }
}

const deleteEntry = () => {
  showDeleteConfirm.value = true
}

const confirmDelete = async () => {
  try {
    await apiDelete(`/journal/entries/${entryId.value}`)
    showDeleteConfirm.value = false
    router.push('/journal')
  } catch (err) {
    console.error('Failed to delete entry:', err)
    // Show error notification
  }
}

// Enhanced viewer methods
const toggleFavorite = () => {
  // TODO: Implement favorite toggle functionality
  console.log('Toggle favorite for entry:', entry.value?.id)
}

const handleViewSession = (sessionInfo) => {
  // Navigate to the original tuning session if it exists
  if (sessionInfo?.sessionId && sessionInfo?.tuningType) {
    router.push(`/tuning-session/${sessionInfo.tuningType}/${sessionInfo.sessionId}`)
  }
}

const handleStartSimilar = (sessionInfo) => {
  // Navigate to start a new similar session
  if (sessionInfo?.sessionData?.tuning_type) {
    router.push(`/calculator?tuning_type=${sessionInfo.sessionData.tuning_type}`)
  }
}

// Utility methods
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getEntryTypeIcon = (type) => {
  const icons = {
    general: 'fas fa-sticky-note',
    setup_change: 'fas fa-tools',
    equipment_change: 'fas fa-exchange-alt',
    arrow_change: 'fas fa-arrow-right',
    tuning_session: 'fas fa-crosshairs',
    shooting_notes: 'fas fa-target',
    maintenance: 'fas fa-wrench',
    upgrade: 'fas fa-arrow-up'
  }
  return icons[type] || 'fas fa-sticky-note'
}

const getEntryTypeLabel = (type) => {
  const labels = {
    general: 'General Entry',
    setup_change: 'Setup Change',
    equipment_change: 'Equipment Change',
    arrow_change: 'Arrow Change',
    tuning_session: 'Tuning Session',
    shooting_notes: 'Shooting Notes',
    maintenance: 'Maintenance',
    upgrade: 'Upgrade'
  }
  return labels[type] || 'Journal Entry'
}

// Load entry on mount
onMounted(async () => {
  console.log('Journal detail page mounting, entry ID:', entryId.value)
  await loadEntry()
  console.log('Journal detail page loaded, entry:', entry.value?.id)
})

// Set page title dynamically
watchEffect(() => {
  if (entry.value?.title) {
    useHead({
      title: `${entry.value.title} - Journal`
    })
  }
})
</script>

<style scoped>
.journal-entry-page {
  min-height: 100vh;
  background: var(--md-sys-color-surface-container-lowest);
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
  text-align: center;
  padding: 2rem;
}

.error-icon {
  font-size: 3rem;
  color: var(--md-sys-color-error);
  margin-bottom: 1rem;
}

.entry-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.entry-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding-bottom: 1rem;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.entry-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.entry-type-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.type-tuning_session { 
  background: var(--md-sys-color-error-container); 
  color: var(--md-sys-color-on-error-container); 
}

.type-equipment_change { 
  background: var(--md-sys-color-tertiary-container); 
  color: var(--md-sys-color-on-tertiary-container); 
}

.type-shooting_notes { 
  background: var(--md-sys-color-primary-container); 
  color: var(--md-sys-color-on-primary-container); 
}

.entry-dates {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.date-item {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
}

.enhanced-entry-content {
  /* Ensure the enhanced viewer displays properly in full-page mode */
}

.full-page-viewer {
  /* Remove modal styles when in full-page mode */
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .entry-container {
    padding: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .entry-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>