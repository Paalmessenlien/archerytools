<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="container mx-auto px-4 py-8">
      <div class="animate-pulse">
        <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-96 mb-6"></div>
        <div class="h-64 bg-gray-200 dark:bg-gray-700 rounded mb-6"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="container mx-auto px-4 py-8">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <i class="fas fa-exclamation-triangle text-4xl text-red-600 dark:text-red-400 mb-4"></i>
        <h2 class="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">Session Not Found</h2>
        <p class="text-red-600 dark:text-red-400 mb-4">{{ error }}</p>
        <div class="flex justify-center space-x-3">
          <button
            @click="$router.go(-1)"
            class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            Go Back
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="sessionData" class="container mx-auto px-4 py-6 max-w-6xl">
      <!-- Header -->
      <TuningSessionHeader
        :session-id="route.params.sessionId"
        session-type="bareshaft"
        :arrow-info="sessionData ? `${sessionData.arrow?.manufacturer} ${sessionData.arrow?.model_name}` : 'Loading...'"
        :bow-setup-name="sessionData?.bow_setup?.name || 'Loading...'"
        session-status="active"
        :tests-completed="completedTests.length"
        :total-tests="10"
        :start-time="sessionData?.started_at ? new Date(sessionData.started_at) : new Date()"
        :can-save="completedTests.length > 0"
        show-progress
        @pause-resume="handlePause"
        @abandon-session="handleAbandon"
        @save-exit="handleSaveExit"
      />

      <!-- Progress Section -->
      <div class="mb-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Session Progress</h3>
            <div class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
              <span>{{ completedTests.length }} tests completed</span>
              <span v-if="sessionQualityScore > 0" class="px-2 py-1 rounded-full text-xs font-medium"
                    :class="getQualityScoreClasses(sessionQualityScore)">
                {{ Math.round(sessionQualityScore) }}% quality
              </span>
            </div>
          </div>
          
          <!-- Enhanced Progress Visualization -->
          <div class="space-y-4">
            <!-- Progress Dots with Quality Rings -->
            <div class="flex items-center space-x-2">
              <div 
                v-for="(test, index) in Math.max(completedTests.length + 1, 6)" 
                :key="index"
                class="relative flex-shrink-0"
              >
                <!-- Outer quality ring -->
                <div v-if="index < completedTests.length && completedTests[index]" 
                     class="absolute inset-0 w-4 h-4 rounded-full border-2 -m-0.5"
                     :class="getTestQualityRingClass(completedTests[index].confidence_score)">
                </div>
                <!-- Main progress dot -->
                <div class="w-3 h-3 rounded-full relative z-10"
                     :class="index < completedTests.length 
                       ? getTestQualityDotClass(completedTests[index]?.confidence_score || 0)
                       : index === completedTests.length 
                         ? 'bg-blue-500 animate-pulse' 
                         : 'bg-gray-300 dark:bg-gray-600'">
                </div>
              </div>
              <span v-if="completedTests.length >= 3" class="text-sm text-gray-600 dark:text-gray-400 ml-2">
                <i class="fas fa-check-circle text-green-500 mr-1"></i>
                Ready to complete session
              </span>
            </div>

            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div class="h-2 rounded-full transition-all duration-500 bg-gradient-to-r"
                   :class="progressBarGradient"
                   :style="{ width: `${progressPercentage}%` }">
              </div>
            </div>

            <!-- Pattern Distribution Summary -->
            <div v-if="completedTests.length > 0" class="grid grid-cols-2 gap-3 text-xs">
              <!-- Most Common Pattern -->
              <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                <span class="text-gray-600 dark:text-gray-400">Most Common:</span>
                <div class="flex items-center gap-1">
                  <span v-html="mostCommonPattern.icon"></span>
                  <span class="font-medium">{{ mostCommonPattern.name }}</span>
                </div>
              </div>
              <!-- Improvement Trend -->
              <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                <span class="text-gray-600 dark:text-gray-400">Trend:</span>
                <div class="flex items-center gap-1">
                  <i :class="improvementTrend.icon"></i>
                  <span class="font-medium" :class="improvementTrend.colorClass">
                    {{ improvementTrend.text }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Current Test Section (Left Column) -->
        <div class="space-y-6">
          <!-- Progressive Step-by-Step Instructions -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div class="flex items-start justify-between mb-3">
              <h3 class="text-lg font-medium text-blue-900 dark:text-blue-100">
                <i class="fas fa-crosshairs mr-2"></i>
                Bareshaft Test #{{ completedTests.length + 1 }}
              </h3>
              <div class="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-800 rounded-full text-blue-700 dark:text-blue-200">
                Step {{ currentStep }}/4
              </div>
            </div>

            <!-- Progressive Steps -->
            <div class="space-y-3">
              <!-- Step 1: Setup -->
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                     :class="currentStep >= 1 ? 'bg-blue-500 text-white' : 'bg-gray-300 dark:bg-gray-600 text-gray-500'">
                  1
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-gray-100" 
                       :class="currentStep === 1 ? 'text-blue-600 dark:text-blue-400' : ''">
                    Setup Your Position
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    <span v-if="currentStep === 1" class="text-blue-600 dark:text-blue-400 font-medium">▶</span>
                    Prepare {{ testDistance }}m distance. Ensure your bow is properly sighted with fletched arrows first.
                  </div>
                </div>
                <div v-if="currentStep === 1" class="flex-shrink-0">
                  <button @click="nextStep" class="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors">
                    Ready
                  </button>
                </div>
              </div>

              <!-- Step 2: Shoot Fletched Group -->
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                     :class="currentStep >= 2 ? 'bg-blue-500 text-white' : 'bg-gray-300 dark:bg-gray-600 text-gray-500'">
                  2
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-gray-100"
                       :class="currentStep === 2 ? 'text-blue-600 dark:text-blue-400' : ''">
                    Shoot Fletched Control Group
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    <span v-if="currentStep === 2" class="text-blue-600 dark:text-blue-400 font-medium">▶</span>
                    Shoot 3-6 fletched arrows at your aiming point. Note where they impact and group quality.
                  </div>
                </div>
                <div v-if="currentStep === 2" class="flex-shrink-0">
                  <button @click="nextStep" class="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors">
                    Done
                  </button>
                </div>
              </div>

              <!-- Step 3: Shoot Bareshaft Group -->
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                     :class="currentStep >= 3 ? 'bg-blue-500 text-white' : 'bg-gray-300 dark:bg-gray-600 text-gray-500'">
                  3
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-gray-100"
                       :class="currentStep === 3 ? 'text-blue-600 dark:text-blue-400' : ''">
                    Shoot Bareshaft Group
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    <span v-if="currentStep === 3" class="text-blue-600 dark:text-blue-400 font-medium">▶</span>
                    From the same position, shoot 3-6 bareshaft arrows (no fletching) at the same aiming point.
                  </div>
                </div>
                <div v-if="currentStep === 3" class="flex-shrink-0">
                  <button @click="nextStep" class="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors">
                    Done
                  </button>
                </div>
              </div>

              <!-- Step 4: Record Pattern -->
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                     :class="currentStep >= 4 ? 'bg-blue-500 text-white' : 'bg-gray-300 dark:bg-gray-600 text-gray-500'">
                  4
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-gray-100"
                       :class="currentStep === 4 ? 'text-blue-600 dark:text-blue-400' : ''">
                    Analyze & Record Impact Pattern
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    <span v-if="currentStep === 4" class="text-blue-600 dark:text-blue-400 font-medium">▶</span>
                    Compare bareshaft group to fletched group and select the matching pattern below.
                  </div>
                </div>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="mt-4">
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                <div class="bg-blue-500 h-1.5 rounded-full transition-all duration-300" 
                     :style="{ width: `${(currentStep / 4) * 100}%` }"></div>
              </div>
            </div>
          </div>

          <!-- Shooting Distance Selection -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              Test Settings
            </h4>
            
            <div class="space-y-4">
              <!-- Distance Selector -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Shooting Distance
                </label>
                <select 
                  v-model="testDistance" 
                  class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                >
                  <option value="10">10 yards</option>
                  <option value="15">15 yards</option>
                  <option value="20">20 yards</option>
                  <option value="30">30 yards</option>
                </select>
              </div>

              <!-- Group Consistency -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Group Consistency
                </label>
                <select 
                  v-model="groupConsistency" 
                  class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                >
                  <option value="excellent">Excellent (tight groups)</option>
                  <option value="good">Good (consistent groups)</option>
                  <option value="fair">Fair (some scatter)</option>
                  <option value="poor">Poor (inconsistent)</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Bareshaft Impact Pattern Selection -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-crosshairs mr-2 text-blue-500"></i>
                Bareshaft Impact Pattern
              </h4>
              <button 
                @click="showPatternGuide = !showPatternGuide"
                class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Show Pattern Guide"
              >
                <i class="fas fa-question-circle text-gray-500 dark:text-gray-400"></i>
              </button>
            </div>

            <!-- Pattern Guide Modal -->
            <div v-if="showPatternGuide" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div class="p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Reading Bareshaft Impact Patterns</h3>
                    <button @click="showPatternGuide = false" class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                      <i class="fas fa-times text-gray-500"></i>
                    </button>
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 space-y-3">
                    <p><strong>Step 1:</strong> Shoot 3-6 fletched arrows at your chosen distance</p>
                    <p><strong>Step 2:</strong> From the same position, shoot 3-6 bareshaft arrows (no fletching)</p>
                    <p><strong>Step 3:</strong> Compare where the bareshaft group hits relative to your fletched group</p>
                    <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                      <p class="font-medium text-blue-900 dark:text-blue-100">Key Principle:</p>
                      <p>The bareshaft impact pattern reveals spine and tuning issues that fletching normally corrects. Select the pattern that best matches where your bareshafts hit compared to your fletched arrows.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Instructions -->
            <div class="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p class="text-sm text-blue-800 dark:text-blue-200">
                <i class="fas fa-info-circle mr-1"></i>
                Compare where your <strong>bareshaft group</strong> hits relative to your <strong>fletched group</strong>. Select the pattern below that best matches your observation.
              </p>
            </div>

            <!-- Impact Pattern Grid -->
            <div class="grid grid-cols-3 gap-2 mb-4">
              <!-- Top Row -->
              <div 
                v-for="pattern in impactPatterns.slice(0, 3)" 
                :key="pattern.id"
                @click="selectImpactPattern(pattern)"
                class="relative group cursor-pointer border-2 rounded-lg p-3 text-center transition-all duration-200 hover:shadow-md"
                :class="selectedImpactPattern?.id === pattern.id 
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30' 
                  : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500'"
              >
                <div class="text-2xl mb-1" v-html="pattern.icon"></div>
                <div class="text-xs font-medium text-gray-900 dark:text-gray-100">{{ pattern.displayName }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">{{ pattern.shortDesc }}</div>
                
                <!-- Tooltip -->
                <div class="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap pointer-events-none">
                  {{ pattern.description }}
                </div>
              </div>

              <!-- Middle Row -->
              <div 
                v-for="pattern in impactPatterns.slice(3, 6)" 
                :key="pattern.id"
                @click="selectImpactPattern(pattern)"
                class="relative group cursor-pointer border-2 rounded-lg p-3 text-center transition-all duration-200 hover:shadow-md"
                :class="selectedImpactPattern?.id === pattern.id 
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30' 
                  : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500'"
              >
                <div class="text-2xl mb-1" v-html="pattern.icon"></div>
                <div class="text-xs font-medium text-gray-900 dark:text-gray-100">{{ pattern.displayName }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">{{ pattern.shortDesc }}</div>
                
                <!-- Tooltip -->
                <div class="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap pointer-events-none">
                  {{ pattern.description }}
                </div>
              </div>

              <!-- Bottom Row -->
              <div 
                v-for="pattern in impactPatterns.slice(6, 9)" 
                :key="pattern.id"
                @click="selectImpactPattern(pattern)"
                class="relative group cursor-pointer border-2 rounded-lg p-3 text-center transition-all duration-200 hover:shadow-md"
                :class="selectedImpactPattern?.id === pattern.id 
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30' 
                  : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500'"
              >
                <div class="text-2xl mb-1" v-html="pattern.icon"></div>
                <div class="text-xs font-medium text-gray-900 dark:text-gray-100">{{ pattern.displayName }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">{{ pattern.shortDesc }}</div>
                
                <!-- Tooltip -->
                <div class="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap pointer-events-none">
                  {{ pattern.description }}
                </div>
              </div>
            </div>

            <!-- Selected Pattern Details -->
            <div v-if="selectedImpactPattern" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div class="flex items-start space-x-3">
                <div class="text-3xl" v-html="selectedImpactPattern.icon"></div>
                <div class="flex-1">
                  <h5 class="font-medium text-gray-900 dark:text-gray-100">{{ selectedImpactPattern.displayName }}</h5>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">{{ selectedImpactPattern.description }}</p>
                  <div class="text-xs text-blue-600 dark:text-blue-400 font-medium">
                    {{ selectedImpactPattern.spineDiagnosis }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bow Type Specific Recommendations -->
          <div v-if="selectedImpactPattern && selectedImpactPattern.id !== 'perfect'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-tools mr-2 text-orange-500"></i>
                Recommended Adjustments
              </h4>
              <div class="text-xs px-2 py-1 bg-orange-100 dark:bg-orange-900/30 rounded-full text-orange-700 dark:text-orange-300">
                {{ getRecommendationPriority(selectedImpactPattern.id) }}
              </div>
            </div>

            <!-- Bow Type Selector -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Your Bow Type for Specific Instructions
              </label>
              <select v-model="selectedBowType" class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100">
                <option value="compound">Compound Bow</option>
                <option value="recurve">Olympic Recurve</option>
                <option value="traditional">Traditional Bow</option>
                <option value="barebow">Barebow Recurve</option>
              </select>
            </div>

            <!-- Bow-Specific Recommendations -->
            <div v-if="selectedBowType" class="space-y-4">
              <div class="bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                <h5 class="font-medium text-orange-900 dark:text-orange-100 mb-3">
                  <i class="fas fa-arrow-right mr-1"></i>
                  {{ getBowTypeDisplayName(selectedBowType) }} Adjustments
                </h5>
                
                <!-- Adjustment Steps -->
                <div class="space-y-3">
                  <div v-for="(adjustment, index) in getBowSpecificAdjustments(selectedImpactPattern.id, selectedBowType)" :key="index" class="flex items-start space-x-3">
                    <div class="flex-shrink-0 w-6 h-6 rounded-full bg-orange-500 text-white flex items-center justify-center text-xs font-bold">
                      {{ index + 1 }}
                    </div>
                    <div class="flex-1">
                      <div class="font-medium text-gray-900 dark:text-gray-100 text-sm">
                        {{ adjustment.title }}
                      </div>
                      <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {{ adjustment.instruction }}
                      </div>
                      <div v-if="adjustment.warning" class="text-xs text-red-600 dark:text-red-400 mt-1 italic">
                        ⚠️ {{ adjustment.warning }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Testing Reminder -->
                <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                  <div class="flex items-start space-x-2">
                    <i class="fas fa-info-circle text-blue-600 dark:text-blue-400 text-sm mt-0.5"></i>
                    <div class="text-xs text-blue-800 dark:text-blue-200">
                      <strong>Important:</strong> Make small adjustments (listed increments) and test after each change. 
                      Record each test to track your progress toward the center.
                    </div>
                  </div>
                </div>
              </div>

              <!-- Alternative Solutions -->
              <div v-if="getAlternativeSolutions(selectedImpactPattern.id, selectedBowType).length > 0" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h6 class="font-medium text-gray-900 dark:text-gray-100 mb-2 text-sm">
                  <i class="fas fa-lightbulb mr-1 text-yellow-500"></i>
                  If Initial Adjustments Don't Work:
                </h6>
                <ul class="space-y-1">
                  <li v-for="solution in getAlternativeSolutions(selectedImpactPattern.id, selectedBowType)" :key="solution" class="text-xs text-gray-600 dark:text-gray-400 flex items-start space-x-1">
                    <span class="text-yellow-500 mt-0.5">•</span>
                    <span>{{ solution }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Perfect Tune Celebration -->
          <div v-else-if="selectedImpactPattern && selectedImpactPattern.id === 'perfect'" class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <div class="text-center">
              <div class="text-4xl mb-2">🎯</div>
              <h4 class="text-lg font-bold text-green-900 dark:text-green-100 mb-2">
                Excellent Bareshaft Tune!
              </h4>
              <p class="text-sm text-green-800 dark:text-green-200 mb-4">
                Your bareshafts are grouping with your fletched arrows. This indicates excellent bow setup and arrow spine matching.
              </p>
              <div class="bg-green-100 dark:bg-green-900/30 rounded-lg p-3">
                <h5 class="font-medium text-green-900 dark:text-green-100 mb-2">Next Steps:</h5>
                <ul class="text-xs text-green-800 dark:text-green-200 space-y-1 text-left">
                  <li>• Test at longer distances to verify tune consistency</li>
                  <li>• If hunting, test broadheads - they should group with field points</li>
                  <li>• Record multiple perfect tests to confirm repeatability</li>
                  <li>• Consider this your baseline setup for future reference</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Record Test Button -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="space-y-4">
              <!-- Notes -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Test Notes (optional)
                </label>
                <textarea
                  v-model="testNotes"
                  class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  rows="3"
                  placeholder="Any observations, adjustments made, or environmental factors..."
                ></textarea>
              </div>
              
              <!-- Submit Test -->
              <button
                @click="recordTest"
                :disabled="!selectedImpactPattern || recordingTest"
                class="w-full px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                <i v-if="recordingTest" class="fas fa-spinner fa-spin mr-2"></i>
                <i v-else class="fas fa-save mr-2"></i>
                {{ recordingTest ? 'Recording Test...' : 'Record Test Result' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Previous Tests Section (Right Column) -->
        <div class="space-y-6">
          <!-- Group Overview Visualization -->
          <div v-if="groupOverviewData && completedTests.length >= 2" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-chart-area mr-2 text-purple-500"></i>
                Session Overview
              </h4>
              <button @click="showGroupOverview = !showGroupOverview" 
                      class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                <i :class="showGroupOverview ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
                   class="text-gray-500 dark:text-gray-400"></i>
              </button>
            </div>
            
            <div v-show="showGroupOverview">
              <!-- Statistics Summary -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 text-center">
                  <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {{ groupOverviewData.statistics.totalTests }}
                  </div>
                  <div class="text-xs text-blue-800 dark:text-blue-200">Total Tests</div>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 text-center">
                  <div class="text-2xl font-bold text-green-600 dark:text-green-400">
                    {{ groupOverviewData.statistics.avgOffset }}cm
                  </div>
                  <div class="text-xs text-green-800 dark:text-green-200">Avg Offset</div>
                </div>
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 text-center">
                  <div class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                    {{ groupOverviewData.statistics.minOffset }}cm
                  </div>
                  <div class="text-xs text-yellow-800 dark:text-yellow-200">Best Test</div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 text-center">
                  <div class="flex items-center justify-center">
                    <span class="text-2xl font-bold" 
                          :class="groupOverviewData.statistics.isImproving 
                            ? 'text-green-600 dark:text-green-400' 
                            : 'text-red-600 dark:text-red-400'">
                      <i :class="groupOverviewData.statistics.isImproving ? 'fas fa-arrow-down' : 'fas fa-arrow-up'" 
                         class="mr-1"></i>
                      {{ Math.abs(groupOverviewData.statistics.trend) }}cm
                    </span>
                  </div>
                  <div class="text-xs" 
                       :class="groupOverviewData.statistics.isImproving 
                         ? 'text-green-800 dark:text-green-200' 
                         : 'text-red-800 dark:text-red-200'">
                    {{ groupOverviewData.statistics.isImproving ? 'Improving' : 'Varying' }}
                  </div>
                </div>
              </div>

              <!-- Composite Target View -->
              <div class="mb-4">
                <h5 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                  All Test Groups Overlay
                </h5>
                <div class="flex justify-center">
                  <div class="relative bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 
                              rounded-full border-4 border-yellow-300 dark:border-yellow-600"
                       style="width: 200px; height: 200px;">
                    <!-- Center crosshair -->
                    <div class="absolute inset-0 flex items-center justify-center">
                      <div class="w-8 h-0.5 bg-gray-400 dark:bg-gray-500"></div>
                      <div class="absolute w-0.5 h-8 bg-gray-400 dark:bg-gray-500"></div>
                    </div>
                    
                    <!-- Test points -->
                    <template v-for="(testPoint, index) in groupOverviewData.testPoints" :key="`overview-${index}`">
                      <!-- Fletched group -->
                      <div class="absolute w-3 h-3 bg-blue-500 rounded-full border border-white transform -translate-x-1/2 -translate-y-1/2"
                           :style="{
                             left: (testPoint.fletchedPosition.x / 300 * 200) + 'px',
                             top: (testPoint.fletchedPosition.y / 300 * 200) + 'px'
                           }"
                           :title="`Test ${testPoint.testNumber} - Fletched`">
                        <div class="absolute -bottom-5 left-1/2 transform -translate-x-1/2 text-xs font-bold text-blue-600 dark:text-blue-400">
                          F{{ testPoint.testNumber }}
                        </div>
                      </div>
                      
                      <!-- Bareshaft group -->
                      <div class="absolute w-3 h-3 bg-red-500 rounded-full border border-white transform -translate-x-1/2 -translate-y-1/2"
                           :style="{
                             left: (testPoint.bareshaftPosition.x / 300 * 200) + 'px',
                             top: (testPoint.bareshaftPosition.y / 300 * 200) + 'px'
                           }"
                           :title="`Test ${testPoint.testNumber} - Bareshaft`">
                        <div class="absolute -top-5 left-1/2 transform -translate-x-1/2 text-xs font-bold text-red-600 dark:text-red-400">
                          B{{ testPoint.testNumber }}
                        </div>
                      </div>
                      
                      <!-- Offset line -->
                      <svg class="absolute inset-0 pointer-events-none">
                        <line :x1="testPoint.fletchedPosition.x / 300 * 200" 
                              :y1="testPoint.fletchedPosition.y / 300 * 200"
                              :x2="testPoint.bareshaftPosition.x / 300 * 200" 
                              :y2="testPoint.bareshaftPosition.y / 300 * 200"
                              :stroke="`hsl(${index * 60}, 70%, 50%)`" 
                              stroke-width="1" 
                              stroke-dasharray="2,2" 
                              opacity="0.7" />
                      </svg>
                    </template>
                  </div>
                </div>
                
                <!-- Legend -->
                <div class="flex justify-center mt-3 space-x-4 text-sm text-gray-600 dark:text-gray-400">
                  <div class="flex items-center">
                    <div class="w-3 h-3 bg-blue-500 rounded-full mr-1"></div>
                    Fletched Groups
                  </div>
                  <div class="flex items-center">
                    <div class="w-3 h-3 bg-red-500 rounded-full mr-1"></div>
                    Bareshaft Groups
                  </div>
                  <div class="flex items-center">
                    <div class="w-4 h-0.5 bg-gray-400 mr-1" style="border: 1px dashed;"></div>
                    Offset Lines
                  </div>
                </div>
              </div>

              <!-- Progress Chart -->
              <div class="mb-4">
                <h5 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                  Offset Distance Trend
                </h5>
                <div class="h-24 bg-gray-50 dark:bg-gray-700 rounded-lg p-4 relative">
                  <div class="flex items-end h-full space-x-2">
                    <template v-for="(testPoint, index) in groupOverviewData.testPoints" :key="`chart-${index}`">
                      <div class="flex-1 flex flex-col items-center">
                        <div class="bg-blue-500 rounded-t transition-all duration-300"
                             :style="{ 
                               height: Math.max(4, (testPoint.offset / Math.max(10, groupOverviewData.statistics.maxOffset) * 60)) + 'px',
                               width: '20px'
                             }">
                        </div>
                        <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          T{{ testPoint.testNumber }}
                        </div>
                        <div class="text-xs font-medium text-gray-900 dark:text-gray-100">
                          {{ testPoint.offset }}cm
                        </div>
                      </div>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Test History -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-history mr-2"></i>
              Previous Tests ({{ completedTests.length }})
            </h4>
            
            <div v-if="completedTests.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
              <i class="fas fa-clipboard-list text-4xl mb-4"></i>
              <p>No tests recorded yet</p>
              <p class="text-sm">Complete your first bareshaft test above</p>
            </div>
            
            <div v-else class="space-y-4">
              <div 
                v-for="(test, index) in completedTests" 
                :key="test.id"
                class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4"
              >
                <div class="flex items-start space-x-4">
                  <!-- Mini Target Visualization -->
                  <div class="flex-shrink-0">
                    <div class="relative w-16 h-16 border border-gray-300 dark:border-gray-600 rounded-full bg-yellow-50 dark:bg-yellow-900/10">
                      <!-- Target rings -->
                      <div class="absolute inset-1 border border-gray-400 dark:border-gray-500 rounded-full opacity-30"></div>
                      <div class="absolute inset-2 border border-gray-400 dark:border-gray-500 rounded-full opacity-30"></div>
                      
                      <!-- Center cross -->
                      <div class="absolute left-1/2 top-1/2 w-2 h-px bg-gray-400 dark:bg-gray-500 transform -translate-x-1/2 -translate-y-px opacity-50"></div>
                      <div class="absolute left-1/2 top-1/2 w-px h-2 bg-gray-400 dark:bg-gray-500 transform -translate-x-px -translate-y-1/2 opacity-50"></div>
                      
                      <!-- Fletched group (scaled down) -->
                      <div 
                        v-if="test.test_data?.fletched_group_position"
                        class="absolute w-2 h-2 bg-blue-500 rounded-full transform -translate-x-1/2 -translate-y-1/2"
                        :style="{ 
                          left: (test.test_data.fletched_group_position.x / 300 * 64) + 'px', 
                          top: (test.test_data.fletched_group_position.y / 300 * 64) + 'px' 
                        }"
                      ></div>
                      
                      <!-- Bareshaft group (scaled down) -->
                      <div 
                        v-if="test.test_data?.bareshaft_group_position"
                        class="absolute w-2 h-2 bg-red-500 rounded-full transform -translate-x-1/2 -translate-y-1/2"
                        :style="{ 
                          left: (test.test_data.bareshaft_group_position.x / 300 * 64) + 'px', 
                          top: (test.test_data.bareshaft_group_position.y / 300 * 64) + 'px' 
                        }"
                      ></div>
                      
                      <!-- Offset line (scaled down) -->
                      <svg v-if="test.test_data?.fletched_group_position && test.test_data?.bareshaft_group_position" 
                           class="absolute inset-0 w-full h-full pointer-events-none">
                        <line 
                          :x1="test.test_data.fletched_group_position.x / 300 * 64"
                          :y1="test.test_data.fletched_group_position.y / 300 * 64"
                          :x2="test.test_data.bareshaft_group_position.x / 300 * 64"
                          :y2="test.test_data.bareshaft_group_position.y / 300 * 64"
                          stroke="#3B82F6" 
                          stroke-width="1" 
                          stroke-dasharray="2,2"
                          opacity="0.7"
                        />
                      </svg>
                    </div>
                  </div>
                  
                  <!-- Test Details -->
                  <div class="flex-1">
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                        Test #{{ index + 1 }}
                      </span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">
                        {{ formatDate(test.timestamp) }}
                      </span>
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                      <div class="flex items-center">
                        <i class="fas fa-ruler text-blue-500 w-4 mr-2"></i>
                        <span>Offset: {{ test.test_data?.offset_distance_cm || 'N/A' }}cm {{ test.test_data?.bareshaft_offset || '' }}</span>
                      </div>
                      <div class="flex items-center">
                        <i class="fas fa-map-marker-alt text-green-500 w-4 mr-2"></i>
                        <span>Distance: {{ test.test_data?.shooting_distance_m || 'N/A' }}m</span>
                      </div>
                      <div class="flex items-center">
                        <i class="fas fa-crosshairs text-purple-500 w-4 mr-2"></i>
                        <span>Consistency: {{ test.test_data?.group_consistency || 'N/A' }}</span>
                      </div>
                      <div class="flex items-center">
                        <i class="fas fa-percentage text-orange-500 w-4 mr-2"></i>
                        <span>Confidence: {{ Math.round(test.confidence_score || 0) }}%</span>
                      </div>
                      <div v-if="test.notes" class="text-xs text-gray-500 dark:text-gray-400 italic mt-2 pl-6">
                        <i class="fas fa-comment text-gray-400 mr-1"></i>
                        {{ test.notes }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Session Completion -->
          <div v-if="completedTests.length >= 3" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-check-circle mr-2 text-green-500"></i>
              Complete Session
            </h4>
            
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
              You've completed {{ completedTests.length }} tests. You can now save this session to your journal.
            </p>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Session Summary (optional)
                </label>
                <textarea
                  v-model="completionNotes"
                  class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  rows="3"
                  placeholder="Overall observations, final adjustments, next steps..."
                ></textarea>
              </div>
              
              <button
                @click="completeSession"
                :disabled="completingSession"
                class="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                <i v-if="completingSession" class="fas fa-spinner fa-spin mr-2"></i>
                <i v-else class="fas fa-flag-checkered mr-2"></i>
                {{ completingSession ? 'Completing Session...' : 'Complete & Save Session' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Recommendations Modal -->
  <div v-if="showRecommendationsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="closeRecommendationsModal">
    <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto" @click.stop>
      <div class="p-6">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg mr-3">
              <i class="fas fa-lightbulb text-green-600 dark:text-green-400 text-xl"></i>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">
                Test #{{ currentRecommendations?.testNumber }} Results
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Tuning recommendations based on your test
              </p>
            </div>
          </div>
          <button @click="closeRecommendationsModal" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
            <i class="fas fa-times text-gray-500 dark:text-gray-400"></i>
          </button>
        </div>

        <!-- Basic Recommendations -->
        <div v-if="currentRecommendations?.basic?.length > 0" class="mb-6">
          <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
            <i class="fas fa-arrow-right text-blue-500 mr-2"></i>
            Recommendations
          </h4>
          <div class="space-y-2">
            <div v-for="(recommendation, index) in currentRecommendations.basic" :key="index" 
                 class="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p class="text-sm text-blue-800 dark:text-blue-200">{{ recommendation }}</p>
            </div>
          </div>
        </div>

        <!-- Detailed Analysis -->
        <div v-if="currentRecommendations?.analysis" class="mb-6">
          <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
            <i class="fas fa-chart-line text-purple-500 mr-2"></i>
            Detailed Analysis
          </h4>
          
          <!-- Confidence Score -->
          <div v-if="currentRecommendations.analysis.confidence_score" class="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Analysis Confidence</span>
              <span class="text-sm font-bold text-gray-900 dark:text-gray-100">
                {{ Math.round(currentRecommendations.analysis.confidence_score) }}%
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
              <div class="bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 h-2 rounded-full" 
                   :style="{ width: currentRecommendations.analysis.confidence_score + '%' }"></div>
            </div>
          </div>

          <!-- Tuning Status -->
          <div v-if="currentRecommendations.analysis.tuning_status" class="mb-4 p-3 border rounded-lg"
               :class="currentRecommendations.analysis.tuning_status === 'well_tuned' 
                 ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' 
                 : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'">
            <div class="flex items-center">
              <i :class="currentRecommendations.analysis.tuning_status === 'well_tuned' 
                ? 'fas fa-check-circle text-green-600 dark:text-green-400' 
                : 'fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400'"
                 class="mr-2"></i>
              <span class="text-sm font-medium"
                    :class="currentRecommendations.analysis.tuning_status === 'well_tuned' 
                      ? 'text-green-800 dark:text-green-200' 
                      : 'text-yellow-800 dark:text-yellow-200'">
                {{ currentRecommendations.analysis.tuning_status === 'well_tuned' ? 'Well Tuned' : 'Needs Adjustment' }}
              </span>
            </div>
          </div>

          <!-- Detailed Recommendations -->
          <div v-if="currentRecommendations.analysis.detailed_recommendations?.length > 0" class="space-y-3">
            <h5 class="text-md font-medium text-gray-900 dark:text-gray-100">Specific Adjustments:</h5>
            <div v-for="(rec, index) in currentRecommendations.analysis.detailed_recommendations" :key="index" 
                 class="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
              <div class="flex items-start">
                <i class="fas fa-cog text-purple-500 mt-1 mr-2 text-sm"></i>
                <div class="flex-1">
                  <div class="text-sm font-medium text-purple-900 dark:text-purple-100 mb-1">
                    {{ rec.component || 'Adjustment' }}: {{ rec.action || 'Modify' }} {{ rec.magnitude || '' }}
                  </div>
                  <div v-if="rec.reason" class="text-xs text-purple-700 dark:text-purple-300">
                    {{ rec.reason }}
                  </div>
                  <div v-if="rec.priority" class="mt-1">
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs"
                          :class="rec.priority <= 2 
                            ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200' 
                            : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'">
                      Priority {{ rec.priority }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Close Button -->
        <div class="flex justify-end">
          <button @click="closeRecommendationsModal" 
                  class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors">
            <i class="fas fa-check mr-2"></i>
            Continue Testing
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import TuningSessionHeader from '~/components/TuningSessionHeader.vue'

// Set page title and meta
useHead({
  title: 'Bareshaft Tuning Session',
  meta: [
    { name: 'description', content: 'Interactive bareshaft tuning session with visual target interface and progress tracking.' }
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

// Reactive data
const sessionData = ref(null)
const completedTests = ref([])
const loading = ref(true)
const error = ref(null)

// Test recording state
const recordingTest = ref(false)
const completingSession = ref(false)

// Recommendations state
const currentRecommendations = ref(null)
const showRecommendationsModal = ref(false)

// Group overview state
const showGroupOverview = ref(false)

// Test parameters
const testDistance = ref(20)
const groupConsistency = ref('good')
const testNotes = ref('')
const completionNotes = ref('')

// Impact pattern selection state
const selectedImpactPattern = ref(null)
const showPatternGuide = ref(false)

// Progressive guidance state
const currentStep = ref(1)
const nextStep = () => {
  if (currentStep.value < 4) {
    currentStep.value++
  }
}

// Bow type specific recommendations
const selectedBowType = ref('compound')

// Impact patterns based on bareshaft tuning documentation
const impactPatterns = [
  // Top row
  { 
    id: 'high-left', 
    displayName: 'High Left', 
    shortDesc: 'Above & Left',
    description: 'Bareshafts hit above and left of fletched arrows',
    spineDiagnosis: 'Arrows too stiff + nocking point too low',
    icon: '<i class="fa-duotone fa-solid fa-arrow-up transform -rotate-45 text-red-500"></i>'
  },
  { 
    id: 'high', 
    displayName: 'High', 
    shortDesc: 'Above Center',
    description: 'Bareshafts hit above fletched arrows',
    spineDiagnosis: 'Nocking point too low',
    icon: '<i class="fa-duotone fa-solid fa-arrow-up text-red-500"></i>'
  },
  { 
    id: 'high-right', 
    displayName: 'High Right', 
    shortDesc: 'Above & Right',
    description: 'Bareshafts hit above and right of fletched arrows',
    spineDiagnosis: 'Arrows too weak + nocking point too low',
    icon: '<i class="fa-duotone fa-solid fa-arrow-up transform rotate-45 text-red-500"></i>'
  },
  // Middle row
  { 
    id: 'left', 
    displayName: 'Left', 
    shortDesc: 'Left of Center',
    description: 'Bareshafts hit left of fletched arrows',
    spineDiagnosis: 'Arrows too stiff (right-handed archer)',
    icon: '<i class="fa-duotone fa-solid fa-arrow-left text-orange-500"></i>'
  },
  { 
    id: 'perfect', 
    displayName: 'Perfect', 
    shortDesc: 'Same Impact',
    description: 'Bareshafts group with fletched arrows',
    spineDiagnosis: 'Excellent tune achieved!',
    icon: '<i class="fa-duotone fa-solid fa-circle-dot text-green-500"></i>'
  },
  { 
    id: 'right', 
    displayName: 'Right', 
    shortDesc: 'Right of Center',
    description: 'Bareshafts hit right of fletched arrows',
    spineDiagnosis: 'Arrows too weak (right-handed archer)',
    icon: '<i class="fa-duotone fa-solid fa-arrow-right text-orange-500"></i>'
  },
  // Bottom row
  { 
    id: 'low-left', 
    displayName: 'Low Left', 
    shortDesc: 'Below & Left',
    description: 'Bareshafts hit below and left of fletched arrows',
    spineDiagnosis: 'Arrows too stiff + nocking point too high',
    icon: '<i class="fa-duotone fa-solid fa-arrow-down transform rotate-45 text-red-500"></i>'
  },
  { 
    id: 'low', 
    displayName: 'Low', 
    shortDesc: 'Below Center',
    description: 'Bareshafts hit below fletched arrows',
    spineDiagnosis: 'Nocking point too high',
    icon: '<i class="fa-duotone fa-solid fa-arrow-down text-red-500"></i>'
  },
  { 
    id: 'low-right', 
    displayName: 'Low Right', 
    shortDesc: 'Below & Right',
    description: 'Bareshafts hit below and right of fletched arrows',
    spineDiagnosis: 'Arrows too weak + nocking point too high',
    icon: '<i class="fa-duotone fa-solid fa-arrow-down transform -rotate-45 text-red-500"></i>'
  }
]

// Target interface data
const targetSize = 300
const fletchedGroup = ref({ x: null, y: null, placed: false })
const bareshaftGroup = ref({ x: null, y: null, placed: false })
const targetFace = ref(null)

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
  // Assuming 300px target represents ~30cm diameter
  return (pixelDistance / targetSize) * 30
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

// Tolerance zone calculations
const toleranceZoneRadius = computed(() => {
  // Base tolerance is 7cm at 20m, scale for different distances
  const baseTolerance = 7.0 // cm
  const baseDistance = 20 // meters
  const toleranceCm = baseTolerance * (testDistance.value / baseDistance)
  
  // Convert cm to pixels (approximate conversion based on target size)
  // Target face is 300px representing approximately 122cm (standard target diameter)
  const pixelsPerCm = 300 / 122
  return toleranceCm * pixelsPerCm
})

// Group overview data for visualization
const groupOverviewData = computed(() => {
  if (completedTests.value.length === 0) return null
  
  // Extract test data from completed tests
  const testPoints = completedTests.value.map((test, index) => {
    const testData = test.test_data || {}
    return {
      testNumber: index + 1,
      fletchedPosition: testData.fletched_group_position || { x: 0, y: 0 },
      bareshaftPosition: testData.bareshaft_group_position || { x: 0, y: 0 },
      offset: parseFloat(testData.offset_distance_cm || 0),
      direction: testData.bareshaft_offset || 'unknown',
      distance: testData.shooting_distance_m || 20,
      consistency: testData.group_consistency || 'good'
    }
  })
  
  // Calculate statistics
  const offsets = testPoints.map(p => p.offset)
  const avgOffset = offsets.reduce((sum, offset) => sum + offset, 0) / offsets.length
  const minOffset = Math.min(...offsets)
  const maxOffset = Math.max(...offsets)
  
  // Calculate improvement trend (negative means improving)
  const trend = testPoints.length > 1 
    ? testPoints[testPoints.length - 1].offset - testPoints[0].offset
    : 0
  
  return {
    testPoints,
    statistics: {
      totalTests: testPoints.length,
      avgOffset: Math.round(avgOffset * 10) / 10,
      minOffset: Math.round(minOffset * 10) / 10,
      maxOffset: Math.round(maxOffset * 10) / 10,
      trend: Math.round(trend * 10) / 10,
      isImproving: trend < 0
    }
  }
})

// Methods
const loadSessionData = async () => {
  try {
    loading.value = true
    error.value = null
    
    const sessionId = route.params.sessionId
    const response = await api.get(`/tuning-guides/sessions/${sessionId}`)
    
    sessionData.value = response
    completedTests.value = response.tests || []
    
    // Set default test distance from session settings
    if (response.settings?.shooting_distance) {
      testDistance.value = response.settings.shooting_distance
    }
    
  } catch (err) {
    console.error('Error loading session:', err)
    error.value = err.response?.status === 404 ? 'Session not found' : 'Failed to load session data'
  } finally {
    loading.value = false
  }
}

const handleTargetClick = (event) => {
  const rect = targetFace.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  if (!fletchedGroup.value.placed) {
    fletchedGroup.value = { x, y, placed: true }
  } else if (!bareshaftGroup.value.placed) {
    bareshaftGroup.value = { x, y, placed: true }
  }
}

// Impact pattern selection function
const selectImpactPattern = (pattern) => {
  selectedImpactPattern.value = pattern
}

const resetGroups = () => {
  fletchedGroup.value = { x: null, y: null, placed: false }
  bareshaftGroup.value = { x: null, y: null, placed: false }
  selectedImpactPattern.value = null
  currentStep.value = 1  // Reset progressive guidance
}

const recordTest = async () => {
  if (!selectedImpactPattern.value) return
  
  try {
    recordingTest.value = true
    
    const testData = {
      test_type: 'bareshaft_tuning',
      test_data: {
        shooting_distance_m: testDistance.value,
        impact_pattern: selectedImpactPattern.value.id,
        impact_pattern_name: selectedImpactPattern.value.displayName,
        spine_diagnosis: selectedImpactPattern.value.spineDiagnosis,
        group_consistency: groupConsistency.value,
        pattern_description: selectedImpactPattern.value.description
      },
      notes: testNotes.value.trim() || null,
      confidence_score: calculatePatternConfidenceScore(),
      timestamp: new Date().toISOString()
    }
    
    console.log('Recording bareshaft test:', testData)
    
    const sessionId = route.params.sessionId
    const response = await api.post(`/tuning-guides/sessions/${sessionId}/test`, testData)
    
    // Add to completed tests with proper structure
    const testRecord = {
      id: Date.now(), // Temporary ID
      test_type: 'bareshaft_tuning',
      timestamp: testData.timestamp,
      test_data: testData.test_data,
      notes: testData.notes,
      confidence_score: testData.confidence_score,
      recommendations: response.recommendations || [],
      analysis: response.analysis || null
    }
    completedTests.value.push(testRecord)
    
    // Show recommendations if available
    if (response.recommendations && response.recommendations.length > 0) {
      currentRecommendations.value = {
        basic: response.recommendations,
        analysis: response.analysis || null,
        testNumber: completedTests.value.length
      }
      showRecommendationsModal.value = true
    }
    
    // Reset for next test
    resetGroups()
    testNotes.value = ''
    
  } catch (error) {
    console.error('Error recording test:', error)
    alert('Failed to record test. Please try again.')
  } finally {
    recordingTest.value = false
  }
}

const calculateConfidenceScore = () => {
  // Base score on group consistency and offset measurement clarity
  let score = 70 // Base score
  
  // Adjust for group consistency
  const consistencyBonus = {
    'excellent': 20,
    'good': 15,
    'fair': 10,
    'poor': 0
  }
  score += consistencyBonus[groupConsistency.value] || 0
  
  // Adjust for offset distance (clearer offsets = higher confidence)
  if (offsetDistance.value > 5) {
    score += 10 // Clear offset is easier to measure
  }
  
  return Math.min(95, Math.max(50, score))
}

const calculatePatternConfidenceScore = () => {
  if (!selectedImpactPattern.value) return 50
  
  // Base score on pattern selection and group consistency  
  let score = 70 // Base score
  
  // Adjust for group consistency
  const consistencyBonus = {
    'excellent': 20,
    'good': 15,
    'fair': 10,
    'poor': 0
  }
  score += consistencyBonus[groupConsistency.value] || 0
  
  // Bonus for clear patterns (not perfect)
  if (selectedImpactPattern.value.id !== 'perfect') {
    score += 10 // Clear deviation patterns are valuable for tuning
  } else {
    score += 15 // Perfect impact is the ultimate goal
  }
  
  return Math.min(95, Math.max(50, score))
}

// Bow-specific recommendation functions
const getBowTypeDisplayName = (bowType) => {
  const names = {
    'compound': 'Compound Bow',
    'recurve': 'Olympic Recurve',
    'traditional': 'Traditional Bow',
    'barebow': 'Barebow Recurve'
  }
  return names[bowType] || 'Unknown Bow Type'
}

const getRecommendationPriority = (patternId) => {
  const priorities = {
    'high': 'Moderate Priority',
    'low': 'Moderate Priority', 
    'left': 'High Priority',
    'right': 'High Priority',
    'high-left': 'High Priority',
    'high-right': 'High Priority',
    'low-left': 'High Priority',
    'low-right': 'High Priority',
    'perfect': 'Maintain'
  }
  return priorities[patternId] || 'Unknown'
}

const getBowSpecificAdjustments = (patternId, bowType) => {
  // Comprehensive adjustments based on the documentation
  const adjustments = {
    // High impact patterns (nocking point too low)
    'high': {
      'compound': [
        {
          title: 'Lower Rest Position',
          instruction: 'Lower your arrow rest by 1/32" increments. Test after each adjustment.',
          warning: 'Make small adjustments only - large changes can overcorrect.'
        }
      ],
      'recurve': [
        {
          title: 'Raise Nocking Point',
          instruction: 'Move nocking point UP the string by 1/32" increments.',
          warning: 'Too high can cause arrows to hit the shelf.'
        }
      ],
      'traditional': [
        {
          title: 'Raise Nocking Point',
          instruction: 'Move nocking point UP the string by 1/32" increments.',
          warning: 'Check arrow clearance over the shelf after adjustment.'
        }
      ],
      'barebow': [
        {
          title: 'Raise Nocking Point',
          instruction: 'Move nocking point UP the string by 1/32" increments for your median crawl distance.',
          warning: 'This affects all crawl positions - expect some compromise.'
        }
      ]
    },
    
    // Low impact patterns (nocking point too high)  
    'low': {
      'compound': [
        {
          title: 'Raise Rest Position',
          instruction: 'Raise your arrow rest by 1/32" increments. Test after each adjustment.',
          warning: 'Check for fletching contact with rest at full draw.'
        }
      ],
      'recurve': [
        {
          title: 'Lower Nocking Point', 
          instruction: 'Move nocking point DOWN the string by 1/32" increments.',
          warning: 'Too low can cause nock pinch and inconsistent release.'
        }
      ],
      'traditional': [
        {
          title: 'Lower Nocking Point',
          instruction: 'Move nocking point DOWN the string by 1/32" increments.',
          warning: 'Maintain minimum 1/8" above square for safe release.'
        }
      ],
      'barebow': [
        {
          title: 'Lower Nocking Point',
          instruction: 'Move nocking point DOWN the string by 1/32" increments for your median crawl.',
          warning: 'Test at multiple crawl distances after adjustment.'
        }
      ]
    },

    // Left impact patterns (arrows too stiff - right-handed archer)
    'left': {
      'compound': [
        {
          title: 'Move Rest Left',
          instruction: 'Move arrow rest LEFT by 1/64" increments (chase the bareshaft).',
          warning: 'If rest movement over 1/8" doesn\'t help, spine may be wrong.'
        },
        {
          title: 'Add Point Weight',
          instruction: 'If rest adjustment doesn\'t work, add 25-grain increments of point weight.',
          warning: 'Heavy points affect arrow trajectory and penetration.'
        }
      ],
      'recurve': [
        {
          title: 'Decrease Plunger Tension',
          instruction: 'Turn plunger spring tension OUT by 1/4 turn (lighter).',
          warning: 'Too light can cause erratic arrow flight.'
        },
        {
          title: 'Move Button Out',
          instruction: 'If tension adjustment insufficient, move plunger button AWAY from riser by 1/32".',
          warning: 'Check arrow clearance past the riser.'
        },
        {
          title: 'Add Point Weight',
          instruction: 'As last resort, add 25-50 grains of point weight.',
          warning: 'Changes arrow trajectory and kinetic energy.'
        }
      ],
      'traditional': [
        {
          title: 'Add Point Weight',
          instruction: 'Add 25-50 grains of point weight to weaken dynamic spine.',
          warning: 'Heavy points drop trajectory significantly.'
        },
        {
          title: 'Raise Brace Height',
          instruction: 'Add string twists to increase brace height by 1/4".',
          warning: 'Higher brace height reduces arrow speed.'
        },
        {
          title: 'Soften Strike Plate',
          instruction: 'Use thinner/softer strike plate material.',
          warning: 'Too soft can wear quickly with heavy arrows.'
        }
      ],
      'barebow': [
        {
          title: 'Decrease Plunger Tension',
          instruction: 'Lighten plunger spring by 1/4 turn for median crawl distance.',
          warning: 'Affects tune across all crawl positions.'
        },
        {
          title: 'Add Point Weight',
          instruction: 'Add 25-50 grains point weight if plunger adjustment insufficient.',
          warning: 'Heavy points change gap and trajectory significantly.'
        }
      ]
    },

    // Right impact patterns (arrows too weak - right-handed archer)
    'right': {
      'compound': [
        {
          title: 'Move Rest Right',
          instruction: 'Move arrow rest RIGHT by 1/64" increments.',
          warning: 'Large rest movements may indicate wrong arrow spine.'
        },
        {
          title: 'Reduce Point Weight',
          instruction: 'If rest adjustment doesn\'t work, remove 25-grain increments of point weight.',
          warning: 'Light points may affect penetration on game.'
        }
      ],
      'recurve': [
        {
          title: 'Increase Plunger Tension',
          instruction: 'Turn plunger spring tension IN by 1/4 turn (stiffer).',
          warning: 'Too stiff can cause harsh arrow release from bow.'
        },
        {
          title: 'Move Button In',
          instruction: 'If tension adjustment insufficient, move plunger button TOWARD riser by 1/32".',
          warning: 'Too close can cause arrow contact with riser.'
        },
        {
          title: 'Reduce Point Weight',
          instruction: 'Remove 25-50 grains of point weight to stiffen dynamic spine.',
          warning: 'Very light points may not fly straight.'
        }
      ],
      'traditional': [
        {
          title: 'Reduce Point Weight',
          instruction: 'Remove 25-50 grains of point weight to stiffen arrows.',
          warning: 'Too light points may cause erratic flight.'
        },
        {
          title: 'Lower Brace Height',
          instruction: 'Remove string twists to decrease brace height by 1/4".',
          warning: 'Too low increases finger pinch and reduces forgiveness.'
        },
        {
          title: 'Stiffen Strike Plate',
          instruction: 'Use thicker/stiffer strike plate material.',
          warning: 'Hard materials can damage arrows on contact.'
        }
      ],
      'barebow': [
        {
          title: 'Increase Plunger Tension',
          instruction: 'Stiffen plunger spring by 1/4 turn for median crawl.',
          warning: 'May require compromise across crawl distances.'
        },
        {
          title: 'Reduce Point Weight',
          instruction: 'Remove 25-50 grains if plunger maxed out.',
          warning: 'Light points significantly affect gap measurements.'
        }
      ]
    }
  }

  // Handle combination patterns by merging relevant adjustments
  if (patternId.includes('-')) {
    const parts = patternId.split('-')
    const vertical = parts[0] === 'high' ? 'high' : 'low' 
    const horizontal = parts[1] === 'left' ? 'left' : 'right'
    
    const verticalAdj = adjustments[vertical]?.[bowType] || []
    const horizontalAdj = adjustments[horizontal]?.[bowType] || []
    
    return [...verticalAdj, ...horizontalAdj]
  }
  
  return adjustments[patternId]?.[bowType] || []
}

const getAlternativeSolutions = (patternId, bowType) => {
  const alternatives = {
    'left': {
      'compound': [
        'Check cam timing if rest adjustment over 1/8" needed',
        'Verify arrow spine - may need stiffer arrows',
        'Check for cam lean or limb twist'
      ],
      'recurve': [
        'Verify arrow spine selection with manufacturer charts',
        'Check clicker position if using one',
        'Consider shorter arrows if legal for your discipline'
      ],
      'traditional': [
        'Test individual arrow shafts - wood arrows vary significantly',
        'Check string silencer positions',
        'Verify consistent anchor point and release'
      ]
    },
    'right': {
      'compound': [
        'Arrow spine likely too weak - consider stiffer arrows',
        'Check for center shot alignment issues',
        'Verify draw weight hasn\'t changed'
      ],
      'recurve': [
        'Consider stiffer arrow spine',
        'Shorten arrows by 1/4" if possible',
        'Check for form inconsistencies'
      ],
      'traditional': [
        'Arrow spine may be fundamentally wrong',
        'Check for worn strike plate or shelf',
        'Verify draw weight at your draw length'
      ]
    },
    'high': {
      'compound': ['Check cam timing', 'Verify D-loop position', 'Add nock sets inside D-loop'],
      'recurve': ['Check tiller adjustment', 'Verify anchor point consistency'],
      'traditional': ['Check tiller', 'Verify consistent anchor and release']
    },
    'low': {
      'compound': ['Check for nock pinch in D-loop', 'Verify rest center shot'],
      'recurve': ['Check for low anchor point', 'Verify shelf height'],
      'traditional': ['Check for inconsistent release', 'Verify shelf setup']
    }
  }

  // Handle combination patterns
  if (patternId.includes('-')) {
    const parts = patternId.split('-')
    const vertical = parts[0] === 'high' ? 'high' : 'low'
    const horizontal = parts[1] === 'left' ? 'left' : 'right'
    
    return [
      ...(alternatives[vertical]?.[bowType] || []),
      ...(alternatives[horizontal]?.[bowType] || [])
    ]
  }
  
  return alternatives[patternId]?.[bowType] || []
}

const completeSession = async () => {
  try {
    completingSession.value = true
    
    const sessionId = route.params.sessionId
    await api.post(`/tuning-guides/sessions/${sessionId}/complete`, {
      completion_notes: completionNotes.value.trim() || null,
      total_tests: completedTests.value.length
    })
    
    // Navigate back to arrow setup
    if (sessionData.value?.setup_arrow_id) {
      router.push(`/setup-arrows/${sessionData.value.setup_arrow_id}`)
    } else {
      router.push('/my-setup')
    }
    
  } catch (error) {
    console.error('Error completing session:', error)
    alert('Failed to complete session. Please try again.')
  } finally {
    completingSession.value = false
  }
}

const handlePause = () => {
  console.log('Pause/Resume session')
}

const handleAbandon = async () => {
  if (confirm('Are you sure you want to abandon this tuning session? All progress will be lost.')) {
    router.go(-1)
  }
}

const handleSaveExit = () => {
  if (completedTests.value.length >= 1) {
    completeSession()
  } else {
    alert('Complete at least 1 test before saving the session.')
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const closeRecommendationsModal = () => {
  showRecommendationsModal.value = false
  currentRecommendations.value = null
}

// Enhanced Progress Tracking Functions
const sessionQualityScore = computed(() => {
  if (completedTests.value.length === 0) return 0
  
  const totalScore = completedTests.value.reduce((sum, test) => {
    return sum + (test.confidence_score || 0)
  }, 0)
  
  return totalScore / completedTests.value.length
})

const progressPercentage = computed(() => {
  const minimumTests = 3
  const maxTests = 8
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

const getQualityScoreClasses = (score) => {
  if (score >= 85) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  if (score >= 70) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  if (score >= 55) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
}

const getTestQualityDotClass = (score) => {
  if (score >= 85) return 'bg-green-500'
  if (score >= 70) return 'bg-blue-500'
  if (score >= 55) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getTestQualityRingClass = (score) => {
  if (score >= 85) return 'border-green-300 dark:border-green-600'
  if (score >= 70) return 'border-blue-300 dark:border-blue-600'
  if (score >= 55) return 'border-yellow-300 dark:border-yellow-600'
  return 'border-red-300 dark:border-red-600'
}

const mostCommonPattern = computed(() => {
  if (completedTests.value.length === 0) {
    return { icon: '<i class="fas fa-question text-gray-400"></i>', name: 'None' }
  }
  
  const patternCounts = {}
  completedTests.value.forEach(test => {
    const patternId = test.test_data?.impact_pattern
    if (patternId) {
      patternCounts[patternId] = (patternCounts[patternId] || 0) + 1
    }
  })
  
  const mostCommon = Object.entries(patternCounts)
    .sort(([,a], [,b]) => b - a)[0]
  
  if (!mostCommon) {
    return { icon: '<i class="fas fa-question text-gray-400"></i>', name: 'None' }
  }
  
  const pattern = impactPatterns.find(p => p.id === mostCommon[0])
  return {
    icon: pattern?.icon || '<i class="fas fa-crosshairs text-gray-400"></i>',
    name: pattern?.shortDesc || 'Unknown'
  }
})

const improvementTrend = computed(() => {
  if (completedTests.value.length < 2) {
    return { 
      icon: 'fas fa-minus text-gray-400', 
      text: 'Insufficient Data', 
      colorClass: 'text-gray-500' 
    }
  }
  
  const recentTests = completedTests.value.slice(-3) // Last 3 tests
  const scores = recentTests.map(test => test.confidence_score || 0)
  
  // Check if trending towards perfect tune (more recent tests showing perfect pattern)
  const perfectTrend = recentTests.filter(test => 
    test.test_data?.impact_pattern === 'perfect'
  ).length
  
  if (perfectTrend >= 2) {
    return { 
      icon: 'fas fa-bullseye text-green-500', 
      text: 'Achieving Tune', 
      colorClass: 'text-green-600' 
    }
  }
  
  // Calculate score trend
  const firstHalf = scores.slice(0, Math.ceil(scores.length / 2))
  const secondHalf = scores.slice(Math.floor(scores.length / 2))
  
  const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length
  const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length
  
  const improvement = secondAvg - firstAvg
  
  if (improvement > 10) {
    return { 
      icon: 'fas fa-arrow-trend-up text-green-500', 
      text: 'Improving', 
      colorClass: 'text-green-600' 
    }
  } else if (improvement > 0) {
    return { 
      icon: 'fas fa-arrow-right text-blue-500', 
      text: 'Stable', 
      colorClass: 'text-blue-600' 
    }
  } else {
    return { 
      icon: 'fas fa-arrow-trend-down text-orange-500', 
      text: 'Variable', 
      colorClass: 'text-orange-600' 
    }
  }
})

// Load data on mount
onMounted(() => {
  loadSessionData()
})
</script>