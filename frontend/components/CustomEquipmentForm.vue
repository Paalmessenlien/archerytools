<template>
  <div class="custom-equipment-form">
    <!-- Equipment Category Selection -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i :class="isEditing ? 'fas fa-edit mr-2 text-blue-600 dark:text-blue-400' : 'fas fa-plus-circle mr-2 text-green-600 dark:text-green-400'"></i>
        {{ isEditing ? 'Edit Equipment' : 'Add Equipment' }}
      </h3>
      
      <!-- Category Tabs -->
      <div v-if="!isEditing" class="flex flex-wrap gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
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
      
      <!-- Category Display for Editing Mode -->
      <div v-else class="mb-6 pb-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center">
          <i :class="getCategoryIcon(selectedCategory)" class="mr-2 text-lg text-blue-600 dark:text-blue-400"></i>
          <span class="text-lg font-medium text-gray-900 dark:text-gray-100">{{ selectedCategory }}</span>
          <span class="ml-2 text-sm text-gray-500 dark:text-gray-400">(Category)</span>
        </div>
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
            <ManufacturerInput
              v-model="formData.manufacturer_name"
              :category="categoryMapping[selectedCategory]"
              label="Manufacturer"
              placeholder="Enter manufacturer name..."
              :required="true"
              @manufacturer-selected="handleManufacturerSelected"
              @manufacturer-created="handleManufacturerCreated"
            />
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

      <!-- Equipment Images -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-images mr-2 text-purple-600 dark:text-purple-400"></i>
          Equipment Images ({{ attachedImages.length }}/5)
        </h4>
        
        <!-- Current Images Display -->
        <div v-if="attachedImages.length" class="mb-4">
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
            <div v-for="(image, index) in attachedImages" :key="index" class="relative group">
              <img 
                :src="image.url" 
                :alt="image.alt || 'Equipment image'" 
                class="w-full h-24 object-cover rounded-lg border border-gray-200 dark:border-gray-600"
              />
              <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                <button 
                  @click="removeImage(index)" 
                  class="p-2 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
                  type="button"
                  title="Remove image"
                >
                  <i class="fas fa-trash text-sm"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Image Upload Component -->
        <div v-if="attachedImages.length < 5" class="mb-4">
          <ImageUpload
            :current-image-url="''"
            alt-text="Equipment image"
            upload-path="equipment"
            :max-size-bytes="52428800"
            @upload-success="handleImageUpload"
            @upload-error="handleImageError"
          />
        </div>
        
        <!-- Upload Guidelines -->
        <div class="text-sm text-gray-600 dark:text-gray-400">
          <i class="fas fa-info-circle mr-2"></i>
          Add up to 5 photos of your equipment (max 50MB each). Images will be stored using CDN for fast loading.
        </div>
      </div>

      <!-- Change Notes (for editing mode) -->
      <div v-if="isEditing" class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-700">
        <label for="changeNotes" class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
          <i class="fas fa-sticky-note mr-2"></i>
          Change Description
          <span class="text-blue-600 dark:text-blue-400 font-normal">(optional)</span>
        </label>
        <textarea
          id="changeNotes"
          v-model="formData.change_notes"
          rows="3"
          class="w-full px-3 py-2 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-blue-900/30 dark:border-blue-700 dark:text-blue-100"
          placeholder="Describe what you changed and why (e.g., 'Updated sight pins for better accuracy at 30 yards')"
        ></textarea>
        <p class="mt-2 text-sm text-blue-600 dark:text-blue-400">
          This note will be logged in your equipment change history to help track modifications.
        </p>
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
          :class="isEditing 
            ? 'bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700'
            : 'bg-green-600 text-white hover:bg-green-700 dark:bg-green-600 dark:hover:bg-green-700'"
        >
          <span v-if="submitting">
            <i class="fas fa-spinner fa-spin mr-2"></i>
            {{ isEditing ? 'Updating...' : 'Adding...' }}
          </span>
          <span v-else>
            <i :class="isEditing ? 'fas fa-save mr-2' : 'fas fa-plus mr-2'"></i>
            {{ isEditing ? 'Save Changes' : 'Add Equipment' }}
          </span>
        </CustomButton>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useApi } from '~/composables/useApi'
import { useImageUpload } from '~/composables/useImageUpload'
import ManufacturerInput from '~/components/ManufacturerInput.vue'
import ImageUpload from '~/components/ImageUpload.vue'

