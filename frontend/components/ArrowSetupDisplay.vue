<template>
  <div class="space-y-6">
    <!-- Main Configuration -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Arrow Length -->
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
        <div class="flex items-center mb-2">
          <i class="fas fa-ruler-horizontal text-blue-600 dark:text-blue-400 mr-2"></i>
          <span class="text-sm font-medium text-blue-800 dark:text-blue-200">Arrow Length</span>
        </div>
        <div class="text-2xl font-bold text-blue-900 dark:text-blue-100">
          {{ setupArrow.arrow_length }}"
        </div>
        <div class="text-xs text-blue-700 dark:text-blue-300 mt-1">
          {{ getLengthCategory() }}
        </div>
      </div>
      
      <!-- Point Weight -->
      <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
        <div class="flex items-center mb-2">
          <i class="fas fa-bullseye text-green-600 dark:text-green-400 mr-2"></i>
          <span class="text-sm font-medium text-green-800 dark:text-green-200">Point Weight</span>
        </div>
        <div class="text-2xl font-bold text-green-900 dark:text-green-100">
          {{ setupArrow.point_weight }} gr
        </div>
        <div class="text-xs text-green-700 dark:text-green-300 mt-1">
          {{ getPointWeightCategory() }}
        </div>
      </div>
      
      <!-- Calculated Spine -->
      <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
        <div class="flex items-center mb-2">
          <i class="fas fa-chart-line text-purple-600 dark:text-purple-400 mr-2"></i>
          <span class="text-sm font-medium text-purple-800 dark:text-purple-200">Spine</span>
        </div>
        <div class="text-2xl font-bold text-purple-900 dark:text-purple-100">
          {{ getDisplaySpine() }}
        </div>
        <div class="text-xs text-purple-700 dark:text-purple-300 mt-1">
          {{ getSpineWeight() }} GPI
        </div>
      </div>
      
      <!-- Compatibility -->
      <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
        <div class="flex items-center mb-2">
          <i class="fas fa-star text-orange-600 dark:text-orange-400 mr-2"></i>
          <span class="text-sm font-medium text-orange-800 dark:text-orange-200">Compatibility</span>
        </div>
        <div class="text-2xl font-bold text-orange-900 dark:text-orange-100">
          {{ setupArrow.compatibility_score || 0 }}%
        </div>
        <div class="text-xs text-orange-700 dark:text-orange-300 mt-1">
          {{ getCompatibilityRating() }}
        </div>
      </div>
    </div>
    
    <!-- Weight Breakdown -->
    <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-6">
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-weight-hanging mr-2 text-gray-600"></i>
        Weight Breakdown
      </h4>
      
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <!-- Shaft Weight -->
        <div class="text-center">
          <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Shaft</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ calculateShaftWeight() }} gr
          </div>
        </div>
        
        <!-- Point Weight -->
        <div class="text-center">
          <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Point</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ setupArrow.point_weight || 0 }} gr
          </div>
        </div>
        
        <!-- Nock Weight -->
        <div class="text-center">
          <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Nock</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ setupArrow.nock_weight || 10 }} gr
          </div>
        </div>
        
        <!-- Insert Weight -->
        <div class="text-center">
          <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Insert</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ setupArrow.insert_weight || 0 }} gr
          </div>
        </div>
        
        <!-- Bushing Weight -->
        <div class="text-center">
          <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Bushing</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ setupArrow.bushing_weight || 0 }} gr
          </div>
        </div>
        
        <!-- Fletching Weight -->
        <div class="text-center">
          <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Fletching</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ setupArrow.fletching_weight || 15 }} gr
          </div>
        </div>
      </div>
      
      <!-- Total Weight -->
      <div class="border-t border-gray-200 dark:border-gray-700 mt-4 pt-4">
        <div class="flex items-center justify-between">
          <span class="text-lg font-medium text-gray-900 dark:text-gray-100">
            Total Arrow Weight:
          </span>
          <span class="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {{ calculateTotalWeight() }} grains
          </span>
        </div>
        <div class="flex items-center justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
          <span>Front of Center (FOC):</span>
          <span class="font-medium">{{ calculateFOC() }}%</span>
        </div>
      </div>
    </div>
    
    <!-- Spine Specification Details -->
    <div v-if="getSelectedSpineSpec()" class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-6">
      <h4 class="text-lg font-medium text-indigo-900 dark:text-indigo-100 mb-4">
        <i class="fas fa-info-circle mr-2 text-indigo-600"></i>
        Spine Specification Details
      </h4>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <div class="text-sm text-indigo-700 dark:text-indigo-300 mb-1">Outer Diameter</div>
          <div class="text-lg font-semibold text-indigo-900 dark:text-indigo-100">
            {{ getSelectedSpineSpec().outer_diameter?.toFixed(3) || 'N/A' }}"
          </div>
        </div>
        
        <div>
          <div class="text-sm text-indigo-700 dark:text-indigo-300 mb-1">Inner Diameter</div>
          <div class="text-lg font-semibold text-indigo-900 dark:text-indigo-100">
            {{ getSelectedSpineSpec().inner_diameter?.toFixed(3) || 'N/A' }}"
          </div>
        </div>
        
        <div>
          <div class="text-sm text-indigo-700 dark:text-indigo-300 mb-1">Wall Thickness</div>
          <div class="text-lg font-semibold text-indigo-900 dark:text-indigo-100">
            {{ calculateWallThickness() }}"
          </div>
        </div>
        
        <div>
          <div class="text-sm text-indigo-700 dark:text-indigo-300 mb-1">Length Options</div>
          <div class="text-sm text-indigo-900 dark:text-indigo-100">
            {{ getLengthOptions() }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Notes -->
    <div v-if="setupArrow.notes" class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
      <div class="flex items-start">
        <i class="fas fa-sticky-note text-yellow-600 dark:text-yellow-400 mr-3 mt-1"></i>
        <div>
          <h4 class="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">Notes</h4>
          <p class="text-yellow-700 dark:text-yellow-300 text-sm leading-relaxed">
            {{ setupArrow.notes }}
          </p>
        </div>
      </div>
    </div>
    
    <!-- Setup Information -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-500 dark:text-gray-400">
      <div>
        <strong>Created:</strong> {{ formatDate(setupArrow.created_at) }}
      </div>
      <div>
        <strong>Setup ID:</strong> {{ setupArrow.id }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  setupArrow: {
    type: Object,
    required: true
  },
  arrow: {
    type: Object,
    required: true
  },
  spineSpecifications: {
    type: Array,
    default: () => []
  }
})

