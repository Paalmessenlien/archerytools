<template>
  <div>
    <!-- Notification Toast -->
    <div v-if="notification.show" class="fixed top-4 right-4 z-50 transition-all duration-300">
      <div 
        :class="[
          'p-4 rounded-lg shadow-lg max-w-sm',
          notification.type === 'success' ? 'bg-green-500 text-white' : '',
          notification.type === 'error' ? 'bg-red-500 text-white' : '',
          notification.type === 'warning' ? 'bg-yellow-500 text-black' : ''
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i v-if="notification.type === 'success'" class="fas fa-check-circle mr-2"></i>
            <i v-if="notification.type === 'error'" class="fas fa-exclamation-circle mr-2"></i>
            <i v-if="notification.type === 'warning'" class="fas fa-exclamation-triangle mr-2"></i>
            <span class="text-sm">{{ notification.message }}</span>
          </div>
          <button @click="hideNotification" class="ml-4 opacity-70 hover:opacity-100">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Arrow Calculator</h1>
    </div>

    <!-- Bow Setup Loaded Notification -->
    <div v-if="selectedBowSetup" class="mb-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <i class="fas fa-crosshairs text-green-600 dark:text-green-400 mr-3"></i>
          <div>
            <h4 class="text-sm font-medium text-green-800 dark:text-green-200">Bow Setup Loaded</h4>
            <p class="text-xs text-green-700 dark:text-green-300 mt-1">
              {{ selectedBowSetup.name }} ({{ selectedBowSetup.bow_type || selectedBowSetup.bow_config?.bow_type }}, {{ selectedBowSetup.draw_weight || selectedBowSetup.bow_config?.draw_weight }}lbs) - Find arrows and add them to your setup
            </p>
          </div>
        </div>
        <CustomButton
          @click="clearSelectedSetup"
          variant="text"
          size="small"
          class="text-green-600 hover:bg-green-100 dark:text-green-400 dark:hover:bg-green-900"
        >
          <i class="fas fa-times"></i>
        </CustomButton>
      </div>
    </div>

    <!-- Bow Selection Section -->
    <div class="mb-6">
      <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
        <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-3">
          <i class="fas fa-crosshairs mr-2"></i>
          Bow Configuration
        </h3>
        
        <!-- Bow Setup Selector -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Bow Setup (Optional)
          </label>
          <md-filled-select 
            :value="selectedBowSetupId" 
            @change="loadBowSetup($event.target.value)"
            label="Choose from your saved bow setups"
            class="w-full"
          >
            <md-select-option value="">
              <div slot="headline">Manual Configuration</div>
            </md-select-option>
            <md-select-option v-for="setup in userBowSetups" :key="setup.id" :value="setup.id.toString()">
              <div slot="headline">{{ setup.name }} ({{ setup.bow_type }}, {{ setup.draw_weight }}lbs)</div>
            </md-select-option>
          </md-filled-select>
        </div>

        <!-- Manual Configuration (shown when no bow setup selected or for overrides) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Bow Type (hidden when bow setup is selected) -->
          <div v-if="!selectedBowSetup">
            <md-filled-select
              ref="bowTypeSelect"
              label="Bow Type"
              :value="bowConfig.bow_type"
              @change="updateBowConfig({ bow_type: $event.target.value })"
              class="w-full"
            >
              <md-select-option value="compound">
                <div slot="headline">Compound</div>
              </md-select-option>
              <md-select-option value="recurve">
                <div slot="headline">Recurve</div>
              </md-select-option>
              <md-select-option value="longbow">
                <div slot="headline">Longbow</div>
              </md-select-option>
              <md-select-option value="traditional">
                <div slot="headline">Traditional</div>
              </md-select-option>
            </md-filled-select>
          </div>

          <!-- Draw Weight (hidden when bow setup is selected) -->
          <div v-if="!selectedBowSetup">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Draw Weight: <span class="font-semibold text-primary">{{ bowConfig.draw_weight }} lbs</span>
            </label>
            <div class="flex items-center gap-3">
              <input
                type="range"
                min="20"
                max="80"
                step="0.5"
                :value="bowConfig.draw_weight"
                @input="updateBowConfig({ draw_weight: parseFloat($event.target.value) })"
                class="flex-1 h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider-touch"
              />
              <input
                type="number"
                :value="bowConfig.draw_weight"
                @input="updateBowConfig({ draw_weight: parseFloat($event.target.value) })"
                min="20"
                max="80"
                step="0.5"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 form-input touch-target"
              />
            </div>
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
              <span>20 lbs</span>
              <span>80 lbs</span>
            </div>
          </div>

          <!-- Arrow Material (always shown) -->
          <div>
            <md-filled-select
              ref="arrowMaterialSelect"
              label="Arrow Material"
              :value="bowConfig.arrow_material || 'carbon'"
              @change="updateBowConfig({ arrow_material: $event.target.value })"
              class="w-full"
            >
              <md-select-option value="">
                <div slot="headline">All Materials</div>
              </md-select-option>
              <md-select-option value="carbon">
                <div slot="headline">Carbon</div>
              </md-select-option>
              <md-select-option value="carbon-aluminum">
                <div slot="headline">Carbon / Aluminum</div>
              </md-select-option>
              <md-select-option value="aluminum">
                <div slot="headline">Aluminum</div>
              </md-select-option>
              <md-select-option value="wood">
                <div slot="headline">Wood</div>
              </md-select-option>
              <md-select-option value="fiberglass">
                <div slot="headline">Fiberglass</div>
              </md-select-option>
            </md-filled-select>
          </div>

          <!-- Arrow Length (always shown) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Arrow Length: <span class="font-semibold text-primary">{{ bowConfig.arrow_length || 29 }}"</span>
            </label>
            <div class="flex items-center gap-3">
              <input
                type="range"
                min="24"
                max="34"
                step="0.5"
                :value="bowConfig.arrow_length || 29"
                @input="updateBowConfig({ arrow_length: parseFloat($event.target.value) })"
                class="flex-1 h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider-touch"
              />
              <input
                type="number"
                :value="bowConfig.arrow_length || 29"
                @input="updateBowConfig({ arrow_length: parseFloat($event.target.value) })"
                min="24"
                max="34"
                step="0.5"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 form-input touch-target"
              />
            </div>
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
              <span>24"</span>
              <span>34"</span>
            </div>
          </div>

          <!-- Point Weight (always shown) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Point Weight: <span class="font-semibold text-primary">{{ bowConfig.point_weight || 125 }} gn</span>
            </label>
            <div class="flex items-center gap-3">
              <input
                type="range"
                min="40"
                max="300"
                step="5"
                :value="bowConfig.point_weight || 125"
                @input="updateBowConfig({ point_weight: parseFloat($event.target.value) })"
                class="flex-1 h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider-touch"
              />
              <input
                type="number"
                :value="bowConfig.point_weight || 125"
                @input="updateBowConfig({ point_weight: parseFloat($event.target.value) })"
                min="40"
                max="300"
                step="5"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 form-input touch-target"
              />
            </div>
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
              <span>40 gn</span>
              <span>300 gn</span>
            </div>
          </div>
        </div>

        <!-- Arrow Components Section -->
        <div class="mt-4">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              <i class="fas fa-puzzle-piece mr-2"></i>
              Arrow Components
            </h4>
            <CustomButton
              @click="showComponents = !showComponents"
              variant="text"
              size="small"
              class="text-blue-600 hover:bg-blue-100 dark:text-blue-400 dark:hover:bg-blue-900 touch-target"
            >
              <i class="fas transition-transform" :class="showComponents ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
              <span class="ml-2">{{ showComponents ? 'Hide' : 'Show' }} Details</span>
            </CustomButton>
          </div>

          <div v-if="showComponents" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <!-- Insert Weight -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Insert Weight: <span class="font-semibold text-primary">{{ bowConfig.insert_weight || 0 }} gn</span>
              </label>
              <div class="mb-2">
                <md-filled-select 
                  :value="bowConfig.insert_weight === 0 ? 'none' : 'custom'" 
                  @change="handleInsertChange($event.target.value)"
                  label="Insert Type"
                  class="w-full"
                >
                  <md-select-option value="none">No Insert</md-select-option>
                  <md-select-option value="custom">Custom Weight</md-select-option>
                </md-filled-select>
              </div>
              <div v-if="bowConfig.insert_weight > 0">
                <md-slider
                  min="5"
                  max="30"
                  step="0.5"
                  :value="bowConfig.insert_weight"
                  @input="updateBowConfig({ insert_weight: parseFloat($event.target.value) })"
                  labeled
                  class="w-full"
                ></md-slider>
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>5 gn</span>
                  <span>30 gn</span>
                </div>
              </div>
            </div>

            <!-- Vane Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Vane Type
              </label>
              <md-filled-select 
                :value="bowConfig.vane_type || 'plastic'" 
                @change="handleVaneTypeChange($event.target.value)"
                label="Vane Type"
                class="w-full"
              >
                <md-select-option value="plastic">Plastic Vanes</md-select-option>
                <md-select-option value="feather">Natural Feathers</md-select-option>
                <md-select-option value="spin">Spin Vanes</md-select-option>
              </md-filled-select>
            </div>

            <!-- Vane Length -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Vane Length: <span class="font-semibold text-primary">{{ bowConfig.vane_length || 4 }}"</span>
              </label>
              <md-slider
                min="1"
                max="6"
                step="0.25"
                :value="bowConfig.vane_length || 4"
                @input="updateBowConfig({ vane_length: parseFloat($event.target.value) })"
                labeled
                class="w-full"
              ></md-slider>
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>1"</span>
                <span>6"</span>
              </div>
            </div>

            <!-- Vane Weight Per -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Vane Weight (Each): <span class="font-semibold text-primary">{{ getVaneWeight() }} gn</span>
              </label>
              <div class="mb-2">
                <md-filled-select 
                  :value="bowConfig.vane_weight_override ? 'custom' : 'auto'" 
                  @change="handleVaneWeightModeChange($event.target.value)"
                  label="Weight Mode"
                  class="w-full"
                >
                  <md-select-option value="auto">Auto Calculate</md-select-option>
                  <md-select-option value="custom">Manual Override</md-select-option>
                </md-filled-select>
              </div>
              <div v-if="!bowConfig.vane_weight_override" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Calculated based on type and length
              </div>
              <div v-if="bowConfig.vane_weight_override">
                <md-slider
                  min="1"
                  max="15"
                  step="0.25"
                  :value="bowConfig.vane_weight_per || 5"
                  @input="updateBowConfig({ vane_weight_per: parseFloat($event.target.value) })"
                  labeled
                  class="w-full"
                ></md-slider>
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>1 gn</span>
                  <span>15 gn</span>
                </div>
              </div>
            </div>

            <!-- Number of Vanes -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Number of Vanes: <span class="font-semibold text-primary">{{ bowConfig.number_of_vanes || 3 }}</span>
              </label>
              <md-slider
                min="2"
                max="6"
                step="1"
                :value="bowConfig.number_of_vanes || 3"
                @input="updateBowConfig({ number_of_vanes: parseInt($event.target.value) })"
                labeled
                ticks
                class="w-full"
              ></md-slider>
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>2</span>
                <span>6</span>
              </div>
            </div>

            <!-- Bushing Weight -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Bushing Weight: <span class="font-semibold text-primary">{{ bowConfig.bushing_weight || 0 }} gn</span>
              </label>
              <div class="mb-2">
                <md-filled-select 
                  :value="bowConfig.bushing_weight === 0 ? 'none' : 'custom'" 
                  @change="handleBushingChange($event.target.value)"
                  label="Bushing Type"
                  class="w-full"
                >
                  <md-select-option value="none">No Bushing</md-select-option>
                  <md-select-option value="custom">Custom Weight</md-select-option>
                </md-filled-select>
              </div>
              <div v-if="bowConfig.bushing_weight > 0">
                <md-slider
                  min="1"
                  max="15"
                  step="0.25"
                  :value="bowConfig.bushing_weight"
                  @input="updateBowConfig({ bushing_weight: parseFloat($event.target.value) })"
                  labeled
                  class="w-full"
                ></md-slider>
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>1 gn</span>
                  <span>15 gn</span>
                </div>
              </div>
            </div>

            <!-- Nock Weight -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nock Weight: <span class="font-semibold text-primary">{{ bowConfig.nock_weight || 10 }} gn</span>
              </label>
              <md-slider
                min="5"
                max="25"
                step="0.5"
                :value="bowConfig.nock_weight || 10"
                @input="updateBowConfig({ nock_weight: parseFloat($event.target.value) })"
                labeled
                class="w-full"
              ></md-slider>
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>5 gn</span>
                <span>25 gn</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>



    <!-- Calculated Specifications -->
    <md-elevated-card class="mb-6 light-surface light-elevation">
      <div class="p-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">
          <i class="fas fa-calculator" style="margin-right: 8px; color: #6366f1;"></i>
          Calculated Specifications
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="flex flex-col">
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">
              <i class="fas fa-bullseye" style="margin-right: 6px; color: #6366f1;"></i>
              Recommended Spine:
            </p>
            <p class="font-semibold text-xl text-primary">{{ recommendedSpine || 'Calculating...' }}</p>
            <p v-if="bowConfig.arrow_material && bowConfig.arrow_material === 'wood'" class="text-xs text-orange-600 dark:text-orange-400 mt-1">
              <i class="fas fa-tree mr-1"></i>
              Wood spine in pounds (traditional measurement)
            </p>
          </div>
          <div class="flex flex-col">
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">
              <i class="fas fa-crosshairs" style="margin-right: 6px; color: #7c3aed;"></i>
              Arrow Setup:
            </p>
            <p class="font-semibold text-gray-900 dark:text-gray-100">{{ arrowSetupDescription }}</p>
          </div>
          <div class="flex flex-col">
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">
              <i class="fas fa-weight-hanging" style="margin-right: 6px; color: #059669;"></i>
              Total Component Weight:
            </p>
            <p class="font-semibold text-xl text-green-600">{{ calculateTotalComponentWeight() }} gn</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Includes all components
            </p>
          </div>
        </div>

        <!-- Enhanced Spine Calculation Results -->
        <div v-if="enhancedSpineResult" class="mt-4 p-3 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <h4 class="text-sm font-semibold text-green-900 dark:text-green-200 mb-2">
            <i class="fas fa-chart-line mr-2"></i>
            Enhanced Calculation Results
          </h4>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <!-- Effective Bow Weight -->
            <div>
              <p class="text-xs text-green-700 dark:text-green-300 mb-1">Effective Bow Weight:</p>
              <p class="font-medium text-green-900 dark:text-green-100">{{ enhancedSpineResult.effective_bow_weight }} lbs</p>
              <div v-if="enhancedSpineResult.adjustments_applied && enhancedSpineResult.adjustments_applied.length > 0" class="text-xs text-green-600 dark:text-green-400 mt-1">
                <div v-for="adjustment in enhancedSpineResult.adjustments_applied" :key="adjustment">
                  • {{ adjustment }}
                </div>
              </div>
            </div>
            
            <!-- Calculation Source -->
            <div>
              <p class="text-xs text-green-700 dark:text-green-300 mb-1">Calculation Source:</p>
              <div v-if="enhancedSpineResult.manufacturer_recommendation">
                <p class="font-medium text-green-900 dark:text-green-100">
                  {{ enhancedSpineResult.manufacturer_recommendation.manufacturer }} 
                  {{ enhancedSpineResult.manufacturer_recommendation.model }}
                </p>
                <p class="text-xs text-green-600 dark:text-green-400 mt-1">
                  Professional manufacturer spine chart
                </p>
              </div>
              <div v-else>
                <p class="font-medium text-green-900 dark:text-green-100">Generic Calculation</p>
                <p class="text-xs text-green-600 dark:text-green-400 mt-1">
                  Standard spine calculation method
                </p>
              </div>
            </div>
          </div>
          
          <!-- Calculation Notes -->
          <div v-if="enhancedSpineResult.calculation_notes && enhancedSpineResult.calculation_notes.length > 0" class="mt-3 pt-3 border-t border-green-200 dark:border-green-700">
            <p class="text-xs text-green-700 dark:text-green-300 mb-1">Notes:</p>
            <div class="text-xs text-green-600 dark:text-green-400 space-y-1">
              <div v-for="note in enhancedSpineResult.calculation_notes" :key="note">
                • {{ note }}
              </div>
            </div>
          </div>
        </div>

        <!-- Calculation Loading State -->
        <div v-else-if="isCalculatingEnhancedSpine" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent dark:border-blue-400"></div>
            <span class="ml-2 text-sm text-blue-700 dark:text-blue-300">Calculating enhanced spine recommendation...</span>
          </div>
        </div>
        
        <!-- Material-specific calculation notes -->
        <div v-if="bowConfig.arrow_material && bowConfig.arrow_material === 'wood'" class="mt-3 p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
          <p class="text-sm text-orange-800 dark:text-orange-200">
            <i class="fas fa-info-circle mr-2"></i>
            <strong>Wood Arrow Calculation:</strong> Uses traditional wood arrow spine charts with pound-based measurements. 
            This calculation method works for any bow type when wood arrows are selected.
          </p>
        </div>
        
        <div v-else-if="!bowConfig.arrow_material || bowConfig.arrow_material === ''" class="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p class="text-sm text-blue-800 dark:text-blue-200">
            <i class="fas fa-info-circle mr-2"></i>
            <strong>All Materials:</strong> Shows recommendations for all arrow materials. 
            Spine calculations use standard carbon spine numbers based on your bow type.
          </p>
        </div>

        <!-- Match Summary -->
        <div v-if="hasMatchDistribution" class="mt-4">
          <div class="flex items-center justify-between gap-4">
            <h4 class="text-base font-medium text-gray-900 dark:text-gray-100">
              <i class="fas fa-chart-bar mr-2 text-blue-600"></i>
              Match Summary
            </h4>
            <button
              @click="showMatchSummary = !showMatchSummary"
              class="px-2 py-1 text-xs text-blue-600 hover:bg-blue-100 dark:text-blue-400 dark:hover:bg-blue-900 rounded-md transition-colors touch-target"
            >
              <i class="fas transition-transform text-xs" :class="showMatchSummary ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
              <span class="ml-1">{{ showMatchSummary ? 'Hide' : 'Show' }}</span>
            </button>
          </div>
          
          <!-- Match Distribution Content -->
          <div v-if="showMatchSummary" class="mt-2 pt-2">
            <div class="border-t border-gray-200 dark:border-gray-700 mb-2"></div>
            
            <!-- Compact Match Distribution Grid -->
            <div class="grid grid-cols-5 gap-1 mb-2">
              <!-- Perfect Matches -->
              <div class="text-center p-1 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                <div class="text-lg font-bold text-green-600 dark:text-green-400">{{ matchDistribution.perfect }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400">Perfect</div>
              </div>
              
              <!-- Excellent Matches -->
              <div class="text-center p-1 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ matchDistribution.excellent }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400">Excellent</div>
              </div>
              
              <!-- Good Matches -->
              <div class="text-center p-1 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                <div class="text-lg font-bold text-indigo-600 dark:text-indigo-400">{{ matchDistribution.good }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400">Good</div>
              </div>
              
              <!-- Fair Matches -->
              <div class="text-center p-1 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                <div class="text-lg font-bold text-orange-600 dark:text-orange-400">{{ matchDistribution.fair }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400">Fair</div>
              </div>
              
              <!-- Acceptable Matches -->
              <div class="text-center p-1 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                <div class="text-lg font-bold text-gray-600 dark:text-gray-400">{{ matchDistribution.acceptable }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400">Acceptable</div>
              </div>
            </div>
            
            <!-- Compact Visual Bar -->
            <div class="h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden flex">
              <div 
                v-if="matchDistribution.perfect > 0"
                class="bg-green-500 transition-all duration-500"
                :style="`width: ${(matchDistribution.perfect / matchDistribution.total) * 100}%`"
              ></div>
              <div 
                v-if="matchDistribution.excellent > 0"
                class="bg-blue-500 transition-all duration-500"
                :style="`width: ${(matchDistribution.excellent / matchDistribution.total) * 100}%`"
              ></div>
              <div 
                v-if="matchDistribution.good > 0"
                class="bg-indigo-500 transition-all duration-500"
                :style="`width: ${(matchDistribution.good / matchDistribution.total) * 100}%`"
              ></div>
              <div 
                v-if="matchDistribution.fair > 0"
                class="bg-orange-500 transition-all duration-500"
                :style="`width: ${(matchDistribution.fair / matchDistribution.total) * 100}%`"
              ></div>
              <div 
                v-if="matchDistribution.acceptable > 0"
                class="bg-gray-500 transition-all duration-500"
                :style="`width: ${(matchDistribution.acceptable / matchDistribution.total) * 100}%`"
              ></div>
            </div>
          </div>
        </div>

        <!-- Advanced Filters -->
        <div class="mt-4">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <CustomButton
              @click="arrowFiltersStore.toggleAdvancedFilters()"
              variant="text"
              class="text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900 touch-target"
            >
              <i class="fas transition-transform" :class="showAdvancedFilters ? 'fa-chevron-up' : 'fa-chevron-down'" style="margin-right: 8px;"></i>
              {{ showAdvancedFilters ? 'Hide' : 'Show' }} Advanced Filters
            </CustomButton>
            
            <div class="flex items-center gap-4">
              <!-- Clear Filters Button -->
              <CustomButton
                v-if="hasActiveFilters" 
                @click="handleClearFilters"
                variant="text"
                size="small"
                class="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900 touch-target"
              >
                <i class="fas fa-times-circle mr-2"></i>
                Clear Filters
              </CustomButton>
            </div>
          </div>
        
          <!-- Advanced Filters Content -->
          <div v-if="showAdvancedFilters" class="mt-4 pt-3">
            <div class="border-t border-gray-200 dark:border-gray-700 mb-3"></div>
            
            <!-- Primary Filters Row -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
              <!-- Manufacturer Filter -->
              <md-filled-select :value="filters.manufacturer" @change="arrowFiltersStore.updateFilter('manufacturer', $event.target.value)" label="Manufacturer">
                <md-select-option value="">
                  <div slot="headline">All Manufacturers</div>
                </md-select-option>
                <md-select-option v-for="mfr in availableManufacturers" :key="mfr" :value="mfr">
                  <div slot="headline">{{ mfr }}</div>
                </md-select-option>
              </md-filled-select>
              
              <!-- Match Quality Filter -->
              <md-filled-select :value="filters.match_quality" @change="arrowFiltersStore.updateFilter('match_quality', $event.target.value)" label="Match Quality">
                <md-select-option value="">
                  <div slot="headline">All Matches</div>
                </md-select-option>
                <md-select-option value="100">
                  <div slot="headline">100% Matches Only</div>
                </md-select-option>
                <md-select-option value="90">
                  <div slot="headline">90%+ Matches</div>
                </md-select-option>
                <md-select-option value="80">
                  <div slot="headline">80%+ Matches</div>
                </md-select-option>
              </md-filled-select>
            </div>
            
            <!-- Search Bar -->
            <div class="mb-3">
              <md-outlined-text-field 
                :value="filters.search"
                @input="arrowFiltersStore.updateFilter('search', $event.target.value)"
                label="Search arrows..."
                type="search"
                class="w-full"
              >
                <i class="fas fa-search" slot="leading-icon" style="color: #6b7280;"></i>
              </md-outlined-text-field>
            </div>
            
            <!-- Sort By -->
            <div class="mb-3">
              <md-filled-select :value="filters.sortBy" @change="arrowFiltersStore.updateFilter('sortBy', $event.target.value)" label="Sort By" class="w-full md:w-1/2">
                <md-select-option value="compatibility">
                  <div slot="headline">Best Match</div>
                </md-select-option>
                <md-select-option value="manufacturer">
                  <div slot="headline">Manufacturer</div>
                </md-select-option>
                <md-select-option value="diameter_asc">
                  <div slot="headline">Diameter (Small to Large)</div>
                </md-select-option>
                <md-select-option value="diameter_desc">
                  <div slot="headline">Diameter (Large to Small)</div>
                </md-select-option>
                <md-select-option value="weight_asc">
                  <div slot="headline">Weight (Light to Heavy)</div>
                </md-select-option>
                <md-select-option value="weight_desc">
                  <div slot="headline">Weight (Heavy to Light)</div>
                </md-select-option>
                <md-select-option value="material">
                  <div slot="headline">Material</div>
                </md-select-option>
              </md-filled-select>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
              <!-- Diameter Range Dropdown -->
              <md-filled-select :value="filters.diameter_range" @change="arrowFiltersStore.updateFilter('diameter_range', $event.target.value)" label="Diameter Range">
                <md-select-option value="">
                  <div slot="headline">All Diameters</div>
                </md-select-option>
                <md-select-option value="0.200-0.250">
                  <div slot="headline">0.200" - 0.250"</div>
                </md-select-option>
                <md-select-option value="0.250-0.300">
                  <div slot="headline">0.250" - 0.300"</div>
                </md-select-option>
                <md-select-option value="0.300-0.350">
                  <div slot="headline">0.300" - 0.350"</div>
                </md-select-option>
                <md-select-option value="0.350-0.400">
                  <div slot="headline">0.350" - 0.400"</div>
                </md-select-option>
                <md-select-option value="0.400-0.450">
                  <div slot="headline">0.400" - 0.450"</div>
                </md-select-option>
              </md-filled-select>
              
              <!-- Weight Range -->
              <md-outlined-text-field 
                :value="filters.weight_min"
                @input="arrowFiltersStore.updateFilter('weight_min', $event.target.value)"
                type="number" 
                step="0.1"
                label="Min Weight (GPI)"
              ></md-outlined-text-field>
              <md-outlined-text-field 
                :value="filters.weight_max"
                @input="arrowFiltersStore.updateFilter('weight_max', $event.target.value)"
                type="number" 
                step="0.1"
                label="Max Weight (GPI)"
              ></md-outlined-text-field>
            </div>
            
            <!-- Professional Spine Calculation -->
            <div class="mb-3">
              <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-200 dark:border-green-800">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-lg font-semibold text-green-900 dark:text-green-200">
                    <i class="fas fa-chart-line mr-2"></i>
                    Professional Spine Calculation
                  </h4>
                  <CustomButton
                    @click="showProfessionalSpine = !showProfessionalSpine"
                    variant="text"
                    size="small"
                    class="text-green-600 hover:bg-green-100 dark:text-green-400 dark:hover:bg-green-900 touch-target"
                  >
                    <i class="fas transition-transform" :class="showProfessionalSpine ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                    <span class="ml-2">{{ showProfessionalSpine ? 'Hide' : 'Show' }}</span>
                  </CustomButton>
                </div>
                
                <div v-if="showProfessionalSpine">
                  <ManufacturerSpineChartSelector
                    :bow-type="bowConfig.bow_type"
                    @selection-change="handleSpineChartSelection"
                  />
                </div>
              </div>
            </div>

            <!-- Spine Conversion Widget -->
            <div>
              <SpineConversionWidget />
            </div>
          </div>
        </div>

        <!-- Performance Dashboard Toggle -->
        <div class="mt-6">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              <i class="fas fa-chart-line mr-2 text-indigo-600"></i>
              Advanced Performance Analysis
            </h3>
            <CustomButton
              @click="togglePerformanceDashboard"
              :class="showPerformanceDashboard ? 'bg-indigo-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'"
              class="transition-all duration-200"
            >
              <i class="fas transition-transform" :class="showPerformanceDashboard ? 'fa-chart-area' : 'fa-analytics'"></i>
              <span class="ml-2">{{ showPerformanceDashboard ? 'Hide Analysis' : 'Show Analysis' }}</span>
            </CustomButton>
          </div>
        </div>
      </div>
    </md-elevated-card>

    <!-- Enhanced Performance Dashboard -->
    <div v-if="showPerformanceDashboard" class="mt-6">
      <md-elevated-card class="light-surface light-elevation">
        <div class="p-6">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
            <i class="fas fa-tachometer-alt mr-3 text-indigo-600"></i>
            Comprehensive Performance Analysis
          </h3>

          <!-- Performance Summary -->
          <div v-if="comprehensivePerformance" class="mb-8 p-4 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-semibold text-indigo-900 dark:text-indigo-200">
                <i class="fas fa-star mr-2"></i>
                Overall Performance Score
              </h4>
              <div class="text-3xl font-bold text-indigo-600">
                {{ comprehensivePerformance.performance_summary.overall_score }}/100
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-indigo-700 dark:text-indigo-300 mb-2">Primary Recommendation:</p>
                <p class="font-medium text-indigo-900 dark:text-indigo-100">
                  {{ comprehensivePerformance.performance_summary.primary_recommendation }}
                </p>
              </div>
              <div>
                <p class="text-sm text-indigo-700 dark:text-indigo-300 mb-2">Estimated Speed:</p>
                <p class="font-medium text-indigo-900 dark:text-indigo-100">
                  {{ comprehensivePerformance.performance_summary.arrow_speed_fps }} fps
                </p>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Enhanced FOC Analysis -->
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  <i class="fas fa-balance-scale text-green-600 mr-2"></i>
                  FOC Analysis
                </h4>
                <CustomButton
                  @click="calculateEnhancedFoc"
                  :disabled="isCalculatingFoc"
                  size="small"
                  variant="text"
                  class="text-green-600 hover:bg-green-50 dark:hover:bg-green-900"
                >
                  <i class="fas fa-sync" :class="{ 'fa-spin': isCalculatingFoc }"></i>
                </CustomButton>
              </div>

              <div v-if="isCalculatingFoc" class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-2 border-green-600 border-t-transparent"></div>
                <span class="ml-3 text-sm text-gray-600 dark:text-gray-400">Calculating FOC...</span>
              </div>

              <div v-else-if="enhancedFocResult" class="space-y-4">
                <div class="text-center">
                  <div class="text-3xl font-bold text-green-600">
                    {{ enhancedFocResult.foc_percentage }}%
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    Current FOC
                  </div>
                  <div class="mt-2">
                    <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                          :class="getFocStatusClass(enhancedFocResult.foc_status)">
                      {{ getFocStatusText(enhancedFocResult.foc_status) }}
                    </span>
                  </div>
                </div>

                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Performance Metrics</h5>
                  <div class="grid grid-cols-2 gap-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-600 dark:text-gray-400">Stability:</span>
                      <span class="font-medium">{{ enhancedFocResult.foc_analysis.stability }}/10</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600 dark:text-gray-400">Accuracy:</span>
                      <span class="font-medium">{{ enhancedFocResult.foc_analysis.accuracy }}/10</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600 dark:text-gray-400">Penetration:</span>
                      <span class="font-medium">{{ enhancedFocResult.foc_analysis.penetration }}/10</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600 dark:text-gray-400">Wind Resistance:</span>
                      <span class="font-medium">{{ enhancedFocResult.foc_analysis.wind_resistance }}/10</span>
                    </div>
                  </div>
                </div>

                <div v-if="enhancedFocResult.optimization" class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                  <h5 class="font-medium text-blue-900 dark:text-blue-200 mb-2">Optimization</h5>
                  <div class="text-sm text-blue-800 dark:text-blue-300">
                    <p v-if="enhancedFocResult.optimization.feasible">
                      <strong>Optimal Point Weight:</strong> {{ enhancedFocResult.optimization.optimal_point_weight }}gr
                      <span class="text-xs block mt-1">
                        ({{ enhancedFocResult.optimization.point_weight_change > 0 ? '+' : '' }}{{ enhancedFocResult.optimization.point_weight_change }}gr change)
                      </span>
                    </p>
                    <p v-else class="text-orange-700 dark:text-orange-300">
                      Large adjustment needed - consider alternative modifications
                    </p>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-8">
                <i class="fas fa-calculator text-4xl text-gray-300 dark:text-gray-600 mb-3"></i>
                <p class="text-sm text-gray-500 dark:text-gray-400">Click refresh to calculate enhanced FOC analysis</p>
              </div>
            </div>

            <!-- Ballistics Analysis -->
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  <i class="fas fa-crosshairs text-red-600 mr-2"></i>
                  Ballistics
                </h4>
                <CustomButton
                  @click="calculateBallistics"
                  :disabled="isCalculatingBallistics"
                  size="small"
                  variant="text"
                  class="text-red-600 hover:bg-red-50 dark:hover:bg-red-900"
                >
                  <i class="fas fa-sync" :class="{ 'fa-spin': isCalculatingBallistics }"></i>
                </CustomButton>
              </div>

              <div v-if="isCalculatingBallistics" class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-2 border-red-600 border-t-transparent"></div>
                <span class="ml-3 text-sm text-gray-600 dark:text-gray-400">Calculating trajectory...</span>
              </div>

              <div v-else-if="ballisticsResult" class="space-y-4">
                <div class="text-center">
                  <div class="text-2xl font-bold text-red-600">
                    {{ ballisticsResult.ballistic_coefficient }}
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    Ballistic Coefficient
                  </div>
                </div>

                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Performance at Distance</h5>
                  <div class="space-y-2 text-sm">
                    <div v-for="(data, distance) in ballisticsResult.performance_metrics.performance_at_distance" 
                         :key="distance" class="flex justify-between">
                      <span class="text-gray-600 dark:text-gray-400">{{ distance }}:</span>
                      <span class="font-medium">{{ data.velocity_fps }}fps, {{ data.kinetic_energy }}ft-lbs</span>
                    </div>
                  </div>
                </div>

                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3">
                  <h5 class="font-medium text-orange-900 dark:text-orange-200 mb-2">Flight Characteristics</h5>
                  <div class="text-sm text-orange-800 dark:text-orange-300">
                    <p><strong>Max Range:</strong> {{ ballisticsResult.performance_metrics.max_effective_range_yards }} yards</p>
                    <p><strong>Flatness Score:</strong> {{ ballisticsResult.performance_metrics.trajectory_flatness_score }}/100</p>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-8">
                <i class="fas fa-chart-area text-4xl text-gray-300 dark:text-gray-600 mb-3"></i>
                <p class="text-sm text-gray-500 dark:text-gray-400">Click refresh to calculate ballistics analysis</p>
              </div>
            </div>

            <!-- Performance Summary -->
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  <i class="fas fa-award text-purple-600 mr-2"></i>
                  Performance
                </h4>
                <CustomButton
                  @click="calculateComprehensivePerformance"
                  :disabled="isCalculatingPerformance"
                  size="small"
                  variant="text"
                  class="text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900"
                >
                  <i class="fas fa-sync" :class="{ 'fa-spin': isCalculatingPerformance }"></i>
                </CustomButton>
              </div>

              <div v-if="isCalculatingPerformance" class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-2 border-purple-600 border-t-transparent"></div>
                <span class="ml-3 text-sm text-gray-600 dark:text-gray-400">Analyzing performance...</span>
              </div>

              <div v-else-if="comprehensivePerformance" class="space-y-4">
                <div class="text-center">
                  <div class="text-3xl font-bold text-purple-600">
                    {{ comprehensivePerformance.penetration_analysis.penetration_score }}
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    Penetration Score
                  </div>
                  <div class="mt-2">
                    <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                          :class="getPenetrationClass(comprehensivePerformance.penetration_analysis.category)">
                      {{ comprehensivePerformance.penetration_analysis.category }}
                    </span>
                  </div>
                </div>

                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Key Strengths</h5>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li v-for="strength in comprehensivePerformance.performance_summary.key_strengths" 
                        :key="strength" class="flex items-start">
                      <i class="fas fa-check text-green-500 mr-2 mt-0.5 text-xs"></i>
                      <span>{{ strength }}</span>
                    </li>
                  </ul>
                </div>

                <div v-if="comprehensivePerformance.performance_summary.improvement_areas.length > 0" 
                     class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3">
                  <h5 class="font-medium text-yellow-900 dark:text-yellow-200 mb-2">Improvement Areas</h5>
                  <ul class="text-sm text-yellow-800 dark:text-yellow-300 space-y-1">
                    <li v-for="area in comprehensivePerformance.performance_summary.improvement_areas" 
                        :key="area" class="flex items-start">
                      <i class="fas fa-wrench text-yellow-500 mr-2 mt-0.5 text-xs"></i>
                      <span>{{ area }}</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div v-else class="text-center py-8">
                <i class="fas fa-trophy text-4xl text-gray-300 dark:text-gray-600 mb-3"></i>
                <p class="text-sm text-gray-500 dark:text-gray-400">Click refresh to analyze comprehensive performance</p>
              </div>
            </div>
          </div>

          <!-- Comprehensive Analysis Button -->
          <div class="mt-6 text-center">
            <CustomButton
              @click="calculateAllPerformanceMetrics"
              :disabled="isCalculatingFoc || isCalculatingBallistics || isCalculatingPerformance"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3"
            >
              <i class="fas fa-calculator mr-2"></i>
              Calculate Complete Analysis
            </CustomButton>
          </div>
        </div>
      </md-elevated-card>
    </div>

    <!-- Arrow Recommendations -->
    <div class="mt-6 arrow-recommendations">
      <ArrowRecommendationsList 
        :bow-config="bowConfig"
        :show-search-filters="true"
        :selected-bow-setup="selectedBowSetup"
        @arrow-added-to-setup="handleArrowAddedToSetup"
        @error="handleError"
        @recommendations-updated="handleRecommendationsUpdated"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBowConfigStore } from '~/stores/bowConfig'
