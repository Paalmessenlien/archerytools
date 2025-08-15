<template>
  <div class="relative inline-block">
    <!-- Question Mark Icon -->
    <button
      @click="toggleTooltip"
      @mouseenter="showTooltip"
      @mouseleave="hideTooltip"
      class="inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-400 dark:bg-gray-600 text-white text-xs hover:bg-gray-500 dark:hover:bg-gray-500 transition-colors cursor-help"
      type="button"
      :aria-label="`Information about ${title}`"
    >
      ?
    </button>
    
    <!-- Tooltip Content -->
    <div
      v-if="isVisible"
      class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-50"
      :class="{ 'sm:block': !isMobile, 'block': isMobile }"
    >
      <div class="bg-gray-900 dark:bg-gray-800 text-white text-xs rounded-lg p-3 shadow-lg max-w-xs w-max">
        <!-- Arrow pointing down -->
        <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-800"></div>
        
        <!-- Content -->
        <div class="font-semibold mb-1">{{ title }}</div>
        <div class="text-gray-200 dark:text-gray-300">{{ content }}</div>
        
        <!-- Close button for mobile -->
        <button
          v-if="isMobile"
          @click="hideTooltip"
          class="absolute top-1 right-1 w-5 h-5 rounded-full bg-gray-700 hover:bg-gray-600 flex items-center justify-center text-xs"
          type="button"
          aria-label="Close tooltip"
        >
          ×
        </button>
      </div>
    </div>
    
    <!-- Mobile backdrop -->
    <div
      v-if="isVisible && isMobile"
      @click="hideTooltip"
      class="fixed inset-0 bg-black bg-opacity-25 z-40"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  content: {
    type: String,
    required: true
  }
})

// State
const isVisible = ref(false)
const isMobile = ref(false)
let hideTimeout = null

// Check if device is mobile
const checkIsMobile = () => {
  isMobile.value = window.innerWidth < 768 || 'ontouchstart' in window
}

// Show tooltip
const showTooltip = () => {
  if (!isMobile.value) {
    clearTimeout(hideTimeout)
    isVisible.value = true
  }
}

// Hide tooltip
const hideTooltip = () => {
  if (!isMobile.value) {
    hideTimeout = setTimeout(() => {
      isVisible.value = false
    }, 150) // Small delay to allow moving to tooltip
  } else {
    isVisible.value = false
  }
}

// Toggle tooltip (for mobile)
const toggleTooltip = () => {
  if (isMobile.value) {
    isVisible.value = !isVisible.value
  }
}

// Lifecycle
onMounted(() => {
  checkIsMobile()
  window.addEventListener('resize', checkIsMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkIsMobile)
  clearTimeout(hideTimeout)
})
</script>