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
    <PerformanceMetricsDisplay 
      v-if="performanceData?.performance_summary"
      :metrics="performanceData.performance_summary"
      :show-detailed="true"
    />
    
    <!-- Detailed Performance Breakdown -->
    <div v-if="performanceData?.performance_summary" class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 sm:p-6">
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-analytics mr-2 text-gray-600"></i>
        Detailed Analysis
      </h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
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
    <div v-if="performanceData?.performance_summary && props.arrow">
      <!-- Single TrajectoryChart with responsive prop -->
      <div class="bg-white dark:bg-gray-800 rounded-lg" :class="{'p-6': !isMobile, 'overflow-hidden': isMobile}">
        <TrajectoryChart 
          :arrow-data="getArrowDataForTrajectory()"
          :bow-config="getBowConfigForTrajectory()"
          :mobile-horizontal="isMobile"
          :key="trajectoryChartKey"
        />
      </div>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useApi } from '~/composables/useApi'
import { usePerformanceAnalysis } from '~/composables/usePerformanceAnalysis'
import PerformanceTooltip from '~/components/PerformanceTooltip.vue'
import PerformanceMetricsDisplay from '~/components/PerformanceMetricsDisplay.vue'
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
const { 
  calculateTotalWeight,
  formatSpeedValue,
  formatKineticEnergy,
  formatFocPercentage,
  formatMomentum,
  getSpeedRating,
  getKineticEnergyRating,
  getFOCRating,
  getPenetrationDescription,
  getPerformanceScoreClass,
  getPenetrationClass,
  getSpeedSourceClass,
  getSpeedSourceIcon,
  getSpeedSourceText
} = usePerformanceAnalysis()

// State
const isCalculating = ref(false)
const performanceData = ref(null)

// Mobile detection and trajectory chart state management
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)
const trajectoryChartKey = ref(0)

// Reactive mobile detection
const isMobile = computed(() => windowWidth.value < 640) // Tailwind 'sm' breakpoint

// Window resize handler to update mobile state
const handleResize = () => {
  const newWidth = window.innerWidth
  const wasMobile = windowWidth.value < 640
  const nowMobile = newWidth < 640
  
  windowWidth.value = newWidth
  
  // Force trajectory chart re-render when switching between mobile/desktop
  // This ensures the chart state is preserved across responsive changes
  if (wasMobile !== nowMobile) {
    trajectoryChartKey.value++
  }
}

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

// Performance helper functions (using shared composable)
const getPerformanceScore = (performanceSummary) => {
  if (!performanceSummary) return 0
  
  const keScore = Math.min(100, (performanceSummary.kinetic_energy_40yd / 80) * 100)
  const penetrationScore = performanceSummary.penetration_score || 0
  const focScore = performanceSummary.foc_percentage ? 
    Math.max(0, 100 - Math.abs((performanceSummary.foc_percentage || 0) - 12) * 5) : 50
  
  const compositeScore = (penetrationScore * 0.4) + (keScore * 0.3) + (focScore * 0.3)
  return Math.round(compositeScore)
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
    total_weight: calculateTotalWeightForAnalysis(),
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

const calculateTotalWeightForAnalysis = () => {
  return calculateTotalWeight(props.arrow, props.setupArrow)
}

// Speed source indicator methods are now handled by the shared composable

// Lifecycle
onMounted(() => {
  // Add window resize listener for mobile detection
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', handleResize)
    // Initial size detection
    handleResize()
  }
})

onUnmounted(() => {
  // Remove window resize listener
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleResize)
  }
})

watch(() => props.setupArrow.performance, (newPerformance) => {
  if (newPerformance && !performanceData.value) {
    // Only set initial data if we don't already have performance data
    // This prevents overwriting calculated data when props change
    performanceData.value = newPerformance
  }
}, { immediate: true })
</script>