import { useBowSetupPickerStore } from '~/stores/bowSetupPicker'
import { useArrowFiltersStore } from '~/stores/arrowFilters'
import ManufacturerSpineChartSelector from '~/components/ManufacturerSpineChartSelector.vue'
import SpineConversionWidget from '~/components/SpineConversionWidget.vue'
import CustomButton from '~/components/CustomButton.vue'

// API
const api = useApi()
const { user, fetchBowSetups } = useAuth()

const bowConfigStore = useBowConfigStore()
const bowSetupPickerStore = useBowSetupPickerStore()
const arrowFiltersStore = useArrowFiltersStore()

// Reactive references from stores
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)
const arrowSetupDescription = computed(() => bowConfigStore.arrowSetupDescription)

// Enhanced performance analysis state
const enhancedFocResult = ref(null)
const isCalculatingFoc = ref(false)
const ballisticsResult = ref(null)
const isCalculatingBallistics = ref(false)
const comprehensivePerformance = ref(null)
const isCalculatingPerformance = ref(false)
const showPerformanceDashboard = ref(false)

// Helper functions for performance dashboard
const togglePerformanceDashboard = () => {
  showPerformanceDashboard.value = !showPerformanceDashboard.value
  if (showPerformanceDashboard.value && !enhancedFocResult.value) {
    calculateAllPerformanceMetrics()
  }
}

