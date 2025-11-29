<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
      <!-- Backdrop -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 dark:bg-gray-900 bg-opacity-75 dark:bg-opacity-75" @click="close"></div>

      <!-- Modal -->
      <div class="relative inline-block w-full max-w-2xl overflow-hidden text-left align-bottom transition-all transform bg-white dark:bg-gray-800 rounded-lg shadow-xl sm:my-8 sm:align-middle">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-sliders-h mr-2 text-purple-600 dark:text-purple-400"></i>
              {{ isEditing ? 'Edit Bow Setup Configuration' : 'New Bow Setup Configuration' }}
            </h3>
            <button @click="close" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <i class="fas fa-times text-lg"></i>
            </button>
          </div>
        </div>

        <!-- Form -->
        <div class="px-6 py-4 max-h-[70vh] overflow-y-auto">
          <!-- Basic Info -->
          <div class="space-y-4 mb-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Configuration Name *
              </label>
              <input
                v-model="formData.name"
                type="text"
                placeholder="e.g., Indoor Competition Setup"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <textarea
                v-model="formData.description"
                rows="2"
                placeholder="Optional description of this tuning setup..."
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              ></textarea>
            </div>

            <div v-if="!isEditing" class="flex items-center">
              <input
                v-model="formData.is_active"
                type="checkbox"
                id="setActive"
                class="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500"
              />
              <label for="setActive" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Set as active configuration
              </label>
            </div>
          </div>

          <!-- Tuning Parameters -->
          <div class="space-y-6">
            <div v-for="group in parameterGroups" :key="group.name">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                <i :class="group.icon" class="mr-2 text-purple-500"></i>
                {{ group.name }}
              </h4>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div
                  v-for="param in group.parameters"
                  :key="param.key"
                  class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3"
                >
                  <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                    {{ param.label }}
                    <span v-if="param.unit" class="text-gray-400">({{ param.unit }})</span>
                  </label>

                  <!-- Text/Number Input -->
                  <input
                    v-if="param.type === 'text' || param.type === 'number'"
                    v-model="formData.values[param.key].value"
                    :type="param.type"
                    :step="param.step || 'any'"
                    :min="param.min"
                    :max="param.max"
                    :placeholder="param.placeholder || ''"
                    class="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />

                  <!-- Select Input -->
                  <select
                    v-else-if="param.type === 'select'"
                    v-model="formData.values[param.key].value"
                    class="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Select...</option>
                    <option v-for="opt in param.options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>

                  <!-- Range/Slider Input -->
                  <div v-else-if="param.type === 'range'" class="flex items-center space-x-2">
                    <input
                      v-model.number="formData.values[param.key].value"
                      type="range"
                      :min="param.min"
                      :max="param.max"
                      :step="param.step || 1"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600"
                    />
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300 w-12 text-right">
                      {{ formData.values[param.key].value || param.min }}
                    </span>
                  </div>

                  <!-- Notes -->
                  <input
                    v-model="formData.values[param.key].notes"
                    type="text"
                    placeholder="Notes..."
                    class="w-full px-2 py-1 mt-1 border border-gray-200 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs focus:ring-1 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Change Reason (for edits) -->
          <div v-if="isEditing" class="mt-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Change Reason <span class="text-gray-400">(optional)</span>
            </label>
            <textarea
              v-model="formData.user_note"
              rows="2"
              placeholder="Why are you making this change?"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            ></textarea>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
          <CustomButton
            @click="close"
            variant="outlined"
            class="text-gray-600 border-gray-300"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="save"
            variant="filled"
            :disabled="saving || !formData.name"
            class="bg-purple-600 text-white hover:bg-purple-700"
          >
            <span v-if="saving">Saving...</span>
            <span v-else>{{ isEditing ? 'Save Changes' : 'Create Configuration' }}</span>
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  },
  config: {
    type: Object,
    default: null
  },
  bowType: {
    type: String,
    default: 'recurve'
  }
})

const emit = defineEmits(['close', 'saved'])

const api = useApi()
const saving = ref(false)

const isEditing = computed(() => !!props.config)

