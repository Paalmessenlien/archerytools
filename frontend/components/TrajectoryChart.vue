<template>
  <div class="trajectory-chart-container bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
    <!-- Compact Show Trajectory Button (when chart is not displayed) -->
    <div v-if="!showChart" class="p-4 text-center">
      <button 
        @click="generateTrajectoryChart"
        :disabled="isLoading"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md text-sm font-medium transition-colors flex items-center mx-auto"
      >
        <i v-if="isLoading" class="fas fa-spinner fa-spin mr-2 text-xs"></i>
        <i v-else class="fas fa-chart-line mr-2 text-xs"></i>
        {{ isLoading ? 'Generating...' : 'Show Flight Trajectory' }}
      </button>
    </div>

    <!-- Chart Display (when chart is shown) -->
    <div v-else class="p-4">
      <!-- Header - Mobile Responsive -->
      <div class="mb-4">
        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
          <div class="flex flex-col">
            <h4 class="text-base font-medium text-gray-900 dark:text-white flex items-center">
              <span class="mr-2 text-sm">🎯</span>
              Flight Trajectory
            </h4>
            <!-- Speed Source Indicator -->
            <div v-if="props.arrowData?.speed_source" class="flex items-center mt-1">
              <span class="text-xs px-2 py-1 rounded-full" :class="getSpeedSourceClass()">
                <i :class="getSpeedSourceIcon()" class="mr-1"></i>
                {{ getSpeedSourceText() }}
              </span>
            </div>
          </div>
          
          <!-- Controls - Responsive Layout -->
          <div class="flex flex-col sm:flex-row gap-2 sm:gap-1">
            <!-- Units Toggle -->
            <div class="flex bg-gray-100 dark:bg-gray-700 rounded-md text-xs w-full sm:w-auto">
              <button 
                @click="setUnits('imperial')"
                :class="[
                  'flex-1 sm:flex-none px-3 py-2 rounded-l-md transition-colors',
                  units === 'imperial' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                ]"
              >
                Yards
              </button>
              <button 
                @click="setUnits('metric')"
                :class="[
                  'flex-1 sm:flex-none px-3 py-2 rounded-r-md transition-colors',
                  units === 'metric' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                ]"
              >
                Meters
              </button>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex gap-2">
              <button 
                @click="toggleEnvironmentalControls"
                class="flex-1 sm:flex-none px-3 py-2 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-md hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
              >
                <i class="fas fa-cog mr-1"></i>
                <span class="hidden sm:inline">{{ showEnvironmentalControls ? 'Hide' : 'Settings' }}</span>
                <span class="sm:hidden">{{ showEnvironmentalControls ? 'Hide' : 'Settings' }}</span>
              </button>
              <button 
                @click="hideChart"
                class="px-3 py-2 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title="Close trajectory chart"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Tooltip moved to separate line on mobile -->
        <div class="mt-2 sm:mt-0 flex justify-center sm:justify-end">
          <PerformanceTooltip 
            :title="'Trajectory Analysis'"
            :content="'Visual representation of arrow flight path showing drop, range, and environmental effects. Toggle between yards/meters and adjust environmental settings.'"
          />
        </div>
      </div>

    <!-- Environmental Controls -->
    <div v-if="showEnvironmentalControls" class="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Environmental Conditions</h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Wind Speed (mph)</label>
          <input 
            v-model.number="environmentalConditions.windSpeed"
            @change="updateTrajectory"
            type="range" 
            min="0" 
            max="20" 
            step="1"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          >
          <span class="text-xs text-gray-500">{{ environmentalConditions.windSpeed }} mph</span>
        </div>
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Temperature (°F)</label>
          <input 
            v-model.number="environmentalConditions.temperature"
            @change="updateTrajectory"
            type="range" 
            min="20" 
            max="100" 
            step="5"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          >
          <span class="text-xs text-gray-500">{{ environmentalConditions.temperature }}°F</span>
        </div>
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Altitude (ft)</label>
          <input 
            v-model.number="environmentalConditions.altitude"
            @change="updateTrajectory"
            type="range" 
            min="0" 
            max="8000" 
            step="500"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          >
          <span class="text-xs text-gray-500">{{ environmentalConditions.altitude }} ft</span>
        </div>
      </div>
    </div>

    <!-- Chart Container -->
    <div class="chart-wrapper overflow-x-auto" style="position: relative; height: 280px; min-height: 240px;">
      <canvas ref="chartCanvas" class="max-w-full"></canvas>
    </div>

    <!-- Trajectory Summary -->
    <div v-if="trajectorySummary" class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
      <div class="bg-blue-50 dark:bg-blue-900/30 p-3 rounded-lg text-center sm:text-left">
        <div class="text-blue-600 dark:text-blue-400 font-medium">Max Range</div>
        <div class="text-gray-900 dark:text-white font-semibold text-lg">{{ getDisplayMaxRange() }} {{ getDistanceUnit() }}</div>
      </div>
      <div class="bg-green-50 dark:bg-green-900/30 p-3 rounded-lg text-center sm:text-left">
        <div class="text-green-600 dark:text-green-400 font-medium">Peak Height</div>
        <div class="text-gray-900 dark:text-white font-semibold text-lg">{{ getDisplayPeakHeight() }}{{ getHeightUnit() }}</div>
      </div>
      <div class="bg-orange-50 dark:bg-orange-900/30 p-3 rounded-lg text-center sm:text-left">
        <div class="text-orange-600 dark:text-orange-400 font-medium">Drop at {{ getDisplayDropReference() }}{{ getDistanceUnit() }}</div>
        <div class="text-gray-900 dark:text-white font-semibold text-lg">{{ getDisplayDropAt40() }}{{ getHeightUnit() }}</div>
      </div>
    </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 flex items-center justify-center rounded-lg">
        <div class="text-center">
          <div class="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <div class="text-sm text-gray-600 dark:text-gray-400">Calculating trajectory...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, markRaw } from 'vue'
