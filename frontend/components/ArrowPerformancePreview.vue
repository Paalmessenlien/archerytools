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
    
    <!-- Core Performance Metrics -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <!-- Total Weight -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 text-center">
        <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">Total Weight</div>
        <div class="text-xl font-bold text-gray-900 dark:text-gray-100">{{ liveCalculations.totalWeight }} gr</div>
        <div class="text-xs mt-1" :class="getChangeClass('weight')">
          {{ getWeightChange() }}
        </div>
      </div>
      
      <!-- Estimated Speed -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 text-center">
        <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">Speed</div>
        <div class="text-xl font-bold text-blue-600 dark:text-blue-400">{{ liveCalculations.estimatedSpeed }} FPS</div>
        <div class="text-xs mt-1" :class="getChangeClass('speed')">
          {{ getSpeedChange() }}
        </div>
        <!-- Speed Source Indicator -->
        <div v-if="liveCalculations.speedSource" class="flex items-center justify-center mt-1">
          <span class="text-xs px-1.5 py-0.5 rounded-full" :class="getSpeedSourceClass(liveCalculations.speedSource)">
            <i :class="getSpeedSourceIcon(liveCalculations.speedSource)" class="mr-1"></i>
            {{ getSpeedSourceText(liveCalculations.speedSource) }}
          </span>
        </div>
      </div>
      
      <!-- Kinetic Energy -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 text-center">
        <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">Kinetic Energy</div>
        <div class="text-xl font-bold text-red-600 dark:text-red-400">{{ liveCalculations.kineticEnergy }} ft-lbs</div>
        <div class="text-xs mt-1" :class="getChangeClass('energy')">
          {{ getEnergyChange() }}
        </div>
      </div>
      
      <!-- FOC -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 text-center">
        <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">FOC</div>
        <div class="text-xl font-bold text-purple-600 dark:text-purple-400">{{ liveCalculations.foc }}%</div>
        <div class="text-xs mt-1" :class="getChangeClass('foc')">
          {{ getFOCChange() }}
        </div>
      </div>
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

    <!-- Flight Trajectory Visualization using TrajectoryChart -->
    <div v-if="hasValidTrajectoryData" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <TrajectoryChart 
        :arrow-data="getArrowDataForTrajectory()"
        :bow-config="getBowConfigForTrajectory()"
        :mobile-horizontal="false"
        :key="trajectoryChartKey"
      />
    </div>

    <!-- Detailed Ballistics Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-table mr-2 text-green-600"></i>
        Ballistics Table
      </h4>
      
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th class="text-left py-2 text-gray-600 dark:text-gray-400">Distance</th>
              <th class="text-right py-2 text-gray-600 dark:text-gray-400">Speed</th>
              <th class="text-right py-2 text-gray-600 dark:text-gray-400">Drop</th>
              <th class="text-right py-2 text-gray-600 dark:text-gray-400">Energy</th>
              <th class="text-right py-2 text-gray-600 dark:text-gray-400">Time</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="point in ballisticsTable" 
              :key="point.distance"
              class="border-b border-gray-100 dark:border-gray-800"
            >
              <td class="py-2 font-medium">{{ point.distance }} yd</td>
              <td class="text-right py-2">{{ point.speed }} FPS</td>
              <td class="text-right py-2" :class="point.drop < 0 ? 'text-red-600 dark:text-red-400' : ''">
                {{ point.drop }}"
              </td>
              <td class="text-right py-2">{{ point.energy }} ft-lbs</td>
              <td class="text-right py-2">{{ point.time }}s</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Performance Recommendations -->
    <div v-if="performanceRecommendations.length > 0" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <h5 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
        <i class="fas fa-lightbulb mr-1"></i>
        Performance Insights
      </h5>
      <ul class="space-y-1">
        <li 
          v-for="recommendation in performanceRecommendations" 
          :key="recommendation.text"
          class="text-sm text-blue-700 dark:text-blue-300 flex items-start"
        >
          <i :class="recommendation.icon" class="mr-2 mt-0.5 text-xs"></i>
          {{ recommendation.text }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useTrajectoryCalculation } from '~/composables/useTrajectoryCalculation'
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
  },
  originalPerformance: {
    type: Object,
    default: null
  }
})

