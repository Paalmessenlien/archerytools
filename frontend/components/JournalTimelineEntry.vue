<template>
  <div class="journal-timeline-entry">
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm hover:shadow-md transition-shadow">
      <!-- Entry Header -->
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <!-- Entry type badge -->
            <span :class="[
              'px-3 py-1 text-sm font-medium rounded-full',
              getEntryTypeBadge(entry.entry_type)
            ]">
              {{ formatEntryType(entry.entry_type) }}
            </span>
            
            <!-- Private indicator -->
            <span v-if="entry.is_private" class="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full">
              <i class="fas fa-lock mr-1"></i>
              Private
            </span>
          </div>
          
          <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
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
        
        <!-- Entry Actions -->
        <div class="flex items-center space-x-2">
          <!-- Quick Edit Button -->
          <button
            @click="toggleEdit"
            class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Edit entry"
          >
            <i class="fas fa-edit"></i>
          </button>
          
          <!-- More Actions Menu -->
          <div class="relative">
            <button
              @click="showActionsMenu = !showActionsMenu"
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="More actions"
            >
              <i class="fas fa-ellipsis-v"></i>
            </button>
            
            <!-- Actions Dropdown -->
            <div
              v-if="showActionsMenu"
              v-click-outside="() => showActionsMenu = false"
              class="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50"
            >
              <button
                @click="duplicateEntry"
                class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
              >
                <i class="fas fa-copy mr-2"></i>
                Duplicate Entry
              </button>
              <button
                @click="exportEntry"
                class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
              >
                <i class="fas fa-download mr-2"></i>
                Export Entry
              </button>
              <hr class="border-gray-200 dark:border-gray-700">
              <button
                @click="confirmDelete"
                class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center"
              >
                <i class="fas fa-trash mr-2"></i>
                Delete Entry
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Entry Content -->
      <div class="mb-4">
        <!-- Edit Mode -->
        <div v-if="isEditing" class="space-y-4">
          <JournalEntryForm
            mode="inline"
            :entry="entry"
            :bow-setups="bowSetup ? [bowSetup] : []"
            :entry-types="entryTypes"
            @save="handleSave"
            @cancel="toggleEdit"
            @error="handleError"
          />
        </div>
        
        <!-- Display Mode -->
        <div v-else>
          <div class="prose prose-sm dark:prose-invert max-w-none">
            <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ entry.content }}</p>
          </div>
          
          <!-- Images -->
          <div v-if="entry.images && entry.images.length > 0" class="mt-4">
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div
                v-for="(image, index) in entry.images"
                :key="index"
                class="relative group"
              >
                <img
                  :src="image.url"
                  :alt="image.alt || `Entry image ${index + 1}`"
                  class="w-full h-32 object-cover rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                  @click="openImageViewer(image.url)"
                  @error="handleImageError"
                >
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 rounded-lg transition-opacity"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Entry Footer -->
      <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-100 dark:border-gray-700">
        <div class="flex items-center space-x-4">
          <span>
            <i class="fas fa-clock mr-1"></i>
            {{ formatTimestamp(entry.created_at) }}
          </span>
          <span v-if="entry.updated_at && entry.updated_at !== entry.created_at">
            <i class="fas fa-edit mr-1"></i>
            Updated {{ formatTimestamp(entry.updated_at) }}
          </span>
        </div>
        
        <!-- Entry Stats -->
        <div class="flex items-center space-x-3">
          <span v-if="entry.content" class="text-xs">
            {{ entry.content.length }} chars
          </span>
          <span v-if="entry.images && entry.images.length > 0" class="text-xs">
            <i class="fas fa-image mr-1"></i>
            {{ entry.images.length }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
        <div class="flex items-center mb-4">
          <i class="fas fa-exclamation-triangle text-red-500 text-xl mr-3"></i>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Delete Journal Entry</h3>
        </div>
        
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete "{{ entry.title }}"? This action cannot be undone.
        </p>
        
        <div class="flex gap-3 justify-end">
          <CustomButton
            @click="showDeleteConfirmation = false"
            variant="outlined"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="handleDelete"
            variant="primary"
            class="bg-red-600 hover:bg-red-700 text-white"
            :disabled="deleting"
          >
            <span v-if="deleting">Deleting...</span>
            <span v-else>Delete Entry</span>
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useJournalApi } from '@/composables/useJournalApi'
import JournalEntryForm from '@/components/JournalEntryForm.vue'
import CustomButton from '@/components/CustomButton.vue'

