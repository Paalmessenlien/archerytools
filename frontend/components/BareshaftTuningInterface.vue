<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Header with Session Info -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          Bareshaft Tuning Test #{{ testNumber }}
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
        Bareshaft Tuning Instructions
      </h3>
      <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
        <li>• Shoot 3-6 fletched arrows at {{ testDistance }} yards</li>
        <li>• Shoot 3-6 bareshaft arrows (no fletching) at the same target</li>
        <li>• Compare group centers and measure the offset distance</li>
        <li>• Use the target interface below to mark the arrow groups</li>
      </ul>
    </div>

    <!-- Shooting Distance Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Test Distance
      </label>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div 
          v-for="distance in commonDistances" 
          :key="distance"
          @click="testDistance = distance"
          class="p-3 border rounded-lg cursor-pointer transition-all duration-200 text-center"
          :class="testDistance === distance 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400'"
        >
          <div class="font-medium text-gray-900 dark:text-gray-100">{{ distance }} yards</div>
        </div>
      </div>
    </div>

    <!-- Interactive Target Interface -->
    <div class="mb-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        Mark Arrow Groups on Target
      </h3>
      <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6">
        <!-- Target Face -->
        <div class="relative mx-auto" :style="{ width: targetSize + 'px', height: targetSize + 'px' }">
          <!-- Target Background -->
          <div 
            class="absolute inset-0 border-2 border-gray-400 dark:border-gray-500 rounded-full bg-white dark:bg-gray-100"
            @click="handleTargetClick"
            ref="targetFace"
          >
            <!-- Target Rings -->
            <div 
              v-for="ring in targetRings" 
              :key="ring.size"
              class="absolute border border-gray-300 dark:border-gray-400 rounded-full pointer-events-none"
              :style="{
                width: ring.size + 'px',
                height: ring.size + 'px',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)'
              }"
            ></div>
            
            <!-- Center Cross -->
            <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
              <div class="w-4 h-0.5 bg-red-500"></div>
              <div class="w-0.5 h-4 bg-red-500 absolute top-0 left-1/2 transform -translate-x-1/2"></div>
            </div>
            
            <!-- Fletched Group -->
            <div 
              v-if="fletchedGroup.x !== null && fletchedGroup.y !== null"
              class="absolute w-6 h-6 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none"
              :style="{ left: fletchedGroup.x + 'px', top: fletchedGroup.y + 'px' }"
            >
              <div class="w-full h-full bg-green-500 rounded-full border-2 border-white shadow-lg flex items-center justify-center">
                <span class="text-white text-xs font-bold">F</span>
              </div>
            </div>
            
            <!-- Bareshaft Group -->
            <div 
              v-if="bareshaftGroup.x !== null && bareshaftGroup.y !== null"
              class="absolute w-6 h-6 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none"
              :style="{ left: bareshaftGroup.x + 'px', top: bareshaftGroup.y + 'px' }"
            >
              <div class="w-full h-full bg-red-500 rounded-full border-2 border-white shadow-lg flex items-center justify-center">
                <span class="text-white text-xs font-bold">B</span>
              </div>
            </div>
            
            <!-- Offset Line -->
            <svg 
              v-if="showOffsetLine" 
              class="absolute inset-0 w-full h-full pointer-events-none"
              :width="targetSize" 
              :height="targetSize"
            >
              <line 
                :x1="fletchedGroup.x" 
                :y1="fletchedGroup.y"
                :x2="bareshaftGroup.x" 
                :y2="bareshaftGroup.y"
                stroke="#3B82F6" 
                stroke-width="2" 
                stroke-dasharray="5,5"
              />
              <!-- Offset Distance Label -->
              <text 
                :x="(fletchedGroup.x + bareshaftGroup.x) / 2"
                :y="(fletchedGroup.y + bareshaftGroup.y) / 2 - 10"
                fill="#3B82F6"
                text-anchor="middle"
                class="text-sm font-medium"
              >
                {{ offsetDistance.toFixed(1) }} cm
              </text>
            </svg>
          </div>
        </div>
        
        <!-- Target Instructions -->
        <div class="mt-4 text-center">
          <div class="text-sm text-gray-600 dark:text-gray-300 space-y-1">
            <p v-if="!fletchedGroup.placed">
              <span class="inline-flex items-center">
                <span class="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                Click to place <strong>fletched group center</strong>
              </span>
            </p>
            <p v-else-if="!bareshaftGroup.placed">
              <span class="inline-flex items-center">
                <span class="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                Click to place <strong>bareshaft group center</strong>
              </span>
            </p>
            <p v-else class="text-green-600 dark:text-green-400 font-medium">
              Groups placed! Offset: {{ offsetDistance.toFixed(1) }} cm
            </p>
          </div>
        </div>

        <!-- Reset Button -->
        <div class="mt-4 text-center">
          <button 
            @click="resetGroups"
            class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white text-sm font-medium rounded-lg transition-colors"
          >
            Reset Groups
          </button>
        </div>
      </div>
    </div>

    <!-- Group Consistency Assessment -->
    <div class="mb-6" v-if="bothGroupsPlaced">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Group Consistency
      </label>
      <div class="grid grid-cols-2 gap-4">
        <div 
          @click="groupConsistency = 'tight'"
          class="p-3 border rounded-lg cursor-pointer transition-all duration-200 text-center"
          :class="groupConsistency === 'tight' 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400'"
        >
          <div class="font-medium text-gray-900 dark:text-gray-100">Tight Groups</div>
          <div class="text-sm text-gray-600 dark:text-gray-300">Both groups are consistent</div>
        </div>
        <div 
          @click="groupConsistency = 'loose'"
          class="p-3 border rounded-lg cursor-pointer transition-all duration-200 text-center"
          :class="groupConsistency === 'loose' 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400'"
        >
          <div class="font-medium text-gray-900 dark:text-gray-100">Loose Groups</div>
          <div class="text-sm text-gray-600 dark:text-gray-300">Groups are scattered</div>
        </div>
      </div>
    </div>

    <!-- Offset Analysis -->
    <div class="mb-6" v-if="bothGroupsPlaced">
      <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
        <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">
          Analysis
        </h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {{ offsetDistance.toFixed(1) }}
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-300">cm offset</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {{ offsetDirection }}
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-300">direction</div>
          </div>
          <div>
            <div class="text-2xl font-bold" :class="toleranceStatus.color">
              {{ toleranceStatus.status }}
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-300">within tolerance</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {{ spineIndication }}
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-300">spine indication</div>
          </div>
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
            <div>Offset: {{ test.test_data.offset_distance_cm || 'N/A' }}cm {{ test.test_data.bareshaft_offset || '' }}</div>
            <div>Distance: {{ test.test_data.shooting_distance_m || 'N/A' }}m</div>
            <div>Consistency: {{ test.test_data.group_consistency || 'N/A' }}</div>
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
import { ref, computed, onMounted } from 'vue'
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
const testDistance = ref(20)  // yards
const groupConsistency = ref('tight')
const notes = ref('')
const recording = ref(false)
const showResults = ref(false)
const showPreviousTests = ref(false)
const testResults = ref(null)
const previousTests = ref([])

