<template>
  <div ref="wizardContainer" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Wizard Header with Progress -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          Interactive Tuning & Equipment Setup
        </h2>
        <!-- Progress Indicator -->
        <div class="flex items-center space-x-2">
          <div class="flex items-center">
            <div v-for="step in 3" :key="step" class="flex items-center">
              <div 
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors',
                  currentStep >= step 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                ]"
              >
                {{ step }}
              </div>
              <div 
                v-if="step < 3" 
                :class="[
                  'w-8 h-0.5 transition-colors',
                  currentStep > step ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                ]"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Dynamic Description based on current step -->
      <p class="text-gray-600 dark:text-gray-300">
        <span v-if="currentStep === 1">Select your bow setup to get started</span>
        <span v-else-if="currentStep === 2">Choose between arrow tuning or equipment setup</span>
        <span v-else-if="currentStep === 3">Select your tuning guide or equipment category</span>
      </p>
    </div>

    <!-- Step 1: Bow Setup Selection -->
    <div v-show="currentStep >= 1" class="wizard-step" :class="{ 'step-completed': currentStep > 1 }">
      <div class="step-header" @click="currentStep > 1 && editStep(1)">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div 
              :class="[
                'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium mr-3 transition-colors',
                currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
              ]"
            >
              <i v-if="currentStep > 1" class="fas fa-check"></i>
              <span v-else>1</span>
            </div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              Select Bow Setup
            </h3>
          </div>
          <!-- Selected Setup Summary (when completed) -->
          <div v-if="currentStep > 1 && selectedBowSetup" class="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span class="font-medium mr-2">{{ selectedBowSetup.name }}</span>
            <button class="text-blue-600 hover:text-blue-700 dark:text-blue-400">
              <i class="fas fa-edit text-xs"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Step 1 Content -->
      <div v-if="currentStep === 1" class="step-content mt-4">

        <div v-if="loading.bowSetups" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600 dark:text-gray-300">Loading bow setups...</span>
        </div>

        <div v-else-if="!bowSetups.length" class="text-center py-12">
          <i class="fas fa-bow-arrow text-gray-400 text-4xl mb-4"></i>
          <p class="text-gray-500 dark:text-gray-400 mb-4">No bow setups found</p>
          <button 
            @click="$router.push('/setups')"
            class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-plus mr-2"></i>
            Create Bow Setup
          </button>
        </div>

        <div v-else class="space-y-6">
          <!-- Bow Setup Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="setup in bowSetups" 
              :key="setup.id"
              @click="selectBowSetup(setup)"
              class="p-5 border-2 rounded-xl cursor-pointer transition-all duration-200 touch-manipulation"
              :class="selectedBowSetup?.id === setup.id 
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400 shadow-md' 
                : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-sm'"
            >
              <div class="flex items-center mb-3">
                <div 
                  :class="[
                    'w-3 h-3 rounded-full mr-3 transition-colors',
                    selectedBowSetup?.id === setup.id ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
                  ]"
                ></div>
                <div class="flex items-center flex-1">
                  <i class="fas fa-crosshairs text-blue-600 dark:text-blue-400 mr-2"></i>
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {{ setup.name }}
                  </h3>
                </div>
                <i v-if="selectedBowSetup?.id === setup.id" class="fas fa-check-circle text-blue-500 ml-2"></i>
              </div>
              <div class="grid grid-cols-3 gap-3 text-sm text-gray-600 dark:text-gray-300">
                <div class="text-center">
                  <div class="font-medium text-gray-900 dark:text-gray-100">{{ formatBowType(setup.bow_type) }}</div>
                  <div class="text-xs">Type</div>
                </div>
                <div class="text-center">
                  <div class="font-medium text-gray-900 dark:text-gray-100">{{ setup.draw_weight }} lbs</div>
                  <div class="text-xs">Draw Weight</div>
                </div>
                <div class="text-center">
                  <div class="font-medium text-gray-900 dark:text-gray-100">{{ setup.draw_length }}"</div>
                  <div class="text-xs">Draw Length</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Continue Button -->
          <div v-if="selectedBowSetup" class="flex justify-center pt-4">
            <button 
              @click="continueToStep(2)"
              class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors shadow-sm hover:shadow-md"
            >
              Continue to Tuning Type
              <i class="fas fa-arrow-right ml-2"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2: Tuning Type Selection -->
    <div v-show="currentStep >= 2" class="wizard-step" :class="{ 'step-completed': currentStep > 2 }">
      <div class="step-header" @click="currentStep > 2 && editStep(2)">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div 
              :class="[
                'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium mr-3 transition-colors',
                currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
              ]"
            >
              <i v-if="currentStep > 2" class="fas fa-check"></i>
              <span v-else>2</span>
            </div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              Choose Tuning Type
            </h3>
          </div>
          <!-- Selected Type Summary (when completed) -->
          <div v-if="currentStep > 2" class="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span class="font-medium mr-2">{{ selectionType === 'arrow' ? 'Arrow Tuning' : 'Equipment Setup' }}</span>
            <button class="text-blue-600 hover:text-blue-700 dark:text-blue-400">
              <i class="fas fa-edit text-xs"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Step 2 Content -->
      <div v-if="currentStep === 2" class="step-content mt-6">
        <!-- Large Selection Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div 
            @click="selectTuningType('arrow')"
            class="p-8 border-2 rounded-xl cursor-pointer transition-all duration-200 touch-manipulation text-center"
            :class="selectionType === 'arrow'
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400 shadow-lg'
              : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-md'"
          >
            <div class="flex justify-center mb-4">
              <div 
                :class="[
                  'w-16 h-16 rounded-full flex items-center justify-center transition-colors',
                  selectionType === 'arrow' 
                    ? 'bg-blue-100 dark:bg-blue-900/50' 
                    : 'bg-gray-100 dark:bg-gray-700'
                ]"
              >
                <i 
                  :class="[
                    'fas fa-bullseye text-3xl',
                    selectionType === 'arrow' 
                      ? 'text-blue-600 dark:text-blue-400' 
                      : 'text-gray-600 dark:text-gray-400'
                  ]"
                ></i>
              </div>
            </div>
            <h4 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Arrow Tuning
            </h4>
            <p class="text-gray-600 dark:text-gray-300 mb-4">
              Interactive guides for paper tuning, bareshaft testing, and walkback analysis
            </p>
            <div class="flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
              <i class="fas fa-clock mr-1"></i>
              15-35 minutes per session
            </div>
            <div v-if="selectionType === 'arrow'" class="mt-4">
              <i class="fas fa-check-circle text-blue-500 text-xl"></i>
            </div>
          </div>

          <div 
            @click="selectTuningType('equipment')"
            class="p-8 border-2 rounded-xl cursor-pointer transition-all duration-200 touch-manipulation text-center"
            :class="selectionType === 'equipment'
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400 shadow-lg'
              : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-md'"
          >
            <div class="flex justify-center mb-4">
              <div 
                :class="[
                  'w-16 h-16 rounded-full flex items-center justify-center transition-colors',
                  selectionType === 'equipment' 
                    ? 'bg-blue-100 dark:bg-blue-900/50' 
                    : 'bg-gray-100 dark:bg-gray-700'
                ]"
              >
                <i 
                  :class="[
                    'fas fa-tools text-3xl',
                    selectionType === 'equipment' 
                      ? 'text-blue-600 dark:text-blue-400' 
                      : 'text-gray-600 dark:text-gray-400'
                  ]"
                ></i>
              </div>
            </div>
            <h4 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Equipment Setup
            </h4>
            <p class="text-gray-600 dark:text-gray-300 mb-4">
              Document bow, sight, rest, and accessory adjustments in your journal
            </p>
            <div class="flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
              <i class="fas fa-journal-whills mr-1"></i>
              Documentation & tracking
            </div>
            <div v-if="selectionType === 'equipment'" class="mt-4">
              <i class="fas fa-check-circle text-blue-500 text-xl"></i>
            </div>
          </div>
        </div>

        <!-- Continue Button -->
        <div v-if="selectionType" class="flex justify-center pt-8">
          <button 
            @click="continueToStep(3)"
            class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors shadow-sm hover:shadow-md"
          >
            Continue to {{ selectionType === 'arrow' ? 'Arrow Selection' : 'Equipment Categories' }}
            <i class="fas fa-arrow-right ml-2"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Step 3: Final Selection (Arrow or Equipment) -->
    <div v-show="currentStep >= 3" class="wizard-step">
      <div class="step-header">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div 
              :class="[
                'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium mr-3 transition-colors',
                currentStep >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
              ]"
            >
              3
            </div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              {{ selectionType === 'arrow' ? 'Select Arrow & Tuning Guide' : 'Select Equipment Category' }}
            </h3>
          </div>
        </div>
      </div>

      <!-- Step 3 Content -->
      <div v-if="currentStep === 3" class="step-content mt-6">
        <!-- Arrow Selection -->
        <div v-if="selectionType === 'arrow'" class="space-y-6">
          <div class="text-center">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Select Arrow Configuration
            </h4>
            <p class="text-gray-600 dark:text-gray-300">
              Choose an arrow to access interactive tuning guides
            </p>
          </div>

          <!-- Arrow Loading/Empty States -->
          <div v-if="loading.arrows" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-3 text-gray-600 dark:text-gray-300">Loading arrows...</span>
          </div>

          <div v-else-if="!setupArrows.length" class="text-center py-12">
            <i class="fas fa-arrows-alt text-gray-400 text-4xl mb-4"></i>
            <p class="text-gray-500 dark:text-gray-400 mb-4">No arrows found for this bow setup</p>
            <button 
              @click="$router.push(`/setups/${selectedBowSetup.id}`)"
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-plus mr-2"></i>
              Add Arrows to Setup
            </button>
          </div>

          <!-- Arrow Selection -->
          <div v-else class="space-y-4">
            <div 
              v-for="arrowSetup in setupArrows" 
              :key="`${arrowSetup.arrow_id}-${arrowSetup.arrow_length}-${arrowSetup.point_weight}`"
              @click="selectArrow(arrowSetup)"
              class="border-2 rounded-xl p-4 cursor-pointer transition-all duration-200 touch-manipulation"
              :class="selectedArrow?.arrow_id === arrowSetup.arrow_id && 
                      selectedArrow?.arrow_length === arrowSetup.arrow_length && 
                      selectedArrow?.point_weight === arrowSetup.point_weight
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400 shadow-md' 
                : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-sm'"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1 min-w-0">
                  <!-- Arrow Header -->
                  <div class="flex items-center mb-3">
                    <div 
                      :class="[
                        'w-3 h-3 rounded-full mr-3 transition-colors',
                        selectedArrow?.arrow_id === arrowSetup.arrow_id && 
                        selectedArrow?.arrow_length === arrowSetup.arrow_length && 
                        selectedArrow?.point_weight === arrowSetup.point_weight ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
                      ]"
                    ></div>
                    <div class="flex items-center space-x-2 flex-1">
                      <h5 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {{ arrowSetup.arrow?.manufacturer || arrowSetup.manufacturer || 'Unknown Manufacturer' }}
                      </h5>
                      <span class="text-gray-400">•</span>
                      <span class="text-gray-700 dark:text-gray-300">
                        {{ arrowSetup.arrow?.model_name || arrowSetup.model_name || `Arrow ID: ${arrowSetup.arrow_id}` }}
                      </span>
                    </div>
                    <i v-if="selectedArrow?.arrow_id === arrowSetup.arrow_id" class="fas fa-check-circle text-blue-500 ml-2"></i>
                  </div>
                  
                  <!-- Arrow Specifications -->
                  <div class="grid grid-cols-3 gap-4 text-sm">
                    <div class="text-center">
                      <div class="font-semibold text-gray-900 dark:text-gray-100">{{ getDisplaySpine(arrowSetup) }}</div>
                      <div class="text-gray-500">Spine</div>
                    </div>
                    <div class="text-center">
                      <div class="font-semibold text-gray-900 dark:text-gray-100">{{ arrowSetup.arrow_length }}"</div>
                      <div class="text-gray-500">Length</div>
                    </div>
                    <div class="text-center">
                      <div class="font-semibold text-gray-900 dark:text-gray-100">{{ arrowSetup.point_weight }} gr</div>
                      <div class="text-gray-500">Point</div>
                    </div>
                  </div>
                </div>
                
                <!-- Tuning History Badge -->
                <div v-if="arrowSetup.tuning_tests_count > 0" class="ml-4 text-center">
                  <div class="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-2 py-1 rounded-full text-xs font-medium">
                    {{ arrowSetup.tuning_tests_count }} tests
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Tuning Guides Selection -->
          <div v-if="selectedArrow" class="mt-8 space-y-4">
            <div class="text-center">
              <h5 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Available Tuning Guides
              </h5>
              <p class="text-gray-600 dark:text-gray-300">
                Choose your preferred tuning method for this arrow
              </p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div 
                v-for="guide in availableTuningGuides" 
                :key="guide.id"
                @click="startTuningGuide(guide)"
                :disabled="starting"
                class="p-6 border-2 border-gray-200 dark:border-gray-600 rounded-xl cursor-pointer transition-all duration-200 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-md text-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div class="flex items-center justify-center mb-4">
                  <div class="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                    <i :class="`${guide.icon} text-2xl ${guide.color}`"></i>
                  </div>
                </div>
                <h6 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {{ guide.name }}
                </h6>
                <p class="text-sm text-gray-600 dark:text-gray-300 mb-3">
                  {{ guide.description }}
                </p>
                <div class="flex items-center justify-center text-xs text-gray-500 dark:text-gray-400">
                  <i class="fas fa-clock mr-1"></i>
                  {{ guide.estimatedTime }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Equipment Selection -->
        <div v-else-if="selectionType === 'equipment'" class="space-y-6">
          <div class="text-center">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Select Equipment Category
            </h4>
            <p class="text-gray-600 dark:text-gray-300">
              Choose equipment to create tuning documentation in your journal
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="category in equipmentCategories" 
              :key="category.name"
              @click="selectEquipmentCategory(category)"
              class="p-6 border-2 rounded-xl cursor-pointer transition-all duration-200 text-center touch-manipulation"
              :class="selectedEquipmentCategory?.name === category.name 
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400 shadow-md' 
                : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-sm'"
            >
              <div class="flex items-center justify-center mb-4">
                <div 
                  :class="[
                    'w-12 h-12 rounded-full flex items-center justify-center transition-colors',
                    selectedEquipmentCategory?.name === category.name 
                      ? 'bg-blue-100 dark:bg-blue-900/50' 
                      : 'bg-gray-100 dark:bg-gray-700'
                  ]"
                >
                  <i :class="`${category.icon} text-2xl ${category.color}`"></i>
                </div>
              </div>
              <h5 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                {{ category.label }}
              </h5>
              <p class="text-sm text-gray-600 dark:text-gray-300">
                {{ category.description }}
              </p>
              <div v-if="selectedEquipmentCategory?.name === category.name" class="mt-4">
                <i class="fas fa-check-circle text-blue-500 text-xl"></i>
              </div>
            </div>
          </div>

          <!-- Equipment Setup Details -->
          <div v-if="selectedEquipmentCategory" class="mt-8">
            <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
              <div class="flex items-start space-x-4">
                <div class="flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/50">
                  <i :class="`${selectedEquipmentCategory.icon} text-2xl ${selectedEquipmentCategory.color}`"></i>
                </div>
                <div class="flex-1">
                  <h4 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
                    {{ selectedEquipmentCategory.label }} Setup Documentation
                  </h4>
                  <p class="text-gray-600 dark:text-gray-300 mb-4">
                    Create a detailed journal entry to document your {{ selectedEquipmentCategory.label.toLowerCase() }} setup process, adjustments, and observations.
                  </p>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h5 class="font-medium text-gray-800 dark:text-gray-200 mb-2">
                        Documentation includes:
                      </h5>
                      <ul class="space-y-1">
                        <li v-for="item in selectedEquipmentCategory.documentationItems" :key="item" class="flex items-center text-sm text-gray-600 dark:text-gray-300">
                          <i class="fas fa-check-circle text-green-500 mr-2 text-xs"></i>
                          {{ item }}
                        </li>
                      </ul>
                    </div>
                    <div>
                      <h5 class="font-medium text-gray-800 dark:text-gray-200 mb-2">
                        Benefits:
                      </h5>
                      <ul class="space-y-1">
                        <li class="flex items-center text-sm text-gray-600 dark:text-gray-300">
                          <i class="fas fa-history text-blue-500 mr-2 text-xs"></i>
                          Track setup changes over time
                        </li>
                        <li class="flex items-center text-sm text-gray-600 dark:text-gray-300">
                          <i class="fas fa-search text-purple-500 mr-2 text-xs"></i>
                          Easy reference for future adjustments
                        </li>
                        <li class="flex items-center text-sm text-gray-600 dark:text-gray-300">
                          <i class="fas fa-chart-line text-green-500 mr-2 text-xs"></i>
                          Performance correlation analysis
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex justify-center mt-6">
              <button 
                @click="startEquipmentSetup"
                :disabled="starting"
                class="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors shadow-sm hover:shadow-md flex items-center"
              >
                <div v-if="starting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                <i v-else class="fas fa-plus mr-2"></i>
                {{ starting ? 'Creating Entry...' : `Create ${selectedEquipmentCategory.label} Setup Entry` }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Wizard Navigation -->
    <div v-if="currentStep > 1" class="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-600 mt-8">
      <button 
        @click="goToPreviousStep"
        class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
      >
        <i class="fas fa-arrow-left mr-2"></i>
        Back
      </button>
      
      <button 
        @click="resetWizard"
        class="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-700 font-medium rounded-lg transition-colors"
      >
        <i class="fas fa-refresh mr-2"></i>
        Start Over
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useApi } from '~/composables/useApi'
import { useRouter } from 'vue-router'

