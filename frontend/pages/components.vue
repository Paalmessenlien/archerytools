<template>
  <div>
    <!-- Beta Notice Banner -->
    <div class="mb-6 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-flask text-orange-600 dark:text-orange-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200">Beta Testing Phase</h4>
          <p class="text-xs text-orange-700 dark:text-orange-300 mt-1">
            Component database is in beta. Functionality may be limited and data may be incomplete.
          </p>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Components</h1>
      <p class="text-gray-600 dark:text-gray-300">
        Browse arrow components including points, nocks, fletchings, and inserts
      </p>
    </div>

    <!-- Stats Overview -->
    <div v-if="statistics" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div v-for="category in statistics.categories" :key="category.name" class="card text-center">
        <div class="text-2xl font-bold text-blue-600 dark:text-purple-400">
          {{ category.count }}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400 capitalize">
          {{ category.name }}
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Filters</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Category Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Component Type
          </label>
          <select 
            v-model="filters.category" 
            @change="filterComponents"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          >
            <option value="">All Components</option>
            <option v-for="category in availableCategories" :key="category" :value="category">
              {{ category && category.length > 0 ? category.charAt(0).toUpperCase() + category.slice(1) : 'Unknown' }}
            </option>
          </select>
        </div>

        <!-- Manufacturer Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Manufacturer
          </label>
          <select 
            v-model="filters.manufacturer" 
            @change="filterComponents"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          >
            <option value="">All Manufacturers</option>
            <option v-for="manufacturer in availableManufacturers" :key="manufacturer" :value="manufacturer">
              {{ manufacturer }}
            </option>
          </select>
        </div>

        <!-- Sort Order -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Sort By
          </label>
          <select 
            v-model="sortBy" 
            @change="sortComponents"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          >
            <option value="manufacturer">Manufacturer</option>
            <option value="model_name">Model Name</option>
            <option value="category">Category</option>
            <option value="created_at">Date Added</option>
          </select>
        </div>
      </div>

      <!-- Search -->
      <div class="mt-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Search Components
        </label>
        <input 
          v-model="searchQuery"
          @input="debounceSearch"
          type="text" 
          placeholder="Search by name, manufacturer, or specifications..."
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400"></div>
      <span class="ml-3 text-gray-600 dark:text-gray-400">Loading components...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
      <div class="flex items-center space-x-3">
        <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <div>
          <h3 class="text-red-800 dark:text-red-200 font-medium">Error Loading Components</h3>
          <p class="text-red-600 dark:text-red-300 text-sm">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Components List -->
    <div v-else>
      <!-- Results Summary -->
      <div class="mb-4 flex justify-between items-center">
        <p class="text-gray-600 dark:text-gray-400">
          Showing {{ filteredComponents.length }} of {{ totalComponents }} components
        </p>
        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-600 dark:text-gray-400">Per page:</span>
          <select 
            v-model="limit" 
            @change="updateLimit"
            class="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          >
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>

      <!-- Component Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="component in paginatedComponents" 
          :key="component.id" 
          class="card hover:shadow-lg transition-shadow duration-200"
        >
          <!-- Component Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 leading-tight">
                {{ component.model_name }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ component.manufacturer }}
              </p>
            </div>
            <span class="badge" :class="getCategoryBadgeClass(component.category_name)">
              {{ component.category_name }}
            </span>
          </div>

          <!-- Component Image -->
          <div v-if="component.image_url" class="mb-3">
            <img 
              :src="component.image_url" 
              :alt="component.model_name"
              class="w-full h-32 object-cover rounded-lg bg-gray-100 dark:bg-gray-700"
              @error="handleImageError"
            />
          </div>

          <!-- Specifications -->
          <div v-if="component.specifications && Object.keys(component.specifications).length > 0" class="mb-3">
            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Specifications</h4>
            <div class="space-y-1">
              <div 
                v-for="(value, key) in component.specifications" 
                :key="key"
                class="flex justify-between text-sm"
              >
                <span class="text-gray-600 dark:text-gray-400 capitalize">
                  {{ key.replace(/_/g, ' ') }}:
                </span>
                <span class="text-gray-900 dark:text-gray-100 font-medium">
                  {{ formatSpecValue(value) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div v-if="component.description" class="mb-3">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ component.description }}
            </p>
          </div>

          <!-- Price -->
          <div v-if="component.price_range" class="mb-3">
            <span class="text-sm font-medium text-green-600 dark:text-green-400">
              {{ component.price_range }}
            </span>
          </div>

          <!-- Footer -->
          <div class="flex justify-between items-center pt-3 border-t border-gray-200 dark:border-gray-700">
            <span class="text-xs text-gray-500 dark:text-gray-400">
              Added {{ formatDate(component.created_at) }}
            </span>
            <CustomButton
              @click="viewCompatibleArrows(component)"
              variant="outlined"
              size="small"
              class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-purple-400 dark:border-purple-400 dark:hover:bg-purple-900/20"
            >
              View Compatible Arrows
            </CustomButton>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-if="filteredComponents.length === 0" class="text-center py-12">
        <svg class="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <rect x="3" y="3" width="7" height="7"/>
          <rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Components Found</h3>
        <p class="text-gray-600 dark:text-gray-400">
          Try adjusting your filters or search terms to find components.
        </p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-8 flex justify-center">
        <nav class="flex items-center space-x-2">
          <CustomButton
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage <= 1"
            variant="outlined"
            size="small"
          >
            Previous
          </CustomButton>
          
          <span class="text-sm text-gray-600 dark:text-gray-400 px-3">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          
          <CustomButton
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage >= totalPages"
            variant="outlined"
            size="small"
          >
            Next
          </CustomButton>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import type { ComponentData, ComponentStatistics } from '~/types/arrow'