const calculateAllPerformanceMetrics = async () => {
  try {
    // Calculate all three metrics in parallel for comprehensive analysis
    await Promise.all([
      calculateEnhancedFoc(),
      calculateBallistics(),
      calculateComprehensivePerformance()
    ])
  } catch (error) {
    console.error('Error calculating performance metrics:', error)
  }
}

const getFocStatusClass = (focResult) => {
  if (!focResult || !focResult.foc_analysis) return 'text-gray-500'
  const analysis = focResult.foc_analysis
  if (analysis.is_optimal) return 'text-green-600 dark:text-green-400'
  if (analysis.performance_impact === 'minimal') return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getFocStatusText = (focResult) => {
  if (!focResult || !focResult.foc_analysis) return 'Not calculated'
  const analysis = focResult.foc_analysis
  if (analysis.is_optimal) return 'Optimal'
  if (analysis.performance_impact === 'minimal') return 'Good'
  return 'Needs adjustment'
}

const getPenetrationClass = (penetrationResult) => {
  if (!penetrationResult) return 'text-gray-500'
  const category = penetrationResult.category
  if (category === 'excellent') return 'text-green-600 dark:text-green-400'
  if (category === 'good') return 'text-blue-600 dark:text-blue-400'
  if (category === 'fair') return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

// Arrow filters store references
const filters = computed(() => arrowFiltersStore.filters)
const showAdvancedFilters = computed(() => arrowFiltersStore.showAdvancedFilters)

// Global bow setup picker state
const selectedBowSetup = computed(() => bowSetupPickerStore.selectedBowSetup)
const selectedBowSetupId = ref('')
const userBowSetups = ref([])

// Arrow recommendations state for match summary
const recommendations = ref([])

// Computed properties for match summary
const matchDistribution = computed(() => {
  const distribution = {
    perfect: 0,     // 100%
    excellent: 0,   // 90-99%
    good: 0,        // 80-89%
    fair: 0,        // 70-79%
    acceptable: 0,  // 60-69%
    total: 0
  }
  
  recommendations.value.forEach(rec => {
    const match = rec.match_percentage || 0
    distribution.total++
    
    if (match === 100) {
      distribution.perfect++
    } else if (match >= 90) {
      distribution.excellent++
    } else if (match >= 80) {
      distribution.good++
    } else if (match >= 70) {
      distribution.fair++
    } else if (match >= 60) {
      distribution.acceptable++
    }
  })
  
  return distribution
})

const hasMatchDistribution = computed(() => {
  return matchDistribution.value.total > 0
})

// Store actions
const { updateBowConfig } = bowConfigStore

// UI state
const showComponents = ref(false)
const showMatchSummary = ref(false) // Default hidden
const showProfessionalSpine = ref(false) // Default hidden

// Advanced filters state
const availableManufacturers = ref([])
const hasActiveFilters = ref(false)

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success' // 'success', 'error', 'warning'
})

