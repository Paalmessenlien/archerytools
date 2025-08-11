<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto mx-4">
      <!-- Modal Header -->
      <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between sm:justify-start">
              <h3 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-gray-100 truncate">
                <i class="fas fa-edit mr-2 text-orange-600"></i>
                Edit Arrow Settings
              </h3>
              <CustomButton
                @click="closeModal"
                variant="outlined"
                size="small"
                class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 sm:hidden"
              >
                <i class="fas fa-times"></i>
              </CustomButton>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1 truncate" v-if="arrowSetup">
              {{ arrowSetup.arrow?.manufacturer }} {{ arrowSetup.arrow?.model_name }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-1" v-if="selectedSpine && availableSpines.length <= 1">
              <i class="fas fa-info-circle mr-1"></i>
              Current Spine: {{ selectedSpine }} (only option)
            </p>
          </div>
          <CustomButton
            @click="closeModal"
            variant="outlined"
            size="small"
            class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 hidden sm:flex"
          >
            <i class="fas fa-times"></i>
          </CustomButton>
        </div>
        
        
        <!-- Spine Selection Section -->
        <div class="mt-4" v-if="selectedSpine && availableSpines.length > 1">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            <i class="fas fa-exchange-alt mr-1 text-orange-600"></i>
            Spine Selection
          </label>
          <div class="flex flex-col sm:flex-row sm:items-center gap-2">
            <md-filled-select 
              :value="selectedSpine.toString()" 
              @change="handleSpineChange($event.target.value)"
              class="flex-1 sm:max-w-xs"
            >
              <md-select-option 
                v-for="spine in availableSpines" 
                :key="spine.spine"
                :value="spine.spine.toString()"
                :selected="spine.spine.toString() === selectedSpine.toString()"
              >
                <span class="hidden sm:inline">Spine {{ spine.spine }} ({{ spine.gpi_weight }} GPI, {{ spine.outer_diameter }}")</span>
                <span class="sm:hidden">{{ spine.spine }} ({{ spine.gpi_weight }}g, {{ spine.outer_diameter }}")</span>
              </md-select-option>
            </md-filled-select>
            <span class="text-xs text-gray-500 dark:text-gray-500 sm:ml-2">
              {{ availableSpines.length }} options
            </span>
          </div>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="p-4 sm:p-6">
        <form @submit.prevent="saveChanges">
          <!-- Arrow Length -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Arrow Length: <span class="font-semibold text-blue-600">{{ editForm.arrow_length }}"</span>
            </label>
            <md-slider
              min="24"
              max="34"
              step="0.5"
              :value="editForm.arrow_length"
              @input="editForm.arrow_length = parseFloat($event.target.value)"
              labeled
              ticks
              class="w-full"
            ></md-slider>
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
              <span>24"</span>
              <span>34"</span>
            </div>
          </div>

          <!-- Point Weight -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Point Weight: <span class="font-semibold text-blue-600">{{ editForm.point_weight }} gr</span>
            </label>
            <md-slider
              min="40"
              max="300"
              step="5"
              :value="editForm.point_weight"
              @input="editForm.point_weight = parseFloat($event.target.value)"
              labeled
              ticks
              class="w-full"
            ></md-slider>
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
              <span>40 gr</span>
              <span>300 gr</span>
            </div>
          </div>

          <!-- Arrow Components Section -->
          <div class="mb-6">
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
                {{ showComponents ? 'Hide' : 'Show' }} Components
              </CustomButton>
            </div>

            <div v-if="showComponents" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Insert Weight -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Insert Weight: <span class="font-semibold text-primary">{{ editForm.insert_weight || 0 }} gn</span>
                </label>
                <div class="mb-2">
                  <md-filled-select 
                    :value="editForm.insert_weight === 0 ? 'none' : 'custom'" 
                    @change="handleInsertChange($event.target.value)"
                    label="Insert Type"
                    class="w-full"
                  >
                    <md-select-option value="none">No Insert</md-select-option>
                    <md-select-option value="custom">Custom Weight</md-select-option>
                  </md-filled-select>
                </div>
                <div v-if="editForm.insert_weight > 0">
                  <md-slider
                    min="5"
                    max="30"
                    step="0.5"
                    :value="editForm.insert_weight"
                    @input="editForm.insert_weight = parseFloat($event.target.value)"
                    labeled
                    class="w-full"
                  ></md-slider>
                  <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                    <span>5 gn</span>
                    <span>30 gn</span>
                  </div>
                </div>
              </div>

              <!-- Nock Weight -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nock Weight: <span class="font-semibold text-primary">{{ editForm.nock_weight || 10 }} gn</span>
                </label>
                <md-slider
                  min="5"
                  max="25"
                  step="0.5"
                  :value="editForm.nock_weight || 10"
                  @input="editForm.nock_weight = parseFloat($event.target.value)"
                  labeled
                  class="w-full"
                ></md-slider>
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>5 gn</span>
                  <span>25 gn</span>
                </div>
              </div>

              <!-- Vane Type -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Vane Type
                </label>
                <md-filled-select 
                  :value="editForm.vane_type || 'plastic'" 
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
                  Vane Length: <span class="font-semibold text-primary">{{ editForm.vane_length || 4 }}"</span>
                </label>
                <md-slider
                  min="1"
                  max="6"
                  step="0.25"
                  :value="editForm.vane_length || 4"
                  @input="editForm.vane_length = parseFloat($event.target.value)"
                  labeled
                  class="w-full"
                ></md-slider>
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>1"</span>
                  <span>6"</span>
                </div>
              </div>

              <!-- Vane Weight -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Vane Weight (Each): <span class="font-semibold text-primary">{{ getVaneWeight() }} gn</span>
                </label>
                <div class="mb-2">
                  <md-filled-select 
                    :value="editForm.vane_weight_override ? 'custom' : 'auto'" 
                    @change="handleVaneWeightModeChange($event.target.value)"
                    label="Weight Mode"
                    class="w-full"
                  >
                    <md-select-option value="auto">Auto Calculate</md-select-option>
                    <md-select-option value="custom">Manual Override</md-select-option>
                  </md-filled-select>
                </div>
                <div v-if="!editForm.vane_weight_override" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Calculated based on type and length
                </div>
                <div v-if="editForm.vane_weight_override">
                  <md-slider
                    min="1"
                    max="15"
                    step="0.25"
                    :value="editForm.vane_weight_per || 5"
                    @input="editForm.vane_weight_per = parseFloat($event.target.value)"
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
                  Number of Vanes: <span class="font-semibold text-primary">{{ editForm.number_of_vanes || 3 }}</span>
                </label>
                <md-slider
                  min="2"
                  max="6"
                  step="1"
                  :value="editForm.number_of_vanes || 3"
                  @input="editForm.number_of_vanes = parseInt($event.target.value)"
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
                  Bushing Weight: <span class="font-semibold text-primary">{{ editForm.bushing_weight || 0 }} gn</span>
                </label>
                <div class="mb-2">
                  <md-filled-select 
                    :value="editForm.bushing_weight === 0 ? 'none' : 'custom'" 
                    @change="handleBushingChange($event.target.value)"
                    label="Bushing Type"
                    class="w-full"
                  >
                    <md-select-option value="none">No Bushing</md-select-option>
                    <md-select-option value="custom">Custom Weight</md-select-option>
                  </md-filled-select>
                </div>
                <div v-if="editForm.bushing_weight > 0">
                  <md-slider
                    min="1"
                    max="15"
                    step="0.25"
                    :value="editForm.bushing_weight"
                    @input="editForm.bushing_weight = parseFloat($event.target.value)"
                    labeled
                    class="w-full"
                  ></md-slider>
                  <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                    <span>1 gn</span>
                    <span>15 gn</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Calculated Results -->
          <div class="mb-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Calculated Spine (Informational) -->
            <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div class="flex items-center mb-2">
                <i v-if="calculatingSpine" class="fas fa-spinner fa-spin text-blue-600 mr-2"></i>
                <i v-else class="fas fa-info-circle text-blue-600 mr-2"></i>
                <span class="text-sm font-medium text-blue-900 dark:text-blue-200">
                  {{ calculatingSpine ? 'Calculating Spine...' : 'Optimal Spine (Reference)' }}
                </span>
              </div>
              <p class="text-lg font-semibold text-blue-700 dark:text-blue-300">
                {{ calculatingSpine ? 'Calculating...' : (calculatedSpine || 'N/A') }}
              </p>
              <p class="text-xs text-blue-600 dark:text-blue-400 mt-1">
                <span class="hidden sm:inline">{{ props.bowSetup ? `For reference - your selected arrow spine remains unchanged` : 'Reference calculation only' }}</span>
                <span class="sm:hidden">Reference only</span>
              </p>
            </div>

            <!-- Total Component Weight -->
            <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <div class="flex items-center mb-2">
                <i class="fas fa-weight-hanging text-green-600 mr-2"></i>
                <span class="text-sm font-medium text-green-900 dark:text-green-200">Component Weight</span>
              </div>
              <p class="text-lg font-semibold text-green-700 dark:text-green-300">
                {{ calculateTotalComponentWeight() }} gn
              </p>
              <p class="text-xs text-green-600 dark:text-green-400 mt-1">
                Points, vanes, nock, inserts
              </p>
            </div>

            <!-- Total Arrow Weight -->
            <div class="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
              <div class="flex items-center mb-2">
                <i class="fas fa-balance-scale text-orange-600 mr-2"></i>
                <span class="text-sm font-medium text-orange-900 dark:text-orange-200">Total Arrow Weight</span>
              </div>
              <p class="text-lg font-semibold text-orange-700 dark:text-orange-300">
                {{ calculateTotalArrowWeight() }} gr
              </p>
              <p class="text-xs text-orange-600 dark:text-orange-400 mt-1">
                Includes shaft weight ({{ selectedSpineSpec?.gpi_weight || 'N/A' }} GPI)
              </p>
            </div>
          </div>

          <!-- Match Score -->
          <div class="mb-6 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <div class="flex items-center mb-2">
              <i v-if="calculatingMatchScore" class="fas fa-spinner fa-spin text-purple-600 mr-2"></i>
              <i v-else class="fas fa-star text-purple-600 mr-2"></i>
              <span class="text-sm font-medium text-purple-900 dark:text-purple-200">
                {{ calculatingMatchScore ? 'Calculating Match Score...' : 'Updated Match Score' }}
              </span>
            </div>
            <p class="text-lg font-semibold text-purple-700 dark:text-purple-300">
              {{ calculatingMatchScore ? 'Calculating...' : (recalculatedMatchScore !== null ? `${recalculatedMatchScore}%` : 'N/A') }}
            </p>
            <p class="text-xs text-purple-600 dark:text-purple-400 mt-1">
              <span class="hidden sm:inline">Based on your configuration changes{{ props.bowSetup ? ` for ${props.bowSetup.bow_type} bow` : '' }}</span>
              <span class="sm:hidden">Based on selected spine vs optimal</span>
            </p>
          </div>

          <!-- Notes -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Notes (Optional)
            </label>
            <md-outlined-text-field
              :value="editForm.notes"
              @input="editForm.notes = $event.target.value"
              label="Notes about this arrow configuration"
              class="w-full"
              rows="3"
              type="textarea"
            ></md-outlined-text-field>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row sm:justify-end gap-3 sm:space-x-3 sm:gap-0">
            <CustomButton
              @click="closeModal"
              variant="outlined"
              class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 order-2 sm:order-1"
            >
              Cancel
            </CustomButton>
            <CustomButton
              type="submit"
              variant="filled"
              :disabled="saving"
              class="bg-orange-600 text-white hover:bg-orange-700 order-1 sm:order-2"
            >
              <i v-if="saving" class="fas fa-spinner fa-spin mr-2"></i>
              <i v-else class="fas fa-save mr-2"></i>
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </CustomButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { calculateSpineAPI, findBestSpineMatch, calculateCompatibilityScore } from '~/utils/spineCalculation'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  arrowSetup: {
    type: Object,
    default: null
  },
  bowSetup: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'save'])

// API
const api = useApi()

// State
const saving = ref(false)
const showComponents = ref(false)
const recalculatedMatchScore = ref(null)
const calculatingMatchScore = ref(false)
const matchCalculationTimer = ref(null)
const selectedSpine = ref(null)
const editForm = ref({
  arrow_length: 29,
  point_weight: 125,
  // Component weights
  nock_weight: 10,
  insert_weight: 0,
  bushing_weight: 0,
  vane_weight_per: 5,
  vane_weight_override: false,
  vane_type: 'plastic',
  vane_length: 4,
  number_of_vanes: 3,
  notes: ''
})

// Build bow configuration from arrow setup for calculations
const bowConfigForCalculation = computed(() => {
  if (!props.arrowSetup) return null
  
  // Use bow setup information if available, otherwise use defaults
  const bowSetup = props.bowSetup
  
  return {
    draw_weight: bowSetup?.draw_weight || 50,
    draw_length: bowSetup?.draw_length || 28,
    bow_type: bowSetup?.bow_type || 'compound',
    arrow_length: editForm.value.arrow_length,
    point_weight: editForm.value.point_weight,
    arrow_material: props.arrowSetup.arrow?.material || 'carbon',
    // Component weights from form
    insert_weight: editForm.value.insert_weight || 0,
    vane_type: editForm.value.vane_type || 'plastic',
    vane_length: editForm.value.vane_length || 4,
    number_of_vanes: editForm.value.number_of_vanes || 3,
    vane_weight_per: getVaneWeight(),
    bushing_weight: editForm.value.bushing_weight || 0,
    nock_weight: editForm.value.nock_weight || 10
  }
})

// Reactive spine calculation result from API
const spineCalculationResult = ref(null)
const calculatingSpine = ref(false)

// Get calculated spine from API result
const calculatedSpine = computed(() => {
  return spineCalculationResult.value?.recommended_spine || 'Calculating...'
})

// Get available spine options for the current arrow
const availableSpines = computed(() => {
  if (!props.arrowSetup?.arrow?.spine_specifications) return []
  return props.arrowSetup.arrow.spine_specifications.sort((a, b) => a.spine - b.spine)
})

// Get the currently selected spine specification details
const selectedSpineSpec = computed(() => {
  if (!selectedSpine.value) return null
  return availableSpines.value.find(spec => spec.spine.toString() === selectedSpine.value.toString())
})

// Calculate vane weight based on type and length
const calculateVaneWeight = () => {
  const vaneType = editForm.value.vane_type || 'plastic'
  const vaneLength = editForm.value.vane_length || 4
  
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
  if (editForm.value.vane_weight_override) {
    return editForm.value.vane_weight_per || 5
  } else {
    return calculateVaneWeight()
  }
}

// Calculate total component weight
const calculateTotalComponentWeight = () => {
  const pointWeight = editForm.value.point_weight || 125
  const insertWeight = editForm.value.insert_weight || 0
  const vaneWeightPer = getVaneWeight()
  const numberOfVanes = editForm.value.number_of_vanes || 3
  const bushingWeight = editForm.value.bushing_weight || 0
  const nockWeight = editForm.value.nock_weight || 10
  
  // Calculate total vane weight
  const totalVaneWeight = vaneWeightPer * numberOfVanes
  
  // Sum all components
  const totalWeight = pointWeight + insertWeight + totalVaneWeight + bushingWeight + nockWeight
  
  return Math.round(totalWeight * 10) / 10 // Round to 1 decimal place
}

// Calculate total arrow weight including shaft
const calculateTotalArrowWeight = () => {
  if (!selectedSpineSpec.value?.gpi_weight) return 'N/A'
  
  // Calculate shaft weight (GPI * length)
  const shaftWeight = selectedSpineSpec.value.gpi_weight * (editForm.value.arrow_length || 32)
  
  // Add component weights
  const componentWeight = calculateTotalComponentWeight()
  
  const totalWeight = shaftWeight + componentWeight
  
  return Math.round(totalWeight * 10) / 10 // Round to 1 decimal place
}

// Component handlers
const handleInsertChange = (value) => {
  if (value === 'none') {
    editForm.value.insert_weight = 0
  } else if (value === 'custom') {
    editForm.value.insert_weight = 10 // Default to 10gn when selecting custom
  }
}

const handleBushingChange = (value) => {
  if (value === 'none') {
    editForm.value.bushing_weight = 0
  } else if (value === 'custom') {
    editForm.value.bushing_weight = 3 // Default to 3gn when selecting custom
  }
}

const handleVaneTypeChange = (value) => {
  editForm.value.vane_type = value
  // The vane weight will be automatically recalculated by calculateVaneWeight()
}

const handleVaneWeightModeChange = (value) => {
  if (value === 'auto') {
    editForm.value.vane_weight_override = false
  } else if (value === 'custom') {
    editForm.value.vane_weight_override = true
    editForm.value.vane_weight_per = calculateVaneWeight() // Set to current calculated value as starting point
  }
}

const handleSpineChange = (newSpineValue) => {
  const newSpine = parseFloat(newSpineValue)
  selectedSpine.value = newSpine
  console.log(`Spine changed to: ${newSpine}`)
  
  // Trigger recalculation of match score with new spine
  triggerCalculation()
}

// Watch for arrow setup changes
watch(() => props.arrowSetup, (newArrowSetup) => {
  if (newArrowSetup) {
    editForm.value = {
      arrow_length: newArrowSetup.arrow_length || 29,
      point_weight: newArrowSetup.point_weight || 125,
      // Component weights
      nock_weight: newArrowSetup.nock_weight || 10,
      insert_weight: newArrowSetup.insert_weight || 0,
      bushing_weight: newArrowSetup.bushing_weight || 0,
      vane_weight_per: newArrowSetup.vane_weight_per || 5,
      vane_weight_override: newArrowSetup.vane_weight_override || false,
      vane_type: newArrowSetup.vane_type || 'plastic',
      vane_length: newArrowSetup.vane_length || 4,
      number_of_vanes: newArrowSetup.number_of_vanes || 3,
      notes: newArrowSetup.notes || ''
    }
    
    // Initialize selected spine from the arrow setup, with fallback
    if (newArrowSetup.calculated_spine) {
      selectedSpine.value = newArrowSetup.calculated_spine
    } else if (availableSpines.value.length > 0) {
      // Fallback: use the first available spine if no calculated_spine exists
      selectedSpine.value = availableSpines.value[0].spine
      console.log('No calculated_spine found, using first available spine:', selectedSpine.value)
    }
    
    recalculatedMatchScore.value = null // Reset match score
  }
}, { immediate: true })

// Unified spine and match score calculation
const calculateSpineAndMatch = async () => {
  if (!props.arrowSetup?.arrow || !bowConfigForCalculation.value) return
  
  calculatingSpine.value = true
  calculatingMatchScore.value = true
  
  try {
    console.log('Calculating spine and match score with config:', bowConfigForCalculation.value)
    
    // Get spine calculation from API - this is the authoritative calculation
    const result = await calculateSpineAPI(bowConfigForCalculation.value, api)
    spineCalculationResult.value = result
    console.log('Spine calculation result:', result)
    
    // Calculate compatibility score using the SELECTED spine (not optimal spine)
    // This shows the match score for the currently selected arrow spine
    const currentSpine = selectedSpine.value
    if (currentSpine && props.arrowSetup.arrow) {
      const spineSpecs = props.arrowSetup.arrow.spine_specifications || []
      
      if (spineSpecs.length > 0) {
        // Calculate compatibility against the optimal spine for this configuration
        const bowType = props.bowSetup?.bow_type || 'compound'
        const manufacturer = props.arrowSetup.arrow?.manufacturer?.toLowerCase() || 'easton'
        
        // Use the centralized compatibility calculation with SELECTED spine vs OPTIMAL spine
        const optimalSpine = result?.recommended_spine || currentSpine
        const compatibility = calculateCompatibilityScore(currentSpine, optimalSpine, bowType, manufacturer)
        
        recalculatedMatchScore.value = compatibility.score
        console.log('Calculated match score:', recalculatedMatchScore.value, 'for selected spine:', currentSpine, 'vs optimal:', optimalSpine)
        console.log('Compatibility explanation:', compatibility.explanation)
      } else {
        recalculatedMatchScore.value = 0
        console.log('No spine specifications found for compatibility calculation')
      }
    } else {
      recalculatedMatchScore.value = 0
      console.log('No selected spine found for compatibility calculation')
    }
  } catch (error) {
    console.error('Error calculating spine and match score:', error)
    // Don't show error to user for this background calculation
    spineCalculationResult.value = null
    recalculatedMatchScore.value = null
  } finally {
    calculatingSpine.value = false
    calculatingMatchScore.value = false
  }
}

// Debounced spine and match calculation trigger
const triggerCalculation = () => {
  if (matchCalculationTimer.value) {
    clearTimeout(matchCalculationTimer.value)
  }
  
  matchCalculationTimer.value = setTimeout(() => {
    calculateSpineAndMatch()
  }, 500)
}

// Watch for form changes to recalculate spine and match score
watch([editForm, bowConfigForCalculation], () => {
  if (props.arrowSetup?.arrow && bowConfigForCalculation.value) {
    triggerCalculation()
  }
}, { deep: true })

// Watch for modal opening to trigger initial calculation
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.arrowSetup?.arrow) {
    // Reset and calculate when modal opens
    spineCalculationResult.value = null
    recalculatedMatchScore.value = null
    nextTick(() => {
      triggerCalculation()
    })
  }
})

