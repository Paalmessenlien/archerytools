<template>
  <div class="custom-checkbox-wrapper">
    <label
      :for="checkboxId"
      :class="labelClasses"
      class="custom-checkbox-label"
    >
      <div class="relative flex items-center">
        <!-- Hidden native checkbox for accessibility -->
        <input
          :id="checkboxId"
          type="checkbox"
          :class="hiddenCheckboxClasses"
          :checked="isChecked"
          :disabled="disabled"
          :required="required"
          :value="value"
          @change="handleChange"
          @focus="handleFocus"
          @blur="handleBlur"
        />

        <!-- Custom checkbox visual -->
        <div :class="checkboxClasses">
          <!-- Checkmark icon -->
          <svg
            v-if="isChecked"
            class="w-3 h-3 text-white pointer-events-none"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
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
    type: [Boolean, Array],
    default: false
  },
  value: {
    type: [String, Number, Boolean],
    default: true
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
  },
  indeterminate: {
    type: Boolean,
    default: false
  }
})

// Generate unique ID for accessibility
const checkboxId = ref(`custom-checkbox-${Math.random().toString(36).substr(2, 9)}`)

const emit = defineEmits(['update:modelValue', 'change', 'focus', 'blur'])

// Computed property to determine if checkbox is checked
const isChecked = computed(() => {
  if (Array.isArray(props.modelValue)) {
    return props.modelValue.includes(props.value)
  }
  return Boolean(props.modelValue)
})

// Handle checkbox change
const handleChange = (event) => {
  const checked = event.target.checked
  
  if (Array.isArray(props.modelValue)) {
    const newValue = [...props.modelValue]
    if (checked) {
      if (!newValue.includes(props.value)) {
        newValue.push(props.value)
      }
    } else {
      const index = newValue.indexOf(props.value)
      if (index > -1) {
        newValue.splice(index, 1)
      }
    }
    emit('update:modelValue', newValue)
    emit('change', newValue, event)
  } else {
    emit('update:modelValue', checked)
    emit('change', checked, event)
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

const hiddenCheckboxClasses = computed(() => [
  'sr-only' // Screen reader only - visually hidden but accessible
])

const checkboxClasses = computed(() => {
  const baseClasses = [
    'flex',
    'items-center',
    'justify-center',
    'border-2',
    'rounded',
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
  } else if (isChecked.value || props.indeterminate) {
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
  'ml-8', // Align with text, accounting for checkbox width + margin
  props.disabled ? 'text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-400'
])
</script>

<style scoped>
.custom-checkbox-wrapper {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Ensure proper focus styles */
.custom-checkbox-label input:focus + div {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

/* Custom focus ring for better visibility */
.custom-checkbox-label:focus-within div {
  /* Focus styles are handled in computed classes */
}

/* Smooth transitions */
.custom-checkbox-label div {
  transition: all 0.2s ease-in-out;
}

/* Ensure checkbox is always visible */
.custom-checkbox-label div {
  min-width: fit-content;
}
</style>