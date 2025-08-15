<template>
  <div class="space-y-4">
    <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
      <div class="flex items-start">
        <i class="fas fa-flask text-yellow-600 dark:text-yellow-400 mr-3 mt-1"></i>
        <div>
          <h5 class="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
            Performance Preview (Experimental)
          </h5>
          <p class="text-sm text-yellow-700 dark:text-yellow-300">
            Real-time performance preview is coming soon. Save your changes to see updated performance calculations.
          </p>
        </div>
      </div>
    </div>
    
    <!-- Basic Calculations Preview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">Total Weight</div>
        <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ calculateTotalWeight() }} gr</div>
      </div>
      
      <div class="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">Est. FOC</div>
        <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ calculateEstimatedFOC() }}%</div>
      </div>
      
      <div class="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">Change</div>
        <div class="text-lg font-semibold" :class="getChangeClass()">
          {{ getWeightChange() }} gr
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  setupArrow: {
    type: Object,
    required: true
  },
  bowConfig: {
    type: Object,
    required: true
  },
  arrow: {
    type: Object,
    required: true
  },
  originalPerformance: {
    type: Object,
    default: null
  }
})

// Helper methods
const calculateTotalWeight = () => {
  // Calculate shaft weight using GPI
  let shaftWeight = 0
  if (props.arrow?.spine_specifications?.length > 0) {
    const spineSpec = props.arrow.spine_specifications.find(spec => 
      spec.spine.toString() === props.setupArrow.calculated_spine?.toString()
    ) || props.arrow.spine_specifications[0]
    
    if (spineSpec?.gpi_weight) {
      shaftWeight = spineSpec.gpi_weight * (props.setupArrow.arrow_length || 32)
    }
  }
  
  // Add component weights
  const componentWeight = 
    (props.setupArrow.point_weight || 0) +
    (props.setupArrow.nock_weight || 10) +
    (props.setupArrow.insert_weight || 0) +
    (props.setupArrow.bushing_weight || 0) +
    (props.setupArrow.fletching_weight || 15)
  
  return Math.round((shaftWeight + componentWeight) * 10) / 10
}

const calculateEstimatedFOC = () => {
  const totalWeight = calculateTotalWeight()
  const pointWeight = props.setupArrow.point_weight || 0
  const insertWeight = props.setupArrow.insert_weight || 0
  
  if (totalWeight === 0) return 0
  
  // Simplified FOC estimation
  const frontWeight = pointWeight + insertWeight
  const foc = (frontWeight / totalWeight) * 15 // Simplified formula
  
  return Math.round(foc * 10) / 10
}

const getWeightChange = () => {
  if (!props.originalPerformance?.total_arrow_weight) return 0
  
  const currentWeight = calculateTotalWeight()
  const originalWeight = props.originalPerformance.total_arrow_weight
  const change = currentWeight - originalWeight
  
  return change > 0 ? `+${change.toFixed(1)}` : change.toFixed(1)
}

const getChangeClass = () => {
  const change = parseFloat(getWeightChange())
  if (change > 0) return 'text-green-600 dark:text-green-400'
  if (change < 0) return 'text-red-600 dark:text-red-400'
  return 'text-gray-600 dark:text-gray-400'
}
</script>