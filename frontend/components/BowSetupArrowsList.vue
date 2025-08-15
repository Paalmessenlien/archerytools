<template>
  <div class="mt-4">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
        <i class="fas fa-bullseye mr-2 text-blue-600"></i>
        Saved Arrows ({{ arrows.length }})
      </h4>
      
      <div class="flex items-center space-x-2">
        <!-- Add Arrow Button -->
        <CustomButton
          @click="navigateToCalculator"
          variant="filled"
          size="small"
          class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-600 dark:hover:bg-green-700"
        >
          <i class="fas fa-plus mr-1"></i>
          <span class="hidden sm:inline">Add Arrow</span>
        </CustomButton>
        
        <!-- Expand/Collapse Button -->
        <CustomButton
          v-if="arrows.length > 0"
          @click="toggleExpanded"
          variant="text"
          size="small"
          class="text-gray-600 dark:text-gray-400"
        >
          <i class="fas transition-transform" :class="isExpanded ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
          {{ isExpanded ? 'Collapse' : 'Expand' }}
        </CustomButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="animate-pulse space-y-3">
      <div v-for="i in 2" :key="i" class="border border-gray-200 rounded-lg p-3">
        <div class="flex justify-between items-start">
          <div class="space-y-2 flex-1">
            <div class="h-4 bg-gray-200 rounded w-48"></div>
            <div class="h-3 bg-gray-200 rounded w-32"></div>
          </div>
          <div class="h-4 bg-gray-200 rounded w-16"></div>
        </div>
      </div>
    </div>

    <!-- No Arrows State -->
    <div v-else-if="arrows.length === 0" class="text-center py-8">
      <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="fas fa-bullseye text-2xl text-gray-400"></i>
      </div>
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Arrows Added Yet</h4>
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        Get started by adding arrows to your bow setup using the arrow calculator.
      </p>
      <CustomButton
        @click="navigateToCalculator"
        variant="filled"
        class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-600 dark:hover:bg-green-700"
      >
        <i class="fas fa-plus mr-2"></i>
        Add Your First Arrow
      </CustomButton>
    </div>

    <!-- Arrows List -->
    <div v-else-if="isExpanded || arrows.length <= 2" class="space-y-3">
      <div 
        v-for="arrowSetup in displayedArrows" 
        :key="arrowSetup.id"
        class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1 min-w-0">
            <!-- Arrow Header -->
            <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-2 mb-3">
              <div class="flex items-center space-x-2">
                <h5 class="font-medium text-gray-900 dark:text-gray-100">
                  {{ arrowSetup.arrow?.manufacturer || 'Unknown Manufacturer' }}
                </h5>
                <!-- Orphaned Arrow Warning -->
                <span v-if="!arrowSetup.arrow" class="px-2 py-1 text-xs bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300 rounded-full">
                  <i class="fas fa-exclamation-triangle mr-1"></i>
                  Orphaned
                </span>
              </div>
              <span class="hidden sm:inline text-gray-400">•</span>
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ arrowSetup.arrow?.model_name || `Arrow ID: ${arrowSetup.arrow_id}` }}
              </span>
            </div>
            
            <!-- Arrow Specifications as Vertical List -->
            <div class="mb-3 space-y-2">
              <!-- Primary Specifications -->
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
                <div class="flex items-center space-x-2">
                  <i class="fas fa-ruler-horizontal text-indigo-600 dark:text-indigo-400"></i>
                  <span class="text-gray-700 dark:text-gray-300">Spine: <span class="font-medium text-gray-900 dark:text-gray-100">{{ getDisplaySpine(arrowSetup) }}</span></span>
                </div>
                
                <div class="flex items-center space-x-2">
                  <i class="fas fa-arrows-alt-h text-green-600 dark:text-green-400"></i>
                  <span class="text-gray-700 dark:text-gray-300">Length: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.arrow_length }}"</span></span>
                </div>
                
                <div class="flex items-center space-x-2">
                  <i class="fas fa-bullseye text-red-600 dark:text-red-400"></i>
                  <span class="text-gray-700 dark:text-gray-300">Point: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.point_weight }} gr</span></span>
                </div>
                
                <div class="flex items-center space-x-2 col-span-2 sm:col-span-1">
                  <i class="fas fa-layer-group text-amber-600 dark:text-amber-400"></i>
                  <span class="text-gray-700 dark:text-gray-300">Material: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.arrow?.material || 'Unknown Material' }}</span></span>
                </div>
                
                <!-- Orphaned Arrow Warning -->
                <div v-if="!arrowSetup.arrow" class="col-span-full mt-2 p-2 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded text-sm">
                  <div class="flex items-start space-x-2">
                    <i class="fas fa-info-circle text-orange-600 dark:text-orange-400 mt-0.5"></i>
                    <div class="text-orange-800 dark:text-orange-200">
                      <strong>Orphaned Arrow:</strong> This arrow configuration references Arrow ID {{ arrowSetup.arrow_id }} which no longer exists in the database. 
                      This can happen when arrow data is updated or removed. You can safely delete this configuration.
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Component Weights (when available) -->
              <div v-if="arrowSetup.nock_weight || (arrowSetup.insert_weight && arrowSetup.insert_weight > 0) || (arrowSetup.bushing_weight && arrowSetup.bushing_weight > 0)" class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm pt-2 border-t border-gray-200 dark:border-gray-700">
                <div v-if="arrowSetup.nock_weight" class="flex items-center space-x-2">
                  <i class="fas fa-circle text-purple-600 dark:text-purple-400"></i>
                  <span class="text-gray-700 dark:text-gray-300">Nock: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.nock_weight }} gr</span></span>
                </div>
                
                <div v-if="arrowSetup.insert_weight && arrowSetup.insert_weight > 0" class="flex items-center space-x-2">
                  <i class="fas fa-circle-dot text-orange-600 dark:text-orange-400"></i>
                  <span class="text-gray-700 dark:text-gray-300">Insert: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.insert_weight }} gr</span></span>
                </div>
                
                <div v-if="arrowSetup.bushing_weight && arrowSetup.bushing_weight > 0" class="flex items-center space-x-2">
                  <i class="fas fa-ring text-green-600 dark:text-green-400"></i>
                  <span class="text-gray-700 dark:text-gray-300">Bushing: <span class="font-medium text-gray-900 dark:text-gray-100">{{ arrowSetup.bushing_weight }} gr</span></span>
                </div>
              </div>
              
              <!-- Weight Totals -->
              <div v-if="calculateTotalComponentWeight(arrowSetup) || calculateTotalArrowWeight(arrowSetup)" class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm pt-2 border-t border-gray-200 dark:border-gray-700">
                <div v-if="calculateTotalComponentWeight(arrowSetup)" class="flex items-center space-x-2 bg-blue-50 dark:bg-blue-900/30 px-3 py-1 rounded">
                  <i class="fas fa-weight-hanging text-blue-600 dark:text-blue-400"></i>
                  <span class="text-blue-800 dark:text-blue-200">Components: <span class="font-medium">{{ calculateTotalComponentWeight(arrowSetup) }} gr</span></span>
                </div>
                
                <div v-if="calculateTotalArrowWeight(arrowSetup)" class="flex items-center space-x-2 bg-purple-50 dark:bg-purple-900/30 px-3 py-1 rounded">
                  <i class="fas fa-balance-scale text-purple-600 dark:text-purple-400"></i>
                  <span class="text-purple-800 dark:text-purple-200">Total Arrow: <span class="font-medium">{{ calculateTotalArrowWeight(arrowSetup) }} gr</span></span>
                </div>
              </div>
              
              <!-- Performance Metrics -->
              <div v-if="arrowSetup.performance?.performance_summary" class="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-3 mt-2">
                <div class="flex items-center justify-between mb-2">
                  <h5 class="text-xs font-semibold text-green-800 dark:text-green-200 uppercase tracking-wide">
                    <i class="fas fa-tachometer-alt mr-1"></i>
                    Performance Metrics
                  </h5>
                  <span :class="getPerformanceScoreClass(arrowSetup.performance.performance_summary)" class="text-xs font-medium">
                    {{ getPerformanceScore(arrowSetup.performance.performance_summary) }}/100
                  </span>
                </div>
                
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  <div class="text-center bg-white dark:bg-gray-800/50 rounded p-2">
                    <div class="text-blue-600 dark:text-blue-400 font-bold text-sm">
                      {{ arrowSetup.performance.performance_summary.estimated_speed_fps }}
                    </div>
                    <div class="text-gray-500 dark:text-gray-400 text-xs">fps</div>
                  </div>
                  <div class="text-center bg-white dark:bg-gray-800/50 rounded p-2">
                    <div class="text-green-600 dark:text-green-400 font-bold text-sm">
                      {{ arrowSetup.performance.performance_summary.kinetic_energy_40yd }}
                    </div>
                    <div class="text-gray-500 dark:text-gray-400 text-xs">ft·lbs @40yd</div>
                  </div>
                  <div class="text-center bg-white dark:bg-gray-800/50 rounded p-2">
                    <div class="text-purple-600 dark:text-purple-400 font-bold text-sm">
                      {{ arrowSetup.performance.performance_summary.foc_percentage?.toFixed(1) || 0 }}%
                    </div>
                    <div class="text-gray-500 dark:text-gray-400 text-xs">FOC</div>
                  </div>
                  <div class="text-center bg-white dark:bg-gray-800/50 rounded p-2">
                    <div :class="getPenetrationClass(arrowSetup.performance.performance_summary.penetration_category)" class="font-bold text-sm capitalize">
                      {{ arrowSetup.performance.performance_summary.penetration_category }}
                    </div>
                    <div class="text-gray-500 dark:text-gray-400 text-xs">Penetration</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Match Score & Notes -->
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div class="flex items-center space-x-3">
                <!-- Compatibility Score -->
                <div v-if="arrowSetup.compatibility_score" class="flex items-center">
                  <span class="text-xs px-2 py-1 rounded-full" 
                        :class="getCompatibilityClass(arrowSetup.compatibility_score)">
                    {{ arrowSetup.compatibility_score }}% Match
                  </span>
                </div>
                
                <!-- Date Added -->
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  <i class="fas fa-clock mr-1"></i>
                  {{ formatDate(arrowSetup.created_at) }}
                </span>
              </div>
              
              <!-- Actions -->
              <div class="flex space-x-1 sm:space-x-2 overflow-x-auto">
                <!-- For orphaned arrows, emphasize the delete button and disable others -->
                <template v-if="!arrowSetup.arrow">
                  <CustomButton
                    @click="removeArrow(arrowSetup.id)"
                    variant="filled"
                    size="small"
                    class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700 whitespace-nowrap"
                  >
                    <i class="fas fa-trash mr-1"></i>
                    <span class="hidden sm:inline">Delete Orphaned</span>
                  </CustomButton>
                  <span class="text-xs text-gray-500 dark:text-gray-400 self-center px-2">
                    Other actions disabled for orphaned arrows
                  </span>
                </template>
                
                <!-- For normal arrows, show all actions -->
                <template v-else>
                  <CustomButton
                    @click="editArrow(arrowSetup)"
                    variant="outlined"
                    size="small"
                    class="text-orange-600 border-orange-600 hover:bg-orange-50 dark:text-orange-400 dark:border-orange-400 whitespace-nowrap"
                  >
                    <i class="fas fa-edit mr-1"></i>
                    <span class="hidden sm:inline">Edit</span>
                  </CustomButton>
                  <CustomButton
                    @click="duplicateArrow(arrowSetup)"
                    variant="outlined"
                    size="small"
                    class="text-purple-600 border-purple-600 hover:bg-purple-50 dark:text-purple-400 dark:border-purple-400 whitespace-nowrap"
                  >
                    <i class="fas fa-copy mr-1"></i>
                    <span class="hidden sm:inline">Duplicate</span>
                  </CustomButton>
                  <CustomButton
                    @click="viewArrowDetails(arrowSetup.arrow_id)"
                    variant="outlined"
                    size="small"
                    class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 whitespace-nowrap"
                  >
                    <i class="fas fa-info-circle mr-1"></i>
                    <span class="hidden sm:inline">Details</span>
                  </CustomButton>
                  <CustomButton
                    @click="removeArrow(arrowSetup.id)"
                    variant="outlined"
                    size="small"
                    class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 whitespace-nowrap"
                  >
                    <i class="fas fa-trash mr-1"></i>
                    <span class="hidden sm:inline">Remove</span>
                  </CustomButton>
                </template>
              </div>
            </div>
            
            <!-- Notes -->
            <div v-if="arrowSetup.notes" class="mt-2 text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 rounded p-2">
              <i class="fas fa-sticky-note mr-1"></i>
              {{ arrowSetup.notes }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Collapsed View (show first 2 arrows) -->
    <div v-else class="space-y-3">
      <div 
        v-for="arrowSetup in arrows.slice(0, 2)" 
        :key="arrowSetup.id"
        class="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
      >
        <div class="flex justify-between items-center">
          <div>
            <span class="font-medium text-gray-900 dark:text-gray-100 text-sm">
              {{ arrowSetup.arrow?.manufacturer || 'Unknown' }} {{ arrowSetup.arrow?.model_name || 'Unknown' }}
            </span>
            <div class="text-xs text-gray-600 dark:text-gray-400">
              {{ arrowSetup.arrow_length }}" • {{ arrowSetup.point_weight }}gr • 
              <span>Spine: {{ getDisplaySpine(arrowSetup) }}</span>
              <span v-if="calculateTotalArrowWeight(arrowSetup)"> • Total: {{ calculateTotalArrowWeight(arrowSetup) }}gr</span>
            </div>
          </div>
          <div v-if="arrowSetup.compatibility_score" class="text-xs px-2 py-1 rounded-full" 
               :class="getCompatibilityClass(arrowSetup.compatibility_score)">
            {{ arrowSetup.compatibility_score }}%
          </div>
        </div>
      </div>
      
      <div v-if="arrows.length > 2" class="text-center py-2">
        <CustomButton
          @click="toggleExpanded"
          variant="text"
          size="small"
          class="text-blue-600 dark:text-blue-400"
        >
          <i class="fas fa-plus mr-1"></i>
          {{ arrows.length - 2 }} more arrow{{ arrows.length - 2 > 1 ? 's' : '' }}
        </CustomButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useRouter } from 'vue-router'

