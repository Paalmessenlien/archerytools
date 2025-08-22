<template>
  <div>

    <!-- Comparison Bar removed per requirements -->

    <!-- Loading State -->
    <div v-if="pending" class="space-y-4">
      <div class="animate-pulse space-y-4">
        <div v-for="i in 6" :key="i">
          <div class="border border-gray-200 rounded-xl p-4 space-y-3">
            <div class="flex justify-between items-start">
              <div class="space-y-2">
                <div class="h-5 bg-gray-200 rounded w-48"></div>
                <div class="h-4 bg-gray-200 rounded w-32"></div>
              </div>
              <div class="space-y-2">
                <div class="h-4 bg-gray-200 rounded w-16"></div>
                <div class="h-4 bg-gray-200 rounded w-20"></div>
              </div>
            </div>
            <div class="grid grid-cols-4 gap-4">
              <div class="h-4 bg-gray-200 rounded"></div>
              <div class="h-4 bg-gray-200 rounded"></div>
              <div class="h-4 bg-gray-200 rounded"></div>
              <div class="h-4 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <md-elevated-card v-if="error" class="text-center">
      <div class="p-12">
        <div class="text-red-500 mb-4">
          <i class="fas fa-exclamation-triangle text-6xl"></i>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Failed to Load Recommendations</h3>
        <p class="text-gray-600 mb-4">{{ error.message || 'An error occurred while loading arrow recommendations.' }}</p>
        <md-filled-button @click="loadRecommendations">
          <i class="fas fa-redo-alt" style="margin-right: 8px;"></i>
          Try Again
        </md-filled-button>
      </div>
    </md-elevated-card>

    <!-- Filters & Controls (Always Visible) -->
    <div v-if="!pending">
      
      
      <!-- No Recommendations Message (shown after filters) -->
      <md-elevated-card v-if="!filteredRecommendations.length" class="text-center mb-6">
        <div class="p-12">
          <div class="text-gray-400 mb-4">
            <i class="fas fa-search-minus text-6xl"></i>
          </div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Recommendations Found</h3>
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            No arrows match your current bow configuration and filters.
          </p>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">
            Try adjusting your bow settings, filters, or search terms above.
          </p>
          <md-outlined-button @click="clearFilters">
            <i class="fas fa-broom" style="margin-right: 8px;"></i>
            Clear Filters
          </md-outlined-button>
        </div>
      </md-elevated-card>

      <!-- Recommendations List -->
      <div v-else class="space-y-4">
        <md-elevated-card 
          v-for="recommendation in paginatedRecommendations" 
          :key="recommendation.arrow.id"
          class="group hover:shadow-lg transition-all duration-200"
        >
          <div class="p-4 sm:p-6">
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between">
              <div class="flex-1 min-w-0">
                <!-- Header -->
                <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-3 mb-4">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 group-hover:text-primary transition-colors">
                    {{ recommendation.arrow.manufacturer }}
                  </h3>
                  <span class="hidden sm:inline text-gray-400">•</span>
                  <span class="text-base font-medium text-gray-700 dark:text-gray-300">
                    {{ recommendation.arrow.model_name }}
                  </span>
                </div>
                
                <!-- Arrow Specifications as Chips -->
                <md-chip-set class="mb-4 flex-wrap">
                  <md-assist-chip :label="`Spine: ${getSpineDisplay(recommendation.arrow)}`">
                    <i class="fas fa-ruler-horizontal fa-icon" slot="icon" style="color: #6366f1;"></i>
                  </md-assist-chip>
                  <md-assist-chip :label="recommendation.arrow.material || 'Material N/A'">
                    <i class="fas fa-layer-group fa-icon" slot="icon" style="color: #059669;"></i>
                  </md-assist-chip>
                  <md-assist-chip :label="`⌀ ${getDiameterDisplay(recommendation.arrow)}`">
                    <i class="fas fa-dot-circle fa-icon" slot="icon" style="color: #dc2626;"></i>
                  </md-assist-chip>
                  <md-assist-chip :label="getWeightDisplay(recommendation.arrow)">
                    <i class="fas fa-weight-hanging fa-icon" slot="icon" style="color: #7c2d12;"></i>
                  </md-assist-chip>
                  <!-- Total Arrow Weight -->
                  <md-assist-chip 
                    :label="`Total: ${calculateTotalArrowWeight(recommendation.arrow, cleanNumericValue(bowConfig?.arrow_length) || 29)} gn`" 
                    :title="getWeightCalculationDebug(recommendation.arrow, cleanNumericValue(bowConfig?.arrow_length) || 29)"
                    class="bg-blue-100 dark:bg-blue-900">
                    <i class="fas fa-balance-scale fa-icon" slot="icon" style="color: #3b82f6;"></i>
                  </md-assist-chip>
                </md-chip-set>
                
                <!-- Match Details -->
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  {{ recommendation.reasons?.join(', ') || 'Compatible with your setup' }}
                </p>
                
                <!-- Performance Metrics -->
                <div v-if="recommendation.performance?.performance_summary" class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-3 mb-3">
                  <div class="flex items-center justify-between mb-2">
                    <h4 class="text-sm font-semibold text-blue-800 dark:text-blue-200">
                      <i class="fas fa-tachometer-alt mr-1"></i>
                      Performance Analysis
                    </h4>
                    <span :class="getPerformanceScoreClass(recommendation.performance.performance_summary)" class="text-xs font-medium">
                      {{ getPerformanceScore(recommendation.performance.performance_summary) }}/100
                    </span>
                  </div>
                  
                  <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div class="text-center">
                      <div class="text-blue-600 dark:text-blue-400 font-medium">
                        {{ recommendation.performance.performance_summary.estimated_speed_fps }} fps
                      </div>
                      <div class="text-gray-500 dark:text-gray-400">Speed</div>
                    </div>
                    <div class="text-center">
                      <div class="text-green-600 dark:text-green-400 font-medium">
                        {{ recommendation.performance.performance_summary.kinetic_energy_40yd }} ft·lbs
                      </div>
                      <div class="text-gray-500 dark:text-gray-400">KE @40yd</div>
                    </div>
                    <div class="text-center">
                      <div class="text-purple-600 dark:text-purple-400 font-medium">
                        {{ recommendation.performance.performance_summary.foc_percentage?.toFixed(1) || 0 }}%
                      </div>
                      <div class="text-gray-500 dark:text-gray-400">FOC</div>
                    </div>
                    <div class="text-center">
                      <div :class="getPenetrationClass(recommendation.performance.performance_summary.penetration_category)" class="font-medium capitalize">
                        {{ recommendation.performance.performance_summary.penetration_category }}
                      </div>
                      <div class="text-gray-500 dark:text-gray-400">Penetration</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Compatibility & Price -->
              <div class="flex flex-col sm:flex-row sm:items-start justify-between mt-4 sm:mt-0 sm:ml-6">
                <!-- Actions -->
                <div class="flex flex-col sm:flex-row gap-2 order-2 sm:order-1 mt-3 sm:mt-0">
                  <!-- Add to Setup Button (when bow setup is selected) -->
                  <md-filled-button 
                    v-if="props.selectedBowSetup"
                    size="small"
                    @click.stop="addToSetup(recommendation)"
                    class="bg-green-600 text-white hover:bg-green-700"
                  >
                    <i class="fas fa-plus" style="margin-right: 6px;"></i>
                    Add to {{ props.selectedBowSetup.name }}
                  </md-filled-button>
                  
                  <md-filled-button size="small" @click="viewArrowDetails(recommendation.arrow.id, recommendation)">
                    <i class="fas fa-eye" style="margin-right: 6px;"></i>
                    View Details
                  </md-filled-button>
                  <!-- Compare button removed per requirements -->
                </div>
                
                <!-- Match Score -->
                <div class="text-center sm:text-right flex-shrink-0 order-1 sm:order-2">
                  <!-- Match Score with Progress -->
                  <div class="mb-4">
                    <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Match Score</div>
                    <div class="text-2xl font-bold text-primary mb-1">
                      {{ recommendation.match_percentage || 0 }}%
                    </div>
                    <md-linear-progress 
                      :value="(recommendation.match_percentage || 0) / 100"
                      class="w-20 mx-auto sm:mx-0"
                    ></md-linear-progress>
                  </div>
                  <!-- Price removed per requirements -->
                </div>
              </div>
            </div>
          </div>
        </md-elevated-card>
      </div>
      
      <!-- Load More Button -->
      <div v-if="hasMoreResults && filteredRecommendations.length > 0" class="flex flex-col items-center justify-center mt-8 mb-24 md:mb-4 p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Showing <span class="font-semibold text-gray-900 dark:text-gray-100">{{ paginatedRecommendations.length }}</span> of <span class="font-semibold text-gray-900 dark:text-gray-100">{{ filteredRecommendations.length }}</span> arrows
        </div>
        <md-filled-button 
          @click="loadMoreResults"
          :disabled="loadingMore"
          class="bg-primary-600 hover:bg-primary-700"
          style="min-width: 200px;"
        >
          <template v-if="loadingMore">
            <div class="loading-spinner mr-2"></div>
            Loading...
          </template>
          <template v-else>
            <i class="fas fa-arrow-down" style="margin-right: 8px;"></i>
            Load More Arrows ({{ remainingResults }} remaining)
          </template>
        </md-filled-button>
      </div>
      
      <!-- Debug Info (remove in production) -->
      <div v-if="false" class="mt-4 p-4 bg-yellow-100 dark:bg-yellow-900 text-sm">
        <div>Debug Info:</div>
        <div>• Total recommendations loaded: {{ recommendations.length }}</div>
        <div>• Total after filtering: {{ filteredRecommendations.length }}</div>
        <div>• Display limit: {{ displayLimit }}</div>
        <div>• Currently showing: {{ paginatedRecommendations.length }}</div>
        <div>• Has more results: {{ hasMoreResults }}</div>
        <div>• Remaining: {{ remainingResults }}</div>
        <div>• Pending: {{ pending }}</div>
      </div>
    </div> <!-- End Filters & Controls (Always Visible) -->

    <!-- Comparison removed -->
  </div>
