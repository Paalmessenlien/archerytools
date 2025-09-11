<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Header -->
    <div class="mb-8">
      <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
        Interactive Tuning & Equipment Setup
      </h2>
      <p class="text-gray-600 dark:text-gray-300">
        Select your bow setup, then choose arrows for guided tuning or equipment for journal documentation
      </p>
    </div>

    <!-- Step 1: Bow Setup Selection -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full text-sm font-medium mr-3">
          1
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          Select Bow Setup
        </h3>
      </div>

      <div v-if="loading.bowSetups" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600 dark:text-gray-300">Loading bow setups...</span>
      </div>

      <div v-else-if="!bowSetups.length" class="text-center py-8">
        <i class="fas fa-bow-arrow text-gray-400 text-4xl mb-4"></i>
        <p class="text-gray-500 dark:text-gray-400 mb-4">No bow setups found</p>
        <button 
          @click="$router.push('/setups')"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Create Bow Setup
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
          v-for="setup in bowSetups" 
          :key="setup.id"
          @click="selectBowSetup(setup)"
          class="p-4 border rounded-lg cursor-pointer transition-all duration-200"
          :class="selectedBowSetup?.id === setup.id 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400' 
            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'"
        >
          <div class="flex items-center mb-3">
            <i class="fas fa-crosshairs text-blue-600 dark:text-blue-400 mr-2"></i>
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              {{ setup.name }}
            </h3>
          </div>
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

    <!-- Step 2: Arrow or Equipment Selection -->
    <div v-if="selectedBowSetup" class="mb-8">
      <div class="flex items-center mb-4">
        <div class="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full text-sm font-medium mr-3">
          2
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          Choose Tuning Type
        </h3>
      </div>

      <!-- Selection Toggle -->
      <div class="mb-6">
        <div class="bg-gray-100 dark:bg-gray-700 p-1 rounded-lg inline-flex">
          <button
            @click="selectionType = 'arrow'"
            class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
            :class="selectionType === 'arrow' 
              ? 'bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 shadow-sm' 
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'"
          >
            <i class="fas fa-bullseye mr-2"></i>
            Arrow Tuning
          </button>
          <button
            @click="selectionType = 'equipment'"
            class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
            :class="selectionType === 'equipment' 
              ? 'bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 shadow-sm' 
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'"
          >
            <i class="fas fa-tools mr-2"></i>
            Equipment Setup
          </button>
        </div>
      </div>

      <!-- Arrow Selection -->
      <div v-if="selectionType === 'arrow'">
        <div class="mb-4">
          <h4 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-2">
            Select Arrow Configuration
          </h4>
          <p class="text-sm text-gray-600 dark:text-gray-300">
            Choose an arrow to access interactive tuning guides (paper, bareshaft, walkback)
          </p>
        </div>

        <div v-if="loading.arrows" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600 dark:text-gray-300">Loading arrows...</span>
        </div>

        <div v-else-if="!setupArrows.length" class="text-center py-8">
          <i class="fas fa-arrows-alt text-gray-400 text-4xl mb-4"></i>
          <p class="text-gray-500 dark:text-gray-400 mb-4">No arrows found for this bow setup</p>
          <button 
            @click="$router.push(`/setups/${selectedBowSetup.id}`)"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Add Arrows to Setup
          </button>
        </div>

        <div v-else class="space-y-3">
          <div 
            v-for="arrowSetup in setupArrows" 
            :key="`${arrowSetup.arrow_id}-${arrowSetup.arrow_length}-${arrowSetup.point_weight}`"
            @click="selectArrow(arrowSetup)"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
            :class="selectedArrow?.arrow_id === arrowSetup.arrow_id && 
                    selectedArrow?.arrow_length === arrowSetup.arrow_length && 
                    selectedArrow?.point_weight === arrowSetup.point_weight
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400' 
              : 'border-gray-200 dark:border-gray-700'"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1 min-w-0">
                <!-- Arrow Header -->
                <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-2 mb-2">
                  <div class="flex items-center space-x-2">
                    <h5 class="mobile-heading-4 md:text-base font-medium text-gray-900 dark:text-gray-100">
                      {{ arrowSetup.arrow?.manufacturer || arrowSetup.manufacturer || 'Unknown Manufacturer' }}
                    </h5>
                    <!-- Orphaned Arrow Warning -->
                    <span v-if="!arrowSetup.arrow && !arrowSetup.manufacturer" class="px-2 py-1 text-xs bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300 rounded-full">
                      <i class="fas fa-exclamation-triangle mr-1"></i>
                      Orphaned
                    </span>
                  </div>
                  <span class="hidden sm:inline text-gray-400">•</span>
                  <span class="mobile-body-small md:text-sm text-gray-700 dark:text-gray-300">
                    {{ arrowSetup.arrow?.model_name || arrowSetup.model_name || `Arrow ID: ${arrowSetup.arrow_id}` }}
                  </span>
                </div>
                
                <!-- Arrow Specifications - Simplified for mobile -->
                <div class="mb-3">
                  <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm">
                    <!-- Mobile: Single column with essential specs -->
                    <div class="sm:hidden space-y-1">
                      <div class="text-gray-700 dark:text-gray-300">
                        Spine: <span class="font-medium text-gray-900 dark:text-gray-100">{{ getDisplaySpine(arrowSetup) }}</span> • 
                        Length: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.arrow_length }}"</span> • 
                        Point: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.point_weight }} gr</span>
                      </div>
                    </div>
                    
                    <!-- Desktop: Multi-column with icons -->
                    <div class="hidden sm:flex items-center space-x-2">
                      <i class="fas fa-ruler-horizontal text-indigo-600 dark:text-indigo-400"></i>
                      <span class="text-gray-700 dark:text-gray-300">Spine: <span class="font-medium text-gray-900 dark:text-gray-100">{{ getDisplaySpine(arrowSetup) }}</span></span>
                    </div>
                    
                    <div class="hidden sm:flex items-center space-x-2">
                      <i class="fas fa-arrows-alt-h text-green-600 dark:text-green-400"></i>
                      <span class="text-gray-700 dark:text-gray-300">Length: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.arrow_length }}"</span></span>
                    </div>
                    
                    <div class="hidden sm:flex items-center space-x-2">
                      <i class="fas fa-bullseye text-red-600 dark:text-red-400"></i>
                      <span class="text-gray-700 dark:text-gray-300">Point: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.point_weight }} gr</span></span>
                    </div>
                  </div>
                  
                  <!-- Essential Weight Info Only -->
                  <div v-if="calculateTotalArrowWeight(arrowSetup)" class="text-sm pt-2 border-t border-gray-200 dark:border-gray-700">
                    <div class="flex items-center space-x-2 bg-purple-50 dark:bg-purple-900/30 px-3 py-1 rounded">
                      <i class="fas fa-balance-scale text-purple-600 dark:text-purple-400"></i>
                      <span class="text-purple-800 dark:text-purple-200">Total Weight: <span class="font-medium">{{ calculateTotalArrowWeight(arrowSetup) }} gr</span></span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Tuning History Indicator -->
              <div v-if="arrowSetup.tuning_tests_count > 0" class="ml-4 flex flex-col items-end">
                <div class="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-2 py-1 rounded-full text-xs font-medium">
                  {{ arrowSetup.tuning_tests_count }} tests
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Last: {{ formatDate(arrowSetup.last_test_date) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Equipment Selection -->
      <div v-else-if="selectionType === 'equipment'">
        <div class="mb-4">
          <h4 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-2">
            Select Equipment Category
          </h4>
          <p class="text-sm text-gray-600 dark:text-gray-300">
            Choose equipment to create tuning documentation in your journal
          </p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div 
            v-for="category in equipmentCategories" 
            :key="category.name"
            @click="selectEquipmentCategory(category)"
            class="p-4 border rounded-lg cursor-pointer transition-all duration-200 text-center"
            :class="selectedEquipmentCategory?.name === category.name 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400' 
              : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'"
          >
            <div class="flex justify-center mb-3">
              <i :class="`${category.icon} text-2xl ${category.color}`"></i>
            </div>
            <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-1">
              {{ category.label }}
            </h5>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ category.description }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Available Options -->
    <div v-if="selectedBowSetup && ((selectionType === 'arrow' && selectedArrow) || (selectionType === 'equipment' && selectedEquipmentCategory))" class="mb-8">
      <div class="flex items-center mb-4">
        <div class="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full text-sm font-medium mr-3">
          3
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          {{ selectionType === 'arrow' ? 'Available Tuning Guides' : 'Equipment Setup Options' }}
        </h3>
      </div>

      <!-- Arrow Tuning Guides -->
      <div v-if="selectionType === 'arrow'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="guide in availableTuningGuides" 
          :key="guide.id"
          @click="startTuningGuide(guide)"
          class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer transition-all duration-200 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md"
        >
          <div class="flex items-center justify-center mb-3">
            <i :class="`${guide.icon} text-3xl ${guide.color}`"></i>
          </div>
          <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 text-center mb-2">
            {{ guide.name }}
          </h4>
          <p class="text-sm text-gray-600 dark:text-gray-300 text-center mb-3">
            {{ guide.description }}
          </p>
          <div class="flex items-center justify-center text-xs text-gray-500 dark:text-gray-400">
            <i class="fas fa-clock mr-1"></i>
            {{ guide.estimatedTime }}
          </div>
        </div>
      </div>

      <!-- Equipment Setup Options -->
      <div v-else-if="selectionType === 'equipment'" class="space-y-4">
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div class="flex items-start space-x-3">
            <i :class="`${selectedEquipmentCategory.icon} text-2xl ${selectedEquipmentCategory.color} mt-1`"></i>
            <div class="flex-1">
              <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                {{ selectedEquipmentCategory.label }} Setup Documentation
              </h4>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
                Create a detailed journal entry to document your {{ selectedEquipmentCategory.label.toLowerCase() }} setup process, adjustments, and observations.
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                  <h5 class="text-sm font-medium text-gray-800 dark:text-gray-200">
                    Documentation includes:
                  </h5>
                  <ul class="text-xs text-gray-600 dark:text-gray-300 space-y-1">
                    <li v-for="item in selectedEquipmentCategory.documentationItems" :key="item" class="flex items-center">
                      <i class="fas fa-check-circle text-green-500 mr-2 text-xs"></i>
                      {{ item }}
                    </li>
                  </ul>
                </div>
                <div class="space-y-2">
                  <h5 class="text-sm font-medium text-gray-800 dark:text-gray-200">
                    Benefits:
                  </h5>
                  <ul class="text-xs text-gray-600 dark:text-gray-300 space-y-1">
                    <li class="flex items-center">
                      <i class="fas fa-history text-blue-500 mr-2 text-xs"></i>
                      Track setup changes over time
                    </li>
                    <li class="flex items-center">
                      <i class="fas fa-search text-purple-500 mr-2 text-xs"></i>
                      Easy reference for future adjustments
                    </li>
                    <li class="flex items-center">
                      <i class="fas fa-chart-line text-green-500 mr-2 text-xs"></i>
                      Performance correlation analysis
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <button 
          @click="startEquipmentSetup"
          :disabled="starting"
          class="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center"
        >
          <div v-if="starting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          <i v-else class="fas fa-plus mr-2"></i>
          {{ starting ? 'Creating Entry...' : `Create ${selectedEquipmentCategory.label} Setup Entry` }}
        </button>
      </div>
    </div>

    <!-- Action Buttons -->
    <div v-if="selectedBowSetup" class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-600">
      <button 
        @click="resetSelections"
        class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
      >
        <i class="fas fa-undo mr-2"></i>
        Reset Selection
      </button>
      
      <div class="text-sm text-gray-500 dark:text-gray-400">
        <span v-if="selectionType === 'arrow' && selectedArrow">
          Ready to start {{ availableTuningGuides.length }} tuning guide{{ availableTuningGuides.length !== 1 ? 's' : '' }}
        </span>
        <span v-else-if="selectionType === 'equipment' && selectedEquipmentCategory">
          Ready to document {{ selectedEquipmentCategory.label.toLowerCase() }} setup
        </span>
        <span v-else>
          Select {{ selectionType }} to continue
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useRouter } from 'vue-router'

