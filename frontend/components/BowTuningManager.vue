<template>
  <div class="bow-tuning-manager">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
        <i class="fas fa-sliders-h mr-2 text-purple-600 dark:text-purple-400"></i>
        Technical Tuning
      </h2>
      <CustomButton
        @click="openCreateModal"
        variant="filled"
        class="bg-purple-600 text-white hover:bg-purple-700 dark:bg-purple-600 dark:hover:bg-purple-700 w-full sm:w-auto"
      >
        <i class="fas fa-plus mr-2"></i>
        Add Configuration
      </CustomButton>
    </div>

    <!-- Tab Navigation -->
    <div class="flex border-b border-gray-200 dark:border-gray-700 mb-4">
      <button
        @click="activeTab = 'configs'"
        :class="[
          'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
          activeTab === 'configs'
            ? 'text-purple-600 dark:text-purple-400 border-purple-600 dark:border-purple-400'
            : 'text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        <i class="fas fa-cog mr-2"></i>
        Configurations
      </button>
      <button
        @click="activeTab = 'history'"
        :class="[
          'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
          activeTab === 'history'
            ? 'text-purple-600 dark:text-purple-400 border-purple-600 dark:border-purple-400'
            : 'text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        <i class="fas fa-history mr-2"></i>
        Tuning History
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 dark:border-purple-400 mx-auto mb-3"></div>
      <p class="text-gray-600 dark:text-gray-400">Loading tuning configurations...</p>
    </div>

    <!-- Configurations Tab -->
    <div v-else-if="activeTab === 'configs'">
      <!-- Empty State -->
      <div v-if="configs.length === 0" class="text-center py-12">
        <i class="fas fa-sliders-h text-4xl text-gray-300 dark:text-gray-600 mb-4"></i>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Tuning Configurations</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          Create your first tuning configuration to track brace height, tiller, nocking point, and more.
        </p>
        <CustomButton
          @click="openCreateModal"
          variant="filled"
          class="bg-purple-600 text-white hover:bg-purple-700"
        >
          <i class="fas fa-plus mr-2"></i>
          Create Configuration
        </CustomButton>
      </div>

      <!-- Configurations List -->
      <div v-else class="space-y-4">
        <div
          v-for="config in configs"
          :key="config.id"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
        >
          <!-- Config Header -->
          <div
            @click="toggleConfig(config.id)"
            class="px-4 py-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 cursor-pointer"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center flex-1">
                <i v-if="config.is_active" class="fas fa-star text-yellow-500 mr-2"></i>
                <h3 class="font-medium text-gray-900 dark:text-gray-100">{{ config.name }}</h3>
                <span
                  v-if="config.is_active"
                  class="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full"
                >
                  Active
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-500 dark:text-gray-400 hidden sm:inline">
                  Updated {{ formatDate(config.updated_at) }}
                </span>
                <i :class="expandedConfigs[config.id] ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="text-gray-400"></i>
              </div>
            </div>
            <p v-if="config.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {{ config.description }}
            </p>
          </div>

          <!-- Config Details (Expandable) -->
          <div v-if="expandedConfigs[config.id]" class="p-4">
            <!-- Tuning Values Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              <div
                v-for="(param, key) in getDisplayableParameters(config)"
                :key="key"
                class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3"
              >
                <div class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                  {{ formatParameterName(key) }}
                </div>
                <div class="text-lg font-medium text-gray-900 dark:text-gray-100">
                  {{ formatParameterValue(param) }}
                </div>
                <div v-if="param.notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1 italic">
                  {{ param.notes }}
                </div>
              </div>
            </div>

            <!-- Empty Parameters Message -->
            <div v-if="Object.keys(getDisplayableParameters(config)).length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">
              <i class="fas fa-info-circle mr-2"></i>
              No tuning values recorded yet. Click Edit to add values.
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-wrap gap-2 pt-4 border-t border-gray-200 dark:border-gray-600">
              <CustomButton
                @click.stop="openEditModal(config)"
                variant="outlined"
                class="text-purple-600 border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20"
              >
                <i class="fas fa-edit mr-2"></i>
                Edit
              </CustomButton>
              <CustomButton
                @click.stop="duplicateConfig(config)"
                variant="outlined"
                class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20"
              >
                <i class="fas fa-copy mr-2"></i>
                Duplicate
              </CustomButton>
              <CustomButton
                v-if="!config.is_active"
                @click.stop="activateConfig(config)"
                variant="outlined"
                class="text-green-600 border-green-600 hover:bg-green-50 dark:hover:bg-green-900/20"
              >
                <i class="fas fa-check-circle mr-2"></i>
                Set as Active
              </CustomButton>
              <CustomButton
                @click.stop="confirmDelete(config)"
                variant="outlined"
                class="text-red-600 border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <i class="fas fa-trash mr-2"></i>
                Delete
              </CustomButton>
            </div>
          </div>
        </div>

        <!-- Compare Button -->
        <div v-if="configs.length >= 2" class="mt-4">
          <CustomButton
            @click="openCompareModal"
            variant="outlined"
            class="w-full text-purple-600 border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20"
          >
            <i class="fas fa-balance-scale mr-2"></i>
            Compare Configurations
          </CustomButton>
        </div>
      </div>
    </div>

    <!-- History Tab -->
    <div v-else-if="activeTab === 'history'">
      <div v-if="loadingHistory" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 dark:border-purple-400 mx-auto mb-3"></div>
        <p class="text-gray-600 dark:text-gray-400">Loading history...</p>
      </div>

      <div v-else-if="history.length === 0" class="text-center py-12">
        <i class="fas fa-history text-4xl text-gray-300 dark:text-gray-600 mb-4"></i>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No History Yet</h3>
        <p class="text-gray-600 dark:text-gray-400">
          Changes to tuning configurations will appear here.
        </p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="entry in history"
          :key="entry.id"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
        >
          <div class="flex items-start space-x-3">
            <div :class="getChangeTypeIcon(entry.change_type)" class="mt-1"></div>
            <div class="flex-1">
              <p class="text-gray-900 dark:text-gray-100">{{ entry.change_description }}</p>
              <div class="flex items-center space-x-3 mt-1 text-sm text-gray-500 dark:text-gray-400">
                <span>{{ formatDateTime(entry.created_at) }}</span>
                <span v-if="entry.config_name" class="text-purple-600 dark:text-purple-400">
                  {{ entry.config_name }}
                </span>
              </div>
              <div v-if="entry.user_note" class="mt-2 text-sm text-gray-600 dark:text-gray-400 italic">
                <i class="fas fa-quote-left mr-1 text-xs"></i>
                {{ entry.user_note }}
              </div>
              <div v-if="entry.old_value && entry.new_value" class="mt-2 text-sm">
                <span class="text-red-500 line-through">{{ entry.old_value }}</span>
                <i class="fas fa-arrow-right mx-2 text-gray-400"></i>
                <span class="text-green-500">{{ entry.new_value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="history.length < historyTotal" class="text-center mt-4">
          <CustomButton
            @click="loadMoreHistory"
            variant="outlined"
            :disabled="loadingHistory"
            class="text-purple-600 border-purple-600"
          >
            <span v-if="loadingHistory">Loading...</span>
            <span v-else>Load More</span>
          </CustomButton>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="configToDelete" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
          Delete Configuration
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete "<strong>{{ configToDelete.name }}</strong>"? This action cannot be undone.
        </p>
        <div class="flex justify-end space-x-3">
          <CustomButton
            @click="configToDelete = null"
            variant="outlined"
            class="text-gray-600 border-gray-300"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="deleteConfig"
            variant="filled"
            :disabled="deleting"
            class="bg-red-600 text-white hover:bg-red-700"
          >
            <span v-if="deleting">Deleting...</span>
            <span v-else>Delete</span>
          </CustomButton>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <TuningConfigModal
      v-if="showConfigModal"
      :bow-setup="bowSetup"
      :config="editingConfig"
      :bow-type="bowSetup?.bow_type"
      @close="closeConfigModal"
      @saved="handleConfigSaved"
    />

    <!-- Compare Modal -->
    <TuningCompareModal
      v-if="showCompareModal"
      :configs="configs"
      @close="showCompareModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['show-notification'])

const api = useApi()

// State
const loading = ref(false)
const configs = ref([])
const expandedConfigs = ref({})
const activeTab = ref('configs')

// History state
const loadingHistory = ref(false)
const history = ref([])
const historyTotal = ref(0)
const historyOffset = ref(0)

// Modal state
const showConfigModal = ref(false)
const editingConfig = ref(null)
const showCompareModal = ref(false)

// Delete state
const configToDelete = ref(null)
const deleting = ref(false)

// Parameter display names
const parameterDisplayNames = {
  brace_height: 'Brace Height',
  tiller_top: 'Tiller (Top)',
  tiller_bottom: 'Tiller (Bottom)',
  tiller_difference: 'Tiller Difference',
  nocking_point: 'Nocking Point',
  plunger_pressure: 'Plunger Pressure',
  plunger_position: 'Plunger Position',
  clicker_position: 'Clicker Position',
  string_material: 'String Material',
  string_strands: 'String Strands',
  axle_to_axle: 'Axle-to-Axle',
  draw_weight_actual: 'Draw Weight (Actual)',
  letoff_percentage: 'Let-off',
  cam_timing: 'Cam Timing',
  cam_lean: 'Cam Lean',
  peep_height: 'Peep Height',
  rest_centershot: 'Rest Centershot',
  rest_height: 'Rest Height',
  cable_guard_position: 'Cable Guard Position',
  arrow_pass_position: 'Arrow Pass Position',
  sight_pin_position: 'Sight Pin Position'
}

// Load tuning configurations
const loadConfigs = async () => {
  if (!props.bowSetup?.id) return

  try {
    loading.value = true
    const response = await api.get(`/bow-setups/${props.bowSetup.id}/tuning-configs`)
    configs.value = response.configs || []

    // Auto-expand active config
    configs.value.forEach(config => {
      if (config.is_active) {
        expandedConfigs.value[config.id] = true
      }
    })
  } catch (error) {
    console.error('Error loading tuning configs:', error)
    emit('show-notification', 'Failed to load tuning configurations', 'error')
  } finally {
    loading.value = false
  }
}

// Load tuning history
const loadHistory = async (reset = true) => {
  if (!props.bowSetup?.id) return

  try {
    loadingHistory.value = true
    if (reset) {
      historyOffset.value = 0
      history.value = []
    }

    const response = await api.get(`/bow-setups/${props.bowSetup.id}/tuning-history`, {
      params: {
        limit: 20,
        offset: historyOffset.value
      }
    })

    if (reset) {
      history.value = response.history || []
    } else {
      history.value = [...history.value, ...(response.history || [])]
    }
    historyTotal.value = response.total || 0
    historyOffset.value = history.value.length
  } catch (error) {
    console.error('Error loading tuning history:', error)
    emit('show-notification', 'Failed to load tuning history', 'error')
  } finally {
    loadingHistory.value = false
  }
}

const loadMoreHistory = () => {
  loadHistory(false)
}

// Toggle config expansion
const toggleConfig = (configId) => {
  expandedConfigs.value[configId] = !expandedConfigs.value[configId]
}

// Open create modal
const openCreateModal = () => {
  editingConfig.value = null
  showConfigModal.value = true
}

// Open edit modal
const openEditModal = (config) => {
  editingConfig.value = config
  showConfigModal.value = true
}

// Close config modal
const closeConfigModal = () => {
  showConfigModal.value = false
  editingConfig.value = null
}

// Handle config saved
const handleConfigSaved = async () => {
  closeConfigModal()
  await loadConfigs()
  emit('show-notification', 'Tuning configuration saved successfully', 'success')

  // Refresh history if on that tab
  if (activeTab.value === 'history') {
    await loadHistory()
  }
}

// Activate config
const activateConfig = async (config) => {
  try {
    await api.post(`/tuning-configs/${config.id}/activate`)
    await loadConfigs()
    emit('show-notification', `"${config.name}" is now active`, 'success')

    // Refresh history
    if (activeTab.value === 'history') {
      await loadHistory()
    }
  } catch (error) {
    console.error('Error activating config:', error)
    emit('show-notification', 'Failed to activate configuration', 'error')
  }
}

// Duplicate config
const duplicateConfig = async (config) => {
  try {
    const response = await api.post(`/tuning-configs/${config.id}/duplicate`)
    await loadConfigs()
    emit('show-notification', `Configuration duplicated as "${response.config?.name}"`, 'success')

    // Expand the new config
    if (response.config?.id) {
      expandedConfigs.value[response.config.id] = true
    }
  } catch (error) {
    console.error('Error duplicating config:', error)
    emit('show-notification', 'Failed to duplicate configuration', 'error')
  }
}

// Confirm delete
const confirmDelete = (config) => {
  configToDelete.value = config
}

// Delete config
const deleteConfig = async () => {
  if (!configToDelete.value) return

  try {
    deleting.value = true
    await api.delete(`/tuning-configs/${configToDelete.value.id}`)
    await loadConfigs()
    emit('show-notification', 'Configuration deleted', 'success')
    configToDelete.value = null

    // Refresh history
    if (activeTab.value === 'history') {
      await loadHistory()
    }
  } catch (error) {
    console.error('Error deleting config:', error)
    emit('show-notification', 'Failed to delete configuration', 'error')
  } finally {
    deleting.value = false
  }
}

// Open compare modal
const openCompareModal = () => {
  showCompareModal.value = true
}

// Get displayable parameters for a config
const getDisplayableParameters = (config) => {
  if (!config.values) return {}

  // Filter out empty values
  const displayable = {}
  for (const [key, param] of Object.entries(config.values)) {
    if (param.value !== null && param.value !== undefined && param.value !== '') {
      displayable[key] = param
    }
  }
  return displayable
}

// Format parameter name
const formatParameterName = (key) => {
  return parameterDisplayNames[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

// Format parameter value
const formatParameterValue = (param) => {
  if (!param || param.value === null || param.value === undefined) return '-'

  let display = param.value
  if (param.unit) {
    display += ` ${param.unit}`
  }
  return display
}

// Format date
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}

// Format date time
const formatDateTime = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return 'Unknown'
  }
}

// Get change type icon
const getChangeTypeIcon = (changeType) => {
  const icons = {
    config_created: 'fas fa-plus-circle text-green-500',
    config_updated: 'fas fa-edit text-blue-500',
    config_deleted: 'fas fa-trash text-red-500',
    config_activated: 'fas fa-star text-yellow-500',
    parameter_changed: 'fas fa-exchange-alt text-purple-500'
  }
  return icons[changeType] || 'fas fa-circle text-gray-500'
}

// Watch for tab changes
watch(activeTab, async (newTab) => {
  if (newTab === 'history' && history.value.length === 0) {
    await loadHistory()
  }
})

// Watch for bow setup changes
watch(() => props.bowSetup?.id, () => {
  if (props.bowSetup?.id) {
    loadConfigs()
    history.value = []
    historyOffset.value = 0
    if (activeTab.value === 'history') {
      loadHistory()
    }
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  if (props.bowSetup?.id) {
    loadConfigs()
  }
})
</script>

<style scoped>
.bow-tuning-manager {
  @apply w-full;
}
</style>
