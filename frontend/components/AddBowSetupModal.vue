<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-lg shadow-lg">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Add New Bow Setup</h3>
      <form @submit.prevent="saveBowSetup">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="mb-4">
            <label for="setupName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Setup Name</label>
            <input type="text" id="setupName" v-model="setupData.name" class="form-input" required />
          </div>
          <div class="mb-4">
            <label for="bowType" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bow Type</label>
            <select id="bowType" v-model="setupData.bow_type" class="form-select" required>
              <option value="">Select Bow Type</option>
              <option value="compound">Compound</option>
              <option value="recurve">Recurve</option>
              <option value="longbow">Longbow</option>
              <option value="traditional">Traditional</option>
            </select>
          </div>
          <div class="mb-4">
            <label for="drawWeight" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Draw Weight (lbs)</label>
            <input type="number" id="drawWeight" v-model.number="setupData.draw_weight" class="form-input" required step="0.5" />
          </div>
          <div class="mb-4">
            <label for="drawLength" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Draw Length (inches)</label>
            <input type="number" id="drawLength" v-model.number="setupData.draw_length" class="form-input" required step="0.1" />
          </div>
          <div class="mb-4">
            <label for="arrowLength" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Arrow Length (inches)</label>
            <input type="number" id="arrowLength" v-model.number="setupData.arrow_length" class="form-input" required step="0.1" />
          </div>
          <div class="mb-4">
            <label for="pointWeight" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Point Weight (gn)</label>
            <input type="number" id="pointWeight" v-model.number="setupData.point_weight" class="form-input" required step="0.5" min="40" />
          </div>
        </div>
        
        <!-- Bow Brand and Model Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4" v-if="setupData.bow_type === 'recurve' || setupData.bow_type === 'traditional'">
          <div>
            <label for="riserBrand" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Riser Brand</label>
            <select id="riserBrand" v-model="setupData.riser_brand" class="form-select">
              <option value="">Select Riser Brand</option>
              <option value="Hoyt">Hoyt</option>
              <option value="Win&Win">Win&Win</option>
              <option value="Sebastian Flute">Sebastian Flute</option>
              <option value="Gillo">Gillo</option>
              <option value="Samick">Samick</option>
              <option value="KTA">KTA</option>
              <option value="Border">Border</option>
              <option value="Dryad">Dryad</option>
              <option value="Bear">Bear</option>
              <option value="Martin">Martin</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label for="riserModel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Riser Model</label>
            <input type="text" id="riserModel" v-model="setupData.riser_model" class="form-input" placeholder="e.g., Satori, Formula Xi" />
          </div>
          <div>
            <label for="limbBrand" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Limb Brand</label>
            <select id="limbBrand" v-model="setupData.limb_brand" class="form-select">
              <option value="">Select Limb Brand</option>
              <option value="Uukha">Uukha</option>
              <option value="Win&Win">Win&Win</option>
              <option value="Hoyt">Hoyt</option>
              <option value="KTA">KTA</option>
              <option value="SF Archery">SF Archery</option>
              <option value="Border">Border</option>
              <option value="Samick">Samick</option>
              <option value="Bear">Bear</option>
              <option value="Martin">Martin</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label for="limbModel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Limb Model</label>
            <input type="text" id="limbModel" v-model="setupData.limb_model" class="form-input" placeholder="e.g., VX1000, Storm" />
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4" v-if="setupData.bow_type === 'compound'">
          <div>
            <label for="compoundBrand" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Compound Bow Brand</label>
            <select id="compoundBrand" v-model="setupData.compound_brand" class="form-select">
              <option value="">Select Compound Brand</option>
              <option value="Mathews">Mathews</option>
              <option value="Hoyt">Hoyt</option>
              <option value="PSE">PSE</option>
              <option value="Bowtech">Bowtech</option>
              <option value="Bear">Bear</option>
              <option value="Prime">Prime</option>
              <option value="Elite">Elite</option>
              <option value="Mission">Mission</option>
              <option value="Diamond">Diamond</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label for="compoundModel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Compound Bow Model</label>
            <input type="text" id="compoundModel" v-model="setupData.compound_model" class="form-input" placeholder="e.g., V3X 33, RX-7 Ultra" />
          </div>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bow Usage</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="usage in usageOptions"
              :key="usage"
              type="button"
              @click="toggleUsage(usage)"
              :class="[
                'px-3 py-1 text-sm rounded-full border transition-colors',
                isUsageSelected(usage)
                  ? 'bg-blue-500 text-white border-blue-500 dark:bg-purple-600 dark:border-purple-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
              ]"
            >
              {{ usage }}
            </button>
          </div>
        </div>
        <div class="mb-4">
          <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description (optional)</label>
          <textarea id="description" v-model="setupData.description" class="form-textarea"></textarea>
        </div>

        <div class="flex justify-end space-x-3">
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
            <span v-else>Add Setup</span>
          </CustomButton>
        </div>
        <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: Object, // Represents newSetup object
  isSaving: Boolean,
  error: String,
});

const emit = defineEmits(['update:modelValue', 'save', 'close']);

// Create a local ref to work with the form data
const setupData = ref({
  name: '',
  bow_type: '',
  draw_weight: null,
  draw_length: null,
  arrow_length: null,
  point_weight: 100,
  description: '',
  riser_brand: '',
  riser_model: '',
  limb_brand: '',
  limb_model: '',
  compound_brand: '',
  compound_model: '',
  bow_usage: [],
});

const usageOptions = ['Target', 'Field', '3D', 'Hunting'];

const toggleUsage = (usage) => {
  const index = setupData.value.bow_usage.indexOf(usage);
  if (index > -1) {
    setupData.value.bow_usage.splice(index, 1);
  } else {
    setupData.value.bow_usage.push(usage);
  }
};

const isUsageSelected = (usage) => {
  return setupData.value.bow_usage.includes(usage);
};

// Watch for changes in the modelValue prop and update local setupData
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    setupData.value = { ...newValue };
  }
}, { immediate: true });

const saveBowSetup = () => {
  emit('save', setupData.value);
};
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
.form-textarea {
  @apply w-full h-24 resize-y;
}
</style>
