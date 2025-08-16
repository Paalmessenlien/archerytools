<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="container mx-auto px-4 py-8">
      <div class="animate-pulse">
        <!-- Breadcrumb skeleton -->
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-64 mb-6"></div>
        
        <!-- Header skeleton -->
        <div class="mb-8">
          <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-96 mb-4"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48"></div>
        </div>
        
        <!-- Content skeleton -->
        <div class="space-y-6">
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4"></div>
            <div class="space-y-3">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="container mx-auto px-4 py-8">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <i class="fas fa-exclamation-triangle text-4xl text-red-600 dark:text-red-400 mb-4"></i>
        <h2 class="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">Arrow Setup Not Found</h2>
        <p class="text-red-600 dark:text-red-400 mb-4">{{ error }}</p>
        <div class="flex justify-center space-x-3">
          <button
            @click="$router.go(-1)"
            class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            Go Back
          </button>
          <NuxtLink
            to="/my-setup"
            class="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <i class="fas fa-list mr-2"></i>
            My Setups
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="setupArrowData" class="container mx-auto px-3 sm:px-4 py-4 sm:py-8 max-w-7xl">
      <!-- Breadcrumb Navigation -->
      <SetupContextBreadcrumb
        :bow-setup="setupArrowData.bow_setup"
        :arrow-name="getArrowDisplayName()"
        class="mb-6"
      />

      <!-- Header -->
      <div class="space-y-6 mb-8">
        <!-- Title and Info -->
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
            {{ getArrowDisplayName() }}
          </h1>
          <p class="text-lg text-gray-600 dark:text-gray-400 mt-2">
            {{ setupArrowData.arrow?.material || 'Unknown Material' }} Arrow in {{ setupArrowData.bow_setup.name }}
          </p>
          
          <!-- Quick Stats Pills -->
          <div class="flex flex-wrap items-center gap-3 mt-4">
            <div class="flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-sm">
              <i class="fas fa-ruler-horizontal mr-2"></i>
              {{ setupArrowData.setup_arrow.arrow_length }}" length
            </div>
            <div class="flex items-center px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full text-sm">
              <i class="fas fa-bullseye mr-2"></i>
              {{ setupArrowData.setup_arrow.point_weight }} gr point
            </div>
            <div class="flex items-center px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 rounded-full text-sm">
              <i class="fas fa-balance-scale mr-2"></i>
              {{ calculateTotalWeight() }} gr total
            </div>
            <div v-if="setupArrowData.setup_arrow.compatibility_score" 
                 class="flex items-center px-3 py-1 rounded-full text-sm"
                 :class="getCompatibilityClass(setupArrowData.setup_arrow.compatibility_score)">
              <i class="fas fa-star mr-2"></i>
              {{ setupArrowData.setup_arrow.compatibility_score }}% match
            </div>
          </div>
        </div>
        
        <!-- Actions - Mobile Responsive -->
        <div class="flex flex-col sm:flex-row gap-3">
          <button
            @click="editMode = !editMode"
            class="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors w-full sm:w-auto"
          >
            <i :class="editMode ? 'fas fa-eye' : 'fas fa-edit'" class="mr-2"></i>
            {{ editMode ? 'View Mode' : 'Edit Setup' }}
          </button>
          <button
            @click="duplicateArrow"
            class="inline-flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors w-full sm:w-auto"
          >
            <i class="fas fa-copy mr-2"></i>
            Duplicate
          </button>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
        <!-- Left Column: Arrow Configuration -->
        <div class="lg:col-span-2 space-y-4 sm:space-y-6">
          <!-- Arrow Setup Configuration -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
                <i class="fas fa-cog mr-3 text-blue-600"></i>
                Arrow Configuration
              </h2>
              <div v-if="hasUnsavedChanges" class="flex items-center text-amber-600 dark:text-amber-400 text-sm">
                <i class="fas fa-exclamation-circle mr-1"></i>
                Unsaved changes
              </div>
            </div>
            
            <ArrowSetupEditor
              v-if="editMode"
              :setup-arrow="setupArrowData.setup_arrow"
              :arrow="setupArrowData.arrow"
              :spine-specifications="setupArrowData.spine_specifications"
              :bow-config="setupArrowData.bow_setup"
              @update="handleConfigUpdate"
              @save="handleConfigSave"
              @cancel="handleConfigCancel"
              class="space-y-4"
            />
            
            <ArrowSetupDisplay
              v-else
              :setup-arrow="setupArrowData.setup_arrow"
              :arrow="setupArrowData.arrow"
              :spine-specifications="setupArrowData.spine_specifications"
              class="space-y-4"
            />
          </div>

          <!-- Performance Analysis -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <ArrowPerformanceAnalysis
              :setup-arrow="setupArrowData.setup_arrow"
              :bow-config="setupArrowData.bow_setup"
              :arrow="setupArrowData.arrow"
              @performance-updated="handlePerformanceUpdate"
            />
          </div>

          <!-- Chronograph Data -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <ChronographDataEntry
              :bow-setup-id="setupArrowData.bow_setup.id"
              :current-setup-arrow="setupArrowData.setup_arrow"
              :current-arrow="setupArrowData.arrow"
              @data-updated="handleChronographDataUpdate"
              @speed-calculated="handleSpeedCalculated"
            />
          </div>
        </div>

        <!-- Right Column: Arrow Information -->
        <div class="space-y-4 sm:space-y-6">
          <!-- Arrow Database Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-database mr-2 text-green-600"></i>
              Arrow Information
            </h3>
            
            <ArrowDatabaseInfo
              :arrow="setupArrowData.arrow"
              :spine-specifications="setupArrowData.spine_specifications"
            />
          </div>

          <!-- Setup Context -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-crosshairs mr-2 text-orange-600"></i>
              Bow Setup Context
            </h3>
            
            <BowSetupContext
              :bow-setup="setupArrowData.bow_setup"
              @edit-bow="navigateToBowSetup"
            />
          </div>

          <!-- Quick Actions -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-bolt mr-2 text-yellow-600"></i>
              Quick Actions
            </h3>
            
            <div class="space-y-3">
              <button
                @click="calculatePerformance"
                :disabled="calculatingPerformance"
                class="w-full inline-flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-400 transition-colors"
              >
                <i :class="calculatingPerformance ? 'fas fa-spinner fa-spin' : 'fas fa-calculator'" class="mr-2"></i>
                {{ calculatingPerformance ? 'Calculating...' : 'Recalculate Performance' }}
              </button>
              
              <button
                @click="viewInDatabase"
                class="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <i class="fas fa-external-link-alt mr-2"></i>
                View in Database
              </button>
              
              <button
                @click="addToCalculator"
                class="w-full inline-flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <i class="fas fa-plus mr-2"></i>
                Add to Calculator
              </button>
              
              <button
                @click="removeArrow"
                class="w-full inline-flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <i class="fas fa-trash mr-2"></i>
                Remove from Setup
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <ConfirmationModal
      v-if="showConfirmModal"
      :title="confirmModal.title"
      :message="confirmModal.message"
      :confirm-text="confirmModal.confirmText"
      :cancel-text="confirmModal.cancelText"
      @confirm="confirmModal.onConfirm"
      @cancel="showConfirmModal = false"
    />

    <!-- Notification Toast -->
    <NotificationToast
      v-if="notification.show"
      :message="notification.message"
      :type="notification.type"
      @close="hideNotification"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter, useHead, onBeforeRouteLeave } from '#imports'
