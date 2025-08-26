<template>
  <div class="arrow-journal">
    <!-- Journal Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 flex items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex-shrink-0">
            <i class="fas fa-journal-whills text-indigo-600 dark:text-indigo-400 text-lg"></i>
          </div>
          <div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Arrow Journal</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">Track performance notes and observations for this arrow</p>
          </div>
        </div>
        
        <div class="flex gap-2">
          <CustomButton
            @click="showQuickEntryForm = !showQuickEntryForm"
            variant="primary"
            class="flex-shrink-0"
          >
            <i class="fas fa-plus mr-2"></i>
            Add Note
          </CustomButton>
          
          <CustomButton
            @click="refreshEntries"
            variant="outlined"
            :disabled="loading"
          >
            <i :class="['fas fa-sync-alt', loading ? 'animate-spin' : '']"></i>
          </CustomButton>
        </div>
      </div>

      <!-- Quick Stats -->
      <div v-if="entries.length > 0" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ entries.length }}</div>
          <div class="text-xs text-blue-600 dark:text-blue-400">Total Entries</div>
        </div>
        <div class="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div class="text-lg font-bold text-green-600 dark:text-green-400">{{ recentEntries }}</div>
          <div class="text-xs text-green-600 dark:text-green-400">This Week</div>
        </div>
        <div class="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <div class="text-lg font-bold text-purple-600 dark:text-purple-400">{{ performanceEntries }}</div>
          <div class="text-xs text-purple-600 dark:text-purple-400">Performance</div>
        </div>
        <div class="text-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
          <div class="text-lg font-bold text-orange-600 dark:text-orange-400">{{ tuningEntries }}</div>
          <div class="text-xs text-orange-600 dark:text-orange-400">Tuning</div>
        </div>
      </div>
    </div>

    <!-- Quick Entry Form (Collapsible) -->
    <div v-if="showQuickEntryForm" class="mb-6">
      <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-200 dark:border-indigo-800 p-1">
        <JournalEntryForm
          mode="inline"
          :entry="null"
          :bow-setups="[]"
          :entry-types="arrowEntryTypes"
          @save="handleQuickEntrySave"
          @cancel="showQuickEntryForm = false"
          @auto-save="handleAutoSave"
        />
      </div>
    </div>

    <!-- Entry Type Filter -->
    <div v-if="entries.length > 0" class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Filter:</label>
          <select
            v-model="filterType"
            @change="filterEntries"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Types</option>
            <option value="shooting_notes">Shooting Notes</option>
            <option value="arrow_performance">Performance</option>
            <option value="tuning_session">Tuning</option>
            <option value="maintenance">Maintenance</option>
            <option value="general">General Notes</option>
          </select>
        </div>
        
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ filteredEntries.length }} entries
        </div>
      </div>
    </div>

    <!-- Journal Entries -->
    <div class="space-y-4">
      <!-- Loading State -->
      <div v-if="loading && entries.length === 0" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 dark:border-indigo-400 mx-auto mb-3"></div>
        <p class="text-gray-600 dark:text-gray-400">Loading journal entries...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="entries.length === 0 && !loading" class="text-center py-12">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
          <i class="fas fa-bullseye text-2xl text-gray-400"></i>
        </div>
        <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          No Journal Entries Yet
        </h4>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          Start tracking your experience with this arrow by adding your first entry.
        </p>
        <CustomButton
          @click="showQuickEntryForm = true"
          variant="primary"
        >
          <i class="fas fa-plus mr-2"></i>
          Add First Entry
        </CustomButton>
      </div>

      <!-- Entry List -->
      <div v-else class="space-y-4">
        <div
          v-for="entry in filteredEntries"
          :key="entry.id"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <div class="flex items-center space-x-2 mb-2">
                <span :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  getEntryTypeBadge(entry.entry_type)
                ]">
                  {{ formatEntryType(entry.entry_type) }}
                </span>
                
                <span v-if="entry.is_private" class="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full">
                  <i class="fas fa-lock mr-1"></i>
                  Private
                </span>
              </div>
              
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                {{ entry.title }}
              </h4>
              
              <!-- Tags -->
              <div v-if="entry.tags && entry.tags.length > 0" class="flex flex-wrap gap-1 mb-2">
                <span
                  v-for="tag in entry.tags"
                  :key="tag"
                  class="px-2 py-1 text-xs bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-full"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
            
            <div class="text-right">
              <div class="text-sm text-gray-500 dark:text-gray-400">
                {{ formatTimestamp(entry.created_at) }}
              </div>
            </div>
          </div>
          
          <!-- Content Preview -->
          <div class="mb-3">
            <p class="text-gray-700 dark:text-gray-300 text-sm line-clamp-3">
              {{ entry.content }}
            </p>
          </div>
          
          <!-- Images Preview -->
          <div v-if="entry.images && entry.images.length > 0" class="mb-3">
            <div class="flex gap-2 overflow-x-auto">
              <img
                v-for="(image, index) in entry.images.slice(0, 3)"
                :key="index"
                :src="image.url"
                :alt="image.alt || `Entry image ${index + 1}`"
                class="w-16 h-16 object-cover rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                @click="openImageViewer(image.url)"
                @error="handleImageError"
              >
              <div
                v-if="entry.images.length > 3"
                class="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center text-sm font-medium text-gray-600 dark:text-gray-400"
              >
                +{{ entry.images.length - 3 }}
              </div>
            </div>
          </div>
          
          <!-- Actions -->
          <div class="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700">
            <div class="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <span>{{ entry.content?.length || 0 }} chars</span>
              <span v-if="entry.images && entry.images.length > 0">
                <i class="fas fa-image mr-1"></i>
                {{ entry.images.length }}
              </span>
            </div>
            
            <div class="flex gap-2">
              <button
                @click="editEntry(entry)"
                class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Edit entry"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="deleteEntry(entry.id)"
                class="p-2 text-gray-400 hover:text-red-500 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Delete entry"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMoreEntries" class="text-center py-4">
        <CustomButton
          @click="loadMoreEntries"
          variant="outlined"
          :disabled="loading"
        >
          <i class="fas fa-chevron-down mr-2"></i>
          Load More Entries
        </CustomButton>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingEntry" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <JournalEntryForm
          mode="modal"
          :show="true"
          :entry="editingEntry"
          :bow-setups="[]"
          :entry-types="arrowEntryTypes"
          @save="handleEntrySave"
          @close="editingEntry = null"
          @cancel="editingEntry = null"
        />
      </div>
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
import { useJournalApi } from '@/composables/useJournalApi'
import JournalEntryForm from '@/components/JournalEntryForm.vue'
import CustomButton from '@/components/CustomButton.vue'

