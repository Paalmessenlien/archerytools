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
          class="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider-touch mobile-slider-safe"
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
          class="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider-touch mobile-slider-safe"
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
          @change="handleSpineChange"
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
            <i v-if="isCalculatingCompatibility" class="fas fa-spinner fa-spin mr-1"></i>
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
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
      <!-- Reset to Recommended Button -->
      <button
        @click="resetToRecommended"
        type="button"
        class="inline-flex items-center px-4 py-2 border border-orange-300 dark:border-orange-600 rounded-md shadow-sm text-sm font-medium text-orange-700 dark:text-orange-300 bg-orange-50 dark:bg-orange-900/20 hover:bg-orange-100 dark:hover:bg-orange-900/30 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors"
      >
        <i class="fas fa-magic mr-2"></i>
        Reset to Recommended
      </button>
      
      <!-- Cancel and Save Actions -->
      <div class="flex space-x-3">
        <button
          @click="handleCancel"
          type="button"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Cancel
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
    </div>
    
    <!-- Real-time Performance Preview -->
    <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-chart-line mr-2 text-green-600"></i>
        Live Performance Preview
        <span class="ml-2 px-2 py-1 text-xs bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full">
          Real-time
        </span>
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
import { useApi } from '~/composables/useApi'
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

// Composables
const api = useApi()

// State
const editableConfig = ref({})
const originalConfig = ref({})
const showPreview = ref(true) // Always show preview for real-time updates

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

// Real-time compatibility score calculation
const isCalculatingCompatibility = ref(false)

const calculateCompatibilityScore = async () => {
  if (!props.arrow?.id || isCalculatingCompatibility.value) return
  
  isCalculatingCompatibility.value = true
  
  try {
    const response = await api.post('/calculate-compatibility-score', {
      arrow_id: props.arrow.id,
      bow_config: {
        draw_weight: props.bowConfig.draw_weight,
        draw_length: props.bowConfig.draw_length,
        bow_type: props.bowConfig.bow_type
      },
      arrow_config: {
        arrow_length: editableConfig.value.arrow_length,
        point_weight: editableConfig.value.point_weight,
        calculated_spine: editableConfig.value.calculated_spine
      }
    })
    
    if (response.compatibility_score !== undefined) {
      // Update compatibility score in real-time
      editableConfig.value.compatibility_score = response.compatibility_score
    }
  } catch (error) {
    console.error('Error calculating compatibility score:', error)
  } finally {
    isCalculatingCompatibility.value = false
  }
}

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
  
  // Calculate compatibility score when spine, length, or point weight changes
  calculateCompatibilityScore()
}

const handleSpineChange = (event) => {
  // Update the spine value
  editableConfig.value.calculated_spine = event.target.value
  
  // Trigger change handling
  handleChange()
}

const handleSave = () => {
  emit('save', { ...editableConfig.value })
}

const handleCancel = () => {
  emit('cancel')
}