// Router
const router = useRouter()

// Wizard state management
const currentStep = ref(1)
const wizardContainer = ref(null)

// Reactive data
const selectedBowSetup = ref(null)
const selectionType = ref('arrow') // 'arrow' or 'equipment'
const selectedArrow = ref(null)
const selectedEquipmentCategory = ref(null)
const bowSetups = ref([])
const setupArrows = ref([])
const starting = ref(false)

const loading = ref({
  bowSetups: false,
  arrows: false
})

// API composable
const api = useApi()

// Equipment categories with enhanced metadata
const equipmentCategories = [
  {
    name: 'bow',
    label: 'Bow',
    icon: 'fas fa-crosshairs',
    color: 'text-blue-600 dark:text-blue-400',
    description: 'Bow tuning & setup',
    documentationItems: [
      'Tiller measurements',
      'Brace height adjustments', 
      'Timing and synchronization',
      'Performance notes'
    ]
  },
  {
    name: 'arrow_rest',
    label: 'Arrow Rest',
    icon: 'fas fa-grip-horizontal',
    color: 'text-green-600 dark:text-green-400',
    description: 'Rest positioning & tuning',
    documentationItems: [
      'Centershot alignment',
      'Height adjustments',
      'Contact pressure settings',
      'Clearance verification'
    ]
  },
  {
    name: 'sight',
    label: 'Sight',
    icon: 'fas fa-bullseye',
    color: 'text-purple-600 dark:text-purple-400',
    description: 'Sight setup & calibration',
    documentationItems: [
      'Pin gap measurements',
      'Windage adjustments',
      'Elevation settings',
      'Distance marks'
    ]
  },
  {
    name: 'release',
    label: 'Release Aid',
    icon: 'fas fa-hand-point-up',
    color: 'text-orange-600 dark:text-orange-400',
    description: 'Release tuning & setup',
    documentationItems: [
      'Trigger sensitivity',
      'Grip positioning',
      'Length adjustments',
      'Performance feedback'
    ]
  },
  {
    name: 'stabilizer',
    label: 'Stabilizer',
    icon: 'fas fa-balance-scale',
    color: 'text-indigo-600 dark:text-indigo-400',
    description: 'Stabilizer configuration',
    documentationItems: [
      'Weight distribution',
      'Length combinations',
      'Angle adjustments',
      'Balance point effects'
    ]
  },
  {
    name: 'string',
    label: 'String & Cables',
    icon: 'fas fa-grip-lines',
    color: 'text-red-600 dark:text-red-400',
    description: 'String system setup',
    documentationItems: [
      'Serving applications',
      'Twist adjustments',
      'Stretch measurements',
      'Peep alignment'
    ]
  },
  {
    name: 'peep_sight',
    label: 'Peep Sight',
    icon: 'fas fa-dot-circle',
    color: 'text-teal-600 dark:text-teal-400',
    description: 'Peep sight positioning',
    documentationItems: [
      'Height positioning',
      'Rotation alignment',
      'Size selection',
      'Visibility optimization'
    ]
  },
  {
    name: 'other',
    label: 'Other Equipment',
    icon: 'fas fa-tools',
    color: 'text-gray-600 dark:text-gray-400',
    description: 'Miscellaneous equipment',
    documentationItems: [
      'Custom modifications',
      'Accessory installations',
      'Performance accessories',
      'Setup notes'
    ]
  }
]

