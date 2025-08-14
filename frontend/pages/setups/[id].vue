
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="container mx-auto px-4 py-8">
      <div class="animate-pulse">
        <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-64 mb-6"></div>
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-4"></div>
          <div class="space-y-3">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="container mx-auto px-4 py-8">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <i class="fas fa-exclamation-triangle text-4xl text-red-600 dark:text-red-400 mb-4"></i>
        <h2 class="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">Setup Not Found</h2>
        <p class="text-red-600 dark:text-red-400 mb-4">{{ error }}</p>
        <NuxtLink
          to="/my-setup"
          class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          <i class="fas fa-arrow-left mr-2"></i>
          Back to My Setups
        </NuxtLink>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="setup" class="container mx-auto px-4 py-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <div class="flex items-center space-x-2 mb-2">
            <NuxtLink
              to="/my-setup"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              <i class="fas fa-arrow-left mr-1"></i>
              Back to Setups
            </NuxtLink>
          </div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ setup.name }}</h1>
          <p class="text-gray-600 dark:text-gray-400">{{ setup.bow_type }} Setup</p>
        </div>
        
      </div>

      <!-- Tab Navigation -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-6">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="flex space-x-8 px-6" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              ]"
            >
              <i :class="tab.icon" class="mr-2"></i>
              {{ tab.name }}
              <span v-if="tab.badge" class="ml-2 px-2 py-1 text-xs bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 rounded-full">
                {{ tab.badge }}
              </span>
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="p-6">
          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="space-y-6">
            <BowSetupOverview 
              :setup="setup" 
              :statistics="statistics" 
              @switch-tab="(tab) => activeTab = tab"
            />
          </div>

          <!-- Arrows Tab -->
          <div v-if="activeTab === 'arrows'" class="space-y-6">
            <BowSetupArrowsList 
              :bowSetup="setup" 
              :expanded="true"
              @arrow-updated="loadSetup"
              @show-notification="showNotification"
              @edit-arrow="handleEditArrow"
              @view-details="handleViewArrowDetails"
              @duplicate-arrow="handleDuplicateArrow"
            />
          </div>

          <!-- Equipment Tab -->
          <div v-if="activeTab === 'equipment'" class="space-y-6">
            <BowEquipmentManager 
              :bow-setup="setup"
              @equipment-updated="loadSetup"
              @show-notification="showNotification"
            />
          </div>

          <!-- Change History Tab -->
          <div v-if="activeTab === 'history'" class="space-y-6">
            <EnhancedChangeLogViewer
              ref="changeLogComponent"
              :bow-setup-id="setup.id"
              :show-header="false"
              @error="(message) => showNotification(message, 'error')"
            />
          </div>

          <!-- Settings Tab -->
          <div v-if="activeTab === 'settings'" class="space-y-6">
            <BowSetupSettings 
              :setup="setup"
              @setup-updated="loadSetup"
              @show-notification="showNotification"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Setup Modal -->
    <AddBowSetupModal
      v-if="showEditModal"
      :modelValue="setup"
      :is-editing="true"
      :isSaving="isSaving"
      :error="editError"
      @update:modelValue="setup = $event"
      @save="handleSaveSetup"
      @close="showEditModal = false"
    />

    <!-- Arrow Edit Modal -->
    <EditArrowModal
      :is-open="showArrowEditModal"
      :arrow-setup="editingArrowSetup"
      :bow-setup="setup"
      @close="showArrowEditModal = false; editingArrowSetup = null"
      @save="handleArrowSave"
      @error="(message) => showNotification(message, 'error')"
    />

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
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import BowSetupOverview from '~/components/BowSetupOverview.vue'
import BowSetupArrowsList from '~/components/BowSetupArrowsList.vue'
import BowEquipmentManager from '~/components/BowEquipmentManager.vue'
import EnhancedChangeLogViewer from '~/components/EnhancedChangeLogViewer.vue'
import BowSetupSettings from '~/components/BowSetupSettings.vue'
import AddBowSetupModal from '~/components/AddBowSetupModal.vue'
import EditArrowModal from '~/components/EditArrowModal.vue'
import CustomButton from '~/components/CustomButton.vue'

// Meta information
definePageMeta({
  title: 'Bow Setup Details'
})

