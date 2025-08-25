<template>
  <button
    :class="buttonClasses"
    :disabled="disabled"
    :type="type"
    @click="$emit('click', $event)"
  >
    <i v-if="icon" :class="iconClasses" :style="iconStyle"></i>
    <slot></slot>
  </button>
</template>

<script setup>
defineEmits(['click'])

const props = defineProps({
  variant: {
    type: String,
    default: 'filled', // filled, outlined, text, primary
    validator: (value) => ['filled', 'outlined', 'text', 'primary'].includes(value)
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  icon: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'button'
  }
})

const buttonClasses = computed(() => {
  const baseClasses = [
    'inline-flex',
    'items-center',
    'justify-center',
    'font-medium',
    'rounded-lg',
    'transition-all',
    'duration-200',
    'cursor-pointer',
    'border',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-offset-2',
    // Mobile-first responsiveness
    'w-full',            // Full width by default on mobile
    'sm:w-auto',         // Auto width on small screens and up
    'max-w-full',        // Prevent overflow
    'min-w-0',           // Allow shrinking inside flex rows
    'text-center',       // Center label on full-width buttons
    'whitespace-normal'  // Allow wrapping to avoid overflow
  ]

  // Size classes
  const sizeClasses = {
    small: ['px-3', 'py-1.5', 'text-sm', 'min-h-[32px]'],
    medium: ['px-4', 'py-2', 'text-sm', 'min-h-[40px]'],
    large: ['px-6', 'py-3', 'text-base', 'min-h-[48px]']
  }

  // Variant classes
  const variantClasses = {
    filled: [
      'bg-gray-200',
      'text-black',
      'border-gray-200',
      'hover:bg-gray-300',
      'focus:ring-gray-300',
      'active:bg-gray-400',
      'dark:bg-gray-600',
      'dark:text-white',
      'dark:border-gray-600',
      'dark:hover:bg-gray-500',
      'dark:focus:ring-gray-500',
      'dark:active:bg-gray-700'
    ],
    primary: [
      'bg-blue-600',
      'text-white',
      'border-blue-600',
      'hover:bg-blue-700',
      'focus:ring-blue-500',
      'active:bg-blue-800',
      'dark:bg-purple-600',
      'dark:text-white',
      'dark:border-purple-600',
      'dark:hover:bg-purple-700',
      'dark:focus:ring-purple-500',
      'dark:active:bg-purple-800'
    ],
    outlined: [
      'bg-transparent',
      'text-gray-700',
      'border-gray-300',
      'hover:bg-gray-50',
      'focus:ring-gray-300',
      'dark:text-gray-300',
      'dark:border-gray-600',
      'dark:hover:bg-gray-800',
      'dark:focus:ring-gray-600'
    ],
    text: [
      'bg-transparent',
      'text-gray-700',
      'border-transparent',
      'hover:bg-gray-100',
      'focus:ring-gray-300',
      'dark:text-gray-300',
      'dark:hover:bg-gray-800',
      'dark:focus:ring-gray-600'
    ]
  }

  // Disabled classes
  const disabledClasses = props.disabled ? [
    'opacity-50',
    'cursor-not-allowed',
    'pointer-events-none'
  ] : []

  return [
    ...baseClasses,
    ...sizeClasses[props.size],
    ...variantClasses[props.variant],
    ...disabledClasses
  ]
})

const iconClasses = computed(() => {
  if (!props.icon) return []
  
  const baseIconClasses = [props.icon]
  
  // Add margin if there's slot content
  const marginClass = 'mr-2'
  
  return [...baseIconClasses, marginClass]
})

const iconStyle = computed(() => ({
  fontSize: props.size === 'small' ? '14px' : props.size === 'large' ? '18px' : '16px'
}))
</script>

<style scoped>
/* Ensure proper font rendering */
button {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  text-decoration: none;
  user-select: none;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Ensure icons display properly */
i {
  display: inline-block;
  font-style: normal;
  font-variant: normal;
  text-rendering: auto;
  line-height: 1;
}
</style>