// Available tuning guides for arrows
const availableTuningGuides = computed(() => [
  {
    id: 'paper_tuning',
    name: 'Paper Tuning',
    description: 'Analyze arrow tear patterns through paper for spine and clearance issues',
    estimatedTime: '15-20 minutes',
    icon: 'fas fa-file-alt',
    color: 'text-blue-600 dark:text-blue-400'
  },
  {
    id: 'bareshaft_tuning',
    name: 'Bareshaft Tuning', 
    description: 'Compare bare shaft vs fletched arrow grouping for spine validation',
    estimatedTime: '20-30 minutes',
    icon: 'fas fa-bullseye',
    color: 'text-green-600 dark:text-green-400'
  },
  {
    id: 'walkback_tuning',
    name: 'Walkback Tuning',
    description: 'Multi-distance shooting analysis for rest/centershot alignment',
    estimatedTime: '25-35 minutes',
    icon: 'fas fa-chart-line',
    color: 'text-purple-600 dark:text-purple-400'
  }
])

// Methods
const loadBowSetups = async () => {
  loading.value.bowSetups = true
  try {
    const response = await api.get('/bow-setups')
    // Handle response - it might be direct array or wrapped in setups property
    bowSetups.value = Array.isArray(response) ? response : (response.setups || [])
    console.log('Loaded bow setups:', bowSetups.value.length, 'setups')
  } catch (error) {
    console.error('Failed to load bow setups:', error)
    bowSetups.value = []
  } finally {
    loading.value.bowSetups = false
  }
}