import { useApi } from '~/composables/useApi'
import SetupContextBreadcrumb from '~/components/SetupContextBreadcrumb.vue'
import ArrowSetupEditor from '~/components/ArrowSetupEditor.vue'
import ArrowSetupDisplay from '~/components/ArrowSetupDisplay.vue'
import ArrowPerformanceAnalysis from '~/components/ArrowPerformanceAnalysis.vue'
import ArrowDatabaseInfo from '~/components/ArrowDatabaseInfo.vue'
import BowSetupContext from '~/components/BowSetupContext.vue'
import ChronographDataEntry from '~/components/ChronographDataEntry.vue'
import ConfirmationModal from '~/components/ConfirmationModal.vue'
import NotificationToast from '~/components/NotificationToast.vue'

// Meta information
definePageMeta({
  title: 'Arrow Setup Details'
})

// Composables
const route = useRoute()
const router = useRouter()
const api = useApi()

// State
const setupArrowData = ref(null)
const loading = ref(true)
const error = ref('')
const editMode = ref(false)
const hasUnsavedChanges = ref(false)
const calculatingPerformance = ref(false)

// Modal state
const showConfirmModal = ref(false)
const confirmModal = ref({
  title: '',
  message: '',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  onConfirm: () => {}
})

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Computed
const setupArrowId = computed(() => route.params.id)

