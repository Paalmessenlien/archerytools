<template>
  <div class="fixed inset-0 modal-overlay bg-white dark:bg-gray-900 md:bg-black md:bg-opacity-50 md:flex md:items-center md:justify-center md:p-4 z-50">
    <div class="w-full h-full md:w-full md:max-w-4xl md:max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800 md:shadow-lg md:rounded-xl">
      <!-- Header -->
      <div class="sticky top-0 z-10 px-4 md:px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
          <i class="fas fa-cogs mr-2 text-blue-600 dark:text-purple-400"></i>
          {{ mode === 'add' ? 'Add Equipment' : 'Edit Equipment' }}
        </h3>
        <button 
          @click="$emit('close')"
          class="md:hidden p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>

      <div class="px-4 md:px-6 pb-6 pb-20 md:pb-6">
        <!-- Mode Selector -->
        <div class="mb-6 flex space-x-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
          <button
            @click="viewMode = 'browse'"
            :class="[
              'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors',
              viewMode === 'browse'
                ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-purple-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'
            ]"
          >
            <i class="fas fa-search mr-2"></i>
            Browse Equipment
          </button>
          <button
            @click="viewMode = 'custom'"
            :class="[
              'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors',
              viewMode === 'custom'
                ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-purple-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'
            ]"
          >
            <i class="fas fa-plus mr-2"></i>
            Custom Entry
          </button>
        </div>

        <!-- Browse Equipment Mode -->
        <div v-if="viewMode === 'browse'">
          <EquipmentSelector @select="selectEquipment" />
          
          <!-- Selected Equipment Preview -->
          <div v-if="selectedEquipment" class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h4 class="font-semibold text-blue-900 dark:text-blue-200 mb-3">
              <i class="fas fa-check-circle mr-2"></i>
              Selected: {{ selectedEquipment.manufacturer }} {{ selectedEquipment.model_name }}
            </h4>
            
            <!-- Custom Specifications Form -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">
                  Installation Notes (Optional)
                </label>
                <textarea
                  v-model="installationNotes"
                  rows="3"
                  class="w-full px-3 py-2 border border-blue-200 dark:border-blue-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  placeholder="Add any installation notes or custom settings..."
                ></textarea>
              </div>

              <!-- Dynamic Custom Specifications based on equipment category -->
              <div v-if="selectedEquipment.specifications" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  v-for="(value, key) in getEditableSpecs(selectedEquipment)"
                  :key="key"
                  class="space-y-1"
                >
                  <label class="block text-sm font-medium text-blue-800 dark:text-blue-300">
                    {{ formatSpecKey(key) }}
                  </label>
                  
                  <!-- Different input types based on specification type -->
                  <select
                    v-if="getSpecType(key, value) === 'select'"
                    v-model="customSpecs[key]"
                    class="w-full px-3 py-2 border border-blue-200 dark:border-blue-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  >
                    <option :value="value">{{ value }} (Default)</option>
                    <option
                      v-for="option in getSpecOptions(key)"
                      :key="option"
                      :value="option"
                    >
                      {{ option }}
                    </option>
                  </select>

                  <input
                    v-else-if="getSpecType(key, value) === 'number'"
                    v-model.number="customSpecs[key]"
                    type="number"
                    step="0.1"
                    :placeholder="String(value)"
                    class="w-full px-3 py-2 border border-blue-200 dark:border-blue-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  />

                  <input
                    v-else
                    v-model="customSpecs[key]"
                    type="text"
                    :placeholder="String(value)"
                    class="w-full px-3 py-2 border border-blue-200 dark:border-blue-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Custom Entry Mode -->
        <div v-else-if="viewMode === 'custom'">
          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-6">
            <div class="flex">
              <i class="fas fa-info-circle text-yellow-600 dark:text-yellow-400 mr-2 mt-0.5"></i>
              <div class="text-sm text-yellow-800 dark:text-yellow-200">
                <p class="font-medium">Custom Equipment Entry</p>
                <p>Add equipment that's not in our database. This will be saved to your setup only.</p>
              </div>
            </div>
          </div>

          <form @submit.prevent="saveCustomEquipment" class="space-y-6">
            <!-- Category Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Equipment Category *
              </label>
              <select
                v-model="customEquipment.category"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              >
                <option value="">Select Category</option>
                <option value="String">String</option>
                <option value="Sight">Sight</option>
                <option value="Stabilizer">Stabilizer</option>
                <option value="Arrow Rest">Arrow Rest</option>
                <option value="Weight">Weight</option>
              </select>
            </div>

            <!-- Basic Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Manufacturer *
                </label>
                <select
                  v-if="!showCustomManufacturer"
                  @change="handleManufacturerSelection($event.target.value)"
                  :value="customEquipment.manufacturer"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  required
                >
                  <option value="">Select Manufacturer</option>
                  <option v-if="loadingManufacturers" disabled>Loading manufacturers...</option>
                  <option v-if="!loadingManufacturers && customEquipment.category && availableManufacturers.length === 0" disabled>No manufacturers found</option>
                  <option 
                    v-for="manufacturer in availableManufacturers" 
                    :key="manufacturer" 
                    :value="manufacturer"
                  >
                    {{ manufacturer }}
                  </option>
                  <option v-if="availableManufacturers.length > 0" value="Other">Other</option>
                </select>
                
                <!-- Custom manufacturer input -->
                <input
                  v-if="showCustomManufacturer"
                  v-model="customEquipment.manufacturer"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  placeholder="Enter custom manufacturer name..."
                />
                
                <!-- Back to dropdown button -->
                <button
                  v-if="showCustomManufacturer"
                  @click="showCustomManufacturer = false; customEquipment.manufacturer = ''"
                  type="button"
                  class="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                >
                  ← Back to manufacturer list
                </button>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Model Name *
                </label>
                <input
                  v-model="customEquipment.model_name"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  placeholder="e.g., Fix Series 5-Pin"
                />
              </div>
            </div>

            <!-- Optional Fields -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Weight (grams)
                </label>
                <input
                  v-model.number="customEquipment.weight_grams"
                  type="number"
                  step="0.1"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  placeholder="e.g., 285"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Price Range
                </label>
                <input
                  v-model="customEquipment.price_range"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  placeholder="e.g., $60-80"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                v-model="customEquipment.description"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                placeholder="Describe the equipment..."
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Installation Notes
              </label>
              <textarea
                v-model="customEquipment.installation_notes"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                placeholder="Add any installation notes..."
              ></textarea>
            </div>
          </form>
        </div>

        <!-- Action Buttons -->
        <div class="fixed bottom-0 left-0 right-0 md:sticky md:bottom-auto flex justify-end space-x-3 p-4 md:pt-4 md:mt-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 md:relative">
          <CustomButton
            type="button"
            @click="$emit('close')"
            variant="outlined"
            class="text-gray-700 dark:text-gray-200 hidden md:inline-flex"
          >
            Cancel
          </CustomButton>
          
          <CustomButton
            @click="saveEquipment"
            variant="filled"
            :disabled="isSaving || !canSave"
            class="flex-1 md:flex-none text-white bg-blue-600 hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
          >
            <span v-if="isSaving">Saving...</span>
            <span v-else>{{ mode === 'add' ? 'Add Equipment' : 'Update Equipment' }}</span>
          </CustomButton>
        </div>

        <p v-if="error" class="mt-3 text-sm text-red-500">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  mode: {
    type: String,
    default: 'add' // 'add' or 'edit'
  },
  bowSetupId: {
    type: Number,
    required: true
  },
  existingEquipment: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])