const loadArrowsForSetup = async () => {
  if (!selectedBowSetup.value?.id) return
  
  loading.value.arrows = true
  try {
    const response = await api.get(`/bow-setups/${selectedBowSetup.value.id}/arrows`)
    // Handle response - it might be direct array or wrapped in arrows property
    setupArrows.value = Array.isArray(response) ? response : (response.arrows || [])
    console.log('Loaded arrows for setup:', setupArrows.value.length, 'arrows')
  } catch (error) {
    console.error('Failed to load arrows for setup:', error)
    setupArrows.value = []
  } finally {
    loading.value.arrows = false
  }
}

const selectBowSetup = (setup) => {
  selectedBowSetup.value = setup
  resetSelections(false) // Don't reset bow setup
  loadArrowsForSetup()
}

// Wizard navigation methods
const continueToStep = async (step) => {
  if (step <= currentStep.value) return
  
  currentStep.value = step
  
  // Auto-scroll to top with smooth animation
  await nextTick()
  if (wizardContainer.value) {
    wizardContainer.value.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start'
    })
  }
}

const goToPreviousStep = async () => {
  if (currentStep.value > 1) {
    currentStep.value--
    
    // Auto-scroll to top
    await nextTick()
    if (wizardContainer.value) {
      wizardContainer.value.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start'
      })
    }
  }
}