const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  },
  initialEquipment: {
    type: Object,
    default: null
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['equipment-added', 'equipment-updated', 'cancel'])

// Composables
const api = useApi()

// Image Upload Composable
const imageUpload = useImageUpload({
  context: 'equipment',
  maxFiles: 5,
  maxSize: 50
})

// State
const loading = ref(false)
const submitting = ref(false)
const selectedCategory = ref('String')
const formSchema = ref(null)
const attachedImages = ref([])
const allowedCategories = ref([])

// All possible categories with icons
const allCategories = [
  { name: 'String', icon: 'fas fa-link' },
  { name: 'Sight', icon: 'fas fa-crosshairs' },
  { name: 'Scope', icon: 'fas fa-search' },
  { name: 'Stabilizer', icon: 'fas fa-balance-scale' },
  { name: 'Arrow Rest', icon: 'fas fa-hand-paper' },
  { name: 'Plunger', icon: 'fas fa-bullseye' },
  { name: 'Weight', icon: 'fas fa-weight-hanging' },
  { name: 'Peep Sight', icon: 'fas fa-circle-notch' },
  { name: 'Other', icon: 'fas fa-cog' }
]

// Filtered categories based on bow type (computed)
const categories = computed(() => {
  if (allowedCategories.value.length === 0) {
    // If no rules loaded yet, show all categories
    return allCategories
  }
  // Filter to only show allowed categories for this bow type
  return allCategories.filter(cat =>
    allowedCategories.value.includes(cat.name)
  )
})

// Map UI categories to API categories for ManufacturerInput
const categoryMapping = {
  'String': 'strings',
  'Sight': 'sights',
  'Scope': 'scopes',
  'Stabilizer': 'stabilizers',
  'Arrow Rest': 'arrow_rests',
  'Plunger': 'plungers',
  'Weight': 'weights',
  'Peep Sight': 'peep_sights',
  'Other': 'other'
}

// Form Data
const formData = ref({
  manufacturer_name: '',
  model_name: '',
  category_name: 'String',
  description: '',
  installation_notes: '',
  change_notes: '',
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
    
    
    // Only reset specifications when not in editing mode or when category actually changes
    const isInitialLoad = !formData.value.category_name
    const categoryChanged = formData.value.category_name && formData.value.category_name !== category
    
    if (!props.isEditing || categoryChanged) {
      // Reset specifications when category changes (but not during initial editing setup)
      formData.value.specifications = {}
    }
    // In editing mode, preserve existing specifications that were set in initializeForEditing
    
    formData.value.category_name = category
    
    // Initialize multi-select fields as arrays if they don't exist
    if (response.fields) {
      response.fields.forEach(field => {
        if (field.type === 'multi-select') {
          if (!formData.value.specifications[field.name]) {
            formData.value.specifications[field.name] = []
          } else {
            // Ensure existing multi-select values are arrays
            let existingValue = formData.value.specifications[field.name]
            if (!Array.isArray(existingValue)) {
              if (typeof existingValue === 'string' && existingValue.length > 0) {
                formData.value.specifications[field.name] = existingValue.split(',').map(v => v.trim()).filter(v => v)
              } else {
                formData.value.specifications[field.name] = existingValue ? [existingValue] : []
              }
            }
          }
        }
      })
    }
    
    // Re-initialize editing data after schema is loaded (for proper field initialization)
    if (props.isEditing && props.initialEquipment && isInitialLoad) {
      await initializeEditingSpecifications()
    }
    
  } catch (error) {
    console.error('Error loading form schema:', error)
  } finally {
    loading.value = false
  }
}

// Handle manufacturer selection from ManufacturerInput
const handleManufacturerSelected = (event) => {
  console.log('Manufacturer selected:', event)
}

// Handle new manufacturer creation
const handleManufacturerCreated = (event) => {
  console.log('New manufacturer will be created:', event)
}

// Image handling methods
const handleImageUpload = (uploadResult) => {
  console.log('Image uploaded:', uploadResult)
  if (uploadResult && uploadResult.url) {
    attachedImages.value.push({
      url: uploadResult.url,
      cdnUrl: uploadResult.cdnUrl,
      originalName: uploadResult.originalName || 'equipment-image.jpg',
      uploadedAt: new Date().toISOString(),
      alt: `${formData.value.manufacturer_name} ${formData.value.model_name} - Equipment Image`
    })
  }
}