// Data
const viewMode = ref('browse')
const selectedEquipment = ref(null)
const installationNotes = ref('')
const customSpecs = ref({})
const isSaving = ref(false)
const error = ref('')

const customEquipment = ref({
  category: '',
  manufacturer: '',
  model_name: '',
  weight_grams: null,
  price_range: '',
  description: '',
  installation_notes: ''
})

// API composable and manufacturer data
const api = useApi()
const availableManufacturers = ref([])
const loadingManufacturers = ref(false)
const showCustomManufacturer = ref(false)

// Computed
const canSave = computed(() => {
  if (viewMode.value === 'browse') {
    return selectedEquipment.value !== null
  } else {
    return customEquipment.value.category && 
           customEquipment.value.manufacturer && 
           customEquipment.value.model_name
  }
})

// Methods
const selectEquipment = (equipment) => {
  selectedEquipment.value = equipment
  // Initialize custom specs with default values
  customSpecs.value = { ...equipment.specifications }
}

const getEditableSpecs = (equipment) => {
  if (!equipment.specifications) return {}
  
  // Return key specifications that users might want to customize
  const editableKeys = [
    'length_inches', 'weight_ounces', 'strand_count', 'pin_count',
    'adjustment_type', 'material', 'thread_size'
  ]
  
  const editable = {}
  editableKeys.forEach(key => {
    if (equipment.specifications[key] !== undefined) {
      editable[key] = equipment.specifications[key]
    }
  })
  
  return editable
}