const editStep = async (step) => {
  currentStep.value = step
  
  // Auto-scroll to top
  await nextTick()
  if (wizardContainer.value) {
    wizardContainer.value.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start'
    })
  }
}

const resetWizard = () => {
  currentStep.value = 1
  resetSelections(true)
}

const selectTuningType = (type) => {
  selectionType.value = type
  selectedArrow.value = null
  selectedEquipmentCategory.value = null
}

const selectArrow = (arrow) => {
  selectedArrow.value = arrow
}

const selectEquipmentCategory = (category) => {
  selectedEquipmentCategory.value = category
}

const startTuningGuide = async (guide) => {
  if (!selectedBowSetup.value || !selectedArrow.value) return
  
  starting.value = true
  try {
    const sessionData = {
      bow_setup_id: selectedBowSetup.value.id,
      arrow_id: selectedArrow.value.arrow_id,
      arrow_length: selectedArrow.value.arrow_length,
      point_weight: selectedArrow.value.point_weight,
      guide_type: guide.id
    }
    
    const response = await api.post('/tuning-guides/start', sessionData)
    
    // Redirect directly to the new tuning session URLs based on guide type
    if (guide.id === 'paper_tuning') {
      router.push(`/tuning-session/paper/${response.session_id}`)
    } else if (guide.id === 'bareshaft_tuning') {
      router.push(`/tuning-session/bareshaft/${response.session_id}`)
    } else if (guide.id === 'walkback_tuning') {
      router.push(`/tuning-session/walkback/${response.session_id}`)
    } else {
      console.error('Unknown guide type:', guide.id)
    }
    
  } catch (error) {
    console.error('Failed to start tuning session:', error)
  } finally {
    starting.value = false
  }
}

