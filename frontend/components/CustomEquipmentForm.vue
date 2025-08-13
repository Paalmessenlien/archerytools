<template>
  <div class="custom-equipment-form">
    <!-- Equipment Category Selection -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-plus-circle mr-2 text-green-600 dark:text-green-400"></i>
        Add Equipment
      </h3>
      
      <!-- Category Tabs -->
      <div class="flex flex-wrap gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
        <button
          v-for="category in categories"
          :key="category.name"
          @click="selectedCategory = category.name"
          :class="[
            'px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors',
            selectedCategory === category.name
              ? 'text-blue-600 border-blue-600 bg-blue-50 dark:text-purple-400 dark:border-purple-400 dark:bg-purple-900/20'
              : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
          ]"
        >
          <i :class="category.icon" class="mr-2"></i>
          {{ category.name }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 dark:border-green-400 mx-auto mb-3"></div>
      <p class="text-gray-600 dark:text-gray-400">Loading form...</p>
    </div>

    <!-- Equipment Form -->
    <form v-else-if="formSchema && selectedCategory" @submit.prevent="submitForm" class="space-y-6">
      <!-- Basic Equipment Information -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-info-circle mr-2 text-blue-600 dark:text-blue-400"></i>
          Basic Information
        </h4>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Manufacturer Name with Autocomplete -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Manufacturer *
            </label>
            <div class="relative">
              <input
                v-model="formData.manufacturer_name"
                @input="searchManufacturers"
                @focus="showManufacturerSuggestions = true"
                type="text"
                placeholder="Enter manufacturer name..."
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              />
              
              <!-- Manufacturer Suggestions Dropdown -->
              <div v-if="showManufacturerSuggestions && manufacturerSuggestions.length > 0" 
                   class="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
                <div
                  v-for="manufacturer in manufacturerSuggestions"
                  :key="manufacturer.name"
                  @click="selectManufacturer(manufacturer)"
                  class="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer text-sm"
                >
                  <div class="font-medium">{{ manufacturer.name }}</div>
                  <div v-if="manufacturer.country" class="text-xs text-gray-500 dark:text-gray-400">
                    {{ manufacturer.country }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Model Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Model Name *
            </label>
            <input
              v-model="formData.model_name"
              type="text"
              placeholder="Enter model name..."
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
            />
          </div>
        </div>

        <!-- Description -->
        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Description
          </label>
          <textarea
            v-model="formData.description"
            rows="3"
            placeholder="Optional description or notes..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          ></textarea>
        </div>
      </div>

      <!-- Technical Specifications -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-cogs mr-2 text-green-600 dark:text-green-400"></i>
          Technical Specifications
        </h4>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="field in sortedFormFields" :key="field.name" :class="field.type === 'multi-select' ? 'md:col-span-2' : ''">
            <!-- Text Input -->
            <div v-if="field.type === 'text'">
              <label :class="['block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2', field.required ? 'required' : '']">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500 ml-1">*</span>
                <span v-if="field.unit" class="text-xs text-gray-500 dark:text-gray-400 ml-1">({{ field.unit }})</span>
              </label>
              <input
                v-model="formData.specifications[field.name]"
                type="text"
                :placeholder="getFieldPlaceholder(field)"
                :required="field.required"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              />
              <p v-if="field.help" class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ field.help }}</p>
            </div>

            <!-- Number Input -->
            <div v-else-if="field.type === 'number'">
              <label :class="['block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2', field.required ? 'required' : '']">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500 ml-1">*</span>
                <span v-if="field.unit" class="text-xs text-gray-500 dark:text-gray-400 ml-1">({{ field.unit }})</span>
              </label>
              <input
                v-model.number="formData.specifications[field.name]"
                type="number"
                :step="getNumberStep(field)"
                :min="field.validation?.min"
                :max="field.validation?.max"
                :placeholder="getFieldPlaceholder(field)"
                :required="field.required"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              />
              <p v-if="field.help" class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ field.help }}</p>
            </div>

            <!-- Dropdown Select -->
            <div v-else-if="field.type === 'dropdown'">
              <label :class="['block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2', field.required ? 'required' : '']">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500 ml-1">*</span>
              </label>
              <select
                v-model="formData.specifications[field.name]"
                :required="field.required"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              >
                <option value="">Select {{ field.label.toLowerCase() }}...</option>
                <option v-for="option in field.options" :key="option" :value="option">
                  {{ formatOptionValue(option) }}
                </option>
              </select>
              <p v-if="field.help" class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ field.help }}</p>
            </div>

            <!-- Multi-Select Checkboxes -->
            <div v-else-if="field.type === 'multi-select'" class="md:col-span-2">
              <label :class="['block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2', field.required ? 'required' : '']">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500 ml-1">*</span>
              </label>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                <label 
                  v-for="option in field.options" 
                  :key="option"
                  class="flex items-center space-x-2 text-sm"
                >
                  <input
                    :value="option"
                    v-model="formData.specifications[field.name]"
                    type="checkbox"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                  />
                  <span class="text-gray-700 dark:text-gray-300">{{ formatOptionValue(option) }}</span>
                </label>
              </div>
              <p v-if="field.help" class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ field.help }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Installation Notes -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-tools mr-2 text-orange-600 dark:text-orange-400"></i>
          Installation
        </h4>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Installation Notes
          </label>
          <textarea
            v-model="formData.installation_notes"
            rows="3"
            placeholder="Optional installation notes, settings, or configuration details..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          ></textarea>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex justify-end space-x-3 pt-4">
        <CustomButton @click="$emit('cancel')" variant="outlined">
          Cancel
        </CustomButton>
        <CustomButton 
          type="submit" 
          variant="filled"
          :disabled="!isFormValid || submitting"
          class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-600 dark:hover:bg-green-700"
        >
          <span v-if="submitting">
            <i class="fas fa-spinner fa-spin mr-2"></i>
            Adding...
          </span>
          <span v-else>
            <i class="fas fa-plus mr-2"></i>
            Add Equipment
          </span>
        </CustomButton>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['equipment-added', 'cancel'])