import PerformanceTooltip from '~/components/PerformanceTooltip.vue'
import { useApi } from '~/composables/useApi'
// Chart.js loaded from CDN to avoid build issues
const initializeChart = async () => {
  if (typeof window === 'undefined') return null
  
  // Check if Chart.js is already loaded from CDN
  if (window.Chart) {
    return window.Chart
  }
  
  // Load Chart.js from CDN if not available
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js'
    script.onload = () => {
      if (window.Chart) {
        resolve(window.Chart)
      } else {
        reject(new Error('Chart.js failed to load from CDN'))
      }
    }
    script.onerror = () => reject(new Error('Failed to load Chart.js script'))
    document.head.appendChild(script)
  })
}

const props = defineProps({
  arrowData: {
    type: Object,
    required: true
  },
  bowConfig: {
    type: Object,
    required: true
  }
})

// Composables
const api = useApi()

// Component state
const chartCanvas = ref(null)
const chartInstance = ref(null)
const isLoading = ref(false)
const showChart = ref(false)
const showEnvironmentalControls = ref(false)
const trajectorySummary = ref(null)
const units = ref('imperial') // 'imperial' or 'metric'

// Environmental conditions
const environmentalConditions = ref({
  windSpeed: 0,
  temperature: 70,
  altitude: 0
})

// No automatic watchers - chart generation is on-demand only

onMounted(async () => {
  // Chart initialization is now on-demand only
  // No automatic initialization to improve performance
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})

const toggleEnvironmentalControls = () => {
  showEnvironmentalControls.value = !showEnvironmentalControls.value
}

const generateTrajectoryChart = async () => {
  // Ensure we're in the browser environment
  if (typeof window === 'undefined') {
    console.warn('TrajectoryChart: Not in browser environment')
    return
  }

  isLoading.value = true

  try {
    // First, show the chart container so the canvas becomes available
    showChart.value = true
    await nextTick() // Wait for DOM to update
    
    await initializeChartComponent()
    await updateTrajectory()
  } catch (error) {
    console.error('Error generating trajectory chart:', error)
    // Hide chart if initialization failed
    showChart.value = false
  } finally {
    isLoading.value = false
  }
}

const hideChart = () => {
  showChart.value = false
  showEnvironmentalControls.value = false
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
}

const setUnits = (newUnits) => {
  units.value = newUnits
  if (chartInstance.value) {
    updateChartUnits()
  }
}

// Unit conversion functions
const yardsToMeters = (yards) => yards * 0.9144
const metersToYards = (meters) => meters / 0.9144
const inchesToCm = (inches) => inches * 2.54
const cmToInches = (cm) => cm / 2.54

const convertDistance = (distance) => {
  return units.value === 'metric' ? yardsToMeters(distance) : distance
}

const convertHeight = (height) => {
  return units.value === 'metric' ? inchesToCm(height) : height
}

const getDistanceUnit = () => {
  return units.value === 'metric' ? 'm' : 'yd'
}

const getHeightUnit = () => {
  return units.value === 'metric' ? 'cm' : 'in'
}

const updateChartUnits = () => {
  if (!chartInstance.value) return
  
  // Update axis labels
  chartInstance.value.options.scales.x.title.text = `Distance (${getDistanceUnit()})`
  chartInstance.value.options.scales.y.title.text = `Height (${getHeightUnit()})`
  
  // Update data with converted units
  if (chartInstance.value.data.datasets[0].data.length > 0) {
    const originalData = chartInstance.value.data.datasets[0].originalData || chartInstance.value.data.datasets[0].data
    chartInstance.value.data.datasets[0].originalData = originalData
    
    // Convert data points
    chartInstance.value.data.datasets[0].data = originalData.map(point => convertHeight(point))
    chartInstance.value.data.labels = chartInstance.value.data.originalLabels?.map(label => 
      convertDistance(parseFloat(label)).toFixed(1)
    ) || chartInstance.value.data.labels
  }
  
  chartInstance.value.update()
}