</template>

<script setup lang="ts">
import type { BowConfiguration, ArrowRecommendation } from '~/types/arrow'
import { useBowConfigStore } from '~/stores/bowConfig'
import { useArrowFiltersStore } from '~/stores/arrowFilters'
import ManufacturerSpineChartSelector from '~/components/ManufacturerSpineChartSelector.vue'
import SpineConversionWidget from '~/components/SpineConversionWidget.vue'

// Props
const props = defineProps({
  selectedBowSetup: {
    type: Object,
    default: null
  },
  showSearchFilters: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['arrow-added-to-setup', 'error', 'recommendations-updated'])

// Stores
const bowConfigStore = useBowConfigStore()
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)

const arrowFiltersStore = useArrowFiltersStore()
const filters = computed(() => arrowFiltersStore.filters)
const showAdvancedFilters = computed(() => arrowFiltersStore.showAdvancedFilters)
const sortBy = computed(() => filters.value.sortBy)

// API
const api = useApi()

// State
const recommendations = ref([])
const pending = ref(false)
const error = ref(null)
const currentPage = ref(1)
const perPage = 20
const displayLimit = ref(20) // Start by showing 20 items
const loadingMore = ref(false)

// Manufacturers from API
const manufacturers = ref([])
const allManufacturers = ref([])

// Computed
const availableManufacturers = computed(() => {
  console.log('Computing available manufacturers...')
  console.log('Database manufacturers:', allManufacturers.value.length)
  console.log('Recommendations count:', recommendations.value.length)
  
  // Use database manufacturers instead of filtering from recommendations
  // This ensures all manufacturers are available for filtering, even if their arrows
  // don't match the current bow configuration
  if (allManufacturers.value.length > 0) {
    const manufacturers = allManufacturers.value.map(m => m.manufacturer).sort()
    console.log('Available manufacturers from database:', manufacturers)
    return manufacturers
  }
  
  // Fallback: extract from current recommendations (legacy behavior)
  const manufacturersFromRecommendations = new Set()
  recommendations.value.forEach(rec => {
    if (rec.arrow && rec.arrow.manufacturer) {
      const mfr = String(rec.arrow.manufacturer).trim()
      if (mfr) {
        manufacturersFromRecommendations.add(mfr)
      }
    }
  })
  
  const manufacturers = Array.from(manufacturersFromRecommendations).sort()
  console.log('Available manufacturers from recommendations (fallback):', manufacturers)
  console.log('Unique manufacturers found:', manufacturers.length)
  return manufacturers
})