// Parameter definitions by bow type
const allParameters = {
  // Common to most bows
  brace_height: { label: 'Brace Height', unit: 'inches', type: 'number', step: 0.0625, min: 5, max: 10, placeholder: '8.75', group: 'basic' },
  nocking_point: { label: 'Nocking Point Height', unit: 'inches', type: 'number', step: 0.0625, min: 0, max: 1, placeholder: '0.25', group: 'basic' },
  string_material: { label: 'String Material', type: 'select', options: ['Dacron B50', 'Fast Flight', 'BCY 452X', 'BCY X99', 'BCY 8190', 'Angel Dyneema', 'Flemish Twist', 'Other'], group: 'string' },
  string_strands: { label: 'String Strands', type: 'number', min: 8, max: 24, step: 1, placeholder: '14', group: 'string' },

  // Recurve/Barebow specific
  tiller_top: { label: 'Tiller (Top)', unit: 'inches', type: 'number', step: 0.0625, min: 7, max: 12, placeholder: '9.25', group: 'limb' },
  tiller_bottom: { label: 'Tiller (Bottom)', unit: 'inches', type: 'number', step: 0.0625, min: 7, max: 12, placeholder: '9.0', group: 'limb' },
  plunger_pressure: { label: 'Plunger Pressure', unit: '1-10', type: 'range', min: 1, max: 10, step: 0.5, group: 'rest' },
  plunger_position: { label: 'Plunger Position', unit: 'mm', type: 'number', step: 0.5, min: -5, max: 5, placeholder: '0', group: 'rest' },
  clicker_position: { label: 'Clicker Position', unit: 'mm', type: 'number', step: 1, min: 0, max: 100, placeholder: '25', group: 'sight' },
  sight_pin_position: { label: 'Sight Pin Position', type: 'text', placeholder: 'e.g., 4.5 marks', group: 'sight' },

  // Compound specific
  axle_to_axle: { label: 'Axle-to-Axle', unit: 'inches', type: 'number', step: 0.125, min: 28, max: 40, placeholder: '33', group: 'basic' },
  draw_weight_actual: { label: 'Draw Weight (Actual)', unit: 'lbs', type: 'number', step: 0.5, min: 10, max: 100, placeholder: '60', group: 'basic' },
  letoff_percentage: { label: 'Let-off', unit: '%', type: 'number', step: 1, min: 50, max: 95, placeholder: '80', group: 'cam' },
  cam_timing: { label: 'Cam Timing', type: 'select', options: ['Synced', 'Top Slightly Advanced', 'Bottom Slightly Advanced', 'Needs Adjustment'], group: 'cam' },
  cam_lean: { label: 'Cam Lean', type: 'select', options: ['Neutral', 'Left', 'Right', 'Needs Adjustment'], group: 'cam' },
  peep_height: { label: 'Peep Height', unit: 'inches from nock', type: 'number', step: 0.125, min: 3, max: 8, placeholder: '5.5', group: 'sight' },
  rest_centershot: { label: 'Rest Centershot', unit: 'inches', type: 'number', step: 0.03125, min: 0.5, max: 1.5, placeholder: '0.8125', group: 'rest' },
  rest_height: { label: 'Rest Height', unit: 'inches', type: 'number', step: 0.03125, min: 0, max: 1, placeholder: '0.5', group: 'rest' },
  cable_guard_position: { label: 'Cable Guard Position', unit: 'inches', type: 'number', step: 0.125, min: 0, max: 3, placeholder: '1.5', group: 'basic' },

  // Longbow/Traditional specific
  arrow_pass_position: { label: 'Arrow Pass Position', type: 'text', placeholder: 'e.g., center of grip', group: 'rest' }
}

// Parameters by bow type
const parametersByBowType = {
  recurve: ['brace_height', 'tiller_top', 'tiller_bottom', 'nocking_point', 'plunger_pressure', 'plunger_position', 'clicker_position', 'sight_pin_position', 'string_material', 'string_strands'],
  barebow: ['brace_height', 'tiller_top', 'tiller_bottom', 'nocking_point', 'plunger_pressure', 'plunger_position', 'string_material', 'string_strands'],
  compound: ['brace_height', 'axle_to_axle', 'draw_weight_actual', 'letoff_percentage', 'cam_timing', 'cam_lean', 'nocking_point', 'peep_height', 'rest_centershot', 'rest_height', 'cable_guard_position', 'string_material'],
  traditional: ['brace_height', 'tiller_top', 'tiller_bottom', 'nocking_point', 'string_material', 'string_strands', 'arrow_pass_position'],
  longbow: ['brace_height', 'nocking_point', 'string_material', 'string_strands', 'arrow_pass_position']
}