// Router
const router = useRouter()

// Reactive data
const selectedBowSetup = ref(null)
const selectionType = ref('arrow') // 'arrow' or 'equipment'
const selectedArrow = ref(null)
const selectedEquipmentCategory = ref(null)
const bowSetups = ref([])
const setupArrows = ref([])
const starting = ref(false)

const loading = ref({
  bowSetups: false,
  arrows: false
})

// API composable
const api = useApi()

// Equipment categories with enhanced metadata
const equipmentCategories = [
  {
    name: 'bow',
    label: 'Bow',
    icon: 'fas fa-crosshairs',
    color: 'text-blue-600 dark:text-blue-400',
    description: 'Bow tuning & setup',
    documentationItems: [
      'Tiller measurements',
      'Brace height adjustments', 
      'Timing and synchronization',
      'Performance notes'
    ]
  },
  {
    name: 'arrow_rest',
    label: 'Arrow Rest',
    icon: 'fas fa-grip-horizontal',
    color: 'text-green-600 dark:text-green-400',
    description: 'Rest positioning & tuning',
    documentationItems: [
      'Centershot alignment',
      'Height adjustments',
      'Contact pressure settings',
      'Clearance verification'
    ]
  },
  {
    name: 'sight',
    label: 'Sight',
    icon: 'fas fa-bullseye',
    color: 'text-purple-600 dark:text-purple-400',
    description: 'Sight setup & calibration',
    documentationItems: [
      'Pin gap measurements',
      'Windage adjustments',
      'Elevation settings',
      'Distance marks'
    ]
  },
  {
    name: 'release',
    label: 'Release Aid',
    icon: 'fas fa-hand-point-up',
    color: 'text-orange-600 dark:text-orange-400',
    description: 'Release tuning & setup',
    documentationItems: [
      'Trigger sensitivity',
      'Grip positioning',
      'Length adjustments',
      'Performance feedback'
    ]
  },
  {
    name: 'stabilizer',
    label: 'Stabilizer',
    icon: 'fas fa-balance-scale',
    color: 'text-indigo-600 dark:text-indigo-400',
    description: 'Stabilizer configuration',
    documentationItems: [
      'Weight distribution',
      'Length combinations',
      'Angle adjustments',
      'Balance point effects'
    ]
  },
  {
    name: 'string',
    label: 'String & Cables',
    icon: 'fas fa-grip-lines',
    color: 'text-red-600 dark:text-red-400',
    description: 'String system setup',
    documentationItems: [
      'Serving applications',
      'Twist adjustments',
      'Stretch measurements',
      'Peep alignment'
    ]
  },
  {
    name: 'peep_sight',
    label: 'Peep Sight',
    icon: 'fas fa-dot-circle',
    color: 'text-teal-600 dark:text-teal-400',
    description: 'Peep sight positioning',
    documentationItems: [
      'Height positioning',
      'Rotation alignment',
      'Size selection',
      'Visibility optimization'
    ]
  },
  {
    name: 'other',
    label: 'Other Equipment',
    icon: 'fas fa-tools',
    color: 'text-gray-600 dark:text-gray-400',
    description: 'Miscellaneous equipment',
    documentationItems: [
      'Custom modifications',
      'Accessory installations',
      'Performance accessories',
      'Setup notes'
    ]
  }
]

