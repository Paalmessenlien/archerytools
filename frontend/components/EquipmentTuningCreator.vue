<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <i :class="`${equipmentCategory.icon} text-2xl ${equipmentCategory.color}`"></i>
            <div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
                {{ equipmentCategory.label }} Setup Documentation
              </h2>
              <p class="text-sm text-gray-600 dark:text-gray-300">
                {{ bowSetup.name }} • {{ formatBowType(bowSetup.bow_type) }}
              </p>
            </div>
          </div>
          <button 
            @click="$emit('cancel')"
            class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>
      </div>

      <!-- Form Content -->
      <div class="p-6 space-y-6">
        <!-- Entry Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Entry Title
          </label>
          <input
            v-model="entryData.title"
            type="text"
            placeholder="e.g., Sight pin adjustment for 20-60 yard marks"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <!-- Quick Setup Options -->
        <div v-if="quickSetupOptions.length > 0">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quick Setup Template
          </label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              v-for="option in quickSetupOptions"
              :key="option.id"
              @click="applyQuickSetup(option)"
              class="p-3 text-left border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div class="flex items-center space-x-2">
                <i :class="`${option.icon} ${equipmentCategory.color}`"></i>
                <div>
                  <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {{ option.title }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ option.description }}
                  </div>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Dynamic Form Fields -->
        <div v-if="dynamicFields.length > 0">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            {{ equipmentCategory.label }} Specifics
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="field in dynamicFields" 
              :key="field.name"
              class="space-y-2"
            >
              <label class="block text-sm text-gray-600 dark:text-gray-400">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500">*</span>
              </label>
              
              <!-- Text Input -->
              <input
                v-if="field.type === 'text'"
                v-model="entryData.dynamicFields[field.name]"
                :type="field.inputType || 'text'"
                :placeholder="field.placeholder"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-blue-500 focus:border-blue-500"
              />
              
              <!-- Number Input -->
              <input
                v-else-if="field.type === 'number'"
                v-model.number="entryData.dynamicFields[field.name]"
                type="number"
                :step="field.step"
                :min="field.min"
                :max="field.max"
                :placeholder="field.placeholder"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-blue-500 focus:border-blue-500"
              />
              
              <!-- Select -->
              <select
                v-else-if="field.type === 'select'"
                v-model="entryData.dynamicFields[field.name]"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select...</option>
                <option 
                  v-for="option in field.options" 
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
              
              <!-- Textarea -->
              <textarea
                v-else-if="field.type === 'textarea'"
                v-model="entryData.dynamicFields[field.name]"
                :placeholder="field.placeholder"
                rows="3"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Setup Notes & Observations
          </label>
          <textarea
            v-model="entryData.content"
            :placeholder="contentPlaceholder"
            rows="8"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Document your process, measurements, adjustments, and results in detail.
          </p>
        </div>

        <!-- Tags -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Tags
          </label>
          <div class="flex flex-wrap gap-2 mb-2">
            <span
              v-for="(tag, index) in entryData.tags"
              :key="index"
              class="inline-flex items-center px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full"
            >
              {{ tag }}
              <button
                @click="removeTag(index)"
                class="ml-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
              >
                <i class="fas fa-times text-xs"></i>
              </button>
            </span>
          </div>
          <div class="flex">
            <input
              v-model="newTag"
              @keyup.enter="addTag"
              placeholder="Add tag and press Enter"
              class="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-l-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              @click="addTag"
              class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded-r-md transition-colors"
            >
              Add
            </button>
          </div>
          <div v-if="suggestedTags.length > 0" class="mt-2">
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Suggested tags:</p>
            <div class="flex flex-wrap gap-1">
              <button
                v-for="tag in suggestedTags"
                :key="tag"
                @click="addTag(tag)"
                class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                + {{ tag }}
              </button>
            </div>
          </div>
        </div>

        <!-- Equipment Specific Information -->
        <div v-if="hasEquipmentInfo" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Equipment Information
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-600 dark:text-gray-400">Category:</span>
              <span class="ml-2 font-medium text-gray-900 dark:text-gray-100">{{ equipmentCategory.label }}</span>
            </div>
            <div>
              <span class="text-gray-600 dark:text-gray-400">Bow Setup:</span>
              <span class="ml-2 font-medium text-gray-900 dark:text-gray-100">{{ bowSetup.name }}</span>
            </div>
            <div>
              <span class="text-gray-600 dark:text-gray-400">Bow Type:</span>
              <span class="ml-2 font-medium text-gray-900 dark:text-gray-100">{{ formatBowType(bowSetup.bow_type) }}</span>
            </div>
            <div>
              <span class="text-gray-600 dark:text-gray-400">Draw Weight:</span>
              <span class="ml-2 font-medium text-gray-900 dark:text-gray-100">{{ bowSetup.draw_weight }} lbs</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="p-6 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <i class="fas fa-info-circle"></i>
            <span>This entry will be linked to your {{ bowSetup.name }} bow setup</span>
          </div>
          
          <div class="flex items-center space-x-3">
            <button 
              @click="$emit('cancel')"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button 
              @click="saveEntry"
              :disabled="!isValid || saving"
              class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center"
            >
              <div v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              <i v-else class="fas fa-save mr-2"></i>
              {{ saving ? 'Saving...' : 'Save Entry' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

// Props
const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  },
  equipmentCategory: {
    type: Object,
    required: true
  }
})

