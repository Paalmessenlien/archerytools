<template>
  <div>
    <!-- Beta Notice Banner -->
    <div class="mb-6 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-flask text-orange-600 dark:text-orange-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200">Beta Testing Phase</h4>
          <p class="text-xs text-orange-700 dark:text-orange-300 mt-1">
            Arrow database is in beta. Data may be incomplete and subject to updates.
          </p>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Arrow Database</h1>
      <p class="text-gray-600 dark:text-gray-300">Browse and search our comprehensive arrow database</p>
    </div>

    <!-- Database Stats -->
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <md-elevated-card class="text-center light-surface light-elevation">
        <div class="p-6">
          <div class="text-2xl font-bold text-indigo-600 mb-2">
            <i class="fas fa-bullseye" style="margin-right: 8px; color: #6366f1;"></i>
            {{ stats.total_arrows }}
          </div>
          <div class="text-sm text-gray-600">Total Arrows</div>
        </div>
      </md-elevated-card>
      <md-elevated-card class="text-center light-surface light-elevation">
        <div class="p-6">
          <div class="text-2xl font-bold text-green-600 mb-2">
            <i class="fas fa-industry" style="margin-right: 8px; color: #059669;"></i>
            {{ stats.total_manufacturers }}
          </div>
          <div class="text-sm text-gray-600">Manufacturers</div>
        </div>
      </md-elevated-card>
      <md-elevated-card class="text-center light-surface light-elevation">
        <div class="p-6">
          <div class="text-2xl font-bold text-purple-600 mb-2">
            <i class="fas fa-ruler-horizontal" style="margin-right: 8px; color: #7c3aed;"></i>
            {{ stats.spine_range.max - stats.spine_range.min }}
          </div>
          <div class="text-sm text-gray-600">Spine Range</div>
        </div>
      </md-elevated-card>
      <md-elevated-card class="text-center light-surface light-elevation">
        <div class="p-6">
          <div class="text-2xl font-bold text-orange-600 mb-2">
            <i class="fas fa-dot-circle" style="margin-right: 8px; color: #ea580c;"></i>
            {{ (stats.diameter_range.max - stats.diameter_range.min).toFixed(3) }}
          </div>
          <div class="text-sm text-gray-600">Diameter Range</div>
        </div>
      </md-elevated-card>
    </div>

    <!-- Search and Filters -->
    <md-elevated-card class="mb-6 light-surface light-elevation">
      <div class="p-6">
        <!-- Main Search Field -->
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
        
        <!-- Basic Filter Dropdowns -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <md-filled-select :value="filters.manufacturer" @change="handleFilterChange('manufacturer', $event.target.value)" label="Manufacturer">
            <md-select-option value="">
              <div slot="headline">All Manufacturers</div>
            </md-select-option>
            <md-select-option v-for="mfr in manufacturers" :key="mfr.manufacturer" :value="mfr.manufacturer">
              <div slot="headline">{{ mfr.manufacturer }} ({{ mfr.arrow_count }})</div>
            </md-select-option>
          </md-filled-select>
          
          <md-filled-select :value="filters.arrow_type" @change="handleFilterChange('arrow_type', $event.target.value)" label="Arrow Type">
            <md-select-option value="">
              <div slot="headline">All Types</div>
            </md-select-option>
            <md-select-option v-for="arrowType in arrowTypes" :key="arrowType.arrow_type" :value="arrowType.arrow_type">
              <div slot="headline">{{ formatArrowType(arrowType.arrow_type) }} ({{ arrowType.count }})</div>
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
        </div>
      
        <!-- Advanced Filters Toggle -->
        <div class="mt-4">
          <md-text-button @click="showAdvancedFilters = !showAdvancedFilters">
            <i class="fas transition-transform" :class="showAdvancedFilters ? 'fa-chevron-up rotate-180' : 'fa-chevron-down'" style="margin-right: 8px;"></i>
            {{ showAdvancedFilters ? 'Hide' : 'Show' }} Advanced Filters
          </md-text-button>
        </div>
      
        <!-- Advanced Filters -->
        <div v-if="showAdvancedFilters" class="mt-4 pt-4">
          <md-divider class="mb-4"></md-divider>
          
          <!-- Row 1: Spine Range + Diameter Range ---->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <md-outlined-text-field 
              :value="filters.spine_min"
              @input="handleAdvancedFilterChange('spine_min', $event.target.value)"
              type="number" 
              label="Min Spine"
            ></md-outlined-text-field>
            
            <md-outlined-text-field 
              :value="filters.spine_max"
              @input="handleAdvancedFilterChange('spine_max', $event.target.value)"
              type="number" 
              label="Max Spine"
            ></md-outlined-text-field>
            
            <md-filled-select :value="filters.diameter_range" @change="handleFilterChange('diameter_range', $event.target.value)" label="Diameter Range">
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
          </div>
          
          <!-- Row 2: Weight Range ---->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <md-outlined-text-field 
              :value="filters.gpi_min"
              @input="handleAdvancedFilterChange('gpi_min', $event.target.value)"
              type="number" 
              step="0.1"
              label="Min Weight (GPI)"
            ></md-outlined-text-field>
            
            <md-outlined-text-field 
              :value="filters.gpi_max"
              @input="handleAdvancedFilterChange('gpi_max', $event.target.value)"
              type="number" 
              step="0.1"
              label="Max Weight (GPI)"
            ></md-outlined-text-field>
            
            <!-- Empty slot for 3-column alignment -->
            <div></div>
          </div>
          
          <div class="mt-4 flex justify-end">
            <md-outlined-button @click="clearFilters">
              <i class="fas fa-broom" style="margin-right: 6px;"></i>
              Clear Filters
            </md-outlined-button>
          </div>
        </div>
      </div>
    </md-elevated-card>

    <!-- Results Header -->
    <div class="flex items-center justify-between mb-4">
      <p class="text-sm text-gray-600">
        {{ searchPerformed ? `Showing ${arrows.length} of ${totalArrows} arrows` : `${totalArrows} arrows available` }}
      </p>
      <div class="flex items-center space-x-2">
        <label for="per-page" class="text-sm text-gray-600">Show:</label>
        <select 
          id="per-page"
          v-model="perPage" 
          @change="searchArrows"
          class="text-sm border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
        >
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-4">
      <div v-for="i in perPage" :key="i">
        <md-elevated-card class="animate-pulse light-surface">
          <div class="p-6 space-y-3">
            <div class="flex justify-between items-start">
              <div class="space-y-2">
                <div class="h-5 bg-gray-200 rounded w-48"></div>
                <div class="h-4 bg-gray-200 rounded w-32"></div>
              </div>
              <div class="h-4 bg-gray-200 rounded w-20"></div>
            </div>
            <div class="grid grid-cols-4 gap-4">
              <div class="h-4 bg-gray-200 rounded"></div>
              <div class="h-4 bg-gray-200 rounded"></div>
              <div class="h-4 bg-gray-200 rounded"></div>
              <div class="h-4 bg-gray-200 rounded"></div>
            </div>
          </div>
        </md-elevated-card>
      </div>
    </div>

    <!-- Error State -->
    <md-elevated-card v-else-if="error" class="text-center light-surface light-elevation">
      <div class="p-12">
        <div class="text-red-500 mb-4">
          <i class="fas fa-exclamation-triangle text-6xl"></i>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Arrows</h3>
        <p class="text-gray-600 mb-4">{{ error.message || 'Failed to load arrow database.' }}</p>
        <md-filled-button @click="searchArrows">
          <i class="fas fa-redo-alt" style="margin-right: 6px;"></i>
          Try Again
        </md-filled-button>
      </div>
    </md-elevated-card>

    <!-- No Results -->
    <md-elevated-card v-else-if="arrows.length === 0 && searchPerformed" class="text-center light-surface light-elevation">
      <div class="p-12">
        <div class="text-gray-400 mb-4">
          <i class="fas fa-search-minus text-6xl"></i>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Arrows Found</h3>
        <p class="text-gray-600 mb-4">No arrows match your search criteria.</p>
        <md-filled-button @click="clearFilters">
          <i class="fas fa-broom" style="margin-right: 6px;"></i>
          Clear Filters
        </md-filled-button>
      </div>
    </md-elevated-card>

    <!-- Arrow Results -->
    <div v-else class="space-y-4">
      <md-elevated-card 
        v-for="arrow in arrows" 
        :key="arrow.id"
        class="cursor-pointer card-interactive light-surface light-elevation"
        @click="viewArrowDetails(arrow)"
      >
        <div class="p-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">
              {{ arrow.manufacturer }} {{ arrow.model_name }}
            </h3>
            <p class="text-gray-600">
              Spine: {{ getSpineDisplay(arrow) }}
            </p>
          </div>
          
          <div class="text-right">
            <p class="font-semibold text-blue-600">
              {{ arrow.price_range || 'Price varies' }}
            </p>
            <div v-if="arrow.arrow_type" class="text-xs text-gray-500 mt-1">
              {{ arrow.arrow_type }} arrow
            </div>
          </div>
        </div>
        
          <!-- Arrow Specifications as Chips -->
          <md-chip-set class="mb-4">
            <md-assist-chip :label="'⌀ ' + getDiameterRange(arrow) + '&quot;'">
              <i class="fas fa-dot-circle fa-icon" slot="icon" style="color: #dc2626;"></i>
            </md-assist-chip>
            <md-assist-chip :label="getGPIRange(arrow) + ' GPI'">
              <i class="fas fa-weight-hanging fa-icon" slot="icon" style="color: #7c2d12;"></i>
            </md-assist-chip>
            <md-assist-chip :label="arrow.material || 'Not specified'">
              <i class="fas fa-layer-group fa-icon" slot="icon" style="color: #059669;"></i>
            </md-assist-chip>
            <md-assist-chip :label="arrow.straightness_tolerance || 'Not specified'">
              <i class="fas fa-crosshairs fa-icon" slot="icon" style="color: #7c3aed;"></i>
            </md-assist-chip>
          </md-chip-set>

        <!-- Description -->
        <div v-if="arrow.description" class="text-sm text-gray-600 mb-4">
          {{ arrow.description }}
        </div>

          <!-- Tags -->
          <div class="flex flex-wrap gap-2">
            <span v-if="arrow.recommended_use" class="badge bg-blue-100 text-blue-800">
              {{ Array.isArray(arrow.recommended_use) ? arrow.recommended_use.join(', ') : arrow.recommended_use }}
            </span>
            <span v-if="arrow.carbon_content" class="badge bg-green-100 text-green-800">
              {{ arrow.carbon_content }}
            </span>
          </div>
        </div>
      </md-elevated-card>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center items-center space-x-4 pt-6">
        <md-outlined-button 
          :disabled="currentPage <= 1"
          @click="changePage(currentPage - 1)"
        >
          <i class="fas fa-chevron-left" style="margin-right: 6px;"></i>
          Previous
        </md-outlined-button>
        
        <div class="flex items-center space-x-2">
          <template v-for="page in paginationRange" :key="page">
            <md-filled-button
              v-if="page !== '...' && page === currentPage"
              @click="changePage(page)"
              size="small"
            >
              {{ page }}
            </md-filled-button>
            <md-outlined-button
              v-else-if="page !== '...'"
              @click="changePage(page)"
              size="small"
            >
              {{ page }}
            </md-outlined-button>
            <span v-else class="text-gray-500">...</span>
          </template>
        </div>
        
        <md-outlined-button 
          :disabled="currentPage >= totalPages"
          @click="changePage(currentPage + 1)"
        >
          Next
          <i class="fas fa-chevron-right" style="margin-left: 6px;"></i>
        </md-outlined-button>
      </div>
    </div>
  </div>
