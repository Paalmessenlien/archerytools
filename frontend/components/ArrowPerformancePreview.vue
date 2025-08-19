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
        <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">Est. Speed</div>
        <div class="text-xl font-bold text-blue-600 dark:text-blue-400">{{ liveCalculations.estimatedSpeed }} FPS</div>
        <div class="text-xs mt-1" :class="getChangeClass('speed')">
          {{ getSpeedChange() }}
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

    <!-- Flight Trajectory Visualization -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          <i class="fas fa-project-diagram mr-2 text-indigo-600"></i>
          Flight Trajectory
        </h4>
        <div class="flex items-center space-x-4 text-sm">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-blue-500 rounded mr-2"></div>
            <span class="text-gray-600 dark:text-gray-400">Current Setup</span>
          </div>
          <div v-if="originalPerformance" class="flex items-center">
            <div class="w-3 h-3 border-2 border-gray-400 rounded mr-2"></div>
            <span class="text-gray-600 dark:text-gray-400">Original</span>
          </div>
        </div>
      </div>
      
      <!-- Trajectory Chart Container -->
      <div class="relative bg-gray-50 dark:bg-gray-900 rounded-lg p-4" style="height: 200px;">
        <svg 
          ref="trajectoryChart" 
          class="w-full h-full" 
          viewBox="0 0 800 200"
          preserveAspectRatio="xMidYMid meet"
        >
          <!-- Grid lines -->
          <defs>
            <pattern id="grid" width="80" height="40" patternUnits="userSpaceOnUse">
              <path d="M 80 0 L 0 0 0 40" fill="none" stroke="#e5e7eb" stroke-width="0.5" opacity="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          <!-- Trajectory Path -->
          <path 
            :d="trajectoryPath" 
            fill="none" 
            stroke="#3b82f6" 
            stroke-width="2"
            class="drop-shadow-sm"
          />
          
          <!-- Original Trajectory (if available) -->
          <path 
            v-if="originalTrajectoryPath" 
            :d="originalTrajectoryPath" 
            fill="none" 
            stroke="#9ca3af" 
            stroke-width="1.5"
            stroke-dasharray="5,5"
            opacity="0.7"
          />
          
          <!-- Distance Markers -->
          <g v-for="marker in trajectoryMarkers" :key="marker.distance">
            <circle 
              :cx="marker.x" 
              :cy="marker.y" 
              r="3" 
              fill="#3b82f6"
              class="drop-shadow-sm"
            />
            <text 
              :x="marker.x" 
              :y="marker.y - 8" 
              text-anchor="middle" 
              class="text-xs fill-gray-600 dark:fill-gray-400"
            >
              {{ marker.distance }}yd
            </text>
          </g>
          
          <!-- Axis Labels -->
          <text x="400" y="195" text-anchor="middle" class="text-xs fill-gray-600 dark:fill-gray-400">
            Distance (yards)
          </text>
          <text x="15" y="20" class="text-xs fill-gray-600 dark:fill-gray-400">
            Height
          </text>
        </svg>
        
        <!-- Trajectory Stats Overlay -->
        <div class="absolute top-2 right-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-2">
          <div class="text-xs space-y-1">
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">Max Height:</span>
              <span class="font-medium text-gray-900 dark:text-gray-100">{{ liveCalculations.maxHeight }}"</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">40yd Drop:</span>
              <span class="font-medium text-gray-900 dark:text-gray-100">{{ liveCalculations.drop40yd }}"</span>
            </div>
          </div>
        </div>
      </div>
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
import { computed, ref } from 'vue'

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

// Reactive references
const trajectoryChart = ref(null)

// Live Performance Calculations
const liveCalculations = computed(() => {
  const totalWeight = calculateTotalWeight()
  const estimatedSpeed = calculateEstimatedSpeed(totalWeight)
  const kineticEnergy = calculateKineticEnergy(estimatedSpeed, totalWeight)
  const foc = calculateAdvancedFOC()
  const trajectory = calculateTrajectory(estimatedSpeed, totalWeight)
  
  return {
    totalWeight: Math.round(totalWeight * 10) / 10,
    estimatedSpeed: Math.round(estimatedSpeed),
    kineticEnergy: Math.round(kineticEnergy * 10) / 10,
    foc: Math.round(foc * 10) / 10,
    trajectory,
    maxHeight: trajectory.maxHeight,
    drop40yd: trajectory.drop40yd
  }
})

