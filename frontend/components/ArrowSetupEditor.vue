<template>
  <div class="space-y-6">
    <!-- Configuration Form -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Arrow Length -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Arrow Length: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ editableConfig.arrow_length || 32 }}"</span>
          <PerformanceTooltip 
            :title="'Arrow Length'"
            :content="'The cut length of the arrow shaft. Affects spine, weight, and performance. Standard hunting arrows: 28-32 inches.'"
          />
        </label>
        <input
          type="range"
          min="20"
          max="36"
          step="0.25"
          :value="editableConfig.arrow_length || 32"
          @input="editableConfig.arrow_length = parseFloat($event.target.value); handleChange()"
          class="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider-touch"
        />
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
          <span>20"</span>
          <span>36"</span>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Recommended: {{ getRecommendedLength() }}"
        </p>
      </div>
      
      <!-- Point Weight -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Point Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ editableConfig.point_weight || 100 }} gr</span>
          <PerformanceTooltip 
            :title="'Point Weight'"
            :content="'Weight of the arrow tip/broadhead. Affects FOC, penetration, and trajectory. Hunting: 100-150gr, Target: 80-120gr.'"
          />
        </label>
        <input
          type="range"
          min="40"
          max="300"
          step="5"
          :value="editableConfig.point_weight || 100"
          @input="editableConfig.point_weight = parseFloat($event.target.value); handleChange()"
          class="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider-touch"
        />
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
          <span>40 gr</span>
          <span>300 gr</span>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Current FOC: {{ calculateFOC() }}%
        </p>
      </div>
      
      <!-- Calculated Spine -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Calculated Spine
          <PerformanceTooltip 
            :title="'Calculated Spine'"
            :content="'The calculated spine requirement for your bow setup. Should match available spine options for optimal performance.'"
          />
        </label>
        <select
          v-model="editableConfig.calculated_spine"
          @change="handleChange"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
        >
          <option value="">Auto-calculate</option>
          <option 
            v-for="spineOption in availableSpines" 
            :key="spineOption.spine"
            :value="spineOption.spine"
          >
            {{ spineOption.spine }} ({{ spineOption.gpi_weight }}gr/in)
          </option>
        </select>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Recommended: {{ getRecommendedSpine() }}
        </p>
      </div>
      
      <!-- Compatibility Score -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Compatibility Score
          <PerformanceTooltip 
            :title="'Compatibility Score'"
            :content="'How well this arrow matches your bow setup. Higher scores indicate better compatibility. 90%+ is excellent.'"
          />
        </label>
        <div class="flex items-center space-x-3">
          <div class="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
            <div 
              class="h-2 rounded-full transition-all duration-300"
              :class="getCompatibilityBarClass(editableConfig.compatibility_score)"
              :style="{ width: `${editableConfig.compatibility_score || 0}%` }"
            ></div>
          </div>
          <span class="text-sm font-medium" :class="getCompatibilityTextClass(editableConfig.compatibility_score)">
            {{ editableConfig.compatibility_score || 0 }}%
          </span>
        </div>
      </div>
    </div>
    
    <!-- Component Weights -->
    <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-weight-hanging mr-2 text-purple-600"></i>
        Component Weights
      </h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Nock Weight -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Nock Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ editableConfig.nock_weight || 10 }} gr</span>
          </label>
          <input
            type="range"
            min="0"
            max="50"
            step="0.5"
            :value="editableConfig.nock_weight || 10"
            @input="editableConfig.nock_weight = parseFloat($event.target.value); handleChange()"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>0 gr</span>
            <span>50 gr</span>
          </div>
        </div>
        
        <!-- Insert Weight -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Insert Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ editableConfig.insert_weight || 0 }} gr</span>
          </label>
          <input
            type="range"
            min="0"
            max="100"
            step="0.5"
            :value="editableConfig.insert_weight || 0"
            @input="editableConfig.insert_weight = parseFloat($event.target.value); handleChange()"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>0 gr</span>
            <span>100 gr</span>
          </div>
        </div>
        
        <!-- Bushing Weight -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Bushing Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ editableConfig.bushing_weight || 0 }} gr</span>
          </label>
          <input
            type="range"
            min="0"
            max="50"
            step="0.5"
            :value="editableConfig.bushing_weight || 0"
            @input="editableConfig.bushing_weight = parseFloat($event.target.value); handleChange()"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>0 gr</span>
            <span>50 gr</span>
          </div>
        </div>
        
        <!-- Fletching Weight -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Fletching Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ editableConfig.fletching_weight || 15 }} gr</span>
          </label>
          <input
            type="range"
            min="0"
            max="50"
            step="0.5"
            :value="editableConfig.fletching_weight || 15"
            @input="editableConfig.fletching_weight = parseFloat($event.target.value); handleChange()"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>0 gr</span>
            <span>50 gr</span>
          </div>
        </div>
      </div>
      
      <!-- Total Weight Display -->
      <div class="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-blue-800 dark:text-blue-200">
            <i class="fas fa-balance-scale mr-2"></i>
            Total Arrow Weight:
          </span>
          <span class="text-lg font-bold text-blue-900 dark:text-blue-100">
            {{ calculateTotalWeight() }} grains
          </span>
        </div>
        <div class="flex items-center justify-between mt-2 text-sm text-blue-700 dark:text-blue-300">
          <span>Shaft Weight ({{ getSelectedSpineGPI() }} GPI × {{ editableConfig.arrow_length }}"):</span>
          <span>{{ calculateShaftWeight() }} gr</span>
        </div>
        <div class="flex items-center justify-between text-sm text-blue-700 dark:text-blue-300">
          <span>Components Total:</span>
          <span>{{ calculateComponentWeight() }} gr</span>
        </div>
      </div>
    </div>
    
    <!-- Notes -->
    <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Notes
      </label>
      <textarea
        v-model="editableConfig.notes"
        @input="handleChange"
        rows="3"
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
        placeholder="Add notes about this arrow setup..."
      ></textarea>
    </div>
    
    <!-- Actions -->
    <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
      <button
        @click="handleCancel"
        type="button"
        class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Cancel
      </button>
      <button
        @click="handlePreview"
        type="button"
        class="px-4 py-2 border border-blue-300 dark:border-blue-600 rounded-md shadow-sm text-sm font-medium text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/40 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <i class="fas fa-eye mr-2"></i>
        Preview Changes
      </button>
      <button
        @click="handleSave"
        :disabled="!hasChanges"
        type="button"
        class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        <i class="fas fa-save mr-2"></i>
        Save Changes
      </button>
    </div>
    
    <!-- Real-time Preview (when enabled) -->
    <div v-if="showPreview" class="border-t border-gray-200 dark:border-gray-700 pt-6">
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-chart-line mr-2 text-green-600"></i>
        Performance Preview
      </h4>
      
      <ArrowPerformancePreview
        :setup-arrow="editableConfig"
        :bow-config="bowConfig"
        :arrow="arrow"
        :original-performance="setupArrow.performance"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import PerformanceTooltip from '~/components/PerformanceTooltip.vue'

const props = defineProps({
  setupArrow: {
    type: Object,
    required: true
  },
  arrow: {
    type: Object,
    required: true
  },
  spineSpecifications: {
    type: Array,
    default: () => []
  },
  bowConfig: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update', 'save', 'cancel'])

// State
const editableConfig = ref({})
const originalConfig = ref({})
const showPreview = ref(false)

// Computed
const availableSpines = computed(() => {
  return props.spineSpecifications.map(spec => ({
    spine: spec.spine,
    gpi_weight: spec.gpi_weight || 8.0,
    outer_diameter: spec.outer_diameter
  })).sort((a, b) => parseFloat(a.spine) - parseFloat(b.spine))
})

const hasChanges = computed(() => {
  // More robust comparison that handles numeric values properly
  const current = editableConfig.value
  const original = originalConfig.value
  
  if (!current || !original) return false
  
  // Check each property individually with proper type conversion
  const keys = ['arrow_length', 'point_weight', 'calculated_spine', 'compatibility_score', 'notes', 'nock_weight', 'insert_weight', 'bushing_weight', 'fletching_weight']
  
  const hasChanged = keys.some(key => {
    const currentVal = current[key]
    const originalVal = original[key]
    
    // Handle numeric comparisons with precision
    if ((typeof currentVal === 'number' || !isNaN(parseFloat(currentVal))) || 
        (typeof originalVal === 'number' || !isNaN(parseFloat(originalVal)))) {
      const currentNum = parseFloat(currentVal) || 0
      const originalNum = parseFloat(originalVal) || 0
      return Math.abs(currentNum - originalNum) > 0.01 // Allow for small floating point differences
    }
    
    // Handle string comparisons
    const currentStr = String(currentVal || '').trim()
    const originalStr = String(originalVal || '').trim()
    return currentStr !== originalStr
  })
  
  // Debug logging in development
  if (process.dev) {
    console.log('hasChanges check:', {
      current: JSON.stringify(current),
      original: JSON.stringify(original),
      hasChanged,
      keys: keys.map(key => ({
        key,
        current: current[key],
        original: original[key],
        changed: current[key] !== original[key]
      }))
    })
  }
  
  return hasChanged
})

// Methods
const initializeConfig = () => {
  const config = {
    arrow_length: parseFloat(props.setupArrow.arrow_length) || 32,
    point_weight: parseFloat(props.setupArrow.point_weight) || 100,
    calculated_spine: String(props.setupArrow.calculated_spine || ''),
    compatibility_score: parseFloat(props.setupArrow.compatibility_score) || 0,
    notes: String(props.setupArrow.notes || ''),
    nock_weight: parseFloat(props.setupArrow.nock_weight) || 10,
    insert_weight: parseFloat(props.setupArrow.insert_weight) || 0,
    bushing_weight: parseFloat(props.setupArrow.bushing_weight) || 0,
    fletching_weight: parseFloat(props.setupArrow.fletching_weight) || 15
  }
  
  // Create completely separate copies to avoid reference sharing
  editableConfig.value = JSON.parse(JSON.stringify(config))
  originalConfig.value = JSON.parse(JSON.stringify(config))
  
  // Debug: Log initial state
  if (process.dev) {
    console.log('Initialized config:', {
      original: JSON.stringify(originalConfig.value),
      editable: JSON.stringify(editableConfig.value),
      areEqual: JSON.stringify(originalConfig.value) === JSON.stringify(editableConfig.value)
    })
  }
}

const handleChange = () => {
  // Emit update for real-time preview
  emit('update', { ...editableConfig.value })
}

const handleSave = () => {
  emit('save', { ...editableConfig.value })
}

const handleCancel = () => {
  emit('cancel')
}

const handlePreview = () => {
  showPreview.value = !showPreview.value
}

const getRecommendedLength = () => {
  // Simple recommendation based on bow type and draw length
  const drawLength = props.bowConfig.draw_length || 28
  if (props.bowConfig.bow_type === 'traditional') {
    return Math.round((drawLength + 3) * 4) / 4 // Add 3" for traditional
  }
  return Math.round((drawLength + 1) * 4) / 4 // Add 1" for compound
}

const getRecommendedSpine = () => {
  // Simplified spine recommendation based on draw weight
  const drawWeight = props.bowConfig.draw_weight || 60
  
  if (drawWeight < 40) return '600-700'
  if (drawWeight < 50) return '500-600'
  if (drawWeight < 60) return '400-500'
  if (drawWeight < 70) return '340-400'
  return '300-340'
}

const getSelectedSpineGPI = () => {
  const selectedSpine = editableConfig.value.calculated_spine
  if (!selectedSpine) return 8.0
  
  const spineSpec = availableSpines.value.find(spec => 
    spec.spine.toString() === selectedSpine.toString()
  )
  
  return spineSpec?.gpi_weight || 8.0
}

const calculateShaftWeight = () => {
  const gpi = getSelectedSpineGPI()
  const length = editableConfig.value.arrow_length || 32
  return Math.round(gpi * length * 10) / 10
}

const calculateComponentWeight = () => {
  const components = 
    (editableConfig.value.point_weight || 0) +
    (editableConfig.value.nock_weight || 0) +
    (editableConfig.value.insert_weight || 0) +
    (editableConfig.value.bushing_weight || 0) +
    (editableConfig.value.fletching_weight || 0)
    
  return Math.round(components * 10) / 10
}

const calculateTotalWeight = () => {
  const shaftWeight = calculateShaftWeight()
  const componentWeight = calculateComponentWeight()
  return Math.round((shaftWeight + componentWeight) * 10) / 10
}

const calculateFOC = () => {
  const totalWeight = calculateTotalWeight()
  const arrowLength = editableConfig.value.arrow_length || 32
  const pointWeight = editableConfig.value.point_weight || 0
  const insertWeight = editableConfig.value.insert_weight || 0
  
  if (totalWeight === 0) return 0
  
  // Simplified FOC calculation
  const balancePoint = arrowLength / 2 // Assuming balance point at center
  const frontWeight = pointWeight + insertWeight
  const foc = ((balancePoint - (arrowLength / 2)) / arrowLength) * 100 + 
              (frontWeight / totalWeight) * 10
  
  return Math.round(foc * 10) / 10
}

const getCompatibilityBarClass = (score) => {
  if (score >= 90) return 'bg-green-600'
  if (score >= 70) return 'bg-yellow-600'
  return 'bg-red-600'
}

const getCompatibilityTextClass = (score) => {
  if (score >= 90) return 'text-green-600 dark:text-green-400'
  if (score >= 70) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

// Lifecycle
onMounted(() => {
  initializeConfig()
})

// Watch for prop changes - only reinitialize if we're not in edit mode
watch(() => props.setupArrow, (newValue, oldValue) => {
  // Only reinitialize if this is truly a new arrow (different ID) 
  // or if we don't have unsaved changes
  if (!editableConfig.value || 
      newValue.id !== oldValue?.id ||
      !hasChanges.value) {
    initializeConfig()
  }
}, { deep: true, immediate: false })
</script>

<style scoped>
/* Slider Styling for Arrow Setup Editor */
.slider-touch {
  -webkit-appearance: none;
  appearance: none;
  background: linear-gradient(to right, #3b82f6 0%, #3b82f6 50%, #d1d5db 50%, #d1d5db 100%);
  outline: none;
  opacity: 0.7;
  transition: opacity 0.2s;
  border-radius: 6px;
}

.slider-touch:hover {
  opacity: 1;
}

.slider-touch::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider-touch::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Dark mode slider styling */
.dark .slider-touch {
  background: linear-gradient(to right, #8b5cf6 0%, #8b5cf6 50%, #4b5563 50%, #4b5563 100%);
}

.dark .slider-touch::-webkit-slider-thumb {
  background: #8b5cf6;
}

.dark .slider-touch::-moz-range-thumb {
  background: #8b5cf6;
}

/* Component weight sliders - smaller styling */
input[type="range"].h-2 {
  -webkit-appearance: none;
  appearance: none;
  outline: none;
  opacity: 0.7;
  transition: opacity 0.2s;
  border-radius: 4px;
}

input[type="range"].h-2:hover {
  opacity: 1;
}

input[type="range"].h-2::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 1px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

input[type="range"].h-2::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 1px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.dark input[type="range"].h-2::-webkit-slider-thumb {
  background: #8b5cf6;
}

.dark input[type="range"].h-2::-moz-range-thumb {
  background: #8b5cf6;
}
</style>