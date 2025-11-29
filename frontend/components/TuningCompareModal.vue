<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
      <!-- Backdrop -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 dark:bg-gray-900 bg-opacity-75 dark:bg-opacity-75" @click="$emit('close')"></div>

      <!-- Modal -->
      <div class="relative inline-block w-full max-w-4xl overflow-hidden text-left align-bottom transition-all transform bg-white dark:bg-gray-800 rounded-lg shadow-xl sm:my-8 sm:align-middle">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-balance-scale mr-2 text-purple-600 dark:text-purple-400"></i>
              Compare Tuning Configurations
            </h3>
            <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <i class="fas fa-times text-lg"></i>
            </button>
          </div>
        </div>

        <!-- Config Selectors -->
        <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                First Configuration
              </label>
              <select
                v-model="selectedConfig1"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500"
              >
                <option :value="null">Select configuration...</option>
                <option v-for="config in configs" :key="config.id" :value="config.id">
                  {{ config.name }}{{ config.is_active ? ' ★' : '' }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Second Configuration
              </label>
              <select
                v-model="selectedConfig2"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500"
              >
                <option :value="null">Select configuration...</option>
                <option v-for="config in configs" :key="config.id" :value="config.id" :disabled="config.id === selectedConfig1">
                  {{ config.name }}{{ config.is_active ? ' ★' : '' }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Comparison Table -->
        <div class="px-6 py-4 max-h-[60vh] overflow-y-auto">
          <div v-if="!config1 || !config2" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <i class="fas fa-balance-scale text-4xl mb-4"></i>
            <p>Select two configurations to compare</p>
          </div>

          <div v-else>
            <!-- Config Headers -->
            <div class="grid grid-cols-3 gap-4 mb-4 pb-4 border-b border-gray-200 dark:border-gray-600">
              <div class="text-sm font-medium text-gray-600 dark:text-gray-400">Parameter</div>
              <div class="text-center">
                <div class="font-medium text-gray-900 dark:text-gray-100">{{ config1.name }}</div>
                <span v-if="config1.is_active" class="inline-flex items-center px-2 py-0.5 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                  <i class="fas fa-star mr-1"></i> Active
                </span>
              </div>
              <div class="text-center">
                <div class="font-medium text-gray-900 dark:text-gray-100">{{ config2.name }}</div>
                <span v-if="config2.is_active" class="inline-flex items-center px-2 py-0.5 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                  <i class="fas fa-star mr-1"></i> Active
                </span>
              </div>
            </div>

            <!-- Comparison Rows -->
            <div class="space-y-2">
              <div
                v-for="param in allParameters"
                :key="param.key"
                :class="[
                  'grid grid-cols-3 gap-4 py-2 px-3 rounded-lg',
                  getDifferenceClass(param.key)
                ]"
              >
                <div class="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {{ param.label }}
                </div>
                <div class="text-center text-sm text-gray-900 dark:text-gray-100">
                  {{ formatValue(config1.values?.[param.key]) || '—' }}
                </div>
                <div class="text-center text-sm flex items-center justify-center">
                  <span :class="getValueClass(param.key)">
                    {{ formatValue(config2.values?.[param.key]) || '—' }}
                  </span>
                  <span v-if="getDifference(param.key)" class="ml-2 text-xs">
                    {{ getDifference(param.key) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Legend -->
            <div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
              <div class="text-xs text-gray-500 dark:text-gray-400 flex flex-wrap gap-4">
                <span class="flex items-center">
                  <span class="w-3 h-3 bg-green-100 dark:bg-green-900/30 rounded mr-2"></span>
                  Higher value
                </span>
                <span class="flex items-center">
                  <span class="w-3 h-3 bg-red-100 dark:bg-red-900/30 rounded mr-2"></span>
                  Lower value
                </span>
                <span class="flex items-center">
                  <span class="w-3 h-3 bg-gray-100 dark:bg-gray-700 rounded mr-2"></span>
                  Same value
                </span>
                <span class="flex items-center">
                  <span class="w-3 h-3 bg-yellow-100 dark:bg-yellow-900/30 rounded mr-2"></span>
                  Different (text)
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
          <CustomButton
            @click="$emit('close')"
            variant="outlined"
            class="text-gray-600 border-gray-300"
          >
            Close
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  configs: {
    type: Array,
    required: true
  }
})

defineEmits(['close'])

const selectedConfig1 = ref(null)
const selectedConfig2 = ref(null)

// Parameter display labels
const parameterLabels = {
  brace_height: 'Brace Height',
  tiller_top: 'Tiller (Top)',
  tiller_bottom: 'Tiller (Bottom)',
  nocking_point: 'Nocking Point',
  plunger_pressure: 'Plunger Pressure',
  plunger_position: 'Plunger Position',
  clicker_position: 'Clicker Position',
  sight_pin_position: 'Sight Pin Position',
  string_material: 'String Material',
  string_strands: 'String Strands',
  axle_to_axle: 'Axle-to-Axle',
  draw_weight_actual: 'Draw Weight (Actual)',
  letoff_percentage: 'Let-off',
  cam_timing: 'Cam Timing',
  cam_lean: 'Cam Lean',
  peep_height: 'Peep Height',
  rest_centershot: 'Rest Centershot',
  rest_height: 'Rest Height',
  cable_guard_position: 'Cable Guard Position',
  arrow_pass_position: 'Arrow Pass Position'
}

// Get selected configs
const config1 = computed(() => {
  return props.configs.find(c => c.id === selectedConfig1.value) || null
})

const config2 = computed(() => {
  return props.configs.find(c => c.id === selectedConfig2.value) || null
})

// Get all unique parameters from both configs
const allParameters = computed(() => {
  const params = new Set()

  if (config1.value?.values) {
    Object.keys(config1.value.values).forEach(key => params.add(key))
  }
  if (config2.value?.values) {
    Object.keys(config2.value.values).forEach(key => params.add(key))
  }

  return Array.from(params).map(key => ({
    key,
    label: parameterLabels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  })).sort((a, b) => a.label.localeCompare(b.label))
})

// Format value for display
const formatValue = (param) => {
  if (!param || param.value === null || param.value === undefined || param.value === '') {
    return null
  }

  let display = String(param.value)
  if (param.unit) {
    display += ` ${param.unit}`
  }
  return display
}

// Get numeric value for comparison
const getNumericValue = (param) => {
  if (!param || param.value === null || param.value === undefined || param.value === '') {
    return null
  }
  const num = parseFloat(param.value)
  return isNaN(num) ? null : num
}

// Get difference class for row
const getDifferenceClass = (paramKey) => {
  const val1 = config1.value?.values?.[paramKey]
  const val2 = config2.value?.values?.[paramKey]

  const num1 = getNumericValue(val1)
  const num2 = getNumericValue(val2)

  // If both are missing, no highlight
  if (num1 === null && num2 === null && !val1?.value && !val2?.value) {
    return ''
  }

  // If numeric comparison is possible
  if (num1 !== null && num2 !== null) {
    if (num1 === num2) {
      return 'bg-gray-50 dark:bg-gray-700'
    }
    return '' // Individual cell highlighting
  }

  // Text comparison
  const str1 = val1?.value?.toString() || ''
  const str2 = val2?.value?.toString() || ''

  if (str1 === str2) {
    return 'bg-gray-50 dark:bg-gray-700'
  }

  if (str1 && str2) {
    return 'bg-yellow-50 dark:bg-yellow-900/20'
  }

  return ''
}

// Get value class for second column
const getValueClass = (paramKey) => {
  const val1 = config1.value?.values?.[paramKey]
  const val2 = config2.value?.values?.[paramKey]

  const num1 = getNumericValue(val1)
  const num2 = getNumericValue(val2)

  if (num1 !== null && num2 !== null && num1 !== num2) {
    if (num2 > num1) {
      return 'text-green-600 dark:text-green-400 font-medium'
    } else {
      return 'text-red-600 dark:text-red-400 font-medium'
    }
  }

  return 'text-gray-900 dark:text-gray-100'
}

// Get difference indicator
const getDifference = (paramKey) => {
  const val1 = config1.value?.values?.[paramKey]
  const val2 = config2.value?.values?.[paramKey]

  const num1 = getNumericValue(val1)
  const num2 = getNumericValue(val2)

  if (num1 !== null && num2 !== null && num1 !== num2) {
    const diff = num2 - num1
    const sign = diff > 0 ? '↑' : '↓'
    const absVal = Math.abs(diff)
    const formatted = absVal < 1 ? absVal.toFixed(3) : absVal.toFixed(2)
    return `(${sign}${formatted})`
  }

  return null
}

// Auto-select first two configs if available
watch(() => props.configs, (newConfigs) => {
  if (newConfigs.length >= 2) {
    // Find active config first
    const activeConfig = newConfigs.find(c => c.is_active)
    if (activeConfig) {
      selectedConfig1.value = activeConfig.id
      const otherConfig = newConfigs.find(c => c.id !== activeConfig.id)
      if (otherConfig) {
        selectedConfig2.value = otherConfig.id
      }
    } else {
      selectedConfig1.value = newConfigs[0].id
      selectedConfig2.value = newConfigs[1].id
    }
  }
}, { immediate: true })
</script>
