<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
      <!-- Icon and Title -->
      <div class="flex items-center mb-4">
        <div class="w-12 h-12 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center mr-4 flex-shrink-0">
          <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 text-xl"></i>
        </div>
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
          {{ title || 'Confirm Deletion' }}
        </h3>
      </div>
      
      <!-- Message -->
      <div class="mb-6">
        <p class="text-gray-700 dark:text-gray-300">
          {{ message || 'Are you sure you want to delete this item? This action cannot be undone.' }}
        </p>
        <p v-if="itemName" class="text-sm text-gray-500 dark:text-gray-400 mt-2 font-medium">
          {{ itemName }}
        </p>
      </div>
      
      <!-- Actions -->
      <div class="flex justify-end space-x-3">
        <CustomButton
          @click="$emit('cancel')"
          variant="outlined"
          class="text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600"
        >
          Cancel
        </CustomButton>
        <CustomButton
          @click="$emit('confirm')"
          variant="filled"
          class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
          :disabled="loading"
        >
          <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>
          {{ confirmText || 'Delete' }}
        </CustomButton>
      </div>
      
      <!-- Error Message -->
      <p v-if="error" class="text-red-500 text-sm mt-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
        <i class="fas fa-exclamation-circle mr-1"></i>
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  message: String,
  itemName: String,
  confirmText: String,
  loading: Boolean,
  error: String
});

defineEmits(['confirm', 'cancel']);
</script>