// Methods
const closeModal = () => {
  emit('close')
}

const saveChanges = async () => {
  if (!props.arrowSetup) return
  
  saving.value = true
  
  try {
    // Prepare update data with all component weights
    // Include the selected spine if it has changed from the original
    const updateData = {
      arrow_id: props.arrowSetup.arrow_id,
      arrow_length: editForm.value.arrow_length,
      point_weight: editForm.value.point_weight,
      // Include selected spine (user can change spine to other options from same arrow)
      calculated_spine: selectedSpine.value,
      // Component weights
      nock_weight: editForm.value.nock_weight,
      insert_weight: editForm.value.insert_weight,
      bushing_weight: editForm.value.bushing_weight,
      vane_weight_per: getVaneWeight(),
      vane_type: editForm.value.vane_type,
      vane_length: editForm.value.vane_length,
      number_of_vanes: editForm.value.number_of_vanes,
      // Updated compatibility score if recalculated
      compatibility_score: recalculatedMatchScore.value || editForm.value.compatibility_score,
      notes: editForm.value.notes || null
    }
    
    console.log('Saving arrow changes:', updateData)
    
    // Emit save event to parent (the parent will handle the API call)
    emit('save', updateData)
    
  } catch (error) {
    console.error('Error updating arrow:', error)
    emit('error', 'Failed to update arrow settings. Please try again.')
  } finally {
    saving.value = false
  }
}
</script>