// Clear selected bow setup
const clearSelectedSetup = () => {
  bowSetupPickerStore.clearSelection()
  selectedBowSetupId.value = ''
}

// Load bow setup from dropdown selection
const loadBowSetup = (setupId) => {
  if (!setupId) {
    clearSelectedSetup()
    return
  }
  
  const setup = userBowSetups.value.find(s => s.id === parseInt(setupId))
  if (setup) {
    bowSetupPickerStore.selectBowSetup(setup)
    selectedBowSetupId.value = setupId
  }
}

// Load bow setup from API by ID (for URL parameters)
const loadBowSetupFromId = async (setupId) => {
  if (!setupId) return
  
  try {
    const response = await api.get(`/bow-setups/${setupId}`)
    const setup = response
    
    bowSetupPickerStore.selectBowSetup(setup)
    selectedBowSetupId.value = setupId.toString()
    
    console.log('Loaded bow setup from URL:', setup)
  } catch (error) {
    console.error('Error loading bow setup from ID:', error)
  }
}

// Load user's bow setups
const loadUserBowSetups = async () => {
  if (!user.value) return
  
  try {
    const setups = await fetchBowSetups()
    userBowSetups.value = setups || []
  } catch (error) {
    console.error('Error loading user bow setups:', error)
    userBowSetups.value = []
  }
}

