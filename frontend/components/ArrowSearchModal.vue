<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-6xl max-h-[90vh] overflow-y-auto">
      <!-- Modal Header -->
      <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-search mr-2 text-blue-600"></i>
              Search & Match Arrows
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Find arrows compatible with: {{ bowSetup?.name }} ({{ bowSetup?.bow_config?.bow_type }}, {{ bowSetup?.bow_config?.draw_weight }}lbs)
            </p>
          </div>
          <CustomButton
            @click="closeModal"
            variant="outlined"
            size="small"
            class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700"
          >
            <i class="fas fa-times"></i>
          </CustomButton>
        </div>
      </div>

      <!-- Search Controls -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <!-- Search Bar -->
        <div class="mb-4">
          <md-outlined-text-field 
            class="w-full"
            :value="filters.search"
            @input="handleSearchInput($event.target.value)"
            label="Search arrows... (3+ letters for typeahead)"
            placeholder="Type arrow name, manufacturer, model..."
          >
            <i class="fas fa-search" slot="leading-icon" style="color: #6b7280;"></i>
            <i v-if="filters.search && filters.search.length >= 3" class="fas fa-spinner fa-spin" slot="trailing-icon" style="color: #6b7280;" v-show="loading"></i>
          </md-outlined-text-field>
        </div>
        
        <!-- Filters -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <md-filled-select :value="filters.manufacturer" @change="handleFilterChange('manufacturer', $event.target.value)" label="Manufacturer">
            <md-select-option value="">
              <div slot="headline">All Manufacturers</div>
            </md-select-option>
            <md-select-option v-for="mfr in manufacturers" :key="mfr.manufacturer" :value="mfr.manufacturer">
              <div slot="headline">{{ mfr.manufacturer }} ({{ mfr.arrow_count }})</div>
            </md-select-option>
          </md-filled-select>
          
          <md-filled-select :value="filters.material" @change="handleFilterChange('material', $event.target.value)" label="Material">
            <md-select-option value="">
              <div slot="headline">All Materials</div>
            </md-select-option>
            <md-select-option value="Carbon">
              <div slot="headline">Carbon</div>
            </md-select-option>
            <md-select-option value="Carbon / Aluminum">
              <div slot="headline">Carbon / Aluminum</div>
            </md-select-option>
            <md-select-option value="Aluminum">
              <div slot="headline">Aluminum</div>
            </md-select-option>
            <md-select-option value="Wood">
              <div slot="headline">Wood</div>
            </md-select-option>
          </md-filled-select>

          <md-filled-select :value="sortBy" @change="sortBy = $event.target.value" label="Sort By">
            <md-select-option value="compatibility">
              <div slot="headline">Best Match</div>
            </md-select-option>
            <md-select-option value="manufacturer">
              <div slot="headline">Manufacturer</div>
            </md-select-option>
            <md-select-option value="spine_match">
              <div slot="headline">Spine Match</div>
            </md-select-option>
          </md-filled-select>
        </div>

        <!-- Arrow Adjustment Controls -->
        <div class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
            <i class="fas fa-sliders-h mr-2 text-blue-600"></i>
            Arrow Adjustments (affects spine matching)
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Arrow Length -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Arrow Length: <span class="font-semibold text-blue-600">{{ adjustments.arrow_length }}"</span>
              </label>
              <md-slider
                min="24"
                max="34"
                step="0.5"
                :value="adjustments.arrow_length"
                @input="updateAdjustment('arrow_length', parseFloat($event.target.value))"
                labeled
                ticks
                class="w-full"
              ></md-slider>
            </div>
            
            <!-- Point Weight -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Point Weight: <span class="font-semibold text-blue-600">{{ adjustments.point_weight }} gr</span>
              </label>
              <md-slider
                min="75"
                max="200"
                step="25"
                :value="adjustments.point_weight"
                @input="updateAdjustment('point_weight', parseInt($event.target.value))"
                labeled
                ticks
                class="w-full"
              ></md-slider>
            </div>
          </div>
          <div class="mt-3 text-sm text-gray-600 dark:text-gray-400">
            <i class="fas fa-info-circle mr-1"></i>
            Recommended spine: <span class="font-medium text-blue-600">{{ calculatedSpine || 'Calculating...' }}</span>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-6">
        <div class="space-y-4">
          <div v-for="i in 3" :key="i" class="animate-pulse">
            <div class="border border-gray-200 rounded-lg p-4 space-y-3">
              <div class="flex justify-between items-start">
                <div class="space-y-2">
                  <div class="h-5 bg-gray-200 rounded w-48"></div>
                  <div class="h-4 bg-gray-200 rounded w-32"></div>
                </div>
                <div class="h-8 bg-gray-200 rounded w-20"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Arrow Results -->
      <div v-else-if="searchResults.length > 0" class="p-6">
        <div class="mb-4 text-sm text-gray-600 dark:text-gray-400">
          Showing {{ searchResults.length }} arrows
          <span v-if="calculatedSpine" class="ml-2 font-medium text-blue-600">
            (Target Spine: {{ calculatedSpine }})
          </span>
        </div>
        
        <div class="space-y-4 max-h-96 overflow-y-auto">
          <div 
            v-for="arrow in sortedResults" 
            :key="arrow.id"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">
                  {{ arrow.manufacturer }} {{ arrow.model_name }}
                </h4>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Spine: {{ getSpineDisplay(arrow) }} | 
                  Diameter: {{ getDiameterRange(arrow) }}" |
                  Weight: {{ getGPIRange(arrow) }} GPI
                </p>
                
                <!-- Compatibility Score -->
                <div class="flex items-center space-x-2 mb-2">
                  <span class="text-xs px-2 py-1 rounded-full" 
                        :class="getCompatibilityClass(arrow.compatibility_score)">
                    {{ arrow.compatibility_score || 0 }}% Match
                  </span>
                  <span v-if="arrow.material" class="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                    {{ arrow.material }}
                  </span>
                </div>
                
                <p v-if="arrow.description" class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                  {{ arrow.description }}
                </p>
              </div>
              
              <div class="ml-4 flex flex-col space-y-2">
                <CustomButton
                  @click="addArrowToSetup(arrow)"
                  variant="filled"
                  size="small"
                  class="bg-green-600 text-white hover:bg-green-700"
                >
                  <i class="fas fa-plus mr-1"></i>
                  Add to Setup
                </CustomButton>
                <CustomButton
                  @click="viewArrowDetails(arrow)"
                  variant="outlined"
                  size="small"
                  class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400"
                >
                  <i class="fas fa-info-circle mr-1"></i>
                  Details
                </CustomButton>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-else-if="searchPerformed && !loading" class="p-12 text-center">
        <div class="text-gray-400 mb-4">
          <i class="fas fa-search-minus text-6xl"></i>
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Arrows Found</h3>
        <p class="text-gray-600 dark:text-gray-400">No arrows match your search criteria.</p>
      </div>

      <!-- Initial State -->
      <div v-else class="p-12 text-center">
        <div class="text-gray-400 mb-4">
          <i class="fas fa-search text-6xl"></i>
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Search for Arrows</h3>
        <p class="text-gray-600 dark:text-gray-400">Use the search bar above to find arrows compatible with your bow setup.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  bowSetup: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'add-arrow'])