// Composables
const { notifySuccess, notifyError } = useNotifications()

// Props
const props = defineProps({
  arrows: {
    type: Array,
    default: () => []
  },
  bowSetup: {
    type: Object,
    default: null
  },
  expanded: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['remove-arrow', 'view-details', 'edit-arrow', 'duplicate-arrow', 'arrow-updated'])

// Composables
const api = useApi()
const router = useRouter()

// State
const isExpanded = ref(props.expanded)
const internalArrows = ref([])
const internalLoading = ref(false)

// Computed
const displayedArrows = computed(() => {
  // Use arrows prop if provided, otherwise use internally loaded arrows
  return props.arrows.length > 0 ? props.arrows : internalArrows.value
})

const arrows = computed(() => displayedArrows.value)

const loading = computed(() => props.loading || internalLoading.value)

// Methods
const loadArrows = async () => {
  if (!props.bowSetup?.id) return
  
  try {
    internalLoading.value = true
    const response = await api.get(`/bow-setups/${props.bowSetup.id}/arrows`)
    internalArrows.value = response.arrows || []
  } catch (error) {
    console.error('Error loading arrows:', error)
    internalArrows.value = []
  } finally {
    internalLoading.value = false
  }
}

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const navigateToCalculator = () => {
  // Navigate to calculator with setup context for easier arrow addition
  if (props.bowSetup?.id) {
    router.push({
      path: '/calculator',
      query: {
        setupId: props.bowSetup.id,
        returnUrl: `/setups/${props.bowSetup.id}?tab=arrows`
      }
    })
  } else {
    // Fallback to basic calculator
    router.push('/calculator')
  }
}

const getCompatibilityClass = (score: number) => {
  if (score >= 90) {
    return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  } else if (score >= 70) {
    return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  } else {
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
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

// Calculate total component weight for display
const calculateTotalComponentWeight = (arrowSetup: any) => {
  const pointWeight = arrowSetup.point_weight || 0
  const insertWeight = arrowSetup.insert_weight || 0
  const nockWeight = arrowSetup.nock_weight || 0
  const bushingWeight = arrowSetup.bushing_weight || 0
  // Note: Vane weights would need additional fields in database
  
  const totalWeight = pointWeight + insertWeight + nockWeight + bushingWeight
  
  return totalWeight > 0 ? Math.round(totalWeight * 10) / 10 : null
}

// Calculate total arrow weight based on GPI and arrow length
const calculateTotalArrowWeight = (arrowSetup: any) => {
  if (!arrowSetup.arrow || !arrowSetup.arrow.spine_specifications || arrowSetup.arrow.spine_specifications.length === 0) {
    return null
  }
  
  // Find the appropriate spine specification
  let spineSpec = null
  
  // Try to find spine spec that matches calculated_spine or first available
  if (arrowSetup.calculated_spine && arrowSetup.calculated_spine !== 'N/A') {
    spineSpec = arrowSetup.arrow.spine_specifications.find(spec => 
      spec.spine && spec.spine.toString() === arrowSetup.calculated_spine.toString()
    )
  }
  
  // If no match found, use the first spine specification
  if (!spineSpec) {
    spineSpec = arrowSetup.arrow.spine_specifications[0]
  }
  
  if (!spineSpec || !spineSpec.gpi_weight) return null
  
  // Use arrow length from setup or default to 32"
  const effectiveLength = arrowSetup.arrow_length || 32
  
  // Calculate shaft weight (GPI * length in inches)
  const shaftWeight = spineSpec.gpi_weight * effectiveLength
  
  // Add component weights from the saved setup
  const pointWeight = arrowSetup.point_weight || 0
  const insertWeight = arrowSetup.insert_weight || 0
  const nockWeight = arrowSetup.nock_weight || 0
  const bushingWeight = arrowSetup.bushing_weight || 0
  const fletchingWeight = arrowSetup.fletching_weight || 15 // Default fletching weight (3 vanes @ 5gr each)
  
  // Total arrow weight = shaft + components
  const totalWeight = shaftWeight + pointWeight + insertWeight + nockWeight + bushingWeight + fletchingWeight
  
  return Math.round(totalWeight * 10) / 10 // Round to 1 decimal place
}

const viewArrowDetails = (arrowId: number) => {
  emit('view-details', arrowId)
}

const removeArrow = async (arrowSetupId: number) => {
  if (!props.bowSetup?.id) {
    emit('remove-arrow', arrowSetupId)
    return
  }
  
  try {
    await api.delete(`/setup-arrows/${arrowSetupId}`)
    await loadArrows() // Reload arrows after removal
    emit('arrow-updated') // Notify parent
  } catch (error) {
    console.error('Error removing arrow:', error)
    // Could emit an error event here
  }
}

const editArrow = async (arrowSetup) => {
  // For now, emit to parent component to handle editing modal
  // In the future, this could be handled inline or with a modal
  emit('edit-arrow', arrowSetup)
}

const duplicateArrow = async (arrowSetup) => {
  if (!props.bowSetup?.id || !arrowSetup.arrow_id) {
    emit('duplicate-arrow', arrowSetup)
    return
  }
  
  try {
    // Create a copy of the arrow setup with the same configuration
    const duplicateData = {
      arrow_id: arrowSetup.arrow_id,
      arrow_length: arrowSetup.arrow_length || 32,
      point_weight: arrowSetup.point_weight || 100,
      calculated_spine: arrowSetup.calculated_spine,
      notes: getSmartCopyNote(arrowSetup.notes),
      nock_weight: arrowSetup.nock_weight || 10,
      insert_weight: arrowSetup.insert_weight || 0,
      bushing_weight: arrowSetup.bushing_weight || 0,
      fletching_weight: arrowSetup.fletching_weight || 15,
      compatibility_score: arrowSetup.compatibility_score,
      user_note: 'Arrow duplicated',
      allow_duplicate: true  // Allow creating duplicate even with same specs
    }
    
    await api.post(`/bow-setups/${props.bowSetup.id}/arrows`, duplicateData)
    await loadArrows() // Reload arrows after duplication
    emit('arrow-updated') // Notify parent
  } catch (error) {
    console.error('Error duplicating arrow:', error)
    
    // For errors, fall back to parent handling
    emit('duplicate-arrow', arrowSetup)
  }
}

// Get display spine value - try calculated_spine first, then fall back to arrow specifications
const getDisplaySpine = (arrowSetup: any) => {
  // If we have a calculated spine and it's not null/empty
  if (arrowSetup.calculated_spine && arrowSetup.calculated_spine !== 'N/A') {
    return arrowSetup.calculated_spine
  }
  
  // Fall back to spine specifications from arrow data
  if (arrowSetup.arrow?.spine_specifications && arrowSetup.arrow.spine_specifications.length > 0) {
    // Return the first spine specification as fallback
    return arrowSetup.arrow.spine_specifications[0].spine
  }
  
  return 'N/A'
}

// Smart copy note generation - avoid nested "Copy of:" prefixes
const getSmartCopyNote = (originalNote: string) => {
  if (!originalNote) {
    return 'Duplicated arrow'
  }
  
  // If it already starts with "Copy of:", just increment or make it "Another copy of:"
  if (originalNote.startsWith('Copy of:')) {
    // Remove the "Copy of: " prefix to get the base note
    const baseNote = originalNote.substring(9).trim()
    return `Another copy of: ${baseNote}`
  }
  
  // For new copies, add the "Copy of:" prefix
  return `Copy of: ${originalNote}`
}

// Lifecycle
onMounted(() => {
  if (props.bowSetup?.id) {
    loadArrows()
  }
})

// Watch for bowSetup changes
watch(() => props.bowSetup?.id, (newId) => {
  if (newId) {
    loadArrows()
  }
})

// Expose methods to parent component
defineExpose({
  loadArrows,
  refresh: loadArrows
})

// Performance helper functions
const getPerformanceScore = (performanceSummary) => {
  if (!performanceSummary) return 0
  
  // Calculate composite performance score based on multiple factors
  const keScore = Math.min(100, (performanceSummary.kinetic_energy_40yd / 80) * 100) // 80 ft-lbs = 100%
  const penetrationScore = performanceSummary.penetration_score || 0
  const focScore = performanceSummary.foc_percentage ? 
    Math.max(0, 100 - Math.abs((performanceSummary.foc_percentage || 0) - 12) * 5) : 50 // Optimal FOC around 12%
  
  // Weighted average: 40% penetration, 30% KE, 30% FOC
  const compositeScore = (penetrationScore * 0.4) + (keScore * 0.3) + (focScore * 0.3)
  return Math.round(compositeScore)
}

const getPerformanceScoreClass = (performanceSummary) => {
  const score = getPerformanceScore(performanceSummary)
  if (score >= 80) return 'text-green-600 dark:text-green-400'
  if (score >= 60) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getPenetrationClass = (category) => {
  switch (category) {
    case 'excellent': return 'text-green-600 dark:text-green-400'
    case 'good': return 'text-blue-600 dark:text-blue-400'
    case 'fair': return 'text-yellow-600 dark:text-yellow-400'
    case 'poor': return 'text-red-600 dark:text-red-400'
    default: return 'text-gray-500 dark:text-gray-400'
  }
}
</script>

<style scoped>
.fa-icon {
  font-size: 0.75rem;
}
</style>