const filteredRecommendations = computed(() => {
  let filtered = [...recommendations.value]
  console.log('Starting with', filtered.length, 'recommendations')
  
  // Apply search filter
  if (filters.value.search) {
    const searchTerm = filters.value.search.toLowerCase()
    const beforeCount = filtered.length
    filtered = filtered.filter(rec => 
      rec.arrow.manufacturer?.toLowerCase().includes(searchTerm) ||
      rec.arrow.model_name?.toLowerCase().includes(searchTerm) ||
      rec.arrow.material?.toLowerCase().includes(searchTerm)
    )
    console.log(`Search filter "${filters.value.search}": ${beforeCount} -> ${filtered.length}`)
  }
  
  // Apply manufacturer filter
  if (filters.value.manufacturer) {
    const beforeCount = filtered.length
    filtered = filtered.filter(rec => {
      if (!rec.arrow || !rec.arrow.manufacturer) {
        console.log('Arrow missing manufacturer data', rec)
        return false
      }
      
      const arrowMfr = String(rec.arrow.manufacturer).trim()
      const filterMfr = String(filters.value.manufacturer).trim()
      const matches = arrowMfr === filterMfr
      
      if (!matches) {
        console.log(`Manufacturer mismatch: arrow="${arrowMfr}" vs filter="${filterMfr}"`)
      }
      
      return matches
    })
    console.log(`Manufacturer filter: "${filters.value.manufacturer}" (${beforeCount} -> ${filtered.length} arrows)`)
    
    if (filtered.length === 0) {
      console.log('No arrows after manufacturer filtering! Checking all available manufacturers in current data:')
      const availableMfrs = new Set()
      recommendations.value.forEach(rec => {
        if (rec.arrow && rec.arrow.manufacturer) {
          availableMfrs.add(String(rec.arrow.manufacturer).trim())
        }
      })
      console.log('Available manufacturers in current recommendations:', Array.from(availableMfrs))
    }
  }
  
  // Apply match quality filter
  if (filters.value.match_quality) {
    const minMatch = parseInt(filters.value.match_quality)
    filtered = filtered.filter(rec => rec.match_percentage >= minMatch)
  }
  
  // Apply weight filters
  if (filters.value.weight_min) {
    const beforeCount = filtered.length
    filtered = filtered.filter(rec => {
      const weight = getNumericWeight(rec.arrow)
      const result = weight && weight >= parseFloat(filters.value.weight_min)
      if (!result && weight) {
        console.log(`Arrow ${rec.arrow.manufacturer} ${rec.arrow.model_name} weight ${weight} < min ${filters.value.weight_min}`)
      }
      return result
    })
    console.log(`Weight min filter ${filters.value.weight_min}: ${beforeCount} -> ${filtered.length}`)
  }
  
  if (filters.value.weight_max) {
    const beforeCount = filtered.length
    filtered = filtered.filter(rec => {
      const weight = getNumericWeight(rec.arrow)
      const result = weight && weight <= parseFloat(filters.value.weight_max)
      if (!result && weight) {
        console.log(`Arrow ${rec.arrow.manufacturer} ${rec.arrow.model_name} weight ${weight} > max ${filters.value.weight_max}`)
      }
      return result
    })
    console.log(`Weight max filter ${filters.value.weight_max}: ${beforeCount} -> ${filtered.length}`)
  }
  
  // Apply diameter range filter
  if (filters.value.diameter_range) {
    const beforeCount = filtered.length
    const [min, max] = filters.value.diameter_range.split('-').map(parseFloat)
    filtered = filtered.filter(rec => {
      const diameter = getNumericDiameter(rec.arrow)
      const result = diameter && diameter >= min && diameter <= max
      if (!result && diameter) {
        console.log(`Arrow ${rec.arrow.manufacturer} ${rec.arrow.model_name} diameter ${diameter} not in range ${min}-${max}`)
      }
      return result
    })
    console.log(`Diameter range filter ${filters.value.diameter_range}: ${beforeCount} -> ${filtered.length}`)
  }
  
  // Apply diameter filters (for custom ranges)
  if (filters.value.diameter_min) {
    filtered = filtered.filter(rec => {
      const diameter = getNumericDiameter(rec.arrow)
      return diameter && diameter >= parseFloat(filters.value.diameter_min)
    })
  }
  
  if (filters.value.diameter_max) {
    filtered = filtered.filter(rec => {
      const diameter = getNumericDiameter(rec.arrow)
      return diameter && diameter <= parseFloat(filters.value.diameter_max)
    })
  }
  
  // Apply sorting
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'compatibility':
        return (b.match_percentage || b.compatibility_score || 0) - (a.match_percentage || a.compatibility_score || 0)
      case 'manufacturer':
        const manufacturerA = a.arrow.manufacturer || 'ZZZ' // Put nulls at end
        const manufacturerB = b.arrow.manufacturer || 'ZZZ'
        const mfgComparison = manufacturerA.localeCompare(manufacturerB)
        // If manufacturers are the same, sort by match score (highest first)
        if (mfgComparison === 0) {
          return (b.match_percentage || b.compatibility_score || 0) - (a.match_percentage || a.compatibility_score || 0)
        }
        return mfgComparison
      case 'diameter_asc':
        const diameterCompAsc = getNumericDiameter(a.arrow) - getNumericDiameter(b.arrow)
        // Secondary sort by match score if diameters are equal
        if (diameterCompAsc === 0) {
          return (b.match_percentage || b.compatibility_score || 0) - (a.match_percentage || a.compatibility_score || 0)
        }
        return diameterCompAsc
      case 'diameter_desc':
        const diameterCompDesc = getNumericDiameter(b.arrow) - getNumericDiameter(a.arrow)
        // Secondary sort by match score if diameters are equal
        if (diameterCompDesc === 0) {
          return (b.match_percentage || b.compatibility_score || 0) - (a.match_percentage || a.compatibility_score || 0)
        }
        return diameterCompDesc
      case 'weight_asc':
        const weightCompAsc = getNumericWeight(a.arrow) - getNumericWeight(b.arrow)
        // Secondary sort by match score if weights are equal
        if (weightCompAsc === 0) {
          return (b.match_percentage || b.compatibility_score || 0) - (a.match_percentage || a.compatibility_score || 0)
        }
        return weightCompAsc
      case 'weight_desc':
        const weightCompDesc = getNumericWeight(b.arrow) - getNumericWeight(a.arrow)
        // Secondary sort by match score if weights are equal
        if (weightCompDesc === 0) {
          return (b.match_percentage || b.compatibility_score || 0) - (a.match_percentage || a.compatibility_score || 0)
        }
        return weightCompDesc
      case 'material':
        const materialA = a.arrow.material || 'ZZZ' // Put nulls at end
        const materialB = b.arrow.material || 'ZZZ'
        const materialComparison = materialA.localeCompare(materialB)
        // Secondary sort by match score if materials are equal
        if (materialComparison === 0) {
          return (b.match_percentage || b.compatibility_score || 0) - (a.match_percentage || a.compatibility_score || 0)
        }
        return materialComparison
      // price sorting removed
      default:
        return 0
    }
  })
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredRecommendations.value.length / perPage))

