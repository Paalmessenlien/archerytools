<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Header ---->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          Tuning History Viewer
        </h2>
        <p class="text-gray-600 dark:text-gray-300" v-if="selectedArrow">
          {{ selectedArrow.manufacturer }} {{ selectedArrow.model_name }} 
          ({{ selectedArrow.arrow_length }}", {{ selectedArrow.point_weight }}gn)
        </p>
        <p class="text-gray-600 dark:text-gray-300" v-else>
          View comprehensive tuning history for your arrows
        </p>
      </div>
      <button 
        @click="$emit('close')"
        class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- Arrow Selection (if not pre-selected) -->
    <div class="mb-6" v-if="!selectedArrow">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Select Arrow Configuration
      </label>
      <div v-if="loading.arrows" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600 dark:text-gray-300">Loading arrows...</span>
      </div>
      <div v-else-if="!availableArrows.length" class="text-center py-8">
        <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
        <p class="text-gray-500 dark:text-gray-400">No arrows with tuning history found</p>
      </div>
      <div v-else class="grid grid-cols-1 gap-3 max-h-80 overflow-y-auto">
        <div 
          v-for="arrow in availableArrows" 
          :key="`${arrow.arrow_id}-${arrow.arrow_length}-${arrow.point_weight}`"
          @click="loadHistoryForArrow(arrow)"
          class="p-4 border rounded-lg cursor-pointer transition-all duration-200 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-700/50"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">
                {{ arrow.manufacturer }} {{ arrow.model_name }}
              </h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600 dark:text-gray-300">
                <div><span class="font-medium">Length:</span> {{ arrow.arrow_length }}"</div>
                <div><span class="font-medium">Point:</span> {{ arrow.point_weight }} gn</div>
                <div><span class="font-medium">Spine:</span> {{ arrow.spine_value || 'N/A' }}</div>
                <div><span class="font-medium">Bow:</span> {{ arrow.bow_setup_name }}</div>
              </div>
            </div>
            <div class="ml-4 text-right">
              <div class="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-2 py-1 rounded-full text-xs font-medium">
                {{ arrow.total_tests || 0 }} tests
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-1" v-if="arrow.last_test_date">
                Last: {{ formatDate(arrow.last_test_date) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Test History Display -->
    <div v-if="selectedArrow || historyData.length > 0">
      <!-- History Filters -->
      <div class="mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex flex-col sm:flex-row gap-4">
            <!-- Test Type Filter -->
            <div class="flex-1">
              <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                Test Type
              </label>
              <select 
                v-model="filters.testType"
                @change="applyFilters"
                class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
              >
                <option value="">All Types</option>
                <option value="paper_tuning">Paper Tuning</option>
                <option value="bareshaft_tuning">Bareshaft Tuning</option>
                <option value="walkback_tuning">Walkback Tuning</option>
              </select>
            </div>
            
            <!-- Date Range Filter -->
            <div class="flex-1">
              <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                Date Range
              </label>
              <select 
                v-model="filters.dateRange"
                @change="applyFilters"
                class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
              >
                <option value="">All Time</option>
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 3 months</option>
                <option value="365">Last year</option>
              </select>
            </div>
          </div>

          <!-- Summary Stats -->
          <div class="flex items-center space-x-4 text-sm">
            <div class="text-center">
              <div class="font-bold text-gray-900 dark:text-gray-100">{{ filteredHistory.length }}</div>
              <div class="text-gray-600 dark:text-gray-300">Total Tests</div>
            </div>
            <div class="text-center" v-if="averageConfidence > 0">
              <div class="font-bold text-blue-600 dark:text-blue-400">{{ averageConfidence }}%</div>
              <div class="text-gray-600 dark:text-gray-300">Avg Confidence</div>
            </div>
          </div>
        </div>
      </div>

      <!-- History Loading -->
      <div v-if="loading.history" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600 dark:text-gray-300">Loading tuning history...</span>
      </div>

      <!-- No History Message -->
      <div v-else-if="!filteredHistory.length" class="text-center py-12">
        <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <p class="text-gray-500 dark:text-gray-400 mb-4">
          {{ filters.testType || filters.dateRange ? 'No tests match the current filters' : 'No tuning history found' }}
        </p>
        <button 
          v-if="filters.testType || filters.dateRange"
          @click="clearFilters"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Clear Filters
        </button>
      </div>

      <!-- History Timeline -->
      <div v-else class="space-y-4 max-h-96 overflow-y-auto">
        <div 
          v-for="test in filteredHistory" 
          :key="test.id"
          class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
        >
          <!-- Test Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div 
                  class="w-3 h-3 rounded-full"
                  :class="getTestTypeColor(test.test_type)"
                ></div>
              </div>
              <div>
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                  {{ formatTestType(test.test_type) }} Test #{{ test.test_number }}
                  <!-- Data Source Badge -->
                  <span 
                    v-if="test.source === 'change_log'"
                    class="ml-2 px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded-full"
                    title="Enhanced change log data"
                  >
                    Enhanced
                  </span>
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(test.created_at) }}
                  <span v-if="test.bow_setup_name" class="ml-2">• {{ test.bow_setup_name }}</span>
                </p>
              </div>
            </div>
            <div class="text-right">
              <div 
                class="px-2 py-1 rounded-full text-xs font-medium"
                :class="getConfidenceColor(test.confidence_score)"
              >
                {{ Math.round(test.confidence_score || 0) }}% confidence
              </div>
            </div>
          </div>

          <!-- Test Data Summary -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-3">
            <!-- Paper Tuning Data -->
            <template v-if="test.test_type === 'paper_tuning'">
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Tear Direction</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.tear_direction || 'N/A' }}
                </div>
              </div>
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Magnitude</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.tear_magnitude || 'N/A' }}
                </div>
              </div>
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Consistency</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.consistency || 'N/A' }}
                </div>
              </div>
            </template>

            <!-- Bareshaft Tuning Data -->
            <template v-if="test.test_type === 'bareshaft_tuning'">
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Offset Direction</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.bareshaft_offset || 'N/A' }}
                </div>
              </div>
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Offset Distance</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.offset_distance_cm ? `${test.test_data.offset_distance_cm} cm` : 'N/A' }}
                </div>
              </div>
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Group Quality</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.group_consistency || 'N/A' }}
                </div>
              </div>
            </template>

            <!-- Walkback Tuning Data -->
            <template v-if="test.test_type === 'walkback_tuning'">
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Drift Direction</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.drift_direction || 'N/A' }}
                </div>
              </div>
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">R-Squared</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.r_squared ? test.test_data.r_squared.toFixed(3) : 'N/A' }}
                </div>
              </div>
              <div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Data Points</span>
                <div class="text-sm text-gray-900 dark:text-gray-100">
                  {{ test.test_data?.data_points?.length || 0 }}
                </div>
              </div>
            </template>

            <!-- Common Data -->
            <div>
              <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Distance</span>
              <div class="text-sm text-gray-900 dark:text-gray-100">
                {{ test.shooting_distance || 'N/A' }} yards
              </div>
            </div>
          </div>

          <!-- Recommendations Summary -->
          <div v-if="test.recommendations && test.recommendations.length > 0" class="mb-3">
            <div class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
              Recommendations ({{ test.recommendations.length }})
            </div>
            <div class="space-y-1">
              <div 
                v-for="(rec, index) in test.recommendations.slice(0, 2)" 
                :key="index"
                class="text-sm"
              >
                <span class="font-medium text-gray-900 dark:text-gray-100">
                  {{ rec.component }}: 
                </span>
                <span class="text-gray-600 dark:text-gray-300">
                  {{ rec.action }} ({{ rec.magnitude }})
                </span>
                <span 
                  class="ml-2 px-1.5 py-0.5 text-xs font-medium rounded-full"
                  :class="rec.priority === 1 
                    ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' 
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'"
                >
                  P{{ rec.priority }}
                </span>
              </div>
              <button 
                v-if="test.recommendations.length > 2"
                @click="expandTest(test)"
                class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
              >
                +{{ test.recommendations.length - 2 }} more recommendations
              </button>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="test.notes" class="text-sm text-gray-600 dark:text-gray-300 border-t border-gray-200 dark:border-gray-600 pt-3">
            <span class="font-medium">Notes:</span> {{ test.notes }}
          </div>

          <!-- Expand/Collapse Button -->
          <div class="flex items-center justify-end mt-3">
            <button 
              @click="toggleTestDetails(test)"
              class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center"
            >
              {{ test.expanded ? 'Less Details' : 'More Details' }}
              <svg 
                class="w-4 h-4 ml-1 transition-transform duration-200"
                :class="test.expanded ? 'rotate-180' : ''"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>
          </div>

          <!-- Expanded Details -->
          <div v-if="test.expanded" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
            <!-- Environmental Conditions -->
            <div v-if="test.environmental_conditions" class="mb-4">
              <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Environmental Conditions</h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                <div v-if="test.environmental_conditions.temperature">
                  <span class="text-gray-600 dark:text-gray-400">Temp:</span>
                  <span class="ml-1 text-gray-900 dark:text-gray-100">{{ test.environmental_conditions.temperature }}°F</span>
                </div>
                <div v-if="test.environmental_conditions.humidity">
                  <span class="text-gray-600 dark:text-gray-400">Humidity:</span>
                  <span class="ml-1 text-gray-900 dark:text-gray-100">{{ test.environmental_conditions.humidity }}%</span>
                </div>
                <div v-if="test.environmental_conditions.wind_speed">
                  <span class="text-gray-600 dark:text-gray-400">Wind:</span>
                  <span class="ml-1 text-gray-900 dark:text-gray-100">{{ test.environmental_conditions.wind_speed }} mph</span>
                </div>
                <div v-if="test.environmental_conditions.lighting">
                  <span class="text-gray-600 dark:text-gray-400">Light:</span>
                  <span class="ml-1 text-gray-900 dark:text-gray-100 capitalize">{{ test.environmental_conditions.lighting }}</span>
                </div>
              </div>
            </div>

            <!-- All Recommendations -->
            <div v-if="test.recommendations && test.recommendations.length > 0" class="mb-4">
              <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">All Recommendations</h4>
              <div class="space-y-2">
                <div 
                  v-for="(rec, index) in test.recommendations" 
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
                      <span 
                        class="px-2 py-1 text-xs font-medium rounded-full"
                        :class="rec.priority === 1 
                          ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' 
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'"
                      >
                        Priority {{ rec.priority }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Raw Test Data -->
            <div class="mb-4">
              <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Raw Test Data</h4>
              <pre class="text-xs bg-gray-100 dark:bg-gray-700 p-3 rounded-md overflow-x-auto text-gray-900 dark:text-gray-100">{{ JSON.stringify(test.test_data, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Progress Analysis (if multiple tests) -->
      <div v-if="filteredHistory.length > 1" class="mt-8">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Progress Analysis</h3>
        <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <div class="text-2xl font-bold text-green-600 dark:text-green-400">
                {{ improvementTrend }}%
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">Confidence Improvement</div>
            </div>
            <div>
              <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {{ filteredHistory.length }}
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">Total Tests</div>
            </div>
            <div>
              <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {{ mostCommonTestType }}
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">Most Common Test</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-between mt-6">
      <button 
        @click="$emit('close')"
        class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
      >
        Close
      </button>
      <div class="space-x-3">
        <button 
          v-if="selectedArrow"
          @click="$emit('start-new-test', selectedArrow)"
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
        >
          Start New Test
        </button>
        <button 
          v-if="filteredHistory.length > 0"
          @click="exportHistory"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Export History
        </button>
        <button 
          v-if="selectedArrow"
          @click="exportAdjustments"
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
        >
          Export Adjustments
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'

// Props
const props = defineProps({
  arrowId: {
    type: [String, Number],
    default: null
  },
  bowSetupId: {
    type: [String, Number],
    default: null
  },
  initialArrow: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'start-new-test'])

// Reactive data
const selectedArrow = ref(props.initialArrow)
const availableArrows = ref([])
const historyData = ref([])
const filteredHistory = ref([])

const loading = ref({
  arrows: false,
  history: false
})

const filters = ref({
  testType: '',
  dateRange: ''
})

// API composable
const api = useApi()

// Computed properties
const averageConfidence = computed(() => {
  if (!filteredHistory.value.length) return 0
  const total = filteredHistory.value.reduce((sum, test) => sum + (test.confidence_score || 0), 0)
  return Math.round(total / filteredHistory.value.length)
})

const improvementTrend = computed(() => {
  if (filteredHistory.value.length < 2) return 0
  
  const sorted = [...filteredHistory.value].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  const firstScore = sorted[0]?.confidence_score || 0
  const lastScore = sorted[sorted.length - 1]?.confidence_score || 0
  
  if (firstScore === 0) return 0
  return Math.round(((lastScore - firstScore) / firstScore) * 100)
})

const mostCommonTestType = computed(() => {
  if (!filteredHistory.value.length) return 'N/A'
  
  const counts = {}
  filteredHistory.value.forEach(test => {
    counts[test.test_type] = (counts[test.test_type] || 0) + 1
  })
  
  const mostCommon = Object.entries(counts).sort((a, b) => b[1] - a[1])[0]
  return mostCommon ? formatTestType(mostCommon[0]) : 'N/A'
})

// Methods
const loadAvailableArrows = async () => {
  loading.value.arrows = true
  try {
    const response = await api.get('/arrows/with-tuning-history')
    availableArrows.value = response.arrows || []
  } catch (error) {
    console.error('Failed to load arrows with tuning history:', error)
    availableArrows.value = []
  } finally {
    loading.value.arrows = false
  }
}

const loadHistoryForArrow = async (arrow = null) => {
  const targetArrow = arrow || selectedArrow.value
  if (!targetArrow) return

  loading.value.history = true
  try {
    // Try to load from enhanced change log system first
    let changeLogHistory = []
    try {
      const changeLogParams = {
        arrow_id: targetArrow.arrow_id || targetArrow.id,
        ...(props.bowSetupId && { bow_setup_id: props.bowSetupId })
      }
      
      const changeLogResponse = await api.get('/tuning-change-log', { params: changeLogParams })
      changeLogHistory = (changeLogResponse.test_history || []).map(test => ({
        ...test,
        expanded: false,
        source: 'change_log'
      }))
    } catch (changeLogError) {
      console.warn('Could not load from change log system:', changeLogError)
    }
    
    // Load from original tuning history system
    const params = {
      ...(props.bowSetupId && { bow_setup_id: props.bowSetupId })
    }
    
    const response = await api.get(`/arrows/${targetArrow.arrow_id || targetArrow.id}/tuning-history`, { params })
    const originalHistory = (response.test_results || []).map(test => ({
      ...test,
      expanded: false,
      source: 'original'
    }))
    
    // Merge and deduplicate histories (prefer change log data for newer entries)
    const combinedHistory = [...changeLogHistory, ...originalHistory]
    
    // Remove duplicates based on test_result_id or created_at + test_type
    const uniqueHistory = combinedHistory.filter((test, index, self) => {
      return index === self.findIndex(t => 
        (t.test_result_id && test.test_result_id && t.test_result_id === test.test_result_id) ||
        (t.created_at === test.created_at && t.test_type === test.test_type)
      )
    })
    
    historyData.value = uniqueHistory
    
    if (arrow) {
      selectedArrow.value = arrow
    }
    
    applyFilters()
  } catch (error) {
    console.error('Failed to load tuning history:', error)
    historyData.value = []
    filteredHistory.value = []
  } finally {
    loading.value.history = false
  }
}

const applyFilters = () => {
  let filtered = [...historyData.value]
  
  // Filter by test type
  if (filters.value.testType) {
    filtered = filtered.filter(test => test.test_type === filters.value.testType)
  }
  
  // Filter by date range
  if (filters.value.dateRange) {
    const days = parseInt(filters.value.dateRange)
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - days)
    
    filtered = filtered.filter(test => new Date(test.created_at) >= cutoffDate)
  }
  
  // Sort by date (most recent first)
  filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  
  filteredHistory.value = filtered
}

const clearFilters = () => {
  filters.value = {
    testType: '',
    dateRange: ''
  }
  applyFilters()
}

const toggleTestDetails = (test) => {
  test.expanded = !test.expanded
}

const expandTest = (test) => {
  test.expanded = true
}

const exportHistory = () => {
  try {
    const data = filteredHistory.value.map(test => ({
      date: test.created_at,
      test_type: test.test_type,
      test_number: test.test_number,
      confidence_score: test.confidence_score,
      test_data: test.test_data,
      recommendations: test.recommendations,
      notes: test.notes,
      environmental_conditions: test.environmental_conditions,
      shooting_distance: test.shooting_distance
    }))
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `tuning-history-${selectedArrow.value?.manufacturer || 'arrow'}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export history:', error)
  }
}

const exportAdjustments = async () => {
  if (!selectedArrow.value) return
  
  try {
    const params = {
      ...(props.bowSetupId && { bow_setup_id: props.bowSetupId })
    }
    
    const response = await api.get('/equipment-adjustments', { params })
    const adjustments = response.adjustments || []
    
    const data = adjustments.map(adj => ({
      date: adj.created_at,
      component: adj.component,
      adjustment_type: adj.adjustment_type,
      old_value: adj.old_value,
      new_value: adj.new_value,
      reason: adj.reason,
      bow_setup_name: adj.bow_setup_name,
      related_test_type: adj.related_test_type,
      related_test_number: adj.related_test_number
    }))
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `tuning-adjustments-${selectedArrow.value?.manufacturer || 'arrow'}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export adjustments:', error)
  }
}

// Utility methods
const formatTestType = (testType) => {
  const types = {
    'paper_tuning': 'Paper Tuning',
    'bareshaft_tuning': 'Bareshaft Tuning',
    'walkback_tuning': 'Walkback Tuning'
  }
  return types[testType] || testType
}

const formatDate = (dateString) => {
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return 'N/A'
  }
}

const getTestTypeColor = (testType) => {
  const colors = {
    'paper_tuning': 'bg-green-500',
    'bareshaft_tuning': 'bg-blue-500',
    'walkback_tuning': 'bg-purple-500'
  }
  return colors[testType] || 'bg-gray-500'
}

const getConfidenceColor = (score) => {
  const numScore = score || 0
  if (numScore >= 80) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
  if (numScore >= 60) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
  return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
}

// Watch for prop changes
watch(() => props.arrowId, (newArrowId) => {
  if (newArrowId && !selectedArrow.value) {
    // Load specific arrow history
    loadHistoryForArrow({ arrow_id: newArrowId })
  }
}, { immediate: true })

watch(() => props.initialArrow, (newArrow) => {
  if (newArrow) {
    selectedArrow.value = newArrow
    loadHistoryForArrow()
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  if (props.arrowId) {
    // Load specific arrow history
    loadHistoryForArrow({ arrow_id: props.arrowId })
  } else if (props.initialArrow) {
    // Load history for provided arrow
    loadHistoryForArrow()
  } else {
    // Load all available arrows
    loadAvailableArrows()
  }
})
</script>

<style scoped>
/* Custom scrollbar for history list */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.dark .overflow-y-auto::-webkit-scrollbar-track {
  background: #374151;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background: #6b7280;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>