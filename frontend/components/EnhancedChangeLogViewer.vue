<template>
  <div class="enhanced-change-log-viewer">
    <!-- Header (optional) -->
    <div v-if="showHeader" class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        <i class="fas fa-history mr-2 text-blue-600 dark:text-blue-400"></i>
        Complete Change History
        <span v-if="changes.length > 0" class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full">
          {{ changes.length }}
        </span>
      </h3>
      
      <div class="flex gap-2">
        <!-- Time filter buttons -->
        <button
          v-for="filter in timeFilters"
          :key="filter.value"
          @click="selectedTimeFilter = filter.value; loadChanges()"
          :class="[
            'px-3 py-1 text-sm rounded-lg transition-colors',
            selectedTimeFilter === filter.value
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
          ]"
        >
          {{ filter.label }}
        </button>
        
        <!-- Refresh button -->
        <CustomButton
          @click="loadChanges()"
          variant="outlined"
          class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-800"
          :disabled="loading"
        >
          <i :class="['fas fa-sync-alt', loading ? 'animate-spin' : '']"></i>
        </CustomButton>
      </div>
    </div>

    <!-- Filters and Controls -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Change Type Filter -->
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Filter by Type
          </label>
          <select
            v-model="selectedChangeType"
            @change="filterChanges"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-600 dark:border-gray-500 dark:text-gray-100"
          >
            <option value="">All Changes</option>
            <option value="arrow">Arrow Changes</option>
            <option value="equipment">Equipment Changes</option>
            <option value="setup">Setup Changes</option>
          </select>
        </div>
        
        <!-- Search -->
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Search Changes
          </label>
          <input
            v-model="searchQuery"
            @input="filterChanges"
            type="text"
            placeholder="Search descriptions, notes, or values..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-600 dark:border-gray-500 dark:text-gray-100 dark:placeholder-gray-400"
          />
        </div>
        
        <!-- User Note Toggle -->
        <div class="flex items-end">
          <label class="flex items-center">
            <input
              v-model="showOnlyWithNotes"
              @change="filterChanges"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Notes only</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-3"></div>
      <p class="text-gray-600 dark:text-gray-400">Loading change history...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredChanges.length === 0 && !loading" class="text-center py-12">
      <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="fas fa-history text-2xl text-gray-400"></i>
      </div>
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
        {{ changes.length === 0 ? 'No Changes Yet' : 'No Matching Changes' }}
      </h4>
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        {{ changes.length === 0 
          ? 'Start making modifications to see your change history here.' 
          : 'Try adjusting your search or filter settings.' 
        }}
      </p>
      <CustomButton
        v-if="changes.length > 0"
        @click="clearFilters"
        variant="outlined"
        class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400"
      >
        <i class="fas fa-filter mr-2"></i>
        Clear Filters
      </CustomButton>
    </div>

    <!-- Enhanced Timeline View -->
    <div v-else class="relative">
      <!-- Timeline line -->
      <div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>
      
      <div class="space-y-8">
        <div
          v-for="(change, index) in filteredChanges"
          :key="`${change.change_source}-${change.id}`"
          class="relative flex items-start"
        >
          <!-- Enhanced Timeline dot with gradient -->
          <div :class="[
            'relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-4 bg-white dark:bg-gray-800 shadow-lg',
            getChangeTypeColor(change.change_type, change.change_source)
          ]">
            <i :class="[
              'text-lg',
              getChangeTypeIcon(change.change_type, change.change_source)
            ]"></i>
          </div>
          
          <!-- Enhanced Change content -->
          <div class="ml-8 flex-1">
            <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm hover:shadow-md transition-shadow">
              <!-- Enhanced change header -->
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <!-- Change type badge -->
                    <span :class="[
                      'px-3 py-1 text-sm font-medium rounded-full',
                      getChangeTypeBadge(change.change_type, change.change_source)
                    ]">
                      {{ formatChangeType(change.change_type) }}
                    </span>
                    
                    <!-- Source badge -->
                    <span :class="[
                      'px-2 py-1 text-xs rounded-full',
                      getSourceBadge(change.change_source)
                    ]">
                      {{ change.change_source.charAt(0).toUpperCase() + change.change_source.slice(1) }}
                    </span>
                  </div>
                  
                  <!-- Enhanced equipment/arrow info -->
                  <div v-if="change.manufacturer_name || change.model_name || change.arrow_id" class="flex items-center space-x-2 mb-2">
                    <i :class="getItemIcon(change.change_source, change.category_name)" class="text-gray-500 dark:text-gray-400"></i>
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                      <template v-if="change.change_source === 'arrow'">
                        Arrow ID: {{ change.item_id }}
                      </template>
                      <template v-else>
                        {{ change.manufacturer_name }} {{ change.model_name }}
                      </template>
                    </span>
                    
                    <!-- Category badge -->
                    <span v-if="change.category_name" :class="[
                      'px-2 py-1 text-xs rounded-full',
                      getCategoryBadge(change.category_name)
                    ]">
                      {{ change.category_name }}
                    </span>
                  </div>
                </div>
                
                <!-- Enhanced timestamp -->
                <div class="text-right">
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    {{ formatTimestamp(change.created_at) }}
                  </div>
                  <div class="text-xs text-gray-400 dark:text-gray-500">
                    {{ formatDate(change.created_at) }}
                  </div>
                </div>
              </div>
              
              <!-- Enhanced change description -->
              <div class="mb-4">
                <p class="text-gray-900 dark:text-gray-100 font-medium">
                  {{ change.change_description }}
                </p>
              </div>
              
              <!-- Equipment Restore Action -->
              <div v-if="canShowRestoreButton(change)" class="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border-l-4 border-yellow-400">
                <div class="flex items-center justify-between">
                  <div class="flex items-center">
                    <i class="fas fa-undo text-yellow-600 dark:text-yellow-400 mr-2"></i>
                    <div>
                      <p class="text-sm font-medium text-yellow-800 dark:text-yellow-200">Equipment Deleted</p>
                      <p class="text-xs text-yellow-700 dark:text-yellow-300">This equipment can be restored if needed</p>
                    </div>
                  </div>
                  <CustomButton
                    @click="restoreEquipment(change)"
                    variant="filled"
                    size="small"
                    class="bg-yellow-600 text-white hover:bg-yellow-700 dark:bg-yellow-600 dark:hover:bg-yellow-700"
                    :disabled="restoringEquipment"
                  >
                    <i class="fas fa-undo mr-1"></i>
                    <span v-if="restoringEquipment">Restoring...</span>
                    <span v-else>Restore</span>
                  </CustomButton>
                </div>
              </div>
              
              <!-- Enhanced user note with styling -->
              <div v-if="change.change_reason" class="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border-l-4 border-amber-400">
                <div class="flex items-start">
                  <i class="fas fa-sticky-note text-amber-600 dark:text-amber-400 mt-0.5 mr-2"></i>
                  <div>
                    <p class="text-sm font-medium text-amber-800 dark:text-amber-200 mb-1">User Note:</p>
                    <p class="text-sm text-amber-700 dark:text-amber-300 italic">
                      "{{ change.change_reason }}"
                    </p>
                  </div>
                </div>
              </div>
              
              <!-- Enhanced Before/After values -->
              <div v-if="change.old_value || change.new_value" class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="flex items-center mb-3">
                  <i class="fas fa-exchange-alt text-gray-500 dark:text-gray-400 mr-2"></i>
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Field: {{ formatFieldName(change.field_name) }}
                  </span>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-if="change.old_value" class="space-y-2">
                    <div class="flex items-center">
                      <i class="fas fa-arrow-left text-red-500 mr-2"></i>
                      <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Before</span>
                    </div>
                    <div class="p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                      <p class="text-sm text-gray-900 dark:text-gray-100 font-mono break-words">
                        {{ formatValue(change.old_value) }}
                      </p>
                    </div>
                  </div>
                  
                  <div v-if="change.new_value" class="space-y-2">
                    <div class="flex items-center">
                      <i class="fas fa-arrow-right text-green-500 mr-2"></i>
                      <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">After</span>
                    </div>
                    <div class="p-3 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800">
                      <p class="text-sm text-gray-900 dark:text-gray-100 font-mono break-words">
                        {{ formatValue(change.new_value) }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Load more button -->
    <div v-if="filteredChanges.length > 0 && filteredChanges.length >= currentLimit" class="mt-8 text-center">
      <CustomButton
        @click="loadMoreChanges()"
        variant="outlined" 
        class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-800"
        :disabled="loading"
      >
        <i class="fas fa-chevron-down mr-2"></i>
        Load More Changes ({{ filteredChanges.length }}+ shown)
      </CustomButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useApi } from '@/composables/useApi'
