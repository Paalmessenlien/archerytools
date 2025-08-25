<template>
  <div class="space-y-6">
    <!-- Live Performance Header -->
    <div class="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
      <div class="flex items-start">
        <i class="fas fa-chart-line text-green-600 dark:text-green-400 mr-3 mt-1"></i>
        <div class="flex-1">
          <h5 class="text-sm font-medium text-green-800 dark:text-green-200 mb-2">
            <i class="fas fa-bolt mr-1"></i>
            Live Performance Preview
          </h5>
          <p class="text-sm text-green-700 dark:text-green-300">
            Real-time calculations update as you modify arrow specifications. Performance based on your bow setup.
          </p>
        </div>
        <div class="flex items-center space-x-2 text-xs">
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
            <span class="text-green-600 dark:text-green-400">Live</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Performance Metrics Display -->
    <PerformanceMetricsDisplay 
      v-if="liveMetrics"
      :metrics="liveMetrics"
      :show-weight="true"
    />
    
    <!-- Loading State -->
    <div v-else class="text-center py-8">
      <div class="animate-spin h-6 w-6 border-2 border-green-500 border-t-transparent rounded-full mx-auto mb-3"></div>
      <p class="text-sm text-gray-600 dark:text-gray-400">Calculating performance...</p>
    </div>
    
    <!-- Draw Length Information -->
    <div v-if="drawLengthInfo.source" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-ruler text-blue-600 dark:text-blue-400 mr-3"></i>
        <div class="flex-1">
          <h5 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-1">
            Draw Length Used in Calculations
          </h5>
          <div class="flex items-center space-x-4">
            <div class="flex items-center">
              <span class="text-lg font-bold text-blue-700 dark:text-blue-300 mr-2">
                {{ drawLengthInfo.length }}"
              </span>
              <span class="text-sm text-blue-600 dark:text-blue-400">
                {{ drawLengthInfo.source }}
              </span>
            </div>
            <div class="text-xs text-blue-500 dark:text-blue-400">
              <i class="fas fa-info-circle mr-1"></i>
              {{ getBowTypeMessage() }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Trajectory Preview (if available) -->
    <div v-if="showTrajectory && liveMetrics?.estimatedSpeed" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        <i class="fas fa-crosshairs mr-2"></i>
        Trajectory Preview
      </h5>
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">Max Height:</span>
          <span class="font-medium text-gray-900 dark:text-gray-100">{{ trajectoryData.maxHeight }}"</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">Drop @ 40yd:</span>
          <span class="font-medium text-gray-900 dark:text-gray-100">{{ Math.abs(trajectoryData.drop40yd) }}"</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { usePerformanceAnalysis } from '~/composables/usePerformanceAnalysis'
import PerformanceMetricsDisplay from '~/components/PerformanceMetricsDisplay.vue'

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
  showTrajectory: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['performance-updated'])

// Use the shared performance analysis composable
const { 
  calculateLivePreview,
  calculateTotalWeight,
  estimateArrowSpeed
} = usePerformanceAnalysis()

// State
const liveMetrics = ref(null)
const trajectoryData = ref({ maxHeight: 0, drop40yd: 0 })

// Update live calculations when data changes
const updateLiveCalculations = () => {
  if (!props.setupArrow || !props.bowConfig || !props.arrow) return
  
  // Calculate live performance using the shared composable
  const performance = calculateLivePreview(props.arrow, props.bowConfig, props.setupArrow)
  
  if (performance) {
    liveMetrics.value = {
      totalWeight: performance.totalWeight,
      estimatedSpeed: performance.estimatedSpeed,
      kineticEnergy: performance.kineticEnergy,
      foc: performance.foc,
      performanceScore: performance.performanceScore,
      speedSource: performance.speedSource
    }
    
    // Calculate simplified trajectory data
    if (props.showTrajectory) {
      calculateSimpleTrajectory(performance.estimatedSpeed)
    }
    
    // Emit the performance update for parent components
    emit('performance-updated', performance)
  }
}

// Calculate simplified trajectory for preview
const calculateSimpleTrajectory = (speed) => {
  if (!speed || speed <= 0) return
  
  // Simplified ballistic calculation
  const distances = [10, 20, 30, 40, 50]
  let maxHeight = 0
  let drop40yd = 0
  
  distances.forEach(distance => {
    const timeToTarget = distance * 3 / speed
    const gravityDrop = 16.1 * timeToTarget * timeToTarget
    const sightHeight = 7
    const zeroDistance = 20
    
    let drop = gravityDrop - sightHeight
    
    if (distance <= zeroDistance) {
      drop = drop + (sightHeight * (zeroDistance - distance) / zeroDistance)
    }
    
    const height = Math.abs(drop)
    if (height > maxHeight) maxHeight = height
    if (distance === 40) drop40yd = Math.round(drop * 10) / 10
  })
  
  trajectoryData.value = {
    maxHeight: Math.round(maxHeight * 10) / 10,
    drop40yd
  }
}

// Draw Length Information
const drawLengthInfo = computed(() => {
  // Check if performance data includes draw length source info
  const performance = props.setupArrow?.performance
  if (performance && performance.draw_length_source && performance.effective_draw_length) {
    return {
      length: performance.effective_draw_length,
      source: performance.draw_length_source
    }
  }
  
  // Fallback to bow config info
  const bowType = props.bowConfig?.bow_type || 'compound'
  const drawLength = props.bowConfig?.draw_length || 28
  
  if (bowType.toLowerCase() === 'compound') {
    return {
      length: drawLength,
      source: `Bow mechanical setting (${drawLength}")`
    }
  } else {
    return {
      length: drawLength,
      source: `User measurement (${drawLength}")`
    }
  }
})

const getBowTypeMessage = () => {
  const bowType = props.bowConfig?.bow_type || 'compound'
  
  if (bowType.toLowerCase() === 'compound') {
    return 'Mechanical draw length from bow module'
  } else {
    return 'Measured draw length for traditional bows'
  }
}

// Watch for changes and update calculations
watch([() => props.setupArrow, () => props.bowConfig, () => props.arrow], 
  updateLiveCalculations, 
  { deep: true, immediate: true }
)

// Initial calculation
onMounted(() => {
  updateLiveCalculations()
})
</script>