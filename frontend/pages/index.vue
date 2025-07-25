<template>
  <div>
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Bow Configuration</h1>
      <p class="text-gray-600 dark:text-gray-300">Configure your bow setup to get personalized arrow recommendations</p>
    </div>

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

        <!-- Arrow Type -->
        <div>
          <md-filled-select
            ref="arrowTypeSelect"
            label="Arrow Type"
            :value="bowConfig.arrow_type"
            @change="updateBowConfig({ arrow_type: $event.target.value })"
            class="w-full"
          >
            <md-select-option value="">
              <div slot="headline">Any Type</div>
            </md-select-option>
            <md-select-option v-for="arrowType in availableArrowTypes" :key="arrowType.arrow_type" :value="arrowType.arrow_type">
              <div slot="headline">{{ formatArrowType(arrowType.arrow_type) }} ({{ arrowType.count }} arrows)</div>
            </md-select-option>
          </md-filled-select>
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
            Arrow Length: <span class="font-semibold text-primary">{{ bowConfig.arrow_length }}"</span>
          </label>
          <md-slider
            ref="arrowLengthSlider"
            min="24"
            max="34"
            step="0.25"
            :value="bowConfig.arrow_length"
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

        <!-- Arrow Material -->
        <div>
          <md-filled-select
            ref="arrowMaterialSelect"
            label="Arrow Material"
            :value="bowConfig.arrow_material"
            @change="updateBowConfig({ arrow_material: $event.target.value })"
            class="w-full"
          >
            <md-select-option value="">
              <div slot="headline">Any Material</div>
            </md-select-option>
            <md-select-option 
              v-for="material in availableMaterials" 
              :key="material.material" 
              :value="material.material"
            >
              <div slot="headline">{{ material.material }} ({{ material.count }} arrows)</div>
            </md-select-option>
          </md-filled-select>
        </div>

        <!-- Point Weight -->
        <div>
          <md-filled-select
            ref="pointWeightSelect"
            label="Point Weight (grains)"
            :value="bowConfig.point_weight"
            @change="updateBowConfig({ point_weight: parseInt($event.target.value) })"
            class="w-full"
          >
            <md-select-option value="75">
              <div slot="headline">75 grains</div>
            </md-select-option>
            <md-select-option value="100">
              <div slot="headline">100 grains</div>
            </md-select-option>
            <md-select-option value="125">
              <div slot="headline">125 grains</div>
            </md-select-option>
            <md-select-option value="150">
              <div slot="headline">150 grains</div>
            </md-select-option>
          </md-filled-select>
        </div>

      </div>

      <!-- Advanced Setup Accordion -->
      <div class="mt-6">
        <button
          @click="showAdvancedSetup = !showAdvancedSetup"
          class="flex items-center justify-between w-full px-4 py-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            <i class="fas fa-cogs mr-2 text-indigo-600"></i>
            Advanced Setup Options
          </span>
          <svg
            :class="{ 'rotate-180': showAdvancedSetup }"
            class="w-5 h-5 text-gray-500 dark:text-gray-400 transform transition-transform duration-200"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>

        <div 
          v-show="showAdvancedSetup"
          class="mt-4 p-6 bg-gray-50/50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
        >
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Arrow Rest Type (only for compound) -->
            <div v-if="isCompoundBow">
              <md-filled-select
                ref="arrowRestSelect"
                label="Arrow Rest Type"
                :value="bowConfig.arrow_rest_type"
                @change="updateBowConfig({ arrow_rest_type: $event.target.value })"
                class="w-full"
              >
                <md-select-option value="drop-away">
                  <div slot="headline">Drop Away</div>
                </md-select-option>
                <md-select-option value="whisker-biscuit">
                  <div slot="headline">Whisker Biscuit</div>
                </md-select-option>
                <md-select-option value="blade">
                  <div slot="headline">Blade Rest</div>
                </md-select-option>
              </md-filled-select>
            </div>

            <!-- Nock Type -->
            <div>
              <md-filled-select
                ref="nockTypeSelect"
                label="Nock Type"
                :value="bowConfig.nock_type"
                @change="updateBowConfig({ nock_type: $event.target.value })"
                class="w-full"
              >
                <md-select-option value="pin">
                  <div slot="headline">Pin Nock</div>
                </md-select-option>
                <md-select-option value="press-fit">
                  <div slot="headline">Press-Fit</div>
                </md-select-option>
                <md-select-option value="over-nock">
                  <div slot="headline">Over Nock</div>
                </md-select-option>
                <md-select-option value="lighted">
                  <div slot="headline">Lighted Nock</div>
                </md-select-option>
                <md-select-option value="half-moon">
                  <div slot="headline">Half-Moon</div>
                </md-select-option>
              </md-filled-select>
            </div>

            <!-- Vane Type -->
            <div>
              <md-filled-select
                ref="vaneTypeSelect"
                label="Vane Type"
                :value="bowConfig.vane_type"
                @change="updateBowConfig({ vane_type: $event.target.value })"
                class="w-full"
              >
                <md-select-option value="plastic">
                  <div slot="headline">Plastic Vanes</div>
                </md-select-option>
                <md-select-option value="feather">
                  <div slot="headline">Natural Feathers</div>
                </md-select-option>
                <md-select-option value="hybrid">
                  <div slot="headline">Hybrid Vanes</div>
                </md-select-option>
                <md-select-option value="blazer">
                  <div slot="headline">Blazer Vanes</div>
                </md-select-option>
                <md-select-option value="helical">
                  <div slot="headline">Helical Vanes</div>
                </md-select-option>
              </md-filled-select>
            </div>

            <!-- Vane Length -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Vane Length: <span class="font-semibold text-primary">{{ bowConfig.vane_length }}"</span>
              </label>
              <md-slider
                ref="vaneLengthSlider"
                min="2"
                max="5"
                step="0.25"
                :value="bowConfig.vane_length"
                @input="updateBowConfig({ vane_length: parseFloat($event.target.value) })"
                labeled
                ticks
                class="w-full"
              ></md-slider>
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                <span>2"</span>
                <span>5"</span>
              </div>
            </div>

            <!-- Number of Vanes -->
            <div>
              <md-filled-select
                ref="numberOfVanesSelect"
                label="Number of Vanes"
                :value="bowConfig.number_of_vanes"
                @change="updateBowConfig({ number_of_vanes: parseInt($event.target.value) })"
                class="w-full"
              >
                <md-select-option value="3">
                  <div slot="headline">3 Vanes</div>
                </md-select-option>
                <md-select-option value="4">
                  <div slot="headline">4 Vanes</div>
                </md-select-option>
              </md-filled-select>
            </div>
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
        <ArrowRecommendationsList />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'

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