// Notification helper functions
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  };
  
  // Auto-hide after 4 seconds
  setTimeout(() => {
    notification.value.show = false;
  }, 4000);
};

const hideNotification = () => {
  notification.value.show = false;
};

// Scroll to recommendations section
const scrollToRecommendations = () => {
  const element = document.querySelector('.arrow-recommendations')
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
};

// Handle arrow added to bow setup
const handleArrowAddedToSetup = (arrowData) => {
  console.log('Arrow added to setup:', arrowData)
  
  // Show success message
  showNotification(`Successfully added ${arrowData.arrow.manufacturer} ${arrowData.arrow.model_name} to ${selectedBowSetup.value?.name}!`)
  
  // Stay on calculator page - all data is preserved via Pinia store
  // User can continue browsing and adding more arrows
}

// Handle errors from arrow recommendations
const handleError = (errorMessage) => {
  showNotification(errorMessage, 'error')
}

// Handle recommendations updates for match summary
const handleRecommendationsUpdated = (newRecommendations) => {
  recommendations.value = newRecommendations
}

// Handle clear filters
const handleClearFilters = () => {
  arrowFiltersStore.clearFilters()
}

// Handle spine chart selection
const handleSpineChartSelection = (selection) => {
  // Handle the spine chart selection if needed
  console.log('Spine chart selection:', selection)
}