// Methods
const loadSetupArrowDetails = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await api.get(`/setup-arrows/${setupArrowId.value}/details`)
    setupArrowData.value = response
    
    // Update page title
    const arrowName = getArrowDisplayName()
    useHead({
      title: `${arrowName} - Arrow Setup Details`,
      meta: [
        { 
          name: 'description', 
          content: `Detailed configuration and performance analysis for ${arrowName} in bow setup.` 
        }
      ]
    })
    
  } catch (err) {
    console.error('Error loading arrow setup details:', err)
    error.value = err.message || 'Failed to load arrow setup details'
  } finally {
    loading.value = false
  }
}

const getArrowDisplayName = () => {
  if (!setupArrowData.value) return 'Arrow Setup'
  
  const arrow = setupArrowData.value.arrow
  if (arrow) {
    return `${arrow.manufacturer} ${arrow.model_name}`
  }
  
  return `Arrow ${setupArrowData.value.setup_arrow.arrow_id}`
}

const calculateTotalWeight = () => {
  if (!setupArrowData.value) return 0
  
  const setup = setupArrowData.value.setup_arrow
  const arrow = setupArrowData.value.arrow
  
  // Calculate shaft weight using GPI
  let shaftWeight = 0
  if (arrow?.spine_specifications?.length > 0) {
    const spineSpec = arrow.spine_specifications.find(spec => 
      spec.spine.toString() === setup.calculated_spine?.toString()
    ) || arrow.spine_specifications[0]
    
    if (spineSpec?.gpi_weight) {
      shaftWeight = spineSpec.gpi_weight * (setup.arrow_length || 32)
    }
  }
  
  // Add component weights
  const pointWeight = setup.point_weight || 0
  const nockWeight = setup.nock_weight || 10
  const insertWeight = setup.insert_weight || 0
  const bushingWeight = setup.bushing_weight || 0
  const fletchingWeight = setup.fletching_weight || 15
  
  const totalWeight = shaftWeight + pointWeight + nockWeight + insertWeight + bushingWeight + fletchingWeight
  
  return Math.round(totalWeight * 10) / 10
}

const getCompatibilityClass = (score) => {
  if (score >= 90) {
    return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
  } else if (score >= 70) {
    return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
  } else {
    return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
  }
}

// Event handlers
const handleConfigUpdate = (updatedConfig) => {
  hasUnsavedChanges.value = true
  // Update local state for real-time preview
  setupArrowData.value.setup_arrow = { ...setupArrowData.value.setup_arrow, ...updatedConfig }
}

const handleConfigSave = async (updatedConfig) => {
  try {
    await api.put(`/setup-arrows/${setupArrowId.value}`, updatedConfig)
    hasUnsavedChanges.value = false
    editMode.value = false
    showNotification('Arrow configuration updated successfully', 'success')
    await loadSetupArrowDetails() // Reload to get fresh data
  } catch (err) {
    console.error('Error saving configuration:', err)
    showNotification('Failed to save configuration', 'error')
  }
}

const handleConfigCancel = () => {
  if (hasUnsavedChanges.value) {
    confirmModal.value = {
      title: 'Discard Changes?',
      message: 'You have unsaved changes. Are you sure you want to cancel editing?',
      confirmText: 'Discard',
      cancelText: 'Keep Editing',
      onConfirm: () => {
        hasUnsavedChanges.value = false
        editMode.value = false
        showConfirmModal.value = false
        loadSetupArrowDetails() // Reload original data
      }
    }
    showConfirmModal.value = true
  } else {
    editMode.value = false
  }
}

