<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          <i class="fas fa-history mr-3 text-blue-600 dark:text-blue-400"></i>
          Change History
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Track all modifications to your bow setups, arrows, and equipment over time.
        </p>
        
        <!-- View Toggle -->
        <div class="mt-4 flex items-center space-x-4">
          <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              @click="viewMode = 'setup-specific'"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-md transition-colors',
                viewMode === 'setup-specific'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              ]"
            >
              <i class="fas fa-crosshairs mr-2"></i>
              By Setup
            </button>
            <button
              @click="viewMode = 'global'"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-md transition-colors',
                viewMode === 'global'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              ]"
            >
              <i class="fas fa-globe mr-2"></i>
              All Activities
            </button>
          </div>
        </div>
      </div>

      <!-- Bow Setup Selector -->
      <div v-if="viewMode === 'setup-specific'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-6">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            <i class="fas fa-crosshairs mr-2 text-green-600 dark:text-green-400"></i>
            Select Bow Setup
          </h2>
          
          <!-- Setup Selection -->
          <div v-if="bowSetups.length > 0" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="setup in bowSetups"
                :key="setup.id"
                @click="selectBowSetup(setup)"
                :class="[
                  'p-4 rounded-lg border-2 cursor-pointer transition-all',
                  selectedSetup?.id === setup.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                ]"
              >
                <div class="flex items-center justify-between mb-2">
                  <h3 class="font-medium text-gray-900 dark:text-gray-100">{{ setup.name }}</h3>
                  <span class="text-xs text-gray-500 dark:text-gray-400">{{ setup.bow_type }}</span>
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  {{ setup.draw_weight }}# @ 28"
                </div>
                <div v-if="setup.description" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ setup.description }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- No setups message -->
          <div v-else-if="!loadingSetups" class="text-center py-8">
            <i class="fas fa-crosshairs text-4xl text-gray-400 mb-4"></i>
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Bow Setups Found</h3>
            <p class="text-gray-600 dark:text-gray-400 mb-4">Create a bow setup to start tracking changes.</p>
            <NuxtLink
              to="/"
              class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <i class="fas fa-plus mr-2"></i>
              Create Your First Setup
            </NuxtLink>
          </div>
          
          <!-- Loading state -->
          <div v-else class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-3"></div>
            <p class="text-gray-600 dark:text-gray-400">Loading bow setups...</p>
          </div>
        </div>
      </div>

      <!-- Global Activity View -->
      <div v-if="viewMode === 'global'" class="space-y-6">
        <!-- Global Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <i class="fas fa-chart-line text-blue-600 dark:text-blue-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Activities</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ globalStatistics.total_activities || 0 }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <i class="fas fa-crosshairs text-green-600 dark:text-green-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Bow Setups</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ globalStatistics.setup_count || 0 }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <i class="fas fa-clock text-purple-600 dark:text-purple-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Last 30 Days</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ globalStatistics.recent_activities || 0 }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <i class="fas fa-cogs text-orange-600 dark:text-orange-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Active Setups</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ globalStatistics.active_setups || 0 }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Global Activity Timeline -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div class="p-6">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-timeline mr-2 text-purple-600 dark:text-purple-400"></i>
              All User Activities
            </h2>
            <GlobalChangeLogViewer
              @statistics-updated="handleGlobalStatisticsUpdate"
              @error="handleError"
            />
          </div>
        </div>
      </div>

      <!-- Change History Content -->
      <div v-if="viewMode === 'setup-specific' && selectedSetup" class="space-y-6">
        <!-- Statistics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <i class="fas fa-chart-line text-blue-600 dark:text-blue-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Changes</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ statistics.total_changes || 0 }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <i class="fas fa-clock text-green-600 dark:text-green-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Last 30 Days</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ statistics.changes_last_30_days || 0 }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <i class="fas fa-bullseye text-red-600 dark:text-red-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Arrow Changes</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ getArrowChangesCount() }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <i class="fas fa-cogs text-purple-600 dark:text-purple-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Equipment Changes</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ getEquipmentChangesCount() }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Enhanced Change History Viewer -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div class="p-6">
            <EnhancedChangeLogViewer
              :bow-setup-id="selectedSetup.id"
              :show-header="false"
              @statistics-updated="handleStatisticsUpdate"
              @error="handleError"
            />
          </div>
        </div>
      </div>

      <!-- Welcome Message -->
      <div v-else-if="viewMode === 'setup-specific' && bowSetups.length > 0" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 text-center">
        <i class="fas fa-arrow-up text-4xl text-blue-600 dark:text-blue-400 mb-4"></i>
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Select a Bow Setup</h3>
        <p class="text-gray-600 dark:text-gray-400">
          Choose a bow setup above to view its complete change history including arrows, equipment, and setup modifications.
        </p>
      </div>
    </div>

    <!-- Error Toast -->
    <div
      v-if="error"
      class="fixed bottom-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50"
    >
      <div class="flex items-center">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        {{ error }}
        <button @click="error = ''" class="ml-4 text-red-200 hover:text-white">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useApi } from '@/composables/useApi'
