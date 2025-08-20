<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Header with Session Info -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          Paper Tuning Test #{{ testNumber }}
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
        Paper Tuning Instructions
      </h3>
      <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
        <li>• Set up paper frame 3-4 feet from the target</li>
        <li>• Shoot from {{ sessionData.settings?.shooting_distance || 20 }} yards through the paper</li>
        <li>• Examine the tear pattern in the paper</li>
        <li>• Click on the grid below to indicate the tear direction and magnitude</li>
      </ul>
    </div>

    <!-- 3x3 Tear Pattern Grid -->
    <div class="mb-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        Select Tear Pattern
      </h3>
      <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6">
        <!-- Grid Instructions -->
        <div class="text-center mb-4">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Click the grid position that best represents your arrow's tear through the paper
          </p>
        </div>
        
        <!-- 3x3 Grid -->
        <div class="grid grid-cols-3 gap-2 max-w-xs mx-auto mb-4">
          <!-- Top Row -->
          <div 
            v-for="position in tearPositions.slice(0, 3)" 
            :key="position.id"
            @click="selectTearPosition(position)"
            class="aspect-square border-2 rounded-lg cursor-pointer transition-all duration-200 flex items-center justify-center relative"
            :class="selectedTearPosition?.id === position.id 
              ? 'border-blue-500 bg-blue-100 dark:bg-blue-900/30' 
              : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-gray-100 dark:hover:bg-gray-600/50'"
          >
            <!-- Grid Position Visual -->
            <div class="text-xs text-gray-500 dark:text-gray-400">
              {{ position.label }}
            </div>
            <!-- Tear Direction Arrow -->
            <div v-if="position.direction !== 'clean'" class="absolute inset-0 flex items-center justify-center">
              <svg 
                class="w-6 h-6 text-red-500" 
                :class="getTearArrowClass(position.direction)"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
              </svg>
            </div>
            <!-- Clean Hole Indicator -->
            <div v-else class="absolute inset-0 flex items-center justify-center">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>

          <!-- Middle Row -->
          <div 
            v-for="position in tearPositions.slice(3, 6)" 
            :key="position.id"
            @click="selectTearPosition(position)"
            class="aspect-square border-2 rounded-lg cursor-pointer transition-all duration-200 flex items-center justify-center relative"
            :class="selectedTearPosition?.id === position.id 
              ? 'border-blue-500 bg-blue-100 dark:bg-blue-900/30' 
              : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-gray-100 dark:hover:bg-gray-600/50'"
          >
            <div class="text-xs text-gray-500 dark:text-gray-400">
              {{ position.label }}
            </div>
            <div v-if="position.direction !== 'clean'" class="absolute inset-0 flex items-center justify-center">
              <svg 
                class="w-6 h-6 text-red-500" 
                :class="getTearArrowClass(position.direction)"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
              </svg>
            </div>
            <div v-else class="absolute inset-0 flex items-center justify-center">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>

          <!-- Bottom Row -->
          <div 
            v-for="position in tearPositions.slice(6, 9)" 
            :key="position.id"
            @click="selectTearPosition(position)"
            class="aspect-square border-2 rounded-lg cursor-pointer transition-all duration-200 flex items-center justify-center relative"
            :class="selectedTearPosition?.id === position.id 
              ? 'border-blue-500 bg-blue-100 dark:bg-blue-900/30' 
              : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-gray-100 dark:hover:bg-gray-600/50'"
          >
            <div class="text-xs text-gray-500 dark:text-gray-400">
              {{ position.label }}
            </div>
            <div v-if="position.direction !== 'clean'" class="absolute inset-0 flex items-center justify-center">
              <svg 
                class="w-6 h-6 text-red-500" 
                :class="getTearArrowClass(position.direction)"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
              </svg>
            </div>
            <div v-else class="absolute inset-0 flex items-center justify-center">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>
        </div>

        <!-- Selected Position Info -->
        <div v-if="selectedTearPosition" class="text-center mb-4">
          <div class="text-lg font-medium text-gray-900 dark:text-gray-100">
            Selected: {{ selectedTearPosition.description }}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">
            {{ selectedTearPosition.indication }}
          </div>
        </div>
      </div>
    </div>

    <!-- Tear Magnitude Selection -->
    <div class="mb-6" v-if="selectedTearPosition && selectedTearPosition.direction !== 'clean'">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Tear Magnitude
      </label>
      <div class="grid grid-cols-3 gap-4">
        <div 
          v-for="magnitude in tearMagnitudes" 
          :key="magnitude.id"
          @click="selectedMagnitude = magnitude.id"
          class="p-3 border rounded-lg cursor-pointer transition-all duration-200 text-center"
          :class="selectedMagnitude === magnitude.id 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400'"
        >
          <div class="font-medium text-gray-900 dark:text-gray-100">
            {{ magnitude.name }}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">
            {{ magnitude.description }}
          </div>
        </div>
      </div>
    </div>

    <!-- Consistency Assessment -->
    <div class="mb-6" v-if="selectedTearPosition">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Tear Consistency
      </label>
      <div class="grid grid-cols-2 gap-4">
        <div 
          @click="consistency = 'consistent'"
          class="p-3 border rounded-lg cursor-pointer transition-all duration-200 text-center"
          :class="consistency === 'consistent' 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400'"
        >
          <div class="font-medium text-gray-900 dark:text-gray-100">Consistent</div>
          <div class="text-sm text-gray-600 dark:text-gray-300">Same pattern each shot</div>
        </div>
        <div 
          @click="consistency = 'inconsistent'"
          class="p-3 border rounded-lg cursor-pointer transition-all duration-200 text-center"
          :class="consistency === 'inconsistent' 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400'"
        >
          <div class="font-medium text-gray-900 dark:text-gray-100">Inconsistent</div>
          <div class="text-sm text-gray-600 dark:text-gray-300">Varying patterns</div>
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
            <div>Pattern: {{ test.test_data.tear_direction || 'N/A' }}</div>
            <div>Magnitude: {{ test.test_data.tear_magnitude || 'N/A' }}</div>
            <div>Consistency: {{ test.test_data.consistency || 'N/A' }}</div>
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
const selectedTearPosition = ref(null)
const selectedMagnitude = ref('')
const consistency = ref('consistent')
const notes = ref('')
const recording = ref(false)
const showResults = ref(false)
const showPreviousTests = ref(false)
const testResults = ref(null)
const previousTests = ref([])