const handlePerformanceUpdate = (performanceData) => {
  if (setupArrowData.value) {
    setupArrowData.value.setup_arrow.performance = performanceData
  }
}

const handleChronographDataUpdate = (data) => {
  console.log('Chronograph data updated:', data)
  // Optionally reload performance data when chronograph data changes
  if (setupArrowData.value) {
    loadSetupArrowDetails()
  }
}

const handleSpeedCalculated = (speedData) => {
  console.log('Speed calculated from chronograph:', speedData)
  showNotification(`Speed updated: ${speedData.speed} FPS for ${speedData.arrow_weight}gr arrow`, 'success')
}

const calculatePerformance = async () => {
  try {
    calculatingPerformance.value = true
    await api.post(`/setup-arrows/${setupArrowId.value}/calculate-performance`, {
      bow_config: setupArrowData.value.bow_setup
    })
    await loadSetupArrowDetails() // Reload to get performance data
    showNotification('Performance calculated successfully', 'success')
  } catch (err) {
    console.error('Error calculating performance:', err)
    showNotification('Failed to calculate performance', 'error')
  } finally {
    calculatingPerformance.value = false
  }
}

const duplicateArrow = () => {
  confirmModal.value = {
    title: 'Duplicate Arrow?',
    message: 'This will create a copy of this arrow setup that you can modify independently.',
    confirmText: 'Duplicate',
    cancelText: 'Cancel',
    onConfirm: async () => {
      try {
        const setup = setupArrowData.value.setup_arrow
        const duplicateData = {
          arrow_id: setup.arrow_id,
          arrow_length: setup.arrow_length,
          point_weight: setup.point_weight,
          calculated_spine: setup.calculated_spine,
          notes: `Copy of: ${setup.notes || 'arrow setup'}`,
          nock_weight: setup.nock_weight,
          insert_weight: setup.insert_weight,
          bushing_weight: setup.bushing_weight,
          fletching_weight: setup.fletching_weight,
          compatibility_score: setup.compatibility_score,
          allow_duplicate: true
        }
        
        await api.post(`/bow-setups/${setup.setup_id}/arrows`, duplicateData)
        showNotification('Arrow duplicated successfully', 'success')
        showConfirmModal.value = false
      } catch (err) {
        console.error('Error duplicating arrow:', err)
        showNotification('Failed to duplicate arrow', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const removeArrow = () => {
  confirmModal.value = {
    title: 'Remove Arrow?',
    message: 'This will permanently remove this arrow from your bow setup. This action cannot be undone.',
    confirmText: 'Remove',
    cancelText: 'Cancel',
    onConfirm: async () => {
      try {
        await api.delete(`/setup-arrows/${setupArrowId.value}`)
        showNotification('Arrow removed successfully', 'success')
        showConfirmModal.value = false
        // Navigate back to bow setup
        router.push(`/setups/${setupArrowData.value.setup_arrow.setup_id}?tab=arrows`)
      } catch (err) {
        console.error('Error removing arrow:', err)
        showNotification('Failed to remove arrow', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const viewInDatabase = () => {
  if (setupArrowData.value?.setup_arrow?.arrow_id) {
    router.push(`/arrows/${setupArrowData.value.setup_arrow.arrow_id}`)
  }
}

const addToCalculator = () => {
  const bow = setupArrowData.value.bow_setup
  router.push({
    path: '/calculator',
    query: {
      draw_weight: bow.draw_weight,
      draw_length: bow.draw_length,
      bow_type: bow.bow_type,
      ibo_speed: bow.ibo_speed,
      let_off: bow.let_off_percentage
    }
  })
}

const navigateToBowSetup = () => {
  router.push(`/setups/${setupArrowData.value.setup_arrow.setup_id}`)
}

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

// Lifecycle
onMounted(() => {
  if (setupArrowId.value) {
    loadSetupArrowDetails()
  }
})

// Watch for route changes
watch(() => setupArrowId.value, (newId) => {
  if (newId) {
    loadSetupArrowDetails()
  }
})

// Warn about unsaved changes when leaving
onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    const leave = confirm('You have unsaved changes. Are you sure you want to leave?')
    if (leave) {
      next()
    } else {
      next(false)
    }
  } else {
    next()
  }
})
</script>