// Reactive data
const entryData = ref({
  title: '',
  content: '',
  tags: [],
  dynamicFields: {}
})

const newTag = ref('')
const saving = ref(false)

// API composable
const api = useApi()

// Computed properties
const isValid = computed(() => {
  return entryData.value.title.trim().length > 0 && entryData.value.content.trim().length > 0
})

const contentPlaceholder = computed(() => {
  const category = props.equipmentCategory.name
  const placeholders = {
    bow: 'Document tiller measurements, brace height adjustments, timing checks, and performance observations...',
    arrow_rest: 'Record centershot positioning, height adjustments, contact pressure, and clearance measurements...',
    sight: 'Note pin gap measurements, windage/elevation adjustments, distance marks, and sight calibration...',
    release: 'Document trigger sensitivity, grip positioning, length adjustments, and release performance...',
    stabilizer: 'Record weight distribution, length combinations, angle adjustments, and balance effects...',
    string: 'Note serving applications, twist adjustments, stretch measurements, and string maintenance...',
    peep_sight: 'Document height positioning, rotation alignment, size selection, and visibility optimization...',
    other: 'Describe the equipment setup, adjustments made, and performance observations...'
  }
  return placeholders[category] || 'Describe your equipment setup process and observations...'
})

const quickSetupOptions = computed(() => {
  const category = props.equipmentCategory.name
  const options = {
    bow: [
      {
        id: 'initial_setup',
        title: 'Initial Bow Setup',
        description: 'New bow configuration and tuning',
        icon: 'fas fa-plus-circle'
      },
      {
        id: 'timing_adjustment',
        title: 'Timing Adjustment',
        description: 'Cam timing and synchronization',
        icon: 'fas fa-sync-alt'
      }
    ],
    arrow_rest: [
      {
        id: 'centershot_tuning',
        title: 'Centershot Tuning',
        description: 'Initial centershot alignment',
        icon: 'fas fa-crosshairs'
      },
      {
        id: 'height_adjustment',
        title: 'Rest Height Adjustment',
        description: 'Vertical positioning optimization',
        icon: 'fas fa-arrows-alt-v'
      }
    ],
    sight: [
      {
        id: 'pin_gap_setup',
        title: 'Pin Gap Setup',
        description: 'Initial distance pin calibration',
        icon: 'fas fa-bullseye'
      },
      {
        id: 'sight_leveling',
        title: 'Sight Leveling',
        description: 'Sight alignment and leveling',
        icon: 'fas fa-balance-scale'
      }
    ],
    stabilizer: [
      {
        id: 'weight_tuning',
        title: 'Weight Tuning',
        description: 'Stabilizer weight optimization',
        icon: 'fas fa-weight-hanging'
      }
    ]
  }
  return options[category] || []
})

const dynamicFields = computed(() => {
  const category = props.equipmentCategory.name
  const fields = {
    bow: [
      {
        name: 'brace_height',
        label: 'Brace Height',
        type: 'text',
        placeholder: 'e.g., 7.25"',
        required: false
      },
      {
        name: 'tiller_measurement',
        label: 'Tiller Measurement',
        type: 'text',
        placeholder: 'e.g., Top: 1/4", Bottom: 1/4"',
        required: false
      }
    ],
    arrow_rest: [
      {
        name: 'centershot_position',
        label: 'Centershot Position',
        type: 'text',
        placeholder: 'e.g., 13/16" from riser',
        required: false
      },
      {
        name: 'rest_height',
        label: 'Rest Height',
        type: 'text',
        placeholder: 'e.g., 1" above shelf',
        required: false
      }
    ],
    sight: [
      {
        name: 'pin_distances',
        label: 'Pin Distances',
        type: 'textarea',
        placeholder: 'e.g., 20yd: top pin, 30yd: 2nd pin...',
        required: false
      }
    ],
    stabilizer: [
      {
        name: 'stabilizer_length',
        label: 'Stabilizer Length',
        type: 'text',
        placeholder: 'e.g., 30"',
        required: false
      },
      {
        name: 'weight_configuration',
        label: 'Weight Configuration',
        type: 'text',
        placeholder: 'e.g., 4oz front, 12oz side',
        required: false
      }
    ]
  }
  
  const categoryFields = fields[category] || []
  
  // Initialize dynamic fields object
  categoryFields.forEach(field => {
    if (!(field.name in entryData.value.dynamicFields)) {
      entryData.value.dynamicFields[field.name] = ''
    }
  })
  
  return categoryFields
})