// Use the unified trajectory calculation composable
const {
  isCalculating: isLoadingPerformance,
  trajectoryData: apiPerformanceData,
  error,
  hasTrajectoryData,
  performanceSummary,
  trajectoryPoints,
  calculateTrajectory,
  calculateSimplifiedTrajectory,
  buildArrowData,
  buildBowConfig
} = useTrajectoryCalculation()

// TrajectoryChart integration
const trajectoryChartKey = ref(0)

// TrajectoryChart helper functions (same as ArrowPerformanceAnalysis)
const getArrowDataForTrajectory = async () => {
  const arrowData = await buildArrowData(props.setupArrow, props.arrow)
  
  return {
    estimated_speed_fps: arrowData.estimated_speed_fps || 280,
    total_weight: arrowData.total_weight,
    outer_diameter: arrowData.outer_diameter,
    arrow_type: arrowData.arrow_type,
    manufacturer: arrowData.manufacturer,
    model_name: arrowData.model_name,
    spine: arrowData.spine,
    setup_id: arrowData.setup_id,
    arrow_id: arrowData.arrow_id,
    speed_source: arrowData.speed_source
  }
}

const getBowConfigForTrajectory = () => {
  return buildBowConfig(props.bowConfig)
}

const hasValidTrajectoryData = computed(() => {
  return !!(props.setupArrow && props.arrow && props.bowConfig)
})

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
      source: `Archer draw length (${bowType}, ${drawLength}")`
    }
  }
})

const getBowTypeMessage = () => {
  const bowType = props.bowConfig?.bow_type?.toLowerCase() || 'compound'
  
  if (bowType === 'compound') {
    return 'Compound bows use mechanical draw length set on the bow'
  } else if (bowType === 'recurve') {
    return 'Recurve bows use the archer\'s physical draw length'
  } else if (bowType === 'traditional') {
    return 'Traditional bows use the archer\'s physical draw length'
  } else {
    return 'Draw length source depends on bow type'
  }
}

// Unified API Performance Calculation using the composable
const calculatePerformanceAPI = async () => {
  const bowConfig = buildBowConfig(props.bowConfig)
  
  try {
    // Use the unified trajectory calculation with default environmental conditions
    const result = await calculateTrajectory(props.setupArrow, props.arrow, bowConfig)
    
    // Check if we actually got valid trajectory data, not just a truthy response
    if (!result || !hasTrajectoryData.value) {
      console.warn('API Performance calculation failed, using fallback - no valid trajectory data returned')
    }
  } catch (error) {
    console.warn('API Performance calculation failed, using fallback - exception:', error)
  }
}

// Helper function for total weight calculation (using composable)
const calculateTotalWeight = async () => {
  const arrowData = await buildArrowData(props.setupArrow, props.arrow)
  return arrowData.total_weight
}

// Helper function for simple trajectory calculation
const calculateTrajectoryPoints = (speed, weight) => {
  const points = []
  const distances = Array.from({length: 21}, (_, i) => i * 5) // 0 to 100 yards
  
  let maxHeight = 0
  let drop40yd = 0
  
  distances.forEach(distance => {
    if (distance === 0) {
      points.push({ distance: 0, drop: 0, height: 0 })
      return
    }
    
    // Simplified ballistic trajectory calculation
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
    
    points.push({
      distance,
      drop: Math.round(drop * 10) / 10,
      height: Math.round(height * 10) / 10
    })
  })
  
  return {
    points,
    maxHeight: Math.round(maxHeight * 10) / 10,
    drop40yd
  }
}

// Reactive state for live calculations
const liveCalculationsState = ref({
  totalWeight: 0,
  estimatedSpeed: 280,
  kineticEnergy: 0,
  foc: 12,
  trajectory: { points: [], maxHeight: 0, drop40yd: 0 },
  maxHeight: 0,
  drop40yd: 0,
  speedSource: 'estimated',
  confidence: null
})

