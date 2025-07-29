<template>
  <div>
    <!-- Beta Notice Banner -->
    <div class="mb-6 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-flask text-orange-600 dark:text-orange-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200">Beta Testing Phase</h4>
          <p class="text-xs text-orange-700 dark:text-orange-300 mt-1">
            This platform is in beta. Features may change and data may be reset. Invitation-only access.
          </p>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Arrow Tuning Platform</h1>
      <p class="text-gray-600 dark:text-gray-300">Manage your bow setups and arrow configurations for personalized recommendations</p>
    </div>

    <!-- Navigation Tabs -->
    <div class="mb-6">
      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8">
          <button
            @click="activeTab = 'tuning'"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === 'tuning'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            <i class="fas fa-crosshairs mr-2"></i>
            Quick Tuning
          </button>
          <button
            @click="activeTab = 'setups'"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === 'setups'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            <i class="fas fa-archive mr-2"></i>
            Bow Setups
          </button>
        </nav>
      </div>
    </div>

    <!-- Quick Tuning Tab -->
    <div v-if="activeTab === 'tuning'" class="card card-interactive glass-card">
      <!-- Bow Configuration Form -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Bow Type -->
        <div>
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

        <!-- Point Weight -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Point Weight: <span class="font-semibold text-primary">{{ bowConfig.point_weight || 125 }} gr</span>
          </label>
          <md-slider
            ref="pointWeightSlider"
            min="75"
            max="200"
            step="25"
            :value="bowConfig.point_weight || 125"
            @input="updateBowConfig({ point_weight: parseInt($event.target.value) })"
            labeled
            ticks
            class="w-full"
          ></md-slider>
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
            <span>75 gr</span>
            <span>200 gr</span>
          </div>
        </div>

        <!-- Draw Weight -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Draw Weight: <span class="font-semibold text-primary">{{ bowConfig.draw_weight }} lbs</span>
          </label>
          <md-slider
            ref="drawWeightSlider"
            min="20"
            max="80"
            :value="bowConfig.draw_weight"
            @input="updateBowConfig({ draw_weight: parseInt($event.target.value) })"
            labeled
            ticks
            class="w-full"
          ></md-slider>
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
            <span>20 lbs</span>
            <span>80 lbs</span>
          </div>
        </div>



        <!-- Arrow Length -->
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


      <!-- Calculated Specifications -->
      <md-elevated-card class="mt-8 light-surface light-elevation">
        <div class="p-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            <i class="fas fa-calculator" style="margin-right: 8px; color: #6366f1;"></i>
            Calculated Specifications
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="flex flex-col">
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">
                <i class="fas fa-bullseye" style="margin-right: 6px; color: #6366f1;"></i>
                Recommended Spine:
              </p>
              <p class="font-semibold text-xl text-primary">{{ recommendedSpine || 'Calculating...' }}</p>
            </div>
            <div class="flex flex-col">
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">
                <i class="fas fa-crosshairs" style="margin-right: 6px; color: #7c3aed;"></i>
                Arrow Setup:
              </p>
              <p class="font-semibold text-gray-900 dark:text-gray-100">{{ arrowSetupDescription }}</p>
            </div>
          </div>
        </div>
      </md-elevated-card>

      <!-- Arrow Recommendations -->
      <div class="mt-8">
        <ArrowRecommendationsList 
          :bow-config="bowConfig"
          :show-search-filters="false"
          class="simplified-recommendations"
        />
      </div>

      <!-- Saved Arrow Setups -->
      <SavedArrowSetups 
        :saved-setups="savedArrowSetups"
        @remove-setup="removeArrowSetup"
      />
    </div>

    <!-- Bow Setups Tab -->
    <div v-if="activeTab === 'setups'">
      <!-- Bow Setups Management -->
      <div class="card card-interactive glass-card">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-archive mr-2 text-indigo-600"></i>
            Your Bow Setups
          </h2>
          <CustomButton
            @click="showCreateSetupModal = true"
            variant="filled"
            class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
          >
            <i class="fas fa-plus mr-2"></i>
            Create Bow Setup
          </CustomButton>
        </div>

        <!-- Bow Setups List -->
        <div v-if="bowSetups.length > 0" class="space-y-4 mb-6">
          <div 
            v-for="setup in bowSetups" 
            :key="setup.id"
            class="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
            @click="selectBowSetup(setup)"
            :class="{ 'ring-2 ring-indigo-500': selectedBowSetup?.id === setup.id }"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h3 class="font-medium text-gray-900 dark:text-gray-100 mb-2">{{ setup.name }}</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                  <div>
                    <span class="text-gray-600 dark:text-gray-400">Type:</span>
                    <span class="font-medium ml-1">{{ formatBowType(setup.bow_type) }}</span>
                  </div>
                  <div>
                    <span class="text-gray-600 dark:text-gray-400">Draw Weight:</span>
                    <span class="font-medium ml-1">{{ setup.draw_weight }} lbs</span>
                  </div>
                  <div>
                    <span class="text-gray-600 dark:text-gray-400">Draw Length:</span>
                    <span class="font-medium ml-1">{{ setup.draw_length }}"</span>
                  </div>
                </div>
                <div v-if="setup.description" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  {{ setup.description }}
                </div>
              </div>
              <div class="flex space-x-2 ml-4">
                <CustomButton
                  @click.stop="editBowSetup(setup)"
                  variant="outlined"
                  size="small"
                  class="text-gray-600 dark:text-gray-400"
                >
                  <i class="fas fa-edit"></i>
                </CustomButton>
                <CustomButton
                  @click.stop="deleteBowSetup(setup)"
                  variant="outlined"
                  size="small"
                  class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900/20"
                >
                  <i class="fas fa-trash"></i>
                </CustomButton>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
          <i class="fas fa-archive text-4xl mb-4 opacity-50"></i>
          <p class="text-lg mb-2">No bow setups yet</p>
          <p class="text-sm">Create your first bow setup to get started with arrow configurations</p>
        </div>

        <!-- Selected Bow Setup Arrow Configurations -->
        <div v-if="selectedBowSetup" class="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <ArrowConfigurationsList 
            :configurations="getArrowConfigsForSetup(selectedBowSetup.id)"
            :bow-config="selectedBowSetup"
            @add-configuration="addArrowConfigurationToSetup"
            @update-configuration="updateArrowConfiguration"
            @delete-configuration="deleteArrowConfiguration"
            @add-arrow-to-setup="addArrowToSetup"
          />
        </div>
      </div>
    </div>

    <!-- Create/Edit Bow Setup Modal -->
    <div v-if="showCreateSetupModal || editingSetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-lg shadow-lg">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {{ editingSetup ? 'Edit Bow Setup' : 'Create Bow Setup' }}
        </h3>
        <form @submit.prevent="saveBowSetup">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label for="setupName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Setup Name</label>
              <input 
                type="text" 
                id="setupName" 
                v-model="bowSetupForm.name" 
                class="form-input w-full" 
                required 
                placeholder="e.g., My Hunting Bow"
              />
            </div>
            <div>
              <label for="bowType" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bow Type</label>
              <select id="bowType" v-model="bowSetupForm.bow_type" class="form-select w-full" required>
                <option value="">Select Bow Type</option>
                <option value="compound">Compound</option>
                <option value="recurve">Recurve</option>
                <option value="longbow">Longbow</option>
                <option value="traditional">Traditional</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Draw Weight: <span class="font-semibold text-primary">{{ bowSetupForm.draw_weight || 45 }} lbs</span>
              </label>
              <md-slider
                ref="drawWeightSlider"
                min="20"
                max="80"
                :value="bowSetupForm.draw_weight || 45"
                @input="bowSetupForm.draw_weight = parseInt($event.target.value)"
                labeled
                ticks
                class="w-full"
              ></md-slider>
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                <span>20 lbs</span>
                <span>80 lbs</span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Draw Length: <span class="font-semibold text-primary">{{ bowSetupForm.draw_length || 28 }}"</span>
              </label>
              <md-slider
                ref="drawLengthSlider"
                min="24"
                max="34"
                step="0.25"
                :value="bowSetupForm.draw_length || 28"
                @input="bowSetupForm.draw_length = parseFloat($event.target.value)"
                labeled
                ticks
                class="w-full"
              ></md-slider>
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                <span>24"</span>
                <span>34"</span>
              </div>
            </div>
            <div class="md:col-span-2">
              <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description (optional)</label>
              <textarea 
                id="description" 
                v-model="bowSetupForm.description" 
                class="form-textarea w-full h-20 resize-y"
                placeholder="Description of this bow setup..."
              ></textarea>
            </div>
          </div>

          <div class="flex justify-end space-x-3 mt-6">
            <CustomButton
              type="button"
              @click="closeBowSetupModal"
              variant="outlined"
              class="text-gray-700 dark:text-gray-200"
            >
              Cancel
            </CustomButton>
            <CustomButton
              type="submit"
              variant="filled"
              :disabled="isSavingSetup"
              class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
            >
              <span v-if="isSavingSetup">Saving...</span>
              <span v-else>{{ editingSetup ? 'Update Setup' : 'Create Setup' }}</span>
            </CustomButton>
          </div>
          <p v-if="setupError" class="text-red-500 text-sm mt-3">{{ setupError }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBowConfigStore } from '~/stores/bowConfig'
