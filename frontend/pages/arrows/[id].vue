<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading" class="space-y-6">
      <div class="animate-pulse">
        <div class="h-8 bg-gray-200 rounded w-64 mb-4"></div>
        <div class="h-4 bg-gray-200 rounded w-48 mb-6"></div>
      </div>
      
      <div class="card animate-pulse">
        <div class="space-y-4">
          <div class="h-6 bg-gray-200 rounded w-32"></div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="h-16 bg-gray-200 rounded"></div>
            <div class="h-16 bg-gray-200 rounded"></div>
            <div class="h-16 bg-gray-200 rounded"></div>
            <div class="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card text-center py-12">
      <div class="text-red-500 mb-4">
        <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Arrow Not Found</h3>
      <p class="text-gray-600 dark:text-gray-300 mb-4">{{ error.message || 'Failed to load arrow details.' }}</p>
      <NuxtLink to="/database" class="btn-primary">
        Back to Database
      </NuxtLink>
    </div>

    <!-- Arrow Details -->
    <div v-else-if="arrow" class="space-y-6">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
            {{ arrow.manufacturer }} {{ arrow.model_name }}
          </h1>
          <p v-if="arrow.arrow_type" class="text-gray-600 dark:text-gray-300 mt-2">
            {{ arrow.arrow_type.charAt(0).toUpperCase() + arrow.arrow_type.slice(1) }} Arrow
          </p>
        </div>
        
        <NuxtLink to="/database" class="btn-secondary">
          ← Back to Database
        </NuxtLink>
      </div>

      <!-- Arrow Image -->
      <div v-if="arrow.primary_image_url" class="card">
        <h3 class="text-lg font-semibold mb-4">Product Image</h3>
        <img 
          :src="arrow.primary_image_url" 
          :alt="`${arrow.manufacturer} ${arrow.model_name}`"
          class="max-w-md mx-auto rounded-lg shadow-md"
          @error="imageError = true"
        />
        <div v-if="imageError" class="text-center text-gray-500 py-8">
          Image not available
        </div>
      </div>

      <!-- Basic Information -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Arrow Information</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Manufacturer</label>
            <p class="text-lg">{{ arrow.manufacturer }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Model</label>
            <p class="text-lg">{{ arrow.model_name }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Material</label>
            <p class="text-lg">{{ arrow.material || 'Not specified' }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Arrow Type</label>
            <p class="text-lg">{{ arrow.arrow_type || 'Not specified' }}</p>
          </div>
          
          <div v-if="arrow.carbon_content">
            <label class="block text-sm font-medium text-gray-700 mb-1">Carbon Content</label>
            <p class="text-lg">{{ arrow.carbon_content }}</p>
          </div>
          
          <div v-if="arrow.source_url">
            <label class="block text-sm font-medium text-gray-700 mb-1">Source</label>
            <a :href="arrow.source_url" target="_blank" rel="noopener" class="text-blue-600 hover:text-blue-700 underline">
              View Original
            </a>
          </div>
        </div>

        <!-- Description -->
        <div v-if="arrow.description" class="mt-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <p class="text-gray-700 leading-relaxed">{{ arrow.description }}</p>
        </div>
      </div>

      <!-- Spine Specifications -->
      <div v-if="arrow.spine_specifications && arrow.spine_specifications.length > 0" class="card">
        <h3 class="text-lg font-semibold mb-4">
          Spine Specifications
          <span class="text-sm font-normal text-gray-600 ml-2">
            ({{ arrow.spine_specifications.length }} options available)
          </span>
        </h3>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Spine
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Outer Diameter
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Weight (GPI)
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Inner Diameter
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Length Options
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr 
                v-for="spec in arrow.spine_specifications" 
                :key="spec.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ spec.spine }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ spec.outer_diameter ? spec.outer_diameter.toFixed(3) + '"' : 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ spec.gpi_weight ? spec.gpi_weight.toFixed(1) : 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ spec.inner_diameter ? spec.inner_diameter.toFixed(3) + '"' : 'N/A' }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                  <span v-if="spec.length_options && spec.length_options.length > 0">
                    {{ spec.length_options.map(l => `${l}"`).join(', ') }}
                  </span>
                  <span v-else>Standard</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Summary</h3>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ getSpineRange() }}</div>
            <div class="text-sm text-blue-600 dark:text-blue-400">Spine Range</div>
          </div>
          
          <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ getDiameterRange() }}</div>
            <div class="text-sm text-green-600 dark:text-green-400">Diameter Range</div>
          </div>
          
          <div class="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ getGPIRange() }}</div>
            <div class="text-sm text-purple-600 dark:text-purple-400">Weight Range (GPI)</div>
          </div>
          
          <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
            <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ arrow.spine_specifications?.length || 0 }}</div>
            <div class="text-sm text-orange-600 dark:text-orange-400">Spine Options</div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Actions</h3>
        
        <div class="flex flex-wrap gap-3">
          <NuxtLink 
            to="/recommendations" 
            class="btn-primary"
          >
            Find Compatible Setup
          </NuxtLink>
          
          <button 
            @click="copyToClipboard"
            class="btn-secondary"
          >
            Copy Arrow Info
          </button>
          
          <a 
            v-if="arrow.source_url"
            :href="arrow.source_url" 
            target="_blank" 
            rel="noopener"
            class="btn-secondary"
          >
            View Original Source
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// API
const api = useApi()
const route = useRoute()

