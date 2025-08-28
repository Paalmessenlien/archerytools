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
      <!-- Bow Arrow Configuration (when viewing from bow page) -->
      <BowArrowConfiguration
        v-if="bowContext"
        :bow-id="bowContext.bowId"
        :arrow-id="arrowId"
        :bow-name="bowContext.bowName"
        :return-to="bowContext.returnTo"
        @loaded="onBowConfigLoaded"
        class="mb-6"
      />

      <!-- Calculation Context (when coming from calculator) -->
      <CalculationSummary
        v-else-if="calculationContext"
        :bow-config="calculationContext.bowConfig"
        :compatibility-score="calculationContext.compatibilityScore"
        :match-percentage="calculationContext.matchPercentage"
        :compatibility-rating="calculationContext.compatibilityRating"
        :reasons="calculationContext.reasons"
        :spine-spec="calculationContext.spineSpec"
        @edit-configuration="showInlineCalculator = true"
        @back-to-calculator="navigateTo('/calculator')"
        class="mb-6"
      />
      
      <!-- Inline Calculator (when editing) -->
      <InlineCalculator
        v-if="showInlineCalculator && calculationContext"
        :bow-config="editingBowConfig || calculationContext.bowConfig"
        :is-recalculating="isRecalculating"
        @close="showInlineCalculator = false"
        @update="handleConfigUpdate"
        @apply="handleConfigApply"
        class="mb-6"
      />
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <div class="min-w-0">
          <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
            {{ arrow.manufacturer }} {{ arrow.model_name }}
          </h1>
          <p v-if="arrow.arrow_type" class="text-gray-600 dark:text-gray-300 mt-1">
            {{ arrow.arrow_type && arrow.arrow_type.length > 0 ? arrow.arrow_type.charAt(0).toUpperCase() + arrow.arrow_type.slice(1) : 'Unknown' }} Arrow
          </p>
        </div>
        
        <NuxtLink to="/database" class="btn-secondary w-full sm:w-auto">
          ← Back to Database
        </NuxtLink>
      </div>

      <!-- Quick Specs (chips) -->
      <md-chip-set class="mb-4 mt-2">
        <md-assist-chip :label="'Spine: ' + getSpineRange()">
          <i class="fas fa-ruler-horizontal fa-icon" slot="icon" style="color: #6366f1;"></i>
        </md-assist-chip>
        <md-assist-chip :label="'⌀ ' + getDiameterRange()">
          <i class="fas fa-dot-circle fa-icon" slot="icon" style="color: #dc2626;"></i>
        </md-assist-chip>
        <md-assist-chip :label="getGPIRange() + ' GPI'">
          <i class="fas fa-weight-hanging fa-icon" slot="icon" style="color: #7c2d12;"></i>
        </md-assist-chip>
        <md-assist-chip :label="arrow.material || 'Material N/A'">
          <i class="fas fa-layer-group fa-icon" slot="icon" style="color: #059669;"></i>
        </md-assist-chip>
        <md-assist-chip v-if="arrow.straightness_tolerance" :label="arrow.straightness_tolerance">
          <i class="fas fa-crosshairs fa-icon" slot="icon" style="color: #7c3aed;"></i>
        </md-assist-chip>
      </md-chip-set>

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
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">
            Spine Specifications
            <span class="text-sm font-normal text-gray-600 dark:text-gray-400 ml-2">
              ({{ arrow.spine_specifications.length }} options available)
            </span>
          </h3>
          <div v-if="calculationContext?.spineSpec" class="flex items-center text-sm text-blue-600 dark:text-blue-400">
            <i class="fas fa-star mr-1"></i>
            Recommended: {{ calculationContext.spineSpec.spine }}
          </div>
        </div>
        
        <div class="table-responsive">
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
                :class="[
                  'hover:bg-gray-50 dark:hover:bg-gray-700',
                  isRecommendedSpine(spec) ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500' : ''
                ]"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                  <div class="flex items-center space-x-2">
                    <span>{{ spec.spine }}</span>
                    <i v-if="isRecommendedSpine(spec)" class="fas fa-star text-blue-500 text-xs"></i>
                  </div>
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
        <h3 class="text-lg font-semibold mb-4">Quick Actions</h3>
        
        <div class="flex flex-wrap gap-3">
          <NuxtLink 
            v-if="calculationContext"
            to="/calculator" 
            class="btn-primary"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            Back to Calculator
          </NuxtLink>
          
          <NuxtLink 
            v-else
            to="/calculator" 
            class="btn-primary"
          >
            <i class="fas fa-calculator mr-2"></i>
            Find Compatible Setup
          </NuxtLink>
          
          <button 
            @click="copyToClipboard"
            class="btn-secondary"
          >
            <i class="fas fa-copy mr-2"></i>
            Copy Arrow Info
          </button>
          
          <a 
            v-if="arrow.source_url"
            :href="arrow.source_url" 
            target="_blank" 
            rel="noopener"
            class="btn-secondary"
          >
            <i class="fas fa-external-link-alt mr-2"></i>
            View Original Source
          </a>
        </div>
      </div>

      <!-- Arrow Journal -->
      <ArrowJournal
        :arrow-id="arrowId"
        :arrow="arrow"
        @statistics-updated="handleJournalStatistics"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BowConfiguration, SpineSpecification } from '~/types/arrow'
