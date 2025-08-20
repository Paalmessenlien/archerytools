<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Header with Session Info -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          Walkback Tuning Test #{{ testNumber }}
        </h2>
        <p class="text-gray-600 dark:text-gray-300">
          {{ sessionData.arrow.manufacturer }} {{ sessionData.arrow.model_name }} 
          ({{ sessionData.arrow_length }}", {{ sessionData.point_weight }}gn)
        </p>
      </div>
      <div class="text-right">
        <div class="text-sm text-gray-500 dark:text-gray-400">Session ID: {{ sessionData.session_id }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ sessionData.bow_setup.name }}
        </div>
      </div>
    </div>

    <!-- Progress Indicator -->
    <div class="mb-6">
      <div class="flex items-center space-x-4">
        <div class="flex items-center">
          <div class="w-4 h-4 rounded-full bg-blue-600"></div>
          <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Current Test</span>
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ previousTests.length }} previous tests available
        </div>
      </div>
    </div>

    <!-- Test Instructions -->
    <div class="mb-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <h3 class="text-lg font-medium text-blue-900 dark:text-blue-100 mb-2">
        Walkback Tuning Instructions
      </h3>
      <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
        <li>• Set up a vertical reference line on your target</li>
        <li>• Shoot from multiple distances (10, 15, 20, 25, 30 yards)</li>
        <li>• Aim at the same point on the vertical line for each distance</li>
        <li>• Record the horizontal offset from the line at each distance</li>
        <li>• Use the chart below to plot your results</li>
      </ul>
    </div>

    <!-- Distance Input Section -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          Distance Measurements
        </h3>
        <button 
          @click="addDistance"
          :disabled="distanceData.length >= 8"
          class="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Add Distance
        </button>
      </div>
      
      <div class="space-y-3">
        <div 
          v-for="(point, index) in distanceData" 
          :key="index"
          class="grid grid-cols-3 md:grid-cols-4 gap-4 items-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
        >
          <div>
            <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Distance (yards)</label>
            <input 
              v-model.number="point.distance"
              type="number"
              step="1"
              min="5"
              max="100"
              class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
            />
          </div>
          <div>
            <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Offset (cm)</label>
            <input 
              v-model.number="point.offset"
              type="number"
              step="0.1"
              class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
            />
          </div>
          <div>
            <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Direction</label>
            <select 
              v-model="point.direction"
              class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
            >
              <option value="left">Left</option>
              <option value="right">Right</option>
              <option value="center">Center</option>
            </select>
          </div>
          <div class="flex justify-end">
            <button 
              @click="removeDistance(index)"
              :disabled="distanceData.length <= 2"
              class="p-2 text-red-600 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Walkback Chart Visualization -->
    <div class="mb-6" v-if="chartData.length >= 3">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        Walkback Chart
      </h3>
      <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6">
        <!-- SVG Chart -->
        <div class="relative">
          <svg :width="chartWidth" :height="chartHeight" class="border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-100">
            <!-- Grid Lines -->
            <defs>
              <pattern id="grid" width="40" height="30" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 30" fill="none" stroke="#e5e7eb" stroke-width="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            <!-- Axes -->
            <line :x1="chartMargin" :y1="chartHeight - chartMargin" :x2="chartWidth - chartMargin" :y2="chartHeight - chartMargin" 
                  stroke="#374151" stroke-width="2"/>
            <line :x1="chartMargin" :y1="chartMargin" :x2="chartMargin" :y2="chartHeight - chartMargin" 
                  stroke="#374151" stroke-width="2"/>
            
            <!-- X-axis labels (Distance) -->
            <text v-for="(tick, index) in xTicks" :key="`x-${index}`"
                  :x="tick.x" :y="chartHeight - chartMargin + 20" 
                  text-anchor="middle" class="text-sm fill-gray-600">
              {{ tick.value }}yd
            </text>
            
            <!-- Y-axis labels (Offset) -->
            <text v-for="(tick, index) in yTicks" :key="`y-${index}`"
                  :x="chartMargin - 10" :y="tick.y + 5" 
                  text-anchor="end" class="text-sm fill-gray-600">
              {{ tick.value }}cm
            </text>
            
            <!-- Data Points -->
            <circle v-for="(point, index) in chartPoints" :key="`point-${index}`"
                    :cx="point.x" :cy="point.y" r="4" 
                    fill="#3B82F6" stroke="#1E40AF" stroke-width="2"/>
            
            <!-- Trend Line -->
            <line v-if="trendLine" 
                  :x1="trendLine.x1" :y1="trendLine.y1" 
                  :x2="trendLine.x2" :y2="trendLine.y2" 
                  stroke="#EF4444" stroke-width="2" stroke-dasharray="5,5"/>
            
            <!-- Zero Line -->
            <line :x1="chartMargin" :y1="zeroLineY" :x2="chartWidth - chartMargin" :y2="zeroLineY" 
                  stroke="#10B981" stroke-width="1" stroke-dasharray="3,3"/>
            
            <!-- Tolerance Bands -->
            <rect v-if="toleranceBand" 
                  :x="chartMargin" :y="toleranceBand.top" 
                  :width="chartWidth - 2 * chartMargin" :height="toleranceBand.height" 
                  fill="#10B981" fill-opacity="0.1" stroke="#10B981" stroke-width="1" stroke-dasharray="2,2"/>
            
            <!-- Axis Labels -->
            <text :x="chartWidth / 2" :y="chartHeight - 5" 
                  text-anchor="middle" class="text-sm font-medium fill-gray-700">
              Distance (yards)
            </text>
            <text :x="15" :y="chartHeight / 2" 
                  text-anchor="middle" transform="rotate(-90, 15, ${chartHeight / 2})" 
                  class="text-sm font-medium fill-gray-700">
              Horizontal Offset (cm)
            </text>
          </svg>
        </div>

        <!-- Chart Legend -->
        <div class="mt-4 flex flex-wrap items-center gap-4 text-sm">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            <span class="text-gray-700 dark:text-gray-300">Data Points</span>
          </div>
          <div class="flex items-center">
            <div class="w-6 h-0.5 bg-red-500 mr-2" style="border-style: dashed;"></div>
            <span class="text-gray-700 dark:text-gray-300">Trend Line</span>
          </div>
          <div class="flex items-center">
            <div class="w-6 h-0.5 bg-green-500 mr-2" style="border-style: dashed;"></div>
            <span class="text-gray-700 dark:text-gray-300">Zero Line</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-3 bg-green-500 opacity-20 border border-green-500 mr-2" style="border-style: dashed;"></div>
            <span class="text-gray-700 dark:text-gray-300">Tolerance Zone</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Analysis Results -->
    <div class="mb-6" v-if="analysisResults">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        Analysis Results
      </h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {{ (analysisResults.slope * 1000).toFixed(1) }}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">cm/m slope</div>
        </div>
        <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {{ analysisResults.intercept.toFixed(1) }}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">cm intercept</div>
        </div>
        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold" :class="rSquaredColor">
            {{ (analysisResults.rSquared * 100).toFixed(1) }}%
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">R² (linearity)</div>
        </div>
        <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold" :class="toleranceColor">
            {{ analysisResults.withinTolerance ? 'PASS' : 'FAIL' }}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">within tolerance</div>
        </div>
      </div>
      
      <!-- Detailed Analysis -->
      <div class="mt-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
        <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Interpretation</h4>
        <div class="text-sm text-gray-600 dark:text-gray-300 space-y-1">
          <p><strong>Drift Direction:</strong> {{ driftDirection }}</p>
          <p><strong>Linearity Quality:</strong> {{ linearityQuality }}</p>
          <p><strong>Recommendation:</strong> {{ nextStep }}</p>
        </div>
      </div>
    </div>

    <!-- Environmental Conditions -->
    <div class="mb-6" v-if="sessionData.settings?.record_environment">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Environmental Conditions (Optional)
      </label>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Temperature (°F)</label>
          <input 
            v-model.number="environmentalConditions.temperature"
            type="number"
            class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Humidity (%)</label>
          <input 
            v-model.number="environmentalConditions.humidity"
            type="number"
            class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Wind (mph)</label>
          <input 
            v-model.number="environmentalConditions.wind_speed"
            type="number"
            class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Light</label>
          <select 
            v-model="environmentalConditions.lighting"
            class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
          >
            <option value="">Select...</option>
            <option value="bright">Bright</option>
            <option value="overcast">Overcast</option>
            <option value="indoor">Indoor</option>
            <option value="low_light">Low Light</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Notes -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Additional Notes
      </label>
      <textarea 
        v-model="notes"
        placeholder="Record any additional observations, equipment changes made, or other relevant information..."
        class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        rows="3"
      ></textarea>
    </div>

    <!-- Previous Test Results -->
    <div class="mb-6" v-if="previousTests.length > 0">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          Previous Tests ({{ previousTests.length }})
        </h3>
        <button 
          @click="showPreviousTests = !showPreviousTests"
          class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm font-medium"
        >
          {{ showPreviousTests ? 'Hide' : 'Show' }} History
        </button>
      </div>
      
      <div v-if="showPreviousTests" class="space-y-3 max-h-64 overflow-y-auto">
        <div 
          v-for="test in previousTests" 
          :key="test.id"
          class="border border-gray-200 dark:border-gray-600 rounded-lg p-3"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="font-medium text-gray-900 dark:text-gray-100">
              Test #{{ test.test_number }}
            </div>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              {{ formatDate(test.created_at) }}
            </div>
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300 space-y-1">
            <div>Slope: {{ (test.test_data.slope_cm_per_m || 0).toFixed(3) }} cm/m</div>
            <div>Intercept: {{ (test.test_data.intercept_cm || 0).toFixed(1) }} cm</div>
            <div>R²: {{ ((test.test_data.r_squared || 0) * 100).toFixed(1) }}%</div>
            <div>Confidence: {{ Math.round(test.confidence_score || 0) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-between">
      <button 
        @click="$emit('cancel')"
        class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
      >
        Cancel
      </button>
      <div class="space-x-3">
        <button 
          @click="calculateAnalysis"
          :disabled="chartData.length < 3"
          class="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
        >
          Calculate Analysis
        </button>
        <button 
          @click="recordTest"
          :disabled="!canRecordTest || recording"
          class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center"
        >
          <div v-if="recording" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          {{ recording ? 'Recording...' : 'Record Test Result' }}
        </button>
      </div>
    </div>

    <!-- Analysis Results Modal -->
    <div v-if="showResults" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Test Results & Recommendations
            </h3>
            <button 
              @click="showResults = false"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <div v-if="testResults" class="space-y-4">
            <!-- Confidence Score -->
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-blue-900 dark:text-blue-100">Confidence Score</span>
                <span class="text-lg font-bold text-blue-600 dark:text-blue-400">
                  {{ Math.round(testResults.confidence_score || 0) }}%
                </span>
              </div>
            </div>
            
            <!-- Recommendations -->
            <div class="space-y-3">
              <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">Recommendations</h4>
              <div 
                v-for="(rec, index) in testResults.recommendations" 
                :key="index"
                class="border border-gray-200 dark:border-gray-600 rounded-lg p-3"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="font-medium text-gray-900 dark:text-gray-100">
                      {{ rec.component }}: {{ rec.action }}
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      {{ rec.reason }}
                    </div>
                    <div class="text-sm text-blue-600 dark:text-blue-400 mt-1">
                      Adjustment: {{ rec.magnitude }}
                    </div>
                  </div>
                  <div class="ml-4">
                    <span class="px-2 py-1 text-xs font-medium rounded-full"
                          :class="rec.priority === 1 
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' 
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'">
                      Priority {{ rec.priority }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="mt-6 flex justify-end">
            <button 
              @click="showResults = false"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'

// Props
const props = defineProps({
  sessionData: {
    type: Object,
    required: true
  }
})

// Define emits
const emit = defineEmits(['test-recorded', 'cancel'])

// Reactive data
const testNumber = ref(1)
const notes = ref('')
const recording = ref(false)
const showResults = ref(false)
const showPreviousTests = ref(false)
const testResults = ref(null)
const previousTests = ref([])
const analysisResults = ref(null)

// Chart dimensions
const chartWidth = 600
const chartHeight = 400
const chartMargin = 60

// Distance data points
const distanceData = ref([
  { distance: 10, offset: 0, direction: 'center' },
  { distance: 20, offset: 0, direction: 'center' },
  { distance: 30, offset: 0, direction: 'center' }
])

const environmentalConditions = ref({
  temperature: null,
  humidity: null,
  wind_speed: null,
  lighting: ''
})

// API composable
const api = useApi()

// Computed properties
const chartData = computed(() => {
  return distanceData.value
    .filter(d => d.distance && d.offset !== null && d.offset !== undefined)
    .map(d => ({
      distance: d.distance,
      offset: d.direction === 'left' ? -Math.abs(d.offset) : 
              d.direction === 'right' ? Math.abs(d.offset) : 
              d.offset || 0
    }))
    .sort((a, b) => a.distance - b.distance)
})

const xRange = computed(() => {
  if (chartData.value.length === 0) return [0, 40]
  const distances = chartData.value.map(d => d.distance)
  const min = Math.min(...distances)
  const max = Math.max(...distances)
  const padding = (max - min) * 0.1
  return [Math.max(0, min - padding), max + padding]
})

const yRange = computed(() => {
  if (chartData.value.length === 0) return [-10, 10]
  const offsets = chartData.value.map(d => d.offset)
  const min = Math.min(...offsets, 0)
  const max = Math.max(...offsets, 0)
  const padding = Math.max(2, (max - min) * 0.2)
  return [min - padding, max + padding]
})

const chartPoints = computed(() => {
  const [xMin, xMax] = xRange.value
  const [yMin, yMax] = yRange.value
  
  return chartData.value.map(d => ({
    x: chartMargin + ((d.distance - xMin) / (xMax - xMin)) * (chartWidth - 2 * chartMargin),
    y: chartHeight - chartMargin - ((d.offset - yMin) / (yMax - yMin)) * (chartHeight - 2 * chartMargin)
  }))
})

const xTicks = computed(() => {
  const [xMin, xMax] = xRange.value
  const tickCount = 6
  const ticks = []
  
  for (let i = 0; i <= tickCount; i++) {
    const value = xMin + (i / tickCount) * (xMax - xMin)
    const x = chartMargin + (i / tickCount) * (chartWidth - 2 * chartMargin)
    ticks.push({ value: Math.round(value), x })
  }
  
  return ticks
})

const yTicks = computed(() => {
  const [yMin, yMax] = yRange.value
  const tickCount = 6
  const ticks = []
  
  for (let i = 0; i <= tickCount; i++) {
    const value = yMin + (i / tickCount) * (yMax - yMin)
    const y = chartHeight - chartMargin - (i / tickCount) * (chartHeight - 2 * chartMargin)
    ticks.push({ value: Math.round(value * 10) / 10, y })
  }
  
  return ticks
})

const zeroLineY = computed(() => {
  const [yMin, yMax] = yRange.value
  return chartHeight - chartMargin - ((0 - yMin) / (yMax - yMin)) * (chartHeight - 2 * chartMargin)
})

const trendLine = computed(() => {
  if (!analysisResults.value || chartData.value.length < 2) return null
  
  const [xMin, xMax] = xRange.value
  const [yMin, yMax] = yRange.value
  const { slope, intercept } = analysisResults.value
  
  const x1 = chartMargin
  const x2 = chartWidth - chartMargin
  const distance1 = xMin
  const distance2 = xMax
  const y1Value = slope * distance1 + intercept
  const y2Value = slope * distance2 + intercept
  
  const y1 = chartHeight - chartMargin - ((y1Value - yMin) / (yMax - yMin)) * (chartHeight - 2 * chartMargin)
  const y2 = chartHeight - chartMargin - ((y2Value - yMin) / (yMax - yMin)) * (chartHeight - 2 * chartMargin)
  
  return { x1, y1, x2, y2 }
})

const toleranceBand = computed(() => {
  const [yMin, yMax] = yRange.value
  const tolerance = getBowTypeTolerance() // Get tolerance based on bow type
  
  const topValue = tolerance
  const bottomValue = -tolerance
  
  const top = chartHeight - chartMargin - ((topValue - yMin) / (yMax - yMin)) * (chartHeight - 2 * chartMargin)
  const bottom = chartHeight - chartMargin - ((bottomValue - yMin) / (yMax - yMin)) * (chartHeight - 2 * chartMargin)
  
  return {
    top: Math.max(chartMargin, top),
    height: Math.min(bottom - top, chartHeight - 2 * chartMargin)
  }
})

const rSquaredColor = computed(() => {
  if (!analysisResults.value) return 'text-gray-400'
  const r2 = analysisResults.value.rSquared
  if (r2 >= 0.9) return 'text-green-600 dark:text-green-400'
  if (r2 >= 0.8) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
})

const toleranceColor = computed(() => {
  if (!analysisResults.value) return 'text-gray-400'
  return analysisResults.value.withinTolerance 
    ? 'text-green-600 dark:text-green-400' 
    : 'text-red-600 dark:text-red-400'
})

const driftDirection = computed(() => {
  if (!analysisResults.value) return 'N/A'
  const slope = analysisResults.value.slope
  if (Math.abs(slope) < getBowTypeTolerance() / 100) return 'Minimal drift (excellent)'
  return slope > 0 ? 'Drifting right' : 'Drifting left'
})

const linearityQuality = computed(() => {
  if (!analysisResults.value) return 'N/A'
  const r2 = analysisResults.value.rSquared
  if (r2 >= 0.9) return 'Excellent'
  if (r2 >= 0.8) return 'Good'
  if (r2 >= 0.7) return 'Fair'
  return 'Poor (check form/clearance)'
})

const nextStep = computed(() => {
  if (!analysisResults.value) return 'Complete analysis first'
  const { slope, rSquared, withinTolerance } = analysisResults.value
  
  if (rSquared < 0.8) return 'Investigate form consistency and clearance issues'
  if (!withinTolerance) return 'Make rest/plunger adjustment and retest'
  return 'Walkback tuning complete - excellent results'
})

const canRecordTest = computed(() => {
  return chartData.value.length >= 3 && analysisResults.value
})

// Methods
const addDistance = () => {
  if (distanceData.value.length < 8) {
    const lastDistance = Math.max(...distanceData.value.map(d => d.distance))
    distanceData.value.push({
      distance: lastDistance + 5,
      offset: 0,
      direction: 'center'
    })
  }
}

const removeDistance = (index) => {
  if (distanceData.value.length > 2) {
    distanceData.value.splice(index, 1)
  }
}

const getBowTypeTolerance = () => {
  const bowType = props.sessionData.bow_setup.bow_type || 'compound'
  const tolerances = {
    compound: 0.10,
    recurve: 0.15,
    barebow: 0.20,
    traditional: 0.20
  }
  return tolerances[bowType] || 0.15
}

const calculateLinearRegression = (data) => {
  const n = data.length
  const sumX = data.reduce((sum, d) => sum + d.distance, 0)
  const sumY = data.reduce((sum, d) => sum + d.offset, 0)
  const sumXY = data.reduce((sum, d) => sum + d.distance * d.offset, 0)
  const sumX2 = data.reduce((sum, d) => sum + d.distance * d.distance, 0)
  const sumY2 = data.reduce((sum, d) => sum + d.offset * d.offset, 0)
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
  const intercept = (sumY - slope * sumX) / n
  
  // Calculate R-squared
  const yMean = sumY / n
  const ssRes = data.reduce((sum, d) => {
    const predicted = slope * d.distance + intercept
    return sum + Math.pow(d.offset - predicted, 2)
  }, 0)
  const ssTot = data.reduce((sum, d) => sum + Math.pow(d.offset - yMean, 2), 0)
  const rSquared = 1 - (ssRes / ssTot)
  
  return { slope, intercept, rSquared }
}

const calculateAnalysis = () => {
  if (chartData.value.length < 3) return
  
  const { slope, intercept, rSquared } = calculateLinearRegression(chartData.value)
  const tolerance = getBowTypeTolerance()
  const withinTolerance = Math.abs(slope) <= tolerance
  
  analysisResults.value = {
    slope,
    intercept,
    rSquared,
    withinTolerance,
    tolerance
  }
}

const loadPreviousTests = async () => {
  try {
    const response = await api.get(`/arrows/${props.sessionData.arrow_id}/tuning-history`, {
      params: {
        bow_setup_id: props.sessionData.bow_setup.id,
        test_type: 'walkback_tuning'
      }
    })
    previousTests.value = response.test_results || []
    if (previousTests.value.length > 0) {
      testNumber.value = Math.max(...previousTests.value.map(t => t.test_number)) + 1
    }
  } catch (error) {
    console.error('Failed to load previous tests:', error)
  }
}

const recordTest = async () => {
  if (!canRecordTest.value) return
  
  recording.value = true
  try {
    const testData = {
      distances_m: chartData.value.map(d => d.distance * 0.9144), // Convert yards to meters
      x_offsets_cm: chartData.value.map(d => d.offset),
      reference_distance: 20
    }
    
    const requestData = {
      test_data: testData,
      environmental_conditions: environmentalConditions.value,
      shooting_distance: 20, // Reference distance
      notes: notes.value
    }
    
    const response = await api.post(
      `/tuning-guides/${props.sessionData.session_id}/record-test`, 
      requestData
    )
    
    testResults.value = response
    showResults.value = true
    
    // Update test number
    testNumber.value = response.test_number + 1
    
    // Reload previous tests
    await loadPreviousTests()
    
    emit('test-recorded', response)
    
  } catch (error) {
    console.error('Failed to record test:', error)
  } finally {
    recording.value = false
  }
}

const formatDate = (dateString) => {
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return 'N/A'
  }
}

// Watch for data changes to trigger analysis
watch(chartData, (newData) => {
  if (newData.length >= 3) {
    calculateAnalysis()
  } else {
    analysisResults.value = null
  }
}, { deep: true })

// Lifecycle
onMounted(() => {
  loadPreviousTests()
})
</script>

<style scoped>
/* Custom styles for chart */
svg {
  font-family: system-ui, -apple-system, sans-serif;
}
</style>