const getSpecType = (key, value) => {
  if (typeof value === 'number') return 'number'
  if (key.includes('type') || key.includes('material')) return 'select'
  return 'text'
}

const getSpecOptions = (key) => {
  const optionsMap = {
    'material': ['Carbon', 'Aluminum', 'Steel', 'Titanium'],
    'adjustment_type': ['Micro', 'Standard', 'Toolless'],
    'sight_type': ['Multi-pin', 'Single-pin', 'Scope'],
    'rest_type': ['Drop-away', 'Blade', 'Launcher', 'Whisker-biscuit'],
    'thread_size': ['5/16-24', '1/4-20', '8-32']
  }
  return optionsMap[key] || []
}

const formatSpecKey = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

// Load manufacturers for a specific equipment category
const loadManufacturersForCategory = async (category) => {
  if (!category) {
    availableManufacturers.value = []
    return
  }
  
  try {
    loadingManufacturers.value = true
    
    // Map equipment category names to API category names
    const categoryMapping = {
      'String': 'strings',
      'Sight': 'sights', 
      'Stabilizer': 'stabilizers',
      'Arrow Rest': 'arrow_rests',
      'Weight': 'weights'
    }
    
    const apiCategory = categoryMapping[category]
    if (!apiCategory) {
      availableManufacturers.value = []
      return
    }
    
    const response = await api.get(`/bow-equipment/manufacturers?category=${apiCategory}`)
    availableManufacturers.value = response?.manufacturers || []
  } catch (error) {
    console.error('Error loading manufacturers:', error)
    availableManufacturers.value = []
  } finally {
    loadingManufacturers.value = false
  }
}

// Handle manufacturer selection
const handleManufacturerSelection = (value) => {
  if (value === 'Other') {
    showCustomManufacturer.value = true
    customEquipment.value.manufacturer = ''
  } else {
    showCustomManufacturer.value = false
    customEquipment.value.manufacturer = value
  }
}

// Watch for category changes to load manufacturers
watch(() => customEquipment.value.category, (newCategory) => {
  customEquipment.value.manufacturer = ''
  showCustomManufacturer.value = false
  loadManufacturersForCategory(newCategory)
})

const saveEquipment = async () => {
  if (!canSave.value) return
  
  isSaving.value = true
  error.value = ''
  
  try {
    const { $fetch } = useNuxtApp()
    
    if (viewMode.value === 'browse') {
      // Save existing equipment
      const payload = {
        equipment_id: selectedEquipment.value.id,
        installation_notes: installationNotes.value,
        custom_specifications: customSpecs.value
      }
      
      await $fetch(`/api/bow-setups/${props.bowSetupId}/equipment`, {
        method: 'POST',
        body: payload
      })
    } else {
      // Create and save custom equipment
      // This would require a custom equipment creation endpoint
      // For now, we'll show an error message
      throw new Error('Custom equipment creation not yet implemented')
    }
    
    emit('saved')
    emit('close')
  } catch (err) {
    console.error('Error saving equipment:', err)
    error.value = err.message || 'Failed to save equipment'
  } finally {
    isSaving.value = false
  }
}

const saveCustomEquipment = () => {
  // This would be implemented when custom equipment creation is available
  console.log('Custom equipment save not yet implemented')
}

// Lifecycle
onMounted(() => {
  if (props.existingEquipment) {
    // Initialize for editing mode
    selectedEquipment.value = props.existingEquipment
    installationNotes.value = props.existingEquipment.installation_notes || ''
    customSpecs.value = { ...props.existingEquipment.custom_specifications }
  }
})
</script>