const props = defineProps({
  arrowId: {
    type: [String, Number],
    required: true
  },
  arrow: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['statistics-updated'])

// Composables
const journalApi = useJournalApi()

// State
const loading = ref(false)
const showQuickEntryForm = ref(false)
const entries = ref([])
const filteredEntries = ref([])
const filterType = ref('')
const editingEntry = ref(null)
const hasMoreEntries = ref(false)
const currentPage = ref(1)

// Arrow-specific entry types
const arrowEntryTypes = ref([
  { value: 'shooting_notes', label: 'Shooting Notes', icon: 'fas fa-target' },
  { value: 'arrow_performance', label: 'Performance Notes', icon: 'fas fa-chart-line' },
  { value: 'tuning_session', label: 'Tuning Session', icon: 'fas fa-adjust' },
  { value: 'maintenance', label: 'Maintenance', icon: 'fas fa-tools' },
  { value: 'general', label: 'General Note', icon: 'fas fa-sticky-note' }
])

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Computed statistics
const recentEntries = computed(() => {
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  return entries.value.filter(entry => new Date(entry.created_at) > oneWeekAgo).length
})

const performanceEntries = computed(() => {
  return entries.value.filter(entry => 
    entry.entry_type === 'arrow_performance' || entry.entry_type === 'shooting_notes'
  ).length
})

const tuningEntries = computed(() => {
  return entries.value.filter(entry => entry.entry_type === 'tuning_session').length
})

// Load entries
const loadEntries = async (append = false) => {
  loading.value = true
  try {
    const response = await journalApi.getEntries({
      linked_arrow: props.arrowId,
      page: append ? currentPage.value : 1,
      limit: 10
    })
    
    if (response.success) {
      if (append) {
        entries.value.push(...response.data)
      } else {
        entries.value = response.data
        currentPage.value = 1
      }
      
      hasMoreEntries.value = response.pagination && 
        response.pagination.page < response.pagination.pages
    }
    
    filterEntries()
    emitStatistics()
    
  } catch (error) {
    console.error('Error loading arrow journal entries:', error)
    showNotification('Failed to load journal entries', 'error')
  } finally {
    loading.value = false
  }
}

// Filter entries
const filterEntries = () => {
  if (!filterType.value) {
    filteredEntries.value = entries.value
  } else {
    filteredEntries.value = entries.value.filter(entry => 
      entry.entry_type === filterType.value
    )
  }
}

// Handle quick entry save
const handleQuickEntrySave = async (entryData) => {
  try {
    const submitData = {
      ...entryData,
      linked_arrow: props.arrowId
    }

    const response = await journalApi.createEntry(submitData)
    
    if (response.success) {
      showNotification('Journal entry created successfully', 'success')
      showQuickEntryForm.value = false
      await refreshEntries()
    } else {
      throw new Error(response.error || 'Failed to create entry')
    }
  } catch (error) {
    console.error('Error creating arrow journal entry:', error)
    showNotification(error.message || 'Failed to create journal entry', 'error')
  }
}

// Handle entry edit
const editEntry = (entry) => {
  editingEntry.value = entry
}

// Handle entry save from edit modal
const handleEntrySave = async (updatedData) => {
  try {
    const response = await journalApi.updateEntry(editingEntry.value.id, updatedData)
    
    if (response.success) {
      showNotification('Entry updated successfully', 'success')
      editingEntry.value = null
      await refreshEntries()
    } else {
      throw new Error(response.error || 'Failed to update entry')
    }
  } catch (error) {
    console.error('Error updating entry:', error)
    showNotification(error.message || 'Failed to update entry', 'error')
  }
}

// Handle entry deletion
const deleteEntry = async (entryId) => {
  if (!confirm('Are you sure you want to delete this journal entry?')) {
    return
  }
  
  try {
    const response = await journalApi.deleteEntry(entryId)
    
    if (response.success) {
      showNotification('Entry deleted successfully', 'success')
      await refreshEntries()
    } else {
      throw new Error(response.error || 'Failed to delete entry')
    }
  } catch (error) {
    console.error('Error deleting entry:', error)
    showNotification(error.message || 'Failed to delete entry', 'error')
  }
}

// Load more entries
const loadMoreEntries = async () => {
  currentPage.value++
  await loadEntries(true)
}

// Refresh entries
const refreshEntries = async () => {
  await loadEntries()
}

// Auto-save handler
const handleAutoSave = (draftData) => {
  console.log('Auto-saving draft:', draftData)
}

// Image viewer
const openImageViewer = (imageUrl) => {
  window.open(imageUrl, '_blank')
}

// Handle image errors
const handleImageError = (event) => {
  console.error('Failed to load image:', event.target.src)
  event.target.style.display = 'none'
}

// Emit statistics
const emitStatistics = () => {
  const stats = {
    total_entries: entries.value.length,
    recent_entries: recentEntries.value,
    performance_entries: performanceEntries.value,
    tuning_entries: tuningEntries.value
  }
  
  emit('statistics-updated', stats)
}

// Notification methods
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  }
  
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

