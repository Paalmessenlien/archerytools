<template>
  <div>
    <!-- Recommendations Header -->
    <div class="mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-2">
        Arrow Recommendations
      </h2>
      <p class="text-gray-600">
        Based on your bow configuration: <span class="font-medium">{{ bowConfigStore.configSummary }}</span>
      </p>
    </div>

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

    <!-- No Recommendations -->
    <md-elevated-card v-else-if="!pending && !filteredRecommendations.length" class="text-center">
      <div class="p-12">
        <div class="text-gray-400 mb-4">
          <i class="fas fa-search-minus text-6xl"></i>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Recommendations Found</h3>
        <p class="text-gray-600 mb-4">
          No arrows match your current bow configuration and filters.
        </p>
        <p class="text-sm text-gray-500 mb-6">
          Try adjusting your bow settings, filters, or search terms.
        </p>
        <md-outlined-button @click="clearFilters">
          <i class="fas fa-broom" style="margin-right: 8px;"></i>
          Clear Filters
        </md-outlined-button>
      </div>
    </md-elevated-card>

    <!-- Recommendations with Filters -->
    <div v-else>
      <!-- Filters & Controls -->
      <md-elevated-card class="mb-6">
        <div class="p-6">
          <!-- Search Bar -->
          <div class="mb-4">
            <md-outlined-text-field 
              :value="filters.search"
              @input="filters.search = $event.target.value"
              label="Search arrows..."
              type="search"
              class="w-full"
            >
              <i class="fas fa-search" slot="leading-icon" style="color: #6b7280;"></i>
            </md-outlined-text-field>
          </div>
          
          <!-- Filter Row -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <!-- Manufacturer Filter -->
            <md-filled-select :value="filters.manufacturer" @change="filters.manufacturer = $event.target.value" label="Manufacturer">
              <md-select-option value="">
                <div slot="headline">All Manufacturers</div>
              </md-select-option>
              <md-select-option v-for="mfr in availableManufacturers" :key="mfr" :value="mfr">
                <div slot="headline">{{ mfr }}</div>
              </md-select-option>
            </md-filled-select>
            
            <!-- Match Quality Filter -->
            <md-filled-select :value="filters.match_quality" @change="filters.match_quality = $event.target.value" label="Match Quality">
              <md-select-option value="">
                <div slot="headline">All Matches</div>
              </md-select-option>
              <md-select-option value="100">
                <div slot="headline">100% Matches Only</div>
              </md-select-option>
              <md-select-option value="90">
                <div slot="headline">90%+ Matches</div>
              </md-select-option>
              <md-select-option value="80">
                <div slot="headline">80%+ Matches</div>
              </md-select-option>
            </md-filled-select>
            
            <!-- Sort By -->
            <md-filled-select :value="sortBy" @change="sortBy = $event.target.value" label="Sort By">
              <md-select-option value="compatibility">
                <div slot="headline">Best Match</div>
              </md-select-option>
              <md-select-option value="manufacturer">
                <div slot="headline">Manufacturer</div>
              </md-select-option>
              <md-select-option value="diameter_asc">
                <div slot="headline">Diameter (Small to Large)</div>
              </md-select-option>
              <md-select-option value="diameter_desc">
                <div slot="headline">Diameter (Large to Small)</div>
              </md-select-option>
              <md-select-option value="weight_asc">
                <div slot="headline">Weight (Light to Heavy)</div>
              </md-select-option>
              <md-select-option value="weight_desc">
                <div slot="headline">Weight (Heavy to Light)</div>
              </md-select-option>
              <md-select-option value="material">
                <div slot="headline">Material</div>
              </md-select-option>
              <md-select-option value="price">
                <div slot="headline">Price</div>
              </md-select-option>
            </md-filled-select>
          </div>
        
          <!-- Advanced Filters Toggle -->
          <div class="flex items-center justify-between">
            <md-text-button @click="showAdvancedFilters = !showAdvancedFilters">
              <i class="fas transition-transform" :class="showAdvancedFilters ? 'fa-chevron-up rotate-180' : 'fa-chevron-down'" style="margin-right: 8px;"></i>
              {{ showAdvancedFilters ? 'Hide' : 'Show' }} Advanced Filters
            </md-text-button>
            
            <div class="text-sm text-gray-600">
              Showing {{ filteredRecommendations.length }} arrows
              <span v-if="recommendedSpine" class="ml-2 font-medium text-primary">
                (Target Spine: {{ recommendedSpine }})
              </span>
            </div>
          </div>
        
          <!-- Advanced Filters -->
          <div v-if="showAdvancedFilters" class="mt-6 pt-4">
            <md-divider class="mb-4"></md-divider>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <!-- Diameter Range Dropdown -->
              <md-filled-select :value="filters.diameter_range" @change="filters.diameter_range = $event.target.value" label="Diameter Range">
                <md-select-option value="">
                  <div slot="headline">All Diameters</div>
                </md-select-option>
                <md-select-option value="0.200-0.250">
                  <div slot="headline">0.200" - 0.250"</div>
                </md-select-option>
                <md-select-option value="0.250-0.300">
                  <div slot="headline">0.250" - 0.300"</div>
                </md-select-option>
                <md-select-option value="0.300-0.350">
                  <div slot="headline">0.300" - 0.350"</div>
                </md-select-option>
                <md-select-option value="0.350-0.400">
                  <div slot="headline">0.350" - 0.400"</div>
                </md-select-option>
                <md-select-option value="0.400-0.450">
                  <div slot="headline">0.400" - 0.450"</div>
                </md-select-option>
              </md-filled-select>
              
              <!-- Weight Range -->
              <md-outlined-text-field 
                :value="filters.weight_min"
                @input="filters.weight_min = $event.target.value"
                type="number" 
                step="0.1"
                label="Min Weight (GPI)"
              ></md-outlined-text-field>
              <md-outlined-text-field 
                :value="filters.weight_max"
                @input="filters.weight_max = $event.target.value"
                type="number" 
                step="0.1"
                label="Max Weight (GPI)"
              ></md-outlined-text-field>
            </div>
          </div>
        </div>
      </md-elevated-card>

      <!-- Recommendations List -->
      <div class="space-y-4">
        <md-elevated-card 
          v-for="recommendation in paginatedRecommendations" 
          :key="recommendation.arrow.id"
          @click="openArrowDetails(recommendation.arrow)"
          class="cursor-pointer group hover:shadow-lg transition-all duration-200"
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
                </md-chip-set>
                
                <!-- Match Details -->
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  {{ recommendation.reasons?.join(', ') || 'Compatible with your setup' }}
                </p>
              </div>
              
              <!-- Compatibility & Price -->
              <div class="flex flex-col sm:flex-row sm:items-start justify-between mt-4 sm:mt-0 sm:ml-6">
                <!-- Actions -->
                <div class="flex flex-col sm:flex-row gap-2 order-2 sm:order-1 mt-3 sm:mt-0">
                  <md-filled-button size="small">
                    <i class="fas fa-eye" style="margin-right: 6px;"></i>
                    View Details
                  </md-filled-button>
                  <md-text-button size="small">
                    <i class="fas fa-plus-circle" style="margin-right: 6px;"></i>
                    Add to Session
                  </md-text-button>
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
                  
                  <!-- Price -->
                  <div class="text-center sm:text-right">
                    <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Price Range</div>
                    <p class="font-semibold text-gray-900 dark:text-gray-100">
                      {{ recommendation.arrow.price_range || 'Varies' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </md-elevated-card>
      </div>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-center space-x-4 mt-6">
        <md-outlined-button 
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
        >
          <i class="fas fa-chevron-left" style="margin-right: 6px;"></i>
          Previous
        </md-outlined-button>
        
        <span class="px-4 py-2 text-sm text-gray-600 font-medium">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        
        <md-outlined-button 
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
        >
          Next
          <i class="fas fa-chevron-right" style="margin-left: 6px;"></i>
        </md-outlined-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'

// Store
const bowConfigStore = useBowConfigStore()
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)

// API
const api = useApi()

// State
const recommendations = ref([])
const pending = ref(false)
const error = ref(null)
const showAdvancedFilters = ref(false)
const currentPage = ref(1)
const perPage = 12

// Filters
const filters = ref({
  search: '',
  manufacturer: '',
  match_quality: '',
  weight_min: '',
  weight_max: '',
  diameter_range: '',
  diameter_min: '',
  diameter_max: ''
})

const sortBy = ref('compatibility')

// Manufacturers from API
const manufacturers = ref([])
const allManufacturers = ref([])

// Computed
const availableManufacturers = computed(() => {
  console.log('Computing available manufacturers...')
  console.log('API manufacturers:', allManufacturers.value)
  console.log('Recommendations count:', recommendations.value.length)
  
  // First try to get manufacturers from API data
  if (allManufacturers.value.length > 0) {
    const apiManufacturers = allManufacturers.value.map(m => m.manufacturer || m).sort()
    console.log('Using API manufacturers:', apiManufacturers)
    return apiManufacturers
  }
  
  // Fallback to extracting from recommendations
  const manufacturersFromRecommendations = new Set()
  recommendations.value.forEach(rec => {
    if (rec.arrow && rec.arrow.manufacturer) {
      manufacturersFromRecommendations.add(rec.arrow.manufacturer)
    }
  })
  
  const manufacturers = Array.from(manufacturersFromRecommendations).sort()
  console.log('Using manufacturers from recommendations:', manufacturers)
  return manufacturers
})

const filteredRecommendations = computed(() => {
  let filtered = [...recommendations.value]
  
  // Apply search filter
  if (filters.value.search) {
    const searchTerm = filters.value.search.toLowerCase()
    filtered = filtered.filter(rec => 
      rec.arrow.manufacturer?.toLowerCase().includes(searchTerm) ||
      rec.arrow.model_name?.toLowerCase().includes(searchTerm) ||
      rec.arrow.material?.toLowerCase().includes(searchTerm)
    )
  }
  
  // Apply manufacturer filter
  if (filters.value.manufacturer) {
    console.log('Filtering by manufacturer:', filters.value.manufacturer)
    const beforeCount = filtered.length
    filtered = filtered.filter(rec => {
      const match = rec.arrow && rec.arrow.manufacturer === filters.value.manufacturer
      if (!match && rec.arrow) {
        console.log('Filtered out:', rec.arrow.manufacturer, 'looking for:', filters.value.manufacturer)
      }
      return match
    })
    console.log('Filtered arrows count:', beforeCount, '->', filtered.length)
  }
  
  // Apply match quality filter
  if (filters.value.match_quality) {
    const minMatch = parseInt(filters.value.match_quality)
    filtered = filtered.filter(rec => rec.match_percentage >= minMatch)
  }
  
  // Apply weight filters
  if (filters.value.weight_min) {
    filtered = filtered.filter(rec => {
      const weight = getNumericWeight(rec.arrow)
      return weight && weight >= parseFloat(filters.value.weight_min)
    })
  }
  
  if (filters.value.weight_max) {
    filtered = filtered.filter(rec => {
      const weight = getNumericWeight(rec.arrow)
      return weight && weight <= parseFloat(filters.value.weight_max)
    })
  }
  
  // Apply diameter range filter
  if (filters.value.diameter_range) {
    const [min, max] = filters.value.diameter_range.split('-').map(parseFloat)
    filtered = filtered.filter(rec => {
      const diameter = getNumericDiameter(rec.arrow)
      return diameter && diameter >= min && diameter <= max
    })
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
        return (b.compatibility_score || 0) - (a.compatibility_score || 0)
      case 'manufacturer':
        const manufacturerA = a.arrow.manufacturer || 'ZZZ' // Put nulls at end
        const manufacturerB = b.arrow.manufacturer || 'ZZZ'
        return manufacturerA.localeCompare(manufacturerB)
      case 'diameter_asc':
        return getNumericDiameter(a.arrow) - getNumericDiameter(b.arrow)
      case 'diameter_desc':
        return getNumericDiameter(b.arrow) - getNumericDiameter(a.arrow)
      case 'weight_asc':
        return getNumericWeight(a.arrow) - getNumericWeight(b.arrow)
      case 'weight_desc':
        return getNumericWeight(b.arrow) - getNumericWeight(a.arrow)
      case 'material':
        const materialA = a.arrow.material || 'ZZZ' // Put nulls at end
        const materialB = b.arrow.material || 'ZZZ'
        return materialA.localeCompare(materialB)
      case 'price':
        const priceA = a.arrow.price_range || 'ZZZ' // Put nulls at end
        const priceB = b.arrow.price_range || 'ZZZ'
        return priceA.localeCompare(priceB)
      default:
        return 0
    }
  })
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredRecommendations.value.length / perPage))

