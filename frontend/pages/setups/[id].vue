
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="px-1 py-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
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
    <div v-else-if="error" class="px-1 py-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
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
    <div v-else-if="setup" class="px-1 py-4 mx-auto max-w-7xl sm:px-6 lg:px-8 pb-24 md:pb-8">
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

      <!-- Mobile-First Accordion Content Interface -->
      <div class="space-y-4">
        <!-- Overview Section - Always Expanded by Default -->
        <div class="accordion-section bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden" data-section="overview">
          <!-- Section Header -->
          <button
            @click="toggleSection('overview')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 
              'bg-blue-50 dark:bg-blue-900/20': expandedSections.overview,
              'expanded': expandedSections.overview 
            }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30 flex-shrink-0">
                <i class="fas fa-tachometer-alt text-blue-600 dark:text-blue-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Overview</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Bow specifications and quick statistics</p>
              </div>
            </div>
            <i 
              :class="expandedSections.overview ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
              class="text-gray-400 transition-transform duration-200"
            ></i>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.overview" class="accordion-content p-4 sm:p-6 space-y-4 sm:space-y-6">
            <BowSetupOverview 
              :setup="setup" 
              :statistics="statistics" 
              @switch-tab="handleAccordionSwitch"
            />
          </div>
        </div>

        <!-- Arrows Section -->
        <div class="accordion-section bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden" data-section="arrows">
          <!-- Section Header -->
          <button
            @click="toggleSection('arrows')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 
              'bg-green-50 dark:bg-green-900/20': expandedSections.arrows,
              'expanded': expandedSections.arrows 
            }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30 flex-shrink-0">
                <i class="fas fa-crosshairs text-green-600 dark:text-green-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">My Arrows</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Manage your arrow configurations and performance data</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <!-- Arrow Count Badge -->
              <div v-if="statistics.arrow_count" class="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-xs font-medium">
                {{ statistics.arrow_count }} arrows
              </div>
              <!-- Expand/Collapse Icon -->
              <i 
                :class="expandedSections.arrows ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
                class="text-gray-400 transition-transform duration-200"
              ></i>
            </div>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.arrows" class="accordion-content p-4 sm:p-6 space-y-4 sm:space-y-6">
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
        </div>

        <!-- Equipment Section -->
        <div class="accordion-section bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden" data-section="equipment">
          <!-- Section Header -->
          <button
            @click="toggleSection('equipment')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 
              'bg-purple-50 dark:bg-purple-900/20': expandedSections.equipment,
              'expanded': expandedSections.equipment 
            }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/30 flex-shrink-0">
                <i class="fas fa-cogs text-purple-600 dark:text-purple-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Equipment Setup</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Track your bow accessories and components</p>
              </div>
            </div>
            <i 
              :class="expandedSections.equipment ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
              class="text-gray-400 transition-transform duration-200"
            ></i>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.equipment" class="accordion-content p-4 sm:p-6 space-y-4 sm:space-y-6">
            <BowEquipmentManager 
              :bow-setup="setup"
              @equipment-updated="loadSetup"
              @show-notification="showNotification"
            />
          </div>
        </div>

        <!-- Journal & History Section -->
        <div class="accordion-section bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden" data-section="journal">
          <!-- Section Header -->
          <button
            @click="toggleSection('journal')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 
              'bg-indigo-50 dark:bg-indigo-900/20': expandedSections.journal,
              'expanded': expandedSections.journal 
            }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex-shrink-0">
                <i class="fas fa-journal-whills text-indigo-600 dark:text-indigo-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Journal & History</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Track your setup changes and shooting notes</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <!-- Activity Count Badge -->
              <div v-if="statistics.total_activity" class="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full text-xs font-medium">
                {{ statistics.total_activity }} items
              </div>
              <!-- Expand/Collapse Icon -->
              <i 
                :class="expandedSections.journal ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
                class="text-gray-400 transition-transform duration-200"
              ></i>
            </div>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.journal" class="accordion-content p-4 sm:p-6 space-y-4 sm:space-y-6">
            <SetupJournal
              ref="setupJournalComponent"
              :bow-setup="setup"
              @statistics-updated="handleJournalStatisticsUpdate"
              @notification="showNotification"
            />
          </div>
        </div>

        <!-- Settings Section -->
        <div class="accordion-section bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden" data-section="settings">
          <!-- Section Header -->
          <button
            @click="toggleSection('settings')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 
              'bg-indigo-50 dark:bg-indigo-900/20': expandedSections.settings,
              'expanded': expandedSections.settings 
            }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex-shrink-0">
                <i class="fas fa-sliders-h text-indigo-600 dark:text-indigo-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Setup Configuration</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Modify your bow specifications and settings</p>
              </div>
            </div>
            <i 
              :class="expandedSections.settings ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
              class="text-gray-400 transition-transform duration-200"
            ></i>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.settings" class="accordion-content p-4 sm:p-6 space-y-4 sm:space-y-6">
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
import SetupJournal from '~/components/SetupJournal.vue'
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
const statistics = ref({})

