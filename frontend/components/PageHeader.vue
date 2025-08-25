<template>
  <header :class="headerClasses">
    <!-- Title Section -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <!-- Title and Subtitle -->
      <div class="flex-1 min-w-0">
        <!-- Main Title -->
        <h1 :class="titleClasses">
          <slot name="title">
            {{ title }}
          </slot>
        </h1>
        
        <!-- Subtitle -->
        <div v-if="subtitle || $slots.subtitle" :class="subtitleClasses">
          <slot name="subtitle">
            {{ subtitle }}
          </slot>
        </div>
        
        <!-- Breadcrumbs -->
        <nav v-if="breadcrumbs && breadcrumbs.length" class="mt-2" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <li v-for="(crumb, index) in breadcrumbs" :key="index" class="flex items-center">
              <template v-if="index > 0">
                <i class="fas fa-chevron-right mx-2 text-xs"></i>
              </template>
              <NuxtLink
                v-if="crumb.to"
                :to="crumb.to"
                class="hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
              >
                {{ crumb.label }}
              </NuxtLink>
              <span v-else class="text-gray-900 dark:text-gray-100 font-medium">
                {{ crumb.label }}
              </span>
            </li>
          </ol>
        </nav>
      </div>
      
      <!-- Actions -->
      <div v-if="$slots.actions" class="flex-shrink-0">
        <div class="flex items-center gap-3">
          <slot name="actions" />
        </div>
      </div>
    </div>
    
    <!-- Additional Content -->
    <div v-if="$slots.content" class="mt-6">
      <slot name="content" />
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
  subtitle: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'large', // small, medium, large, xl
    validator: (value) => ['small', 'medium', 'large', 'xl'].includes(value)
  },
  variant: {
    type: String,
    default: 'default', // default, bordered, contained
    validator: (value) => ['default', 'bordered', 'contained'].includes(value)
  },
  breadcrumbs: {
    type: Array,
    default: () => []
  }
})

const headerClasses = computed(() => {
  const baseClasses = ['page-header']
  
  // Spacing classes
  const spacingClasses = {
    small: ['py-4'],
    medium: ['py-6'],
    large: ['py-8'],
    xl: ['py-12']
  }
  
  // Variant classes
  const variantClasses = {
    default: [],
    bordered: [
      'border-b',
      'border-gray-200',
      'dark:border-gray-700',
      'pb-6',
      'mb-8'
    ],
    contained: [
      'bg-white',
      'dark:bg-gray-800',
      'rounded-lg',
      'p-6',
      'border',
      'border-gray-200',
      'dark:border-gray-700',
      'shadow-sm'
    ]
  }
  
  return [
    ...baseClasses,
    ...spacingClasses[props.size],
    ...variantClasses[props.variant]
  ]
})

const titleClasses = computed(() => {
  const baseClasses = [
    'font-bold',
    'text-gray-900',
    'dark:text-gray-100',
    'tracking-tight',
    'leading-tight'
  ]
  
  // Size classes
  const sizeClasses = {
    small: ['text-xl', 'sm:text-2xl'],
    medium: ['text-2xl', 'sm:text-3xl'],
    large: ['text-3xl', 'sm:text-4xl'],
    xl: ['text-4xl', 'sm:text-5xl']
  }
  
  return [
    ...baseClasses,
    ...sizeClasses[props.size]
  ]
})

const subtitleClasses = computed(() => {
  const baseClasses = [
    'mt-2',
    'text-gray-600',
    'dark:text-gray-400',
    'max-w-2xl'
  ]
  
  // Size classes
  const sizeClasses = {
    small: ['text-sm'],
    medium: ['text-base'],
    large: ['text-lg'],
    xl: ['text-xl']
  }
  
  return [
    ...baseClasses,
    ...sizeClasses[props.size]
  ]
})
</script>

<style scoped>
.page-header {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Ensure proper line heights for titles */
h1 {
  line-height: 1.2;
  word-wrap: break-word;
}

/* Smooth transitions for interactive elements */
a {
  transition: color 0.15s ease-in-out;
}

/* Mobile optimization */
@media (max-width: 640px) {
  .page-header h1 {
    word-break: break-word;
  }
}
</style>