// Ballistics Table Data
const ballisticsTable = computed(() => {
  const speed = liveCalculations.value.estimatedSpeed
  const weight = liveCalculations.value.totalWeight
  const distances = [10, 20, 30, 40, 50, 60, 80, 100]
  
  return distances.map(distance => ({
    distance,
    speed: Math.round(calculateSpeedAtDistance(speed, distance)),
    drop: calculateDropAtDistance(speed, distance),
    energy: Math.round(calculateEnergyAtDistance(speed, weight, distance) * 10) / 10,
    time: calculateTimeToDistance(speed, distance)
  }))
})

// Trajectory Path for SVG
const trajectoryPath = computed(() => {
  const points = liveCalculations.value.trajectory.points
  if (!points || points.length === 0) return ''
  
  const maxDistance = Math.max(...points.map(p => p.distance))
  const maxDrop = Math.max(...points.map(p => Math.abs(p.drop)))
  
  const pathData = points.map((point, index) => {
    const x = (point.distance / maxDistance) * 750 + 25 // Scale to SVG width
    const y = 100 - ((point.drop + maxDrop) / (maxDrop * 2)) * 150 + 25 // Invert Y and scale
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
  
  return pathData
})

// Original Trajectory Path (if available)
const originalTrajectoryPath = computed(() => {
  if (!props.originalPerformance?.trajectory) return null
  
  const points = props.originalPerformance.trajectory.points
  if (!points || points.length === 0) return null
  
  const maxDistance = Math.max(...points.map(p => p.distance))
  const maxDrop = Math.max(...points.map(p => Math.abs(p.drop)))
  
  const pathData = points.map((point, index) => {
    const x = (point.distance / maxDistance) * 750 + 25
    const y = 100 - ((point.drop + maxDrop) / (maxDrop * 2)) * 150 + 25
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
  
  return pathData
})

// Trajectory Markers
const trajectoryMarkers = computed(() => {
  const trajectory = liveCalculations.value.trajectory
  const markerDistances = [20, 40, 60, 80]
  const maxDistance = 100
  
  return markerDistances.map(distance => {
    const point = trajectory.points.find(p => p.distance === distance) || { distance, drop: 0 }
    const maxDrop = 20 // Estimated max drop range
    
    return {
      distance,
      x: (distance / maxDistance) * 750 + 25,
      y: 100 - ((point.drop + maxDrop) / (maxDrop * 2)) * 150 + 25
    }
  })
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

// Core Calculation Methods
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
  
  return shaftWeight + componentWeight
}

const calculateEstimatedSpeed = (arrowWeight) => {
  const bowSpeed = props.bowConfig.ibo_speed || 310 // Default IBO speed
  const drawWeight = props.bowConfig.draw_weight || 60
  const drawLength = props.bowConfig.draw_length || 28
  
  // Simplified speed estimation based on IBO formula
  // Adjust for draw weight and length
  const dwFactor = (drawWeight - 70) / 10 * 10 // +/- 10 fps per 10 lbs
  const dlFactor = (drawLength - 30) / 1 * 10   // +/- 10 fps per inch
  const weightFactor = (arrowWeight - 350) / 5 * -2 // -2 fps per 5 grains
  
  return Math.max(bowSpeed + dwFactor + dlFactor + weightFactor, 150) // Minimum 150 fps
}

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
  
  if (totalWeight === 0) return 0
  
  // More accurate FOC calculation
  const frontWeight = pointWeight + insertWeight
  const balancePoint = arrowLength / 2 // Simplified balance point
  const centerOfArrow = arrowLength / 2
  
  // FOC = ((Balance Point - Center of Arrow) / Arrow Length) × 100
  const foc = ((balancePoint - centerOfArrow) / arrowLength) * 100 + 
             (frontWeight / totalWeight) * 15 // Additional factor for front weight
  
  return Math.max(foc, 0)
}

const calculateTrajectory = (speed, weight) => {
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
</script>