const paginatedRecommendations = computed(() => {
  // Use display limit for progressive loading
  return filteredRecommendations.value.slice(0, displayLimit.value)
})

const hasMoreResults = computed(() => {
  return filteredRecommendations.value.length > displayLimit.value
})

const remainingResults = computed(() => {
  return Math.max(0, filteredRecommendations.value.length - displayLimit.value)
})

// Match distribution statistics

// Methods
const getSpineDisplay = (arrow) => {
  // Prioritize exact matched spine over range
  if (arrow.matched_spine) {
    const material = arrow.material?.toLowerCase() || ''
    if (material.includes('wood')) {
      return `${arrow.matched_spine}#`
    } else {
      return `${arrow.matched_spine}`
    }
  }
  
  if (arrow.spine_display) {
    return arrow.spine_display
  }
  
  if (arrow.min_spine && arrow.max_spine) {
    const material = arrow.material?.toLowerCase() || ''
    if (material.includes('wood')) {
      return arrow.min_spine === arrow.max_spine 
        ? `${arrow.min_spine}#` 
        : `${arrow.min_spine}-${arrow.max_spine}#`
    } else {
      return arrow.min_spine === arrow.max_spine 
        ? `${arrow.min_spine}` 
        : `${arrow.min_spine}-${arrow.max_spine}`
    }
  }
  
  return 'N/A'
}

const getDiameterDisplay = (arrow) => {
  // Prioritize exact matched diameter over range
  if (arrow.matched_outer_diameter) {
    return `${arrow.matched_outer_diameter}"`
  }
  
  if (arrow.min_diameter && arrow.max_diameter) {
    return arrow.min_diameter === arrow.max_diameter 
      ? `${arrow.min_diameter}"` 
      : `${arrow.min_diameter}-${arrow.max_diameter}"`
  }
  return 'N/A'
}

const getWeightDisplay = (arrow) => {
  // Prioritize exact matched weight over range
  if (arrow.matched_gpi) {
    return `${arrow.matched_gpi} GPI`
  }
  
  if (arrow.min_gpi && arrow.max_gpi) {
    return arrow.min_gpi === arrow.max_gpi 
      ? `${arrow.min_gpi} GPI` 
      : `${arrow.min_gpi}-${arrow.max_gpi} GPI`
  }
  
  // Check spine_specifications for actual GPI weight
  if (arrow.spine_specifications && arrow.spine_specifications.length > 0) {
    const spec = arrow.spine_specifications[0]
    if (spec.gpi_weight && spec.gpi_weight > 0) {
      return `${spec.gpi_weight} GPI`
    }
    
    // If no GPI weight, estimate it based on spine and characteristics
    const estimatedGpi = estimateGpiWeight(spec.spine, arrow.material, spec.outer_diameter)
    return `~${estimatedGpi} GPI` // ~ indicates estimated value
  }
  
  return 'N/A'
}

const getNumericSpine = (arrow) => {
  return arrow.min_spine || 0
}

const getNumericWeight = (arrow) => {
  // Handle different data structures - recommendations vs database arrows
  if (arrow.matched_gpi) return arrow.matched_gpi
  if (arrow.min_gpi) return arrow.min_gpi
  if (arrow.max_gpi) return arrow.max_gpi
  
  // Check spine_specifications array for GPI weight
  if (arrow.spine_specifications && arrow.spine_specifications.length > 0) {
    const spec = arrow.spine_specifications[0]
    if (spec.gpi_weight && spec.gpi_weight > 0) {
      return spec.gpi_weight
    }
    
    // If no GPI weight, estimate it based on spine and characteristics
    return estimateGpiWeight(spec.spine, arrow.material, spec.outer_diameter)
  }
  
  return 0
}

const getNumericDiameter = (arrow) => {
  // Handle different data structures - recommendations vs database arrows
  if (arrow.matched_outer_diameter) return arrow.matched_outer_diameter
  if (arrow.matched_inner_diameter) return arrow.matched_inner_diameter
  if (arrow.min_diameter) return arrow.min_diameter
  if (arrow.max_diameter) return arrow.max_diameter
  if (arrow.min_outer_diameter) return arrow.min_outer_diameter
  if (arrow.min_inner_diameter) return arrow.min_inner_diameter
  
  // Check spine_specifications array for diameter
  if (arrow.spine_specifications && arrow.spine_specifications.length > 0) {
    const spec = arrow.spine_specifications[0]
    if (spec.outer_diameter) return spec.outer_diameter
    if (spec.inner_diameter) return spec.inner_diameter
  }
  
  return 0
}