const paginatedRecommendations = computed(() => {
  const start = (currentPage.value - 1) * perPage
  const end = start + perPage
  return filteredRecommendations.value.slice(start, end)
})

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
  return 'N/A'
}

const getNumericSpine = (arrow) => {
  return arrow.min_spine || 0
}

const getNumericWeight = (arrow) => {
  return arrow.matched_gpi || arrow.min_gpi || arrow.spine_specification?.gpi_weight || 0
}

const getNumericDiameter = (arrow) => {
  // Prioritize matched diameters, then fall back to ranges
  const matchedInnerDiameter = arrow.matched_inner_diameter
  const matchedOuterDiameter = arrow.matched_outer_diameter
  const innerDiameter = arrow.min_inner_diameter || arrow.spine_specification?.inner_diameter
  const outerDiameter = arrow.min_outer_diameter || arrow.spine_specification?.outer_diameter
  
  return matchedInnerDiameter || matchedOuterDiameter || innerDiameter || outerDiameter || 0
}

const clearFilters = () => {
  filters.value = {
    search: '',
    manufacturer: '',
    match_quality: '',
    weight_min: '',
    weight_max: '',
    diameter_range: '',
    diameter_min: '',
    diameter_max: ''
  }
  currentPage.value = 1
}

const openArrowDetails = (arrow) => {
  // Navigate to arrow details page
  navigateTo(`/arrows/${arrow.id}`)
}

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