</template>

<script setup>
// API
const api = useApi()

// Reactive state
const arrows = ref([])
const stats = ref(null)
const manufacturers = ref([])
const arrowTypes = ref([])
const loading = ref(false)
const error = ref(null)
const searchPerformed = ref(false)
const showAdvancedFilters = ref(false)

// Pagination
const currentPage = ref(1)
const perPage = ref(20)
const totalArrows = ref(0)
const totalPages = ref(0)

// Filters
const filters = ref({
  search: '',
  manufacturer: '',
  arrow_type: '',
  material: '',
  spine_min: '',
  spine_max: '',
  diameter_range: '',
  diameter_min: '',
  diameter_max: '',
  gpi_min: '',
  gpi_max: ''
})

// Computed
const paginationRange = computed(() => {
  const range = []
  const delta = 2
  const rangeWithDots = []
  
  for (let i = Math.max(2, currentPage.value - delta); 
       i <= Math.min(totalPages.value - 1, currentPage.value + delta); 
       i++) {
    range.push(i)
  }
  
  if (currentPage.value - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }
  
  rangeWithDots.push(...range)
  
  if (currentPage.value + delta < totalPages.value - 1) {
    rangeWithDots.push('...', totalPages.value)
  } else if (totalPages.value > 1) {
    rangeWithDots.push(totalPages.value)
  }
  
  return rangeWithDots
})

