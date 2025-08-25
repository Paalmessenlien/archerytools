<template>
  <div class="custom-input-wrapper">
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      :class="labelClasses"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Input/Textarea -->
    <component
      :is="type === 'textarea' ? 'textarea' : 'input'"
      :id="inputId"
      :type="type === 'textarea' ? undefined : type"
      :class="inputClasses"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :required="required"
      :rows="type === 'textarea' ? rows : undefined"
      :value="modelValue"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    />

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

defineEmits(['update:modelValue', 'blur', 'focus'])

const props = defineProps({
  modelValue: {
    type: [String, Number],
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
  type: {
    type: String,
    default: 'text', // text, email, password, number, tel, url, search, textarea
    validator: (value) => ['text', 'email', 'password', 'number', 'tel', 'url', 'search', 'textarea'].includes(value)
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
  readonly: {
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
  },
  rows: {
    type: Number,
    default: 3
  }
})

// Generate unique ID for accessibility
const inputId = ref(`custom-input-${Math.random().toString(36).substr(2, 9)}`)

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

// Handle input events
const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}

// Computed classes
const labelClasses = computed(() => [
  'block',
  'text-sm',
  'font-medium',
  'mb-2',
  props.disabled ? 'text-gray-400 dark:text-gray-500' : 'text-gray-700 dark:text-gray-300'
])

const inputClasses = computed(() => {
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

  if (props.readonly) {
    stateClasses.push(
      'bg-gray-50',
      'dark:bg-gray-800',
      'cursor-default'
    )
  }

  // Text color
  const textClasses = [
    'text-gray-900',
    'dark:text-gray-100',
    'placeholder:text-gray-500',
    'dark:placeholder:text-gray-400'
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
.custom-input-wrapper {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Ensure proper input styling */
input,
textarea {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Remove default textarea resize handle styling */
textarea {
  resize: vertical;
}

/* Remove browser-specific styling */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

/* Focus state improvements */
input:focus,
textarea:focus {
  box-shadow: 0 0 0 0 transparent;
}
</style>