const hasActiveFilters = computed(() => {
  const f = filters.value
  return !!(f.search || f.manufacturer || f.match_quality || f.weight_min || 
           f.weight_max || f.diameter_range || f.diameter_min || f.diameter_max ||
           f.sortBy !== 'compatibility')
})

const clearFilters = () => {
  arrowFiltersStore.clearFilters()
  currentPage.value = 1
}

const loadMoreResults = () => {
  loadingMore.value = true
  // Simulate loading delay for better UX
  setTimeout(() => {
    displayLimit.value += 20 // Load 20 more results
    loadingMore.value = false
  }, 300)
}


// Calculate vane weight based on type and length (same logic as calculator)
const calculateVaneWeight = () => {
  const vaneType = bowConfig.value.vane_type || 'plastic'
  const vaneLength = bowConfig.value.vane_length || 4
  
  // Base weights per inch for different vane types
  const baseWeights = {
    plastic: 1.2,    // gn per inch - typical plastic vane
    feather: 0.8,    // gn per inch - natural feathers are lighter
    spin: 1.5        // gn per inch - spin vanes are typically heavier
  }
  
  const baseWeight = baseWeights[vaneType] || baseWeights.plastic
  const calculatedWeight = baseWeight * vaneLength
  
  return Math.round(calculatedWeight * 10) / 10 // Round to 1 decimal place
}

// Smart GPI weight estimation based on spine values and arrow characteristics
const estimateGpiWeight = (spine, material, outerDiameter) => {
  // Professional GPI weight estimation based on industry standards
  
  // Base GPI weight ranges by spine (industry averages)
  let baseGpi = 8.5 // Default fallback
  
  if (spine >= 600) {
    baseGpi = 12.5 // Very weak spines (heavy arrows)
  } else if (spine >= 500) {
    baseGpi = 10.5 // Weak spines 
  } else if (spine >= 400) {
    baseGpi = 8.5  // Medium spines
  } else if (spine >= 340) {
    baseGpi = 7.5  // Stiff spines
  } else if (spine >= 300) {
    baseGpi = 6.8  // Very stiff spines
  } else if (spine >= 250) {
    baseGpi = 5.9  // Ultra stiff spines
  } else {
    baseGpi = 5.2  // Extremely stiff spines (light, fast arrows)
  }
  
  // Material adjustments
  if (material) {
    const materialLower = material.toLowerCase()
    if (materialLower.includes('aluminum') && materialLower.includes('carbon')) {
      baseGpi *= 1.15 // Carbon/Aluminum composite arrows are heavier
    } else if (materialLower.includes('aluminum')) {
      baseGpi *= 1.3  // Pure aluminum arrows are heavier
    } else if (materialLower.includes('wood')) {
      baseGpi *= 1.25 // Wood arrows are heavier
    }
    // Carbon arrows use base weight (lightest option)
  }
  
  // Diameter adjustments (larger diameter = more material = heavier)
  if (outerDiameter) {
    const diameter = parseFloat(outerDiameter)
    if (diameter > 0.3) {
      baseGpi *= 1.2  // Large diameter arrows
    } else if (diameter > 0.25) {
      baseGpi *= 1.1  // Standard diameter arrows
    } else if (diameter < 0.2) {
      baseGpi *= 0.85 // Ultra-thin arrows
    }
    // Standard 0.2-0.25" diameter uses base weight
  }
  
  return Math.round(baseGpi * 10) / 10 // Round to 1 decimal place
}

// Utility function to clean numeric values from strings (removes quotes, units, etc.)
const cleanNumericValue = (value) => {
  if (typeof value === 'number') return value
  if (!value) return null
  
  // Convert to string and remove all non-numeric characters except decimal point and negative sign
  const cleaned = String(value).replace(/[^0-9.-]/g, '')
  const parsed = parseFloat(cleaned)
  
  return isNaN(parsed) ? null : parsed
}