// Calculate vane weight based on type and length
const calculateVaneWeight = () => {
  const vaneType = bowConfig.value.vane_type || 'plastic'
  const vaneLength = bowConfig.value.vane_length || 4
  
  // Base weights per inch for different vane types
  const baseWeights = {
    plastic: 1.2,    // gn per inch - typical plastic vane
    feather: 0.8,    // gn per inch - natural feathers are lighter
    spin: 1.5        // gn per inch - spin vanes are typically heavier
  }
  
  const baseWeight = baseWeights[vaneType] || baseWeights.plastic
  const calculatedWeight = baseWeight * vaneLength
  
  return Math.round(calculatedWeight * 10) / 10 // Round to 1 decimal place
}

// Get vane weight based on override setting
const getVaneWeight = () => {
  if (bowConfig.value.vane_weight_override) {
    return bowConfig.value.vane_weight_per || 5
  } else {
    return calculateVaneWeight()
  }
}

// Calculate total component weight from all components
const calculateTotalComponentWeight = () => {
  const pointWeight = bowConfig.value.point_weight || 125
  const insertWeight = bowConfig.value.insert_weight || 0
  const vaneWeightPer = getVaneWeight()
  const numberOfVanes = bowConfig.value.number_of_vanes || 3
  const bushingWeight = bowConfig.value.bushing_weight || 0
  const nockWeight = bowConfig.value.nock_weight || 10
  
  // Calculate total vane weight
  const totalVaneWeight = vaneWeightPer * numberOfVanes
  
  // Sum all components
  const totalWeight = pointWeight + insertWeight + totalVaneWeight + bushingWeight + nockWeight
  
  return Math.round(totalWeight * 10) / 10 // Round to 1 decimal place
}

