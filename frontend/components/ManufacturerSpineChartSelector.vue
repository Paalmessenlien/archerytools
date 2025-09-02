<template>
  <div class="manufacturer-spine-chart-selector">
    <!-- Manufacturer Selection -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        <i class="fas fa-industry mr-2"></i>
        Spine Chart Manufacturer (Optional)
      </label>
      <md-filled-select 
        :value="selectedManufacturer" 
        @change="handleManufacturerChange($event.target.value)"
        label="Choose manufacturer spine chart"
        class="w-full"
      >
        <md-select-option value="">
          <div slot="headline">Generic Charts (Default)</div>
          <div slot="supporting-text">Use standard spine calculations (no chart override)</div>
        </md-select-option>
        <md-select-option 
          v-for="manufacturer in availableManufacturers" 
          :key="manufacturer.manufacturer" 
          :value="manufacturer.manufacturer"
        >
          <div slot="headline">{{ manufacturer.manufacturer }}</div>
          <div slot="supporting-text">
            {{ manufacturer.chart_count }} charts • {{ manufacturer.bow_types.join(', ') }}
          </div>
        </md-select-option>
      </md-filled-select>
    </div>

    <!-- Chart Selection (shown when manufacturer is selected) -->
    <div v-if="selectedManufacturer && availableCharts.length > 0" class="mb-4">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        <i class="fas fa-chart-line mr-2"></i>
        Specific Chart Model
      </label>
      <md-filled-select 
        :value="selectedChartId" 
        @change="handleChartChange($event.target.value)"
        label="Choose specific chart"
        class="w-full"
      >
        <md-select-option value="">
          <div slot="headline">Auto-select best match</div>
          <div slot="supporting-text">Choose based on bow type</div>
        </md-select-option>
        <md-select-option 
          v-for="chart in availableCharts" 
          :key="chart.id" 
          :value="chart.id.toString()"
        >
          <div slot="headline">{{ chart.model }} ({{ formatBowType(chart.bow_type) }})</div>
          <div slot="supporting-text">
            {{ chart.spine_system }} • {{ chart.provenance?.substring(0, 50) }}...
          </div>
        </md-select-option>
      </md-filled-select>
    </div>

    <!-- Chart Information Display -->
    <div v-if="selectedChart" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
      <div class="flex items-start justify-between mb-3">
        <div>
          <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-200">
            {{ selectedChart.manufacturer }} {{ selectedChart.model }}
          </h4>
          <p class="text-xs text-blue-700 dark:text-blue-300 mt-1">
            {{ formatBowType(selectedChart.bow_type) }} • {{ selectedChart.spine_system }}
          </p>
        </div>
        <CustomButton
          @click="showChartDetails = !showChartDetails"
          variant="text"
          size="small"
          class="text-blue-600 hover:bg-blue-100 dark:text-blue-400 dark:hover:bg-blue-900"
        >
          <i class="fas transition-transform" :class="showChartDetails ? 'fa-chevron-up' : 'fa-info-circle'"></i>
          {{ showChartDetails ? 'Hide' : 'Info' }}
        </CustomButton>
      </div>

      <!-- Chart Details (expandable) -->
      <div v-if="showChartDetails" class="space-y-3">
        <div v-if="selectedChart.chart_notes" class="text-xs text-blue-800 dark:text-blue-200">
          <strong>Notes:</strong> {{ selectedChart.chart_notes }}
        </div>
        
        <div v-if="selectedChart.provenance" class="text-xs text-blue-600 dark:text-blue-400">
          <strong>Source:</strong> {{ selectedChart.provenance }}
        </div>

        <!-- Spine Grid Preview -->
        <div v-if="selectedChart.spine_grid && selectedChart.spine_grid.length > 0" class="mt-3">
          <h5 class="text-xs font-medium text-blue-900 dark:text-blue-200 mb-2">Spine Chart Preview:</h5>
          <div class="overflow-x-auto">
            <table class="min-w-full text-xs">
              <thead>
                <tr class="border-b border-blue-300 dark:border-blue-700">
                  <th class="text-left py-1 px-2 text-blue-800 dark:text-blue-200">Draw Weight</th>
                  <th class="text-left py-1 px-2 text-blue-800 dark:text-blue-200">Arrow Length</th>
                  <th class="text-left py-1 px-2 text-blue-800 dark:text-blue-200">Recommended Spine</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="(entry, index) in selectedChart.spine_grid.slice(0, 5)" 
                  :key="index"
                  class="border-b border-blue-200 dark:border-blue-800"
                >
                  <td class="py-1 px-2 text-blue-700 dark:text-blue-300">
                    {{ entry.draw_weight_range_lbs }} lbs
                  </td>
                  <td class="py-1 px-2 text-blue-700 dark:text-blue-300">
                    {{ entry.arrow_length_in }}"
                  </td>
                  <td class="py-1 px-2 font-medium text-blue-900 dark:text-blue-100">
                    {{ entry.spine }}
                  </td>
                </tr>
                <tr v-if="selectedChart.spine_grid.length > 5">
                  <td colspan="3" class="py-1 px-2 text-xs text-blue-600 dark:text-blue-400 italic">
                    ... and {{ selectedChart.spine_grid.length - 5 }} more entries
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Calculation Method Selection -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        <i class="fas fa-calculator mr-2"></i>
        Calculation Method
      </label>
      <md-filled-select 
        :value="calculationMethod" 
        @change="updateCalculationMethod($event.target.value)"
        label="Choose calculation method"
        class="w-full"
      >
        <md-select-option value="universal">
          <div slot="headline">Universal Formula (Default)</div>
          <div slot="supporting-text">Generic spine charts - works for all manufacturers</div>
        </md-select-option>
        <md-select-option value="german_industry">
          <div slot="headline">German Industry Standard</div>
          <div slot="supporting-text">Specialized formulas for recurve/traditional bows</div>
        </md-select-option>
      </md-filled-select>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
        Universal formula provides broader compatibility; German standard offers specialized accuracy for European equipment
      </p>
    </div>

    <!-- Calculation Mode Toggle -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        <i class="fas fa-cog mr-2"></i>
        Calculation Mode
      </label>
      <div class="flex items-center space-x-4">
        <label class="flex items-center">
          <input
            type="radio"
            :checked="calculationMode === 'simple'"
            @change="updateCalculationMode('simple')"
            class="mr-2 text-blue-600"
          />
          <span class="text-sm">Simple</span>
        </label>
        <label class="flex items-center">
          <input
            type="radio"
            :checked="calculationMode === 'professional'"
            @change="updateCalculationMode('professional')"
            class="mr-2 text-blue-600"
          />
          <span class="text-sm">Professional</span>
        </label>
      </div>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
        Professional mode includes all adjustment factors (bow speed, release type, etc.)
      </p>
    </div>

    <!-- Professional Mode Additional Settings -->
    <div v-if="calculationMode === 'professional'" class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
      <h4 class="text-sm font-semibold text-purple-900 dark:text-purple-200 mb-3">
        <i class="fas fa-sliders-h mr-2"></i>
        Professional Adjustments
      </h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Bow Speed -->
        <div>
          <label class="block text-xs font-medium text-purple-700 dark:text-purple-300 mb-1">
            Bow Speed (FPS) - Optional
          </label>
          <input
            type="number"
            :value="bowSpeed"
            @input="updateBowSpeed($event.target.value)"
            placeholder="e.g., 320"
            min="200"
            max="400"
            step="5"
            class="w-full px-2 py-1 text-sm border border-purple-300 dark:border-purple-600 rounded focus:ring-purple-500 focus:border-purple-500 dark:bg-gray-700 dark:text-gray-100"
          />
          <p class="text-xs text-purple-600 dark:text-purple-400 mt-1">
            IBO/ATA speed rating
          </p>
        </div>

        <!-- Release Type -->
        <div>
          <label class="block text-xs font-medium text-purple-700 dark:text-purple-300 mb-1">
            Release Type
          </label>
          <md-filled-select 
            :value="releaseType" 
            @change="updateReleaseType($event.target.value)"
            label="Release method"
            class="w-full"
          >
            <md-select-option value="mechanical">
              <div slot="headline">Mechanical Release</div>
            </md-select-option>
            <md-select-option value="finger_release">
              <div slot="headline">Finger Release</div>
            </md-select-option>
          </md-filled-select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-4">
      <div class="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent dark:border-purple-400"></div>
      <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading manufacturers...</span>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
      <p class="text-sm text-red-700 dark:text-red-300">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Manufacturer {
  manufacturer: string
  chart_count: number
  bow_types: string[]
}

