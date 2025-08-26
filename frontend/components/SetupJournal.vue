<template>
  <div class="setup-journal">
    <!-- Journal Header with Quick Actions -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 flex items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex-shrink-0">
          <i class="fas fa-journal-whills text-indigo-600 dark:text-indigo-400 text-lg"></i>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Journal & History</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">Track your setup changes and shooting notes</p>
        </div>
      </div>
      
      <div class="flex gap-2">
        <CustomButton
          @click="showQuickEntryForm = !showQuickEntryForm"
          variant="primary"
          class="flex-shrink-0"
        >
          <i class="fas fa-plus mr-2"></i>
          Quick Entry
        </CustomButton>
        
        <CustomButton
          @click="refreshTimeline"
          variant="outlined"
          :disabled="loading"
        >
          <i :class="['fas fa-sync-alt', loading ? 'animate-spin' : '']"></i>
        </CustomButton>
      </div>
    </div>

    <!-- Quick Entry Form (Collapsible) -->
    <div v-if="showQuickEntryForm" class="mb-6">
      <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-200 dark:border-indigo-800 p-1">
        <JournalEntryForm
          mode="inline"
          :entry="null"
          :bow-setups="[bowSetup]"
          :entry-types="entryTypes"
          @save="handleQuickEntrySave"
          @cancel="showQuickEntryForm = false"
          @auto-save="handleAutoSave"
        />
      </div>
    </div>

    <!-- Timeline View Toggle -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">View:</label>
          <select
            v-model="viewMode"
            @change="filterTimeline"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="all">All Activity</option>
            <option value="journal">Journal Only</option>
            <option value="changes">Changes Only</option>
          </select>
        </div>
        
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ filteredItems.length }} items
        </div>
      </div>
      
      <div class="text-xs text-gray-400">
        Last updated: {{ lastUpdated }}
      </div>
    </div>

    <!-- Unified Timeline -->
    <JournalTimelineView
      :items="filteredItems"
      :loading="loading"
      :bow-setup="bowSetup"
      @entry-updated="refreshTimeline"
      @entry-deleted="refreshTimeline"
      @equipment-restored="handleEquipmentRestored"
      @error="handleError"
    />

    <!-- Load More Button -->
    <div v-if="hasMoreItems" class="mt-6 text-center">
      <CustomButton
        @click="loadMoreItems"
        variant="outlined"
        :disabled="loading"
      >
        <i class="fas fa-chevron-down mr-2"></i>
        Load More Activity
      </CustomButton>
    </div>

    <!-- Notification Toast -->
    <div
      v-if="notification.show"
      class="fixed bottom-4 right-4 z-50 transition-all duration-300"
      :class="getNotificationClasses(notification.type)"
    >
      <div class="flex items-center">
        <i :class="getNotificationIcon(notification.type)" class="mr-2"></i>
        {{ notification.message }}
        <button @click="hideNotification" class="ml-4 opacity-70 hover:opacity-100">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '@/composables/useApi'
import { useJournalApi } from '@/composables/useJournalApi'
import JournalEntryForm from '@/components/JournalEntryForm.vue'
import JournalTimelineView from '@/components/JournalTimelineView.vue'
import CustomButton from '@/components/CustomButton.vue'

const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['statistics-updated', 'notification'])

// Composables
const journalApi = useJournalApi()

// State
const loading = ref(false)
const showQuickEntryForm = ref(false)
const viewMode = ref('all')
const timelineItems = ref([])
const changeHistoryItems = ref([])
const journalEntries = ref([])
const filteredItems = ref([])
const hasMoreItems = ref(false)
const currentPage = ref(1)
const lastUpdated = ref('')

// Entry types for quick form
const entryTypes = ref([
  { value: 'setup_change', label: 'Setup Change', icon: 'fas fa-crosshairs' },
  { value: 'tuning_session', label: 'Tuning Session', icon: 'fas fa-adjust' },
  { value: 'shooting_notes', label: 'Shooting Notes', icon: 'fas fa-target' },
  { value: 'maintenance', label: 'Maintenance', icon: 'fas fa-wrench' },
  { value: 'general', label: 'General Note', icon: 'fas fa-sticky-note' }
])

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Load timeline data
const loadTimelineData = async (append = false) => {
  loading.value = true
  try {
    // Load journal entries
    const journalResponse = await journalApi.getEntries({
      bow_setup_id: props.bowSetup.id,
      page: append ? currentPage.value : 1,
      limit: 20
    })
    
    if (journalResponse.success) {
      if (append) {
        journalEntries.value.push(...journalResponse.data)
      } else {
        journalEntries.value = journalResponse.data
        currentPage.value = 1
      }
    }

    // Load change history (assuming API exists)
    try {
      const api = useApi()
      const changeResponse = await api.get(`/bow-setups/${props.bowSetup.id}/change-log`, {
        params: { limit: append ? (currentPage.value * 20) : 20 }
      })
      
      if (!append) {
        changeHistoryItems.value = changeResponse.changes || []
      }
    } catch (err) {
      console.warn('Change history not available:', err)
      changeHistoryItems.value = []
    }

    // Merge and sort timeline items
    mergeTimelineItems()
    updateLastUpdated()
    
    // Update statistics
    emitStatistics()

  } catch (error) {
    console.error('Error loading timeline data:', error)
    showNotification('Failed to load timeline data', 'error')
  } finally {
    loading.value = false
  }
}