// Calculate total arrow weight based on GPI and arrow length
const calculateTotalArrowWeight = (arrow, arrowLength, componentWeights = {}) => {
  if (!arrow || !arrow.spine_specifications) return 0
  
  // Find the appropriate spine specification (use first one if no specific match)
  const spineSpec = arrow.spine_specifications[0]
  if (!spineSpec) return 0
  
  // Use actual GPI weight or estimate based on arrow characteristics
  let gpiWeight = spineSpec.gpi_weight
  if (!gpiWeight || gpiWeight <= 0) {
    gpiWeight = estimateGpiWeight(
      spineSpec.spine, 
      arrow.material, 
      spineSpec.outer_diameter
    )
    console.log(`🎯 Estimated GPI weight for ${arrow.manufacturer} ${arrow.model_name} (${spineSpec.spine} spine): ${gpiWeight} GPI`)
  }
  
  // Arrow base length (from manufacturer database) - used for WEIGHT calculation only
  // This is different from user's calculator length which is used for tuning/spine calculations
  let arrowBaseLength = null
  
  // First priority: Use arrow's own base length from database
  if (spineSpec.length_options && spineSpec.length_options.length > 0) {
    // Use the most common/middle length option from arrow's database specifications
    const sortedLengths = [...spineSpec.length_options].sort((a, b) => a - b)
    const rawArrowBaseLength = sortedLengths[Math.floor(sortedLengths.length / 2)]
    arrowBaseLength = cleanNumericValue(rawArrowBaseLength)
    console.log(`📏 Using arrow's base length from database: "${rawArrowBaseLength}" → Cleaned: ${arrowBaseLength}" (options: ${spineSpec.length_options.join(', ')})`)
  } else {
    // Arrow has no base length data - use spine-based manufacturer defaults
    if (spineSpec.spine <= 300) {
      arrowBaseLength = 28  // Very stiff spines typically come in shorter lengths
    } else if (spineSpec.spine <= 350) {
      arrowBaseLength = 29  // Standard target/hunting length
    } else if (spineSpec.spine <= 400) {
      arrowBaseLength = 30  // Medium spine hunting arrows
    } else {
      arrowBaseLength = 31  // Weak spine traditional/longer arrows
    }
    console.log(`⚠️  Arrow has no base length data - using spine-based default: ${arrowBaseLength}" (spine: ${spineSpec.spine})`)
  }
  
  // Ensure we have a valid base length for calculation
  if (!arrowBaseLength || arrowBaseLength <= 0) {
    console.error(`❌ Cannot calculate weight - no valid base length for ${arrow.manufacturer} ${arrow.model_name}`)
    return 0
  }
  
  // Calculate shaft weight using arrow's base length (not user's calculator length)
  const shaftWeight = gpiWeight * arrowBaseLength
  
  // Add component weights from user's bow configuration
  const pointWeight = componentWeights.point_weight || bowConfig.value?.point_weight || 125
  const insertWeight = componentWeights.insert_weight || bowConfig.value?.insert_weight || 0
  const nockWeight = componentWeights.nock_weight || bowConfig.value?.nock_weight || 10
  const bushingWeight = componentWeights.bushing_weight || bowConfig.value?.bushing_weight || 0
  const vaneWeightPerVane = componentWeights.vane_weight_per || calculateVaneWeight()
  const numberOfVanes = componentWeights.number_of_vanes || bowConfig.value?.number_of_vanes || 3
  
  const totalVaneWeight = vaneWeightPerVane * numberOfVanes
  
  // Total arrow weight = shaft + components
  const totalWeight = shaftWeight + pointWeight + insertWeight + nockWeight + bushingWeight + totalVaneWeight
  
  console.log(`⚖️  Weight calculation for ${arrow.manufacturer} ${arrow.model_name}:`)
  console.log(`   Shaft: ${gpiWeight} GPI × ${arrowBaseLength}" = ${shaftWeight.toFixed(1)} gn`)
  console.log(`   Components: Point(${pointWeight}) + Insert(${insertWeight}) + Nock(${nockWeight}) + Vanes(${totalVaneWeight.toFixed(1)}) = ${(pointWeight + insertWeight + nockWeight + totalVaneWeight).toFixed(1)} gn`)
  console.log(`   Total: ${totalWeight.toFixed(1)} gn`)
  
  return Math.round(totalWeight * 10) / 10 // Round to 1 decimal place
}

// Debug function to get detailed calculation info for tooltips
const getWeightCalculationDebug = (arrow, arrowLength) => {
  if (!arrow || !arrow.spine_specifications) return 'No arrow or spine specs'
  
  const spineSpec = arrow.spine_specifications[0]
  if (!spineSpec) return 'No spine specification'
  
  // Clean the arrow length value to remove any quotes or units
  const cleanedLength = cleanNumericValue(arrowLength)
  console.log(`🔍 Debug: Raw arrow length: "${arrowLength}" → Cleaned: ${cleanedLength}`)
  
  // Use actual GPI weight or estimate based on arrow characteristics
  let gpiWeight = spineSpec.gpi_weight
  let gpiSource = 'actual'
  if (!gpiWeight || gpiWeight <= 0) {
    gpiWeight = estimateGpiWeight(
      spineSpec.spine, 
      arrow.material, 
      spineSpec.outer_diameter
    )
    gpiSource = 'estimated'
  }
  
  // Arrow base length calculation
  let arrowBaseLength = null
  let lengthSource = 'unknown'
  
  if (spineSpec.length_options && spineSpec.length_options.length > 0) {
    const sortedLengths = [...spineSpec.length_options].sort((a, b) => a - b)
    arrowBaseLength = sortedLengths[Math.floor(sortedLengths.length / 2)]
    lengthSource = `database (${spineSpec.length_options.join(', ')})`
  } else {
    if (spineSpec.spine <= 300) {
      arrowBaseLength = 28
    } else if (spineSpec.spine <= 350) {
      arrowBaseLength = 29
    } else if (spineSpec.spine <= 400) {
      arrowBaseLength = 30
    } else {
      arrowBaseLength = 31
    }
    lengthSource = `spine-based default`
  }
  
  if (!arrowBaseLength || arrowBaseLength <= 0) {
    return `ERROR: No valid base length for ${arrow.manufacturer} ${arrow.model_name}`
  }
  
  // Calculate components
  const shaftWeight = gpiWeight * arrowBaseLength
  const pointWeight = bowConfig.value?.point_weight || 125
  const insertWeight = bowConfig.value?.insert_weight || 0
  const nockWeight = bowConfig.value?.nock_weight || 10
  const bushingWeight = bowConfig.value?.bushing_weight || 0
  const vaneWeightPerVane = calculateVaneWeight()
  const numberOfVanes = bowConfig.value?.number_of_vanes || 3
  const totalVaneWeight = vaneWeightPerVane * numberOfVanes
  
  const totalWeight = shaftWeight + pointWeight + insertWeight + nockWeight + bushingWeight + totalVaneWeight
  
  return `${arrow.manufacturer} ${arrow.model_name}
Raw Length Input: "${arrowLength}" → Cleaned: ${cleanedLength}
GPI: ${gpiWeight} (${gpiSource})
Length: ${arrowBaseLength}" (${lengthSource})
Shaft: ${gpiWeight} × ${arrowBaseLength}" = ${shaftWeight.toFixed(1)}gn
Point: ${pointWeight}gn
Insert: ${insertWeight}gn
Nock: ${nockWeight}gn
Vanes: ${numberOfVanes} × ${vaneWeightPerVane.toFixed(1)} = ${totalVaneWeight.toFixed(1)}gn
Total: ${totalWeight.toFixed(1)}gn
Result: ${isNaN(totalWeight) ? 'NaN - CHECK CALCULATION!' : 'OK'}`
}

