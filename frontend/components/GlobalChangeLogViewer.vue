<template>
  <div class="global-change-log-viewer">
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
            @change="loadChanges()"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          >
            <option value="">All Activities</option>
            <option value="setup">Bow Setup Changes</option>
            <option value="equipment">Equipment Changes</option>
            <option value="arrow">Arrow Changes</option>
          </select>
        </div>
        
        <!-- Time Range Filter -->
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Time Range
          </label>
          <select
            v-model="selectedTimeFilter"
            @change="loadChanges()"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          >
            <option value="">All Time</option>
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="90">Last 90 Days</option>
          </select>
        </div>
        
        <!-- Refresh Button -->
        <div class="flex items-end">
          <CustomButton
            @click="loadChanges()"
            variant="outlined"
            class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-800"
            :disabled="loading"
          >
            <i :class="['fas fa-sync-alt mr-2', loading ? 'animate-spin' : '']"></i>
            Refresh
          </CustomButton>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && changes.length === 0" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-3"></div>
      <p class="text-gray-600 dark:text-gray-400">Loading activity history...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && changes.length === 0" class="text-center py-12">
      <i class="fas fa-history text-4xl text-gray-400 mb-4"></i>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Activities Found</h3>
      <p class="text-gray-600 dark:text-gray-400">
        {{ selectedChangeType || selectedTimeFilter ? 'Try adjusting your filters to see more activities.' : 'Start using the platform to see your activity history here.' }}
      </p>
    </div>

    <!-- Activity Timeline -->
    <div v-else class="space-y-4">
      <div v-for="change in changes" :key="`${change.change_source}-${change.id}`" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 transition-all hover:shadow-md">
        <div class="flex items-start space-x-4">
          <!-- Activity Icon -->
          <div class="flex-shrink-0">
            <div :class="getActivityIconClass(change.change_source, change.change_type)">
              <i :class="getActivityIcon(change.change_source, change.change_type)"></i>
            </div>
          </div>

          <!-- Activity Content -->
          <div class="flex-1 min-w-0">
            <!-- Activity Header -->
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <span :class="getActivityBadgeClass(change.change_source)">
                  {{ getActivityTypeLabel(change.change_source) }}
                </span>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  {{ formatChangeType(change.change_type) }}
                </span>
              </div>
              <time class="text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(change.created_at) }}
              </time>
            </div>

            <!-- Activity Details -->
            <div class="space-y-1">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                {{ change.change_description || getDefaultDescription(change) }}
              </p>
              
              <!-- Bow Setup Context -->
              <div v-if="change.bow_setup_name" class="flex items-center text-xs text-gray-500 dark:text-gray-400">
                <i class="fas fa-crosshairs mr-1"></i>
                <span>{{ change.bow_setup_name }}</span>
              </div>

              <!-- Equipment Context -->
              <div v-if="change.manufacturer_name || change.model_name" class="flex items-center text-xs text-gray-500 dark:text-gray-400">
                <i class="fas fa-cog mr-1"></i>
                <span>{{ [change.manufacturer_name, change.model_name, change.category_name].filter(Boolean).join(' - ') }}</span>
              </div>

              <!-- Field Changes -->
              <div v-if="change.field_name && (change.old_value || change.new_value)" class="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
                <span class="font-medium">{{ change.field_name }}:</span>
                <span v-if="change.old_value" class="text-red-600 dark:text-red-400 line-through ml-1">{{ change.old_value }}</span>
                <span v-if="change.new_value" class="text-green-600 dark:text-green-400 ml-1">{{ change.new_value }}</span>
              </div>

              <!-- Change Reason -->
              <div v-if="change.change_reason || change.user_note" class="mt-2 text-xs text-gray-600 dark:text-gray-400 italic">
                "{{ change.change_reason || change.user_note }}"
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="text-center pt-4">
        <CustomButton
          @click="loadMoreChanges()"
          variant="outlined"
          :disabled="loading"
          class="text-blue-600 border-blue-300 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-600 dark:hover:bg-blue-900/20"
        >
          <i v-if="loading" class="fas fa-spinner animate-spin mr-2"></i>
          <i v-else class="fas fa-chevron-down mr-2"></i>
          Load More Activities
        </CustomButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

// Emits
const emit = defineEmits(['statistics-updated', 'error'])

// Composables
const api = useApi()

// State
const changes = ref([])
const loading = ref(false)
const selectedChangeType = ref('')
const selectedTimeFilter = ref('')
const currentPage = ref(1)
const hasMore = ref(true)
const pageSize = 20

// Methods
const loadChanges = async (reset = true) => {
  if (reset) {
    currentPage.value = 1
    changes.value = []
  }

  try {
    loading.value = true
    
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      limit: pageSize.toString()
    })
    
    if (selectedChangeType.value) {
      params.append('change_source', selectedChangeType.value)
    }
    
    if (selectedTimeFilter.value) {
      params.append('days_back', selectedTimeFilter.value)
    }

    const response = await api.get(`/change-log/global?${params}`)
    
    if (reset) {
      changes.value = response.changes || []
    } else {
      changes.value.push(...(response.changes || []))
    }
    
    hasMore.value = (response.changes || []).length === pageSize
    
    // Emit statistics update
    if (response.statistics) {
      emit('statistics-updated', response.statistics)
    }
    
  } catch (error) {
    console.error('Error loading global changes:', error)
    emit('error', 'Failed to load activity history')
  } finally {
    loading.value = false
  }
}

const loadMoreChanges = () => {
  currentPage.value++
  loadChanges(false)
}

// Helper functions
const getActivityIcon = (source, type) => {
  const iconMap = {
    setup: 'fas fa-crosshairs',
    equipment: 'fas fa-cog',
    arrow: 'fas fa-bullseye'
  }
  return iconMap[source] || 'fas fa-edit'
}

const getActivityIconClass = (source, type) => {
  const baseClasses = 'w-8 h-8 rounded-full flex items-center justify-center text-sm'
  const colorMap = {
    setup: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
    equipment: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
    arrow: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
  }
  return `${baseClasses} ${colorMap[source] || 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}`
}

const getActivityBadgeClass = (source) => {
  const baseClasses = 'px-2 py-1 text-xs font-medium rounded-full'
  const colorMap = {
    setup: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    equipment: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    arrow: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
  }
  return `${baseClasses} ${colorMap[source] || 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'}`
}

const getActivityTypeLabel = (source) => {
  const labels = {
    setup: 'Setup',
    equipment: 'Equipment',
    arrow: 'Arrow'
  }
  return labels[source] || 'Activity'
}

const formatChangeType = (changeType) => {
  return changeType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getDefaultDescription = (change) => {
  const source = getActivityTypeLabel(change.change_source)
  const type = formatChangeType(change.change_type)
  return `${source} ${type}`
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))
  
  if (diffInHours < 1) {
    return 'Just now'
  } else if (diffInHours < 24) {
    return `${diffInHours}h ago`
  } else if (diffInHours < 48) {
    return 'Yesterday'
  } else {
    return date.toLocaleDateString()
  }
}

// Lifecycle
onMounted(() => {
  loadChanges()
})
</script>

<style scoped>
.global-change-log-viewer {
  /* Custom styles if needed */
}
</style>