const startEquipmentSetup = async () => {
  if (!selectedBowSetup.value || !selectedEquipmentCategory.value) return
  
  starting.value = true
  try {
    // Emit equipment setup event for parent to handle
    emit('equipment-setup-requested', {
      bow_setup: selectedBowSetup.value,
      equipment_category: selectedEquipmentCategory.value
    })
    
  } catch (error) {
    console.error('Failed to start equipment setup:', error)
  } finally {
    starting.value = false
  }
}

const resetSelections = (includeSetup = true) => {
  if (includeSetup) {
    selectedBowSetup.value = null
    setupArrows.value = []
  }
  selectedArrow.value = null
  selectedEquipmentCategory.value = null
  selectionType.value = 'arrow'
}

// Format utility functions
const formatBowType = (bowType) => {
  const types = {
    'compound': 'Compound',
    'recurve': 'Recurve', 
    'traditional': 'Traditional',
    'barebow': 'Barebow'
  }
  return types[bowType] || bowType
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'N/A'
  }
}

const getDisplaySpine = (arrowSetup) => {
  return arrowSetup.spine_value || arrowSetup.arrow?.spine || 'N/A'
}

const calculateTotalArrowWeight = (arrowSetup) => {
  if (arrowSetup.total_weight) return `${arrowSetup.total_weight}`
  
  // Calculate if we have individual components
  const arrowWeight = arrowSetup.arrow?.gpi_weight || 0
  const pointWeight = arrowSetup.point_weight || 0
  const nockWeight = arrowSetup.arrow?.nock_weight || 5 // Default nock weight
  const fletchingWeight = arrowSetup.arrow?.fletching_weight || 10 // Default fletching weight
  
  if (arrowWeight && pointWeight) {
    return `${Math.round(arrowWeight + pointWeight + nockWeight + fletchingWeight)}`
  }
  
  return null
}

