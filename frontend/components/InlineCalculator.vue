<template>
  <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
          <i class="fas fa-sliders-h text-blue-600 dark:text-blue-300"></i>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Edit Configuration</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">Adjust settings to recalculate arrow compatibility</p>
        </div>
      </div>
      <CustomButton
        @click="$emit('close')"
        variant="text"
        size="small"
        class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        <i class="fas fa-times"></i>
      </CustomButton>
    </div>

    <!-- Configuration Form -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Bow Type -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Bow Type
        </label>
        <md-filled-select
          :value="localConfig.bow_type"
          @change="updateConfig('bow_type', $event.target.value)"
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

      <!-- Draw Weight -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Draw Weight (lbs)
        </label>
        <md-filled-text-field
          :value="localConfig.draw_weight?.toString() || ''"
          @input="updateConfig('draw_weight', parseFloat($event.target.value) || 0)"
          type="number"
          min="10"
          max="150"
          step="0.5"
          class="w-full"
        />
      </div>

      <!-- Draw Length -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Draw Length (inches)
        </label>
        <md-filled-text-field
          :value="localConfig.draw_length?.toString() || ''"
          @input="updateConfig('draw_length', parseFloat($event.target.value) || 0)"
          type="number"
          min="20"
          max="36"
          step="0.25"
          class="w-full"
        />
      </div>

      <!-- Arrow Length -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Arrow Length (inches)
        </label>
        <md-filled-text-field
          :value="localConfig.arrow_length?.toString() || ''"
          @input="updateConfig('arrow_length', parseFloat($event.target.value) || 0)"
          type="number"
          min="20"
          max="36"
          step="0.5"
          class="w-full"
        />
      </div>

      <!-- Point Weight -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Point Weight (grains)
        </label>
        <md-filled-text-field
          :value="localConfig.point_weight?.toString() || ''"
          @input="updateConfig('point_weight', parseFloat($event.target.value) || 0)"
          type="number"
          min="40"
          max="300"
          step="5"
          class="w-full"
        />
      </div>

      <!-- Arrow Material -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Arrow Material
        </label>
        <md-filled-select
          :value="localConfig.arrow_material"
          @change="updateConfig('arrow_material', $event.target.value)"
          class="w-full"
        >
          <md-select-option value="carbon">
            <div slot="headline">Carbon</div>
          </md-select-option>
          <md-select-option value="aluminum">
            <div slot="headline">Aluminum</div>
          </md-select-option>
          <md-select-option value="carbon-aluminum">
            <div slot="headline">Carbon/Aluminum</div>
          </md-select-option>
          <md-select-option value="wood">
            <div slot="headline">Wood</div>
          </md-select-option>
        </md-filled-select>
      </div>
    </div>

    <!-- Additional Settings (Collapsible) -->
    <div class="mt-6">
      <button
        @click="showAdvanced = !showAdvanced"
        class="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
      >
        <i :class="showAdvanced ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="mr-2"></i>
        Advanced Settings
      </button>
      
      <div v-if="showAdvanced" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Arrow Rest Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Arrow Rest Type
            </label>
            <md-filled-select
              :value="localConfig.arrow_rest_type"
              @change="updateConfig('arrow_rest_type', $event.target.value)"
              class="w-full"
            >
              <md-select-option value="drop-away">
                <div slot="headline">Drop-Away</div>
              </md-select-option>
              <md-select-option value="whisker-biscuit">
                <div slot="headline">Whisker Biscuit</div>
              </md-select-option>
              <md-select-option value="shoot-through">
                <div slot="headline">Shoot-Through</div>
              </md-select-option>
              <md-select-option value="shelf">
                <div slot="headline">Shelf</div>
              </md-select-option>
            </md-filled-select>
          </div>

          <!-- Insert Weight -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Insert Weight (grains)
            </label>
            <md-filled-text-field
              :value="localConfig.insert_weight?.toString() || '0'"
              @input="updateConfig('insert_weight', parseFloat($event.target.value) || 0)"
              type="number"
              min="0"
              max="50"
              step="1"
              class="w-full"
            />
          </div>

          <!-- Nock Weight -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Nock Weight (grains)
            </label>
            <md-filled-text-field
              :value="localConfig.nock_weight?.toString() || '10'"
              @input="updateConfig('nock_weight', parseFloat($event.target.value) || 0)"
              type="number"
              min="5"
              max="30"
              step="1"
              class="w-full"
            />
          </div>

          <!-- Vane Weight Per -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Vane Weight Each (grains)
            </label>
            <md-filled-text-field
              :value="localConfig.vane_weight_per?.toString() || '5'"
              @input="updateConfig('vane_weight_per', parseFloat($event.target.value) || 0)"
              type="number"
              min="1"
              max="20"
              step="0.5"
              class="w-full"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="text-sm text-gray-500 dark:text-gray-400">
        Changes will recalculate compatibility automatically
      </div>
      <div class="flex space-x-3">
        <CustomButton
          @click="resetToOriginal"
          variant="outlined"
          size="small"
          class="text-gray-600 border-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-400 dark:hover:bg-gray-700"
        >
          Reset
        </CustomButton>
        <CustomButton
          @click="applyChanges"
          variant="filled"
          size="small"
          class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800"
        >
          <i class="fas fa-check mr-2"></i>
          Apply Changes
        </CustomButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isRecalculating" class="absolute inset-0 bg-white dark:bg-gray-800 bg-opacity-75 dark:bg-opacity-75 flex items-center justify-center rounded-xl">
      <div class="flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 dark:border-blue-400"></div>
        <span class="text-gray-700 dark:text-gray-300">Recalculating...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BowConfiguration } from '~/types/arrow'

// Props
interface Props {
  bowConfig: BowConfiguration
  isRecalculating?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isRecalculating: false
})

// Emits
const emit = defineEmits<{
  close: []
  update: [config: BowConfiguration]
  apply: [config: BowConfiguration]
}>()

// State
const localConfig = ref<BowConfiguration>({ ...props.bowConfig })
const showAdvanced = ref(false)

// Watch for external config changes
watch(() => props.bowConfig, (newConfig) => {
  localConfig.value = { ...newConfig }
}, { deep: true })

// Methods
const updateConfig = (key: keyof BowConfiguration, value: any) => {
  localConfig.value = {
    ...localConfig.value,
    [key]: value
  }
  
  // Emit update for real-time recalculation
  emit('update', localConfig.value)
}

const resetToOriginal = () => {
  localConfig.value = { ...props.bowConfig }
  emit('update', localConfig.value)
}

const applyChanges = () => {
  emit('apply', localConfig.value)
}
</script>

<style scoped>
/* Material Design field styling fixes */
md-filled-text-field,
md-filled-select {
  --md-filled-field-container-color: rgb(245 245 245);
}

:is(.dark) md-filled-text-field,
:is(.dark) md-filled-select {
  --md-filled-field-container-color: rgb(55 65 81);
  --md-filled-field-label-text-color: rgb(156 163 175);
  --md-filled-field-input-text-color: rgb(243 244 246);
}
</style>