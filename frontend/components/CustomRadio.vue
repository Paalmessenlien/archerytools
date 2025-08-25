<template>
  <div class="custom-radio-wrapper">
    <label
      :for="radioId"
      :class="labelClasses"
      class="custom-radio-label"
    >
      <div class="relative flex items-center">
        <!-- Hidden native radio for accessibility -->
        <input
          :id="radioId"
          type="radio"
          :name="name"
          :class="hiddenRadioClasses"
          :checked="isChecked"
          :disabled="disabled"
          :required="required"
          :value="value"
          @change="handleChange"
          @focus="handleFocus"
          @blur="handleBlur"
        />

        <!-- Custom radio visual -->
        <div :class="radioClasses">
          <!-- Radio dot -->
          <div
            v-if="isChecked"
            class="w-2 h-2 bg-white rounded-full pointer-events-none"
          />
        </div>

        <!-- Label text -->
        <div v-if="label || $slots.default" :class="textClasses">
          <slot>
            {{ label }}
          </slot>
          <span v-if="required" class="text-red-500 ml-1">*</span>
        </div>
      </div>
    </label>

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
  value: {
    type: [String, Number, Boolean],
    required: true
  },
  name: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
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
const radioId = ref(`custom-radio-${Math.random().toString(36).substr(2, 9)}`)

const emit = defineEmits(['update:modelValue', 'change', 'focus', 'blur'])

// Computed property to determine if radio is checked
const isChecked = computed(() => {
  return props.modelValue === props.value
})

// Handle radio change
const handleChange = (event) => {
  if (event.target.checked) {
    emit('update:modelValue', props.value)
    emit('change', props.value, event)
  }
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleBlur = (event) => {
  emit('blur', event)
}

// Computed classes
const labelClasses = computed(() => [
  'flex',
  'items-start',
  'cursor-pointer',
  'select-none',
  props.disabled ? 'cursor-not-allowed opacity-50' : 'hover:opacity-80'
])

const hiddenRadioClasses = computed(() => [
  'sr-only' // Screen reader only - visually hidden but accessible
])

const radioClasses = computed(() => {
  const baseClasses = [
    'flex',
    'items-center',
    'justify-center',
    'border-2',
    'rounded-full',
    'transition-all',
    'duration-200',
    'mr-3',
    'flex-shrink-0'
  ]

  // Size classes
  const sizeClasses = {
    small: ['w-4', 'h-4'],
    medium: ['w-5', 'h-5'],
    large: ['w-6', 'h-6']
  }

  // State-based styling
  const stateClasses = []
  
  if (props.disabled) {
    stateClasses.push(
      'bg-gray-100',
      'border-gray-200',
      'dark:bg-gray-700',
      'dark:border-gray-600'
    )
  } else if (isChecked.value) {
    if (props.error) {
      stateClasses.push(
        'bg-red-600',
        'border-red-600',
        'hover:bg-red-700',
        'focus:ring-2',
        'focus:ring-red-500',
        'focus:ring-offset-2'
      )
    } else {
      stateClasses.push(
        'bg-blue-600',
        'border-blue-600',
        'hover:bg-blue-700',
        'focus:ring-2',
        'focus:ring-blue-500',
        'focus:ring-offset-2',
        'dark:bg-purple-600',
        'dark:border-purple-600',
        'dark:hover:bg-purple-700',
        'dark:focus:ring-purple-500'
      )
    }
  } else {
    if (props.error) {
      stateClasses.push(
        'bg-white',
        'border-red-300',
        'hover:border-red-400',
        'focus:border-red-500',
        'focus:ring-2',
        'focus:ring-red-500',
        'focus:ring-offset-2',
        'dark:bg-gray-800',
        'dark:border-red-600'
      )
    } else {
      stateClasses.push(
        'bg-white',
        'border-gray-300',
        'hover:border-gray-400',
        'focus:border-blue-500',
        'focus:ring-2',
        'focus:ring-blue-500',
        'focus:ring-offset-2',
        'dark:bg-gray-800',
        'dark:border-gray-600',
        'dark:hover:border-gray-500',
        'dark:focus:border-purple-500',
        'dark:focus:ring-purple-500'
      )
    }
  }

  return [
    ...baseClasses,
    ...sizeClasses[props.size],
    ...stateClasses
  ]
})

const textClasses = computed(() => [
  'text-sm',
  'leading-5',
  'select-none',
  props.disabled ? 'text-gray-400 dark:text-gray-500' : 'text-gray-900 dark:text-gray-100'
])

const helperTextClasses = computed(() => [
  'mt-1',
  'text-sm',
  'ml-8', // Align with text, accounting for radio width + margin
  props.disabled ? 'text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-400'
])
</script>

<style scoped>
.custom-radio-wrapper {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Ensure proper focus styles */
.custom-radio-label input:focus + div {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

/* Custom focus ring for better visibility */
.custom-radio-label:focus-within div {
  /* Focus styles are handled in computed classes */
}

/* Smooth transitions */
.custom-radio-label div {
  transition: all 0.2s ease-in-out;
}

/* Ensure radio dot scales properly with size */
.custom-radio-label div > div {
  transition: all 0.2s ease-in-out;
}

/* Ensure radio is always visible */
.custom-radio-label div {
  min-width: fit-content;
}
</style>