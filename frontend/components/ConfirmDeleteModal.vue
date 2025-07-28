<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg text-center">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Confirm Deletion</h3>
      <p class="text-gray-700 dark:text-gray-300 mb-6">Are you sure you want to delete this item?</p>
      <div class="flex justify-center space-x-4">
        <CustomButton
          @click="$emit('cancel')"
          variant="outlined"
          class="text-gray-700 dark:text-gray-200"
        >
          Cancel
        </CustomButton>
        <CustomButton
          @click="$emit('confirm')"
          variant="filled"
          class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
        >
          Delete
        </CustomButton>
      </div>
      <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  error: String,
});

defineEmits(['confirm', 'cancel']);
</script>