// Target interface data
const targetSize = 300  // pixels
const fletchedGroup = ref({ x: null, y: null, placed: false })
const bareshaftGroup = ref({ x: null, y: null, placed: false })
const targetFace = ref(null)

const environmentalConditions = ref({
  temperature: null,
  humidity: null,
  wind_speed: null,
  lighting: ''
})

// Constants
const commonDistances = [10, 15, 18, 20, 25, 30]
const targetRings = [
  { size: 280 },
  { size: 240 },
  { size: 200 },
  { size: 160 },
  { size: 120 },
  { size: 80 },
  { size: 40 }
]

// API composable
const api = useApi()

// Computed properties
const bothGroupsPlaced = computed(() => {
  return fletchedGroup.value.placed && bareshaftGroup.value.placed
})

const showOffsetLine = computed(() => bothGroupsPlaced.value)

const offsetDistance = computed(() => {
  if (!bothGroupsPlaced.value) return 0
  
  const dx = bareshaftGroup.value.x - fletchedGroup.value.x
  const dy = bareshaftGroup.value.y - fletchedGroup.value.y
  const pixelDistance = Math.sqrt(dx * dx + dy * dy)
  
  // Convert pixels to cm (approximate scaling based on target size)
  const cmPerPixel = 20 / targetSize  // Assuming 20cm target diameter
  return pixelDistance * cmPerPixel
})

const offsetDirection = computed(() => {
  if (!bothGroupsPlaced.value) return 'N/A'
  
  const dx = bareshaftGroup.value.x - fletchedGroup.value.x
  const dy = bareshaftGroup.value.y - fletchedGroup.value.y
  
  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0 ? 'right' : 'left'
  } else {
    return dy > 0 ? 'low' : 'high'
  }
})

const toleranceStatus = computed(() => {
  const tolerance = 7.0 * (testDistance.value / 20)  // Scale tolerance based on distance
  const offset = offsetDistance.value
  
  if (offset <= tolerance) {
    return { status: 'YES', color: 'text-green-600 dark:text-green-400' }
  } else {
    return { status: 'NO', color: 'text-red-600 dark:text-red-400' }
  }
})

const spineIndication = computed(() => {
  const direction = offsetDirection.value
  if (direction === 'left') return 'Too Stiff'
  if (direction === 'right') return 'Too Weak'
  return 'Good'
})

const canRecordTest = computed(() => {
  return bothGroupsPlaced.value && groupConsistency.value
})

// Methods
const handleTargetClick = (event) => {
  if (!targetFace.value) return
  
  const rect = targetFace.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  if (!fletchedGroup.value.placed) {
    fletchedGroup.value = { x, y, placed: true }
  } else if (!bareshaftGroup.value.placed) {
    bareshaftGroup.value = { x, y, placed: true }
  }
}

const resetGroups = () => {
  fletchedGroup.value = { x: null, y: null, placed: false }
  bareshaftGroup.value = { x: null, y: null, placed: false }
}

const loadPreviousTests = async () => {
  try {
    const response = await api.get(`/arrows/${props.sessionData.arrow_id}/tuning-history`, {
      params: {
        bow_setup_id: props.sessionData.bow_setup.id,
        test_type: 'bareshaft_tuning'
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
      bareshaft_offset: offsetDirection.value,
      offset_distance_cm: offsetDistance.value,
      shooting_distance_m: testDistance.value * 0.9144,  // Convert yards to meters
      group_consistency: groupConsistency.value
    }
    
    const requestData = {
      test_data: testData,
      environmental_conditions: environmentalConditions.value,
      shooting_distance: testDistance.value,
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

// Lifecycle
onMounted(() => {
  loadPreviousTests()
})
</script>

<style scoped>
/* Custom styles for target interface */
.target-ring {
  border: 1px solid #cbd5e1;
}
</style>