// API
const api = useApi()

// Reactive state
const loading = ref(false)
const searchPerformed = ref(false)
const searchResults = ref([])
const manufacturers = ref([])
const sortBy = ref('compatibility')

// Filters
const filters = ref({
  search: '',
  manufacturer: '',
  material: ''
})

// Arrow adjustments
const adjustments = ref({
  arrow_length: 29.0,
  point_weight: 125
})

// Computed
const calculatedSpine = computed(() => {
  if (!props.bowSetup?.bow_config) return null
  
  // Simple spine calculation based on draw weight, arrow length, and point weight
  const drawWeight = props.bowSetup.bow_config.draw_weight || 50
  const arrowLength = adjustments.value.arrow_length
  const pointWeight = adjustments.value.point_weight
  
  // Basic spine formula (this should match the backend calculation)
  let baseSpine = drawWeight * 12.5 // Base spine calculation
  
  // Adjust for arrow length (longer = weaker/higher spine number)
  const lengthAdjustment = (arrowLength - 28) * 25
  baseSpine += lengthAdjustment
  
  // Adjust for point weight (heavier = weaker/higher spine number)  
  const pointAdjustment = (pointWeight - 125) * 0.5
  baseSpine += pointAdjustment
  
  return Math.round(baseSpine)
})

const sortedResults = computed(() => {
  if (!searchResults.value.length) return []
  
  let sorted = [...searchResults.value]
  
  switch (sortBy.value) {
    case 'compatibility':
      // Calculate compatibility score for each arrow
      sorted = sorted.map(arrow => ({
        ...arrow,
        compatibility_score: calculateCompatibilityScore(arrow)
      }))
      return sorted.sort((a, b) => (b.compatibility_score || 0) - (a.compatibility_score || 0))
    
    case 'manufacturer':
      return sorted.sort((a, b) => a.manufacturer.localeCompare(b.manufacturer))
    
    case 'spine_match':
      return sorted.sort((a, b) => {
        const aSpineDiff = Math.abs((a.min_spine + a.max_spine) / 2 - calculatedSpine.value)
        const bSpineDiff = Math.abs((b.min_spine + b.max_spine) / 2 - calculatedSpine.value)
        return aSpineDiff - bSpineDiff
      })
    
    default:
      return sorted
  }
})