const addToSetup = async (recommendation) => {
  console.log('Add to setup called for:', recommendation.arrow.manufacturer, recommendation.arrow.model_name)
  
  if (!props.selectedBowSetup) {
    console.error('No bow setup selected')
    emit('error', 'No bow setup selected')
    return
  }

  try {
    const { useAuth } = await import('~/composables/useAuth')
    const { addArrowToSetup } = useAuth()

    // Prepare the arrow data for adding to setup
    // IMPORTANT: Use the selected arrow spine, NOT the calculated optimal spine
    const arrowData = {
      arrow_id: recommendation.arrow.id,
      arrow_length: bowConfig.value.arrow_length || 29,
      point_weight: bowConfig.value.point_weight || 125,
      calculated_spine: recommendation.matched_spine || recommendation.arrow?.matched_spine,
      compatibility_score: recommendation.match_percentage,
      // Include all component weights from bow configuration
      nock_weight: bowConfig.value.nock_weight || 10,
      insert_weight: bowConfig.value.insert_weight || 0,
      bushing_weight: bowConfig.value.bushing_weight || 0,
      vane_weight_per: bowConfig.value.vane_weight_override ? (bowConfig.value.vane_weight_per || 5) : calculateVaneWeight(),
      vane_type: bowConfig.value.vane_type || 'plastic',
      vane_length: bowConfig.value.vane_length || 4,
      number_of_vanes: bowConfig.value.number_of_vanes || 3,
      notes: `Added from calculator - ${recommendation.match_percentage}% match`
    }

    // Call the API to add arrow to setup
    console.log('Calling API to add arrow to setup...')
    const result = await addArrowToSetup(props.selectedBowSetup.id, arrowData)
    console.log('API call successful:', result)

    // Emit event to parent component
    console.log('Emitting arrow-added-to-setup event')
    emit('arrow-added-to-setup', {
      arrow: recommendation.arrow,
      setup: props.selectedBowSetup,
      arrowData
    })

  } catch (error) {
    console.error('Error adding arrow to setup:', error)
    emit('error', `Failed to add arrow to setup: ${error.message}`)
  }
}

const viewArrowDetails = (arrowId, recommendation = null) => {
  // Navigate to arrow details page with calculation context if available
  const query: Record<string, string> = {}
  
  if (recommendation && props.bowConfig) {
    // Encode bow configuration
    query.bow_config = btoa(JSON.stringify(props.bowConfig))
    
    // Include recommendation data
    query.compatibility_score = recommendation.compatibility_score.toString()
    query.match_percentage = recommendation.match_percentage.toString()
    query.compatibility_rating = recommendation.compatibility_rating
    query.reasons = btoa(JSON.stringify(recommendation.reasons))
    
    // Include spine specification details
    if (recommendation.spine_specification) {
      query.spine_spec = btoa(JSON.stringify(recommendation.spine_specification))
    }
  }
  
  navigateTo({
    path: `/arrows/${arrowId}`,
    query: Object.keys(query).length > 0 ? query : undefined
  })
}

// Handle spine chart selection

const loadManufacturers = async () => {
  try {
    const result = await api.getManufacturers()
    console.log('Loaded manufacturers from API:', result)
    allManufacturers.value = result || []
  } catch (err) {
    console.error('Error loading manufacturers:', err)
    // Fallback - will use manufacturers from recommendations
    allManufacturers.value = []
  }
}

// REMOVED: loadArrowsFromManufacturer function 
// This function was causing 0% match scores by using the database API instead of tuning API
// Now we always use loadRecommendations() which calls the tuning API with proper scoring

const loadRecommendations = async () => {
  if (pending.value) return

  pending.value = true
  error.value = null

  try {
    // Try the tuning recommendations API first
    const requestData = {
        draw_weight: bowConfig.value.draw_weight || 45,
        draw_length: bowConfig.value.draw_length || 28, // NOTE: Only used for archer profile, NOT spine calculations
        bow_type: bowConfig.value.bow_type || 'compound',
        arrow_length: bowConfig.value.arrow_length || 29, // This is what's used for spine calculations
        point_weight: bowConfig.value.point_weight || 125,
        arrow_material: bowConfig.value.arrow_material || 'carbon',
        shooting_style: 'target',
        experience_level: 'intermediate',
        primary_goal: 'maximum_accuracy',
        arrow_type: 'target_outdoor',
        limit: 300,  // Request more recommendations for progressive loading
        min_match_percentage: 60  // Include all matches down to 60%
      }
      
      // Add manufacturer filter if selected
      if (filters.value.manufacturer) {
        console.log(`Adding manufacturer filter to API request: "${filters.value.manufacturer}"`)
        requestData.preferred_manufacturers = [filters.value.manufacturer]
      }
      
    console.log('Sending recommendation request:', requestData)
    
    try {
      const result = await api.getArrowRecommendations(requestData)
      recommendations.value = result.recommended_arrows || []
      console.log('API Response Summary:', {
        requested_limit: requestData.limit,
        received_count: recommendations.value.length,
        result_keys: Object.keys(result),
        has_more_field: result.has_more || 'not_present',
        total_available: result.total || 'not_present'
      })
      console.log('Full API result structure:', result)
      
      // Debug: Check if we got proper match scores
      if (recommendations.value.length > 0) {
        const firstRec = recommendations.value[0]
        console.log('First recommendation structure:', {
          match_percentage: firstRec.match_percentage,
          compatibility_score: firstRec.compatibility_score,
          arrow_manufacturer: firstRec.arrow?.manufacturer,
          spine_specs_count: firstRec.arrow?.spine_specifications?.length || 0
        })
      }
    } catch (tuningError) {
      console.warn('Tuning API failed, falling back to arrow search:', tuningError)
      console.log('Tuning error details:', tuningError)
      
      // Fallback: Use arrow search with basic filtering - get more results
      const fallbackFilters = {
        // Don't restrict by material initially to get more diverse results
        limit: 200  // Increased to get more results for progressive loading
      }
      
      // Only add material filter if it's specifically set and not "all materials"
      if (bowConfig.value.arrow_material && bowConfig.value.arrow_material !== '' && bowConfig.value.arrow_material !== 'carbon') {
        fallbackFilters.material = bowConfig.value.arrow_material
      }
      
      const arrowsResult = await api.getArrows(fallbackFilters)
      const arrows = arrowsResult.arrows || []
      
      // Convert arrows to recommendation format with basic compatibility scoring
      recommendations.value = arrows.map(arrow => ({
        arrow: arrow,
        spine_specification: arrow.spine_specifications?.[0] || {},
        match_percentage: calculateBasicCompatibility(arrow),
        spine_calculation: {
          calculated_spine: bowConfig.value.calculated_spine || 400
        },
        recommendations: ["Fallback recommendation - verify compatibility"]
      }))
      
      console.log('Loaded fallback recommendations:', recommendations.value.length, 'arrows')
    }

  } catch (err) {
    error.value = err
    console.error('Error loading recommendations:', err)
    console.error('Error details:', {
      message: err.message,
      bowConfig: bowConfig.value
    })
  } finally {
    pending.value = false
  }
}

