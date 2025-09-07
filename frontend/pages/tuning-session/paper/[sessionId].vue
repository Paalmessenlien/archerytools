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
        session-type="paper"
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

      <!-- Enhanced Progress Section -->
      <div class="mb-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-chart-line mr-2 text-blue-500"></i>
              Session Progress
            </h3>
            <div class="text-right">
              <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ completedTests.length }}/{{ Math.max(completedTests.length + 1, 10) }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">tests completed</div>
            </div>
          </div>
          
          <!-- Enhanced Progress Bar -->
          <div class="mb-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Overall Progress</span>
              <span class="text-sm text-gray-600 dark:text-gray-400">{{ Math.round((completedTests.length / Math.max(completedTests.length + 1, 10)) * 100) }}%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 relative overflow-hidden">
              <div 
                class="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-500 ease-out"
                :style="{ width: `${Math.round((completedTests.length / Math.max(completedTests.length + 1, 10)) * 100)}%` }"
              ></div>
              <div v-if="completedTests.length >= 3" class="absolute inset-0 bg-green-400/20 animate-pulse"></div>
            </div>
          </div>

          <!-- Test Quality Indicators -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
            <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3 text-center">
              <div class="text-lg font-bold text-green-700 dark:text-green-300">{{ excellentTests }}</div>
              <div class="text-xs text-green-600 dark:text-green-400">Excellent (≤0.25")</div>
            </div>
            <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3 text-center">
              <div class="text-lg font-bold text-yellow-700 dark:text-yellow-300">{{ goodTests }}</div>
              <div class="text-xs text-yellow-600 dark:text-yellow-400">Good (0.25"-0.75")</div>
            </div>
            <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 text-center">
              <div class="text-lg font-bold text-red-700 dark:text-red-300">{{ needsWorkTests }}</div>
              <div class="text-xs text-red-600 dark:text-red-400">Needs Work (>0.75")</div>
            </div>
          </div>

          <!-- Progress Dots with Quality Indicators -->
          <div class="flex items-center justify-center space-x-1.5 mb-4">
            <div 
              v-for="(test, index) in Math.max(completedTests.length + 1, 10)" 
              :key="index"
              class="relative group"
            >
              <div 
                class="w-4 h-4 rounded-full transition-all duration-300 cursor-pointer"
                :class="getTestDotClass(index)"
                :title="getTestDotTooltip(index)"
              >
                <!-- Quality indicator ring for completed tests -->
                <div 
                  v-if="index < completedTests.length"
                  class="absolute -inset-0.5 rounded-full opacity-50"
                  :class="getTestQualityRing(index)"
                ></div>
              </div>
            </div>
          </div>

          <!-- Session Status -->
          <div class="flex items-center justify-between text-sm">
            <div class="flex items-center space-x-4">
              <div class="flex items-center text-gray-600 dark:text-gray-400">
                <i class="fas fa-clock mr-1"></i>
                <span>{{ sessionDuration }}</span>
              </div>
              <div v-if="averageTearSize !== null" class="flex items-center text-gray-600 dark:text-gray-400">
                <i class="fas fa-crosshairs mr-1"></i>
                <span>Avg: {{ averageTearSize.toFixed(2) }}"</span>
              </div>
            </div>
            <div v-if="completedTests.length >= 3" class="flex items-center text-green-600 dark:text-green-400 font-medium">
              <i class="fas fa-check-circle mr-1"></i>
              Ready to complete
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
                <i class="fas fa-target mr-2"></i>
                Paper Tuning Test #{{ completedTests.length + 1 }}
              </h3>
              <div class="text-xs bg-blue-200 dark:bg-blue-800 text-blue-800 dark:text-blue-200 px-2 py-1 rounded-full">
                Step {{ currentStep }} of 4
              </div>
            </div>
            
            <!-- Step Progress Bar -->
            <div class="mb-4">
              <div class="flex items-center justify-between text-xs text-blue-700 dark:text-blue-300 mb-2">
                <span>Setup</span>
                <span>Shoot</span>
                <span>Examine</span>
                <span>Record</span>
              </div>
              <div class="relative h-2 bg-blue-200 dark:bg-blue-800 rounded-full">
                <div 
                  class="absolute h-2 bg-blue-500 rounded-full transition-all duration-500"
                  :style="{ width: `${(currentStep / 4) * 100}%` }"
                ></div>
                <!-- Step indicators -->
                <div v-for="step in 4" :key="step" 
                     class="absolute top-1/2 w-3 h-3 -mt-1.5 rounded-full border-2 border-white transition-colors"
                     :class="step <= currentStep ? 'bg-blue-500' : 'bg-blue-200 dark:bg-blue-700'"
                     :style="{ left: `${((step - 1) / 3) * 100}%`, transform: 'translateX(-50%)' }">
                </div>
              </div>
            </div>
            
            <!-- Dynamic step content -->
            <div class="space-y-3">
              <div v-if="currentStep === 1" class="space-y-2">
                <div class="flex items-center gap-3 text-sm text-blue-800 dark:text-blue-200">
                  <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-xs">1</div>
                  <span class="font-medium">Set up your paper frame</span>
                </div>
                <ul class="text-xs text-blue-700 dark:text-blue-300 ml-11 space-y-1">
                  <li>• Position paper frame 3-4 feet from target</li>
                  <li>• Ensure paper is taut and centered</li>
                  <li>• Stand {{ sessionData.settings?.shooting_distance || 20 }} yards behind paper</li>
                </ul>
                <button @click="nextStep" class="ml-11 text-xs bg-blue-500 text-white px-3 py-1 rounded-full hover:bg-blue-600 transition-colors">
                  Setup Complete →
                </button>
              </div>
              
              <div v-else-if="currentStep === 2" class="space-y-2">
                <div class="flex items-center gap-3 text-sm text-blue-800 dark:text-blue-200">
                  <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-xs">2</div>
                  <span class="font-medium">Shoot your arrow</span>
                </div>
                <ul class="text-xs text-blue-700 dark:text-blue-300 ml-11 space-y-1">
                  <li>• Use your normal shooting form</li>
                  <li>• Aim for center of paper</li>
                  <li>• Shoot only ONE arrow through the paper</li>
                </ul>
                <button @click="nextStep" class="ml-11 text-xs bg-blue-500 text-white px-3 py-1 rounded-full hover:bg-blue-600 transition-colors">
                  Shot Taken →
                </button>
              </div>
              
              <div v-else-if="currentStep === 3" class="space-y-2">
                <div class="flex items-center gap-3 text-sm text-blue-800 dark:text-blue-200">
                  <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-xs">3</div>
                  <span class="font-medium">Examine the tear pattern</span>
                </div>
                <ul class="text-xs text-blue-700 dark:text-blue-300 ml-11 space-y-1">
                  <li>• Look at the hole in the paper</li>
                  <li>• Note the direction of jagged edges</li>
                  <li>• Measure the longest dimension of tear</li>
                </ul>
                <div class="ml-11 flex items-center gap-2">
                  <button @click="nextStep" class="text-xs bg-blue-500 text-white px-3 py-1 rounded-full hover:bg-blue-600 transition-colors">
                    Examined →
                  </button>
                  <button @click="showTearGuide = true" class="text-xs border border-blue-300 text-blue-600 px-3 py-1 rounded-full hover:bg-blue-50 transition-colors">
                    Need Help?
                  </button>
                </div>
              </div>
              
              <div v-else-if="currentStep === 4" class="space-y-2">
                <div class="flex items-center gap-3 text-sm text-blue-800 dark:text-blue-200">
                  <div class="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold text-xs">4</div>
                  <span class="font-medium">Record your results</span>
                </div>
                <ul class="text-xs text-blue-700 dark:text-blue-300 ml-11 space-y-1">
                  <li>• Select the tear pattern that matches what you see</li>
                  <li>• Set the tear size using presets or slider</li>
                  <li>• Add any notes about conditions or observations</li>
                </ul>
                <div class="ml-11 text-xs text-green-600 dark:text-green-400 font-medium flex items-center gap-1">
                  <i class="fas fa-arrow-down"></i>
                  Complete the form below to record this test
                </div>
              </div>
            </div>
            
            <!-- Reset steps button -->
            <div class="mt-3 pt-3 border-t border-blue-200 dark:border-blue-700">
              <button @click="currentStep = 1" class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 flex items-center gap-1">
                <i class="fas fa-redo text-xs"></i>
                Start Over
              </button>
            </div>
          </div>

          <!-- Paper Tear Pattern Grid -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              Select Tear Pattern
            </h4>
            
            <!-- Enhanced Tear Pattern Grid -->
            <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6 mb-4">
              <div class="flex items-center justify-between mb-4">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Select the tear pattern that matches your paper
                </p>
                <button 
                  @click="showTearGuide = !showTearGuide" 
                  class="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1 transition-colors"
                >
                  <i class="fas fa-question-circle"></i>
                  {{ showTearGuide ? 'Hide' : 'Show' }} Guide
                </button>
              </div>
              
              <!-- Larger, clearer 3x3 grid -->
              <div class="grid grid-cols-3 gap-3 max-w-md mx-auto mb-4">
                <button
                  v-for="position in tearPositions" 
                  :key="position.id"
                  @click="selectTearPosition(position)"
                  class="aspect-square min-h-[4rem] border-2 rounded-xl cursor-pointer transition-all duration-200 flex flex-col items-center justify-center p-2 relative group hover:shadow-md"
                  :class="selectedTearPosition?.id === position.id 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 shadow-lg transform scale-105' 
                    : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-600/30'"
                  :title="position.description"
                  :aria-label="`Select ${position.displayName} tear pattern`"
                >
                  <!-- Visual indicator -->
                  <div class="w-6 h-6 mb-1 flex items-center justify-center">
                    <div v-if="position.direction !== 'clean'" class="relative">
                      <i 
                        class="text-red-500 text-lg transition-colors group-hover:text-red-600"
                        :class="getTearArrowClass(position.direction)"
                      ></i>
                    </div>
                    <div v-else class="relative">
                      <i class="fa-duotone fa-solid fa-circle-dot text-green-500 text-lg transition-colors group-hover:text-green-600 animate-pulse"></i>
                    </div>
                  </div>
                  
                  <!-- Clear label -->
                  <span class="text-xs font-medium text-center leading-tight">{{ position.displayName }}</span>
                  
                  <!-- Selection indicator -->
                  <div v-if="selectedTearPosition?.id === position.id" 
                       class="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                    <i class="fas fa-check text-white text-xs"></i>
                  </div>
                  
                  <!-- Tooltip on hover -->
                  <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                    <div class="bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded-lg px-3 py-2 whitespace-nowrap">
                      {{ position.description }}
                      <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-100"></div>
                    </div>
                  </div>
                </button>
              </div>
              
              <!-- Selected pattern confirmation -->
              <div v-if="selectedTearPosition" class="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div class="flex items-center justify-center gap-2 text-sm text-blue-800 dark:text-blue-200">
                  <i class="fas fa-check-circle text-green-500"></i>
                  <span>Selected: <strong>{{ selectedTearPosition.displayName }}</strong></span>
                </div>
                <p class="text-xs text-blue-600 dark:text-blue-300 mt-1">{{ selectedTearPosition.description }}</p>
              </div>
            </div>
            
            <!-- Expandable tear guide -->
            <div v-if="showTearGuide" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4 transition-all duration-300">
              <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                <i class="fas fa-book-open text-blue-500"></i>
                Paper Tear Pattern Reference
              </h5>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div class="space-y-2">
                  <h6 class="font-medium text-gray-800 dark:text-gray-200">What the tears mean:</h6>
                  <ul class="space-y-1 text-gray-600 dark:text-gray-400">
                    <li class="flex items-center gap-2">
                      <i class="fas fa-arrow-up text-red-500 text-xs"></i>
                      <span><strong>High tears:</strong> Nocking point too low</span>
                    </li>
                    <li class="flex items-center gap-2">
                      <i class="fas fa-arrow-down text-red-500 text-xs"></i>
                      <span><strong>Low tears:</strong> Nocking point too high</span>
                    </li>
                    <li class="flex items-center gap-2">
                      <i class="fas fa-arrow-left text-red-500 text-xs"></i>
                      <span><strong>Left tears:</strong> Weak spine or rest issue</span>
                    </li>
                    <li class="flex items-center gap-2">
                      <i class="fas fa-arrow-right text-red-500 text-xs"></i>
                      <span><strong>Right tears:</strong> Stiff spine or rest issue</span>
                    </li>
                  </ul>
                </div>
                <div class="space-y-2">
                  <h6 class="font-medium text-gray-800 dark:text-gray-200">How to measure:</h6>
                  <ul class="space-y-1 text-gray-600 dark:text-gray-400 text-xs">
                    <li>• Measure the longest dimension of the tear</li>
                    <li>• Don't include the arrow shaft hole</li>
                    <li>• Look for the jagged edge direction</li>
                    <li>• A clean hole means perfect tune!</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Enhanced Tear Magnitude Selector -->
            <div class="mb-4">
              <div class="flex items-center justify-between mb-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Tear Magnitude
                </label>
                <button 
                  @click="showMagnitudeHelp = !showMagnitudeHelp" 
                  class="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors"
                >
                  <i class="fas fa-question-circle"></i>
                  Help
                </button>
              </div>
              
              <!-- Expandable help -->
              <div v-if="showMagnitudeHelp" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mb-3 transition-all duration-300">
                <div class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                  <p class="font-medium">How to measure tear size:</p>
                  <ul class="text-xs space-y-1 ml-2">
                    <li>• Measure the longest dimension of the tear</li>
                    <li>• Don't include the arrow shaft hole</li>
                    <li>• Look for the direction of the jagged edges</li>
                  </ul>
                  <div class="grid grid-cols-2 gap-2 text-xs mt-2">
                    <div class="flex items-center gap-2">
                      <div class="w-3 h-3 bg-green-500 rounded"></div>
                      <span>0-1/4": Excellent</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <div class="w-3 h-3 bg-yellow-500 rounded"></div>
                      <span>1/4"-3/4": Good</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <div class="w-3 h-3 bg-orange-500 rounded"></div>
                      <span>3/4"-1.25": Needs work</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <div class="w-3 h-3 bg-red-500 rounded"></div>
                      <span>1.25"+: Poor tune</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Quick preset buttons -->
              <div class="grid grid-cols-5 gap-2 mb-3">
                <button 
                  v-for="preset in magnitudePresets" 
                  :key="preset.value"
                  @click="tearMagnitudeInches = preset.value"
                  class="py-2 px-1 text-xs font-medium rounded-lg border-2 transition-all duration-200 min-h-[2.5rem] flex flex-col items-center justify-center"
                  :class="tearMagnitudeInches === preset.value 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 shadow-md' 
                    : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 hover:bg-gray-50 dark:hover:bg-gray-600/30'"
                  :title="`Set magnitude to ${preset.label}`"
                >
                  <span class="font-bold">{{ preset.label }}</span>
                  <span class="text-[10px] opacity-75">{{ preset.quality }}</span>
                </button>
              </div>
              
              <!-- Visual ruler with current position indicator -->
              <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 mb-3">
                <div class="relative h-6 bg-gradient-to-r from-green-100 via-yellow-100 via-orange-100 to-red-100 dark:from-green-900/30 dark:via-yellow-900/30 dark:via-orange-900/30 dark:to-red-900/30 rounded-full mb-2">
                  <!-- Current value indicator -->
                  <div 
                    class="absolute top-0 bottom-0 w-2 bg-blue-500 rounded-full shadow-lg transition-all duration-200 transform -translate-x-1/2" 
                    :style="{ left: `${Math.min(100, (tearMagnitudeInches / 2) * 100)}%` }"
                  >
                    <div class="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                      {{ formatInches(tearMagnitudeInches) }}
                    </div>
                  </div>
                  
                  <!-- Scale markers -->
                  <div class="absolute inset-0 flex items-center justify-between px-1">
                    <div v-for="mark in [0, 0.5, 1, 1.5, 2]" :key="mark" class="w-px h-3 bg-gray-400 dark:bg-gray-500"></div>
                  </div>
                </div>
                
                <!-- Fine-tune slider -->
                <input 
                  v-model="tearMagnitudeInches"
                  type="range"
                  min="0"
                  max="2"
                  step="0.125"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider"
                  :aria-label="`Tear magnitude: ${formatInches(tearMagnitudeInches)}`"
                >
                
                <!-- Scale labels -->
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>0"</span>
                  <span>1/2"</span>
                  <span>1"</span>
                  <span>1.5"</span>
                  <span>2"</span>
                </div>
              </div>
              
              <!-- Current values display with quality indicator -->
              <div class="flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                <div class="flex items-center gap-4">
                  <div class="text-center">
                    <div class="text-lg font-bold text-blue-600 dark:text-blue-400">
                      {{ formatInches(tearMagnitudeInches) }}
                    </div>
                    <div class="text-xs text-gray-600 dark:text-gray-400">inches</div>
                  </div>
                  <div class="text-center">
                    <div class="text-lg font-bold text-green-600 dark:text-green-400">
                      {{ formatCentimeters(tearMagnitudeInches) }}
                    </div>
                    <div class="text-xs text-gray-600 dark:text-gray-400">cm</div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-medium px-3 py-1 rounded-full" :class="getMagnitudeClass(tearMagnitudeInches)">
                    {{ getMagnitudeLabel(tearMagnitudeInches) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Environmental Conditions -->
            <div class="mb-4">
              <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Environmental Conditions</h5>
              <div class="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Wind</label>
                  <select v-model="environmentalConditions.wind" class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                    <option value="">Select...</option>
                    <option value="calm">Calm</option>
                    <option value="light">Light</option>
                    <option value="moderate">Moderate</option>
                    <option value="strong">Strong</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Lighting</label>
                  <select v-model="environmentalConditions.lighting" class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                    <option value="">Select...</option>
                    <option value="bright">Bright</option>
                    <option value="overcast">Overcast</option>
                    <option value="indoor">Indoor</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Notes -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Test Notes
              </label>
              <textarea 
                v-model="currentTestNotes"
                placeholder="Record any observations, changes made, or other notes..."
                class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                rows="2"
              ></textarea>
            </div>

            <!-- Enhanced Record Test Button -->
            <div class="space-y-3">
              <!-- Validation checklist for incomplete forms -->
              <div v-if="!canRecordTest && !recording" class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3">
                <h6 class="text-sm font-medium text-amber-800 dark:text-amber-200 mb-2 flex items-center gap-2">
                  <i class="fas fa-exclamation-triangle"></i>
                  Complete Required Fields:
                </h6>
                <ul class="text-sm text-amber-700 dark:text-amber-300 space-y-1">
                  <li class="flex items-center gap-2">
                    <i :class="selectedTearPosition ? 'fas fa-check text-green-500' : 'fas fa-times text-red-500'"></i>
                    Select tear pattern
                  </li>
                  <li class="flex items-center gap-2">
                    <i class="fas fa-check text-green-500"></i>
                    Set tear magnitude ({{ formatInches(tearMagnitudeInches) }})
                  </li>
                </ul>
              </div>
              
              <!-- Main record button -->
              <button 
                @click="recordTest"
                :disabled="!canRecordTest || recording"
                class="w-full py-4 text-lg font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-3 shadow-lg hover:shadow-xl"
                :class="canRecordTest && !recording
                  ? 'bg-green-600 hover:bg-green-700 text-white transform hover:scale-[1.02] hover:-translate-y-0.5' 
                  : recording
                    ? 'bg-blue-600 text-white cursor-wait'
                    : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'"
              >
                <div v-if="recording" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <i v-else-if="canRecordTest" class="fas fa-check-circle text-xl"></i>
                <i v-else class="fas fa-exclamation-circle text-xl"></i>
                
                <span>
                  {{ recording ? 'Recording Test...' : 
                     canRecordTest ? 'Record Test Result' : 
                     'Complete Required Fields' }}
                </span>
              </button>
              
              <!-- Success feedback for ready state -->
              <div v-if="canRecordTest && !recording" class="text-center">
                <p class="text-xs text-green-600 dark:text-green-400 flex items-center justify-center gap-1">
                  <i class="fas fa-thumbs-up"></i>
                  Ready to record - all fields complete!
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Test Results & Analysis (Right Column) -->
        <div class="space-y-6">
          <!-- Previous Tests -->
          <div v-if="completedTests.length > 0" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-history mr-2"></i>
              Test Results ({{ completedTests.length }})
            </h4>
            
            <div class="space-y-4 max-h-96 overflow-y-auto">
              <div 
                v-for="(test, index) in completedTests.slice().reverse()" 
                :key="test.id"
                class="border border-gray-200 dark:border-gray-600 rounded-lg p-4"
              >
                <div class="flex items-center justify-between mb-2">
                  <div class="font-medium text-gray-900 dark:text-gray-100">
                    Test #{{ completedTests.length - index }}
                  </div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    {{ formatTime(test.created_at) }}
                  </div>
                </div>
                
                <div class="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                  <div><strong>Pattern:</strong> {{ test.test_data.tear_direction || 'Clean' }}</div>
                  <div><strong>Magnitude:</strong> {{ test.test_data.tear_magnitude || 'N/A' }}</div>
                  <div v-if="test.test_data.notes" class="text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded">
                    {{ test.test_data.notes }}
                  </div>
                </div>

                <!-- Recommendations -->
                <div v-if="test.recommendations" class="mt-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <h6 class="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-1">
                    <i class="fas fa-lightbulb mr-1"></i>
                    Recommendation:
                  </h6>
                  <p class="text-xs text-yellow-700 dark:text-yellow-300">{{ test.recommendations }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Session Analysis -->
          <div v-if="completedTests.length >= 2" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-chart-line mr-2"></i>
              Session Analysis
            </h4>
            
            <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span class="text-sm text-gray-600 dark:text-gray-300">Progress Trend:</span>
                <span class="text-sm font-medium" :class="getTrendClass()">
                  <i :class="getTrendIcon()" class="mr-1"></i>
                  {{ getProgressTrend() }}
                </span>
              </div>
              
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span class="text-sm text-gray-600 dark:text-gray-300">Consistency:</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ getConsistencyRating() }}%
                </span>
              </div>
            </div>
          </div>

          <!-- Complete Session Button -->
          <div v-if="completedTests.length >= 1" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <h4 class="text-lg font-medium text-green-800 dark:text-green-200 mb-2">
              <i class="fas fa-check-circle mr-2"></i>
              Ready to Complete Session?
            </h4>
            <p class="text-sm text-green-700 dark:text-green-300 mb-4">
              You've completed {{ completedTests.length }} test{{ completedTests.length > 1 ? 's' : '' }}. 
              Save your results to the journal and return to your arrow setup.
            </p>
            
            <div class="space-y-3">
              <button 
                @click="completeSession"
                :disabled="completing"
                class="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center justify-center"
              >
                <div v-if="completing" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                <i v-else class="fas fa-save mr-2"></i>
                {{ completing ? 'Saving...' : 'Complete Session & Save to Journal' }}
              </button>
              
              <button 
                @click="continueTests"
                class="w-full py-2 bg-blue-100 dark:bg-blue-900/30 hover:bg-blue-200 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 font-medium rounded-lg transition-colors"
              >
                Continue Testing
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import TuningSessionHeader from '~/components/TuningSessionHeader.vue'

// Route and API
const route = useRoute()
const router = useRouter()
const api = useApi()

// Page state
const loading = ref(true)
const error = ref('')
const sessionData = ref(null)
const completedTests = ref([])
const recording = ref(false)
const completing = ref(false)

// Current test state
const selectedTearPosition = ref(null)
const selectedMagnitude = ref('')
const tearMagnitudeInches = ref(0)
const currentTestNotes = ref('')
const showTearGuide = ref(false)
const showMagnitudeHelp = ref(false)
const environmentalConditions = ref({
  wind: '',
  lighting: ''
})

// Progressive guidance state
const currentStep = ref(1)
const nextStep = () => {
  if (currentStep.value < 4) {
    currentStep.value++
  }
}

// Magnitude presets for quick selection
const magnitudePresets = [
  { value: 0, label: '0"', quality: 'Perfect' },
  { value: 0.25, label: '1/4"', quality: 'Excellent' },
  { value: 0.5, label: '1/2"', quality: 'Good' },
  { value: 0.75, label: '3/4"', quality: 'Fair' },
  { value: 1, label: '1"', quality: 'Poor' }
]

// Tear positions for 3x3 grid with clear names and descriptions
const tearPositions = [
  { id: 'high-left', label: 'HL', displayName: 'High Left', direction: 'high-left', description: 'Tear above and left of center' },
  { id: 'high', label: 'H', displayName: 'High', direction: 'high', description: 'Tear directly above center' },
  { id: 'high-right', label: 'HR', displayName: 'High Right', direction: 'high-right', description: 'Tear above and right of center' },
  { id: 'left', label: 'L', displayName: 'Left', direction: 'left', description: 'Tear directly left of center' },
  { id: 'clean', label: 'CLEAN', displayName: 'Perfect Hole', direction: 'clean', description: 'Clean round bullet hole - perfect tune!' },
  { id: 'right', label: 'R', displayName: 'Right', direction: 'right', description: 'Tear directly right of center' },
  { id: 'low-left', label: 'LL', displayName: 'Low Left', direction: 'low-left', description: 'Tear below and left of center' },
  { id: 'low', label: 'L', displayName: 'Low', direction: 'low', description: 'Tear directly below center' },
  { id: 'low-right', label: 'LR', displayName: 'Low Right', direction: 'low-right', description: 'Tear below and right of center' }
]

// Computed
const canRecordTest = computed(() => {
  return selectedTearPosition.value && tearMagnitudeInches.value >= 0 && !recording.value
})

// Progress tracking computed properties
const excellentTests = computed(() => {
  return completedTests.value.filter(test => test.test_data.tear_magnitude_inches <= 0.25).length
})

const goodTests = computed(() => {
  return completedTests.value.filter(test => 
    test.test_data.tear_magnitude_inches > 0.25 && test.test_data.tear_magnitude_inches <= 0.75
  ).length
})

const needsWorkTests = computed(() => {
  return completedTests.value.filter(test => test.test_data.tear_magnitude_inches > 0.75).length
})

const averageTearSize = computed(() => {
  if (completedTests.value.length === 0) return null
  const total = completedTests.value.reduce((sum, test) => sum + test.test_data.tear_magnitude_inches, 0)
  return total / completedTests.value.length
})

const sessionDuration = computed(() => {
  if (!sessionData.value?.started_at) return '00:00'
  const start = new Date(sessionData.value.started_at)
  const now = new Date()
  const diff = now - start
  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

// Methods
const selectTearPosition = (position) => {
  selectedTearPosition.value = position
}

const getTearArrowClass = (direction) => {
  // Arrows point inward - direction of arrow travel through paper
  const iconClasses = {
    'high': 'fa-duotone fa-solid fa-arrow-down',        // High tear = arrow moving down
    'high-right': 'fa-duotone fa-solid fa-arrow-down transform rotate-45',  // High-right = arrow moving down-left
    'right': 'fa-duotone fa-solid fa-arrow-left',       // Right tear = arrow moving left
    'low-right': 'fa-duotone fa-solid fa-arrow-left transform -rotate-45',     // Low-right = arrow moving up-left
    'low': 'fa-duotone fa-solid fa-arrow-up',           // Low tear = arrow moving up
    'low-left': 'fa-duotone fa-solid fa-arrow-right transform rotate-45',     // Low-left = arrow moving up-right
    'left': 'fa-duotone fa-solid fa-arrow-right',       // Left tear = arrow moving right
    'high-left': 'fa-duotone fa-solid fa-arrow-down transform -rotate-45'   // High-left = arrow moving down-right
  }
  return iconClasses[direction] || 'fa-duotone fa-solid fa-arrow-down'
}

// Tear magnitude slider helper functions
const formatInches = (inches) => {
  const num = parseFloat(inches)
  if (num === 0) return '0"'
  if (num < 1) {
    // Convert to fractions for values less than 1 inch
    const fractions = {
      0.125: '1/8"',
      0.25: '1/4"',
      0.375: '3/8"',
      0.5: '1/2"',
      0.625: '5/8"',
      0.75: '3/4"',
      0.875: '7/8"'
    }
    return fractions[num] || `${num.toFixed(3)}"`
  }
  // For values 1 inch and above, show decimal
  return `${num.toFixed(num % 1 === 0 ? 0 : 2)}"`
}

const formatCentimeters = (inches) => {
  const cm = parseFloat(inches) * 2.54
  if (cm === 0) return '0 cm'
  return `${cm.toFixed(1)} cm`
}

const getMagnitudeLabel = (inches) => {
  const num = parseFloat(inches)
  if (num === 0) return 'Perfect'
  if (num <= 0.25) return 'Minimal'
  if (num <= 0.75) return 'Small'
  if (num <= 1.25) return 'Medium'
  return 'Large'
}

const getMagnitudeClass = (inches) => {
  const num = parseFloat(inches)
  if (num === 0) return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
  if (num <= 0.25) return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
  if (num <= 0.75) return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
  if (num <= 1.25) return 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300'
  return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
}

const recordTest = async () => {
  if (!canRecordTest.value) return
  
  recording.value = true
  
  try {
    const testData = {
      test_type: 'paper_tuning',
      tear_position: selectedTearPosition.value.id,
      tear_direction: selectedTearPosition.value.direction,
      tear_magnitude: formatInches(tearMagnitudeInches.value),
      tear_magnitude_inches: tearMagnitudeInches.value,
      environmental_conditions: environmentalConditions.value,
      notes: currentTestNotes.value,
      test_number: completedTests.value.length + 1
    }

    const result = await api.post(`/tuning-guides/sessions/${route.params.sessionId}/test`, testData)
    
    // Add to completed tests
    completedTests.value.push({
      id: result.id,
      test_data: testData,
      recommendations: result.recommendations,
      created_at: new Date().toISOString()
    })

    // Reset form
    selectedTearPosition.value = null
    selectedMagnitude.value = ''
    tearMagnitudeInches.value = 0
    currentTestNotes.value = ''
    environmentalConditions.value = { wind: '', lighting: '' }
    currentStep.value = 1  // Reset progressive guidance

    // Show success notification
    showNotification('Test recorded successfully!', 'success')
    
  } catch (err) {
    console.error('Error recording test:', err)
    showNotification('Failed to record test', 'error')
  } finally {
    recording.value = false
  }
}

// Progress visualization helper functions
const getTestDotClass = (index) => {
  if (index < completedTests.value.length) {
    const test = completedTests.value[index]
    const magnitude = test.test_data.tear_magnitude_inches
    if (magnitude <= 0.25) return 'bg-green-500'
    if (magnitude <= 0.75) return 'bg-yellow-500'
    return 'bg-red-500'
  } else if (index === completedTests.value.length) {
    return 'bg-blue-500 animate-pulse'
  } else {
    return 'bg-gray-300 dark:bg-gray-600'
  }
}

const getTestQualityRing = (index) => {
  if (index >= completedTests.value.length) return ''
  const test = completedTests.value[index]
  const magnitude = test.test_data.tear_magnitude_inches
  if (magnitude <= 0.25) return 'ring-2 ring-green-400'
  if (magnitude <= 0.75) return 'ring-2 ring-yellow-400'
  return 'ring-2 ring-red-400'
}

const getTestDotTooltip = (index) => {
  if (index < completedTests.value.length) {
    const test = completedTests.value[index]
    const tearPos = tearPositions.find(p => p.id === test.test_data.tear_position)
    return `Test ${index + 1}: ${tearPos?.displayName || 'Unknown'} - ${test.test_data.tear_magnitude}`
  } else if (index === completedTests.value.length) {
    return `Current test (${index + 1})`
  } else {
    return `Test ${index + 1} (pending)`
  }
}

const completeSession = async () => {
  completing.value = true
  
  try {
    const sessionSummary = {
      total_tests: completedTests.value.length,
      progress_trend: getProgressTrend(),
      consistency_rating: getConsistencyRating(),
      final_notes: `Paper tuning session completed with ${completedTests.value.length} tests.`
    }

    await api.post(`/tuning-guides/sessions/${route.params.sessionId}/complete`, sessionSummary)
    
    // Create journal entry with proper formatting
    await createJournalEntryForSession()
    
    showNotification('Session completed and saved to journal!', 'success')
    
    // Navigate back to arrow setup
    if (sessionData.value?.arrow_setup_id) {
      await router.push(`/setup-arrows/${sessionData.value.arrow_setup_id}`)
    } else {
      await router.push('/my-setup')
    }
    
  } catch (err) {
    console.error('Error completing session:', err)
    showNotification('Failed to complete session', 'error')
  } finally {
    completing.value = false
  }
}

const continueTests = () => {
  // Just a UI helper - user continues with current form
  showNotification('Continue recording test results', 'info')
}

const handleSaveExit = () => {
  if (completedTests.value.length > 0) {
    completeSession()
  } else {
    handleAbandon()
  }
}

const handlePause = async () => {
  try {
    await api.post(`/guide-sessions/${route.params.sessionId}/pause`, {
      notes: `Session paused with ${completedTests.value.length} completed tests.`
    })
    showNotification('Session paused', 'info')
    router.go(-1)
  } catch (err) {
    showNotification('Failed to pause session', 'error')
  }
}

const handleAbandon = async () => {
  if (confirm('Are you sure you want to abandon this session? All test data will be lost.')) {
    try {
      await api.delete(`/guide-sessions/${route.params.sessionId}`)
      showNotification('Session abandoned', 'info')
      router.go(-1)
    } catch (err) {
      showNotification('Failed to abandon session', 'error')
    }
  }
}

// Analysis methods
const getProgressTrend = () => {
  if (completedTests.value.length < 2) return 'Insufficient data'
  
  const recent = completedTests.value.slice(-2)
  const improvement = recent[1].test_data.tear_direction === 'clean' || 
                     (recent[0].test_data.tear_direction !== 'clean' && recent[1].test_data.tear_magnitude === 'minimal')
  
  return improvement ? 'Improving' : 'Stable'
}

const getTrendClass = () => {
  const trend = getProgressTrend()
  if (trend === 'Improving') return 'text-green-600 dark:text-green-400'
  if (trend === 'Stable') return 'text-blue-600 dark:text-blue-400'
  return 'text-gray-600 dark:text-gray-400'
}

const getTrendIcon = () => {
  const trend = getProgressTrend()
  if (trend === 'Improving') return 'fas fa-arrow-up'
  if (trend === 'Stable') return 'fas fa-minus'
  return 'fas fa-question'
}

const getConsistencyRating = () => {
  if (completedTests.value.length < 2) return 0
  
  const patterns = completedTests.value.map(t => t.test_data.tear_direction)
  const uniquePatterns = new Set(patterns)
  
  // More consistent = fewer unique patterns
  return Math.max(0, 100 - (uniquePatterns.size - 1) * 25)
}

// Journal entry creation for paper tuning
const createJournalEntryForSession = async () => {
  try {
    const arrowName = sessionData.value?.arrow ? 
      `${sessionData.value.arrow.manufacturer} ${sessionData.value.arrow.model_name}` : 
      `Arrow ${sessionData.value?.arrow_id || 'Unknown'}`
    
    const bowSetupName = sessionData.value?.bow_setup?.name || 'Unknown Setup'
    
    // Format session duration
    const sessionDuration = formatSessionDuration()
    
    // Create journal entry content
    const journalContent = createPaperTuningJournalContent(arrowName, bowSetupName, sessionDuration)
    
    // Enhanced session data for detail viewer with complete bow setup and arrow data
    const enhancedSessionData = {
      tuning_type: 'paper',
      session_quality: calculateSessionQuality(),
      test_results: completedTests.value.map(test => ({
        test_number: test.test_number,
        timestamp: test.timestamp,
        tear_direction: test.test_data.tear_direction,
        tear_magnitude: test.test_data.tear_magnitude_inches,
        tear_position: test.test_data.tear_position,
        notes: test.notes || '',
        confidence_score: calculateTestConfidence(test),
        summary: test.summary || ''
      })),
      most_common_tear: getMostCommonTear(),
      average_tear_size: averageTearSize.value,
      consistency_rating: getConsistencyRating(),
      progress_trend: getProgressTrend(),
      // Complete arrow technical data (not linked)
      arrow_technical_data: {
        manufacturer: sessionData.value?.arrow?.manufacturer,
        model_name: sessionData.value?.arrow?.model_name,
        material: sessionData.value?.arrow?.material,
        spine: sessionData.value?.arrow?.spine,
        diameter_inches: sessionData.value?.arrow?.diameter_inches,
        length_inches: sessionData.value?.arrow_length || sessionData.value?.arrow?.length_inches,
        weight_grains: sessionData.value?.arrow?.weight_grains,
        gpi: sessionData.value?.arrow?.gpi,
        point_weight_grains: sessionData.value?.point_weight,
        total_weight_grains: sessionData.value?.arrow?.weight_grains ? 
          (sessionData.value.arrow.weight_grains + (sessionData.value.point_weight || 0)) : null,
        nock_type: sessionData.value?.arrow?.nock_type,
        fletching_type: sessionData.value?.arrow?.fletching_type,
        shaft_construction: sessionData.value?.arrow?.shaft_construction,
        tolerances: sessionData.value?.arrow?.tolerances
      },
      // Complete bow setup data (not linked)
      bow_setup_data: {
        name: sessionData.value?.bow_setup?.name,
        bow_type: sessionData.value?.bow_setup?.bow_type,
        draw_length_inches: sessionData.value?.bow_setup?.draw_length,
        draw_weight_pounds: sessionData.value?.bow_setup?.draw_weight,
        brace_height_inches: sessionData.value?.bow_setup?.brace_height,
        cam_type: sessionData.value?.bow_setup?.cam_type,
        bow_manufacturer: sessionData.value?.bow_setup?.bow_manufacturer,
        bow_model: sessionData.value?.bow_setup?.bow_model,
        riser_material: sessionData.value?.bow_setup?.riser_material,
        limb_material: sessionData.value?.bow_setup?.limb_material,
        string_type: sessionData.value?.bow_setup?.string_type,
        string_length: sessionData.value?.bow_setup?.string_length,
        cable_guard: sessionData.value?.bow_setup?.cable_guard,
        rest_type: sessionData.value?.bow_setup?.rest_type,
        rest_manufacturer: sessionData.value?.bow_setup?.rest_manufacturer,
        rest_model: sessionData.value?.bow_setup?.rest_model,
        sight_type: sessionData.value?.bow_setup?.sight_type,
        sight_manufacturer: sessionData.value?.bow_setup?.sight_manufacturer,
        sight_model: sessionData.value?.bow_setup?.sight_model,
        stabilizer_config: sessionData.value?.bow_setup?.stabilizer_config,
        release_aid_type: sessionData.value?.bow_setup?.release_aid_type,
        peep_sight_diameter: sessionData.value?.bow_setup?.peep_sight_diameter,
        d_loop_material: sessionData.value?.bow_setup?.d_loop_material,
        kisser_button: sessionData.value?.bow_setup?.kisser_button,
        notes: sessionData.value?.bow_setup?.notes
      },
      session_details: {
        session_duration: sessionDuration,
        started_at: sessionData.value?.started_at,
        completed_at: new Date().toISOString(),
        total_tests_conducted: completedTests.value.length,
        environmental_conditions: environmentalConditions.value
      }
    }

    const journalEntry = {
      title: `Paper Tuning Session - ${arrowName}`,
      content: journalContent,
      entry_type: 'paper_tuning_session',
      bow_setup_id: sessionData.value?.bow_setup_id,
      session_data: enhancedSessionData,
      tags: ['paper-tuning', 'tuning-session']
    }

    await api.post('/journal', journalEntry)
  } catch (error) {
    console.error('Failed to create journal entry:', error)
    // Don't throw error - journal creation failure shouldn't stop session completion
  }
}

const createPaperTuningJournalContent = (arrowName, bowSetupName, sessionDuration) => {
  const testResults = completedTests.value.map(test => {
    const tearPos = tearPositions.find(pos => pos.id === test.test_data.tear_position)
    const tearName = tearPos?.displayName || 'Unknown position'
    const tearMagnitude = test.test_data.tear_magnitude_inches
    const magnitudeText = tearMagnitude === 0 ? 'Clean hole' : `${tearMagnitude}"`
    
    return `Test ${test.test_number}: ${tearName} - ${magnitudeText}`
  }).join('\n')

  const sessionStats = {
    totalTests: completedTests.value.length,
    excellentCount: excellentTests.value,
    goodCount: goodTests.value,
    needsWorkCount: needsWorkTests.value,
    averageTear: averageTearSize.value ? averageTearSize.value.toFixed(2) : 'N/A'
  }

  const arrowTechData = sessionData.value?.arrow
  const bowSetupData = sessionData.value?.bow_setup
  
  return `# Paper Tuning Session - ${arrowName}

## Session Details
- **Arrow**: ${arrowName}
- **Bow Setup**: ${bowSetupName}
- **Session Duration**: ${sessionDuration}
- **Date**: ${new Date().toLocaleDateString()}

## Arrow Technical Specifications
- **Manufacturer**: ${arrowTechData?.manufacturer || 'Not specified'}
- **Model**: ${arrowTechData?.model_name || 'Not specified'}
- **Material**: ${arrowTechData?.material || 'Not specified'}
- **Spine**: ${arrowTechData?.spine || 'Not specified'}
- **Diameter**: ${arrowTechData?.diameter_inches || 'Not specified'}"
- **Length**: ${sessionData.value?.arrow_length || arrowTechData?.length_inches || 'Not specified'}"
- **Weight (grains)**: ${arrowTechData?.weight_grains || 'Not specified'}
- **GPI**: ${arrowTechData?.gpi || 'Not specified'}
- **Point Weight**: ${sessionData.value?.point_weight || 'Not specified'} grains
- **Total Weight**: ${arrowTechData?.weight_grains && sessionData.value?.point_weight ? 
    (arrowTechData.weight_grains + sessionData.value.point_weight) : 'Not calculated'} grains
- **Shaft Construction**: ${arrowTechData?.shaft_construction || 'Not specified'}
- **Tolerances**: ${arrowTechData?.tolerances || 'Not specified'}
- **Nock Type**: ${arrowTechData?.nock_type || 'Not specified'}
- **Fletching**: ${arrowTechData?.fletching_type || 'Not specified'}

## Bow Setup Configuration
- **Bow Type**: ${bowSetupData?.bow_type || 'Not specified'}
- **Manufacturer**: ${bowSetupData?.bow_manufacturer || 'Not specified'}
- **Model**: ${bowSetupData?.bow_model || 'Not specified'}
- **Draw Weight**: ${bowSetupData?.draw_weight || 'Not specified'} lbs
- **Draw Length**: ${bowSetupData?.draw_length || 'Not specified'}"
- **Brace Height**: ${bowSetupData?.brace_height || 'Not specified'}"
- **Cam Type**: ${bowSetupData?.cam_type || 'Not specified'}
- **Riser Material**: ${bowSetupData?.riser_material || 'Not specified'}
- **Limb Material**: ${bowSetupData?.limb_material || 'Not specified'}
- **Rest Type**: ${bowSetupData?.rest_type || 'Not specified'}
- **Rest**: ${bowSetupData?.rest_manufacturer} ${bowSetupData?.rest_model || ''} 
- **Sight**: ${bowSetupData?.sight_manufacturer} ${bowSetupData?.sight_model || ''}
- **String Type**: ${bowSetupData?.string_type || 'Not specified'}
- **Release Aid**: ${bowSetupData?.release_aid_type || 'Not specified'}
- **Peep Sight**: ${bowSetupData?.peep_sight_diameter || 'Not specified'}
- **D-Loop**: ${bowSetupData?.d_loop_material || 'Not specified'}

## Test Results Summary
- **Total Tests**: ${sessionStats.totalTests}
- **Excellent (≤0.25")**: ${sessionStats.excellentCount}
- **Good (0.25"-0.75")**: ${sessionStats.goodCount}
- **Needs Work (>0.75")**: ${sessionStats.needsWorkCount}
- **Average Tear Size**: ${sessionStats.averageTear}"

## Individual Test Results
${testResults}

## Analysis
- **Most Common Tear**: ${getMostCommonTear()}
- **Progress Trend**: ${getProgressTrend()}
- **Consistency Rating**: ${getConsistencyRating()}%

## Recommendations
${generatePaperTuningRecommendations()}

## Notes
Session completed successfully with comprehensive tear pattern analysis. All equipment specifications recorded for future reference and comparison.`
}

const formatSessionDuration = () => {
  if (!sessionData.value?.started_at) return 'Unknown duration'
  
  const start = new Date(sessionData.value.started_at)
  const end = new Date()
  const durationMinutes = Math.floor((end - start) / 60000)
  
  if (durationMinutes < 60) {
    return `${durationMinutes} minutes`
  } else {
    const hours = Math.floor(durationMinutes / 60)
    const remainingMinutes = durationMinutes % 60
    return `${hours}h ${remainingMinutes}m`
  }
}

const calculateSessionQuality = () => {
  if (completedTests.value.length === 0) return 0
  
  let qualityScore = 0
  completedTests.value.forEach(test => {
    const tearSize = test.test_data.tear_magnitude_inches
    if (tearSize <= 0.25) qualityScore += 100
    else if (tearSize <= 0.5) qualityScore += 85
    else if (tearSize <= 0.75) qualityScore += 70
    else if (tearSize <= 1.0) qualityScore += 55
    else qualityScore += 40
  })
  
  return Math.round(qualityScore / completedTests.value.length)
}

const calculateTestConfidence = (test) => {
  const tearSize = test.test_data.tear_magnitude_inches
  const hasNotes = test.notes && test.notes.length > 0
  
  let confidence = 90 // Base confidence
  
  // Reduce confidence for larger tears (less precise)
  if (tearSize > 1.0) confidence -= 20
  else if (tearSize > 0.75) confidence -= 10
  else if (tearSize > 0.5) confidence -= 5
  
  // Increase confidence if there are detailed notes
  if (hasNotes) confidence += 5
  
  return Math.max(50, Math.min(100, confidence))
}

const getMostCommonTear = () => {
  if (completedTests.value.length === 0) return 'No tests recorded'
  
  const tearCounts = {}
  completedTests.value.forEach(test => {
    const tearPos = tearPositions.find(pos => pos.id === test.test_data.tear_position)
    const tearName = tearPos?.displayName || 'Unknown'
    tearCounts[tearName] = (tearCounts[tearName] || 0) + 1
  })
  
  const mostCommon = Object.entries(tearCounts).reduce((max, [tear, count]) => 
    count > max.count ? { tear, count } : max, { tear: 'None', count: 0 })
  
  return `${mostCommon.tear} (${mostCommon.count} times)`
}

const generatePaperTuningRecommendations = () => {
  if (completedTests.value.length === 0) return 'No recommendations available.'
  
  const recommendations = []
  const mostRecentTest = completedTests.value[completedTests.value.length - 1]
  const tearDirection = mostRecentTest.test_data.tear_direction
  const tearSize = mostRecentTest.test_data.tear_magnitude_inches
  
  // Basic tuning recommendations based on tear direction
  switch (tearDirection) {
    case 'right':
      recommendations.push('• Move arrow rest slightly left or reduce draw weight')
      break
    case 'left':
      recommendations.push('• Move arrow rest slightly right or increase draw weight')
      break
    case 'high':
      recommendations.push('• Lower nocking point or reduce arrow spine')
      break
    case 'low':
      recommendations.push('• Raise nocking point or increase arrow spine')
      break
    case 'clean':
      recommendations.push('• Excellent! Your bow is well tuned')
      break
    default:
      if (tearDirection.includes('high') && tearDirection.includes('right')) {
        recommendations.push('• Move rest left and lower nocking point')
      } else if (tearDirection.includes('high') && tearDirection.includes('left')) {
        recommendations.push('• Move rest right and lower nocking point')
      } else if (tearDirection.includes('low') && tearDirection.includes('right')) {
        recommendations.push('• Move rest left and raise nocking point')
      } else if (tearDirection.includes('low') && tearDirection.includes('left')) {
        recommendations.push('• Move rest right and raise nocking point')
      }
  }
  
  // Additional recommendations based on tear size
  if (tearSize > 1.0) {
    recommendations.push('• Consider checking arrow spine compatibility')
    recommendations.push('• Verify consistent anchor point and release')
  } else if (tearSize <= 0.25) {
    recommendations.push('• Minimal adjustments needed - fine tuning complete')
  }
  
  return recommendations.length > 0 ? recommendations.join('\n') : 'Continue testing for more specific recommendations.'
}

// Utility methods
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const showNotification = (message, type = 'info') => {
  // Implementation depends on your notification system
  console.log(`${type}: ${message}`)
}

// Load session data
const loadSession = async () => {
  loading.value = true
  
  try {
    const response = await api.get(`/tuning-guides/${route.params.sessionId}`)
    sessionData.value = response
    
    // Load existing test results
    if (response.test_results) {
      completedTests.value = response.test_results
    }
    
  } catch (err) {
    console.error('Error loading session:', err)
    error.value = err.message || 'Failed to load session'
  } finally {
    loading.value = false
  }
}

// Page meta
definePageMeta({
  middleware: 'auth-check'
})

// Initialize
onMounted(() => {
  loadSession()
})
</script>

<style scoped>
/* Custom styles for the tuning session page */
.grid {
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .grid-cols-1 {
    grid-template-columns: 1fr;
  }
}

/* Tear position grid styling */
.aspect-square {
  aspect-ratio: 1 / 1;
  min-height: 60px;
}

/* Test results scrolling */
.max-h-96 {
  max-height: 24rem;
}

/* Progress dots animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Custom slider styling */
.slider {
  -webkit-appearance: none;
  background: transparent;
  cursor: pointer;
}

.slider::-webkit-slider-track {
  width: 100%;
  height: 8px;
  cursor: pointer;
  background: #e2e8f0;
  border-radius: 4px;
}

.dark .slider::-webkit-slider-track {
  background: #374151;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.slider::-moz-range-track {
  width: 100%;
  height: 8px;
  cursor: pointer;
  background: #e2e8f0;
  border-radius: 4px;
  border: none;
}

.dark .slider::-moz-range-track {
  background: #374151;
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.slider::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}
</style>