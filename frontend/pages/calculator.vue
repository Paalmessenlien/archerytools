<template>
  <div>
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
              {{ selectedBowSetup.name }} ({{ selectedBowSetup.bow_type }}, {{ selectedBowSetup.draw_weight }}lbs) - Find arrows and add them to your setup
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

// API
const api = useApi()
const { user, fetchBowSetups } = useAuth()

const bowConfigStore = useBowConfigStore()

// Reactive references from store
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)
const arrowSetupDescription = computed(() => bowConfigStore.arrowSetupDescription)

// Store actions
const { updateBowConfig } = bowConfigStore

// Selected bow setup from navigation or dropdown
const selectedBowSetup = ref(null)
const selectedBowSetupId = ref('')
const userBowSetups = ref([])

// UI state
const showComponents = ref(false)

// Clear selected bow setup
const clearSelectedSetup = () => {
  selectedBowSetup.value = null
  selectedBowSetupId.value = ''
  // Clear from localStorage
  if (process.client) {
    localStorage.removeItem('selectedBowSetup')
  }
}

// Load bow setup from dropdown selection
const loadBowSetup = (setupId) => {
  if (!setupId) {
    clearSelectedSetup()
    return
  }
  
  const setup = userBowSetups.value.find(s => s.id === parseInt(setupId))
  if (setup) {
    selectedBowSetup.value = setup
    selectedBowSetupId.value = setupId
    
    // Apply the bow setup configuration to the calculator
    updateBowConfig({
      bow_type: setup.bow_type,
      draw_weight: setup.draw_weight,
      draw_length: setup.draw_length,
      arrow_length: setup.arrow_length || 29,
      point_weight: setup.point_weight || 125
    })
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

// Handle arrow added to bow setup
const handleArrowAddedToSetup = (arrowData) => {
  // Show success message
  alert(`Successfully added ${arrowData.arrow.manufacturer} ${arrowData.arrow.model_name} to ${selectedBowSetup.value?.name}!`)
  
  // Navigate to my-page to show the updated setup
  navigateTo('/my-page')
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

// Load data on mount
onMounted(async () => {
  // Load user's bow setups for the dropdown
  await loadUserBowSetups()
  
  // Check if a bow setup was selected from my-page navigation
  if (process.client) {
    const savedSetup = localStorage.getItem('selectedBowSetup')
    if (savedSetup) {
      try {
        const setup = JSON.parse(savedSetup)
        selectedBowSetup.value = setup
        selectedBowSetupId.value = setup.id.toString()
        
        // Apply the bow setup configuration to the calculator
        updateBowConfig({
          bow_type: setup.bow_type,
          draw_weight: setup.draw_weight,
          draw_length: setup.draw_length,
          arrow_length: setup.arrow_length || 29,
          point_weight: setup.point_weight || 125
        })
        
        // Clear the stored setup after loading it
        localStorage.removeItem('selectedBowSetup')
      } catch (error) {
        console.error('Error loading selected bow setup:', error)
      }
    }
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