// Meta
useHead({
  title: 'Components - ArrowTune Beta',
  meta: [
    { name: 'description', content: 'Browse arrow components including points, nocks, fletchings, and inserts (Beta)' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})

// API composable
const { getComponents, getComponentStatistics } = useApi()

// State
const components = ref<ComponentData[]>([])
const statistics = ref<ComponentStatistics | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

// Filters
const filters = ref({
  category: '',
  manufacturer: ''
})
const searchQuery = ref('')
const sortBy = ref('manufacturer')
const limit = ref(50)

// Pagination
const currentPage = ref(1)
const itemsPerPage = 25

// Computed
const availableCategories = computed(() => {
  if (!statistics.value?.categories) return []
  return statistics.value.categories
    .filter(cat => cat.count > 0)
    .map(cat => cat.name)
    .sort()
})

const availableManufacturers = computed(() => {
  const manufacturers = [...new Set(components.value.map(c => c.manufacturer))]
  return manufacturers.filter(Boolean).sort()
})

const filteredComponents = computed(() => {
  let filtered = [...components.value]

  // Apply filters
  if (filters.value.category) {
    filtered = filtered.filter(c => c.category_name === filters.value.category)
  }
  
  if (filters.value.manufacturer) {
    filtered = filtered.filter(c => c.manufacturer === filters.value.manufacturer)
  }

  // Apply search
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(component => {
      const searchableText = [
        component.model_name,
        component.manufacturer,
        component.description,
        Object.values(component.specifications || {}).join(' ')
      ].join(' ').toLowerCase()
      
      return searchableText.includes(query)
    })
  }

  // Apply sorting
  filtered.sort((a, b) => {
    let aVal = a[sortBy.value] || ''
    let bVal = b[sortBy.value] || ''
    
    if (sortBy.value === 'created_at') {
      return new Date(bVal) - new Date(aVal) // Newest first
    }
    
    return aVal.toString().localeCompare(bVal.toString())
  })

  return filtered
})

const totalComponents = computed(() => components.value.length)

const paginatedComponents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredComponents.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredComponents.value.length / itemsPerPage)
})

// Methods
const fetchComponents = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    console.log('🔄 Fetching components with limit:', limit.value)
    
    const response = await getComponents({
      limit: limit.value
    })
    
    console.log('📦 Component response:', response)
    
    if (response?.components) {
      components.value = response.components
      console.log('✅ Loaded components:', components.value.length)
    } else {
      console.log('⚠️ No components in response')
      error.value = 'No components found in response'
    }
  } catch (err) {
    console.error('❌ Error fetching components:', err)
    console.error('Error details:', {
      message: err.message,
      stack: err.stack,
      cause: err.cause
    })
    error.value = `Failed to load components: ${err.message}`
  } finally {
    isLoading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    console.log('📊 Fetching component statistics...')
    const response = await getComponentStatistics()
    console.log('📊 Statistics response:', response)
    
    if (response) {
      statistics.value = response
      console.log('✅ Loaded statistics:', statistics.value.total_components, 'total components')
    } else {
      console.log('⚠️ No statistics in response')
    }
  } catch (err) {
    console.error('❌ Error fetching component statistics:', err)
    console.error('Statistics error details:', {
      message: err.message,
      stack: err.stack
    })
  }
}

const filterComponents = () => {
  currentPage.value = 1 // Reset to first page when filtering
}

const sortComponents = () => {
  currentPage.value = 1 // Reset to first page when sorting
}

const updateLimit = async () => {
  currentPage.value = 1
  await fetchComponents()
}

// Debounced search
let searchTimeout
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
  }, 300)
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const getCategoryBadgeClass = (category) => {
  const classes = {
    'points': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'nocks': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'fletchings': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'inserts': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'strings': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    'rests': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
    'accessories': 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
  }
  return classes[category] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
}

const formatSpecValue = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return value
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
}

const viewCompatibleArrows = (component) => {
  // TODO: Implement component-to-arrow compatibility view
  // This could navigate to a new page or open a modal
  console.log('View compatible arrows for:', component)
  // For now, we could navigate to the arrows page with a filter
  navigateTo(`/database?compatible_with=${component.id}`)
}

// Watch for filter changes to reset pagination
watch([filters, searchQuery, sortBy], () => {
  currentPage.value = 1
}, { deep: true })

// Initialize
onMounted(async () => {
  await Promise.all([
    fetchComponents(),
    fetchStatistics()
  ])
})
</script>