// Update live calculations when data changes
const updateLiveCalculations = async () => {
  try {
    // Use API data from the composable when available
    if (hasTrajectoryData.value && performanceSummary.value) {
      const performance = performanceSummary.value
      const trajectory = trajectoryPoints.value || []
      
      // Find max height and 40yd drop from trajectory data
      const maxHeight = trajectory.length > 0 ? Math.max(...trajectory.map(p => p.height_inches - 7.0)) : 0
      const point40yd = trajectory.find(p => Math.abs(p.distance_yards - 40) <= 2)
      const drop40yd = point40yd ? Math.abs(point40yd.height_inches - 7.0) : 0
      
      liveCalculationsState.value = {
        totalWeight: Math.round((performance.total_arrow_weight || await calculateTotalWeight()) * 10) / 10,
        estimatedSpeed: Math.round(performance.estimated_speed_fps || 0),
        kineticEnergy: Math.round((performance.kinetic_energy_40yd || 0) * 10) / 10,
        foc: Math.round((performance.foc_percentage || 0) * 10) / 10,
        trajectory: {
          points: trajectory.map(p => ({
            distance: p.distance_yards,
            drop: Math.round((p.height_inches - 7.0) * 10) / 10,
            height: Math.round(Math.abs(p.height_inches - 7.0) * 10) / 10
          })),
          maxHeight: Math.round(maxHeight * 10) / 10,
          drop40yd: Math.round(drop40yd * 10) / 10
        },
        maxHeight: Math.round(maxHeight * 10) / 10,
        drop40yd: Math.round(drop40yd * 10) / 10,
        speedSource: performance.speed_source || 'estimated',
        confidence: performance.confidence
      }
      return
    }
    
    // Fallback to simplified calculations using the composable
    const bowConfig = buildBowConfig(props.bowConfig)
    
    // Check for chronograph data first to ensure consistency with Performance Analysis
    let chronographSpeed = null
    if (props.setupArrow.setup_id && props.setupArrow.arrow_id) {
      try {
        const { getChronographSpeed } = useTrajectoryCalculation()
        chronographSpeed = await getChronographSpeed(props.setupArrow.setup_id, props.setupArrow.arrow_id)
        if (chronographSpeed) {
          console.log('🎯 Live Preview using chronograph data:', chronographSpeed, 'fps')
        }
      } catch (error) {
        console.warn('Live Preview chronograph check failed:', error)
      }
    }
    
    const simplified = await calculateSimplifiedTrajectory(props.setupArrow, props.arrow, bowConfig)
    
    if (simplified.performance_summary) {
      const performance = simplified.performance_summary
      
      // Override with chronograph data if available to ensure consistency
      const finalSpeed = chronographSpeed || performance.estimated_speed_fps
      const finalSpeedSource = chronographSpeed ? 'chronograph' : performance.speed_source
      
      const simpleTrajectory = calculateTrajectoryPoints(finalSpeed, performance.total_arrow_weight)
      
      liveCalculationsState.value = {
        totalWeight: Math.round(performance.total_arrow_weight * 10) / 10,
        estimatedSpeed: Math.round(finalSpeed),
        kineticEnergy: Math.round(performance.kinetic_energy_40yd * 10) / 10,
        foc: Math.round(performance.foc_percentage * 10) / 10,
        trajectory: simpleTrajectory,
        maxHeight: simpleTrajectory.maxHeight,
        drop40yd: simpleTrajectory.drop40yd,
        speedSource: finalSpeedSource,
        confidence: null
      }
      return
    }
    
    // Final fallback
    liveCalculationsState.value = {
      totalWeight: await calculateTotalWeight(),
      estimatedSpeed: 280,
      kineticEnergy: 0,
      foc: 12,
      trajectory: { points: [], maxHeight: 0, drop40yd: 0 },
      maxHeight: 0,
      drop40yd: 0,
      speedSource: 'estimated',
      confidence: null
    }
  } catch (error) {
    console.error('Error updating live calculations:', error)
  }
}