// Handle insert type change
const handleInsertChange = (value) => {
  if (value === 'none') {
    updateBowConfig({ insert_weight: 0 })
  } else if (value === 'custom') {
    updateBowConfig({ insert_weight: 10 }) // Default to 10gn when selecting custom
  }
}

// Handle bushing type change
const handleBushingChange = (value) => {
  if (value === 'none') {
    updateBowConfig({ bushing_weight: 0 })
  } else if (value === 'custom') {
    updateBowConfig({ bushing_weight: 3 }) // Default to 3gn when selecting custom
  }
}

// Handle vane type change
const handleVaneTypeChange = (value) => {
  updateBowConfig({ vane_type: value })
  // The vane weight will be automatically recalculated by calculateVaneWeight()
}

// Handle vane weight mode change (auto vs manual)
const handleVaneWeightModeChange = (value) => {
  if (value === 'auto') {
    updateBowConfig({ vane_weight_override: false })
  } else if (value === 'custom') {
    updateBowConfig({ 
      vane_weight_override: true,
      vane_weight_per: calculateVaneWeight() // Set to current calculated value as starting point
    })
  }
}

// Enhanced Performance Analysis Functions
// =====================================

const calculateEnhancedFoc = async () => {
  isCalculatingFoc.value = true
  try {
    const totalComponentWeight = calculateTotalComponentWeight()
    const shaftWeight = totalComponentWeight - (bowConfig.value.point_weight || 125) - 
                      (bowConfig.value.nock_weight || 10) - 
                      (getVaneWeight() * (bowConfig.value.number_of_vanes || 3)) - 
                      (bowConfig.value.insert_weight || 0)
    
    const response = await api.post('/calculator/enhanced-foc', {
      arrow_length: bowConfig.value.arrow_length || 29,
      point_weight: bowConfig.value.point_weight || 125,
      shaft_weight: Math.max(200, shaftWeight), // Estimate shaft weight
      nock_weight: bowConfig.value.nock_weight || 10,
      fletching_weight: getVaneWeight() * (bowConfig.value.number_of_vanes || 3),
      insert_weight: bowConfig.value.insert_weight || 0,
      intended_use: getIntendedUse()
    })
    
    enhancedFocResult.value = response
  } catch (error) {
    console.error('Error calculating enhanced FOC:', error)
    showNotification('Failed to calculate enhanced FOC analysis', 'error')
  } finally {
    isCalculatingFoc.value = false
  }
}