const suggestedTags = computed(() => {
  const category = props.equipmentCategory.name
  const bowType = props.bowSetup.bow_type
  
  const baseTags = [category, bowType, 'setup', 'tuning']
  const categoryTags = {
    bow: ['timing', 'tiller', 'brace-height'],
    arrow_rest: ['centershot', 'clearance', 'height'],
    sight: ['pins', 'windage', 'elevation'],
    release: ['trigger', 'sensitivity', 'grip'],
    stabilizer: ['balance', 'weight', 'vibration'],
    string: ['serving', 'twist', 'maintenance'],
    peep_sight: ['alignment', 'rotation', 'visibility'],
    other: ['modification', 'accessory', 'custom']
  }
  
  const allSuggestions = [...baseTags, ...(categoryTags[category] || [])]
  
  // Filter out already added tags
  return allSuggestions.filter(tag => !entryData.value.tags.includes(tag))
})

const hasEquipmentInfo = computed(() => {
  return props.bowSetup && props.equipmentCategory
})

// Methods
const addTag = (tagText = null) => {
  const tag = (tagText || newTag.value).trim().toLowerCase()
  if (tag && !entryData.value.tags.includes(tag)) {
    entryData.value.tags.push(tag)
    newTag.value = ''
  }
}

const removeTag = (index) => {
  entryData.value.tags.splice(index, 1)
}

const applyQuickSetup = (option) => {
  entryData.value.title = option.title
  entryData.value.tags.push(option.id.replace('_', '-'))
  
  // Add category-specific content templates
  const templates = {
    initial_setup: `Initial setup and configuration for ${props.equipmentCategory.label.toLowerCase()}.\n\nSetup process:\n- \n\nMeasurements:\n- \n\nObservations:\n- \n\nNext steps:\n- `,
    centershot_tuning: `Centershot alignment process for arrow rest.\n\nInitial position:\n- \n\nAdjustments made:\n- \n\nFinal position:\n- \n\nTest results:\n- `,
    pin_gap_setup: `Pin gap calibration for sight setup.\n\nDistances marked:\n- \n\nPin positions:\n- \n\nAdjustments needed:\n- `
  }
  
  if (templates[option.id]) {
    entryData.value.content = templates[option.id]
  }
}

const saveEntry = async () => {
  if (!isValid.value) return
  
  saving.value = true
  try {
    // Prepare journal entry data
    const journalData = {
      entry_type: 'equipment_change',
      title: entryData.value.title,
      content: entryData.value.content,
      tags: entryData.value.tags,
      bow_setup_id: props.bowSetup.id,
      linked_equipment: null, // We might enhance this later to link specific equipment pieces
      session_type: props.equipmentCategory.name,
      session_metadata: {
        equipment_category: props.equipmentCategory.name,
        equipment_label: props.equipmentCategory.label,
        bow_setup: props.bowSetup,
        dynamic_fields: entryData.value.dynamicFields
      }
    }
    
    const response = await api.post('/journal/entries', journalData)
    
    // Emit success event
    emit('entry-created', {
      entry_id: response.id,
      entry: response,
      equipment_category: props.equipmentCategory,
      bow_setup: props.bowSetup
    })
    
  } catch (error) {
    console.error('Failed to create equipment entry:', error)
    // Could add error notification here
  } finally {
    saving.value = false
  }
}

// Format utility functions
const formatBowType = (bowType) => {
  const types = {
    'compound': 'Compound',
    'recurve': 'Recurve', 
    'traditional': 'Traditional',
    'barebow': 'Barebow'
  }
  return types[bowType] || bowType
}

// Define emits
const emit = defineEmits(['entry-created', 'cancel'])

// Initialize with default title
onMounted(() => {
  entryData.value.title = `${props.equipmentCategory.label} Setup - ${props.bowSetup.name}`
})
</script>

<style scoped>
/* Custom scrollbar for the modal */
.max-h-[90vh] {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.max-h-[90vh]::-webkit-scrollbar {
  width: 6px;
}

.max-h-[90vh]::-webkit-scrollbar-track {
  background: transparent;
}

.max-h-[90vh]::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}
</style>