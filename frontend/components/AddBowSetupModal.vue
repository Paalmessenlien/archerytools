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
            <input type="number" id="drawWeight" v-model.number="setupData.draw_weight" class="form-input" required step="0.1" />
          </div>
          <div class="mb-4">
            <label for="drawLength" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Draw Length (inches)</label>
            <input type="number" id="drawLength" v-model.number="setupData.draw_length" class="form-input" required step="0.1" />
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
  description: '',
});

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