// Live Performance Calculations (use reactive state)
const liveCalculations = computed(() => liveCalculationsState.value)

// Watch for changes and recalculate
watch([() => props.setupArrow, () => props.bowConfig], async () => {
  await calculatePerformanceAPI()
  await updateLiveCalculations()
  // Force TrajectoryChart to re-render when props change
  trajectoryChartKey.value++
}, { immediate: true, deep: true })

// Ballistics Table Data (use API data from composable when available)
const ballisticsTable = computed(() => {
  // Use API trajectory data from the composable if available
  if (hasTrajectoryData.value && trajectoryPoints.value?.length > 0) {
    const trajectoryPointsData = trajectoryPoints.value
    const baseDistances = [10, 20, 30, 40, 50, 60, 80, 100]
    
    return baseDistances.map(distanceYards => {
      const point = trajectoryPointsData.find(p => Math.abs(p.distance_yards - distanceYards) <= 2)
      
      if (point) {
        return {
          distance: distanceYards,
          speed: Math.round(point.velocity_fps),
          drop: Math.round((point.height_inches - 7.0) * 10) / 10,
          energy: Math.round(point.kinetic_energy_ft_lbs * 10) / 10,
          time: Math.round(point.time_seconds * 1000) / 1000
        }
      }
      
      // Fallback to interpolation if exact point not found
      const speed = liveCalculations.value.estimatedSpeed
      const weight = liveCalculations.value.totalWeight
      
      return {
        distance: distanceYards,
        speed: Math.round(calculateSpeedAtDistance(speed, distanceYards)),
        drop: calculateDropAtDistance(speed, distanceYards),
        energy: Math.round(calculateEnergyAtDistance(speed, weight, distanceYards) * 10) / 10,
        time: calculateTimeToDistance(speed, distanceYards)
      }
    })
  }
  
  // Fallback to simplified calculations
  const speed = liveCalculations.value.estimatedSpeed
  const weight = liveCalculations.value.totalWeight
  
  const baseDistances = [10, 20, 30, 40, 50, 60, 80, 100]
  
  return baseDistances.map(distanceYards => ({
    distance: distanceYards,
    speed: Math.round(calculateSpeedAtDistance(speed, distanceYards)),
    drop: calculateDropAtDistance(speed, distanceYards),
    energy: Math.round(calculateEnergyAtDistance(speed, weight, distanceYards) * 10) / 10,
    time: calculateTimeToDistance(speed, distanceYards)
  }))
})


// Performance Recommendations
const performanceRecommendations = computed(() => {
  const recommendations = []
  const foc = liveCalculations.value.foc
  const weight = liveCalculations.value.totalWeight
  const speed = liveCalculations.value.estimatedSpeed
  
  // FOC recommendations
  if (foc < 6) {
    recommendations.push({
      icon: 'fas fa-exclamation-triangle',
      text: 'FOC is low. Consider heavier point weight for better stability.'
    })
  } else if (foc > 20) {
    recommendations.push({
      icon: 'fas fa-info-circle',
      text: 'High FOC setup - excellent for hunting but may affect long-range accuracy.'
    })
  }
  
  // Weight recommendations
  if (weight < 350) {
    recommendations.push({
      icon: 'fas fa-feather-alt',
      text: 'Lightweight arrow - good for speed but consider kinetic energy for hunting.'
    })
  } else if (weight > 550) {
    recommendations.push({
      icon: 'fas fa-weight-hanging',
      text: 'Heavy arrow setup - excellent kinetic energy but check bow compatibility.'
    })
  }
  
  // Speed recommendations
  if (speed > 300) {
    recommendations.push({
      icon: 'fas fa-tachometer-alt',
      text: 'High speed setup - great for 3D but ensure proper spine tuning.'
    })
  }
  
  return recommendations.slice(0, 3) // Limit to 3 recommendations
})

