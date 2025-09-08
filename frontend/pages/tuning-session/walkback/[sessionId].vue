<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Session Header -->
      <TuningSessionHeader
        :session-id="route.params.sessionId"
        session-type="walkback"
        :arrow-info="sessionData?.setup_arrow?.arrow_name || 'Unknown Arrow'"
        :bow-setup-name="sessionData?.bow_setup?.setup_name || 'Unknown Setup'"
        :session-status="sessionData?.status || 'active'"
        :tests-completed="completedTests.length"
        :total-tests="6"
        :start-time="sessionData?.created_at ? new Date(sessionData.created_at) : new Date()"
        :can-save="completedTests.length >= 3"
        :show-progress="true"
        @pause-resume="handlePause"
        @abandon-session="handleAbandon"
        @save-exit="handleSaveExit"
      />

      <!-- Enhanced Session Progress -->
      <div class="mb-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Walkback Progress</h3>
            <div class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
              <span>{{ completedDistances.length }} distances tested</span>
              <span v-if="sessionQualityScore > 0" class="px-2 py-1 rounded-full text-xs font-medium"
                    :class="getQualityScoreClasses(sessionQualityScore)">
                {{ Math.round(sessionQualityScore) }}% accuracy
              </span>
            </div>
          </div>
          
          <!-- Distance Progress Visualization -->
          <div class="space-y-4">
            <!-- Distance Progress Dots -->
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div 
                  v-for="(distance, index) in plannedDistances" 
                  :key="distance"
                  class="flex flex-col items-center space-y-1"
                >
                  <!-- Distance dot with quality indicator -->
                  <div class="relative">
                    <div v-if="getDistanceTestData(distance)" 
                         class="absolute inset-0 w-6 h-6 rounded-full border-2 -m-1"
                         :class="getDistanceQualityRingClass(getDistanceTestData(distance)?.confidence_score || 0)">
                    </div>
                    <div class="w-4 h-4 rounded-full relative z-10"
                         :class="getDistanceStatusClass(distance)">
                    </div>
                  </div>
                  <!-- Distance label -->
                  <span class="text-xs font-medium" 
                        :class="currentDistance === distance ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500'">
                    {{ distance }}m
                  </span>
                </div>
              </div>
              
              <!-- Drift Analysis Summary -->
              <div v-if="completedDistances.length >= 2" class="flex items-center gap-2 text-sm">
                <div class="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  <i :class="driftAnalysis.icon"></i>
                  <span>{{ driftAnalysis.text }}</span>
                </div>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div class="h-2 rounded-full transition-all duration-500 bg-gradient-to-r"
                   :class="progressBarGradient"
                   :style="{ width: `${progressPercentage}%` }">
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Current Test Section (Left Column) -->
        <div class="space-y-6">
          <!-- Progressive Step Instructions -->
          <div class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <div class="flex items-start justify-between mb-3">
              <h3 class="text-lg font-medium text-green-900 dark:text-green-100">
                <i class="fas fa-long-arrow-alt-right mr-2"></i>
                Walkback Test - {{ currentDistance }}m
              </h3>
              <div class="text-xs px-2 py-1 bg-green-100 dark:bg-green-800 rounded-full text-green-700 dark:text-green-200">
                {{ completedDistances.length + 1 }}/{{ plannedDistances.length }}
              </div>
            </div>

            <!-- Current Distance Instructions -->
            <div class="space-y-3 mb-4">
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  1
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-gray-100">
                    Position at {{ currentDistance }}m from target
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {{ getDistanceInstructions(currentDistance) }}
                  </div>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  2
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-gray-100">
                    Shoot 3-6 arrows at the vertical line
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Use your {{ getSightPin() }} pin. Don't worry about vertical drop - focus on horizontal alignment with the line.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Vertical Line Target Interface -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Target Interface - {{ currentDistance }}m
              </h3>
              <div class="text-sm text-gray-500">
                Click where your arrow group centers
              </div>
            </div>

            <!-- Target with Vertical Line -->
            <div class="relative">
              <div 
                ref="targetCanvas"
                @click="recordArrowImpact"
                class="w-full aspect-square max-w-md mx-auto bg-gradient-to-br from-yellow-100 to-yellow-200 dark:from-yellow-900/30 dark:to-yellow-800/30 rounded-full border-4 border-yellow-400 dark:border-yellow-600 cursor-crosshair relative overflow-hidden"
                style="max-height: 400px;"
              >
                <!-- Concentric rings -->
                <div class="absolute inset-4 border-2 border-yellow-500/50 rounded-full"></div>
                <div class="absolute inset-8 border-2 border-yellow-600/50 rounded-full"></div>
                <div class="absolute inset-12 border-2 border-red-500/50 rounded-full"></div>
                <div class="absolute inset-16 border-2 border-red-600/50 rounded-full"></div>
                
                <!-- Vertical Reference Line -->
                <div class="absolute top-0 bottom-0 left-1/2 w-1 bg-red-600 dark:bg-red-400 transform -translate-x-0.5 z-10">
                </div>
                
                <!-- Center Aiming Point -->
                <div class="absolute top-1/2 left-1/2 w-3 h-3 bg-red-600 dark:bg-red-400 rounded-full transform -translate-x-1.5 -translate-y-1.5 z-20">
                </div>
                
                <!-- Previous Impact Markers -->
                <div 
                  v-for="(impact, index) in currentDistanceImpacts" 
                  :key="index"
                  class="absolute w-3 h-3 transform -translate-x-1.5 -translate-y-1.5 z-30"
                  :style="{ left: impact.x + 'px', top: impact.y + 'px' }"
                >
                  <div class="w-full h-full bg-blue-600 rounded-full border-2 border-white">
                  </div>
                  <div class="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs bg-blue-600 text-white px-1 rounded">
                    {{ index + 1 }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Impact Recording Controls -->
            <div class="mt-6 space-y-4">
              <!-- Test Parameters -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Group Quality
                  </label>
                  <select v-model="groupConsistency" 
                          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100">
                    <option value="excellent">Excellent (tight group)</option>
                    <option value="good">Good (reasonable spread)</option>
                    <option value="fair">Fair (loose group)</option>
                    <option value="poor">Poor (scattered)</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Horizontal Offset
                  </label>
                  <div class="text-lg font-mono bg-gray-100 dark:bg-gray-600 px-3 py-2 rounded border">
                    {{ calculatedOffset }} cm
                  </div>
                </div>
              </div>

              <!-- Notes -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Test Notes (optional)
                </label>
                <textarea v-model="testNotes" 
                          placeholder="Note conditions, observations, or any issues..."
                          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 resize-none"
                          rows="2">
                </textarea>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <button @click="clearCurrentImpacts" 
                          class="px-3 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors">
                    <i class="fas fa-undo mr-2"></i>Clear Impacts
                  </button>
                </div>
                
                <div class="flex items-center gap-3">
                  <button v-if="completedDistances.length > 0"
                          @click="skipDistance"
                          class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    Skip Distance
                  </button>
                  
                  <button @click="recordDistanceTest" 
                          :disabled="currentDistanceImpacts.length === 0 || recordingTest"
                          class="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center">
                    <i class="fas fa-save mr-2"></i>
                    {{ recordingTest ? 'Recording...' : 'Record Test' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Results and Analysis Section (Right Column) -->
        <div class="space-y-6">
          <!-- Current Session Results -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Walkback Analysis
            </h3>

            <div v-if="completedTests.length === 0" class="text-center py-8 text-gray-500">
              <i class="fas fa-chart-line text-3xl mb-3"></i>
              <p>Complete distance tests to see analysis</p>
            </div>

            <div v-else class="space-y-4">
              <!-- Drift Trend Visualization -->
              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Drift Pattern</h4>
                
                <!-- Simple trend visualization -->
                <div class="relative h-32 bg-white dark:bg-gray-600 rounded border">
                  <!-- Vertical center line -->
                  <div class="absolute top-0 bottom-0 left-1/2 w-0.5 bg-gray-400 transform -translate-x-0.25"></div>
                  
                  <!-- Plot points -->
                  <div 
                    v-for="(test, index) in completedTests" 
                    :key="test.id"
                    class="absolute w-2 h-2 bg-blue-500 rounded-full transform -translate-x-1 -translate-y-1"
                    :style="getPlotPosition(test)"
                  >
                  </div>
                  
                  <!-- Distance labels -->
                  <div class="absolute -bottom-6 left-2 text-xs text-gray-500">{{ minDistance }}m</div>
                  <div class="absolute -bottom-6 right-2 text-xs text-gray-500">{{ maxDistance }}m</div>
                </div>
                
                <div class="mt-4 text-sm">
                  <div class="flex items-center justify-between">
                    <span class="text-gray-600 dark:text-gray-400">Drift Rate:</span>
                    <span class="font-mono font-medium" :class="driftAnalysis.colorClass">
                      {{ formatDriftRate(calculatedSlope) }} cm/m {{ driftAnalysis.direction }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Completed Tests Summary -->
              <div class="space-y-2">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Test Summary</h4>
                <div 
                  v-for="test in completedTests" 
                  :key="test.id"
                  class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded"
                >
                  <div class="flex items-center gap-3">
                    <div class="w-2 h-2 rounded-full" :class="getTestQualityDotClass(test.confidence_score)"></div>
                    <span class="font-medium">{{ test.test_data.distance_m }}m</span>
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    {{ formatOffset(test.test_data.horizontal_offset_cm) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Next Steps -->
          <div v-if="completedTests.length >= 3" class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h3 class="text-lg font-medium text-blue-900 dark:text-blue-100 mb-3">
              <i class="fas fa-tools mr-2"></i>
              Recommended Adjustments
            </h3>

            <div v-if="tuningRecommendations.length > 0" class="space-y-3">
              <div 
                v-for="(recommendation, index) in tuningRecommendations" 
                :key="index"
                class="p-3 bg-white dark:bg-blue-900/30 rounded border border-blue-200 dark:border-blue-700"
              >
                <div class="font-medium text-blue-900 dark:text-blue-100 mb-2">
                  {{ recommendation.title }}
                </div>
                <div class="text-sm text-blue-800 dark:text-blue-200 mb-2">
                  {{ recommendation.instruction }}
                </div>
                <div v-if="recommendation.warning" class="text-xs text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/30 p-2 rounded">
                  <i class="fas fa-exclamation-triangle mr-1"></i>
                  {{ recommendation.warning }}
                </div>
              </div>
            </div>

            <div v-else class="text-center py-4 text-blue-700 dark:text-blue-300">
              <i class="fas fa-check-circle text-2xl mb-2"></i>
              <p>Your bow appears well-tuned! Continue testing if desired.</p>
            </div>
          </div>

          <!-- Complete Session Button -->
          <div v-if="completedTests.length >= 3">
            <button @click="showCompletionModal = true" 
                    class="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors">
              <i class="fas fa-flag-checkered mr-2"></i>
              Complete Walkback Session
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Session Completion Modal -->
    <div v-if="showCompletionModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Complete Walkback Session
        </h3>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Session Summary (optional)
          </label>
          <textarea v-model="completionNotes" 
                    placeholder="Overall results, final adjustments made, or next steps..."
                    class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 resize-none"
                    rows="3">
          </textarea>
        </div>
        
        <div class="flex items-center justify-between">
          <button @click="showCompletionModal = false" 
                  class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
            Cancel
          </button>
          <button @click="completeSession" 
                  :disabled="completingSession"
                  class="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg">
            {{ completingSession ? 'Completing...' : 'Complete Session' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Session Completion Success Modal -->
  <div v-if="showCompletionSuccessModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
      <div class="text-center mb-6">
        <div class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <i class="fas fa-check-circle text-3xl text-green-500"></i>
        </div>
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Walkback Session Complete!
        </h3>
        <p class="text-gray-600 dark:text-gray-400">
          Your walkback tuning session has been saved and added to your journal.
        </p>
      </div>

      <!-- Session Summary -->
      <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-gray-600 dark:text-gray-400">Distances Tested:</span>
          <span class="font-medium">{{ completedTests.length }}</span>
        </div>
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-gray-600 dark:text-gray-400">Session Quality:</span>
          <span class="font-medium" :class="getQualityScoreClasses(sessionQualityScore)">
            {{ Math.round(sessionQualityScore) }}%
          </span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600 dark:text-gray-400">Drift Assessment:</span>
          <div class="flex items-center gap-1">
            <i :class="driftAnalysis.icon"></i>
            <span class="font-medium" :class="driftAnalysis.colorClass">{{ driftAnalysis.text }}</span>
          </div>
        </div>
      </div>
      
      <!-- Navigation Options -->
      <div class="space-y-3">
        <button @click="navigateToArrow" 
                class="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center">
          <i class="fas fa-arrow-left mr-2"></i>
          Return to Arrow Setup
        </button>
        
        <button @click="navigateToJournal" 
                class="w-full px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium rounded-lg transition-colors flex items-center justify-center">
          <i class="fas fa-book mr-2"></i>
          View in Journal
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import { useJournalApi } from '~/composables/useJournalApi'
import TuningSessionHeader from '~/components/TuningSessionHeader.vue'

// Set page title and meta
useHead({
  title: 'Walkback Tuning Session',
  meta: [
    { name: 'description', content: 'Interactive walkback tuning session with multi-distance analysis and drift detection.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})

// Route, Router, and API
const route = useRoute()
const router = useRouter()
const api = useApi()
const { createEntry } = useJournalApi()

// Reactive data
const sessionData = ref(null)
const completedTests = ref([])
const loading = ref(true)
const error = ref(null)

// Test recording state
const recordingTest = ref(false)
const completingSession = ref(false)
const showCompletionModal = ref(false)

// Walkback specific state
const plannedDistances = ref([20, 30, 40, 50, 60]) // Default distances in meters
const currentDistance = ref(20)
const completedDistances = ref([])
const currentDistanceImpacts = ref([])

// Test parameters
const groupConsistency = ref('good')
const testNotes = ref('')
const completionNotes = ref('')
const targetCanvas = ref(null)

// Computed properties for walkback analysis
const calculatedOffset = computed(() => {
  if (currentDistanceImpacts.value.length === 0) return '0.0'
  
  // Calculate average horizontal offset from center line
  const targetCenter = targetCanvas.value ? targetCanvas.value.offsetWidth / 2 : 200
  const avgX = currentDistanceImpacts.value.reduce((sum, impact) => sum + impact.x, 0) / currentDistanceImpacts.value.length
  const offsetPixels = avgX - targetCenter
  
  // Convert pixels to cm (approximate conversion based on target size)
  const pixelToCm = 20 / (targetCanvas.value ? targetCanvas.value.offsetWidth / 2 : 200) // 20cm radius for target
  const offsetCm = offsetPixels * pixelToCm
  
  return offsetCm.toFixed(1)
})

const calculatedSlope = computed(() => {
  if (completedTests.value.length < 2) return 0
  
  // Linear regression to calculate slope (cm/m)
  const tests = completedTests.value
  const n = tests.length
  
  const sumX = tests.reduce((sum, test) => sum + test.test_data.distance_m, 0)
  const sumY = tests.reduce((sum, test) => sum + test.test_data.horizontal_offset_cm, 0)
  const sumXY = tests.reduce((sum, test) => sum + (test.test_data.distance_m * test.test_data.horizontal_offset_cm), 0)
  const sumX2 = tests.reduce((sum, test) => sum + (test.test_data.distance_m * test.test_data.distance_m), 0)
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
  return slope || 0
})

const driftAnalysis = computed(() => {
  const slope = calculatedSlope.value
  const absSlope = Math.abs(slope)
  
  if (absSlope < 0.05) {
    return { 
      icon: 'fas fa-check-circle text-green-500', 
      text: 'Excellent Tune', 
      direction: '',
      colorClass: 'text-green-600' 
    }
  } else if (absSlope < 0.1) {
    return { 
      icon: 'fas fa-info-circle text-blue-500', 
      text: 'Minor Drift', 
      direction: slope > 0 ? 'right' : 'left',
      colorClass: 'text-blue-600' 
    }
  } else if (absSlope < 0.2) {
    return { 
      icon: 'fas fa-exclamation-triangle text-yellow-500', 
      text: 'Moderate Drift', 
      direction: slope > 0 ? 'right' : 'left',
      colorClass: 'text-yellow-600' 
    }
  } else {
    return { 
      icon: 'fas fa-times-circle text-red-500', 
      text: 'Significant Drift', 
      direction: slope > 0 ? 'right' : 'left',
      colorClass: 'text-red-600' 
    }
  }
})

const tuningRecommendations = computed(() => {
  const slope = calculatedSlope.value
  const absSlope = Math.abs(slope)
  
  if (absSlope < 0.05) return [] // No adjustments needed
  
  const bowType = sessionData.value?.bow_setup?.bow_type || 'compound'
  const recommendations = []
  
  if (slope > 0) { // Drifting right
    if (bowType === 'compound') {
      recommendations.push({
        title: 'Move Rest LEFT',
        instruction: `Move your arrow rest LEFT by ${Math.min(0.4, absSlope * 2).toFixed(1)}-${Math.min(0.6, absSlope * 3).toFixed(1)}mm`,
        warning: 'Make small adjustments and retest. Large changes can overcorrect.'
      })
    } else {
      recommendations.push({
        title: 'Reduce Plunger Tension',
        instruction: `Reduce plunger tension by ${Math.ceil(absSlope * 4)}/8 turn, or move rest IN 0.5mm`,
        warning: 'If no plunger, adjust arrow rest position instead.'
      })
    }
  } else { // Drifting left
    if (bowType === 'compound') {
      recommendations.push({
        title: 'Move Rest RIGHT',
        instruction: `Move your arrow rest RIGHT by ${Math.min(0.4, absSlope * 2).toFixed(1)}-${Math.min(0.6, absSlope * 3).toFixed(1)}mm`,
        warning: 'Make small adjustments and retest. Large changes can overcorrect.'
      })
    } else {
      recommendations.push({
        title: 'Increase Plunger Tension',
        instruction: `Increase plunger tension by ${Math.ceil(absSlope * 4)}/8 turn, or move rest OUT 0.5mm`,
        warning: 'If no plunger, adjust arrow rest position instead.'
      })
    }
  }
  
  if (absSlope > 0.15) {
    recommendations.push({
      title: 'Verify Arrow Spine',
      instruction: 'Large drift may indicate arrow spine mismatch. Consider spine testing.',
      warning: 'Ensure arrows match your bow\'s specifications before making major rest adjustments.'
    })
  }
  
  return recommendations
})

const minDistance = computed(() => Math.min(...completedTests.value.map(t => t.test_data.distance_m)))
const maxDistance = computed(() => Math.max(...completedTests.value.map(t => t.test_data.distance_m)))

// Progress tracking functions similar to bareshaft
const sessionQualityScore = computed(() => {
  if (completedTests.value.length === 0) return 0
  
  const totalScore = completedTests.value.reduce((sum, test) => {
    return sum + (test.confidence_score || 0)
  }, 0)
  
  return totalScore / completedTests.value.length
})

const progressPercentage = computed(() => {
  const minimumTests = 3
  const current = completedTests.value.length
  const percentage = Math.min((current / minimumTests) * 100, 100)
  return percentage
})

const progressBarGradient = computed(() => {
  const quality = sessionQualityScore.value
  if (quality >= 85) return 'from-green-400 to-green-600'
  if (quality >= 70) return 'from-blue-400 to-blue-600'
  if (quality >= 55) return 'from-yellow-400 to-yellow-600'
  return 'from-red-400 to-red-600'
})

// Helper functions
const getQualityScoreClasses = (score) => {
  if (score >= 85) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  if (score >= 70) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  if (score >= 55) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
}

const getDistanceStatusClass = (distance) => {
  if (completedDistances.value.includes(distance)) {
    const testData = getDistanceTestData(distance)
    return getTestQualityDotClass(testData?.confidence_score || 0)
  } else if (distance === currentDistance.value) {
    return 'bg-blue-500 animate-pulse'
  } else {
    return 'bg-gray-300 dark:bg-gray-600'
  }
}

const getDistanceQualityRingClass = (score) => {
  if (score >= 85) return 'border-green-300 dark:border-green-600'
  if (score >= 70) return 'border-blue-300 dark:border-blue-600'
  if (score >= 55) return 'border-yellow-300 dark:border-yellow-600'
  return 'border-red-300 dark:border-red-600'
}

const getTestQualityDotClass = (score) => {
  if (score >= 85) return 'bg-green-500'
  if (score >= 70) return 'bg-blue-500'
  if (score >= 55) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getDistanceTestData = (distance) => {
  return completedTests.value.find(test => test.test_data.distance_m === distance)
}

const getDistanceInstructions = (distance) => {
  if (distance === 20) {
    return 'Start at 20m. Sight in using your 20m pin to hit the center aiming point.'
  } else {
    return `Use the same 20m pin. Don't adjust your sight - look for horizontal drift from the vertical line.`
  }
}

const getSightPin = () => {
  return completedDistances.value.length === 0 ? '20m' : '20m (same pin)'
}

const formatOffset = (offsetCm) => {
  const abs = Math.abs(offsetCm)
  const direction = offsetCm > 0 ? 'R' : 'L'
  return `${abs.toFixed(1)}cm ${direction}`
}

const formatDriftRate = (slope) => {
  return Math.abs(slope).toFixed(2)
}

const getPlotPosition = (test) => {
  const containerWidth = 280 // Approximate chart width
  const containerHeight = 120
  
  const distanceRange = maxDistance.value - minDistance.value
  const xPercent = distanceRange > 0 ? (test.test_data.distance_m - minDistance.value) / distanceRange : 0
  
  // For Y position, center is middle, positive offset goes down
  const maxOffset = Math.max(...completedTests.value.map(t => Math.abs(t.test_data.horizontal_offset_cm)))
  const yPercent = maxOffset > 0 ? (test.test_data.horizontal_offset_cm / maxOffset * 0.4) + 0.5 : 0.5
  
  return {
    left: (xPercent * (containerWidth - 20) + 10) + 'px',
    top: (yPercent * (containerHeight - 20) + 10) + 'px'
  }
}

// Event handlers
const recordArrowImpact = (event) => {
  if (!targetCanvas.value) return
  
  const rect = targetCanvas.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  currentDistanceImpacts.value.push({ x, y })
}

const clearCurrentImpacts = () => {
  currentDistanceImpacts.value = []
}

const skipDistance = () => {
  moveToNextDistance()
}

const moveToNextDistance = () => {
  const currentIndex = plannedDistances.value.indexOf(currentDistance.value)
  if (currentIndex < plannedDistances.value.length - 1) {
    currentDistance.value = plannedDistances.value[currentIndex + 1]
  }
  clearCurrentImpacts()
}

const recordDistanceTest = async () => {
  if (currentDistanceImpacts.value.length === 0) return
  
  try {
    recordingTest.value = true
    
    const testData = {
      test_type: 'walkback_tuning',
      test_data: {
        distance_m: currentDistance.value,
        horizontal_offset_cm: parseFloat(calculatedOffset.value),
        group_consistency: groupConsistency.value,
        impact_count: currentDistanceImpacts.value.length,
        impacts: currentDistanceImpacts.value
      },
      notes: testNotes.value.trim() || null,
      confidence_score: calculateConfidenceScore(),
      timestamp: new Date().toISOString()
    }
    
    console.log('Recording walkback test:', testData)
    
    const sessionId = route.params.sessionId
    const response = await api.post(`/tuning-guides/sessions/${sessionId}/test`, testData)
    
    // Add to completed tests
    const testRecord = {
      id: Date.now(),
      test_type: 'walkback_tuning',
      timestamp: testData.timestamp,
      test_data: testData.test_data,
      notes: testData.notes,
      confidence_score: testData.confidence_score,
      recommendations: response.recommendations || [],
      analysis: response.analysis || null
    }
    completedTests.value.push(testRecord)
    completedDistances.value.push(currentDistance.value)
    
    // Move to next distance
    moveToNextDistance()
    testNotes.value = ''
    
  } catch (error) {
    console.error('Error recording test:', error)
    alert('Failed to record test. Please try again.')
  } finally {
    recordingTest.value = false
  }
}

const calculateConfidenceScore = () => {
  let score = 70 // Base score
  
  // Adjust for group consistency
  const consistencyBonus = {
    'excellent': 20,
    'good': 15,
    'fair': 10,
    'poor': 0
  }
  score += consistencyBonus[groupConsistency.value] || 0
  
  // Adjust for number of arrows
  if (currentDistanceImpacts.value.length >= 5) {
    score += 10 // More arrows = higher confidence
  }
  
  return Math.min(95, Math.max(50, score))
}

const completeSession = async () => {
  try {
    completingSession.value = true
    
    const sessionId = route.params.sessionId
    
    // Prepare session completion data with enhanced walkback data
    const completionData = {
      completion_notes: completionNotes.value.trim() || null,
      total_tests: completedTests.value.length,
      skip_journal_creation: true, // Skip old journal creation, use new method instead
      session_data: {
        tuning_type: 'walkback',
        test_results: completedTests.value.map(test => ({
          distance_m: test.test_data?.distance_m,
          horizontal_offset_cm: test.test_data?.horizontal_offset_cm,
          confidence_score: test.confidence_score,
          notes: test.notes,
          timestamp: test.timestamp
        })),
        drift_analysis: {
          slope: calculatedSlope.value,
          drift_direction: driftAnalysis.value.direction,
          quality_assessment: driftAnalysis.value.text,
          drift_rate_cm_per_m: Math.abs(calculatedSlope.value).toFixed(2)
        },
        final_recommendations: tuningRecommendations.value || [],
        session_quality: sessionQualityScore.value,
        distances_tested: completedDistances.value
      }
    }
    
    const response = await api.post(`/tuning-guides/sessions/${sessionId}/complete`, completionData)
    
    // Auto-create journal entry for this tuning session
    await createJournalEntryForSession(completionData)
    
    // Show completion notification with return options
    showCompletionSuccessModal.value = true
    
  } catch (error) {
    console.error('Error completing session:', error)
    alert('Failed to complete session. Please try again.')
  } finally {
    completingSession.value = false
  }
}

// Auto-create journal entry for completed walkback tuning session
const createJournalEntryForSession = async (completionData) => {
  try {
    const sessionId = route.params.sessionId
    const sessionType = 'Walkback Tuning'
    
    // Generate meaningful title based on session results
    const testsCount = completionData.total_tests || 0
    const qualityScore = Math.round(completionData.session_data?.session_quality || 0)
    const driftRate = completionData.session_data?.drift_analysis?.drift_rate_cm_per_m || '0.0'
    const driftDirection = completionData.session_data?.drift_analysis?.drift_direction || 'None'
    
    // Get arrow name for better title
    const arrowName = sessionData.value?.arrow ? 
      `${sessionData.value.arrow.manufacturer} ${sessionData.value.arrow.model_name}` : 
      `Arrow ${sessionData.value?.arrow_id || 'Unknown'}`
    
    const title = `${sessionType} Session - ${arrowName}`
    
    // Format dates properly
    const sessionDate = new Date().toLocaleDateString()
    const sessionTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    const sessionDuration = sessionData.value?.started_at ? 
      formatSessionDuration(sessionData.value.started_at, new Date().toISOString()) : 
      'Unknown'
    
    // Create structured content with better formatting
    let content = `# ${sessionType} Session - ${arrowName}\n\n`
    
    content += `## Session Details\n`
    content += `- **Arrow**: ${arrowName}\n`
    content += `- **Bow Setup**: ${sessionData.value?.bow_setup?.name || 'Unknown'}\n`
    content += `- **Arrow Length**: ${sessionData.value?.arrow_length || 'Not specified'} inches\n`
    content += `- **Point Weight**: ${sessionData.value?.point_weight || 'Not specified'} grains\n`
    content += `- **Date**: ${sessionDate}\n`
    content += `- **Time**: ${sessionTime}\n`
    content += `- **Session Duration**: ${sessionDuration}\n`
    content += `- **Session Quality**: ${qualityScore}%\n\n`
    
    // Add drift analysis first (most important for walkback)
    if (completionData.session_data?.drift_analysis) {
      const analysis = completionData.session_data.drift_analysis
      content += `## Drift Analysis Results\n`
      content += `- **Overall Assessment**: ${analysis.quality_assessment}\n`
      content += `- **Drift Rate**: ${analysis.drift_rate_cm_per_m} cm/m\n`
      content += `- **Drift Direction**: ${analysis.drift_direction}\n`
      content += `- **Calculated Slope**: ${analysis.slope?.toFixed(4) || 'N/A'}\n\n`
    }
    
    // Add test results in detailed format
    if (completionData.session_data?.test_results?.length > 0) {
      content += `## Distance Test Results\n`
      content += `**${testsCount} distance tests completed**\n\n`
      
      // Sort test results by distance for better readability
      const sortedTests = [...completionData.session_data.test_results].sort((a, b) => a.distance_m - b.distance_m)
      
      sortedTests.forEach((test, index) => {
        const offset = test.horizontal_offset_cm >= 0 ? `+${test.horizontal_offset_cm}` : `${test.horizontal_offset_cm}`
        content += `### ${test.distance_m}m Distance Test\n`
        content += `- **Horizontal Offset**: ${offset}cm\n`
        content += `- **Confidence Score**: ${Math.round(test.confidence_score)}%\n`
        if (test.notes) {
          content += `- **Notes**: ${test.notes}\n`
        }
        content += `- **Time**: ${new Date(test.timestamp).toLocaleTimeString()}\n\n`
      })
    }
    
    // Add recommendations if available  
    if (completionData.session_data?.final_recommendations?.length > 0) {
      content += `## Tuning Recommendations\n`
      completionData.session_data.final_recommendations.forEach((rec, index) => {
        content += `${index + 1}. **${rec.title}**\n`
        content += `   ${rec.instruction}\n\n`
      })
    }
    
    // Add session notes
    if (completionData.completion_notes) {
      content += `## Session Notes\n${completionData.completion_notes}\n\n`
    }
    
    content += `---\n`
    content += `*Session completed successfully with ${qualityScore}% quality score and ${driftRate} cm/m drift rate*`
    
    // Prepare journal entry data
    const entryData = {
      title,
      content,
      entry_type: 'tuning_session', // Use generic tuning_session for modal detection
      bow_setup_id: sessionData.value?.bow_setup_id || null,
      linked_arrow: sessionData.value?.arrow_id || null, // Link to arrow for proper filtering
      tags: ['tuning', 'walkback', 'session', sessionData.value?.arrow?.material?.toLowerCase() || 'arrow'].filter(Boolean),
      is_private: false,
      session_type: 'walkback', // Specific session type for filtering
      session_quality_score: qualityScore, // For quality-based filtering
      session_metadata: { // Use session_metadata instead of session_data
        tuning_type: 'walkback', // Essential for modal display
        session_quality: qualityScore,
        test_results: completionData.session_data?.test_results || [],
        drift_analysis: completionData.session_data?.drift_analysis || {},
        final_recommendations: completionData.session_data?.final_recommendations || [],
        // Add additional context for the detail viewer
        arrow_info: sessionData.value?.arrow || {},
        bow_info: sessionData.value?.bow_setup || {},
        session_details: {
          arrow_length: sessionData.value?.arrow_length,
          point_weight: sessionData.value?.point_weight,
          started_at: sessionData.value?.started_at,
          completed_at: new Date().toISOString(),
          session_duration: sessionDuration
        },
        session_id: sessionId
      }
    }
    
    // Create the journal entry
    const result = await createEntry(entryData)
    
    if (result.success) {
      console.log('Journal entry created successfully for walkback tuning session:', result.data.id)
    } else {
      console.error('Failed to create journal entry:', result.error)
    }
    
  } catch (error) {
    console.error('Error creating journal entry for walkback session:', error)
    // Don't throw error to avoid disrupting the session completion flow
  }
}

// Helper function to format session duration
const formatSessionDuration = (startTime, endTime) => {
  try {
    const start = new Date(startTime)
    const end = new Date(endTime)
    const durationMs = end - start
    const minutes = Math.floor(durationMs / (1000 * 60))
    const hours = Math.floor(minutes / 60)
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`
    } else {
      return `${minutes}m`
    }
  } catch (error) {
    return 'Unknown'
  }
}

// Add navigation handlers
const navigateToArrow = async () => {
  try {
    // First check if we already have setup_arrow_id in session data
    if (sessionData.value?.setup_arrow_id) {
      router.push(`/setup-arrows/${sessionData.value.setup_arrow_id}`)
      return
    }
    
    // If not, we need to find it using bow_setup_id and arrow_id
    if (sessionData.value?.bow_setup_id && sessionData.value?.arrow_id) {
      const setupArrowId = await findSetupArrowId(sessionData.value.bow_setup_id, sessionData.value.arrow_id)
      if (setupArrowId) {
        router.push(`/setup-arrows/${setupArrowId}`)
        return
      }
    }
    
    // Fallback to general setup page
    router.push('/my-setup')
  } catch (error) {
    console.error('Error navigating to arrow setup:', error)
    router.push('/my-setup')
  }
}

// Helper function to find setup_arrow_id from bow_setup_id and arrow_id
const findSetupArrowId = async (bowSetupId, arrowId) => {
  try {
    const response = await api.get('/my-setups')
    const bowSetups = response.setups || []
    
    // Find the bow setup
    const bowSetup = bowSetups.find(setup => setup.id === bowSetupId)
    if (!bowSetup || !bowSetup.arrows) {
      return null
    }
    
    // Find the arrow in this bow setup
    const setupArrow = bowSetup.arrows.find(arrow => arrow.arrow_id === arrowId)
    return setupArrow ? setupArrow.id : null
    
  } catch (error) {
    console.error('Error finding setup arrow ID:', error)
    return null
  }
}

const navigateToJournal = () => {
  router.push('/journal')
}

const showCompletionSuccessModal = ref(false)

const handlePause = () => {
  console.log('Pause/Resume session')
}

const handleAbandon = async () => {
  if (confirm('Are you sure you want to abandon this walkback tuning session? All progress will be lost.')) {
    router.go(-1)
  }
}

const handleSaveExit = () => {
  if (completedTests.value.length >= 3) {
    completeSession()
  } else {
    alert('Complete at least 3 distance tests before saving the session.')
  }
}

// Data loading
const loadSessionData = async () => {
  try {
    loading.value = true
    const sessionId = route.params.sessionId
    const response = await api.get(`/tuning-guides/${sessionId}`)
    sessionData.value = response
    
    if (response.tests && response.tests.length > 0) {
      completedTests.value = response.tests
      completedDistances.value = response.tests.map(test => test.test_data.distance_m)
      
      // Set current distance to next untested distance
      const nextDistance = plannedDistances.value.find(d => !completedDistances.value.includes(d))
      if (nextDistance) {
        currentDistance.value = nextDistance
      }
    }
  } catch (error) {
    console.error('Error loading session:', error)
    error.value = 'Failed to load session data'
  } finally {
    loading.value = false
  }
}

// Load data on mount
onMounted(() => {
  loadSessionData()
})
</script>