// Formatting methods
const formatEntryType = (type) => {
  const labels = {
    'shooting_notes': 'Shooting Notes',
    'arrow_performance': 'Performance',
    'tuning_session': 'Tuning Session',
    'maintenance': 'Maintenance',
    'general': 'General Note'
  }
  return labels[type] || type
}

const getEntryTypeBadge = (type) => {
  const badges = {
    'shooting_notes': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'arrow_performance': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'tuning_session': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'maintenance': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    'general': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
  }
  return badges[type] || 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
}

const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (days > 7) {
    return date.toLocaleDateString()
  } else if (days > 0) {
    return `${days} day${days > 1 ? 's' : ''} ago`
  } else if (hours > 0) {
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else if (minutes > 0) {
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  } else {
    return 'Just now'
  }
}

// Watch for arrow ID changes
watch(() => props.arrowId, (newId) => {
  if (newId) {
    loadEntries()
  }
})

// Load entries on mount
onMounted(() => {
  if (props.arrowId) {
    loadEntries()
  }
})

// Expose refresh method
defineExpose({
  refresh: refreshEntries
})
</script>

<style scoped>
.arrow-journal {
  width: 100%;
}

/* Line clamp for content preview */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Quick entry form animation */
.arrow-journal .bg-indigo-50 {
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
  .arrow-journal .grid-cols-2.md\:grid-cols-4 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .arrow-journal .p-6 {
    padding: 1rem;
  }
  
  .arrow-journal .text-xl {
    font-size: 1.125rem;
  }
}
</style>