import CustomButton from '@/components/CustomButton.vue'

const props = defineProps({
  bowSetupId: {
    type: Number,
    required: true
  },
  showHeader: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['error', 'statistics-updated'])

const api = useApi()
const loading = ref(false)
const changes = ref([])
const filteredChanges = ref([])
const selectedTimeFilter = ref('all')
const selectedChangeType = ref('')
const searchQuery = ref('')
const showOnlyWithNotes = ref(false)
const currentLimit = ref(50)

const timeFilters = [
  { value: 'all', label: 'All Time' },
  { value: 7, label: 'Last Week' },
  { value: 30, label: 'Last Month' },
  { value: 90, label: 'Last 3 Months' }
]

const loadChanges = async () => {
  loading.value = true
  try {
    const params = {
      limit: currentLimit.value
    }
    
    if (selectedTimeFilter.value !== 'all') {
      params.days_back = selectedTimeFilter.value
    }
    
    const response = await api.get(`/bow-setups/${props.bowSetupId}/change-log`, { params })
    changes.value = response.changes || []
    filterChanges()
    
    // Emit statistics update
    const stats = {
      total_changes: changes.value.length,
      arrow_changes_by_type: {},
      equipment_changes_by_type: {}
    }
    
    changes.value.forEach(change => {
      if (change.change_source === 'arrow') {
        stats.arrow_changes_by_type[change.change_type] = (stats.arrow_changes_by_type[change.change_type] || 0) + 1
      } else if (change.change_source === 'equipment') {
        stats.equipment_changes_by_type[change.change_type] = (stats.equipment_changes_by_type[change.change_type] || 0) + 1
      }
    })
    
    emit('statistics-updated', stats)
    
  } catch (error) {
    console.error('Error loading change history:', error)
    emit('error', 'Failed to load change history')
  } finally {
    loading.value = false
  }
}

const filterChanges = () => {
  let filtered = [...changes.value]
  
  // Filter by change type/source
  if (selectedChangeType.value) {
    filtered = filtered.filter(change => change.change_source === selectedChangeType.value)
  }
  
  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(change => 
      change.change_description?.toLowerCase().includes(query) ||
      change.change_reason?.toLowerCase().includes(query) ||
      change.old_value?.toLowerCase().includes(query) ||
      change.new_value?.toLowerCase().includes(query) ||
      change.manufacturer_name?.toLowerCase().includes(query) ||
      change.model_name?.toLowerCase().includes(query)
    )
  }
  
  // Filter by notes
  if (showOnlyWithNotes.value) {
    filtered = filtered.filter(change => change.change_reason && change.change_reason.trim())
  }
  
  filteredChanges.value = filtered
}

