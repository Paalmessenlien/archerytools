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

    <!-- Comparison Bar -->
    <div v-if="comparisonArrows.length > 0" class="mb-6">
      <md-elevated-card class="!bg-blue-50 dark:!bg-blue-900/20 border border-blue-200 dark:border-blue-800">
        <div class="p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <i class="fas fa-balance-scale text-blue-600 text-lg"></i>
              <div>
                <h3 class="font-medium text-blue-900 dark:text-blue-100">
                  {{ comparisonArrows.length }} Arrow{{ comparisonArrows.length > 1 ? 's' : '' }} Selected for Comparison
                </h3>
                <p class="text-sm text-blue-700 dark:text-blue-300">
                  {{ comparisonArrows.map(a => `${a.manufacturer} ${a.model_name}`).join(', ') }}
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <md-filled-button 
                @click="openComparison"
                :disabled="comparisonArrows.length < 2"
                class="bg-blue-600 text-white hover:bg-blue-700"
              >
                <i class="fas fa-chart-bar" style="margin-right: 6px;"></i>
                Compare ({{ comparisonArrows.length }})
              </md-filled-button>
              <md-text-button @click="clearComparison" class="text-blue-600 hover:bg-blue-100">
                <i class="fas fa-times" style="margin-right: 6px;"></i>
                Clear
              </md-text-button>
            </div>
          </div>
        </div>
      </md-elevated-card>
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

    <!-- Filters & Controls (Always Visible) -->
    <div v-if="!pending">
      <!-- Filters & Controls -->
      <md-elevated-card class="mb-6">
        <div class="p-6">
          <!-- Basic Filters Row -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <!-- Manufacturer Filter -->
            <md-filled-select :value="filters.manufacturer" @change="arrowFiltersStore.updateFilter('manufacturer', $event.target.value)" label="Manufacturer">
              <md-select-option value="">
                <div slot="headline">All Manufacturers</div>
              </md-select-option>
              <md-select-option v-for="mfr in availableManufacturers" :key="mfr" :value="mfr">
                <div slot="headline">{{ mfr }}</div>
              </md-select-option>
            </md-filled-select>
            
            <!-- Match Quality Filter -->
            <md-filled-select :value="filters.match_quality" @change="arrowFiltersStore.updateFilter('match_quality', $event.target.value)" label="Match Quality">
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
          </div>
        
          <!-- Advanced Filters Toggle -->
          <div class="flex items-center justify-between">
            <md-text-button @click="arrowFiltersStore.toggleAdvancedFilters()">
              <i class="fas transition-transform" :class="showAdvancedFilters ? 'fa-chevron-up rotate-180' : 'fa-chevron-down'" style="margin-right: 8px;"></i>
              {{ showAdvancedFilters ? 'Hide' : 'Show' }} Advanced Filters
            </md-text-button>
            
            <div class="flex items-center gap-4">
              <!-- Clear Filters Button -->
              <md-text-button 
                v-if="hasActiveFilters" 
                @click="handleClearFilters"
                class="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900"
              >
                <i class="fas fa-times-circle" style="margin-right: 6px;"></i>
                Clear Filters
              </md-text-button>
              
              <div class="text-sm text-gray-600">
                Showing {{ filteredRecommendations.length }} arrows
                <span v-if="recommendedSpine" class="ml-2 font-medium text-primary">
                  (Target Spine: {{ recommendedSpine }})
                </span>
              </div>
            </div>
          </div>
        
          <!-- Advanced Filters -->
          <div v-if="showAdvancedFilters" class="mt-6 pt-4">
            <md-divider class="mb-4"></md-divider>
            
            <!-- Search Bar -->
            <div class="mb-4">
              <md-outlined-text-field 
                :value="filters.search"
                @input="arrowFiltersStore.updateFilter('search', $event.target.value)"
                label="Search arrows..."
                type="search"
                class="w-full"
              >
                <i class="fas fa-search" slot="leading-icon" style="color: #6b7280;"></i>
              </md-outlined-text-field>
            </div>
            
            <!-- Sort By -->
            <div class="mb-4">
              <md-filled-select :value="sortBy" @change="arrowFiltersStore.updateFilter('sortBy', $event.target.value)" label="Sort By" class="w-full md:w-1/2">
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
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <!-- Diameter Range Dropdown -->
              <md-filled-select :value="filters.diameter_range" @change="arrowFiltersStore.updateFilter('diameter_range', $event.target.value)" label="Diameter Range">
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
                @input="arrowFiltersStore.updateFilter('weight_min', $event.target.value)"
                type="number" 
                step="0.1"
                label="Min Weight (GPI)"
              ></md-outlined-text-field>
              <md-outlined-text-field 
                :value="filters.weight_max"
                @input="arrowFiltersStore.updateFilter('weight_max', $event.target.value)"
                type="number" 
                step="0.1"
                label="Max Weight (GPI)"
              ></md-outlined-text-field>
            </div>
          </div>
        </div>
      </md-elevated-card>
      
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
                  <md-assist-chip :label="`Total: ${calculateTotalArrowWeight(recommendation.arrow, bowConfig.arrow_length)} gn`" class="bg-blue-100 dark:bg-blue-900">
                    <i class="fas fa-balance-scale fa-icon" slot="icon" style="color: #3b82f6;"></i>
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
                  
                  <md-filled-button size="small" @click="viewArrowDetails(recommendation.arrow.id)">
                    <i class="fas fa-eye" style="margin-right: 6px;"></i>
                    View Details
                  </md-filled-button>
                  <md-text-button 
                    size="small" 
                    @click="addToComparison(recommendation)"
                    :class="{ 'text-blue-600 dark:text-blue-400': isInComparison(recommendation.arrow) }"
                  >
                    <i 
                      class="fas" 
                      :class="isInComparison(recommendation.arrow) ? 'fa-check-circle' : 'fa-plus-circle'" 
                      style="margin-right: 6px;"
                    ></i>
                    {{ isInComparison(recommendation.arrow) ? 'Added to Compare' : 'Add to Compare' }}
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
      
      <!-- Load More Button -->
      <div v-if="hasMoreResults" class="flex flex-col items-center justify-center mt-8 mb-4">
        <div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Showing {{ paginatedRecommendations.length }} of {{ filteredRecommendations.length }} arrows
        </div>
        <md-filled-button 
          @click="loadMoreResults"
          :disabled="loadingMore"
          class="bg-primary-600 hover:bg-primary-700"
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
    </div> <!-- End Filters & Controls (Always Visible) -->

    <!-- Arrow Comparison Modal -->
    <div v-if="showComparisonModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        <!-- Modal Header -->
        <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
                <i class="fas fa-balance-scale mr-2 text-blue-600"></i>
                Arrow Comparison
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Comparing {{ comparisonArrows.length }} arrows side by side
              </p>
            </div>
            <md-text-button @click="closeComparison" class="text-gray-600 hover:bg-gray-100">
              <i class="fas fa-times"></i>
            </md-text-button>
          </div>
        </div>

        <!-- Comparison Content -->
        <div class="p-6">
          <div class="overflow-x-auto">
            <table class="w-full min-w-max">
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700">
                  <th class="text-left py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Specification</th>
                  <th v-for="arrow in comparisonArrows" :key="arrow.id" class="text-center py-3 px-4 min-w-48">
                    <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ arrow.manufacturer }}
                    </div>
                    <div class="text-xs text-gray-600 dark:text-gray-400">
                      {{ arrow.model_name }}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <!-- Match Score -->
                <tr>
                  <td class="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Match Score</td>
                  <td v-for="arrow in comparisonArrows" :key="`${arrow.id}-match`" class="py-3 px-4 text-center">
                    <div class="text-lg font-bold text-blue-600">
                      {{ arrow.recommendation_data?.match_percentage || 0 }}%
                    </div>
                    <div class="w-16 mx-auto mt-1">
                      <md-linear-progress 
                        :value="(arrow.recommendation_data?.match_percentage || 0) / 100"
                      ></md-linear-progress>
                    </div>
                  </td>
                </tr>
                
                <!-- Spine Range -->
                <tr>
                  <td class="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Spine Range</td>
                  <td v-for="arrow in comparisonArrows" :key="`${arrow.id}-spine`" class="py-3 px-4 text-center text-sm">
                    {{ getSpineDisplay(arrow) }}
                  </td>
                </tr>
                
                <!-- Diameter -->
                <tr>
                  <td class="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Diameter</td>
                  <td v-for="arrow in comparisonArrows" :key="`${arrow.id}-diameter`" class="py-3 px-4 text-center text-sm">
                    {{ getDiameterDisplay(arrow) }}"
                  </td>
                </tr>
                
                <!-- Weight (GPI) -->
                <tr>
                  <td class="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Weight (GPI)</td>
                  <td v-for="arrow in comparisonArrows" :key="`${arrow.id}-weight`" class="py-3 px-4 text-center text-sm">
                    {{ getWeightDisplay(arrow) }}
                  </td>
                </tr>
                
                <!-- Material -->
                <tr>
                  <td class="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Material</td>
                  <td v-for="arrow in comparisonArrows" :key="`${arrow.id}-material`" class="py-3 px-4 text-center text-sm">
                    {{ arrow.material || 'N/A' }}
                  </td>
                </tr>
                
                <!-- Arrow Type -->
                <tr>
                  <td class="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Arrow Type</td>
                  <td v-for="arrow in comparisonArrows" :key="`${arrow.id}-type`" class="py-3 px-4 text-center text-sm">
                    {{ arrow.arrow_type || 'N/A' }}
                  </td>
                </tr>
                
                <!-- Price Range -->
                <tr>
                  <td class="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Price Range</td>
                  <td v-for="arrow in comparisonArrows" :key="`${arrow.id}-price`" class="py-3 px-4 text-center text-sm">
                    {{ arrow.price_range || 'N/A' }}
                  </td>
                </tr>
                
                <!-- Compatibility Reasons -->
                <tr>
                  <td class="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">Why It Matches</td>
                  <td v-for="arrow in comparisonArrows" :key="`${arrow.id}-reasons`" class="py-3 px-4 text-center">
                    <div class="text-xs text-gray-600 dark:text-gray-400 max-w-36 mx-auto">
                      {{ arrow.recommendation_data?.reasons?.join(', ') || 'Compatible with your setup' }}
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Actions -->
          <div class="mt-6 flex justify-between items-center">
            <md-text-button @click="clearComparison" class="text-red-600 hover:bg-red-50">
              <i class="fas fa-trash mr-2"></i>
              Clear All
            </md-text-button>
            <div class="flex space-x-3">
              <md-outlined-button @click="closeComparison">
                Close
              </md-outlined-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'