// Computed
const getDisplaySpine = () => {
  return props.setupArrow.calculated_spine || 'N/A'
}

const getSelectedSpineSpec = () => {
  const spine = props.setupArrow.calculated_spine
  if (!spine) return null
  
  return props.spineSpecifications.find(spec => 
    spec.spine.toString() === spine.toString()
  )
}

const getSpineWeight = () => {
  const spineSpec = getSelectedSpineSpec()
  return spineSpec?.gpi_weight?.toFixed(1) || 'N/A'
}

const calculateShaftWeight = () => {
  const spineSpec = getSelectedSpineSpec()
  if (!spineSpec?.gpi_weight) return 0
  
  const gpi = spineSpec.gpi_weight
  const length = props.setupArrow.arrow_length || 32
  
  return Math.round(gpi * length * 10) / 10
}

const calculateTotalWeight = () => {
  const shaftWeight = calculateShaftWeight()
  const components = 
    (props.setupArrow.point_weight || 0) +
    (props.setupArrow.nock_weight || 10) +
    (props.setupArrow.insert_weight || 0) +
    (props.setupArrow.bushing_weight || 0) +
    (props.setupArrow.fletching_weight || 15)
    
  return Math.round((shaftWeight + components) * 10) / 10
}

const calculateFOC = () => {
  const arrowLength = props.setupArrow.arrow_length || 32
  const pointWeight = props.setupArrow.point_weight || 0
  const insertWeight = props.setupArrow.insert_weight || 0
  const nockWeight = props.setupArrow.nock_weight || 10
  const fletchingWeight = props.setupArrow.fletching_weight || 15
  const shaftWeight = calculateShaftWeight()
  
  const totalWeight = shaftWeight + pointWeight + insertWeight + nockWeight + fletchingWeight
  if (totalWeight === 0) return 0
  
  // Physics-based FOC calculation using component positions and moments
  // Component positions (from nock end in inches)
  const pointPosition = arrowLength  // Point at arrow tip
  const insertPosition = arrowLength - 0.5  // Insert ~0.5" from tip
  const shaftCenter = arrowLength / 2  // Shaft center
  const nockFletchingPosition = 0  // Nock and fletching at back
  
  // Calculate balance point using weighted moments
  const totalMoment = (pointWeight * pointPosition) + 
                     (insertWeight * insertPosition) +
                     (shaftWeight * shaftCenter) +
                     (nockWeight * nockFletchingPosition) +
                     (fletchingWeight * nockFletchingPosition)
  
  const balancePoint = totalMoment / totalWeight
  const physicalCenter = arrowLength / 2
  const focDistance = balancePoint - physicalCenter
  const focPercentage = (focDistance / arrowLength) * 100
  
  return Math.round(focPercentage * 10) / 10
}

const calculateWallThickness = () => {
  const spineSpec = getSelectedSpineSpec()
  if (!spineSpec?.outer_diameter || !spineSpec?.inner_diameter) return 'N/A'
  
  const thickness = (spineSpec.outer_diameter - spineSpec.inner_diameter) / 2
  return thickness.toFixed(4)
}

const getLengthOptions = () => {
  const spineSpec = getSelectedSpineSpec()
  if (!spineSpec?.length_options) {
    return 'Standard'
  }
  
  // Handle both array and string (JSON) formats
  let lengthOptions = spineSpec.length_options
  if (typeof lengthOptions === 'string') {
    try {
      lengthOptions = JSON.parse(lengthOptions)
    } catch {
      return spineSpec.length_options // Return as string if not valid JSON
    }
  }
  
  if (!Array.isArray(lengthOptions) || lengthOptions.length === 0) {
    return 'Standard'
  }
  
  return lengthOptions.map(l => `${l}"`).join(', ')
}

const getLengthCategory = () => {
  const length = props.setupArrow.arrow_length || 32
  if (length < 28) return 'Short'
  if (length < 30) return 'Standard'
  if (length < 32) return 'Long'
  return 'Extra Long'
}

const getPointWeightCategory = () => {
  const weight = props.setupArrow.point_weight || 100
  if (weight < 85) return 'Light'
  if (weight < 125) return 'Standard'
  if (weight < 150) return 'Heavy'
  return 'Extra Heavy'
}

const getCompatibilityRating = () => {
  const score = props.setupArrow.compatibility_score || 0
  if (score >= 90) return 'Excellent'
  if (score >= 80) return 'Very Good'
  if (score >= 70) return 'Good'
  if (score >= 60) return 'Fair'
  return 'Poor'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return 'Invalid date'
  }
}
</script>