// Additional calculation helper methods

const calculateKineticEnergy = (speed, weight) => {
  // KE = (mass × velocity²) / 2gc
  // Using archery formula: KE = (speed² × weight) / 450240
  return (speed * speed * weight) / 450240
}

const calculateAdvancedFOC = () => {
  const arrowLength = props.setupArrow.arrow_length || 32
  const totalWeight = calculateTotalWeight()
  const pointWeight = props.setupArrow.point_weight || 0
  const insertWeight = props.setupArrow.insert_weight || 0
  const nockWeight = props.setupArrow.nock_weight || 10
  const bushingWeight = props.setupArrow.bushing_weight || 0
  const fletchingWeight = props.setupArrow.fletching_weight || 15
  
  if (totalWeight === 0 || arrowLength === 0) return 0
  
  // Industry-accurate FOC calculation using weight distribution method
  // This method calculates the actual balance point based on component locations
  
  // Component positions along the arrow (in inches from nock end)
  const nockPosition = 0 // Nock at rear end
  const fletchingPosition = 3 // Fletching typically 3" from nock
  const bushingPosition = arrowLength // Bushing at front end (inside shaft)
  const insertPosition = arrowLength // Insert at front end
  const pointPosition = arrowLength + 0.5 // Point extends beyond shaft end
  
  // Shaft weight distribution (assuming uniform carbon/aluminum shaft)
  const shaftWeight = totalWeight - pointWeight - insertWeight - nockWeight - bushingWeight - fletchingWeight
  const shaftCenterPosition = arrowLength / 2 // Shaft center of mass
  
  // Calculate weighted balance point using moment arm principle
  // Sum of (weight × position) divided by total weight
  const weightedMoments = 
    (nockWeight * nockPosition) +
    (fletchingWeight * fletchingPosition) +
    (shaftWeight * shaftCenterPosition) +
    (bushingWeight * bushingPosition) +
    (insertWeight * insertPosition) +
    (pointWeight * pointPosition)
  
  const balancePoint = weightedMoments / totalWeight
  
  // Physical center of arrow (geometric center of arrow shaft only)
  const physicalCenter = arrowLength / 2
  
  // Industry standard FOC formula
  // FOC% = ((Balance Point - Physical Center) / Arrow Length) × 100
  const focPercentage = ((balancePoint - physicalCenter) / arrowLength) * 100
  
  // FOC should typically be between 6% and 20% for hunting arrows
  // Target arrows often run 8-12% FOC
  return Math.round(focPercentage * 10) / 10
}

const calculateLocalTrajectory = (speed, weight) => {
  const points = []
  const distances = Array.from({length: 21}, (_, i) => i * 5) // 0 to 100 yards in 5-yard increments
  
  let maxHeight = 0
  let drop40yd = 0
  
  distances.forEach(distance => {
    if (distance === 0) {
      points.push({ distance: 0, drop: 0, height: 0 })
      return
    }
    
    // Simplified ballistic trajectory calculation
    const timeToTarget = distance * 3 / speed // Approximate time in seconds
    const gravityDrop = 16.1 * timeToTarget * timeToTarget // Drop due to gravity
    const sightHeight = 7 // Inches above bore
    const zeroDistance = 20 // Yards
    
    // Calculate arc (simplified)
    let drop = gravityDrop - sightHeight
    
    // Adjust for zero at 20 yards
    if (distance <= zeroDistance) {
      drop = drop + (sightHeight * (zeroDistance - distance) / zeroDistance)
    }
    
    const height = Math.abs(drop)
    if (height > maxHeight) maxHeight = height
    if (distance === 40) drop40yd = Math.round(drop * 10) / 10
    
    points.push({
      distance,
      drop: Math.round(drop * 10) / 10,
      height: Math.round(height * 10) / 10
    })
  })
  
  return {
    points,
    maxHeight: Math.round(maxHeight * 10) / 10,
    drop40yd
  }
}