// Available tuning guides for arrows
const availableTuningGuides = computed(() => [
  {
    id: 'paper_tuning',
    name: 'Paper Tuning',
    description: 'Analyze arrow tear patterns through paper for spine and clearance issues',
    estimatedTime: '15-20 minutes',
    icon: 'fas fa-file-alt',
    color: 'text-blue-600 dark:text-blue-400'
  },
  {
    id: 'bareshaft_tuning',
    name: 'Bareshaft Tuning', 
    description: 'Compare bare shaft vs fletched arrow grouping for spine validation',
    estimatedTime: '20-30 minutes',
    icon: 'fas fa-bullseye',
    color: 'text-green-600 dark:text-green-400'
  },
  {
    id: 'walkback_tuning',
    name: 'Walkback Tuning',
    description: 'Multi-distance shooting analysis for rest/centershot alignment',
    estimatedTime: '25-35 minutes',
    icon: 'fas fa-chart-line',
    color: 'text-purple-600 dark:text-purple-400'
  }
])

// Methods
const loadBowSetups = async () => {
  loading.value.bowSetups = true
  try {
    const response = await api.get('/bow-setups')
    // Handle response - it might be direct array or wrapped in setups property
    bowSetups.value = Array.isArray(response) ? response : (response.setups || [])
    console.log('Loaded bow setups:', bowSetups.value.length, 'setups')
  } catch (error) {
    console.error('Failed to load bow setups:', error)
    bowSetups.value = []
  } finally {
    loading.value.bowSetups = false
  }
}