const clearFilters = () => {
  selectedChangeType.value = ''
  searchQuery.value = ''
  showOnlyWithNotes.value = false
  filterChanges()
}

const loadMoreChanges = async () => {
  currentLimit.value += 50
  await loadChanges()
}

// Enhanced styling functions
const getChangeTypeColor = (changeType, source) => {
  const colors = {
    arrow: {
      'arrow_added': 'border-emerald-500',
      'arrow_removed': 'border-red-500',
      'arrow_modified': 'border-blue-500',
      'specifications_changed': 'border-orange-500'
    },
    equipment: {
      'add': 'border-green-500',
      'remove': 'border-red-500',
      'modify': 'border-blue-500',
      'settings_change': 'border-orange-500',
      'activation_change': 'border-purple-500'
    },
    setup: {
      'created': 'border-indigo-500',
      'setup_modified': 'border-blue-500',
      'name_changed': 'border-yellow-500'
    }
  }
  return colors[source]?.[changeType] || 'border-gray-400'
}

const getChangeTypeIcon = (changeType, source) => {
  const icons = {
    arrow: {
      'arrow_added': 'fas fa-plus text-emerald-600',
      'arrow_removed': 'fas fa-minus text-red-600',
      'arrow_modified': 'fas fa-edit text-blue-600',
      'specifications_changed': 'fas fa-cog text-orange-600'
    },
    equipment: {
      'add': 'fas fa-plus text-green-600',
      'remove': 'fas fa-minus text-red-600',
      'modify': 'fas fa-edit text-blue-600',
      'settings_change': 'fas fa-cog text-orange-600',
      'activation_change': 'fas fa-toggle-on text-purple-600'
    },
    setup: {
      'created': 'fas fa-star text-indigo-600',
      'setup_modified': 'fas fa-wrench text-blue-600',
      'name_changed': 'fas fa-tag text-yellow-600'
    }
  }
  return icons[source]?.[changeType] || 'fas fa-circle text-gray-400'
}