const resetToRecommended = async () => {
  try {
    console.log('Starting Reset to Recommended optimization...')
    const currentScore = editableConfig.value.compatibility_score || 0
    
    // Generate test configurations to find the best compatibility score
    const testConfigurations = []
    
    // Get base recommendations as starting points
    const recommendedLength = getRecommendedLength()
    const recommendedSpine = getRecommendedSpineValue()
    const baseLengths = [recommendedLength - 0.5, recommendedLength, recommendedLength + 0.5].filter(l => l >= 20 && l <= 36)
    const basePointWeights = [85, 100, 115, 125, 140] // Common point weights
    
    // Generate test combinations
    baseLengths.forEach(length => {
      basePointWeights.forEach(pointWeight => {
        availableSpines.value.forEach(spine => {
          testConfigurations.push({
            arrow_length: length,
            point_weight: pointWeight,
            calculated_spine: String(spine.spine),
            nock_weight: 10,
            insert_weight: 0,
            bushing_weight: 0,
            fletching_weight: 15
          })
        })
      })
    })
    
    console.log(`Testing ${testConfigurations.length} configurations for optimal compatibility...`)
    
    let bestConfig = null
    let bestScore = currentScore
    let testedCount = 0
    
    // Test configurations in batches to avoid overwhelming the API
    const batchSize = 10
    for (let i = 0; i < testConfigurations.length; i += batchSize) {
      const batch = testConfigurations.slice(i, i + batchSize)
      
      // Test each configuration in the batch
      for (const testConfig of batch) {
        try {
          const response = await api.post('/calculate-compatibility-score', {
            arrow_id: props.arrow.id,
            bow_config: {
              draw_weight: props.bowConfig.draw_weight,
              draw_length: props.bowConfig.draw_length,
              bow_type: props.bowConfig.bow_type
            },
            arrow_config: testConfig
          })
          
          testedCount++
          
          if (response.compatibility_score > bestScore) {
            bestScore = response.compatibility_score
            bestConfig = { ...testConfig }
            console.log(`New best configuration found: ${bestScore}% (Length: ${testConfig.arrow_length}", Point: ${testConfig.point_weight}gr, Spine: ${testConfig.calculated_spine})`)
          }
        } catch (error) {
          console.warn('Error testing configuration:', error)
        }
      }
      
      // Add small delay between batches to be respectful to the API
      if (i + batchSize < testConfigurations.length) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }
    
    console.log(`Optimization complete: Tested ${testedCount} configurations`)
    
    if (bestConfig && bestScore > currentScore) {
      const improvement = (bestScore - currentScore).toFixed(1)
      console.log(`Found better configuration: ${improvement}% improvement (${currentScore}% → ${bestScore}%)`)
      
      // Apply the optimized configuration
      editableConfig.value = {
        ...editableConfig.value,
        ...bestConfig,
        compatibility_score: bestScore,
        notes: `Optimized for maximum compatibility: ${bestScore}% (+${improvement}% improvement) - Length: ${bestConfig.arrow_length}", Point: ${bestConfig.point_weight}gr, Spine: ${bestConfig.calculated_spine} - ${new Date().toLocaleDateString()}`
      }
      
      // Trigger change event for real-time updates
      handleChange()
    } else {
      console.log(`No improvement found. Current score ${currentScore}% is already optimal.`)
      
      // Still apply basic recommended values but inform user
      const recommendedPointWeight = getRecommendedPointWeight(recommendedLength)
      
      editableConfig.value = {
        ...editableConfig.value,
        arrow_length: recommendedLength,
        calculated_spine: recommendedSpine,
        point_weight: recommendedPointWeight,
        nock_weight: 10,
        insert_weight: 0,
        bushing_weight: 0,
        fletching_weight: 15,
        notes: `Applied standard recommendations (current ${currentScore}% compatibility already near-optimal) - ${props.bowConfig.bow_type} bow (${props.bowConfig.draw_weight}lbs @ ${props.bowConfig.draw_length}") - ${new Date().toLocaleDateString()}`
      }
      
      handleChange()
    }
  } catch (error) {
    console.error('Error in Reset to Recommended optimization:', error)
    
    // Fallback to simplified calculation if optimization fails
    const recommendedLength = getRecommendedLength()
    const recommendedSpine = getRecommendedSpineValue()
    const recommendedPointWeight = getRecommendedPointWeight(recommendedLength)
    
    editableConfig.value = {
      ...editableConfig.value,
      arrow_length: recommendedLength,
      calculated_spine: recommendedSpine,
      point_weight: recommendedPointWeight,
      nock_weight: 10,
      insert_weight: 0,
      bushing_weight: 0,
      fletching_weight: 15,
      notes: `Applied fallback recommendations due to optimization error - ${props.bowConfig.bow_type} bow (${props.bowConfig.draw_weight}lbs @ ${props.bowConfig.draw_length}") - ${new Date().toLocaleDateString()}`
    }
    
    handleChange()
  }
}

// Preview is now always shown in real-time, no toggle needed

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

const getRecommendedSpineValue = () => {
  // Get the actual spine value from available options based on draw weight
  const drawWeight = props.bowConfig.draw_weight || 60
  
  // Find the best spine match from available options
  let targetSpine = 500 // Default
  
  if (drawWeight < 40) targetSpine = 600
  else if (drawWeight < 50) targetSpine = 500  
  else if (drawWeight < 60) targetSpine = 400
  else if (drawWeight < 70) targetSpine = 340
  else targetSpine = 300
  
  // Find the closest available spine option
  const availableSpine = availableSpines.value.find(spine => 
    spine.spine === targetSpine
  )
  
  return availableSpine ? String(availableSpine.spine) : String(targetSpine)
}

const getRecommendedPointWeight = (arrowLength = 32) => {
  // Calculate point weight for optimal FOC (12-15%)
  const drawWeight = props.bowConfig.draw_weight || 60
  const bowType = props.bowConfig.bow_type || 'compound'
  
  // Base point weight recommendations
  let basePointWeight = 100
  
  if (bowType === 'traditional') {
    // Traditional bows benefit from heavier points
    basePointWeight = Math.max(125, drawWeight * 1.8)
  } else {
    // Compound bow recommendations
    if (drawWeight < 40) basePointWeight = 85
    else if (drawWeight < 50) basePointWeight = 100
    else if (drawWeight < 60) basePointWeight = 115
    else if (drawWeight < 70) basePointWeight = 125
    else basePointWeight = 140
  }
  
  // Adjust for arrow length (longer arrows need slightly heavier points for good FOC)
  const lengthAdjustment = (arrowLength - 30) * 2
  basePointWeight += lengthAdjustment
  
  // Round to nearest 5 grains and ensure within limits
  return Math.max(40, Math.min(300, Math.round(basePointWeight / 5) * 5))
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