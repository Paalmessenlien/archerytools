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
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">Arrow Calculator</h1>
      <p class="text-lg text-gray-600 dark:text-gray-300 mb-4">
        Find the perfect arrows for your bow setup with professional spine calculations and compatibility scoring.
      </p>
    </div>

    <!-- Bow Setup Loaded Notification -->
    <div v-if="selectedBowSetup" class="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
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
    <div class="mb-8">
      <div class="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
        <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-4">
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
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Draw Weight: <span class="font-semibold text-primary">{{ bowConfig.draw_weight }} lbs</span>
            </label>
            <md-slider
              ref="drawWeightSlider"
              min="20"
              max="80"
              step="0.5"
              :value="bowConfig.draw_weight"
              @input="updateBowConfig({ draw_weight: parseFloat($event.target.value) })"
              labeled
              ticks
              class="w-full"
            ></md-slider>
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
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Arrow Length: <span class="font-semibold text-primary">{{ bowConfig.arrow_length || 29 }}"</span>
            </label>
            <md-slider
              ref="arrowLengthSlider"
              min="24"
              max="34"
              step="0.5"
              :value="bowConfig.arrow_length || 29"
              @input="updateBowConfig({ arrow_length: parseFloat($event.target.value) })"
              labeled
              ticks
              class="w-full"
            ></md-slider>
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
              <span>24"</span>
              <span>34"</span>
            </div>
          </div>
        </div>

        <!-- Arrow Components Section -->
        <div class="mt-6">
          <div class="flex items-center justify-between mb-4">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              <i class="fas fa-puzzle-piece mr-2"></i>
              Arrow Components
            </h4>
            <CustomButton
              @click="showComponents = !showComponents"
              variant="text"
              size="small"
              class="text-blue-600 hover:bg-blue-100 dark:text-blue-400 dark:hover:bg-blue-900"
            >
              <i class="fas transition-transform" :class="showComponents ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
              {{ showComponents ? 'Hide' : 'Show' }} Details
            </CustomButton>
          </div>

          <div v-if="showComponents" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Point Weight -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Point Weight: <span class="font-semibold text-primary">{{ bowConfig.point_weight || 125 }} gn</span>
              </label>
              <md-slider
                ref="pointWeightSlider"
                min="40"
                max="300"
                step="5"
                :value="bowConfig.point_weight || 125"
                @input="updateBowConfig({ point_weight: parseFloat($event.target.value) })"
                labeled
                ticks
                class="w-full"
              ></md-slider>
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                <span>40 gn</span>
                <span>300 gn</span>
              </div>
            </div>

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

    <!-- Manufacturer Spine Chart Selector -->
    <div class="mb-8">
      <div class="bg-green-50 dark:bg-green-900/20 p-6 rounded-lg border border-green-200 dark:border-green-800">
        <h3 class="text-lg font-semibold text-green-900 dark:text-green-200 mb-4">
          <i class="fas fa-chart-line mr-2"></i>
          Professional Spine Calculation
        </h3>
        
        <ManufacturerSpineChartSelector
          :bow-type="bowConfig.bow_type"
          @selection-change="handleSpineChartSelection"
        />
      </div>
    </div>

    <!-- Calculated Specifications -->
    <md-elevated-card class="mb-8 light-surface light-elevation">
      <div class="p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-calculator" style="margin-right: 8px; color: #6366f1;"></i>
          Calculated Specifications
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
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
        <div v-if="enhancedSpineResult" class="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <h4 class="text-sm font-semibold text-green-900 dark:text-green-200 mb-3">
            <i class="fas fa-chart-line mr-2"></i>
            Enhanced Calculation Results
          </h4>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        <div v-else-if="isCalculatingEnhancedSpine" class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent dark:border-blue-400"></div>
            <span class="ml-2 text-sm text-blue-700 dark:text-blue-300">Calculating enhanced spine recommendation...</span>
          </div>
        </div>
        
        <!-- Material-specific calculation notes -->
        <div v-if="bowConfig.arrow_material && bowConfig.arrow_material === 'wood'" class="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
          <p class="text-sm text-orange-800 dark:text-orange-200">
            <i class="fas fa-info-circle mr-2"></i>
            <strong>Wood Arrow Calculation:</strong> Uses traditional wood arrow spine charts with pound-based measurements. 
            This calculation method works for any bow type when wood arrows are selected.
          </p>
        </div>
        
        <div v-else-if="!bowConfig.arrow_material || bowConfig.arrow_material === ''" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p class="text-sm text-blue-800 dark:text-blue-200">
            <i class="fas fa-info-circle mr-2"></i>
            <strong>All Materials:</strong> Shows recommendations for all arrow materials. 
            Spine calculations use standard carbon spine numbers based on your bow type.
          </p>
        </div>

        <!-- Spine Conversion Widget -->
        <div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <SpineConversionWidget />
        </div>
      </div>
    </md-elevated-card>

    <!-- Arrow Recommendations -->
    <div class="mt-8">
      <ArrowRecommendationsList 
        :bow-config="bowConfig"
        :show-search-filters="true"
        :selected-bow-setup="selectedBowSetup"
        @arrow-added-to-setup="handleArrowAddedToSetup"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBowConfigStore } from '~/stores/bowConfig'