const handleImageError = (error) => {
  console.error('Image upload error:', error)
}

const removeImage = (index) => {
  attachedImages.value.splice(index, 1)
}

const getCategoryIcon = (categoryName) => {
  const iconMap = {
    'String': 'fas fa-link',
    'Sight': 'fas fa-crosshairs',
    'Scope': 'fas fa-search',
    'Stabilizer': 'fas fa-balance-scale',
    'Arrow Rest': 'fas fa-hand-paper',
    'Plunger': 'fas fa-bullseye',
    'Weight': 'fas fa-weight-hanging',
    'Other': 'fas fa-cog'
  }
  return iconMap[categoryName] || 'fas fa-cog'
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
      specifications: formData.value.specifications,
      images: attachedImages.value.map(img => ({
        url: img.url,
        cdnUrl: img.cdnUrl,
        originalName: img.originalName,
        alt: img.alt
      }))
    }
    
    if (props.isEditing) {
      // Handle equipment update
      equipmentData.change_reason = formData.value.change_notes || 'Equipment updated'
      
      const response = await api.put(`/bow-setups/${props.bowSetup.id}/equipment/${props.initialEquipment.id}`, equipmentData)
      emit('equipment-updated', response)
    } else {
      // Handle equipment addition
      const response = await api.post(`/bow-setups/${props.bowSetup.id}/equipment`, equipmentData)
      emit('equipment-added', response)
      
      // Reset form for adding mode only
      formData.value = {
        manufacturer_name: '',
        model_name: '',
        category_name: selectedCategory.value,
        description: '',
        installation_notes: '',
        change_notes: '',
        specifications: {}
      }
      
      // Clear attached images
      attachedImages.value = []
      
      // Reinitialize multi-select fields
      if (formSchema.value?.fields) {
        formSchema.value.fields.forEach(field => {
          if (field.type === 'multi-select') {
            formData.value.specifications[field.name] = []
          }
        })
      }
    }
    
  } catch (error) {
    console.error(`Error ${props.isEditing ? 'updating' : 'adding'} equipment:`, error)
    // Could show error notification here
    alert(`Error ${props.isEditing ? 'updating' : 'adding'} equipment: ${error.message || 'Please try again.'}`)
  } finally {
    submitting.value = false
  }
}

// Watchers
watch(selectedCategory, (newCategory) => {
  loadFormSchema(newCategory)
})


// Initialize form for editing mode
const initializeForEditing = () => {
  if (props.isEditing && props.initialEquipment) {
    const equipment = props.initialEquipment
    
    
    // Set basic form data
    formData.value.manufacturer_name = equipment.manufacturer_name || equipment.manufacturer || ''
    formData.value.model_name = equipment.model_name || ''
    formData.value.category_name = equipment.category_name || 'String'
    formData.value.description = equipment.description || ''
    formData.value.installation_notes = equipment.installation_notes || ''
    formData.value.change_notes = ''
    
    // Set category
    selectedCategory.value = equipment.category_name || 'String'
    
    // IMMEDIATELY set specifications if available (don't wait for schema loading)
    if (equipment.specifications && typeof equipment.specifications === 'object') {
      formData.value.specifications = { ...equipment.specifications }
    } else if (equipment.custom_specifications) {
      try {
        const parsedSpecs = typeof equipment.custom_specifications === 'string' 
          ? JSON.parse(equipment.custom_specifications)
          : equipment.custom_specifications
        formData.value.specifications = { ...parsedSpecs }
      } catch (error) {
        console.error('Error parsing custom_specifications in initializeForEditing:', error)
      }
    }
    
    // Initialize images if available
    if (equipment.images && Array.isArray(equipment.images)) {
      attachedImages.value = equipment.images.map(img => ({
        url: img.url || img.cdnUrl,
        cdnUrl: img.cdnUrl,
        originalName: img.originalName || 'equipment-image.jpg',
        uploadedAt: img.uploadedAt || new Date().toISOString(),
        alt: img.alt || `${equipment.manufacturer_name || equipment.manufacturer} ${equipment.model_name} - Equipment Image`
      }))
    }
    
  } else {
    // Not in editing mode or no equipment provided
  }
}