const calculateBallistics = async () => {
  isCalculatingBallistics.value = true
  try {
    const totalWeight = calculateTotalComponentWeight()
    const estimatedSpeed = await estimateArrowSpeed()
    
    const response = await api.post('/calculator/ballistics', {
      arrow_speed_fps: estimatedSpeed,
      arrow_weight_grains: totalWeight,
      arrow_diameter_inches: 0.246, // Default, could be made configurable
      arrow_type: getIntendedUse(),
      environmental: {
        temperature_f: 70,
        humidity_percent: 50,
        altitude_feet: 0,
        wind_speed_mph: 0,
        wind_direction_degrees: 0
      },
      shooting: {
        shot_angle_degrees: 0,
        sight_height_inches: 7,
        zero_distance_yards: 20,
        max_range_yards: 100
      }
    })
    
    ballisticsResult.value = response
  } catch (error) {
    console.error('Error calculating ballistics:', error)
    showNotification('Failed to calculate ballistics analysis', 'error')
  } finally {
    isCalculatingBallistics.value = false
  }
}

const calculateComprehensivePerformance = async () => {
  isCalculatingPerformance.value = true
  try {
    const totalWeight = calculateTotalComponentWeight()
    const shaftWeight = totalWeight - (bowConfig.value.point_weight || 125) - 
                      (bowConfig.value.nock_weight || 10) - 
                      (getVaneWeight() * (bowConfig.value.number_of_vanes || 3)) - 
                      (bowConfig.value.insert_weight || 0)
    
    const response = await api.post('/calculator/comprehensive-performance', {
      bow_config: {
        draw_weight: bowConfig.value.draw_weight || 50,
        draw_length: bowConfig.value.draw_length || 29,
        ibo_speed: 310 // Default IBO speed
      },
      arrow_specs: {
        arrow_length: bowConfig.value.arrow_length || 29,
        point_weight: bowConfig.value.point_weight || 125,
        shaft_weight: Math.max(200, shaftWeight),
        total_weight: totalWeight,
        nock_weight: bowConfig.value.nock_weight || 10,
        fletching_weight: getVaneWeight() * (bowConfig.value.number_of_vanes || 3),
        insert_weight: bowConfig.value.insert_weight || 0,
        diameter: 0.246,
        intended_use: getIntendedUse()
      }
    })
    
    comprehensivePerformance.value = response
  } catch (error) {
    console.error('Error calculating comprehensive performance:', error)
    showNotification('Failed to calculate comprehensive performance analysis', 'error')
  } finally {
    isCalculatingPerformance.value = false
  }
}

const estimateArrowSpeed = async () => {
  try {
    const response = await api.post('/calculator/arrow-speed-estimate', {
      bow_ibo_speed: 310, // Default IBO speed
      bow_draw_weight: bowConfig.value.draw_weight || 50,
      bow_draw_length: bowConfig.value.draw_length || 29,
      arrow_weight_grains: calculateTotalComponentWeight()
    })
    return response.estimated_speed_fps
  } catch (error) {
    console.error('Error estimating arrow speed:', error)
    return 280 // Fallback speed
  }
}

const getIntendedUse = () => {
  // Determine intended use based on arrow specifications or default
  const material = bowConfig.value.arrow_material
  if (material === 'wood') return 'traditional'
  
  const pointWeight = bowConfig.value.point_weight || 125
  if (pointWeight >= 150) return 'hunting'
  if (pointWeight <= 100) return 'target'
  return '3d'
}

// Trigger performance calculations when configuration changes
watch([bowConfig], async () => {
  if (showPerformanceDashboard.value) {
    // Debounce calculations to avoid too frequent updates
    clearTimeout(performanceCalculationTimeout.value)
    performanceCalculationTimeout.value = setTimeout(async () => {
      await Promise.all([
        calculateEnhancedFoc(),
        calculateBallistics(),
        calculateComprehensivePerformance()
      ])
    }, 1000)
  }
}, { deep: true })

const performanceCalculationTimeout = ref(null)

// Watch for changes to the selected bow setup from the global picker
watch(selectedBowSetup, (newBowSetup) => {
  if (newBowSetup) {
    // Update dropdown selection
    selectedBowSetupId.value = newBowSetup.id?.toString() || ''
    
    // Apply the bow configuration from the selected setup
    const bowConfig = newBowSetup.bow_config || {
      draw_weight: newBowSetup.draw_weight,
      draw_length: newBowSetup.draw_length,
      bow_type: newBowSetup.bow_type,
      arrow_length: newBowSetup.arrow_length || 29,
      point_weight: newBowSetup.point_weight || 125,
      arrow_material: newBowSetup.arrow_material || 'carbon'
    }
    
    updateBowConfig(bowConfig)
  } else {
    // Clear dropdown when no bow setup selected
    selectedBowSetupId.value = ''
  }
}, { immediate: false })

// Load data on mount
onMounted(async () => {
  // Load user's bow setups for the dropdown
  await loadUserBowSetups()
  
  // Check for URL query parameters (setupId from bow detail page)
  const route = useRoute()
  if (route.query.setupId) {
    // Load bow setup from setupId parameter
    await loadBowSetupFromId(route.query.setupId)
  } else if (selectedBowSetup.value) {
    // If a bow setup is already selected in the global picker, make sure configuration is applied
    selectedBowSetupId.value = selectedBowSetup.value.id?.toString() || ''
    
    // Ensure the bow configuration is properly loaded from the selected setup
    const setup = selectedBowSetup.value
    const bowConfig = setup.bow_config || {
      draw_weight: setup.draw_weight,
      draw_length: setup.draw_length,
      bow_type: setup.bow_type,
      arrow_length: setup.arrow_length || 29,
      point_weight: setup.point_weight || 125,
      arrow_material: setup.arrow_material || 'carbon'
    }
    
    // Apply the bow configuration from the selected setup
    updateBowConfig(bowConfig)
  }
  
  // Apply any query parameters to the bow config (these take precedence)
  if (route.query.bow_type) {
    updateBowConfig({ bow_type: route.query.bow_type })
  }
  if (route.query.draw_weight) {
    updateBowConfig({ draw_weight: parseFloat(route.query.draw_weight) })
  }
  if (route.query.draw_length) {
    updateBowConfig({ draw_length: parseFloat(route.query.draw_length) })
  }
  if (route.query.arrow_length) {
    updateBowConfig({ arrow_length: parseFloat(route.query.arrow_length) })
  }
  if (route.query.point_weight) {
    updateBowConfig({ point_weight: parseFloat(route.query.point_weight) })
  }
})

// Set page title
useHead({
  title: 'Arrow Calculator - ArcheryTool Beta',
  meta: [
    { name: 'description', content: 'Professional arrow calculator with spine calculations, compatibility scoring, and intelligent recommendations for your bow setup.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
</style>