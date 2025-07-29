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

    <!-- Page Title for Quick Tuning -->
    <div class="mb-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 flex items-center">
        <i class="fas fa-crosshairs mr-2 text-indigo-600"></i>
        Quick Arrow Tuning
      </h2>
      <p class="text-gray-600 dark:text-gray-300 mt-1">Get instant arrow recommendations based on your bow configuration</p>
    </div>

    <!-- Quick Tuning Section -->
    <div class="card card-interactive glass-card">
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
  </div>
</template>

<script setup lang="ts">
import { useBowConfigStore } from '~/stores/bowConfig'
import type { ArrowConfiguration, ArrowRecommendation } from '~/types/arrow'

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


// Arrow configurations state
const arrowConfigurations = ref<ArrowConfiguration[]>([])
const savedArrowSetups = ref([]) // Arrows saved from database recommendations


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