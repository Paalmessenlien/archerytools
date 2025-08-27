<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1100] p-4">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 sm:p-6 w-full max-w-sm sm:max-w-md shadow-lg">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Edit Profile</h3>
      <form @submit.prevent="saveProfile">
        <div class="mb-4">
          <label for="editedName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Full Name
          </label>
          <input
            type="text"
            id="editedName"
            v-model="nameInput"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
            required
          />
        </div>
        <div class="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3">
          <CustomButton
            type="button"
            @click="$emit('close')"
            variant="outlined"
            class="w-full sm:w-auto text-gray-700 dark:text-gray-200 h-12 sm:h-10"
          >
            Cancel
          </CustomButton>
          <CustomButton
            type="submit"
            variant="filled"
            :disabled="isSaving"
            class="w-full sm:w-auto bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 h-12 sm:h-10"
          >
            <span v-if="isSaving">Saving...</span>
            <span v-else>Save Changes</span>
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
  modelValue: String,
  isSaving: Boolean,
  error: String,
});

const emit = defineEmits(['update:modelValue', 'save', 'close']);

const nameInput = ref(props.modelValue);

watch(() => props.modelValue, (newValue) => {
  nameInput.value = newValue;
});

const saveProfile = () => {
  emit('save', nameInput.value);
};
</script>