// Basic compatibility calculation for fallback
const calculateBasicCompatibility = (arrow) => {
  if (!arrow.spine_specifications || arrow.spine_specifications.length === 0) {
    return 50 // Default compatibility if no spine data
  }
  
  const targetSpine = calculateTargetSpine()
  const spineSpec = arrow.spine_specifications[0]
  const arrowSpine = parseFloat(spineSpec.spine) || 0
  
  if (arrowSpine === 0) return 50
  
  // Calculate percentage based on how close the spine is to target
  const spineDiff = Math.abs(targetSpine - arrowSpine)
  const compatibility = Math.max(0, 100 - (spineDiff / targetSpine) * 100)
  
  return Math.round(compatibility)
}

// Basic spine calculation for fallback
const calculateTargetSpine = () => {
  const drawWeight = bowConfig.value.draw_weight || 50
  const arrowLength = bowConfig.value.arrow_length || 29
  const pointWeight = bowConfig.value.point_weight || 125
  
  // Simple spine calculation
  let baseSpine = drawWeight * 12.5
  const lengthAdjustment = (arrowLength - 28) * 25
  const pointAdjustment = (pointWeight - 125) * 0.5
  
  return baseSpine + lengthAdjustment + pointAdjustment
}

// Arrow comparison state
const comparisonArrows = ref([])
const showComparisonModal = ref(false)

// Comparison methods
const addToComparison = (recommendation) => {
  const arrow = recommendation.arrow
  // Check if arrow is already in comparison
  if (comparisonArrows.value.find(a => a.id === arrow.id)) {
    // Remove from comparison
    comparisonArrows.value = comparisonArrows.value.filter(a => a.id !== arrow.id)
  } else {
    // Add to comparison (limit to 4 arrows for better UX)
    if (comparisonArrows.value.length < 4) {
      comparisonArrows.value.push({
        ...arrow,
        recommendation_data: recommendation
      })
    }
  }
}

const isInComparison = (arrow) => {
  return comparisonArrows.value.some(a => a.id === arrow.id)
}

const clearComparison = () => {
  comparisonArrows.value = []
}

const openComparison = () => {
  if (comparisonArrows.value.length >= 2) {
    showComparisonModal.value = true
  }
}

const closeComparison = () => {
  showComparisonModal.value = false
}

// Watch for bow config changes
watch([bowConfig], () => {
  // Debounce the reload
  setTimeout(() => {
    loadRecommendations()
  }, 300)
}, { deep: true, immediate: true })

// Watch for recommendations changes to update manufacturers
watch(recommendations, () => {
  // Force reactivity update for manufacturers
  nextTick(() => {
    console.log('Recommendations updated, available manufacturers:', availableManufacturers.value)
    // Emit recommendations data to parent
    emit('recommendations-updated', recommendations.value)
  })
}, { deep: true })

// Watch for manufacturer filter changes
watch(() => filters.value.manufacturer, async (newManufacturer, oldManufacturer) => {
  console.log(`Manufacturer filter changed: "${oldManufacturer}" -> "${newManufacturer}"`)
  
  if (newManufacturer !== oldManufacturer) {
    // Always reload recommendations when manufacturer filter changes
    // This ensures we get proper tuning scores from the API
    console.log(`Manufacturer filter changed, reloading recommendations with tuning API...`)
    await loadRecommendations()
  }
  
  // Reset to first page when filter changes
  currentPage.value = 1
  displayLimit.value = 20 // Reset display limit
})

// Watch for other filter changes
watch(filters, () => {
  currentPage.value = 1
  displayLimit.value = 20 // Reset display limit when any filter changes
}, { deep: true })

// Initial load
onMounted(() => {
  // Initialize filters from localStorage
  arrowFiltersStore.initializeFilters()
  
  // Reset display limit on mount
  displayLimit.value = 20
  
  loadManufacturers() // Load manufacturers first
  loadRecommendations()
})

// Performance helper functions
const getPerformanceScore = (performanceSummary) => {
  if (!performanceSummary) return 0
  
  // Calculate composite performance score based on multiple factors
  const keScore = Math.min(100, (performanceSummary.kinetic_energy_40yd / 80) * 100) // 80 ft-lbs = 100%
  const penetrationScore = performanceSummary.penetration_score || 0
  const focScore = performanceSummary.foc_percentage ? 
    Math.max(0, 100 - Math.abs((performanceSummary.foc_percentage || 0) - 12) * 5) : 50 // Optimal FOC around 12%
  
  // Weighted average: 40% penetration, 30% KE, 30% FOC
  const compositeScore = (penetrationScore * 0.4) + (keScore * 0.3) + (focScore * 0.3)
  return Math.round(compositeScore)
}

const getPerformanceScoreClass = (performanceSummary) => {
  const score = getPerformanceScore(performanceSummary)
  if (score >= 80) return 'text-green-600 dark:text-green-400'
  if (score >= 60) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getPenetrationClass = (category) => {
  switch (category) {
    case 'excellent': return 'text-green-600 dark:text-green-400'
    case 'good': return 'text-blue-600 dark:text-blue-400'
    case 'fair': return 'text-yellow-600 dark:text-yellow-400'
    case 'poor': return 'text-red-600 dark:text-red-400'
    default: return 'text-gray-500 dark:text-gray-400'
  }
}
</script>