// Methods
const searchArrows = async () => {
  loading.value = true
  searchPerformed.value = true
  
  try {
    const searchFilters = {
      limit: 50
    }
    
    // Add non-empty filters
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        searchFilters[key] = value
      }
    })
    
    const result = await api.getArrows(searchFilters)
    searchResults.value = result.arrows || []
    
  } catch (err) {
    console.error('Error searching arrows:', err)
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

const loadManufacturers = async () => {
  try {
    manufacturers.value = await api.getManufacturers()
  } catch (err) {
    console.error('Error loading manufacturers:', err)
  }
}

const calculateCompatibilityScore = (arrow) => {
  if (!calculatedSpine.value || !arrow.min_spine || !arrow.max_spine) return 0
  
  const targetSpine = calculatedSpine.value
  const arrowMinSpine = arrow.min_spine
  const arrowMaxSpine = arrow.max_spine
  
  // Check if target spine is within arrow's range
  if (targetSpine >= arrowMinSpine && targetSpine <= arrowMaxSpine) {
    return 100 // Perfect match
  }
  
  // Calculate how far off we are
  const arrowMidSpine = (arrowMinSpine + arrowMaxSpine) / 2
  const spineDifference = Math.abs(targetSpine - arrowMidSpine)
  const spineRange = arrowMaxSpine - arrowMinSpine
  
  // Score based on how close we are (max difference of 100 spine)
  const maxDifference = Math.max(100, spineRange)
  const compatibility = Math.max(0, 100 - (spineDifference / maxDifference * 100))
  
  return Math.round(compatibility)
}

const handleSearchInput = (value) => {
  filters.value.search = value
  if (value.length >= 3 || value.length === 0) {
    debouncedSearch()
  }
}

const handleFilterChange = (filterName, value) => {
  filters.value[filterName] = value
  searchArrows()
}

const updateAdjustment = (field, value) => {
  adjustments.value[field] = value
  // Recalculate compatibility scores when adjustments change
  if (searchResults.value.length > 0) {
    searchResults.value = searchResults.value.map(arrow => ({
      ...arrow,
      compatibility_score: calculateCompatibilityScore(arrow)
    }))
  }
}

const addArrowToSetup = (arrow) => {
  const arrowWithSetup = {
    arrow,
    adjustments: { ...adjustments.value },
    calculatedSpine: calculatedSpine.value,
    compatibility_score: calculateCompatibilityScore(arrow)
  }
  
  emit('add-arrow', arrowWithSetup)
  closeModal()
}

const viewArrowDetails = (arrow) => {
  // Navigate to arrow details page
  window.open(`/arrows/${arrow.id}`, '_blank')
}

const closeModal = () => {
  emit('close')
}

// Helper methods
const getSpineDisplay = (arrow) => {
  if (arrow.spine_display) return arrow.spine_display
  
  if (arrow.min_spine && arrow.max_spine) {
    return arrow.min_spine === arrow.max_spine 
      ? `${arrow.min_spine}` 
      : `${arrow.min_spine}-${arrow.max_spine}`
  }
  
  return 'N/A'
}

const getDiameterRange = (arrow) => {
  if (arrow.min_diameter && arrow.max_diameter) {
    if (arrow.min_diameter === arrow.max_diameter) {
      return arrow.min_diameter.toFixed(3)
    }
    return `${arrow.min_diameter.toFixed(3)}-${arrow.max_diameter.toFixed(3)}`
  }
  return 'N/A'
}

const getGPIRange = (arrow) => {
  if (arrow.min_gpi && arrow.max_gpi) {
    if (arrow.min_gpi === arrow.max_gpi) {
      return arrow.min_gpi.toFixed(1)
    }
    return `${arrow.min_gpi.toFixed(1)}-${arrow.max_gpi.toFixed(1)}`
  }
  return 'N/A'
}

const getCompatibilityClass = (score) => {
  if (score >= 90) {
    return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  } else if (score >= 70) {
    return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  } else {
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
}

// Debounce function
const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

const debouncedSearch = debounce(() => {
  searchArrows()
}, 300)

// Initialize adjustments from bow setup
watch(() => props.bowSetup, (newSetup) => {
  if (newSetup?.bow_config) {
    adjustments.value.arrow_length = newSetup.bow_config.arrow_length || 29.0
    adjustments.value.point_weight = newSetup.bow_config.point_weight || 125
  }
}, { immediate: true })

// Load initial data when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    loadManufacturers()
    // Auto-search if we have a bow setup
    if (props.bowSetup) {
      searchArrows()
    }
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>