// Initialize specifications after schema is loaded (for editing mode)
const initializeEditingSpecifications = async () => {
  if (props.isEditing && props.initialEquipment) {
    const equipment = props.initialEquipment
    
    console.log('🔧 DROPDOWN DEBUG: initializeEditingSpecifications called')
    console.log('🔧 Initial equipment object:', JSON.stringify(equipment, null, 2))
    console.log('🔧 Equipment specifications field:', equipment.specifications)
    console.log('🔧 Equipment custom_specifications field:', equipment.custom_specifications)
    
    // Check multiple possible field names for specifications
    let specsSource = null
    let specs = {}
    
    if (equipment.specifications) {
      specsSource = 'specifications'
      specs = equipment.specifications
    } else if (equipment.custom_specifications) {
      specsSource = 'custom_specifications'  
      specs = equipment.custom_specifications
    }
    
    console.log('🔧 Using specifications from field:', specsSource)
    console.log('🔧 Raw specs value:', specs)
    
    if (specs) {
      try {
        const parsedSpecs = typeof specs === 'string' 
          ? JSON.parse(specs)
          : specs
        
        console.log('🔧 Parsed specifications:', JSON.stringify(parsedSpecs, null, 2))
        console.log('🔧 Form schema available:', !!formSchema.value)
        console.log('🔧 Form schema fields:', formSchema.value?.fields?.length || 0)
        
        // Preserve existing specifications and merge with parsed ones
        const oldSpecs = { ...formData.value.specifications }
        formData.value.specifications = { 
          ...formData.value.specifications,
          ...parsedSpecs 
        }
        
        console.log('🔧 Old form specifications:', JSON.stringify(oldSpecs, null, 2))
        console.log('🔧 New form specifications:', JSON.stringify(formData.value.specifications, null, 2))
        
        // Ensure multi-select fields are arrays
        if (formSchema.value?.fields) {
          formSchema.value.fields.forEach(field => {
            console.log(`🔧 Processing field: ${field.name} (${field.type})`)
            
            if (field.type === 'multi-select' && parsedSpecs[field.name]) {
              // Convert single values or strings to arrays
              let value = parsedSpecs[field.name]
              console.log(`🔧 Multi-select field ${field.name} original value:`, value)
              
              if (typeof value === 'string') {
                // Handle comma-separated strings
                value = value.split(',').map(v => v.trim()).filter(v => v)
              } else if (!Array.isArray(value)) {
                value = [value]
              }
              
              formData.value.specifications[field.name] = value
              console.log(`🔧 Multi-select field ${field.name} converted to:`, value)
            } else if (field.type === 'dropdown' && parsedSpecs[field.name]) {
              console.log(`🔧 Dropdown field ${field.name} value:`, parsedSpecs[field.name])
              console.log(`🔧 Dropdown field ${field.name} options:`, field.options)
            }
          })
        }
        
        console.log('🔧 Final form specifications after processing:', JSON.stringify(formData.value.specifications, null, 2))
        
      } catch (error) {
        console.error('🔧 Error parsing equipment specifications:', error)
      }
    } else {
      console.log('🔧 No specifications found in equipment object')
    }
  } else {
    console.log('🔧 initializeEditingSpecifications skipped - not editing or no equipment')
  }
}

// Lifecycle
// Load allowed categories for this bow type
const loadAllowedCategories = async () => {
  try {
    const bowType = props.bowSetup?.bow_type
    if (bowType) {
      const response = await api.get(`/equipment/categories?bow_type=${bowType}`)
      if (response.categories && Array.isArray(response.categories)) {
        allowedCategories.value = response.categories.map(cat => cat.name)
        // Update selected category if current one is not allowed
        if (!allowedCategories.value.includes(selectedCategory.value) && allowedCategories.value.length > 0) {
          selectedCategory.value = allowedCategories.value[0]
        }
      }
    }
  } catch (error) {
    console.error('Error loading allowed categories:', error)
    // On error, show all categories
    allowedCategories.value = []
  }
}

onMounted(async () => {
  // Initialize for editing first, then load schema
  if (props.isEditing) {
    initializeForEditing()
  }
  // Load allowed categories based on bow type
  await loadAllowedCategories()
  await loadFormSchema(selectedCategory.value)
})
</script>

<style scoped>
.required::after {
  content: ' *';
  color: #ef4444;
}
</style>