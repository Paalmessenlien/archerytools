
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
    <div v-else-if="setup" class="container mx-auto px-4 py-8 pb-24 md:pb-8 mobile-safe-area">
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
          <nav class="tab-navigation flex overflow-x-auto sm:space-x-8 sm:px-6" aria-label="Tabs">
            <!-- Mobile: Equal width tabs, Desktop: Auto width -->
            <div class="flex w-full sm:contents">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="handleTabClick(tab.id)"
                @touchstart="handleTouchStart"
                @touchend="handleTouchEnd"
                :class="[
                  'py-4 px-4 sm:px-1 min-h-[48px] border-b-2 font-medium text-sm transition-all duration-200 touch-manipulation',
                  'flex items-center justify-center flex-1 sm:flex-initial',
                  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                ]"
              >
                <!-- Mobile: Show icon + badge, Desktop: Show all -->
                <span class="flex items-center">
                  <i :class="tab.icon" class="mr-1 sm:mr-2"></i>
                  <!-- Short names on mobile, full names on desktop -->
                  <span class="hidden sm:inline">{{ tab.name }}</span>
                  <span class="sm:hidden">{{ tab.shortName || tab.name }}</span>
                  <span v-if="tab.badge" class="ml-1 sm:ml-2 px-1.5 py-0.5 sm:px-2 sm:py-1 text-xs bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 rounded-full">
                    {{ tab.badge }}
                  </span>
                </span>
              </button>
            </div>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="p-4 sm:p-6">
          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="space-y-4 sm:space-y-6">
            <BowSetupOverview 
              :setup="setup" 
              :statistics="statistics" 
              @switch-tab="(tab) => activeTab = tab"
            />
          </div>

          <!-- Arrows Tab -->
          <div v-if="activeTab === 'arrows'" class="space-y-4 sm:space-y-6">
            <div class="mobile-arrows-header">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                My Arrows ({{ statistics.arrow_count || 0 }})
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Manage your arrow configurations and performance data
              </p>
            </div>
            <BowSetupArrowsList 
              ref="arrowsList"
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
          <div v-if="activeTab === 'equipment'" class="space-y-4 sm:space-y-6">
            <div class="mobile-equipment-header">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Equipment Setup
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Track your bow accessories and components
              </p>
            </div>
            <BowEquipmentManager 
              :bow-setup="setup"
              @equipment-updated="loadSetup"
              @show-notification="showNotification"
            />
          </div>

          <!-- Change History Tab -->
          <div v-if="activeTab === 'history'" class="space-y-4 sm:space-y-6">
            <div class="mobile-history-header">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Setup History ({{ statistics.total_changes || 0 }})
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Track all changes made to your bow setup
              </p>
            </div>
            <EnhancedChangeLogViewer
              ref="changeLogComponent"
              :bow-setup-id="setup.id"
              :show-header="false"
              @error="(message) => showNotification(message, 'error')"
            />
          </div>

          <!-- Settings Tab -->
          <div v-if="activeTab === 'settings'" class="space-y-4 sm:space-y-6">
            <div class="mobile-settings-header">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Setup Configuration
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Modify your bow specifications and settings
              </p>
            </div>
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
import { useBowSetupPickerStore } from '~/stores/bowSetupPicker'
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
const bowSetupPickerStore = useBowSetupPickerStore()

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
const arrowsList = ref(null)

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Performance calculation state
const calculatingPerformance = ref(false)

// Tab configuration with mobile-friendly names
const tabs = computed(() => [
  {
    id: 'overview',
    name: 'Overview',
    shortName: 'Overview',
    icon: 'fas fa-tachometer-alt',
    badge: null
  },
  {
    id: 'arrows',
    name: 'Arrows',
    shortName: 'Arrows',
    icon: 'fas fa-bullseye',
    badge: statistics.value.arrow_count || null
  },
  {
    id: 'equipment',
    name: 'Equipment',
    shortName: 'Equipment',
    icon: 'fas fa-cogs',
    badge: statistics.value.equipment_count || null
  },
  {
    id: 'history',
    name: 'Change History',
    shortName: 'History',
    icon: 'fas fa-history',
    badge: statistics.value.total_changes || null
  },
  {
    id: 'settings',
    name: 'Edit Setup',
    shortName: 'Edit',
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
    
    // Refresh bow selector navigation cache after successful save
    if (bowSetupPickerStore.refreshSelectedBowSetup) {
      await bowSetupPickerStore.refreshSelectedBowSetup(parseInt(route.params.id))
    }
    
  } catch (err) {
    console.error('Error saving setup:', err)
    editError.value = err.message || 'Failed to save bow setup'
  } finally {
    isSaving.value = false
  }
}

// Enhanced tab interaction methods
const handleTabClick = (tabId) => {
  console.log('Tab clicked:', tabId)
  activeTab.value = tabId
}

const handleTouchStart = (event) => {
  // Add visual feedback on touch start
  event.target.style.opacity = '0.8'
}

const handleTouchEnd = (event) => {
  // Remove visual feedback on touch end
  event.target.style.opacity = '1'
  
  // Ensure click event fires
  setTimeout(() => {
    if (event.target.closest('button')) {
      event.target.closest('button').click()
    }
  }, 10)
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

// Performance calculation function
const calculatePerformanceForAllArrows = async () => {
  calculatingPerformance.value = true
  try {
    const response = await api.post(`/bow-setups/${setup.value.id}/arrows/calculate-performance`, {})
    
    if (response.updated_arrows && response.updated_arrows.length > 0) {
      showNotification(`Performance calculated for ${response.updated_arrows.length} arrows`, 'success')
      // Refresh the arrows list to show updated performance data
      if (arrowsList.value) {
        await arrowsList.value.refresh()
      } else {
        // Fallback to full setup reload
        await loadSetup()
      }
    } else {
      showNotification('No arrows found to calculate performance for', 'warning')
    }
  } catch (error) {
    console.error('Error calculating performance:', error)
    showNotification('Failed to calculate arrow performance', 'error')
  } finally {
    calculatingPerformance.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadSetup()
})
</script>

<style scoped>
/* Enhanced tab navigation styling */
.tab-navigation {
  /* Hide scrollbar on mobile while maintaining scroll functionality */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.tab-navigation::-webkit-scrollbar {
  display: none;
}

/* Enhanced touch interaction for mobile */
@media (max-width: 640px) {
  .tab-navigation button {
    /* Ensure minimum touch target size */
    min-width: 60px;
  }
  
  /* Add ripple effect simulation on touch */
  .tab-navigation button:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }
}

/* Smooth transitions for tab switching */
.tab-navigation button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced focus states for accessibility */
.tab-navigation button:focus-visible {
  outline: 2px solid rgb(59 130 246);
  outline-offset: 2px;
}

/* Mobile content optimization */
@media (max-width: 640px) {
  /* Mobile header sections */
  .mobile-arrows-header,
  .mobile-equipment-header,
  .mobile-history-header,
  .mobile-settings-header {
    background: rgb(249 250 251);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
  }
  
  .dark .mobile-arrows-header,
  .dark .mobile-equipment-header,
  .dark .mobile-history-header,
  .dark .mobile-settings-header {
    background: rgb(31 41 55);
    border: 1px solid rgb(55 65 81);
  }
  
  /* Reduce excessive spacing on mobile */
  .space-y-4 > * + * {
    margin-top: 1rem;
  }
  
  /* Mobile-optimized card spacing */
  .space-y-4 {
    gap: 1rem;
  }
}
</style>