// Composables
const api = useApi()

// State
const loading = ref(false)
const submitting = ref(false)
const selectedCategory = ref('String')
const formSchema = ref(null)
const manufacturerSuggestions = ref([])
const showManufacturerSuggestions = ref(false)

// Categories
const categories = ref([
  { name: 'String', icon: 'fas fa-link' },
  { name: 'Sight', icon: 'fas fa-crosshairs' },
  { name: 'Stabilizer', icon: 'fas fa-balance-scale' },
  { name: 'Arrow Rest', icon: 'fas fa-hand-paper' },
  { name: 'Weight', icon: 'fas fa-weight-hanging' }
])

// Form Data
const formData = ref({
  manufacturer_name: '',
  model_name: '',
  category_name: 'String',
  description: '',
  installation_notes: '',
  specifications: {}
})

// Computed
const sortedFormFields = computed(() => {
  if (!formSchema.value?.fields) return []
  return formSchema.value.fields.sort((a, b) => (a.order || 0) - (b.order || 0))
})

const isFormValid = computed(() => {
  // Check required basic fields
  if (!formData.value.manufacturer_name || !formData.value.model_name) {
    return false
  }
  
  // Check required specification fields
  if (formSchema.value?.fields) {
    for (const field of formSchema.value.fields) {
      if (field.required) {
        const value = formData.value.specifications[field.name]
        if (!value || (Array.isArray(value) && value.length === 0)) {
          return false
        }
      }
    }
  }
  
  return true
})

// Methods
const loadFormSchema = async (category) => {
  try {
    loading.value = true
    const response = await api.get(`/equipment/form-schema/${category}`)
    formSchema.value = response
    
    // Reset specifications when category changes
    formData.value.specifications = {}
    formData.value.category_name = category
    
    // Initialize multi-select fields as arrays
    if (response.fields) {
      response.fields.forEach(field => {
        if (field.type === 'multi-select') {
          formData.value.specifications[field.name] = []
        }
      })
    }
  } catch (error) {
    console.error('Error loading form schema:', error)
  } finally {
    loading.value = false
  }
}

const searchManufacturers = async () => {
  if (formData.value.manufacturer_name.length < 2) {
    manufacturerSuggestions.value = []
    return
  }
  
  try {
    const response = await api.get(`/equipment/manufacturers/suggest?q=${encodeURIComponent(formData.value.manufacturer_name)}&category=${selectedCategory.value}`)
    manufacturerSuggestions.value = response.manufacturers || []
  } catch (error) {
    console.error('Error searching manufacturers:', error)
    manufacturerSuggestions.value = []
  }
}

const selectManufacturer = (manufacturer) => {
  formData.value.manufacturer_name = manufacturer.name
  showManufacturerSuggestions.value = false
  manufacturerSuggestions.value = []
}

const getFieldPlaceholder = (field) => {
  if (field.default) {
    return `Default: ${field.default}`
  }
  return `Enter ${field.label.toLowerCase()}...`
}

const getNumberStep = (field) => {
  if (field.unit === 'ounces' || field.validation?.min < 1) {
    return '0.1'
  }
  return '1'
}

const formatOptionValue = (value) => {
  return value.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const submitForm = async () => {
  if (!isFormValid.value) return
  
  try {
    submitting.value = true
    
    const equipmentData = {
      manufacturer_name: formData.value.manufacturer_name,
      model_name: formData.value.model_name,
      category_name: selectedCategory.value,
      description: formData.value.description,
      installation_notes: formData.value.installation_notes,
      specifications: formData.value.specifications
    }
    
    const response = await api.post(`/bow-setups/${props.bowSetup.id}/equipment`, equipmentData)
    
    emit('equipment-added', response)
    
    // Reset form
    formData.value = {
      manufacturer_name: '',
      model_name: '',
      category_name: selectedCategory.value,
      description: '',
      installation_notes: '',
      specifications: {}
    }
    
    // Reinitialize multi-select fields
    if (formSchema.value?.fields) {
      formSchema.value.fields.forEach(field => {
        if (field.type === 'multi-select') {
          formData.value.specifications[field.name] = []
        }
      })
    }
    
  } catch (error) {
    console.error('Error adding equipment:', error)
    // Could show error notification here
  } finally {
    submitting.value = false
  }
}

// Watchers
watch(selectedCategory, (newCategory) => {
  loadFormSchema(newCategory)
})

// Click outside to close manufacturer suggestions
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showManufacturerSuggestions.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await loadFormSchema(selectedCategory.value)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.required::after {
  content: ' *';
  color: #ef4444;
}
</style>