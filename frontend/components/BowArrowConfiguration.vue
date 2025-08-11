<template>
  <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl shadow-sm border border-blue-200 dark:border-blue-700 p-6 mb-6">
    <!-- Loading State -->
    <div v-if="loading" class="animate-pulse">
      <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-64 mb-4"></div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    </div>

    <!-- Configuration Content -->
    <div v-else-if="arrowSetup && bowInfo">
      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div>
          <div class="flex items-center space-x-2 mb-2">
            <i class="fas fa-bow-arrow text-2xl text-blue-600 dark:text-blue-400"></i>
            <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">
              Arrow Configuration for {{ bowInfo.name }}
            </h2>
          </div>
          <div class="flex items-center space-x-3">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              <i class="fas fa-target mr-2"></i>
              {{ arrowSetup.compatibility_score }}% Match
            </span>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              <i class="fas fa-calendar-plus mr-1"></i>
              Added {{ formatDate(arrowSetup.created_at) }}
            </span>
          </div>
        </div>
        
        <CustomButton
          v-if="bowInfo.returnTo"
          @click="navigateTo(bowInfo.returnTo)"
          variant="outlined"
          size="small"
          class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400"
        >
          <i class="fas fa-arrow-left mr-2"></i>
          Back to {{ bowInfo.name }}
        </CustomButton>
      </div>

      <!-- Configuration Details Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <!-- Arrow Length -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Arrow Length</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ arrowSetup.arrow_length }}"</p>
            </div>
            <i class="fas fa-arrows-alt-h text-2xl text-green-600 dark:text-green-400"></i>
          </div>
        </div>

        <!-- Point Weight -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Point Weight</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ arrowSetup.point_weight }} gr</p>
            </div>
            <i class="fas fa-bullseye text-2xl text-red-600 dark:text-red-400"></i>
          </div>
        </div>

        <!-- Calculated Spine -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Calculated Spine</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ getDisplaySpine(arrowSetup.calculated_spine) }}</p>
            </div>
            <i class="fas fa-ruler-horizontal text-2xl text-indigo-600 dark:text-indigo-400"></i>
          </div>
        </div>

        <!-- Total Arrow Weight -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Weight</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ calculateTotalWeight() }} gr</p>
            </div>
            <i class="fas fa-weight text-2xl text-purple-600 dark:text-purple-400"></i>
          </div>
        </div>
      </div>

      <!-- Component Weights (if available) -->
      <div v-if="hasComponentWeights" class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm mb-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-cogs mr-2 text-orange-600 dark:text-orange-400"></i>
          Component Weights
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div v-if="arrowSetup.nock_weight" class="flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div class="flex items-center space-x-2">
              <i class="fas fa-circle text-purple-600 dark:text-purple-400"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">Nock Weight</span>
            </div>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.nock_weight }} gr</span>
          </div>
          
          <div v-if="arrowSetup.insert_weight && arrowSetup.insert_weight > 0" class="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
            <div class="flex items-center space-x-2">
              <i class="fas fa-circle-dot text-orange-600 dark:text-orange-400"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">Insert Weight</span>
            </div>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.insert_weight }} gr</span>
          </div>
          
          <div v-if="arrowSetup.bushing_weight && arrowSetup.bushing_weight > 0" class="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div class="flex items-center space-x-2">
              <i class="fas fa-ring text-green-600 dark:text-green-400"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">Bushing Weight</span>
            </div>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.bushing_weight }} gr</span>
          </div>
        </div>
      </div>

      <!-- Notes (if available) -->
      <div v-if="arrowSetup.notes" class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg p-4">
        <h3 class="text-sm font-semibold text-amber-800 dark:text-amber-200 mb-2">
          <i class="fas fa-sticky-note mr-2"></i>
          Configuration Notes
        </h3>
        <p class="text-sm text-amber-700 dark:text-amber-300">{{ arrowSetup.notes }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <div class="text-amber-600 dark:text-amber-400 mb-4">
        <i class="fas fa-info-circle text-3xl mb-2"></i>
        <p class="text-lg font-medium">Arrow Not Configured for This Bow</p>
        <p class="text-sm mb-4">{{ error }}</p>
        <CustomButton
          v-if="bowInfo?.returnTo"
          @click="navigateTo(bowInfo.returnTo)"
          variant="outlined"
          class="text-amber-600 border-amber-600 hover:bg-amber-50 dark:text-amber-400 dark:border-amber-400"
        >
          <i class="fas fa-arrow-left mr-2"></i>
          Back to {{ bowInfo?.name || 'Bow Setup' }}
        </CustomButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  bowId: {
    type: [String, Number],
    required: true
  },
  arrowId: {
    type: [String, Number], 
    required: true
  },
  bowName: {
    type: String,
    default: 'Unknown Bow'
  },
  returnTo: {
    type: String,
    default: null
  }
})

// Emits
const emit = defineEmits(['loaded'])

// State
const arrowSetup = ref(null)
const bowInfo = ref(null)
const loading = ref(true)
const error = ref(null)

// Composables
const api = useApi()

// Computed
const hasComponentWeights = computed(() => {
  return arrowSetup.value && (
    arrowSetup.value.nock_weight ||
    (arrowSetup.value.insert_weight && arrowSetup.value.insert_weight > 0) ||
    (arrowSetup.value.bushing_weight && arrowSetup.value.bushing_weight > 0)
  )
})