import { useBowSetupPickerStore } from '~/stores/bowSetupPicker'
import ManufacturerSpineChartSelector from '~/components/ManufacturerSpineChartSelector.vue'
import SpineConversionWidget from '~/components/SpineConversionWidget.vue'

// API
const api = useApi()
const { user, fetchBowSetups } = useAuth()

const bowConfigStore = useBowConfigStore()
const bowSetupPickerStore = useBowSetupPickerStore()

// Reactive references from stores
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)
const arrowSetupDescription = computed(() => bowConfigStore.arrowSetupDescription)

// Global bow setup picker state
const selectedBowSetup = computed(() => bowSetupPickerStore.selectedBowSetup)
const selectedBowSetupId = ref('')
const userBowSetups = ref([])

// Store actions
const { updateBowConfig } = bowConfigStore

// UI state
const showComponents = ref(false)

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

// Handle arrow added to bow setup
const handleArrowAddedToSetup = (arrowData) => {
  // Show success message
  showNotification(`Successfully added ${arrowData.arrow.manufacturer} ${arrowData.arrow.model_name} to ${selectedBowSetup.value?.name}!`)
  
  // Stay on calculator page - all data is preserved via Pinia store
  // User can continue browsing and adding more arrows
}

// Spine chart selection state
const spineChartSelection = ref({
  manufacturer: null,
  chartId: null,
  chart: null,
  calculationMode: 'simple',
  professionalSettings: {
    bowSpeed: null,
    releaseType: 'mechanical'
  }
})

// Enhanced spine calculation state
const enhancedSpineResult = ref(null)
const isCalculatingEnhancedSpine = ref(false)

// Handle spine chart selection change
const handleSpineChartSelection = async (selection) => {
  spineChartSelection.value = selection
  
  // Trigger enhanced spine calculation if manufacturer is selected
  if (selection.manufacturer || selection.calculationMode === 'professional') {
    await calculateEnhancedSpine()
  } else {
    enhancedSpineResult.value = null
  }
}

// Calculate enhanced spine using manufacturer charts
const calculateEnhancedSpine = async () => {
  if (isCalculatingEnhancedSpine.value) return
  
  isCalculatingEnhancedSpine.value = true
  
  try {
    const requestData = {
      bow_config: {
        ...bowConfig.value,
        // Add professional settings if in professional mode
        ...(spineChartSelection.value.calculationMode === 'professional' ? spineChartSelection.value.professionalSettings : {})
      },
      manufacturer_preference: spineChartSelection.value.manufacturer,
      chart_id: spineChartSelection.value.chartId
    }
    
    const response = await api.post('/calculator/spine-recommendation-enhanced', requestData)
    enhancedSpineResult.value = response
    
    // Update the recommended spine display with enhanced calculation
    if (response.recommended_spine) {
      // Update the bow config store with the enhanced spine
      bowConfigStore.setRecommendedSpine(response.recommended_spine)
    }
    
  } catch (error) {
    console.error('Error calculating enhanced spine:', error)
    showNotification('Failed to calculate enhanced spine recommendation', 'error')
  } finally {
    isCalculatingEnhancedSpine.value = false
  }
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