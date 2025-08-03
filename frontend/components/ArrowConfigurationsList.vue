<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
        <i class="fas fa-crosshairs mr-2 text-indigo-600"></i>
        Arrow Configurations
      </h3>
      <CustomButton
        @click="showAddModal = true"
        variant="filled"
        class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
      >
        <i class="fas fa-plus mr-2"></i>
        Add Configuration
      </CustomButton>
    </div>

    <!-- Configurations List -->
    <div v-if="configurations.length > 0" class="space-y-3">
      <div 
        v-for="config in configurations" 
        :key="config.id || config.name"
        class="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">{{ config.name }}</h4>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div>
                <span class="text-gray-600 dark:text-gray-400">Length:</span>
                <span class="font-medium ml-1">{{ config.arrow_length }}"</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">Point:</span>
                <span class="font-medium ml-1">{{ config.point_weight }}gr</span>
              </div>
              <div v-if="config.total_weight">
                <span class="text-gray-600 dark:text-gray-400">Total:</span>
                <span class="font-medium ml-1">{{ config.total_weight }}gr</span>
              </div>
              <div v-if="config.calculated_foc">
                <span class="text-gray-600 dark:text-gray-400">FOC:</span>
                <span class="font-medium ml-1">{{ config.calculated_foc }}%</span>
              </div>
            </div>

            <div v-if="config.shaft_model || config.shaft_manufacturer" class="mt-2 text-sm">
              <span class="text-gray-600 dark:text-gray-400">Shaft:</span>
              <span class="font-medium ml-1">
                {{ config.shaft_manufacturer ? `${config.shaft_manufacturer} ` : '' }}{{ config.shaft_model || 'Unknown' }}
              </span>
              <span v-if="config.arrow_spine" class="ml-2 text-gray-500">
                ({{ config.arrow_spine }} spine)
              </span>
            </div>

            <div v-if="config.notes" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {{ config.notes }}
            </div>
          </div>

          <div class="flex space-x-2 ml-4">
            <CustomButton
              @click="getRecommendations(config)"
              variant="outlined"
              size="small"
              class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900/20"
              :disabled="loadingRecommendations"
            >
              <i class="fas fa-search mr-1"></i>
              {{ loadingRecommendations ? 'Loading...' : 'Find Arrows' }}
            </CustomButton>
            <CustomButton
              @click="editConfiguration(config)"
              variant="outlined"
              size="small"
              class="text-gray-600 dark:text-gray-400"
            >
              <i class="fas fa-edit"></i>
            </CustomButton>
            <CustomButton
              @click="deleteConfiguration(config)"
              variant="outlined"
              size="small"
              class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900/20"
            >
              <i class="fas fa-trash"></i>
            </CustomButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
      <i class="fas fa-crosshairs text-4xl mb-4 opacity-50"></i>
      <p class="text-lg mb-2">No arrow configurations yet</p>
      <p class="text-sm">Add your first arrow configuration to get personalized recommendations</p>
    </div>

    <!-- Arrow Recommendations Section -->
    <div v-if="showRecommendations && recommendations.length > 0" class="mt-8">
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
        <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-bullseye mr-2 text-green-600"></i>
          Recommended Arrows for "{{ selectedConfig?.name }}"
        </h4>
        
        <div class="space-y-3">
          <div 
            v-for="recommendation in recommendations.slice(0, 5)" 
            :key="recommendation.arrow.id"
            class="flex justify-between items-center p-3 bg-white dark:bg-gray-700 rounded-lg"
          >
            <div class="flex-1">
              <h5 class="font-medium text-gray-900 dark:text-gray-100">
                {{ recommendation.arrow.manufacturer }} {{ recommendation.arrow.model_name }}
              </h5>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Spine: {{ recommendation.spine_specification.spine }} | 
                Diameter: {{ recommendation.spine_specification.outer_diameter }}" |
                GPI: {{ recommendation.spine_specification.gpi_weight }}
              </p>
              <div class="flex items-center mt-1">
                <span class="text-xs px-2 py-1 rounded-full" 
                      :class="getCompatibilityClass(recommendation.compatibility_rating)">
                  {{ recommendation.match_percentage }}% match
                </span>
                <span class="text-xs text-gray-500 ml-2">{{ recommendation.compatibility_rating }}</span>
              </div>
            </div>
            
            <CustomButton
              @click="addArrowToConfiguration(recommendation)"
              variant="filled"
              size="small"
              class="bg-green-600 text-white hover:bg-green-700 ml-4"
            >
              <i class="fas fa-plus mr-1"></i>
              Add to Setup
            </CustomButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Configuration Modal -->
    <ArrowConfigurationModal
      v-if="showAddModal || editingConfig"
      :editing-config="editingConfig"
      :is-saving="isSaving"
      :error="error"
      @save="saveConfiguration"
      @close="closeModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ArrowConfigurationModal from './ArrowConfigurationModal.vue'
import type { ArrowConfiguration, ArrowRecommendation } from '~/types/arrow'

const props = defineProps({
  configurations: {
    type: Array as () => ArrowConfiguration[],
    default: () => []
  },
  bowConfig: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['add-configuration', 'update-configuration', 'delete-configuration', 'add-arrow-to-setup', 'confirm-delete'])

// Modal state
const showAddModal = ref(false)
const editingConfig = ref<ArrowConfiguration | null>(null)
const isSaving = ref(false)
const error = ref('')

// Recommendations state
const showRecommendations = ref(false)
const recommendations = ref<ArrowRecommendation[]>([])
const selectedConfig = ref<ArrowConfiguration | null>(null)
const loadingRecommendations = ref(false)

const api = useApi()

const saveConfiguration = async (configData: ArrowConfiguration) => {
  isSaving.value = true
  error.value = ''
  
  try {
    if (editingConfig.value) {
      emit('update-configuration', { ...configData, id: editingConfig.value.id })
    } else {
      emit('add-configuration', configData)
    }
    closeModal()
  } catch (err) {
    error.value = 'Failed to save configuration. Please try again.'
    console.error('Error saving configuration:', err)
  } finally {
    isSaving.value = false
  }
}

const editConfiguration = (config: ArrowConfiguration) => {
  editingConfig.value = config
  showAddModal.value = true
}

const deleteConfiguration = (config: ArrowConfiguration) => {
  // Emit confirmation request to parent
  emit('confirm-delete', {
    config,
    message: `Are you sure you want to delete "${config.name}"?`
  })
}

const closeModal = () => {
  showAddModal.value = false
  editingConfig.value = null
  error.value = ''
}

const getRecommendations = async (config: ArrowConfiguration) => {
  loadingRecommendations.value = true
  selectedConfig.value = config
  
  try {
    // Create a bow configuration for recommendations that includes arrow-specific data
    const searchConfig = {
      ...props.bowConfig,
      arrow_length: config.arrow_length,
      point_weight: config.point_weight
    }
    
    const result = await api.getArrowRecommendations(searchConfig)
    recommendations.value = result.recommended_arrows || []
    showRecommendations.value = true
  } catch (err) {
    console.error('Error getting recommendations:', err)
    recommendations.value = []
  } finally {
    loadingRecommendations.value = false
  }
}

const addArrowToConfiguration = (recommendation: ArrowRecommendation) => {
  emit('add-arrow-to-setup', {
    arrowConfig: selectedConfig.value,
    arrowRecommendation: recommendation
  })
}

const getCompatibilityClass = (rating: string) => {
  switch (rating) {
    case 'excellent':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    case 'good':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    case 'poor':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
  }
}
</script>