interface SpineChart {
  id: number
  manufacturer: string
  model: string
  bow_type: string
  grid_definition: any
  spine_grid: any[]
  provenance: string
  spine_system: string
  chart_notes: string
  created_at: string
}

// Props
interface Props {
  bowType?: string
  materialPreference?: string
  onSelectionChange?: (selection: any) => void
}

const props = withDefaults(defineProps<Props>(), {
  bowType: 'compound',
  materialPreference: ''
})

// Emits
const emit = defineEmits<{
  selectionChange: [selection: {
    manufacturer: string | null
    chartId: string | null
    chart: SpineChart | null
    calculationMode: string
    calculationMethod: string
    professionalSettings: any
  }]
}>()

// API
const api = useApi()

// Reactive state
const loading = ref(false)
const error = ref<string | null>(null)
const showChartDetails = ref(false)

// Selection state
const selectedManufacturer = ref<string>('')
const selectedChartId = ref<string>('')
const calculationMode = ref<string>('simple')
const calculationMethod = ref<string>('universal')

// Professional mode settings
const bowSpeed = ref<number | null>(null)
const releaseType = ref<string>('mechanical')

// Data
const availableManufacturers = ref<Manufacturer[]>([])
const availableCharts = ref<SpineChart[]>([])

// Computed
const selectedChart = computed(() => {
  if (!selectedChartId.value) return null
  return availableCharts.value.find(chart => chart.id.toString() === selectedChartId.value) || null
})

