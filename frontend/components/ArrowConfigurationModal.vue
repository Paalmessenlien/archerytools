<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-lg">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Add Arrow Configuration</h3>
      
      <form @submit.prevent="saveArrowConfiguration">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Configuration Name -->
          <div class="md:col-span-2">
            <label for="configName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Configuration Name</label>
            <input 
              type="text" 
              id="configName" 
              v-model="configData.name" 
              class="form-input w-full" 
              required 
              placeholder="e.g., Target Setup 29-inch"
            />
          </div>

          <!-- Arrow Length Slider -->
          <div>
            <label class="block mb-3 text-sm font-medium text-gray-700 dark:text-gray-300">
              Arrow Length: <span class="font-semibold text-blue-600 dark:text-blue-400">{{ configData.arrow_length || 29 }}"</span>
            </label>
            <input 
              type="range" 
              min="24" 
              max="34" 
              step="0.25" 
              v-model.number="configData.arrow_length"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider"
            />
            <div class="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span>24"</span>
              <span>34"</span>
            </div>
          </div>

          <!-- Point Weight Slider -->
          <div>
            <label class="block mb-3 text-sm font-medium text-gray-700 dark:text-gray-300">
              Point Weight: <span class="font-semibold text-blue-600 dark:text-blue-400">{{ configData.point_weight || 100 }} grains</span>
            </label>
            <input 
              type="range" 
              min="50" 
              max="300" 
              step="5" 
              v-model.number="configData.point_weight"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider"
            />
            <div class="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span>50 gr</span>
              <span>300 gr</span>
            </div>
          </div>

          <!-- Nock Weight (Optional) -->
          <div>
            <label for="nockWeight" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Nock Weight (grains, optional)</label>
            <input 
              type="number" 
              id="nockWeight" 
              v-model.number="configData.nock_weight" 
              class="form-input w-full" 
              step="0.1" 
              min="0" 
              max="50"
            />
          </div>

          <!-- Fletching Weight (Optional) -->
          <div>
            <label for="fletchingWeight" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Fletching Weight (grains, optional)</label>
            <input 
              type="number" 
              id="fletchingWeight" 
              v-model.number="configData.fletching_weight" 
              class="form-input w-full" 
              step="0.1" 
              min="0" 
              max="100"
            />
          </div>

          <!-- Insert Weight (Optional) -->
          <div>
            <label for="insertWeight" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Insert Weight (grains, optional)</label>
            <input 
              type="number" 
              id="insertWeight" 
              v-model.number="configData.insert_weight" 
              class="form-input w-full" 
              step="0.1" 
              min="0" 
              max="100"
            />
          </div>

          <!-- Arrow Spine (Optional) -->
          <div>
            <label for="arrowSpine" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Arrow Spine (optional)</label>
            <input 
              type="number" 
              id="arrowSpine" 
              v-model.number="configData.arrow_spine" 
              class="form-input w-full" 
              step="1" 
              min="150" 
              max="1000"
            />
          </div>

          <!-- Shaft Model (Optional) -->
          <div>
            <label for="shaftModel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Shaft Model (optional)</label>
            <input 
              type="text" 
              id="shaftModel" 
              v-model="configData.shaft_model" 
              class="form-input w-full" 
              placeholder="e.g., Gold Tip Hunter"
            />
          </div>

          <!-- Shaft Manufacturer (Optional) -->
          <div>
            <label for="shaftManufacturer" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Shaft Manufacturer (optional)</label>
            <input 
              type="text" 
              id="shaftManufacturer" 
              v-model="configData.shaft_manufacturer" 
              class="form-input w-full" 
              placeholder="e.g., Gold Tip"
            />
          </div>

          <!-- Notes -->
          <div class="md:col-span-2">
            <label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Notes (optional)</label>
            <textarea 
              id="notes" 
              v-model="configData.notes" 
              class="form-textarea w-full h-20 resize-y"
              placeholder="Additional notes about this arrow configuration..."
            ></textarea>
          </div>
        </div>

        <!-- Calculated Values Display -->
        <div v-if="calculatedValues" class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Calculated Values</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-600 dark:text-gray-400">Total Weight:</span>
              <span class="font-medium ml-2">{{ calculatedValues.total_weight }} grains</span>
            </div>
            <div v-if="calculatedValues.calculated_foc">
              <span class="text-gray-600 dark:text-gray-400">FOC:</span>
              <span class="font-medium ml-2">{{ calculatedValues.calculated_foc }}%</span>
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-3 mt-6">
          <CustomButton
            type="button"
            @click="$emit('close')"
            variant="outlined"
            class="text-gray-700 dark:text-gray-200"
          >
            Cancel
          </CustomButton>
          <CustomButton
            type="submit"
            variant="filled"
            :disabled="isSaving"
            class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
          >
            <span v-if="isSaving">Saving...</span>
            <span v-else>{{ editingConfig ? 'Update Configuration' : 'Add Configuration' }}</span>
          </CustomButton>
        </div>
        <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ArrowConfiguration } from '~/types/arrow'

const props = defineProps({
  modelValue: Object as () => ArrowConfiguration | null,
  editingConfig: Object as () => ArrowConfiguration | null,
  isSaving: Boolean,
  error: String,
})

const emit = defineEmits(['update:modelValue', 'save', 'close'])

// Create a local ref to work with the form data
const configData = ref<ArrowConfiguration>({
  name: '',
  arrow_length: 29,
  point_weight: 100,
  nock_weight: null,
  fletching_weight: null,
  insert_weight: null,
  arrow_spine: null,
  shaft_model: '',
  shaft_manufacturer: '',
  notes: '',
})

// Watch for changes in the editing config prop
watch(() => props.editingConfig, (newValue) => {
  if (newValue) {
    configData.value = { ...newValue }
  } else {
    // Reset to defaults when not editing
    configData.value = {
      name: '',
      arrow_length: 29,
      point_weight: 100,
      nock_weight: null,
      fletching_weight: null,
      insert_weight: null,
      arrow_spine: null,
      shaft_model: '',
      shaft_manufacturer: '',
      notes: '',
    }
  }
}, { immediate: true })

// Calculated values
const calculatedValues = computed(() => {
  const pointWeight = configData.value.point_weight || 0
  const nockWeight = configData.value.nock_weight || 8 // Default nock weight
  const fletchingWeight = configData.value.fletching_weight || 12 // Default fletching weight
  const insertWeight = configData.value.insert_weight || 15 // Default insert weight
  
  const totalWeight = pointWeight + nockWeight + fletchingWeight + insertWeight
  
  // Basic FOC calculation (simplified)
  const arrowLength = configData.value.arrow_length || 29
  const frontWeight = pointWeight + insertWeight
  const totalArrowWeight = totalWeight + 250 // Estimate shaft weight
  const balancePoint = arrowLength / 2
  const frontOfCenter = ((frontWeight * arrowLength) / totalArrowWeight - balancePoint) / arrowLength * 100
  
  return {
    total_weight: Math.round(totalWeight),
    calculated_foc: frontOfCenter > 0 ? Math.round(frontOfCenter * 10) / 10 : null
  }
})

// Update configData with calculated values
watch(calculatedValues, (newValues) => {
  configData.value.total_weight = newValues.total_weight
  configData.value.calculated_foc = newValues.calculated_foc
}, { deep: true })

const saveArrowConfiguration = () => {
  emit('save', configData.value)
}
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
</style>