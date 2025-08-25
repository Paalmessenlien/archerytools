<template>
  <div :class="containerClasses">
    <!-- Icon -->
    <div v-if="icon || $slots.icon" class="mb-4">
      <slot name="icon">
        <div :class="iconClasses">
          <i :class="icon"></i>
        </div>
      </slot>
    </div>

    <!-- Title -->
    <div v-if="title || $slots.title" class="mb-2">
      <slot name="title">
        <h3 :class="titleClasses">
          {{ title }}
        </h3>
      </slot>
    </div>

    <!-- Description -->
    <div v-if="description || $slots.description" class="mb-6">
      <slot name="description">
        <p :class="descriptionClasses">
          {{ description }}
        </p>
      </slot>
    </div>

    <!-- Actions -->
    <div v-if="$slots.actions" class="flex flex-col sm:flex-row gap-3 justify-center">
      <slot name="actions" />
    </div>
  </div>
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
  icon: {
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
    default: 'default', // default, subtle
    validator: (value) => ['default', 'subtle'].includes(value)
  }
})

const containerClasses = computed(() => {
  const baseClasses = [
    'empty-state',
    'flex',
    'flex-col',
    'items-center',
    'justify-center',
    'text-center'
  ]

  // Size-based padding
  const sizeClasses = {
    small: ['p-6'],
    medium: ['p-8'],
    large: ['p-12']
  }

  // Variant classes
  const variantClasses = {
    default: [
      'bg-gray-50',
      'dark:bg-gray-800',
      'border',
      'border-gray-200',
      'dark:border-gray-700',
      'rounded-lg'
    ],
    subtle: []
  }

  return [
    ...baseClasses,
    ...sizeClasses[props.size],
    ...variantClasses[props.variant]
  ]
})

const iconClasses = computed(() => {
  const baseClasses = [
    'flex',
    'items-center',
    'justify-center',
    'rounded-full',
    'mx-auto'
  ]

  // Size classes for icon container
  const sizeClasses = {
    small: ['w-12', 'h-12', 'text-2xl'],
    medium: ['w-16', 'h-16', 'text-3xl'],
    large: ['w-20', 'h-20', 'text-4xl']
  }

  // Color classes
  const colorClasses = [
    'bg-gray-100',
    'dark:bg-gray-700',
    'text-gray-400',
    'dark:text-gray-500'
  ]

  return [
    ...baseClasses,
    ...sizeClasses[props.size],
    ...colorClasses
  ]
})

const titleClasses = computed(() => {
  const baseClasses = ['font-medium', 'text-gray-900', 'dark:text-gray-100']

  // Size classes for title
  const sizeClasses = {
    small: ['text-lg'],
    medium: ['text-xl'],
    large: ['text-2xl']
  }

  return [
    ...baseClasses,
    ...sizeClasses[props.size]
  ]
})

const descriptionClasses = computed(() => {
  const baseClasses = ['text-gray-600', 'dark:text-gray-400', 'max-w-md', 'mx-auto']

  // Size classes for description
  const sizeClasses = {
    small: ['text-sm'],
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
.empty-state {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  min-height: 200px;
}

/* Smooth fade-in animation */
.empty-state {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Ensure proper line height for description */
.empty-state p {
  line-height: 1.6;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .empty-state {
    min-height: 160px;
  }
}
</style>