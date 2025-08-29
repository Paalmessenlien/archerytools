<template>
  <div class="flex items-center space-x-3">
    <!-- Toggle Switch -->
    <button
      @click="toggleDarkMode"
      class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-purple-500"
      :class="isDarkMode ? 'bg-purple-600' : 'bg-gray-300'"
      role="switch"
      :aria-checked="isDarkMode"
      aria-label="Toggle dark mode"
    >
      <span
        class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ease-in-out shadow-lg"
        :class="isDarkMode ? 'translate-x-6' : 'translate-x-1'"
      >
        <i 
          :class="isDarkMode ? 'fas fa-moon' : 'fas fa-sun'" 
          class="absolute inset-0 flex items-center justify-center text-xs transition-all duration-200"
          :style="{ color: isDarkMode ? '#8b5cf6' : '#f59e0b' }"
        ></i>
      </span>
    </button>
    
    <!-- Label -->
    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
      {{ isDarkMode ? 'Dark' : 'Light' }}
    </span>
  </div>
</template>

<script setup>
const { isDarkMode, toggleDarkMode } = useDarkMode()
</script>

<style scoped>
/* Enhanced focus styles for accessibility */
button:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.dark button:focus {
  box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.5);
}
</style>