// Methods
const attemptSpineRecalculation = async (setup) => {
  try {
    console.log('Attempting to recalculate spine for setup with null spine...')
    
    // Get bow setup details to calculate spine
    const bowSetupResponse = await api.get(`/bow-setups/${props.bowId}`)
    const bowSetup = bowSetupResponse
    
    if (bowSetup) {
      // Calculate spine using the same endpoint as calculator
      const spineCalcData = {
        draw_weight: bowSetup.draw_weight,
        arrow_length: setup.arrow_length,
        point_weight: setup.point_weight,
        bow_type: bowSetup.bow_type,
        nock_weight: 10, // Default values
        fletching_weight: 15
      }
      
      const spineResponse = await api.post('/tuning/calculate-spine', spineCalcData)
      const calculatedSpine = spineResponse.recommended_spine
      
      console.log(`Calculated spine: ${calculatedSpine} for arrow ${setup.arrow_id}`)
      
      // Update the setup object with calculated spine
      setup.calculated_spine = calculatedSpine
      
      // Optionally update the database via API call
      // This would require a specific endpoint to update calculated_spine
      
    }
  } catch (err) {
    console.log('Spine recalculation failed:', err)
  }
}

const attemptPreviewCalculation = async () => {
  try {
    // This is a preview - try to get bow setup details and calculate what spine would be
    // This provides useful information even when arrow isn't saved to the bow
    console.log('Attempting preview calculation for unsaved arrow configuration...')
    
    // For now, just clear the error to show the improved error state
    // Future enhancement: Could fetch bow setup details and calculate preview spine
    
  } catch (err) {
    console.log('Preview calculation failed:', err)
  }
}

const fetchArrowSetup = async () => {
  try {
    loading.value = true
    error.value = null

    // Fetch the arrow setup data for this specific bow and arrow combination
    const response = await api.get(`/bow-setups/${props.bowId}/arrows`)
    
    // Find the specific arrow setup
    const arrowSetups = response.arrows || []
    const foundSetup = arrowSetups.find(setup => 
      setup.arrow_id === parseInt(props.arrowId) || 
      setup.arrow?.id === parseInt(props.arrowId)
    )

    if (foundSetup) {
      // Check if calculated_spine is null and try to recalculate it
      if (foundSetup.calculated_spine === null || foundSetup.calculated_spine === undefined) {
        console.log('Found setup with null calculated_spine, attempting to recalculate...')
        await attemptSpineRecalculation(foundSetup)
      }
      
      arrowSetup.value = foundSetup
      bowInfo.value = {
        id: props.bowId,
        name: props.bowName,
        returnTo: props.returnTo
      }
      emit('loaded', foundSetup)
    } else {
      // Set bowInfo even for error state so back button works
      bowInfo.value = {
        id: props.bowId,
        name: props.bowName,
        returnTo: props.returnTo
      }
      error.value = 'This arrow is not configured for this bow setup'
      
      // Optional: Try to create a temporary configuration for preview
      // This would show what the spine calculation would be if the arrow were added to this bow
      await attemptPreviewCalculation()
    }
  } catch (err) {
    console.error('Error fetching arrow setup:', err)
    error.value = err.message || 'Failed to load arrow configuration'
  } finally {
    loading.value = false
  }
}

const calculateTotalWeight = () => {
  if (!arrowSetup.value) return 'N/A'

  // Get GPI weight from arrow specifications
  const arrow = arrowSetup.value.arrow
  if (!arrow?.spine_specifications?.length) return 'N/A'

  // Find the appropriate spine specification
  let spineSpec = null
  if (arrowSetup.value.calculated_spine && arrowSetup.value.calculated_spine !== 'N/A') {
    spineSpec = arrow.spine_specifications.find(spec => 
      spec.spine && spec.spine.toString() === arrowSetup.value.calculated_spine.toString()
    )
  }

  // If no match found, use the first spine specification
  if (!spineSpec) {
    spineSpec = arrow.spine_specifications[0]
  }

  if (!spineSpec?.gpi_weight) return 'N/A'

  // Calculate shaft weight (GPI * length)
  const shaftWeight = spineSpec.gpi_weight * (arrowSetup.value.arrow_length || 32)
  
  // Add component weights
  const pointWeight = arrowSetup.value.point_weight || 0
  const insertWeight = arrowSetup.value.insert_weight || 0
  const nockWeight = arrowSetup.value.nock_weight || 0
  const bushingWeight = arrowSetup.value.bushing_weight || 0
  const fletchingWeight = arrowSetup.value.fletching_weight || 15 // Default fletching weight
  
  const totalWeight = shaftWeight + pointWeight + insertWeight + nockWeight + bushingWeight + fletchingWeight
  
  return Math.round(totalWeight * 10) / 10
}

const getDisplaySpine = (spine) => {
  // Handle various possible spine value formats
  if (spine === null || spine === undefined || spine === '') {
    return 'Calculating...'
  }
  
  // Handle string "null" or "undefined"
  if (typeof spine === 'string' && (spine.toLowerCase() === 'null' || spine.toLowerCase() === 'undefined')) {
    return 'Calculating...'
  }
  
  // Handle numeric values
  if (typeof spine === 'number' || (typeof spine === 'string' && !isNaN(parseFloat(spine)))) {
    const numericSpine = typeof spine === 'number' ? spine : parseFloat(spine)
    return numericSpine.toString()
  }
  
  return 'N/A'
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'Unknown date'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  } catch (e) {
    return 'Invalid date'
  }
}

// Lifecycle
onMounted(() => {
  fetchArrowSetup()
})
</script>