// Methods
const loadManufacturers = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.get('/calculator/manufacturers')
    availableManufacturers.value = response.manufacturers || []
    
    // After loading manufacturers, check for system default charts
    await loadSystemDefaults()
  } catch (err) {
    error.value = 'Failed to load manufacturers. Using generic calculations.'
    console.error('Error loading manufacturers:', err)
  } finally {
    loading.value = false
  }
}

const loadSystemDefaults = async () => {
  try {
    // Build query with material preference if available
    let query = `/calculator/system-default?bow_type=${props.bowType}`
    if (props.materialPreference) {
      query += `&material=${props.materialPreference}`
    }
    
    const response = await api.get(query)
    
    if (response.default_chart) {
      const defaultChart = response.default_chart
      console.log(`🎯 Found system default chart: ${defaultChart.manufacturer} ${defaultChart.model}`)
      
      // Auto-select the manufacturer and chart
      selectedManufacturer.value = defaultChart.manufacturer
      selectedChartId.value = defaultChart.id.toString()
      
      // Load charts for the manufacturer
      await loadManufacturerCharts(defaultChart.manufacturer)
      
      emitSelectionChange()
    }
  } catch (err) {
    // System defaults are optional - don't show error if not available
    console.log('No system default chart configured for', props.bowType, props.materialPreference ? `with ${props.materialPreference} material` : '')
  }
}

const loadManufacturerCharts = async (manufacturer: string) => {
  if (!manufacturer) {
    availableCharts.value = []
    return
  }

  loading.value = true
  error.value = null
  
  try {
    const response = await api.get(`/calculator/manufacturers/${encodeURIComponent(manufacturer)}/charts`)
    availableCharts.value = response.charts || []
  } catch (err) {
    error.value = `Failed to load charts for ${manufacturer}`
    console.error(`Error loading charts for ${manufacturer}:`, err)
    availableCharts.value = []
  } finally {
    loading.value = false
  }
}

const handleManufacturerChange = async (manufacturer: string) => {
  selectedManufacturer.value = manufacturer
  selectedChartId.value = ''
  
  if (manufacturer) {
    await loadManufacturerCharts(manufacturer)
  } else {
    availableCharts.value = []
  }
  
  emitSelectionChange()
}

const handleChartChange = (chartId: string) => {
  selectedChartId.value = chartId
  emitSelectionChange()
}

const updateCalculationMode = (mode: string) => {
  calculationMode.value = mode
  emitSelectionChange()
}

const updateCalculationMethod = (method: string) => {
  calculationMethod.value = method
  emitSelectionChange()
}

const updateBowSpeed = (speed: string | number) => {
  const numSpeed = typeof speed === 'string' ? parseInt(speed) || null : speed
  bowSpeed.value = numSpeed
  emitSelectionChange()
}

const updateReleaseType = (type: string) => {
  releaseType.value = type
  emitSelectionChange()
}

const emitSelectionChange = () => {
  const selection = {
    manufacturer: selectedManufacturer.value || null,
    chartId: selectedChartId.value || null,
    chart: selectedChart.value,
    calculationMode: calculationMode.value,
    calculationMethod: calculationMethod.value,
    professionalSettings: {
      bowSpeed: bowSpeed.value,
      releaseType: releaseType.value
    }
  }
  
  emit('selectionChange', selection)
}

// Utility functions
const formatBowType = (bowType: string): string => {
  const typeMap: Record<string, string> = {
    'compound': 'Compound',
    'recurve': 'Recurve', 
    'longbow': 'Longbow',
    'traditional': 'Traditional'
  }
  return typeMap[bowType] || bowType
}

// Lifecycle
onMounted(() => {
  loadManufacturers()
})

// Watch for bow type changes to filter relevant charts and reload system defaults
watch(() => props.bowType, async () => {
  if (selectedManufacturer.value) {
    loadManufacturerCharts(selectedManufacturer.value)
  }
  
  // Check for system defaults for new bow type
  await loadSystemDefaults()
})

// Watch for material preference changes to reload appropriate defaults
watch(() => props.materialPreference, async () => {
  // Reload system defaults when material preference changes
  await loadSystemDefaults()
})
</script>

<style scoped>
.manufacturer-spine-chart-selector {
  @apply space-y-4;
}

/* Custom radio button styling */
input[type="radio"] {
  @apply w-4 h-4;
}

input[type="radio"]:checked {
  @apply bg-blue-600 border-blue-600;
}

.dark input[type="radio"]:checked {
  @apply bg-purple-600 border-purple-600;
}

/* Table styling */
table {
  @apply text-xs;
}

table th {
  @apply font-medium;
}

table td {
  @apply text-sm;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .grid-cols-1.md\\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}
</style>