import EnhancedChangeLogViewer from '@/components/EnhancedChangeLogViewer.vue'
import GlobalChangeLogViewer from '@/components/GlobalChangeLogViewer.vue'

// Meta information
definePageMeta({
  title: 'Change History',
  middleware: ['auth-check']
})

// Composables
const api = useApi()

// State
const bowSetups = ref([])
const selectedSetup = ref(null)
const loadingSetups = ref(true)
const statistics = ref({})
const globalStatistics = ref({})
const error = ref('')
const viewMode = ref('setup-specific')

// Methods
const loadBowSetups = async () => {
  try {
    loadingSetups.value = true
    
    // Load bow setups and active setup in parallel
    const [setupsResponse, activeSetupResponse] = await Promise.all([
      api.get('/bow-setups'),
      api.get('/user/active-bow-setup').catch(() => ({ active_bow_setup: null }))
    ])
    
    bowSetups.value = setupsResponse.setups || []
    
    // Auto-select the active bow setup if it exists
    const activeBowSetup = activeSetupResponse.active_bow_setup
    if (activeBowSetup && bowSetups.value.length > 0) {
      const activeSetup = bowSetups.value.find(setup => setup.id === activeBowSetup.id)
      if (activeSetup) {
        selectedSetup.value = activeSetup
        await loadStatistics()
      }
    }
  } catch (err) {
    console.error('Error loading bow setups:', err)
    error.value = 'Failed to load bow setups'
  } finally {
    loadingSetups.value = false
  }
}

const selectBowSetup = async (setup) => {
  selectedSetup.value = setup
  await loadStatistics()
}

const setActiveSetup = async (setup) => {
  try {
    await api.put('/user/active-bow-setup', { bow_setup_id: setup.id })
    // Visual feedback could be added here
    console.log(`Set ${setup.name} as active bow setup`)
  } catch (err) {
    console.error('Error setting active bow setup:', err)
    error.value = 'Failed to set active bow setup'
  }
}

const loadStatistics = async () => {
  if (!selectedSetup.value) return
  
  try {
    const response = await api.get(`/bow-setups/${selectedSetup.value.id}/change-log/statistics`)
    statistics.value = response
  } catch (err) {
    console.error('Error loading statistics:', err)
    error.value = 'Failed to load change statistics'
  }
}

const loadGlobalStatistics = async () => {
  try {
    const response = await api.get('/change-log/global-statistics')
    globalStatistics.value = response
  } catch (err) {
    console.error('Error loading global statistics:', err)
    error.value = 'Failed to load global statistics'
  }
}

const handleStatisticsUpdate = (newStats) => {
  statistics.value = { ...statistics.value, ...newStats }
}

const handleGlobalStatisticsUpdate = (newStats) => {
  globalStatistics.value = { ...globalStatistics.value, ...newStats }
}

const handleError = (message) => {
  error.value = message
}

const getArrowChangesCount = () => {
  const arrowChanges = statistics.value.arrow_changes_by_type || {}
  return Object.values(arrowChanges).reduce((sum, count) => sum + count, 0)
}

const getEquipmentChangesCount = () => {
  const equipmentChanges = statistics.value.equipment_changes_by_type || {}
  return Object.values(equipmentChanges).reduce((sum, count) => sum + count, 0)
}

// Watch for view mode changes
watch(viewMode, (newMode) => {
  if (newMode === 'global') {
    loadGlobalStatistics()
  }
})

// Lifecycle
onMounted(() => {
  loadBowSetups()
  // Load global statistics if starting in global mode
  if (viewMode.value === 'global') {
    loadGlobalStatistics()
  }
})
</script>

<style scoped>
/* Additional custom styles if needed */
.change-card {
  transition: all 0.2s ease-in-out;
}

.change-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>