const loadArrowsForSetup = async () => {
  if (!selectedBowSetup.value?.id) return
  
  loading.value.arrows = true
  try {
    const response = await api.get(`/bow-setups/${selectedBowSetup.value.id}/arrows`)
    // Handle response - it might be direct array or wrapped in arrows property
    setupArrows.value = Array.isArray(response) ? response : (response.arrows || [])
    console.log('Loaded arrows for setup:', setupArrows.value.length, 'arrows')
  } catch (error) {
    console.error('Failed to load arrows for setup:', error)
    setupArrows.value = []
  } finally {
    loading.value.arrows = false
  }
}

const selectBowSetup = (setup) => {
  selectedBowSetup.value = setup
  resetSelections(false) // Don't reset bow setup
  loadArrowsForSetup()
}

const selectArrow = (arrow) => {
  selectedArrow.value = arrow
}

const selectEquipmentCategory = (category) => {
  selectedEquipmentCategory.value = category
}

const startTuningGuide = async (guide) => {
  if (!selectedBowSetup.value || !selectedArrow.value) return
  
  starting.value = true
  try {
    const sessionData = {
      bow_setup_id: selectedBowSetup.value.id,
      arrow_id: selectedArrow.value.arrow_id,
      arrow_length: selectedArrow.value.arrow_length,
      point_weight: selectedArrow.value.point_weight,
      guide_type: guide.id
    }
    
    const response = await api.post('/tuning-guides/start', sessionData)
    
    // Redirect directly to the new tuning session URLs based on guide type
    if (guide.id === 'paper_tuning') {
      router.push(`/tuning-session/paper/${response.session_id}`)
    } else if (guide.id === 'bareshaft_tuning') {
      router.push(`/tuning-session/bareshaft/${response.session_id}`)
    } else if (guide.id === 'walkback_tuning') {
      router.push(`/tuning-session/walkback/${response.session_id}`)
    } else {
      console.error('Unknown guide type:', guide.id)
    }
    
  } catch (error) {
    console.error('Failed to start tuning session:', error)
  } finally {
    starting.value = false
  }
}

