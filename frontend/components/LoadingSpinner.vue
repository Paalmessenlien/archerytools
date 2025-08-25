<template>
  <div :class="containerClasses">
    <!-- Spinner -->
    <div :class="spinnerClasses">
      <div class="animate-spin rounded-full border-solid border-current">
        <div class="rounded-full border-transparent border-t-transparent border-l-transparent"></div>
      </div>
    </div>

    <!-- Loading text -->
    <div v-if="text || $slots.default" :class="textClasses">
      <slot>
        {{ text }}
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  variant: {
    type: String,
    default: 'primary', // primary, secondary, light, dark
    validator: (value) => ['primary', 'secondary', 'light', 'dark'].includes(value)
  },
  center: {
    type: Boolean,
    default: false
  },
  overlay: {
    type: Boolean,
    default: false
  }
})

const containerClasses = computed(() => {
  const baseClasses = ['loading-spinner-container']
  
  if (props.center) {
    baseClasses.push('flex', 'flex-col', 'items-center', 'justify-center')
  } else {
    baseClasses.push('flex', 'items-center')
  }

  if (props.overlay) {
    baseClasses.push(
      'fixed',
      'inset-0',
      'z-50',
      'bg-white',
      'bg-opacity-80',
      'dark:bg-gray-900',
      'dark:bg-opacity-80',
      'backdrop-blur-sm'
    )
  }

  return baseClasses
})

const spinnerClasses = computed(() => {
  const baseClasses = ['loading-spinner']
  
  // Size classes
  const sizeClasses = {
    small: ['w-4', 'h-4', 'border-2'],
    medium: ['w-6', 'h-6', 'border-2'],
    large: ['w-8', 'h-8', 'border-2']
  }

  // Variant classes for color
  const variantClasses = {
    primary: [
      'text-blue-600',
      'dark:text-purple-400'
    ],
    secondary: [
      'text-gray-600',
      'dark:text-gray-400'
    ],
    light: [
      'text-gray-300',
      'dark:text-gray-200'
    ],
    dark: [
      'text-gray-800',
      'dark:text-gray-800'
    ]
  }

  // Margin for text spacing
  if (!props.center && (props.text || '$slots.default')) {
    baseClasses.push('mr-2')
  } else if (props.center && (props.text || '$slots.default')) {
    baseClasses.push('mb-2')
  }

  return [
    ...baseClasses,
    ...sizeClasses[props.size],
    ...variantClasses[props.variant]
  ]
})

const textClasses = computed(() => {
  const baseClasses = ['loading-text', 'text-sm', 'font-medium']
  
  // Text color based on variant
  const variantTextClasses = {
    primary: [
      'text-blue-700',
      'dark:text-purple-300'
    ],
    secondary: [
      'text-gray-700',
      'dark:text-gray-300'
    ],
    light: [
      'text-gray-600',
      'dark:text-gray-200'
    ],
    dark: [
      'text-gray-900',
      'dark:text-gray-100'
    ]
  }

  return [
    ...baseClasses,
    ...variantTextClasses[props.variant]
  ]
})
</script>

<style scoped>
.loading-spinner-container {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Custom spinner animation */
.loading-spinner div {
  animation: spin 1s linear infinite;
  border-width: inherit;
  border-style: solid;
  border-color: currentColor;
  border-top-color: transparent;
  border-right-color: transparent;
  width: 100%;
  height: 100%;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Ensure spinner is always visible */
.loading-spinner {
  flex-shrink: 0;
}

/* Smooth fade-in animation */
.loading-spinner-container {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>