import ArrowJournal from '~/components/ArrowJournal.vue'

// API
const api = useApi()
const route = useRoute()

// Reactive state
const arrow = ref(null)
const loading = ref(false)
const error = ref(null)
const imageError = ref(false)

// Calculation context state
const calculationContext = ref(null)
const showInlineCalculator = ref(false)
const editingBowConfig = ref(null)
const isRecalculating = ref(false)

// Bow context state
const bowContext = ref(null)

// Journal statistics
const journalStatistics = ref({})

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

const parseCalculationContext = () => {
  const query = route.query
  
  if (query.bow_config && query.compatibility_score) {
    try {
      const bowConfig = JSON.parse(atob(query.bow_config))
      const reasons = query.reasons ? JSON.parse(atob(query.reasons)) : []
      const spineSpec = query.spine_spec ? JSON.parse(atob(query.spine_spec)) : null
      
      calculationContext.value = {
        bowConfig,
        compatibilityScore: parseFloat(query.compatibility_score),
        matchPercentage: parseFloat(query.match_percentage),
        compatibilityRating: query.compatibility_rating,
        reasons,
        spineSpec
      }
    } catch (err) {
      console.error('Error parsing calculation context:', err)
      calculationContext.value = null
    }
  }
}

const parseBowContext = () => {
  const query = route.query
  
  if (query.bowId) {
    bowContext.value = {
      bowId: query.bowId,
      bowName: query.bowName || 'Unknown Bow',
      returnTo: query.returnTo || null
    }
  } else {
    bowContext.value = null
  }
}

const handleConfigUpdate = (newConfig: BowConfiguration) => {
  editingBowConfig.value = newConfig
  // TODO: Add debounced real-time recalculation here
}

const handleConfigApply = async (newConfig: BowConfiguration) => {
  isRecalculating.value = true
  showInlineCalculator.value = false
  
  try {
    // Recalculate arrow compatibility with new configuration
    const response = await api.getArrowRecommendations(newConfig)
    
    // Find this arrow in the new recommendations
    const thisArrowRecommendation = response.recommended_arrows.find(
      rec => rec.arrow.id === parseInt(arrowId.value)
    )
    
    if (thisArrowRecommendation) {
      // Update calculation context with new results
      calculationContext.value = {
        bowConfig: newConfig,
        compatibilityScore: thisArrowRecommendation.compatibility_score,
        matchPercentage: thisArrowRecommendation.match_percentage,
        compatibilityRating: thisArrowRecommendation.compatibility_rating,
        reasons: thisArrowRecommendation.reasons,
        spineSpec: thisArrowRecommendation.spine_specification
      }
      
      // Update URL to reflect new calculation
      await navigateTo({
        path: `/arrows/${arrowId.value}`,
        query: {
          bow_config: btoa(JSON.stringify(newConfig)),
          compatibility_score: thisArrowRecommendation.compatibility_score.toString(),
          match_percentage: thisArrowRecommendation.match_percentage.toString(),
          compatibility_rating: thisArrowRecommendation.compatibility_rating,
          reasons: btoa(JSON.stringify(thisArrowRecommendation.reasons)),
          spine_spec: btoa(JSON.stringify(thisArrowRecommendation.spine_specification))
        }
      }, { replace: true })
    }
  } catch (err) {
    console.error('Error recalculating compatibility:', err)
  } finally {
    isRecalculating.value = false
    editingBowConfig.value = null
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

const isRecommendedSpine = (spec) => {
  return calculationContext.value?.spineSpec && 
         calculationContext.value.spineSpec.spine === spec.spine
}

const onBowConfigLoaded = (bowArrowSetup) => {
  // Optional: Do something when bow configuration is loaded
  console.log('Bow arrow configuration loaded:', bowArrowSetup)
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

// Handle journal statistics updates
const handleJournalStatistics = (stats) => {
  journalStatistics.value = stats
  console.log('Arrow journal statistics updated:', stats)
}


// Lifecycle
onMounted(() => {
  if (arrowId.value) {
    loadArrowDetails()
    parseCalculationContext()
    parseBowContext()
  }
})

// Watch for route changes
watch(() => arrowId.value, (newId) => {
  if (newId) {
    loadArrowDetails()
    parseCalculationContext()
    parseBowContext()
  }
})

// Watch for query parameter changes
watch(() => route.query, () => {
  parseCalculationContext()
  parseBowContext()
}, { deep: true })

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

// Page metadata
definePageMeta({
  middleware: ['auth-check']
})
</script>