// Reactive state
const arrow = ref(null)
const loading = ref(false)
const error = ref(null)
const imageError = ref(false)

// Get arrow ID from route
const arrowId = computed(() => route.params.id)

// Methods
const loadArrowDetails = async () => {
  loading.value = true
  error.value = null

  try {
    arrow.value = await api.getArrowDetails(arrowId.value)
  } catch (err) {
    error.value = err
    console.error('Error loading arrow details:', err)
  } finally {
    loading.value = false
  }
}

// Helper methods
const getSpineRange = () => {
  if (!arrow.value?.spine_specifications?.length) return 'N/A'
  
  const spines = arrow.value.spine_specifications.map(spec => spec.spine)
  const min = Math.min(...spines)
  const max = Math.max(...spines)
  
  return min === max ? `${min}` : `${min}-${max}`
}

const getDiameterRange = () => {
  if (!arrow.value?.spine_specifications?.length) return 'N/A'
  
  const diameters = arrow.value.spine_specifications.map(spec => spec.outer_diameter).filter(d => d)
  if (diameters.length === 0) return 'N/A'
  
  const min = Math.min(...diameters)
  const max = Math.max(...diameters)
  
  return min === max ? `${min.toFixed(3)}"` : `${min.toFixed(3)}"-${max.toFixed(3)}"`
}

const getGPIRange = () => {
  if (!arrow.value?.spine_specifications?.length) return 'N/A'
  
  const weights = arrow.value.spine_specifications.map(spec => spec.gpi_weight).filter(w => w)
  if (weights.length === 0) return 'N/A'
  
  const min = Math.min(...weights)
  const max = Math.max(...weights)
  
  return min === max ? `${min.toFixed(1)}` : `${min.toFixed(1)}-${max.toFixed(1)}`
}

const copyToClipboard = async () => {
  if (!arrow.value) return
  
  const arrowInfo = `${arrow.value.manufacturer} ${arrow.value.model_name}
Material: ${arrow.value.material || 'N/A'}
Spine Range: ${getSpineRange()}
Diameter Range: ${getDiameterRange()}
Weight Range: ${getGPIRange()} GPI
Available Spines: ${arrow.value.spine_specifications?.length || 0} options`

  try {
    await navigator.clipboard.writeText(arrowInfo)
    // Could add a toast notification here
    console.log('Arrow info copied to clipboard')
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
  }
}

// Lifecycle
onMounted(() => {
  if (arrowId.value) {
    loadArrowDetails()
  }
})

// Watch for route changes
watch(() => arrowId.value, (newId) => {
  if (newId) {
    loadArrowDetails()
  }
})

// Set dynamic page title
watchEffect(() => {
  if (arrow.value) {
    useHead({
      title: `${arrow.value.manufacturer} ${arrow.value.model_name} - Arrow Details`,
      meta: [
        { 
          name: 'description', 
          content: `Detailed specifications for ${arrow.value.manufacturer} ${arrow.value.model_name} arrow including spine options, weight, diameter and material information.` 
        }
      ]
    })
  } else {
    useHead({
      title: 'Arrow Details',
      meta: [
        { name: 'description', content: 'Detailed arrow specifications and technical data' }
      ]
    })
  }
})
</script>