<template>
  <div class="custom-select-wrapper">
    <!-- Label -->
    <label
      v-if="label"
      :for="selectId"
      :class="labelClasses"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Select Container -->
    <div class="relative">
      <select
        :id="selectId"
        :class="selectClasses"
        :disabled="disabled"
        :required="required"
        :value="modelValue"
        @change="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
      >
        <!-- Placeholder option -->
        <option
          v-if="placeholder"
          value=""
          disabled
          :selected="!modelValue"
        >
          {{ placeholder }}
        </option>

        <!-- Options from prop -->
        <option
          v-for="option in options"
          :key="getOptionValue(option)"
          :value="getOptionValue(option)"
          :disabled="getOptionDisabled(option)"
        >
          {{ getOptionLabel(option) }}
        </option>

        <!-- Slot for custom options -->
        <slot />
      </select>

      <!-- Custom arrow icon -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg
          class="w-4 h-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>
    </div>

    <!-- Helper Text -->
    <p
      v-if="helperText"
      :class="helperTextClasses"
    >
      {{ helperText }}
    </p>

    <!-- Error Message -->
    <p
      v-if="error"
      class="mt-1 text-sm text-red-600 dark:text-red-400"
    >
      {{ error }}
    </p>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  optionValue: {
    type: String,
    default: 'value' // Key to use for option values when options are objects
  },
  optionLabel: {
    type: String,
    default: 'label' // Key to use for option labels when options are objects
  },
  optionDisabled: {
    type: String,
    default: 'disabled' // Key to use for option disabled state when options are objects
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  variant: {
    type: String,
    default: 'outlined', // outlined, filled
    validator: (value) => ['outlined', 'filled'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  }
})

// Generate unique ID for accessibility
const selectId = ref(`custom-select-${Math.random().toString(36).substr(2, 9)}`)

const emit = defineEmits(['update:modelValue', 'change', 'blur', 'focus'])

// Handle select events
const handleChange = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
  emit('change', value, event)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}

// Helper functions for option handling
const getOptionValue = (option) => {
  if (typeof option === 'object' && option !== null) {
    return option[props.optionValue]
  }
  return option
}

const getOptionLabel = (option) => {
  if (typeof option === 'object' && option !== null) {
    return option[props.optionLabel]
  }
  return option
}

const getOptionDisabled = (option) => {
  if (typeof option === 'object' && option !== null) {
    return option[props.optionDisabled] || false
  }
  return false
}

// Computed classes
const labelClasses = computed(() => [
  'block',
  'text-sm',
  'font-medium',
  'mb-2',
  props.disabled ? 'text-gray-400 dark:text-gray-500' : 'text-gray-700 dark:text-gray-300'
])

const selectClasses = computed(() => {
  const baseClasses = [
    'block',
    'w-full',
    'rounded-lg',
    'transition-all',
    'duration-200',
    'border',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-offset-1',
    'appearance-none', // Remove default browser styling
    'pr-10', // Space for custom arrow
    // Mobile-first font size to prevent zoom on iOS
    'text-base',
    'sm:text-sm'
  ]

  // Size classes
  const sizeClasses = {
    small: ['px-3', 'py-1.5', 'text-sm', 'min-h-[32px]'],
    medium: ['px-3', 'py-2', 'text-sm', 'min-h-[40px]'],
    large: ['px-4', 'py-3', 'text-base', 'min-h-[48px]']
  }

  // Variant classes
  const variantClasses = {
    outlined: [
      'bg-white',
      'dark:bg-gray-800',
      props.error
        ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
        : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500',
      'dark:border-gray-600',
      'dark:focus:border-purple-500',
      'dark:focus:ring-purple-500'
    ],
    filled: [
      'bg-gray-50',
      'dark:bg-gray-700',
      'border-transparent',
      props.error
        ? 'focus:bg-white focus:border-red-500 focus:ring-red-500'
        : 'focus:bg-white focus:border-blue-500 focus:ring-blue-500',
      'dark:focus:bg-gray-800',
      'dark:focus:border-purple-500',
      'dark:focus:ring-purple-500'
    ]
  }

  // State classes
  const stateClasses = []
  if (props.disabled) {
    stateClasses.push(
      'opacity-60',
      'cursor-not-allowed',
      'bg-gray-100',
      'dark:bg-gray-700'
    )
  }

  // Text color
  const textClasses = [
    'text-gray-900',
    'dark:text-gray-100'
  ]

  return [
    ...baseClasses,
    ...sizeClasses[props.size],
    ...variantClasses[props.variant],
    ...stateClasses,
    ...textClasses
  ]
})

const helperTextClasses = computed(() => [
  'mt-1',
  'text-sm',
  props.disabled ? 'text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-400'
])
</script>

<style scoped>
.custom-select-wrapper {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Ensure proper select styling */
select {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Remove default select arrow in different browsers */
select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

/* Firefox specific arrow removal */
select::-ms-expand {
  display: none;
}

/* Focus state improvements */
select:focus {
  box-shadow: 0 0 0 0 transparent;
}

/* Style option elements */
select option {
  background-color: white;
  color: black;
}

@media (prefers-color-scheme: dark) {
  select option {
    background-color: #374151;
    color: white;
  }
}
</style>