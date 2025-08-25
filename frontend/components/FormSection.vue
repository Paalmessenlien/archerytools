<template>
  <section :class="sectionClasses">
    <!-- Section Header -->
    <header v-if="title || description || $slots.header" class="form-section-header mb-6">
      <slot name="header">
        <div v-if="title || description">
          <h3 v-if="title" class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {{ title }}
          </h3>
          <p v-if="description" class="text-sm text-gray-600 dark:text-gray-400">
            {{ description }}
          </p>
        </div>
      </slot>
    </header>

    <!-- Section Content -->
    <div class="form-section-content">
      <slot />
    </div>

    <!-- Section Footer -->
    <footer v-if="$slots.footer" class="form-section-footer mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
      <slot name="footer" />
    </footer>
  </section>
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
  variant: {
    type: String,
    default: 'default', // default, card, bordered
    validator: (value) => ['default', 'card', 'bordered'].includes(value)
  },
  spacing: {
    type: String,
    default: 'normal', // compact, normal, relaxed
    validator: (value) => ['compact', 'normal', 'relaxed'].includes(value)
  }
})

const sectionClasses = computed(() => {
  const baseClasses = ['form-section']
  
  // Variant classes
  const variantClasses = {
    default: [],
    card: [
      'bg-white',
      'dark:bg-gray-800',
      'rounded-lg',
      'p-6',
      'border',
      'border-gray-200',
      'dark:border-gray-700',
      'shadow-sm'
    ],
    bordered: [
      'border',
      'border-gray-200',
      'dark:border-gray-700',
      'rounded-lg',
      'p-6'
    ]
  }
  
  // Spacing classes  
  const spacingClasses = {
    compact: 'mb-6',
    normal: 'mb-8', 
    relaxed: 'mb-12'
  }
  
  return [
    ...baseClasses,
    ...variantClasses[props.variant],
    spacingClasses[props.spacing]
  ]
})
</script>

<style scoped>
.form-section {
  width: 100%;
}

/* Ensure proper typography hierarchy */
.form-section-header h3 {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 500;
  line-height: 1.5;
}

.form-section-header p {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
}

/* Mobile responsive adjustments */
@media (max-width: 640px) {
  .form-section.bg-white,
  .form-section.border {
    @apply px-4 py-4;
  }
  
  .form-section-header {
    @apply mb-4;
  }
  
  .form-section-footer {
    @apply mt-4 pt-4;
  }
}

/* Focus-within styling for better UX */
.form-section:focus-within {
  /* Subtle focus indication for the entire section */
}

/* Ensure proper contrast in dark mode */
@media (prefers-color-scheme: dark) {
  .form-section.bg-white {
    background-color: rgb(31 41 55); /* gray-800 */
  }
}
</style>