const getChangeTypeBadge = (changeType, source) => {
  const badges = {
    arrow: {
      'arrow_added': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
      'arrow_removed': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'arrow_modified': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'specifications_changed': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
    },
    equipment: {
      'add': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'remove': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'modify': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'settings_change': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      'activation_change': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
    },
    setup: {
      'created': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      'setup_modified': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'name_changed': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    }
  }
  return badges[source]?.[changeType] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

const getSourceBadge = (source) => {
  const badges = {
    'arrow': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'equipment': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'setup': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  }
  return badges[source] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

const getCategoryBadge = (category) => {
  const badges = {
    'Arrow': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'String': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
    'Sight': 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-200',
    'Stabilizer': 'bg-violet-100 text-violet-800 dark:bg-violet-900 dark:text-violet-200',
    'Arrow Rest': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    'Weight': 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200',
    'Setup': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  }
  return badges[category] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

const getItemIcon = (source, category) => {
  if (source === 'arrow') {
    return 'fas fa-bullseye'
  }
  
  const icons = {
    'String': 'fas fa-link',
    'Sight': 'fas fa-crosshairs',
    'Scope': 'fas fa-search',
    'Stabilizer': 'fas fa-balance-scale',
    'Arrow Rest': 'fas fa-hand-paper',
    'Plunger': 'fas fa-bullseye',
    'Weight': 'fas fa-weight-hanging'
  }
  return icons[category] || 'fas fa-cog'
}

const formatChangeType = (changeType) => {
  const labels = {
    'arrow_added': 'Arrow Added',
    'arrow_removed': 'Arrow Removed',
    'arrow_modified': 'Arrow Modified',
    'specifications_changed': 'Specs Changed',
    'add': 'Added',
    'remove': 'Removed',
    'modify': 'Modified',
    'settings_change': 'Settings Changed',
    'activation_change': 'Status Changed',
    'created': 'Created',
    'setup_modified': 'Setup Modified',
    'name_changed': 'Name Changed'
  }
  return labels[changeType] || changeType
}

const formatFieldName = (fieldName) => {
  if (!fieldName) return 'General'
  return fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

// Equipment restore functionality
const restoringEquipment = ref(false)

const canShowRestoreButton = (change) => {
  // Show restore button for equipment removal changes that haven't been restored yet
  return change.change_source === 'equipment' && 
         change.change_type === 'remove' && 
         change.item_id && 
         !change.is_restored
}

const restoreEquipment = async (change) => {
  if (!change.item_id || restoringEquipment.value) return
  
  try {
    restoringEquipment.value = true
    
    await api.post(`/bow-setups/${props.bowSetupId}/equipment/${change.item_id}/restore`)
    
    // Mark this change as restored to hide the button
    change.is_restored = true
    
    // Emit success notification
    emit('equipment-restored', {
      equipmentName: change.manufacturer_name && change.model_name 
        ? `${change.manufacturer_name} ${change.model_name}`
        : 'Equipment',
      category: change.category_name
    })
    
    // Reload changes to show the restoration entry
    await loadChanges()
    
  } catch (error) {
    console.error('Error restoring equipment:', error)
    emit('error', `Failed to restore equipment: ${error.message || 'Unknown error'}`)
  } finally {
    restoringEquipment.value = false
  }
}

const formatTimestamp = (timestamp) => {
  // Ensure timestamp is properly parsed as UTC if it doesn't have timezone info
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (days > 7) {
    return date.toLocaleDateString()
  } else if (days > 0) {
    return `${days} day${days > 1 ? 's' : ''} ago`
  } else if (hours > 0) {
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else if (minutes > 0) {
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  } else {
    return 'Just now'
  }
}

const formatDate = (timestamp) => {
  // Create date and ensure it displays in local timezone
  const date = new Date(timestamp)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatValue = (value) => {
  if (!value) return 'N/A'
  
  try {
    // Try to parse as JSON for better formatting
    const parsed = JSON.parse(value)
    return JSON.stringify(parsed, null, 2)
  } catch {
    // Return as-is if not JSON
    return value
  }
}

// Watch for prop changes
watch(() => props.bowSetupId, () => {
  if (props.bowSetupId) {
    loadChanges()
  }
})

onMounted(() => {
  if (props.bowSetupId) {
    loadChanges()
  }
})

// Expose refresh function for parent components
defineExpose({
  refresh: loadChanges,
  clearFilters
})
</script>

<style scoped>
/* Enhanced timeline styling */
.enhanced-change-log-viewer .relative::before {
  content: '';
  position: absolute;
  left: 22px;
  top: 22px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

/* Smooth transitions for filter changes */
.enhanced-change-log-viewer .space-y-8 > div {
  transition: all 0.3s ease-in-out;
}

/* Enhanced hover effects */
.enhanced-change-log-viewer .bg-white:hover {
  transform: translateY(-2px);
}
</style>