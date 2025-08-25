<template>
  <div v-if="show" :class="containerClasses">
    <!-- Icon -->
    <div v-if="showIcon" :class="iconClasses">
      <i :class="iconName"></i>
    </div>

    <!-- Content -->
    <div class="flex-1">
      <!-- Title -->
      <div v-if="title" class="font-medium text-sm mb-1">
        {{ title }}
      </div>

      <!-- Message -->
      <div :class="messageClasses">
        <slot>
          {{ message }}
        </slot>
      </div>
    </div>

    <!-- Dismiss button -->
    <div v-if="dismissible">
      <CustomButton
        @click="handleDismiss"
        variant="text"
        size="small"
        class="!p-1 !min-h-0 opacity-70 hover:opacity-100"
        icon="fas fa-times"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CustomButton from './CustomButton.vue'

const props = defineProps({
  message: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'error', // error, warning, info, success
    validator: (value) => ['error', 'warning', 'info', 'success'].includes(value)
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  show: {
    type: Boolean,
    default: true
  },
  dismissible: {
    type: Boolean,
    default: false
  },
  showIcon: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['dismiss'])

const handleDismiss = () => {
  emit('dismiss')
}

const containerClasses = computed(() => {
  const baseClasses = [
    'flex',
    'items-start',
    'gap-3',
    'rounded-lg',
    'border',
    'transition-all',
    'duration-200'
  ]

  // Size classes
  const sizeClasses = {
    small: ['p-3', 'text-sm'],
    medium: ['p-4', 'text-sm'],
    large: ['p-5', 'text-base']
  }

  // Variant classes
  const variantClasses = {
    error: [
      'bg-red-50',
      'dark:bg-red-900/20',
      'border-red-200',
      'dark:border-red-800',
      'text-red-800',
      'dark:text-red-200'
    ],
    warning: [
      'bg-yellow-50',
      'dark:bg-yellow-900/20',
      'border-yellow-200',
      'dark:border-yellow-800',
      'text-yellow-800',
      'dark:text-yellow-200'
    ],
    info: [
      'bg-blue-50',
      'dark:bg-blue-900/20',
      'border-blue-200',
      'dark:border-blue-800',
      'text-blue-800',
      'dark:text-blue-200'
    ],
    success: [
      'bg-green-50',
      'dark:bg-green-900/20',
      'border-green-200',
      'dark:border-green-800',
      'text-green-800',
      'dark:text-green-200'
    ]
  }

  return [
    ...baseClasses,
    ...sizeClasses[props.size],
    ...variantClasses[props.variant]
  ]
})

const iconClasses = computed(() => {
  const baseClasses = ['flex-shrink-0', 'text-lg']

  // Icon color based on variant
  const variantIconClasses = {
    error: ['text-red-600', 'dark:text-red-400'],
    warning: ['text-yellow-600', 'dark:text-yellow-400'],
    info: ['text-blue-600', 'dark:text-blue-400'],
    success: ['text-green-600', 'dark:text-green-400']
  }

  return [
    ...baseClasses,
    ...variantIconClasses[props.variant]
  ]
})

const messageClasses = computed(() => {
  const baseClasses = ['leading-relaxed']
  
  // Size-based text classes
  const sizeTextClasses = {
    small: ['text-sm'],
    medium: ['text-sm'],
    large: ['text-base']
  }

  return [
    ...baseClasses,
    ...sizeTextClasses[props.size]
  ]
})

const iconName = computed(() => {
  const iconMap = {
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle',
    success: 'fas fa-check-circle'
  }
  return iconMap[props.variant]
})
</script>

<style scoped>
/* Smooth slide-in animation */
div {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Ensure proper font rendering */
div {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Better line height for readability */
div div {
  line-height: 1.5;
}
</style>