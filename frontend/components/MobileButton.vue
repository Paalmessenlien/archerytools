<template>
  <button
    :type="type"
    :class="[
      'mobile-button',
      variantClasses,
      sizeClasses,
      { 'opacity-50 cursor-not-allowed': disabled }
    ]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger', 'text'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  type: {
    type: String,
    default: 'button'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 dark:bg-purple-600 dark:hover:bg-purple-700 dark:active:bg-purple-800',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 active:bg-gray-400 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 dark:active:bg-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 dark:bg-red-700 dark:hover:bg-red-800 dark:active:bg-red-900',
    text: 'bg-transparent text-blue-600 hover:bg-blue-50 active:bg-blue-100 dark:text-purple-400 dark:hover:bg-gray-800 dark:active:bg-gray-700'
  }
  return variants[props.variant]
})

const sizeClasses = computed(() => {
  const sizes = {
    small: 'px-3 py-2 text-sm min-h-[36px]',
    medium: 'px-4 py-3 text-base min-h-[44px]',
    large: 'px-6 py-4 text-lg min-h-[52px]'
  }
  return sizes[props.size]
})
</script>

<style scoped>
.mobile-button {
  @apply inline-flex items-center justify-center font-medium rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-purple-500;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

@media (hover: none) {
  .mobile-button:active {
    transform: scale(0.95);
  }
}
</style>