<template>
  <div class="manufacturer-input-container">
    <label 
      :for="inputId" 
      class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>
    
    <div class="relative">
      <!-- Input field with autocomplete -->
      <input
        :id="inputId"
        v-model="inputValue"
        type="text"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="handleKeydown"
        class="w-full form-input pr-10"
        autocomplete="off"
        :class="[
          dropdownVisible && suggestions.length > 0 ? 'rounded-b-none border-b-0' : '',
          validationClass
        ]"
      />
      
      <!-- Loading/status indicator -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-3">
        <div v-if="loading" class="animate-spin h-4 w-4">
          <i class="fas fa-spinner text-gray-400"></i>
        </div>
        <div v-else-if="manufacturerStatus" class="flex items-center">
          <i 
            :class="statusIconClass"
            class="h-4 w-4"
            :title="statusTooltip"
          ></i>
        </div>
      </div>
      
      <!-- Autocomplete dropdown -->
      <div 
        v-if="dropdownVisible && (suggestions.length > 0 || showNoResults)"
        class="absolute z-50 w-full bg-white dark:bg-gray-800 border-l border-r border-b border-gray-300 dark:border-gray-600 rounded-b-lg shadow-lg max-h-60 overflow-y-auto"
      >
        <!-- Suggestions list -->
        <div v-if="suggestions.length > 0">
          <div
            v-for="(suggestion, index) in suggestions"
            :key="index"
            @mousedown.prevent="selectSuggestion(suggestion)"
            :class="[
              'px-3 py-2 cursor-pointer flex items-center justify-between',
              'hover:bg-gray-100 dark:hover:bg-gray-700',
              index === selectedIndex ? 'bg-blue-50 dark:bg-blue-900/20' : ''
            ]"
          >
            <div class="flex items-center">
              <span class="font-medium">{{ suggestion.name }}</span>
              <span v-if="suggestion.categories" class="ml-2 text-xs text-gray-500 dark:text-gray-400">
                {{ suggestion.categories.join(', ') }}
              </span>
            </div>
            <div class="flex items-center text-xs">
              <span 
                v-if="suggestion.status"
                :class="suggestion.status === 'approved' ? 'text-green-600' : 'text-yellow-600'"
                class="mr-1"
              >
                {{ suggestion.status === 'approved' ? '✓' : '⏳' }}
              </span>
              <span class="text-gray-400">{{ suggestion.usage_count || 0 }}</span>
            </div>
          </div>
        </div>
        
        <!-- No results message -->
        <div v-else-if="showNoResults" class="px-3 py-2 text-gray-500 dark:text-gray-400 text-sm">
          <div class="flex items-center">
            <i class="fas fa-plus-circle mr-2 text-blue-500"></i>
            Add "{{ inputValue }}" as new manufacturer
            <span class="ml-1 text-xs">(pending approval)</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Help text -->
    <p v-if="helpText" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
      {{ helpText }}
    </p>
    
    <!-- Validation message -->
    <p v-if="errorMessage" class="mt-1 text-xs text-red-500">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  category: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: 'Manufacturer'
  },
  placeholder: {
    type: String,
    default: 'Start typing manufacturer name...'
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  helpText: {
    type: String,
    default: 'Type 3+ characters to see suggestions. New manufacturers will be pending approval.'
  },
  minChars: {
    type: Number,
    default: 3
  },
  maxSuggestions: {
    type: Number,
    default: 8
  }
})

const emit = defineEmits(['update:modelValue', 'manufacturer-selected', 'manufacturer-created'])

const api = useApi()

// Component state
const inputValue = ref(props.modelValue || '')
const suggestions = ref([])
const loading = ref(false)
const dropdownVisible = ref(false)
const selectedIndex = ref(-1)
const manufacturerStatus = ref(null)
const errorMessage = ref('')
const debounceTimer = ref(null)

// Generate unique input ID
const inputId = computed(() => `manufacturer-input-${Math.random().toString(36).substr(2, 9)}`)

// Validation class for input styling
const validationClass = computed(() => {
  if (errorMessage.value) return 'border-red-500 focus:border-red-500 focus:ring-red-500'
  if (manufacturerStatus.value === 'approved') return 'border-green-500'
  if (manufacturerStatus.value === 'pending') return 'border-yellow-500'
  return ''
})

// Status icon class
const statusIconClass = computed(() => {
  switch (manufacturerStatus.value) {
    case 'approved': return 'fas fa-check-circle text-green-500'
    case 'pending': return 'fas fa-clock text-yellow-500'
    case 'new': return 'fas fa-plus-circle text-blue-500'
    default: return ''
  }
})

// Status tooltip
const statusTooltip = computed(() => {
  switch (manufacturerStatus.value) {
    case 'approved': return 'Approved manufacturer'
    case 'pending': return 'Pending approval'
    case 'new': return 'Will be added as new manufacturer'
    default: return ''
  }
})

// Show no results when input is long enough but no suggestions
const showNoResults = computed(() => {
  return inputValue.value.length >= props.minChars && 
         suggestions.value.length === 0 && 
         !loading.value &&
         inputValue.value.trim() !== ''
})

