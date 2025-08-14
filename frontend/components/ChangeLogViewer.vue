<template>
  <div class="change-log-viewer">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        <i class="fas fa-history mr-2 text-blue-600 dark:text-blue-400"></i>
        Change History
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

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-3"></div>
      <p class="text-gray-600 dark:text-gray-400">Loading change history...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="changes.length === 0" class="text-center py-8">
      <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="fas fa-history text-2xl text-gray-400"></i>
      </div>
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Changes Yet</h4>
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        Start making equipment modifications to see your change history here.
      </p>
    </div>

    <!-- Timeline View -->
    <div v-else class="relative">
      <!-- Timeline line -->
      <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>
      
      <div class="space-y-6">
        <div
          v-for="(change, index) in changes"
          :key="`${change.change_source}-${change.id}`"
          class="relative flex items-start"
        >
          <!-- Timeline dot -->
          <div :class="[
            'absolute left-2 w-4 h-4 rounded-full border-2 bg-white dark:bg-gray-800',
            getChangeTypeColor(change.change_type)
          ]">
            <i :class="[
              'absolute inset-0 flex items-center justify-center text-xs',
              getChangeTypeIcon(change.change_type)
            ]"></i>
          </div>
          
          <!-- Change content -->
          <div class="ml-12 flex-1">
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <!-- Change header -->
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <span :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    getChangeTypeBadge(change.change_type)
                  ]">
                    {{ formatChangeType(change.change_type) }}
                  </span>
                  
                  <!-- Equipment info -->
                  <span v-if="change.manufacturer_name" class="text-sm text-gray-600 dark:text-gray-400">
                    {{ change.manufacturer_name }} {{ change.model_name }}
                  </span>
                  
                  <!-- Category badge -->
                  <span v-if="change.category_name" :class="[
                    'px-2 py-1 text-xs rounded-full',
                    getCategoryBadge(change.category_name)
                  ]">
                    {{ change.category_name }}
                  </span>
                </div>
                
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  {{ formatTimestamp(change.created_at) }}
                </div>
              </div>
              
              <!-- Change description -->
              <p class="text-gray-900 dark:text-gray-100 mb-2">
                {{ change.change_description }}
              </p>
              
              <!-- Change reason (if provided) -->
              <p v-if="change.change_reason" class="text-sm text-gray-600 dark:text-gray-400 mb-2 italic">
                "{{ change.change_reason }}"
              </p>
              
              <!-- Before/After values (if available) -->
              <div v-if="change.old_value || change.new_value" class="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-if="change.old_value">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Before</span>
                    <p class="text-sm text-gray-900 dark:text-gray-100 mt-1 font-mono bg-white dark:bg-gray-800 px-2 py-1 rounded border">
                      {{ formatValue(change.old_value) }}
                    </p>
                  </div>
                  <div v-if="change.new_value">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">After</span>
                    <p class="text-sm text-gray-900 dark:text-gray-100 mt-1 font-mono bg-white dark:bg-gray-800 px-2 py-1 rounded border">
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

    <!-- Load more button -->
    <div v-if="changes.length > 0 && changes.length >= currentLimit" class="mt-6 text-center">
      <CustomButton
        @click="loadMoreChanges()"
        variant="outlined" 
        class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-800"
        :disabled="loading"
      >
        <i class="fas fa-chevron-down mr-2"></i>
        Load More Changes
      </CustomButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useApi } from '@/composables/useApi'
import CustomButton from '@/components/CustomButton.vue'

const props = defineProps({
  bowSetupId: {
    type: Number,
    required: true
  },
  equipmentId: {
    type: Number,
    required: false
  }
})

const emit = defineEmits(['error'])

const api = useApi()
const loading = ref(false)
const changes = ref([])
const selectedTimeFilter = ref('all')
const currentLimit = ref(20)

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
    
    let endpoint
    if (props.equipmentId) {
      endpoint = `/bow-setups/${props.bowSetupId}/equipment/${props.equipmentId}/change-log`
    } else {
      endpoint = `/bow-setups/${props.bowSetupId}/change-log`
    }
    
    const response = await api.get(endpoint, { params })
    changes.value = response.changes || []
  } catch (error) {
    console.error('Error loading change history:', error)
    emit('error', 'Failed to load change history')
  } finally {
    loading.value = false
  }
}

const loadMoreChanges = async () => {
  currentLimit.value += 20
  await loadChanges()
}

const getChangeTypeColor = (changeType) => {
  const colors = {
    'add': 'border-green-500',
    'remove': 'border-red-500', 
    'modify': 'border-blue-500',
    'settings_change': 'border-orange-500',
    'activation_change': 'border-purple-500',
    'created': 'border-indigo-500',
    'setup_modified': 'border-blue-500',
    'name_changed': 'border-yellow-500'
  }
  return colors[changeType] || 'border-gray-400'
}

const getChangeTypeIcon = (changeType) => {
  const icons = {
    'add': 'fas fa-plus text-green-600',
    'remove': 'fas fa-minus text-red-600',
    'modify': 'fas fa-edit text-blue-600',
    'settings_change': 'fas fa-cog text-orange-600',
    'activation_change': 'fas fa-toggle-on text-purple-600',
    'created': 'fas fa-star text-indigo-600',
    'setup_modified': 'fas fa-wrench text-blue-600',
    'name_changed': 'fas fa-tag text-yellow-600'
  }
  return icons[changeType] || 'fas fa-circle text-gray-400'
}

const getChangeTypeBadge = (changeType) => {
  const badges = {
    'add': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'remove': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'modify': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'settings_change': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    'activation_change': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'created': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    'setup_modified': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'name_changed': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  }
  return badges[changeType] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

const getCategoryBadge = (category) => {
  const badges = {
    'String': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
    'Sight': 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-200',
    'Stabilizer': 'bg-violet-100 text-violet-800 dark:bg-violet-900 dark:text-violet-200',
    'Arrow Rest': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    'Weight': 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200'
  }
  return badges[category] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

const formatChangeType = (changeType) => {
  const labels = {
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

const formatTimestamp = (timestamp) => {
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

onMounted(() => {
  loadChanges()
})

// Expose refresh function for parent components
defineExpose({
  refresh: loadChanges
})
</script>

<style scoped>
/* Timeline styling enhancements */
.change-log-viewer .relative::before {
  content: '';
  position: absolute;
  left: 14px;
  top: 14px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
</style>