const loadRecommendations = async () => {
  if (pending.value) return

  pending.value = true
  error.value = null

  try {
    const result = await api.apiRequest('/tuning/recommendations', {
      method: 'POST',
      body: JSON.stringify({
        draw_weight: bowConfig.value.draw_weight,
        draw_length: bowConfig.value.draw_length,
        bow_type: bowConfig.value.bow_type,
        arrow_length: bowConfig.value.arrow_length,
        point_weight: bowConfig.value.point_weight,
        arrow_material: bowConfig.value.arrow_material,
        shooting_style: 'target',
        experience_level: 'intermediate',
        primary_goal: 'maximum_accuracy',
        arrow_type: 'target_outdoor'
      })
    })

    recommendations.value = result.recommended_arrows || []
    console.log('Loaded recommendations:', recommendations.value.length, 'arrows')
    if (recommendations.value.length > 0) {
      console.log('Sample recommendation:', recommendations.value[0])
    }

  } catch (err) {
    error.value = err
    console.error('Error loading recommendations:', err)
  } finally {
    pending.value = false
  }
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
  })
}, { deep: true })

// Watch for filter changes
watch(() => filters.value, () => {
  currentPage.value = 1
}, { deep: true })

// Initial load
onMounted(() => {
  loadManufacturers() // Load manufacturers first
  loadRecommendations()
})
</script>