const startEquipmentSetup = async () => {
  if (!selectedBowSetup.value || !selectedEquipmentCategory.value) return
  
  starting.value = true
  try {
    // Emit equipment setup event for parent to handle
    emit('equipment-setup-requested', {
      bow_setup: selectedBowSetup.value,
      equipment_category: selectedEquipmentCategory.value
    })
    
  } catch (error) {
    console.error('Failed to start equipment setup:', error)
  } finally {
    starting.value = false
  }
}

const resetSelections = (includeSetup = true) => {
  if (includeSetup) {
    selectedBowSetup.value = null
    setupArrows.value = []
  }
  selectedArrow.value = null
  selectedEquipmentCategory.value = null
  selectionType.value = 'arrow'
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

const getDisplaySpine = (arrowSetup) => {
  return arrowSetup.spine_value || arrowSetup.arrow?.spine || 'N/A'
}

const calculateTotalArrowWeight = (arrowSetup) => {
  if (arrowSetup.total_weight) return `${arrowSetup.total_weight}`
  
  // Calculate if we have individual components
  const arrowWeight = arrowSetup.arrow?.gpi_weight || 0
  const pointWeight = arrowSetup.point_weight || 0
  const nockWeight = arrowSetup.arrow?.nock_weight || 5 // Default nock weight
  const fletchingWeight = arrowSetup.arrow?.fletching_weight || 10 // Default fletching weight
  
  if (arrowWeight && pointWeight) {
    return `${Math.round(arrowWeight + pointWeight + nockWeight + fletchingWeight)}`
  }
  
  return null
}

// Watchers
watch(selectionType, () => {
  selectedArrow.value = null
  selectedEquipmentCategory.value = null
})

// Define emits
const emit = defineEmits(['session-started', 'equipment-setup-requested', 'cancel'])

// Lifecycle
onMounted(() => {
  loadBowSetups()
})
</script>

<style scoped>
/* Custom styles for enhanced visual hierarchy */
.equipment-category-card:hover {
  transform: translateY(-2px);
}

.guide-card:hover {
  transform: translateY(-1px);
}

.transition-all {
  transition: all 0.2s ease-in-out;
}
</style>