// Accordion state - overview expanded by default for primary workflow
const expandedSections = ref({
  overview: true,       // Overview always starts expanded
  arrows: false,       // Arrows collapsed by default
  equipment: false,    // Equipment collapsed by default
  journal: false,      // Journal & History collapsed by default
  settings: false      // Settings collapsed by default
})
const showEditModal = ref(false)
const isSaving = ref(false)
const editError = ref('')
const setupJournalComponent = ref(null)
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


// Methods
const loadSetup = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await api.get(`/bow-setups/${route.params.id}`)
    setup.value = response
    
    // Load additional statistics
    await loadStatistics()
    
    // Refresh journal component if it exists
    if (setupJournalComponent.value) {
      setupJournalComponent.value.refresh()
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
      total_changes: totalChanges,
      total_activity: totalChanges // Initially same as total_changes, will be updated by journal component
    }
    
  } catch (err) {
    console.error('Error loading statistics:', err)
  }
}

// Handle journal statistics updates
const handleJournalStatisticsUpdate = (journalStats) => {
  statistics.value = {
    ...statistics.value,
    journal_entries: journalStats.journal_entries || 0,
    change_history: journalStats.change_history || 0,
    total_activity: journalStats.total_activity || 0
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

// Accordion section toggle method
const toggleSection = (sectionId) => {
  console.log('Accordion section toggled:', sectionId)
  expandedSections.value[sectionId] = !expandedSections.value[sectionId]
}

// Handle accordion switch from overview section
const handleAccordionSwitch = (sectionId) => {
  console.log('Switching to accordion section:', sectionId)
  // Expand the target section
  expandedSections.value[sectionId] = true
  
  // Scroll to the section after a brief delay
  setTimeout(() => {
    const element = document.querySelector(`[data-section="${sectionId}"]`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, 100)
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
/* Mobile-First Accordion Interface Styling */

/* Accordion section headers - Touch-friendly targets */
.accordion-section button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  touch-action: manipulation;
}

/* Enhanced accordion section focus states for accessibility */
.accordion-section button:focus-visible {
  outline: 2px solid rgb(59 130 246);
  outline-offset: -2px;
  border-radius: 8px;
}

/* Accordion section hover effects */
.accordion-section button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dark .accordion-section button:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Smooth accordion content transitions */
.accordion-content {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

/* Mobile-optimized spacing and layout */
@media (max-width: 640px) {
  /* Ensure minimum touch target size for accordion headers */
  .accordion-section button {
    min-height: 64px;
    padding: 16px 20px;
  }
  
  /* Add ripple effect simulation on touch */
  .accordion-section button:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }
  
  /* Mobile-optimized section spacing */
  .space-y-4 > * + * {
    margin-top: 1rem;
  }
  
  /* Enhanced mobile content padding */
  .accordion-content {
    padding: 16px 20px 24px;
  }
}

/* Desktop enhancements */
@media (min-width: 768px) {
  .accordion-content {
    padding: 24px 32px;
  }
  
  /* Enhanced desktop hover effects */
  .accordion-section button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
  }
  
  .dark .accordion-section button:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
  }
}

/* Badge styling for counts */
.accordion-badge {
  transition: all 0.2s ease;
}

/* Section-specific color themes */
.accordion-section[data-section="overview"] button.expanded {
  background-color: rgb(239 246 255);
  border-color: rgb(191 219 254);
}

.dark .accordion-section[data-section="overview"] button.expanded {
  background-color: rgb(30 58 138 / 0.2);
  border-color: rgb(59 130 246 / 0.3);
}

.accordion-section[data-section="arrows"] button.expanded {
  background-color: rgb(240 253 244);
  border-color: rgb(187 247 208);
}

.dark .accordion-section[data-section="arrows"] button.expanded {
  background-color: rgb(20 83 45 / 0.2);
  border-color: rgb(34 197 94 / 0.3);
}

.accordion-section[data-section="equipment"] button.expanded {
  background-color: rgb(250 245 255);
  border-color: rgb(221 214 254);
}

.dark .accordion-section[data-section="equipment"] button.expanded {
  background-color: rgb(88 28 135 / 0.2);
  border-color: rgb(168 85 247 / 0.3);
}

.accordion-section[data-section="journal"] button.expanded {
  background-color: rgb(238 242 255);
  border-color: rgb(199 210 254);
}

.dark .accordion-section[data-section="journal"] button.expanded {
  background-color: rgb(67 56 202 / 0.2);
  border-color: rgb(129 140 248 / 0.3);
}

.accordion-section[data-section="settings"] button.expanded {
  background-color: rgb(238 242 255);
  border-color: rgb(199 210 254);
}

.dark .accordion-section[data-section="settings"] button.expanded {
  background-color: rgb(67 56 202 / 0.2);
  border-color: rgb(129 140 248 / 0.3);
}
</style>