const initializeChartComponent = async () => {
  if (!chartCanvas.value) {
    console.warn('Chart canvas not available for trajectory chart')
    return
  }

  try {
    // Initialize Chart.js dynamically
    const ChartClass = await initializeChart()
    if (!ChartClass) {
      console.warn('Chart.js not available')
      return
    }
    
    const ctx = chartCanvas.value.getContext('2d')
    
    chartInstance.value = markRaw(new ChartClass(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Arrow Flight Path',
          data: [],
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#3B82F6',
          pointBorderColor: '#FFFFFF',
          pointBorderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: `Distance (${getDistanceUnit()})`,
              color: '#6B7280',
              font: {
                size: 12,
                weight: 'bold'
              }
            },
            grid: {
              color: 'rgba(107, 114, 128, 0.1)'
            },
            ticks: {
              color: '#6B7280'
            }
          },
          y: {
            title: {
              display: true,
              text: `Height (${getHeightUnit()})`,
              color: '#6B7280',
              font: {
                size: 12,
                weight: 'bold'
              }
            },
            grid: {
              color: 'rgba(107, 114, 128, 0.1)'
            },
            ticks: {
              color: '#6B7280'
            },
            suggestedMin: -50,
            suggestedMax: 20
          }
        },
        plugins: {
          title: {
            display: false
          },
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(17, 24, 39, 0.95)',
            titleColor: '#F9FAFB',
            bodyColor: '#F9FAFB',
            borderColor: '#374151',
            borderWidth: 1,
            cornerRadius: 8,
            callbacks: {
              title: function(context) {
                return `Distance: ${context[0].label} ${getDistanceUnit()}`
              },
              label: function(context) {
                const height = context.parsed.y
                const unit = getHeightUnit()
                if (height >= 0) {
                  return `Height: ${height.toFixed(1)}${unit} above sight line`
                } else {
                  return `Drop: ${Math.abs(height).toFixed(1)}${unit} below sight line`
                }
              },
              afterLabel: function(context) {
                const distance = parseFloat(context.label)
                const distanceUnit = getDistanceUnit()
                
                // Convert reference distances based on current units
                const zeroDistance = units.value === 'metric' ? convertDistance(20).toFixed(0) : '20'
                const huntingDistance = units.value === 'metric' ? convertDistance(40).toFixed(0) : '40'
                const extendedDistance = units.value === 'metric' ? convertDistance(60).toFixed(0) : '60'
                
                if (Math.abs(distance - parseFloat(zeroDistance)) <= 1) return 'Zero Distance'
                if (Math.abs(distance - parseFloat(huntingDistance)) <= 2) return 'Common Hunting Distance'
                if (Math.abs(distance - parseFloat(extendedDistance)) <= 3) return 'Extended Range'
                return ''
              }
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
    }
  }))
  } catch (error) {
    console.error('Error creating Chart.js instance:', error)
    throw error // Re-throw to be caught by the mounted hook
  }
}

const updateTrajectory = async () => {
  if (!chartInstance.value || !props.arrowData || !props.bowConfig) return

  isLoading.value = true

  try {
    // Use authenticated API call instead of $fetch
    const response = await api.post('/calculate-trajectory', {
      arrow_data: props.arrowData,
      bow_config: props.bowConfig,
      environmental_conditions: {
        temperature_f: environmentalConditions.value.temperature,
        wind_speed_mph: environmentalConditions.value.windSpeed,
        altitude_feet: environmentalConditions.value.altitude,
        humidity_percent: 50.0,
        wind_direction_degrees: 90.0, // Right crosswind
        air_pressure_inHg: 29.92
      },
      shooting_conditions: {
        shot_angle_degrees: 0.0,
        sight_height_inches: 7.0,
        zero_distance_yards: 20.0,
        max_range_yards: 100.0
      }
    })

    if (response.success && response.trajectory_data) {
      updateChartData(response.trajectory_data)
      updateTrajectorySummary(response.trajectory_data)
    }
  } catch (error) {
    console.error('Failed to calculate trajectory:', error)
    // Show fallback trajectory based on basic ballistics
    generateFallbackTrajectory()
  } finally {
    isLoading.value = false
  }
}