import type { ArrowConfiguration, ArrowRecommendation, BowSetup } from '~/types/arrow'

// API
const api = useApi()

const bowConfigStore = useBowConfigStore()

// Reactive references from store
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)
const arrowSetupDescription = computed(() => bowConfigStore.arrowSetupDescription)
const isCompoundBow = computed(() => bowConfigStore.isCompoundBow)

// Store actions
const { updateBowConfig } = bowConfigStore


// Tab management
const activeTab = ref('tuning')

// Bow setups management
const bowSetups = ref<BowSetup[]>([])
const selectedBowSetup = ref<BowSetup | null>(null)
const showCreateSetupModal = ref(false)
const editingSetup = ref<BowSetup | null>(null)
const isSavingSetup = ref(false)
const setupError = ref('')

const bowSetupForm = ref({
  name: '',
  bow_type: '',
  draw_weight: 45,
  draw_length: 28,
  description: ''
})

// Arrow configurations state (now linked to bow setups)
const arrowConfigurations = ref<(ArrowConfiguration & { bow_setup_id?: number })[]>([])
const savedArrowSetups = ref([]) // Arrows saved from database recommendations


// Bow setup management functions
const selectBowSetup = (setup: BowSetup) => {
  selectedBowSetup.value = setup
}

const formatBowType = (bowType: string) => {
  if (!bowType || bowType.length === 0) return 'Unknown'
  return bowType.charAt(0).toUpperCase() + bowType.slice(1)
}