// Merge journal entries and change history into unified timeline
const mergeTimelineItems = () => {
  const mergedItems = []
  
  // Add journal entries with type indicator
  journalEntries.value.forEach(entry => {
    mergedItems.push({
      ...entry,
      item_type: 'journal',
      created_at: entry.created_at,
      sort_date: new Date(entry.created_at)
    })
  })
  
  // Add change history items with type indicator
  changeHistoryItems.value.forEach(change => {
    mergedItems.push({
      ...change,
      item_type: 'change',
      created_at: change.created_at,
      sort_date: new Date(change.created_at)
    })
  })
  
  // Sort by date (newest first)
  mergedItems.sort((a, b) => b.sort_date - a.sort_date)
  
  timelineItems.value = mergedItems
  filterTimeline()
}

// Filter timeline based on view mode
const filterTimeline = () => {
  let filtered = []
  
  switch (viewMode.value) {
    case 'journal':
      filtered = timelineItems.value.filter(item => item.item_type === 'journal')
      break
    case 'changes':
      filtered = timelineItems.value.filter(item => item.item_type === 'change')
      break
    default:
      filtered = timelineItems.value
  }
  
  filteredItems.value = filtered
}

// Handle quick entry save
const handleQuickEntrySave = async (entryData) => {
  try {
    // Ensure bow_setup_id is set
    const submitData = {
      ...entryData,
      bow_setup_id: props.bowSetup.id
    }

    const response = await journalApi.createEntry(submitData)
    
    if (response.success) {
      showNotification('Journal entry created successfully', 'success')
      showQuickEntryForm.value = false
      await refreshTimeline()
    } else {
      throw new Error(response.error || 'Failed to create entry')
    }
  } catch (error) {
    console.error('Error creating journal entry:', error)
    showNotification(error.message || 'Failed to create journal entry', 'error')
  }
}

// Handle auto-save
const handleAutoSave = (draftData) => {
  // Auto-save handled by the form component
  console.log('Auto-saving draft:', draftData)
}

// Refresh timeline
const refreshTimeline = async () => {
  await loadTimelineData()
}

// Load more items
const loadMoreItems = async () => {
  currentPage.value++
  await loadTimelineData(true)
}

// Handle equipment restored
const handleEquipmentRestored = (equipmentInfo) => {
  showNotification(`${equipmentInfo.equipmentName} restored successfully`, 'success')
  refreshTimeline()
}

// Handle errors
const handleError = (message) => {
  showNotification(message, 'error')
}

// Notification methods
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  }
  
  // Emit to parent component as well
  emit('notification', { message, type })
  
  setTimeout(() => {
    hideNotification()
  }, 5000)
}

const hideNotification = () => {
  notification.value.show = false
}

const getNotificationClasses = (type) => {
  const baseClasses = 'p-4 rounded-lg shadow-lg max-w-sm'
  switch (type) {
    case 'success':
      return `${baseClasses} bg-green-600 text-white`
    case 'error':
      return `${baseClasses} bg-red-600 text-white`
    case 'warning':
      return `${baseClasses} bg-yellow-600 text-white`
    default:
      return `${baseClasses} bg-blue-600 text-white`
  }
}

const getNotificationIcon = (type) => {
  switch (type) {
    case 'success':
      return 'fas fa-check-circle'
    case 'error':
      return 'fas fa-exclamation-circle'
    case 'warning':
      return 'fas fa-exclamation-triangle'
    default:
      return 'fas fa-info-circle'
  }
}

// Update last updated timestamp
const updateLastUpdated = () => {
  lastUpdated.value = new Date().toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// Emit statistics to parent
const emitStatistics = () => {
  const stats = {
    journal_entries: journalEntries.value.length,
    change_history: changeHistoryItems.value.length,
    total_activity: timelineItems.value.length
  }
  
  emit('statistics-updated', stats)
}

// Watch for bow setup changes
watch(() => props.bowSetup?.id, (newId) => {
  if (newId) {
    loadTimelineData()
  }
})

// Load data on mount
onMounted(() => {
  if (props.bowSetup?.id) {
    loadTimelineData()
  }
})

// Expose refresh method
defineExpose({
  refresh: refreshTimeline,
  loadMore: loadMoreItems
})
</script>

<style scoped>
.setup-journal {
  width: 100%;
}

/* Quick entry form animation */
.setup-journal .bg-indigo-50 {
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

/* Mobile optimizations */
@media (max-width: 640px) {
  .setup-journal .flex.gap-2 {
    width: 100%;
  }
  
  .setup-journal .flex.gap-2 button {
    flex: 1;
  }
}
</style>