// Composables
const route = useRoute()
const router = useRouter()
const api = useApi()

// State
const setup = ref(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref('overview')
const statistics = ref({})
const showEditModal = ref(false)
const isSaving = ref(false)
const editError = ref('')
const changeLogComponent = ref(null)
const showArrowEditModal = ref(false)
const editingArrowSetup = ref(null)

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Tab configuration
const tabs = computed(() => [
  {
    id: 'overview',
    name: 'Overview',
    icon: 'fas fa-tachometer-alt',
    badge: null
  },
  {
    id: 'arrows',
    name: 'Arrows',
    icon: 'fas fa-bullseye',
    badge: statistics.value.arrow_count || null
  },
  {
    id: 'equipment',
    name: 'Equipment',
    icon: 'fas fa-cogs',
    badge: statistics.value.equipment_count || null
  },
  {
    id: 'history',
    name: 'Change History',
    icon: 'fas fa-history',
    badge: statistics.value.total_changes || null
  },
  {
    id: 'settings',
    name: 'Edit Setup',
    icon: 'fas fa-edit',
    badge: null
  }
])

// Methods
const loadSetup = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await api.get(`/bow-setups/${route.params.id}`)
    setup.value = response
    
    // Load additional statistics
    await loadStatistics()
    
    // Refresh change log if it exists
    if (changeLogComponent.value) {
      changeLogComponent.value.refresh()
    }
    
  } catch (err) {
    console.error('Error loading setup:', err)
    error.value = err.message || 'Failed to load bow setup'
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    // Load arrow count
    const arrowsResponse = await api.get(`/bow-setups/${route.params.id}/arrows`)
    const arrowCount = arrowsResponse.arrows?.length || 0
    
    // Load equipment count
    const equipmentResponse = await api.get(`/bow-setups/${route.params.id}/equipment`)
    const equipmentCount = equipmentResponse.equipment?.length || 0
    
    // Load change statistics
    const statsResponse = await api.get(`/bow-setups/${route.params.id}/change-log/statistics`)
    const totalChanges = statsResponse.total_changes || 0
    
    statistics.value = {
      arrow_count: arrowCount,
      equipment_count: equipmentCount,
      total_changes: totalChanges
    }
    
  } catch (err) {
    console.error('Error loading statistics:', err)
  }
}

const handleSaveSetup = async (setupData) => {
  try {
    isSaving.value = true
    editError.value = ''
    
    await api.put(`/bow-setups/${route.params.id}`, setupData)
    
    showEditModal.value = false
    showNotification('Bow setup updated successfully', 'success')
    await loadSetup()
    
  } catch (err) {
    console.error('Error saving setup:', err)
    editError.value = err.message || 'Failed to save bow setup'
  } finally {
    isSaving.value = false
  }
}

const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  }
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    hideNotification()
  }, 5000)
}

const hideNotification = () => {
  notification.value.show = false
}

// Arrow action handlers
const handleEditArrow = (arrowSetup) => {
  editingArrowSetup.value = arrowSetup
  showArrowEditModal.value = true
}

const handleArrowSave = async (updateData) => {
  try {
    // Call the API to update the arrow
    await api.put(`/setup-arrows/${editingArrowSetup.value.id}`, updateData)
    
    // Reload setup data and close modal
    await loadSetup()
    showArrowEditModal.value = false
    editingArrowSetup.value = null
    
    showNotification('Arrow updated successfully', 'success')
  } catch (error) {
    console.error('Error updating arrow:', error)
    showNotification(error.message || 'Failed to update arrow', 'error')
  }
}

const handleViewArrowDetails = (arrowId) => {
  // Navigate to arrow details page
  if (arrowId) {
    router.push(`/arrows/${arrowId}`)
  } else {
    showNotification('Cannot view details for this arrow', 'error')
  }
}

const handleDuplicateArrow = (arrowSetup) => {
  // This is a fallback for when the component's internal duplication fails
  // The component should handle duplication internally, but this provides user feedback
  console.log('Fallback duplicate arrow:', arrowSetup)
  showNotification('Arrow duplication failed. Please try again.', 'error')
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

// Lifecycle
onMounted(() => {
  loadSetup()
})
</script>