const createBowSetup = () => {
  showCreateSetupModal.value = true
  editingSetup.value = null
  bowSetupForm.value = {
    name: '',
    bow_type: '',
    draw_weight: 45,
    draw_length: 28,
    description: ''
  }
}

const editBowSetup = (setup: BowSetup) => {
  editingSetup.value = setup
  bowSetupForm.value = {
    name: setup.name,
    bow_type: setup.bow_config.bow_type,
    draw_weight: setup.bow_config.draw_weight,
    draw_length: setup.bow_config.draw_length,
    description: setup.description || ''
  }
  showCreateSetupModal.value = true
}

const closeBowSetupModal = () => {
  showCreateSetupModal.value = false
  editingSetup.value = null
  setupError.value = ''
}

const saveBowSetup = () => {
  isSavingSetup.value = true
  setupError.value = ''
  
  try {
    const setupData: BowSetup = {
      id: editingSetup.value?.id || Date.now(),
      name: bowSetupForm.value.name,
      bow_config: {
        bow_type: bowSetupForm.value.bow_type as any,
        draw_weight: Number(bowSetupForm.value.draw_weight),
        draw_length: Number(bowSetupForm.value.draw_length),
        arrow_material: 'Carbon', // Default
        arrow_rest_type: 'drop-away',
        nock_type: 'pin',
        vane_type: 'plastic',
        vane_length: 4,
        number_of_vanes: 3
      },
      arrow_configurations: [],
      description: bowSetupForm.value.description,
      created_at: editingSetup.value?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    if (editingSetup.value) {
      // Update existing setup
      const index = bowSetups.value.findIndex(s => s.id === editingSetup.value!.id)
      if (index !== -1) {
        bowSetups.value[index] = setupData
      }
    } else {
      // Add new setup
      bowSetups.value.push(setupData)
    }
    
    // Save to localStorage
    localStorage.setItem('bowSetups', JSON.stringify(bowSetups.value))
    
    closeBowSetupModal()
  } catch (error) {
    setupError.value = 'Failed to save bow setup. Please try again.'
    console.error('Error saving bow setup:', error)
  } finally {
    isSavingSetup.value = false
  }
}

const deleteBowSetup = (setup: BowSetup) => {
  if (confirm(`Are you sure you want to delete "${setup.name}"? This will also delete all associated arrow configurations.`)) {
    // Remove the bow setup
    const setupIndex = bowSetups.value.findIndex(s => s.id === setup.id)
    if (setupIndex !== -1) {
      bowSetups.value.splice(setupIndex, 1)
    }
    
    // Remove associated arrow configurations
    arrowConfigurations.value = arrowConfigurations.value.filter(config => config.bow_setup_id !== setup.id)
    
    // Clear selection if this setup was selected
    if (selectedBowSetup.value?.id === setup.id) {
      selectedBowSetup.value = null
    }
    
    // Save to localStorage
    localStorage.setItem('bowSetups', JSON.stringify(bowSetups.value))
    localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
  }
}

const getArrowConfigsForSetup = (setupId: number) => {
  return arrowConfigurations.value.filter(config => config.bow_setup_id === setupId)
}

// Arrow configuration management functions (updated to link to bow setups)
const addArrowConfigurationToSetup = (configData: ArrowConfiguration) => {
  if (!selectedBowSetup.value) return
  
  const newConfig = {
    ...configData,
    id: Date.now(),
    bow_setup_id: selectedBowSetup.value.id,
    created_at: new Date().toISOString()
  }
  arrowConfigurations.value.push(newConfig)
  localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
}

const addArrowConfiguration = (configData: ArrowConfiguration) => {
  const newConfig = {
    ...configData,
    id: Date.now(), // Simple ID generation for now
    created_at: new Date().toISOString()
  }
  arrowConfigurations.value.push(newConfig)
  // Store in localStorage for persistence
  localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
}

const updateArrowConfiguration = (configData: ArrowConfiguration) => {
  const index = arrowConfigurations.value.findIndex(config => config.id === configData.id)
  if (index !== -1) {
    arrowConfigurations.value[index] = configData
    // Store in localStorage for persistence
    localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
  }
}

const deleteArrowConfiguration = (configData: ArrowConfiguration) => {
  const index = arrowConfigurations.value.findIndex(config => config.id === configData.id)
  if (index !== -1) {
    arrowConfigurations.value.splice(index, 1)
    // Store in localStorage for persistence
    localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
  }
}

const addArrowToSetup = (data: { arrowConfig: ArrowConfiguration, arrowRecommendation: ArrowRecommendation }) => {
  const { arrowConfig, arrowRecommendation } = data
  
  // Create a saved arrow setup combining the configuration and database arrow
  const savedSetup = {
    id: Date.now(),
    arrow_config: arrowConfig,
    database_arrow: arrowRecommendation.arrow,
    spine_spec: arrowRecommendation.spine_specification,
    compatibility_score: arrowRecommendation.compatibility_score,
    match_percentage: arrowRecommendation.match_percentage,
    saved_at: new Date().toISOString()
  }
  
  savedArrowSetups.value.push(savedSetup)
  // Store in localStorage for persistence
  localStorage.setItem('savedArrowSetups', JSON.stringify(savedArrowSetups.value))
  
  // Show success message
  console.log(`Added ${arrowRecommendation.arrow.manufacturer} ${arrowRecommendation.arrow.model_name} to "${arrowConfig.name}" setup`)
}

const removeArrowSetup = (setup) => {
  const index = savedArrowSetups.value.findIndex(s => s.id === setup.id)
  if (index !== -1) {
    savedArrowSetups.value.splice(index, 1)
    // Store in localStorage for persistence
    localStorage.setItem('savedArrowSetups', JSON.stringify(savedArrowSetups.value))
  }
}

// Load saved configurations from localStorage
const loadSavedConfigurations = () => {
  if (process.client) {
    // Load bow setups
    const savedBowSetups = localStorage.getItem('bowSetups')
    if (savedBowSetups) {
      try {
        bowSetups.value = JSON.parse(savedBowSetups)
      } catch (error) {
        console.error('Error loading saved bow setups:', error)
      }
    }
    
    // Load arrow configurations
    const saved = localStorage.getItem('arrowConfigurations')
    if (saved) {
      try {
        arrowConfigurations.value = JSON.parse(saved)
      } catch (error) {
        console.error('Error loading saved configurations:', error)
      }
    }
    
    // Load saved arrow setups from database
    const savedSetups = localStorage.getItem('savedArrowSetups')
    if (savedSetups) {
      try {
        savedArrowSetups.value = JSON.parse(savedSetups)
      } catch (error) {
        console.error('Error loading saved setups:', error)
      }
    }
  }
}

// Load data on mount
onMounted(() => {
  loadSavedConfigurations()
})

// Set page title
useHead({
  title: 'Arrow Tuning Platform - Beta',
  meta: [
    { name: 'description', content: 'Professional arrow tuning platform for archery enthusiasts (Beta)' }
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