// Methods
const searchArrows = async () => {
  loading.value = true
  error.value = null

  try {
    // Build filter object
    const searchFilters = {
      page: currentPage.value,
      per_page: perPage.value
    }

    // Add non-empty filters
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        // Handle diameter_range specially
        if (key === 'diameter_range' && value) {
          const [min, max] = value.split('-')
          searchFilters.diameter_min = parseFloat(min)
          searchFilters.diameter_max = parseFloat(max)
        } else if (key !== 'diameter_range') {
          searchFilters[key] = value
        }
      }
    })

    const result = await api.getArrows(searchFilters)
    
    arrows.value = result.arrows
    totalArrows.value = result.total
    totalPages.value = result.total_pages
    searchPerformed.value = true

  } catch (err) {
    error.value = err
    console.error('Error searching arrows:', err)
  } finally {
    loading.value = false
  }
}

const loadDatabaseStats = async () => {
  try {
    stats.value = await api.getDatabaseStats()
  } catch (err) {
    console.error('Error loading database stats:', err)
  }
}

const loadManufacturers = async () => {
  try {
    manufacturers.value = await api.getManufacturers()
  } catch (err) {
    console.error('Error loading manufacturers:', err)
  }
}

const clearFilters = () => {
  filters.value = {
    search: '',
    manufacturer: '',
    arrow_type: '',
    material: '',
    spine_min: '',
    spine_max: '',
    diameter_range: '',
    diameter_min: '',
    diameter_max: '',
    gpi_min: '',
    gpi_max: ''
  }
  currentPage.value = 1
  searchArrows()
}

