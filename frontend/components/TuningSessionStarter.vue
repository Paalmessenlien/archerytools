<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
        Start Enhanced Tuning Session
      </h2>
      <p class="text-gray-600 dark:text-gray-300">
        Select your bow setup and arrow configuration to begin professional tuning analysis
      </p>
    </div>

    <!-- Session Type Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Tuning Test Type
      </label>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="testType in testTypes" 
          :key="testType.id"
          @click="selectedTestType = testType.id"
          class="p-4 border rounded-lg cursor-pointer transition-all duration-200"
          :class="selectedTestType === testType.id 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400' 
            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'"
        >
          <div class="flex items-center justify-center mb-3">
            <component :is="testType.icon" class="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 text-center mb-2">
            {{ testType.name }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-300 text-center">
            {{ testType.description }}
          </p>
          <div class="mt-3">
            <div class="flex items-center text-xs text-gray-500 dark:text-gray-400">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              {{ testType.estimatedTime }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bow Setup Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Select Bow Setup
      </label>
      <div v-if="loading.bowSetups" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600 dark:text-gray-300">Loading bow setups...</span>
      </div>
      <div v-else-if="!bowSetups.length" class="text-center py-8">
        <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
        <p class="text-gray-500 dark:text-gray-400 mb-4">No bow setups found</p>
        <button 
          @click="$router.push('/setups')"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Create Bow Setup
        </button>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="setup in bowSetups" 
          :key="setup.id"
          @click="selectedBowSetup = setup"
          class="p-4 border rounded-lg cursor-pointer transition-all duration-200"
          :class="selectedBowSetup?.id === setup.id 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400' 
            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'"
        >
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {{ setup.name }}
          </h3>
          <div class="space-y-1 text-sm text-gray-600 dark:text-gray-300">
            <div class="flex justify-between">
              <span>Type:</span>
              <span class="font-medium">{{ formatBowType(setup.bow_type) }}</span>
            </div>
            <div class="flex justify-between">
              <span>Draw Weight:</span>
              <span class="font-medium">{{ setup.draw_weight }} lbs</span>
            </div>
            <div class="flex justify-between">
              <span>Draw Length:</span>
              <span class="font-medium">{{ setup.draw_length }}"</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Arrow Selection -->
    <div class="mb-6" v-if="selectedBowSetup">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Select Arrow Configuration
      </label>
      <div v-if="loading.arrows" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600 dark:text-gray-300">Loading arrows...</span>
      </div>
      <div v-else-if="!setupArrows.length" class="text-center py-8">
        <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"></path>
        </svg>
        <p class="text-gray-500 dark:text-gray-400 mb-4">No arrows found for this bow setup</p>
        <button 
          @click="$router.push(`/setups/${selectedBowSetup.id}`)"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Add Arrows to Setup
        </button>
      </div>
      <div v-else class="grid grid-cols-1 gap-3">
        <div 
          v-for="arrow in setupArrows" 
          :key="`${arrow.arrow_id}-${arrow.arrow_length}-${arrow.point_weight}`"
          @click="selectedArrow = arrow"
          class="p-4 border rounded-lg cursor-pointer transition-all duration-200"
          :class="selectedArrow?.arrow_id === arrow.arrow_id && 
                  selectedArrow?.arrow_length === arrow.arrow_length && 
                  selectedArrow?.point_weight === arrow.point_weight
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400' 
            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">
                {{ arrow.manufacturer }} {{ arrow.model_name }}
              </h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600 dark:text-gray-300">
                <div>
                  <span class="font-medium">Length:</span> {{ arrow.arrow_length }}"
                </div>
                <div>
                  <span class="font-medium">Point:</span> {{ arrow.point_weight }} gn
                </div>
                <div>
                  <span class="font-medium">Spine:</span> {{ arrow.spine_value || 'N/A' }}
                </div>
                <div>
                  <span class="font-medium">Total Weight:</span> {{ arrow.total_weight }} gn
                </div>
              </div>
            </div>
            <!-- Tuning History Indicator -->
            <div v-if="arrow.tuning_tests_count > 0" class="ml-4 flex flex-col items-end">
              <div class="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-2 py-1 rounded-full text-xs font-medium">
                {{ arrow.tuning_tests_count }} tests
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Last: {{ formatDate(arrow.last_test_date) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Session Settings -->
    <div class="mb-6" v-if="selectedBowSetup && selectedArrow && selectedTestType">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Session Settings
      </label>
      <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Shooting Distance -->
          <div>
            <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
              Shooting Distance (yards)
            </label>
            <input 
              v-model.number="sessionSettings.shooting_distance"
              type="number"
              step="1"
              min="3"
              max="100"
              class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
            />
          </div>
          <!-- Environmental Conditions Toggle -->
          <div>
            <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
              Record Environmental Conditions
            </label>
            <label class="inline-flex items-center">
              <input 
                v-model="sessionSettings.record_environment"
                type="checkbox"
                class="form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out"
              />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Track temperature, humidity, etc.
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-between">
      <button 
        @click="$emit('cancel')"
        class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
      >
        Cancel
      </button>
      <button 
        @click="startTuningSession"
        :disabled="!canStartSession || starting"
        class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center"
      >
        <div v-if="starting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
        {{ starting ? 'Starting...' : 'Start Tuning Session' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'

// Define test types with icons and metadata
const testTypes = [
  {
    id: 'paper_tuning',
    name: 'Paper Tuning',
    description: 'Analyze arrow tear patterns through paper for spine and clearance issues',
    estimatedTime: '15-20 minutes',
    icon: 'PaperIcon'
  },
  {
    id: 'bareshaft_tuning',
    name: 'Bareshaft Tuning', 
    description: 'Compare bare shaft vs fletched arrow grouping for spine validation',
    estimatedTime: '20-30 minutes',
    icon: 'TargetIcon'
  },
  {
    id: 'walkback_tuning',
    name: 'Walkback Tuning',
    description: 'Multi-distance shooting analysis for rest/centershot alignment',
    estimatedTime: '25-35 minutes',
    icon: 'ChartIcon'
  }
]

// Reactive data
const selectedTestType = ref('')
const selectedBowSetup = ref(null)
const selectedArrow = ref(null)
const bowSetups = ref([])
const setupArrows = ref([])
const starting = ref(false)

const loading = ref({
  bowSetups: false,
  arrows: false
})

const sessionSettings = ref({
  shooting_distance: 20,
  record_environment: true
})

// API composable
const api = useApi()

// Computed properties
const canStartSession = computed(() => {
  return selectedTestType.value && selectedBowSetup.value && selectedArrow.value
})

// Methods
const loadBowSetups = async () => {
  loading.value.bowSetups = true
  try {
    const response = await api.get('/bow-setups')
    bowSetups.value = response.setups || []
  } catch (error) {
    console.error('Failed to load bow setups:', error)
    // Could add notification here
  } finally {
    loading.value.bowSetups = false
  }
}

const loadArrowsForSetup = async () => {
  if (!selectedBowSetup.value?.id) return
  
  loading.value.arrows = true
  try {
    const response = await api.get(`/bow-setups/${selectedBowSetup.value.id}/arrows`)
    setupArrows.value = response.arrows || []
    
    // Reset arrow selection when setup changes
    selectedArrow.value = null
  } catch (error) {
    console.error('Failed to load arrows for setup:', error)
    setupArrows.value = []
  } finally {
    loading.value.arrows = false
  }
}

const startTuningSession = async () => {
  if (!canStartSession.value) return
  
  starting.value = true
  try {
    const sessionData = {
      bow_setup_id: selectedBowSetup.value.id,
      arrow_id: selectedArrow.value.arrow_id,
      arrow_length: selectedArrow.value.arrow_length,
      point_weight: selectedArrow.value.point_weight,
      guide_type: selectedTestType.value
    }
    
    const response = await api.post('/tuning-guides/start', sessionData)
    
    // Emit success event with session details
    emit('session-started', {
      session_id: response.session_id,
      guide_type: response.guide_type,
      bow_setup: selectedBowSetup.value,
      arrow: selectedArrow.value,
      settings: sessionSettings.value
    })
    
  } catch (error) {
    console.error('Failed to start tuning session:', error)
    // Could add notification here
  } finally {
    starting.value = false
  }
}

// Format utility functions
const formatBowType = (bowType) => {
  const types = {
    'compound': 'Compound',
    'recurve': 'Recurve', 
    'traditional': 'Traditional',
    'barebow': 'Barebow'
  }
  return types[bowType] || bowType
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'N/A'
  }
}

// Watchers
watch(selectedBowSetup, () => {
  if (selectedBowSetup.value) {
    loadArrowsForSetup()
  } else {
    setupArrows.value = []
    selectedArrow.value = null
  }
})

// Define emits
const emit = defineEmits(['session-started', 'cancel'])

// Component Icons (placeholder SVG components)
const PaperIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z">
      </path>
    </svg>
  `
}

const TargetIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 4a6 6 0 100 12 6 6 0 000-12zm0 2a4 4 0 100 8 4 4 0 000-8z">
      </path>
    </svg>
  `
}

const ChartIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z">
      </path>
    </svg>
  `
}

// Lifecycle
onMounted(() => {
  loadBowSetups()
})
</script>

<style scoped>
.form-checkbox {
  @apply rounded border-gray-300 dark:border-gray-600 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 dark:bg-gray-700 dark:focus:ring-blue-600 dark:focus:ring-opacity-50;
}
</style>