<template>
  <div class="space-y-6">
    <!-- Header - Mobile & Desktop Responsive -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
      <!-- Title -->
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 min-w-0">
        <i class="fas fa-chart-line mr-3 text-green-600"></i>
        Performance Analysis
      </h3>
      
      <!-- Controls Section -->
      <div class="flex flex-col sm:flex-row sm:items-center gap-3 lg:gap-4">
        <!-- Overall Score -->
        <div v-if="performanceData?.performance_summary" class="flex items-center space-x-2 justify-center sm:justify-start">
          <span class="text-sm text-gray-600 dark:text-gray-400">Overall Score:</span>
          <span :class="getPerformanceScoreClass(performanceData.performance_summary)" class="text-xl font-bold">
            {{ getPerformanceScore(performanceData.performance_summary) }}/100
          </span>
          <PerformanceTooltip 
            :title="'Overall Performance Score'"
            :content="'Composite score based on speed, kinetic energy, FOC, and arrow efficiency. Higher scores (80+) indicate excellent performance for hunting and target shooting.'"
          />
        </div>
        
        <!-- Calculate/Recalculate Button -->
        <button
          @click="calculatePerformance"
          :disabled="isCalculating"
          class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-lg transition-colors w-full sm:w-auto whitespace-nowrap"
          :class="performanceData?.performance_summary 
            ? 'text-blue-600 border border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900/20' 
            : 'text-white bg-green-600 hover:bg-green-700'"
        >
          <i :class="isCalculating ? 'fas fa-spinner fa-spin' : 'fas fa-calculator'" class="mr-2"></i>
          <span class="hidden sm:inline">{{ isCalculating ? 'Calculating...' : (performanceData?.performance_summary ? 'Recalculate' : 'Calculate Performance') }}</span>
          <span class="sm:hidden">{{ isCalculating ? 'Calculating...' : (performanceData?.performance_summary ? 'Recalculate' : 'Calculate') }}</span>
        </button>
      </div>
    </div>
    
    <!-- Performance Metrics Display -->
    <div v-if="performanceData?.performance_summary" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Speed -->
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
        <div class="flex items-center justify-between mb-2">
          <div class="text-lg font-bold text-blue-600 dark:text-blue-400">
            {{ formatSpeedValue(performanceData.performance_summary.estimated_speed_fps) }}
          </div>
          <PerformanceTooltip 
            :title="'Arrow Speed'"
            :content="'Estimated arrow velocity in feet per second. Faster arrows have flatter trajectory and less wind drift. Typical hunting speeds: 250-350 fps.'"
          />
        </div>
        <div class="text-sm text-blue-800 dark:text-blue-200 font-medium">Speed</div>
        <div class="text-xs text-blue-600 dark:text-blue-400 mt-1">
          {{ getSpeedRating(performanceData.performance_summary.estimated_speed_fps) }}
        </div>
        <!-- Speed Source & Confidence Indicator -->
        <div v-if="performanceData.performance_summary.speed_source" class="flex items-center justify-between mt-2">
          <div class="flex items-center">
            <span class="text-xs px-2 py-1 rounded-full" :class="getSpeedSourceClass(performanceData.performance_summary.speed_source)">
              <i :class="getSpeedSourceIcon(performanceData.performance_summary.speed_source)" class="mr-1"></i>
              {{ getSpeedSourceText(performanceData.performance_summary.speed_source) }}
            </span>
          </div>
          <div v-if="performanceData.performance_summary.confidence" class="text-xs text-blue-600 dark:text-blue-400">
            {{ performanceData.performance_summary.confidence }}% confidence
          </div>
        </div>
      </div>
      
      <!-- Kinetic Energy -->
      <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
        <div class="flex items-center justify-between mb-2">
          <div class="text-lg font-bold text-green-600 dark:text-green-400">
            {{ formatKineticEnergy(performanceData.performance_summary.kinetic_energy_40yd) }}
          </div>
          <PerformanceTooltip 
            :title="'Kinetic Energy at 40 Yards'"
            :content="'Energy remaining after 40 yards of flight. Determines penetration power. Standards: 25+ ft·lbs (small game), 40+ ft·lbs (deer), 65+ ft·lbs (elk).'"
          />
        </div>
        <div class="text-sm text-green-800 dark:text-green-200 font-medium">KE @40yd</div>
        <div class="text-xs text-green-600 dark:text-green-400 mt-1">
          {{ getKineticEnergyRating(performanceData.performance_summary.kinetic_energy_40yd) }}
        </div>
      </div>
      
      <!-- FOC -->
      <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
        <div class="flex items-center justify-between mb-2">
          <div class="text-lg font-bold text-purple-600 dark:text-purple-400">
            {{ formatFocPercentage(performanceData.performance_summary.foc_percentage) }}
          </div>
          <PerformanceTooltip 
            :title="'Front of Center (FOC)'"
            :content="'How much weight is forward of the arrow center. Higher FOC improves stability and penetration. Recommended: 10-15% (target), 15-20% (hunting).'"
          />
        </div>
        <div class="text-sm text-purple-800 dark:text-purple-200 font-medium">FOC</div>
        <div class="text-xs text-purple-600 dark:text-purple-400 mt-1">
          {{ getFOCRating(performanceData.performance_summary.foc_percentage) }}
        </div>
      </div>
      
      <!-- Penetration -->
      <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
        <div class="flex items-center justify-between mb-2">
          <div :class="getPenetrationClass(performanceData.performance_summary.penetration_category)" class="text-lg font-bold capitalize">
            {{ performanceData.performance_summary.penetration_category }}
          </div>
          <PerformanceTooltip 
            :title="'Penetration Rating'"
            :content="'Overall penetration capability based on kinetic energy and arrow design. Categories: poor, fair, good, excellent. Higher ratings indicate better ability to penetrate through bone and tissue.'"
          />
        </div>
        <div class="text-sm text-orange-800 dark:text-orange-200 font-medium">Penetration</div>
        <div class="text-xs text-orange-600 dark:text-orange-400 mt-1">
          {{ getPenetrationDescription(performanceData.performance_summary.penetration_category) }}
        </div>
      </div>
    </div>
    
    <!-- Detailed Performance Breakdown -->
    <div v-if="performanceData?.performance_summary" class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-6">
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-analytics mr-2 text-gray-600"></i>
        Detailed Analysis
      </h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Performance Metrics -->
        <div class="space-y-3">
          <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300">Performance Metrics</h5>
          <div class="space-y-2 text-sm">
            <div class="flex items-center justify-between">
              <span class="text-gray-600 dark:text-gray-400">Initial Kinetic Energy:</span>
              <span class="font-medium text-gray-900 dark:text-gray-100">
                {{ formatKineticEnergy(performanceData.performance_summary.kinetic_energy_initial || 0) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-600 dark:text-gray-400">Momentum:</span>
              <span class="font-medium text-gray-900 dark:text-gray-100">
                {{ formatMomentum(performanceData.performance_summary.momentum || 0) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-600 dark:text-gray-400">Energy Retention @40yd:</span>
              <span class="font-medium text-gray-900 dark:text-gray-100">
                {{ calculateEnergyRetention() }}%
              </span>
            </div>
          </div>
        </div>
        
        <!-- Recommendations -->
        <div class="space-y-3">
          <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300">Recommendations</h5>
          <div class="space-y-2">
            <div v-for="recommendation in getRecommendations()" :key="recommendation.type" 
                 class="flex items-start space-x-2 text-sm">
              <i :class="recommendation.icon" class="mt-0.5 text-xs"></i>
              <span :class="recommendation.color">{{ recommendation.text }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Trajectory Chart -->
    <div v-if="performanceData?.performance_summary && props.arrow" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <TrajectoryChart 
        :arrow-data="getArrowDataForTrajectory()"
        :bow-config="getBowConfigForTrajectory()"
      />
    </div>
    
    <!-- No Performance Data -->
    <div v-else-if="!isCalculating" class="text-center py-8 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
      <i class="fas fa-calculator text-4xl text-gray-400 mb-4"></i>
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Performance Data</h4>
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        Calculate performance metrics to see detailed ballistics analysis and flight trajectory
      </p>
      <button
        @click="calculatePerformance"
        class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
      >
        <i class="fas fa-calculator mr-2"></i>
        Calculate Performance
      </button>
    </div>
    
    <!-- Calculating State -->
    <div v-else class="text-center py-8">
      <div class="animate-spin h-8 w-8 border-4 border-green-500 border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-600 dark:text-gray-400">Calculating performance metrics...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import PerformanceTooltip from '~/components/PerformanceTooltip.vue'
import TrajectoryChart from '~/components/TrajectoryChart.vue'

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
  }
})

const emit = defineEmits(['performance-updated'])

// Composables
const api = useApi()

// State
const isCalculating = ref(false)
const performanceData = ref(null)

// Computed
const hasPerformanceData = computed(() => {
  return performanceData.value?.performance_summary || props.setupArrow.performance?.performance_summary
})

// Methods
const calculatePerformance = async () => {
  if (!canCalculatePerformance()) return
  
  isCalculating.value = true
  try {
    const response = await api.post(`/setup-arrows/${props.setupArrow.id}/calculate-performance`, {
      bow_config: {
        draw_weight: props.bowConfig.draw_weight,
        draw_length: props.bowConfig.draw_length,
        bow_type: props.bowConfig.bow_type || 'compound',
        ibo_speed: props.bowConfig.ibo_speed || 320
      }
    })
    
    if (response.performance) {
      performanceData.value = response.performance
      emit('performance-updated', response.performance)
    }
  } catch (error) {
    console.error('Error calculating performance:', error)
  } finally {
    isCalculating.value = false
  }
}

const canCalculatePerformance = () => {
  return props.setupArrow.arrow_length && 
         props.setupArrow.point_weight && 
         props.bowConfig.draw_weight
}

// Performance helper functions
const getPerformanceScore = (performanceSummary) => {
  if (!performanceSummary) return 0
  
  const keScore = Math.min(100, (performanceSummary.kinetic_energy_40yd / 80) * 100)
  const penetrationScore = performanceSummary.penetration_score || 0
  const focScore = performanceSummary.foc_percentage ? 
    Math.max(0, 100 - Math.abs((performanceSummary.foc_percentage || 0) - 12) * 5) : 50
  
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

// Formatting functions
const formatSpeedValue = (speed) => {
  if (!speed) return '0 fps'
  return `${parseFloat(speed).toFixed(1)} fps`
}

const formatKineticEnergy = (ke) => {
  if (!ke) return '0 ft·lbs'
  return `${parseFloat(ke).toFixed(2)} ft·lbs`
}

const formatFocPercentage = (foc) => {
  if (!foc) return '0%'
  return `${parseFloat(foc).toFixed(1)}%`
}

const formatMomentum = (momentum) => {
  if (!momentum) return '0 slug·fps'
  return `${parseFloat(momentum).toFixed(2)} slug·fps`
}

// Rating functions
const getSpeedRating = (speed) => {
  if (speed >= 350) return 'Very Fast'
  if (speed >= 300) return 'Fast'
  if (speed >= 250) return 'Moderate'
  return 'Slow'
}

const getKineticEnergyRating = (ke) => {
  if (ke >= 65) return 'Excellent (Elk+)'
  if (ke >= 40) return 'Good (Deer)'
  if (ke >= 25) return 'Fair (Small Game)'
  return 'Low'
}

const getFOCRating = (foc) => {
  if (foc >= 15 && foc <= 20) return 'Optimal (Hunting)'
  if (foc >= 10 && foc <= 15) return 'Good (Target)'
  if (foc >= 8 && foc <= 22) return 'Acceptable'
  return 'Suboptimal'
}

const getPenetrationDescription = (category) => {
  switch (category) {
    case 'excellent': return 'Maximum penetration'
    case 'good': return 'Good penetration'
    case 'fair': return 'Limited penetration'
    case 'poor': return 'Poor penetration'
    default: return 'Unknown'
  }
}

const calculateEnergyRetention = () => {
  const summary = performanceData.value?.performance_summary
  if (!summary?.kinetic_energy_initial || !summary?.kinetic_energy_40yd) return 0
  
  const retention = (summary.kinetic_energy_40yd / summary.kinetic_energy_initial) * 100
  return Math.round(retention)
}

const getRecommendations = () => {
  const summary = performanceData.value?.performance_summary
  if (!summary) return []
  
  const recommendations = []
  
  // Speed recommendations
  if (summary.estimated_speed_fps < 280) {
    recommendations.push({
      type: 'speed',
      icon: 'fas fa-exclamation-triangle text-yellow-500',
      color: 'text-yellow-700 dark:text-yellow-300',
      text: 'Consider lighter arrows or higher draw weight for better speed'
    })
  }
  
  // KE recommendations
  if (summary.kinetic_energy_40yd < 40) {
    recommendations.push({
      type: 'ke',
      icon: 'fas fa-info-circle text-blue-500',
      color: 'text-blue-700 dark:text-blue-300',
      text: 'Increase arrow weight or draw weight for better penetration'
    })
  }
  
  // FOC recommendations
  const foc = summary.foc_percentage
  if (foc < 10 || foc > 20) {
    recommendations.push({
      type: 'foc',
      icon: 'fas fa-balance-scale text-purple-500',
      color: 'text-purple-700 dark:text-purple-300',
      text: 'Adjust point weight for optimal FOC (10-20%)'
    })
  }
  
  // Default positive recommendation
  if (recommendations.length === 0) {
    recommendations.push({
      type: 'good',
      icon: 'fas fa-check-circle text-green-500',
      color: 'text-green-700 dark:text-green-300',
      text: 'Excellent arrow setup for your bow configuration'
    })
  }
  
  return recommendations
}

// Trajectory chart data
const getArrowDataForTrajectory = () => {
  if (!performanceData.value?.performance_summary) return {}
  
  const performance = performanceData.value.performance_summary
  
  return {
    estimated_speed_fps: performance.estimated_speed_fps || 280,
    total_weight: calculateTotalWeight(),
    outer_diameter: props.arrow?.spine_specifications?.[0]?.outer_diameter || 0.246,
    arrow_type: props.arrow?.arrow_type || 'hunting',
    manufacturer: props.arrow?.manufacturer || 'Unknown',
    model_name: props.arrow?.model_name || 'Unknown',
    spine: props.setupArrow.calculated_spine,
    // Include IDs for chronograph data lookup in trajectory calculation
    setup_id: props.setupArrow.setup_id,
    arrow_id: props.setupArrow.arrow_id,
    // Include source information if available
    speed_source: performance.speed_source || 'estimated'
  }
}

const getBowConfigForTrajectory = () => {
  return {
    drawWeight: props.bowConfig.draw_weight || 60,
    bowType: props.bowConfig.bow_type || 'compound',
    drawLength: props.bowConfig.draw_length || 28
  }
}

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
  const pointWeight = props.setupArrow.point_weight || 0
  const nockWeight = props.setupArrow.nock_weight || 10
  const insertWeight = props.setupArrow.insert_weight || 0
  const bushingWeight = props.setupArrow.bushing_weight || 0
  const fletchingWeight = props.setupArrow.fletching_weight || 15
  
  const totalWeight = shaftWeight + pointWeight + nockWeight + insertWeight + bushingWeight + fletchingWeight
  
  return Math.round(totalWeight * 10) / 10
}

// Speed source indicator methods
const getSpeedSourceClass = (source) => {
  if (source === 'chronograph') {
    return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
  } else if (source === 'enhanced_estimated') {
    return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
  } else {
    return 'bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-200'
  }
}

const getSpeedSourceIcon = (source) => {
  if (source === 'chronograph') {
    return 'fas fa-tachometer-alt'
  } else if (source === 'enhanced_estimated') {
    return 'fas fa-cog'
  } else {
    return 'fas fa-calculator'
  }
}

const getSpeedSourceText = (source) => {
  if (source === 'chronograph') {
    return 'Measured'
  } else if (source === 'enhanced_estimated') {
    return 'Enhanced'
  } else {
    return 'Estimated'
  }
}

// Lifecycle
watch(() => props.setupArrow.performance, (newPerformance) => {
  if (newPerformance) {
    performanceData.value = newPerformance
  }
}, { immediate: true })
</script>