import { useArrowFiltersStore } from '~/stores/arrowFilters'

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
const emit = defineEmits(['arrow-added-to-setup', 'error'])

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
      case 'price':
        const priceA = a.arrow.price_range || 'ZZZ' // Put nulls at end
        const priceB = b.arrow.price_range || 'ZZZ'
        const priceComparison = priceA.localeCompare(priceB)
        // Secondary sort by match score if prices are equal
        if (priceComparison === 0) {
          return (b.match_percentage || b.compatibility_score || 0) - (a.match_percentage || a.compatibility_score || 0)
        }
        return priceComparison
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
  // Handle different data structures - recommendations vs database arrows
  if (arrow.matched_gpi) return arrow.matched_gpi
  if (arrow.min_gpi) return arrow.min_gpi
  if (arrow.max_gpi) return arrow.max_gpi
  
  // Check spine_specifications array for GPI weight
  if (arrow.spine_specifications && arrow.spine_specifications.length > 0) {
    const spec = arrow.spine_specifications[0]
    if (spec.gpi_weight) return spec.gpi_weight
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

const handleClearFilters = () => {
  arrowFiltersStore.clearFilters()
  currentPage.value = 1
}

const clearFilters = () => {
  handleClearFilters()
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

// Calculate total arrow weight based on GPI and arrow length
const calculateTotalArrowWeight = (arrow, arrowLength, componentWeights = {}) => {
  if (!arrow || !arrow.spine_specifications) return 0
  
  // Find the appropriate spine specification (use first one if no specific match)
  const spineSpec = arrow.spine_specifications[0]
  if (!spineSpec || !spineSpec.gpi_weight) return 0
  
  // Use provided arrow length or default to 32" if no length options available
  let effectiveLength = arrowLength || 32
  
  // If arrow has specific length options, use the closest one
  if (spineSpec.length_options && spineSpec.length_options.length > 0) {
    // Find the closest available length
    const targetLength = arrowLength || 32
    effectiveLength = spineSpec.length_options.reduce((prev, curr) => 
      Math.abs(curr - targetLength) < Math.abs(prev - targetLength) ? curr : prev
    )
  }
  
  // Calculate shaft weight (GPI * length in inches)
  const shaftWeight = spineSpec.gpi_weight * effectiveLength
  
  // Add component weights
  const pointWeight = componentWeights.point_weight || bowConfig.value.point_weight || 125
  const insertWeight = componentWeights.insert_weight || bowConfig.value.insert_weight || 0
  const nockWeight = componentWeights.nock_weight || bowConfig.value.nock_weight || 10
  const bushingWeight = componentWeights.bushing_weight || bowConfig.value.bushing_weight || 0
  const vaneWeightPerVane = componentWeights.vane_weight_per || calculateVaneWeight()
  const numberOfVanes = componentWeights.number_of_vanes || bowConfig.value.number_of_vanes || 3
  
  const totalVaneWeight = vaneWeightPerVane * numberOfVanes
  
  // Total arrow weight = shaft + components
  const totalWeight = shaftWeight + pointWeight + insertWeight + nockWeight + bushingWeight + totalVaneWeight
  
  return Math.round(totalWeight * 10) / 10 // Round to 1 decimal place
}

const addToSetup = async (recommendation) => {
  if (!props.selectedBowSetup) {
    emit('error', 'No bow setup selected')
    return
  }

  try {
    const { useAuth } = await import('~/composables/useAuth')
    const { addArrowToSetup } = useAuth()

    // Prepare the arrow data for adding to setup
    const arrowData = {
      arrow_id: recommendation.arrow.id,
      arrow_length: bowConfig.value.arrow_length || 29,
      point_weight: bowConfig.value.point_weight || 125,
      calculated_spine: recommendation.spine_calculation?.calculated_spine || bowConfig.value.calculated_spine,
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
    await addArrowToSetup(props.selectedBowSetup.id, arrowData)

    // Emit event to parent component
    emit('arrow-added-to-setup', {
      arrow: recommendation.arrow,
      setup: props.selectedBowSetup,
      arrowData
    })

  } catch (error) {
    console.error('Error adding arrow to setup:', error)
    emit('error', 'Failed to add arrow to setup. Please try again.')
  }
}

const viewArrowDetails = (arrowId) => {
  // Navigate to arrow details page
  navigateTo(`/arrows/${arrowId}`)
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
        limit: 200  // Request more recommendations for progressive loading
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
      console.log('Loaded recommendations:', recommendations.value.length, 'arrows')
      
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
  
  loadManufacturers() // Load manufacturers first
  loadRecommendations()
})
</script>