// Ballistics Table Helper Methods
const calculateSpeedAtDistance = (initialSpeed, distance) => {
  // Simplified speed loss calculation
  const speedLoss = distance * 1.5 // Approximate 1.5 fps loss per yard
  return Math.max(initialSpeed - speedLoss, 100)
}

const calculateDropAtDistance = (speed, distance) => {
  if (distance === 0) return 0
  
  const timeToTarget = distance * 3 / speed
  const gravityDrop = 16.1 * timeToTarget * timeToTarget
  const sightHeight = 7
  
  let drop = gravityDrop - sightHeight
  if (distance <= 20) {
    drop = drop + (sightHeight * (20 - distance) / 20)
  }
  
  return Math.round(drop * 10) / 10
}

const calculateEnergyAtDistance = (initialSpeed, weight, distance) => {
  const speedAtDistance = calculateSpeedAtDistance(initialSpeed, distance)
  return calculateKineticEnergy(speedAtDistance, weight)
}

const calculateTimeToDistance = (speed, distance) => {
  const timeSeconds = (distance * 3) / speed // Convert yards to feet, then divide by fps
  return Math.round(timeSeconds * 1000) / 1000 // Round to 3 decimal places
}

// Change Detection Methods
const getWeightChange = () => {
  if (!props.originalPerformance?.total_arrow_weight) return ''
  
  const currentWeight = liveCalculations.value.totalWeight
  const originalWeight = props.originalPerformance.total_arrow_weight
  const change = currentWeight - originalWeight
  
  if (Math.abs(change) < 0.1) return ''
  return change > 0 ? `+${change.toFixed(1)}` : change.toFixed(1)
}

const getSpeedChange = () => {
  if (!props.originalPerformance?.estimated_speed) return ''
  
  const currentSpeed = liveCalculations.value.estimatedSpeed
  const originalSpeed = props.originalPerformance.estimated_speed
  const change = currentSpeed - originalSpeed
  
  if (Math.abs(change) < 1) return ''
  return change > 0 ? `+${Math.round(change)}` : Math.round(change).toString()
}

const getEnergyChange = () => {
  if (!props.originalPerformance?.kinetic_energy) return ''
  
  const currentEnergy = liveCalculations.value.kineticEnergy
  const originalEnergy = props.originalPerformance.kinetic_energy
  const change = currentEnergy - originalEnergy
  
  if (Math.abs(change) < 0.1) return ''
  return change > 0 ? `+${change.toFixed(1)}` : change.toFixed(1)
}

const getFOCChange = () => {
  if (!props.originalPerformance?.foc) return ''
  
  const currentFOC = liveCalculations.value.foc
  const originalFOC = props.originalPerformance.foc
  const change = currentFOC - originalFOC
  
  if (Math.abs(change) < 0.1) return ''
  return change > 0 ? `+${change.toFixed(1)}%` : `${change.toFixed(1)}%`
}

const getChangeClass = (type) => {
  let change = 0
  
  switch (type) {
    case 'weight':
      if (!props.originalPerformance?.total_arrow_weight) return 'text-gray-500'
      change = liveCalculations.value.totalWeight - props.originalPerformance.total_arrow_weight
      break
    case 'speed':
      if (!props.originalPerformance?.estimated_speed) return 'text-gray-500'
      change = liveCalculations.value.estimatedSpeed - props.originalPerformance.estimated_speed
      break
    case 'energy':
      if (!props.originalPerformance?.kinetic_energy) return 'text-gray-500'
      change = liveCalculations.value.kineticEnergy - props.originalPerformance.kinetic_energy
      break
    case 'foc':
      if (!props.originalPerformance?.foc) return 'text-gray-500'
      change = liveCalculations.value.foc - props.originalPerformance.foc
      break
  }
  
  if (Math.abs(change) < 0.1) return 'text-gray-500'
  if (change > 0) return 'text-green-600 dark:text-green-400'
  return 'text-red-600 dark:text-red-400'
}

// Speed source indicator methods (same as TrajectoryChart)
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
</script>