// Watch for model value changes from parent
watch(() => props.modelValue, (newValue) => {
  if (newValue !== inputValue.value) {
    inputValue.value = newValue || ''
    checkManufacturerStatus()
  }
})

// Watch for category changes
watch(() => props.category, () => {
  if (inputValue.value.length >= props.minChars) {
    fetchSuggestions()
  }
})

// Fetch manufacturer suggestions from API
const fetchSuggestions = async () => {
  if (inputValue.value.length < props.minChars) {
    suggestions.value = []
    dropdownVisible.value = false
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await api.get('/manufacturers/suggestions', {
      query: inputValue.value,
      category: props.category,
      limit: props.maxSuggestions
    })

    if (response && response.suggestions) {
      suggestions.value = response.suggestions.map(suggestion => ({
        name: suggestion.name,
        status: suggestion.status || 'approved',
        categories: suggestion.categories || [],
        usage_count: suggestion.usage_count || 0,
        is_exact_match: suggestion.name.toLowerCase() === inputValue.value.toLowerCase()
      }))

      // Sort exact matches first, then by usage count
      suggestions.value.sort((a, b) => {
        if (a.is_exact_match && !b.is_exact_match) return -1
        if (!a.is_exact_match && b.is_exact_match) return 1
        return b.usage_count - a.usage_count
      })

      dropdownVisible.value = true
    }
  } catch (error) {
    console.error('Error fetching manufacturer suggestions:', error)
    errorMessage.value = 'Failed to load suggestions'
    suggestions.value = []
  } finally {
    loading.value = false
  }
}

// Check manufacturer status for validation
const checkManufacturerStatus = async () => {
  if (!inputValue.value || inputValue.value.length < 2) {
    manufacturerStatus.value = null
    return
  }

  try {
    const response = await api.get('/manufacturers/status', {
      name: inputValue.value,
      category: props.category
    })

    if (response && response.status) {
      manufacturerStatus.value = response.status
    } else {
      manufacturerStatus.value = 'new'
    }
  } catch (error) {
    console.error('Error checking manufacturer status:', error)
    manufacturerStatus.value = null
  }
}

// Handle input changes with debouncing
const handleInput = (event) => {
  const value = event.target.value
  inputValue.value = value
  selectedIndex.value = -1

  // Emit to parent immediately
  emit('update:modelValue', value)

  // Clear previous timer
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
  }

  // Debounce API calls
  debounceTimer.value = setTimeout(() => {
    if (value.length >= props.minChars) {
      fetchSuggestions()
    } else {
      suggestions.value = []
      dropdownVisible.value = false
    }
    checkManufacturerStatus()
  }, 300)
}

// Handle input focus
const handleFocus = () => {
  if (inputValue.value.length >= props.minChars && suggestions.value.length > 0) {
    dropdownVisible.value = true
  }
}

// Handle input blur (with delay to allow for selection)
const handleBlur = () => {
  setTimeout(() => {
    dropdownVisible.value = false
    selectedIndex.value = -1
  }, 150)
}

// Handle keyboard navigation
const handleKeydown = (event) => {
  if (!dropdownVisible.value || suggestions.value.length === 0) return

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, suggestions.value.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
      break
    case 'Enter':
      event.preventDefault()
      if (selectedIndex.value >= 0) {
        selectSuggestion(suggestions.value[selectedIndex.value])
      } else if (showNoResults.value) {
        // Create new manufacturer
        handleNewManufacturer()
      }
      break
    case 'Escape':
      dropdownVisible.value = false
      selectedIndex.value = -1
      break
  }
}

// Select a suggestion from dropdown
const selectSuggestion = (suggestion) => {
  inputValue.value = suggestion.name
  manufacturerStatus.value = suggestion.status
  dropdownVisible.value = false
  selectedIndex.value = -1

  // Emit to parent
  emit('update:modelValue', suggestion.name)
  emit('manufacturer-selected', {
    name: suggestion.name,
    status: suggestion.status,
    categories: suggestion.categories,
    usage_count: suggestion.usage_count
  })
}

// Handle new manufacturer creation
const handleNewManufacturer = () => {
  manufacturerStatus.value = 'pending'
  dropdownVisible.value = false
  
  emit('manufacturer-created', {
    name: inputValue.value,
    category: props.category,
    status: 'pending'
  })
}

// Initialize component
onMounted(() => {
  if (inputValue.value) {
    checkManufacturerStatus()
  }
})
</script>

<style scoped>
.form-input {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 transition-colors;
}

.manufacturer-input-container {
  position: relative;
}

/* Ensure dropdown is above other elements */
.manufacturer-input-container .absolute {
  z-index: 1000;
}

/* Custom scrollbar for dropdown */
.max-h-60::-webkit-scrollbar {
  width: 6px;
}

.max-h-60::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.max-h-60::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.max-h-60::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.dark .max-h-60::-webkit-scrollbar-track {
  background: #374151;
}

.dark .max-h-60::-webkit-scrollbar-thumb {
  background: #6b7280;
}

.dark .max-h-60::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>