// Group definitions
const groupDefinitions = {
  basic: { name: 'Basic Measurements', icon: 'fas fa-ruler-combined' },
  limb: { name: 'Limb Setup', icon: 'fas fa-arrows-alt-v' },
  string: { name: 'String Setup', icon: 'fas fa-link' },
  rest: { name: 'Rest & Plunger', icon: 'fas fa-hand-paper' },
  sight: { name: 'Sight Setup', icon: 'fas fa-crosshairs' },
  cam: { name: 'Cam Setup', icon: 'fas fa-cogs' }
}

// Get parameters for current bow type
const currentParameters = computed(() => {
  const bowType = props.bowType?.toLowerCase() || 'recurve'
  const paramKeys = parametersByBowType[bowType] || parametersByBowType.recurve
  return paramKeys.map(key => ({
    key,
    ...allParameters[key]
  }))
})

// Group parameters
const parameterGroups = computed(() => {
  const groups = {}

  currentParameters.value.forEach(param => {
    const groupKey = param.group || 'basic'
    if (!groups[groupKey]) {
      groups[groupKey] = {
        ...groupDefinitions[groupKey],
        parameters: []
      }
    }
    groups[groupKey].parameters.push(param)
  })

  // Return in specific order
  const orderedGroups = []
  const groupOrder = ['basic', 'limb', 'string', 'rest', 'sight', 'cam']
  groupOrder.forEach(key => {
    if (groups[key]) {
      orderedGroups.push(groups[key])
    }
  })

  return orderedGroups
})

// Form data
const formData = ref({
  name: '',
  description: '',
  is_active: false,
  user_note: '',
  values: {}
})

// Initialize form values
const initializeFormValues = () => {
  // Initialize all parameters with empty values
  const values = {}
  currentParameters.value.forEach(param => {
    values[param.key] = {
      value: '',
      unit: param.unit || '',
      notes: ''
    }
  })

  // If editing, populate with existing values
  if (props.config) {
    formData.value.name = props.config.name || ''
    formData.value.description = props.config.description || ''
    formData.value.is_active = props.config.is_active || false

    if (props.config.values) {
      Object.entries(props.config.values).forEach(([key, val]) => {
        if (values[key]) {
          values[key] = {
            value: val.value || '',
            unit: val.unit || values[key].unit,
            notes: val.notes || ''
          }
        }
      })
    }
  }

  formData.value.values = values
}

// Close modal
const close = () => {
  emit('close')
}

// Save configuration
const save = async () => {
  if (!formData.value.name) return

  try {
    saving.value = true

    // Prepare values - only include non-empty ones
    const cleanValues = {}
    Object.entries(formData.value.values).forEach(([key, val]) => {
      if (val.value !== '' && val.value !== null && val.value !== undefined) {
        cleanValues[key] = {
          value: val.value,
          unit: val.unit || allParameters[key]?.unit || '',
          notes: val.notes || ''
        }
      }
    })

    const payload = {
      name: formData.value.name,
      description: formData.value.description,
      values: cleanValues,
      user_note: formData.value.user_note
    }

    if (!isEditing.value) {
      payload.is_active = formData.value.is_active
    }

    if (isEditing.value) {
      await api.put(`/tuning-configs/${props.config.id}`, payload)
    } else {
      await api.post(`/bow-setups/${props.bowSetup.id}/tuning-configs`, payload)
    }

    emit('saved')
  } catch (error) {
    console.error('Error saving tuning config:', error)
    alert('Failed to save tuning configuration')
  } finally {
    saving.value = false
  }
}

// Watch for config changes
watch(() => props.config, () => {
  initializeFormValues()
}, { immediate: true })

// Watch for bow type changes
watch(() => props.bowType, () => {
  initializeFormValues()
})

onMounted(() => {
  initializeFormValues()
})
</script>