const props = defineProps({
  entry: {
    type: Object,
    required: true
  },
  bowSetup: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['updated', 'deleted', 'error'])

// Composables
const journalApi = useJournalApi()

// State
const isEditing = ref(false)
const showActionsMenu = ref(false)
const showDeleteConfirmation = ref(false)
const deleting = ref(false)

// Entry types for form
const entryTypes = ref([
  { value: 'setup_change', label: 'Setup Change', icon: 'fas fa-crosshairs' },
  { value: 'tuning_session', label: 'Tuning Session', icon: 'fas fa-adjust' },
  { value: 'shooting_notes', label: 'Shooting Notes', icon: 'fas fa-target' },
  { value: 'maintenance', label: 'Maintenance', icon: 'fas fa-wrench' },
  { value: 'equipment_change', label: 'Equipment Change', icon: 'fas fa-cogs' },
  { value: 'general', label: 'General Note', icon: 'fas fa-sticky-note' }
])

// Methods
const toggleEdit = () => {
  isEditing.value = !isEditing.value
  showActionsMenu.value = false
}

const handleSave = async (updatedData) => {
  try {
    const response = await journalApi.updateEntry(props.entry.id, updatedData)
    
    if (response.success) {
      isEditing.value = false
      emit('updated')
    } else {
      throw new Error(response.error || 'Failed to update entry')
    }
  } catch (error) {
    console.error('Error updating entry:', error)
    emit('error', error.message || 'Failed to update entry')
  }
}

const confirmDelete = () => {
  showActionsMenu.value = false
  showDeleteConfirmation.value = true
}

const handleDelete = async () => {
  try {
    deleting.value = true
    const response = await journalApi.deleteEntry(props.entry.id)
    
    if (response.success) {
      emit('deleted')
    } else {
      throw new Error(response.error || 'Failed to delete entry')
    }
  } catch (error) {
    console.error('Error deleting entry:', error)
    emit('error', error.message || 'Failed to delete entry')
  } finally {
    deleting.value = false
    showDeleteConfirmation.value = false
  }
}

const duplicateEntry = async () => {
  try {
    showActionsMenu.value = false
    
    const duplicateData = {
      title: `${props.entry.title} (Copy)`,
      content: props.entry.content,
      entry_type: props.entry.entry_type,
      bow_setup_id: props.entry.bow_setup_id,
      tags: props.entry.tags || [],
      is_private: props.entry.is_private
    }
    
    const response = await journalApi.createEntry(duplicateData)
    
    if (response.success) {
      emit('updated') // Trigger refresh
    } else {
      throw new Error(response.error || 'Failed to duplicate entry')
    }
  } catch (error) {
    console.error('Error duplicating entry:', error)
    emit('error', error.message || 'Failed to duplicate entry')
  }
}

const exportEntry = () => {
  showActionsMenu.value = false
  
  const exportData = {
    title: props.entry.title,
    content: props.entry.content,
    type: props.entry.entry_type,
    tags: props.entry.tags,
    created: props.entry.created_at,
    updated: props.entry.updated_at
  }
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
    type: 'application/json' 
  })
  
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `journal-entry-${props.entry.id}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const openImageViewer = (imageUrl) => {
  // Open image in new tab/window
  window.open(imageUrl, '_blank')
}

const handleImageError = (event) => {
  console.error('Failed to load image:', event.target.src)
  event.target.style.display = 'none'
}

const handleError = (message) => {
  emit('error', message)
}

// Formatting methods
const formatEntryType = (type) => {
  const labels = {
    'setup_change': 'Setup Change',
    'tuning_session': 'Tuning Session',
    'shooting_notes': 'Shooting Notes',
    'maintenance': 'Maintenance',
    'equipment_change': 'Equipment Change',
    'general': 'General Note'
  }
  return labels[type] || type
}

const getEntryTypeBadge = (type) => {
  const badges = {
    'setup_change': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'tuning_session': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'shooting_notes': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'maintenance': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    'equipment_change': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
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

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style scoped>
.journal-timeline-entry {
  width: 100%;
}

/* Enhanced hover effects */
.journal-timeline-entry .bg-white:hover {
  transform: translateY(-1px);
}

/* Image grid responsive */
@media (max-width: 640px) {
  .journal-timeline-entry .grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .journal-timeline-entry .h-32 {
    height: 6rem;
  }
}

/* Actions menu animation */
.journal-timeline-entry .absolute.right-0 {
  animation: fadeInDown 0.2s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Prose styling for content */
.prose p {
  margin-bottom: 0.75rem;
}

.prose p:last-child {
  margin-bottom: 0;
}
</style>