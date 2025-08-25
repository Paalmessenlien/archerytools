<template>
  <header :class="headerClasses">
    <div class="flex items-center justify-between">
      <!-- Title and Description -->
      <div class="flex-1 min-w-0">
        <!-- Title -->
        <component :is="headingTag" :class="titleClasses">
          <slot name="title">
            {{ title }}
          </slot>
        </component>
        
        <!-- Description -->
        <div v-if="description || $slots.description" :class="descriptionClasses">
          <slot name="description">
            {{ description }}
          </slot>
        </div>
      </div>
      
      <!-- Actions -->
      <div v-if="$slots.actions" class="flex-shrink-0 ml-4">
        <div class="flex items-center gap-2">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  level: {
    type: Number,
    default: 2,
    validator: (value) => value >= 1 && value <= 6
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  spacing: {
    type: String,
    default: 'normal', // compact, normal, relaxed
    validator: (value) => ['compact', 'normal', 'relaxed'].includes(value)
  },
  divider: {
    type: Boolean,
    default: false
  }
})

const headingTag = computed(() => `h${props.level}`)

const headerClasses = computed(() => {
  const baseClasses = ['section-header']
  
  // Spacing classes
  const spacingClasses = {
    compact: ['mb-3'],
    normal: ['mb-6'],
    relaxed: ['mb-8']
  }
  
  // Divider classes
  if (props.divider) {
    baseClasses.push(
      'pb-4',
      'border-b',
      'border-gray-200',
      'dark:border-gray-700'
    )
  }
  
  return [
    ...baseClasses,
    ...spacingClasses[props.spacing]
  ]
})

const titleClasses = computed(() => {
  const baseClasses = [
    'font-semibold',
    'text-gray-900',
    'dark:text-gray-100',
    'tracking-tight'
  ]
  
  // Size classes based on both size prop and heading level
  const sizeClasses = {
    small: {
      1: ['text-2xl'],
      2: ['text-xl'],
      3: ['text-lg'],
      4: ['text-base'],
      5: ['text-sm'],
      6: ['text-sm']
    },
    medium: {
      1: ['text-3xl'],
      2: ['text-2xl'],
      3: ['text-xl'],
      4: ['text-lg'],
      5: ['text-base'],
      6: ['text-base']
    },
    large: {
      1: ['text-4xl'],
      2: ['text-3xl'],
      3: ['text-2xl'],
      4: ['text-xl'],
      5: ['text-lg'],
      6: ['text-lg']
    }
  }
  
  return [
    ...baseClasses,
    ...sizeClasses[props.size][props.level]
  ]
})

const descriptionClasses = computed(() => {
  const baseClasses = [
    'mt-1',
    'text-gray-600',
    'dark:text-gray-400',
    'max-w-2xl'
  ]
  
  // Size classes for description
  const sizeClasses = {
    small: ['text-xs'],
    medium: ['text-sm'],
    large: ['text-base']
  }
  
  return [
    ...baseClasses,
    ...sizeClasses[props.size]
  ]
})
</script>

<style scoped>
.section-header {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Ensure proper line heights */
h1, h2, h3, h4, h5, h6 {
  line-height: 1.3;
  margin: 0;
}

/* Mobile optimization */
@media (max-width: 640px) {
  .section-header {
    word-break: break-word;
  }
  
  /* Stack title and actions on mobile for very long titles */
  .section-header > div {
    @apply flex-col items-start gap-3;
  }
  
  .section-header > div > div:last-child {
    @apply ml-0 self-stretch;
  }
  
  /* Center actions on mobile */
  .section-header > div > div:last-child > div {
    @apply justify-center;
  }
}
</style>