// Materials state
const availableMaterials = ref([])

// Arrow types state
const availableArrowTypes = ref([])

// Advanced setup accordion state
const showAdvancedSetup = ref(false)

// Load materials from API
const loadMaterials = async () => {
  try {
    const materials = await api.getMaterials()
    availableMaterials.value = materials || []
  } catch (error) {
    console.error('Error loading materials:', error)
    // Fallback to hardcoded materials
    availableMaterials.value = [
      { material: 'Carbon', count: 0 },
      { material: 'Carbon / Aluminum', count: 0 },
      { material: 'Aluminum', count: 0 },
      { material: 'Wood', count: 0 }
    ]
  }
}

// Load arrow types from API
const loadArrowTypes = async () => {
  try {
    const arrowTypes = await api.getArrowTypes()
    availableArrowTypes.value = arrowTypes || []
  } catch (error) {
    console.error('Error loading arrow types:', error)
    // Fallback to common arrow types
    availableArrowTypes.value = [
      { arrow_type: 'hunting', count: 0 },
      { arrow_type: 'target', count: 0 },
      { arrow_type: '3d', count: 0 },
      { arrow_type: 'indoor', count: 0 },
      { arrow_type: 'outdoor', count: 0 }
    ]
  }
}

// Format arrow type for display
const formatArrowType = (arrowType) => {
  if (!arrowType) return 'Unknown'
  
  const formatted = arrowType
    .split(/[-_\s]+/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
  
  return formatted
}

// Load data on mount
onMounted(() => {
  loadMaterials()
  loadArrowTypes()
})

// Set page title
useHead({
  title: 'Bow Setup',
  meta: [
    { name: 'description', content: 'Configure your bow setup for personalized arrow recommendations' }
  ]
})
</script>