const updateChartData = (trajectoryData) => {
  if (!chartInstance.value || !trajectoryData.trajectory_points) return

  const points = trajectoryData.trajectory_points
  const originalLabels = points.map(p => p.distance_yards.toString())
  const originalHeights = points.map(p => p.height_inches - 7.0) // Adjust for sight height

  // Store original data for unit conversion
  chartInstance.value.data.originalLabels = originalLabels
  chartInstance.value.data.datasets[0].originalData = originalHeights

  // Apply current unit conversion
  const convertedLabels = originalLabels.map(label => 
    convertDistance(parseFloat(label)).toFixed(1)
  )
  const convertedHeights = originalHeights.map(height => convertHeight(height))

  chartInstance.value.data.labels = convertedLabels
  chartInstance.value.data.datasets[0].data = convertedHeights
  chartInstance.value.update('smooth')
}

const updateTrajectorySummary = (trajectoryData) => {
  if (!trajectoryData.trajectory_points) return

  const points = trajectoryData.trajectory_points
  const maxRange = Math.max(...points.map(p => p.distance_yards))
  const maxHeight = Math.max(...points.map(p => p.height_inches - 7.0))
  
  // Find drop at 40 yards
  const point40yd = points.find(p => Math.abs(p.distance_yards - 40) <= 2)
  const dropAt40yd = point40yd ? Math.abs(point40yd.height_inches - 7.0) : 0

  trajectorySummary.value = {
    maxRange: Math.round(maxRange),
    peakHeight: maxHeight.toFixed(1),
    dropAt40yd: dropAt40yd.toFixed(1)
  }
}

const generateFallbackTrajectory = () => {
  // Generate basic trajectory based on arrow speed estimation
  const speed = estimateArrowSpeed()
  const points = []
  const labels = []
  
  for (let distance = 0; distance <= 80; distance += 5) {
    const time = distance * 3 / speed // Convert yards to feet, then to time
    const drop = -16.1 * time * time // Basic gravity drop (ft)
    const dropInches = drop * 12 // Convert to inches
    
    points.push(dropInches)
    labels.push(distance.toString())
  }

  chartInstance.value.data.labels = labels
  chartInstance.value.data.datasets[0].data = points
  chartInstance.value.update('smooth')

  // Basic summary
  trajectorySummary.value = {
    maxRange: 80,
    peakHeight: '2.0',
    dropAt40yd: Math.abs(points[8]).toFixed(1) // 40 yards = index 8
  }
}

const estimateArrowSpeed = () => {
  // Basic speed estimation
  const drawWeight = props.bowConfig?.drawWeight || 60
  const arrowWeight = props.arrowData?.total_weight || 400
  
  // Simplified speed formula
  const baseSpeed = drawWeight * 3.5 + 180
  const weightFactor = Math.sqrt(350 / arrowWeight)
  
  return Math.max(200, Math.min(350, baseSpeed * weightFactor))
}

// Speed source indicator methods
const getSpeedSourceClass = () => {
  const source = props.arrowData?.speed_source
  if (source === 'chronograph') {
    return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
  } else {
    return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
  }
}

const getSpeedSourceIcon = () => {
  const source = props.arrowData?.speed_source
  if (source === 'chronograph') {
    return 'fas fa-tachometer-alt'
  } else {
    return 'fas fa-calculator'
  }
}

const getSpeedSourceText = () => {
  const source = props.arrowData?.speed_source
  if (source === 'chronograph') {
    return 'Measured Speed'
  } else {
    return 'Estimated Speed'
  }
}

// Trajectory summary unit conversion methods
const getDisplayMaxRange = () => {
  if (!trajectorySummary.value) return 0
  const range = trajectorySummary.value.maxRange
  return units.value === 'metric' ? convertDistance(range).toFixed(1) : Math.round(range)
}

const getDisplayPeakHeight = () => {
  if (!trajectorySummary.value) return '0'
  const height = parseFloat(trajectorySummary.value.peakHeight)
  return units.value === 'metric' ? convertHeight(height).toFixed(1) : trajectorySummary.value.peakHeight
}

const getDisplayDropAt40 = () => {
  if (!trajectorySummary.value) return '0'
  const drop = parseFloat(trajectorySummary.value.dropAt40yd)
  return units.value === 'metric' ? convertHeight(drop).toFixed(1) : trajectorySummary.value.dropAt40yd
}

const getDisplayDropReference = () => {
  const referenceDistance = 40
  return units.value === 'metric' ? convertDistance(referenceDistance).toFixed(0) : referenceDistance
}
</script>

<style scoped>
.trajectory-chart-container {
  position: relative;
}

.chart-wrapper {
  background: transparent;
}

/* Custom range slider styling */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  border: 2px solid #FFFFFF;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

input[type="range"]::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  border: 2px solid #FFFFFF;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.dark input[type="range"]::-webkit-slider-thumb {
  border-color: #374151;
}

.dark input[type="range"]::-moz-range-thumb {
  border-color: #374151;
}
</style>