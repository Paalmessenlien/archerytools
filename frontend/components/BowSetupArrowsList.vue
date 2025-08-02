<template>
  <div class="mt-4">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
        <i class="fas fa-bullseye mr-2 text-blue-600"></i>
        Saved Arrows ({{ arrows.length }})
      </h4>
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
    <div v-else-if="arrows.length === 0" class="text-sm text-gray-500 dark:text-gray-400 py-3 text-center">
      <i class="fas fa-search-minus text-lg mb-2 block"></i>
      No arrows added to this bow setup yet.
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
              <h5 class="font-medium text-gray-900 dark:text-gray-100">
                {{ arrowSetup.arrow?.manufacturer || 'Unknown Manufacturer' }}
              </h5>
              <span class="hidden sm:inline text-gray-400">•</span>
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ arrowSetup.arrow?.model_name || 'Unknown Model' }}
              </span>
            </div>
            
            <!-- Arrow Specifications as Chips -->
            <md-chip-set class="mb-3 flex-wrap">
              <!-- Calculated Spine -->
              <md-assist-chip :label="`Spine: ${arrowSetup.calculated_spine || 'N/A'}`">
                <i class="fas fa-ruler-horizontal fa-icon" slot="icon" style="color: #6366f1;"></i>
              </md-assist-chip>
              
              <!-- Arrow Length -->
              <md-assist-chip :label="`Length: ${arrowSetup.arrow_length}\&quot;`">
                <i class="fas fa-arrows-alt-h fa-icon" slot="icon" style="color: #059669;"></i>
              </md-assist-chip>
              
              <!-- Point Weight -->
              <md-assist-chip :label="`Point: ${arrowSetup.point_weight} gr`">
                <i class="fas fa-bullseye fa-icon" slot="icon" style="color: #dc2626;"></i>
              </md-assist-chip>
              
              <!-- Material -->
              <md-assist-chip :label="arrowSetup.arrow?.material || 'Material N/A'">
                <i class="fas fa-layer-group fa-icon" slot="icon" style="color: #7c2d12;"></i>
              </md-assist-chip>

              <!-- Component Weights (when available) -->
              <md-assist-chip v-if="arrowSetup.nock_weight" :label="`Nock: ${arrowSetup.nock_weight} gr`">
                <i class="fas fa-circle fa-icon" slot="icon" style="color: #8b5cf6;"></i>
              </md-assist-chip>
              
              <md-assist-chip v-if="arrowSetup.insert_weight && arrowSetup.insert_weight > 0" :label="`Insert: ${arrowSetup.insert_weight} gr`">
                <i class="fas fa-circle-dot fa-icon" slot="icon" style="color: #f59e0b;"></i>
              </md-assist-chip>
              
              <md-assist-chip v-if="arrowSetup.bushing_weight && arrowSetup.bushing_weight > 0" :label="`Bushing: ${arrowSetup.bushing_weight} gr`">
                <i class="fas fa-ring fa-icon" slot="icon" style="color: #10b981;"></i>
              </md-assist-chip>

              <!-- Total Component Weight -->
              <md-assist-chip v-if="calculateTotalComponentWeight(arrowSetup)" :label="`Components: ${calculateTotalComponentWeight(arrowSetup)} gr`" class="bg-blue-100 dark:bg-blue-900">
                <i class="fas fa-weight-hanging fa-icon" slot="icon" style="color: #3b82f6;"></i>
              </md-assist-chip>

              <!-- Total Arrow Weight -->
              <md-assist-chip v-if="calculateTotalArrowWeight(arrowSetup)" :label="`Arrow: ${calculateTotalArrowWeight(arrowSetup)} gr`" class="bg-purple-100 dark:bg-purple-900">
                <i class="fas fa-balance-scale fa-icon" slot="icon" style="color: #8b5cf6;"></i>
              </md-assist-chip>
            </md-chip-set>
            
            <!-- Match Score & Notes -->
            <div class="flex items-center justify-between">
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
              <div class="flex space-x-2">
                <CustomButton
                  @click="editArrow(arrowSetup)"
                  variant="outlined"
                  size="small"
                  class="text-orange-600 border-orange-600 hover:bg-orange-50 dark:text-orange-400 dark:border-orange-400"
                >
                  <i class="fas fa-edit mr-1"></i>
                  Edit
                </CustomButton>
                <CustomButton
                  @click="viewArrowDetails(arrowSetup.arrow_id)"
                  variant="outlined"
                  size="small"
                  class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400"
                >
                  <i class="fas fa-info-circle mr-1"></i>
                  Details
                </CustomButton>
                <CustomButton
                  @click="removeArrow(arrowSetup.id)"
                  variant="outlined"
                  size="small"
                  class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400"
                >
                  <i class="fas fa-trash mr-1"></i>
                  Remove
                </CustomButton>
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
              <span v-if="arrowSetup.calculated_spine">Spine: {{ arrowSetup.calculated_spine }}</span>
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
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  arrows: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['remove-arrow', 'view-details', 'edit-arrow'])

// State
const isExpanded = ref(false)

// Computed
const displayedArrows = computed(() => {
  return props.arrows
})

// Methods
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
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
  if (!arrowSetup.arrow || !arrowSetup.arrow.spine_specifications) return 0
  
  // Find the appropriate spine specification (use first one if no specific match)
  const spineSpec = arrowSetup.arrow.spine_specifications[0]
  if (!spineSpec || !spineSpec.gpi_weight) return 0
  
  // Use arrow length from setup or default to 32" if no length options available
  let effectiveLength = arrowSetup.arrow_length || 32
  
  // If arrow has specific length options, use the closest one
  if (spineSpec.length_options && spineSpec.length_options.length > 0) {
    // Find the closest available length
    const targetLength = arrowSetup.arrow_length || 32
    effectiveLength = spineSpec.length_options.reduce((prev: number, curr: number) => 
      Math.abs(curr - targetLength) < Math.abs(prev - targetLength) ? curr : prev
    )
  }
  
  // Calculate shaft weight (GPI * length in inches)
  const shaftWeight = spineSpec.gpi_weight * effectiveLength
  
  // Add component weights from the saved setup
  const pointWeight = arrowSetup.point_weight || 0
  const insertWeight = arrowSetup.insert_weight || 0
  const nockWeight = arrowSetup.nock_weight || 0
  const bushingWeight = arrowSetup.bushing_weight || 0
  // Note: For now using default vane weight calculation since vane details aren't stored in setup_arrows
  const vaneWeightPerVane = 5 // Default vane weight
  const numberOfVanes = 3 // Default number of vanes
  
  const totalVaneWeight = vaneWeightPerVane * numberOfVanes
  
  // Total arrow weight = shaft + components
  const totalWeight = shaftWeight + pointWeight + insertWeight + nockWeight + bushingWeight + totalVaneWeight
  
  return Math.round(totalWeight * 10) / 10 // Round to 1 decimal place
}

const viewArrowDetails = (arrowId: number) => {
  emit('view-details', arrowId)
}

const removeArrow = (arrowSetupId: number) => {
  emit('remove-arrow', arrowSetupId)
}

const editArrow = (arrowSetup) => {
  emit('edit-arrow', arrowSetup)
}
</script>

<style scoped>
.fa-icon {
  font-size: 0.75rem;
}
</style>