const environmentalConditions = ref({
  temperature: null,
  humidity: null,
  wind_speed: null,
  lighting: ''
})

// Define tear positions for 3x3 grid
const tearPositions = [
  // Top row
  { id: 'nock-left-high', label: 'NL-H', direction: 'nock-left-high', description: 'Nock Left High', indication: 'High and left tear' },
  { id: 'high', label: 'HIGH', direction: 'high', description: 'High Tear', indication: 'Arrow impacting high' },
  { id: 'nock-right-high', label: 'NR-H', direction: 'nock-right-high', description: 'Nock Right High', indication: 'High and right tear' },
  
  // Middle row
  { id: 'left', label: 'LEFT', direction: 'left', description: 'Left Tear', indication: 'Arrow too stiff' },
  { id: 'clean', label: 'CLEAN', direction: 'clean', description: 'Clean Hole', indication: 'Perfect tune!' },
  { id: 'right', label: 'RIGHT', direction: 'right', description: 'Right Tear', indication: 'Arrow too weak' },
  
  // Bottom row
  { id: 'nock-left-low', label: 'NL-L', direction: 'nock-left-low', description: 'Nock Left Low', indication: 'Low and left tear' },
  { id: 'low', label: 'LOW', direction: 'low', description: 'Low Tear', indication: 'Arrow impacting low' },
  { id: 'nock-right-low', label: 'NR-L', direction: 'nock-right-low', description: 'Nock Right Low', indication: 'Low and right tear' }
]

const tearMagnitudes = [
  { id: 'slight', name: 'Slight', description: 'Barely noticeable' },
  { id: 'moderate', name: 'Moderate', description: 'Clearly visible' },
  { id: 'severe', name: 'Severe', description: 'Very pronounced' }
]

// API composable
const api = useApi()

// Computed properties
const canRecordTest = computed(() => {
  return selectedTearPosition.value && consistency.value &&
         (selectedTearPosition.value.direction === 'clean' || selectedMagnitude.value)
})

// Methods
const selectTearPosition = (position) => {
  selectedTearPosition.value = position
  if (position.direction === 'clean') {
    selectedMagnitude.value = 'none'
  } else {
    selectedMagnitude.value = ''
  }
}

const getTearArrowClass = (direction) => {
  const classes = {
    'high': 'transform -rotate-180',
    'low': 'transform rotate-0',
    'left': 'transform rotate-90',
    'right': 'transform -rotate-90',
    'nock-left-high': 'transform rotate-135',
    'nock-right-high': 'transform -rotate-135',
    'nock-left-low': 'transform rotate-45',
    'nock-right-low': 'transform -rotate-45'
  }
  return classes[direction] || ''
}

const loadPreviousTests = async () => {
  try {
    const response = await api.get(`/arrows/${props.sessionData.arrow_id}/tuning-history`, {
      params: {
        bow_setup_id: props.sessionData.bow_setup.id,
        test_type: 'paper_tuning'
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
      tear_direction: selectedTearPosition.value.direction,
      tear_magnitude: selectedMagnitude.value,
      consistency: consistency.value,
      shooting_distance: props.sessionData.settings?.shooting_distance || 20
    }
    
    const requestData = {
      test_data: testData,
      environmental_conditions: environmentalConditions.value,
      shooting_distance: props.sessionData.settings?.shooting_distance || 20,
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
    // Could add notification here
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
.aspect-square {
  aspect-ratio: 1;
}
</style>