// Watchers
watch(selectionType, () => {
  selectedArrow.value = null
  selectedEquipmentCategory.value = null
})

// Define emits
const emit = defineEmits(['session-started', 'equipment-setup-requested', 'cancel'])

// Lifecycle
onMounted(() => {
  loadBowSetups()
})
</script>

<style scoped>
/* Wizard Step Styles */
.wizard-step {
  @apply mb-8 transition-all duration-300;
}

.step-completed .step-header {
  @apply opacity-75 hover:opacity-100 cursor-pointer transition-opacity;
}

.step-completed .step-header:hover {
  @apply bg-gray-50 dark:bg-gray-700/50 rounded-lg p-2 -m-2;
}

.step-content {
  animation: slideInFromTop 0.5s ease-out;
}

@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Touch-friendly improvements */
.touch-manipulation {
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

/* Enhanced visual hierarchy */
.equipment-category-card:hover {
  transform: translateY(-2px);
}

.guide-card:hover {
  transform: translateY(-1px);
}

.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Mobile responsive adjustments */
@media (max-width: 640px) {
  .wizard-step {
    @apply mb-6;
  }
  
  .step-content {
    @apply px-2;
  }
}

/* Progress indicator animation */
.wizard-step .step-header div[class*="w-8 h-8"] {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Smooth scrolling enhancement */
html {
  scroll-behavior: smooth;
}

/* Loading states */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>