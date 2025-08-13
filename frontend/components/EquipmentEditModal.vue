<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-2xl">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
          <i class="fas fa-edit mr-2 text-blue-600"></i>
          Edit Equipment: {{ equipment.manufacturer_name || equipment.manufacturer }} {{ equipment.model_name }}
        </h3>
      </div>

      <!-- Content -->
      <div class="px-6 py-4 max-h-96 overflow-y-auto">
        <!-- Equipment Info Display -->
        <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div class="flex items-center space-x-4">
            <div class="w-16 h-16 bg-gray-100 dark:bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <img
                v-if="equipment.image_url"
                :src="equipment.image_url"
                :alt="equipment.model_name"
                class="w-full h-full object-cover rounded-lg"
              />
              <i v-else :class="getCategoryIcon(equipment.category_name)" class="text-2xl text-gray-400"></i>
            </div>
            <div>
              <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                {{ equipment.manufacturer_name || equipment.manufacturer }} {{ equipment.model_name }}
              </h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ equipment.category_name }}</p>
              <div v-if="equipment.weight_grams" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Weight: {{ equipment.weight_grams }}g
              </div>
            </div>
          </div>
        </div>

        <!-- Edit Form -->
        <form @submit.prevent="handleSave" class="space-y-4">
          <!-- Installation Notes -->
          <div>
            <label for="installationNotes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Installation Notes
            </label>
            <textarea
              id="installationNotes"
              v-model="formData.installation_notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              placeholder="Add notes about installation, settings, or configuration..."
            ></textarea>
          </div>

          <!-- Custom Specifications -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Custom Specifications
            </label>
            <div class="space-y-3">
              <div
                v-for="(spec, index) in customSpecs"
                :key="index"
                class="flex space-x-2"
              >
                <input
                  v-model="spec.key"
                  type="text"
                  placeholder="Specification name"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                />
                <input
                  v-model="spec.value"
                  type="text"
                  placeholder="Value"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                />
                <CustomButton
                  @click="removeCustomSpec(index)"
                  variant="text"
                  size="small"
                  class="text-red-600 hover:text-red-700"
                >
                  <i class="fas fa-trash"></i>
                </CustomButton>
              </div>
              <CustomButton
                @click="addCustomSpec"
                variant="outlined"
                size="small"
                class="text-blue-600 border-blue-600 hover:bg-blue-50"
              >
                <i class="fas fa-plus mr-2"></i>
                Add Custom Specification
              </CustomButton>
            </div>
          </div>

          <!-- Active Status -->
          <div class="flex items-center">
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="formData.is_active"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              <span class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                Equipment is active on this bow
              </span>
            </label>
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
        <div class="flex justify-end space-x-3">
          <CustomButton @click="$emit('close')" variant="outlined">
            Cancel
          </CustomButton>
          <CustomButton
            @click="handleSave"
            variant="filled"
            :disabled="saving"
            class="bg-blue-600 text-white hover:bg-blue-700"
          >
            <span v-if="saving">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              Saving...
            </span>
            <span v-else>
              <i class="fas fa-save mr-2"></i>
              Save Changes
            </span>
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  equipment: {
    type: Object,
    required: true
  },
  bowSetup: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['save', 'close'])

// State
const saving = ref(false)
const formData = ref({
  installation_notes: '',
  is_active: true
})
const customSpecs = ref([])

// Computed
const getCategoryIcon = computed(() => {
  return (categoryName) => {
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
})

// Methods
const initializeForm = () => {
  formData.value = {
    installation_notes: props.equipment.installation_notes || '',
    is_active: props.equipment.is_active !== false
  }

  // Initialize custom specifications
  if (props.equipment.custom_specifications) {
    try {
      const specs = typeof props.equipment.custom_specifications === 'string' 
        ? JSON.parse(props.equipment.custom_specifications)
        : props.equipment.custom_specifications
      
      customSpecs.value = Object.entries(specs).map(([key, value]) => ({ key, value }))
    } catch (error) {
      console.error('Error parsing custom specifications:', error)
      customSpecs.value = []
    }
  } else {
    customSpecs.value = []
  }
}

const addCustomSpec = () => {
  customSpecs.value.push({ key: '', value: '' })
}

const removeCustomSpec = (index) => {
  customSpecs.value.splice(index, 1)
}

const handleSave = async () => {
  try {
    saving.value = true

    // Convert custom specs array to object
    const customSpecsObject = {}
    customSpecs.value.forEach(spec => {
      if (spec.key && spec.value) {
        customSpecsObject[spec.key] = spec.value
      }
    })

    const updatedEquipment = {
      id: props.equipment.id,
      installation_notes: formData.value.installation_notes,
      custom_specifications: customSpecsObject,
      is_active: formData.value.is_active
    }

    emit('save', updatedEquipment)
  } catch (error) {
    console.error('Error saving equipment:', error)
  } finally {
    saving.value = false
  }
}

// Lifecycle
onMounted(() => {
  initializeForm()
})
</script>