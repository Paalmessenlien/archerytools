<template>
  <div>
    <!-- Loading State -->
    <div v-if="pending" class="space-y-3">
      <div v-for="i in limit" :key="i" class="animate-pulse">
        <div class="flex items-center justify-between p-4 bg-gray-100 rounded-lg">
          <div class="flex-1 space-y-2">
            <div class="h-4 bg-gray-200 rounded w-1/2"></div>
            <div class="h-3 bg-gray-200 rounded w-3/4"></div>
          </div>
          <div class="h-6 bg-gray-200 rounded w-16"></div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-500 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
      </div>
      <p class="text-gray-600 mb-4">Failed to load compatible arrows</p>
      <button @click="refresh()" class="btn-primary text-sm">
        Try Again
      </button>
    </div>

    <!-- No Compatible Arrows -->
    <div v-else-if="!compatibleArrows.length" class="text-center py-6">
      <div class="text-gray-400 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.034 0-3.9.785-5.291 2.073M6.343 6.343A8 8 0 0112 4a8 8 0 018 8 8 8 0 01-8 8 8 8 0 01-8-8 8 8 0 018-8z"/>
        </svg>
      </div>
      <p class="text-gray-600 text-sm">No arrows compatible with your current configuration.</p>
      <p class="text-xs text-gray-500 mt-1">Try adjusting your bow settings or arrow material.</p>
    </div>

    <!-- Compatible Arrows List -->
    <div v-else class="space-y-2">
      <div class="text-xs text-gray-500 mb-3">
        Showing {{ displayedArrows.length }} compatible arrow{{ displayedArrows.length !== 1 ? 's' : '' }} 
        (sorted by compatibility)
      </div>
      
      <div 
        v-for="arrow in displayedArrows" 
        :key="arrow.id"
        class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200"
      >
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-3">
            <div class="flex-1 min-w-0">
              <h4 class="font-medium text-gray-900 truncate">
                {{ arrow.manufacturer }} {{ arrow.model_name }}
              </h4>
              <p class="text-sm text-gray-600">
                {{ arrow.material }} • Spine: {{ getSpineDisplay(arrow) }} • {{ arrow.price_range || 'Price varies' }}
              </p>
            </div>
            
            <!-- Recommended Badge -->
            <div v-if="arrow.recommended" class="badge-success">
              Recommended
            </div>
          </div>
        </div>
        
        <!-- Compatibility Badge -->
        <div class="ml-3 flex-shrink-0">
          <span 
            class="badge"
            :class="{
              'badge-success': arrow.compatibility === 'excellent',
              'badge-warning': arrow.compatibility === 'good',
              'badge-error': arrow.compatibility === 'poor'
            }"
          >
            {{ arrow.compatibility }}
          </span>
        </div>
      </div>

      <!-- Show More Link -->
      <div v-if="compatibleArrows.length > limit" class="text-center pt-3">
        <p class="text-xs text-gray-500">
          + {{ compatibleArrows.length - limit }} more arrows available
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'

// Props
const props = withDefaults(defineProps(), {
  limit: 6
})

// Store
const bowConfigStore = useBowConfigStore()
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)

// API
const api = useApi()

// Reactive state
const compatibleArrows = ref([])
const pending = ref(false)
const error = ref(null)

// Computed
const displayedArrows = computed(() => {
  return compatibleArrows.value.slice(0, props.limit)
})

// Methods
const calculateCompatibility = (arrowSpine, recommendedSpine) => {
  if (!recommendedSpine) return 'poor'
  
  // Handle string spine ranges (traditional arrows)
  if (typeof recommendedSpine === 'string' && typeof arrowSpine === 'string') {
    try {
      const recSpineRange = recommendedSpine.split('-').map(s => parseInt(s))
      const arrowSpineRange = arrowSpine.split('-').map(s => parseInt(s))
      const recMin = recSpineRange[0], recMax = recSpineRange[1]
      const arrMin = arrowSpineRange[0], arrMax = arrowSpineRange[1]
      
      if (arrMin <= recMax && arrMax >= recMin) return 'excellent'
      if (Math.abs(recMin - arrMax) <= 5 || Math.abs(arrMin - recMax) <= 5) return 'good'
      return 'poor'
    } catch {
      return 'poor'
    }
  }
  
  // Handle numeric spines
  if (typeof recommendedSpine === 'number' && typeof arrowSpine === 'number') {
    const diff = Math.abs(arrowSpine - recommendedSpine)
    if (diff <= 20) return 'excellent'
    if (diff <= 50) return 'good'
    return 'poor'
  }
  
  return 'poor'
}

const getSpineDisplay = (arrow) => {
  // Use the pre-formatted spine_display field if available (supports wood spine format)
  if (arrow.spine_display) {
    return arrow.spine_display
  }
  
  // Fallback to spine_specifications for backward compatibility
  if (arrow.spine_specifications && arrow.spine_specifications.length > 0) {
    return arrow.spine_specifications.map(spec => spec.spine).join(', ')  
  }
  
  // Final fallback to min/max spine range
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

const loadCompatibleArrows = async () => {
  if (pending.value) return

  pending.value = true
  error.value = null

  try {
    const result = await api.apiRequest('/arrows/compatible', {
      method: 'POST',
      body: JSON.stringify({
        bow_config: bowConfig.value,
        filters: {
          // Add any additional filters here
        }
      })
    })

    // Add compatibility ratings to arrows
    const arrowsWithCompatibility = result.compatible_arrows.map(arrow => {
      // Get primary spine for compatibility check
      const primarySpine = arrow.spine_specifications?.[0]?.spine || arrow.spine || 0
      const compatibility = calculateCompatibility(primarySpine, recommendedSpine.value)
      
      return {
        ...arrow,
        compatibility,
        recommended: Math.random() > 0.7 // Temporary random recommendation
      }
    })

    // Sort by compatibility and recommendation
    arrowsWithCompatibility.sort((a, b) => {
      // Recommended arrows first
      if (a.recommended && !b.recommended) return -1
      if (!a.recommended && b.recommended) return 1
      
      // Then by compatibility
      const compatibilityOrder = { excellent: 3, good: 2, poor: 1 }
      return compatibilityOrder[b.compatibility] - compatibilityOrder[a.compatibility]
    })

    compatibleArrows.value = arrowsWithCompatibility

  } catch (err) {
    error.value = err
    console.error('Error loading compatible arrows:', err)
  } finally {
    pending.value = false
  }
}

const refresh = () => {
  loadCompatibleArrows()
}

// Watch for bow config changes
watch([bowConfig, recommendedSpine], () => {
  // Debounce the reload
  setTimeout(() => {
    loadCompatibleArrows()
  }, 300)
}, { deep: true, immediate: true })

// Initial load
onMounted(() => {
  loadCompatibleArrows()
})
</script>