const changePage = (page) => {
  currentPage.value = page
  searchArrows()
}

const viewArrowDetails = (arrow) => {
  // Navigate to arrow details page
  navigateTo(`/arrows/${arrow.id}`)
}

// Helper methods
const getSpineDisplay = (arrow) => {
  // Use the pre-formatted spine_display field if available (supports wood spine format)
  if (arrow.spine_display) {
    return arrow.spine_display
  }
  
  // Fallback for min/max spine range with proper formatting
  if (arrow.min_spine && arrow.max_spine) {
    const material = arrow.material?.toLowerCase() || ''
    if (material.includes('wood')) {
      // Wood arrows use traditional spine format
      return arrow.min_spine === arrow.max_spine 
        ? `${arrow.min_spine}#` 
        : `${arrow.min_spine}-${arrow.max_spine}#`
    } else {
      // Carbon/aluminum arrows use numbers
      return arrow.min_spine === arrow.max_spine 
        ? `${arrow.min_spine}` 
        : `${arrow.min_spine}-${arrow.max_spine}`
    }
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

// Enhanced search handling
const handleSearchInput = (value) => {
  filters.value.search = value
  if (value.length >= 3 || value.length === 0) {
    currentPage.value = 1
    debouncedSearch()
  }
}

const handleFilterChange = (filterName, value) => {
  filters.value[filterName] = value
  currentPage.value = 1
  searchArrows()
}

const handleAdvancedFilterChange = (filterName, value) => {
  filters.value[filterName] = value
  currentPage.value = 1
  debouncedAdvancedSearch()
}

// Create debounced functions
const debouncedSearch = debounce(() => {
  searchArrows()
}, 300)

const debouncedAdvancedSearch = debounce(() => {
  searchArrows()
}, 500)

// Debounce function
function debounce(func, wait) {
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

// Lifecycle
// Format arrow type for display
const formatArrowType = (arrowType) => {
  if (!arrowType) return 'Unknown'
  
  return arrowType
    .split(/[-_\s]+/)
    .filter(word => word && word.length > 0)
    .map(word => word && word.length > 0 ? word.charAt(0).toUpperCase() + word.slice(1).toLowerCase() : '')
    .filter(word => word.length > 0)
    .join(' ')
}

// Load arrow types
const loadArrowTypes = async () => {
  try {
    arrowTypes.value = await api.getArrowTypes()
  } catch (err) {
    console.error('Error loading arrow types:', err)
    arrowTypes.value = []
  }
}

onMounted(() => {
  loadDatabaseStats()
  loadManufacturers()
  loadArrowTypes()
  searchArrows()
})

// Set page title
useHead({
  title: 'Arrow Database - Beta',
  meta: [
    { name: 'description', content: 'Browse and search our comprehensive database of arrow specifications (Beta)' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})
</script>