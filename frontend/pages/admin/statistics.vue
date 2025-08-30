<template>
  <div>
    <!-- Admin Notice Banner -->
    <div class="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-chart-bar text-red-600 dark:text-red-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-red-800 dark:text-red-200">Usage Statistics</h4>
          <p class="text-xs text-red-700 dark:text-red-300 mt-1">
            Comprehensive platform usage analytics and metrics
          </p>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Usage Statistics</h1>
          <p class="text-gray-600 dark:text-gray-300">Platform metrics and user activity analytics</p>
        </div>
        <div class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
          <span>{{ lastUpdated ? `Updated ${lastUpdated}` : 'Loading...' }}</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !statistics" class="flex items-center justify-center py-12">
      <div class="flex items-center space-x-3">
        <div class="w-6 h-6 border-b-2 border-blue-600 rounded-full animate-spin dark:border-purple-400"></div>
        <span class="text-gray-600 dark:text-gray-300">Loading statistics...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <div class="flex items-center">
        <i class="fas fa-exclamation-circle text-red-600 dark:text-red-400 mr-3"></i>
        <div>
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Failed to load statistics</h3>
          <p class="text-xs text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Statistics Content -->
    <div v-else-if="statistics" class="space-y-6">
      <!-- Overview Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <i class="fas fa-users text-blue-600 dark:text-blue-400 text-2xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Users</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ statistics.overview.total_users }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <i class="fas fa-check-circle text-green-600 dark:text-green-400 text-2xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Approved Users</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ statistics.overview.approved_users }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <i class="fas fa-bow-arrow text-orange-600 dark:text-orange-400 text-2xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Bow Setups</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ statistics.overview.total_bow_setups }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <i class="fas fa-database text-purple-600 dark:text-purple-400 text-2xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Arrows</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ statistics.overview.total_arrows }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Secondary Metrics -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <i class="fas fa-clock text-blue-600 dark:text-blue-400 text-2xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Active (30d)</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ statistics.overview.active_users_30d }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <i class="fas fa-cogs text-green-600 dark:text-green-400 text-2xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Equipment</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ statistics.overview.total_equipment }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <i class="fas fa-book text-indigo-600 dark:text-indigo-400 text-2xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Journal Entries</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ statistics.overview.journal_entries }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <i class="fas fa-industry text-gray-600 dark:text-gray-400 text-2xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Manufacturers</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ statistics.overview.active_manufacturers }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-chart-line mr-2"></i>
          Recent Activity (Last 7 Days)
        </h3>
        <div class="grid grid-cols-2 gap-6">
          <div class="text-center">
            <div class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ statistics.recent_activity.new_users_7d }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400">New Users</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold text-green-600 dark:text-green-400">{{ statistics.recent_activity.new_setups_7d }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400">New Bow Setups</div>
          </div>
        </div>
      </div>

      <!-- Arrows by Manufacturer Chart -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-chart-pie mr-2"></i>
          Arrows by Manufacturer
        </h3>
        <div class="h-64">
          <canvas ref="manufacturerChart"></canvas>
        </div>
      </div>

      <!-- Equipment by Category Chart -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-chart-bar mr-2"></i>
          Equipment by Category
        </h3>
        <div class="h-64">
          <canvas ref="equipmentChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// Authentication middleware
definePageMeta({
  middleware: 'admin'
})

// Set page title
useHead({
  title: 'Usage Statistics - Admin',
  meta: [
    { name: 'description', content: 'Usage statistics and analytics for ArcheryTool platform administrators' }
  ]
})

// Reactive data
const statistics = ref(null)
const loading = ref(false)
const error = ref(null)
const lastUpdated = ref(null)
const notification = ref({ show: false, type: '', message: '' })

// Chart references
const manufacturerChart = ref(null)
const equipmentChart = ref(null)
let manufacturerChartInstance = null
let equipmentChartInstance = null
let refreshInterval = null

// API composable  
const api = useApi()

// Fetch statistics
const fetchStatistics = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.get('/admin/statistics')
    
    statistics.value = response
    lastUpdated.value = new Date().toLocaleTimeString()
    
    // Update charts
    nextTick(() => {
      updateCharts()
    })
    
  } catch (err) {
    console.error('Failed to fetch statistics:', err)
    error.value = err.message || 'Failed to load statistics'
  } finally {
    loading.value = false
  }
}

// Update charts
const updateCharts = () => {
  if (!statistics.value || !window.Chart) return

  // Manufacturer Chart
  if (manufacturerChart.value) {
    const ctx = manufacturerChart.value.getContext('2d')
    
    if (manufacturerChartInstance) {
      manufacturerChartInstance.destroy()
    }
    
    manufacturerChartInstance = new window.Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: statistics.value.breakdowns.arrows_by_manufacturer.map(item => item.manufacturer),
        datasets: [{
          data: statistics.value.breakdowns.arrows_by_manufacturer.map(item => item.count),
          backgroundColor: [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
            '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: document.documentElement.classList.contains('dark') ? '#E5E7EB' : '#374151'
            }
          }
        }
      }
    })
  }

  // Equipment Chart
  if (equipmentChart.value) {
    const ctx = equipmentChart.value.getContext('2d')
    
    if (equipmentChartInstance) {
      equipmentChartInstance.destroy()
    }
    
    equipmentChartInstance = new window.Chart(ctx, {
      type: 'bar',
      data: {
        labels: statistics.value.breakdowns.equipment_by_category.map(item => item.category || 'Uncategorized'),
        datasets: [{
          label: 'Equipment Count',
          data: statistics.value.breakdowns.equipment_by_category.map(item => item.count),
          backgroundColor: '#3B82F6',
          borderColor: '#2563EB',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              color: document.documentElement.classList.contains('dark') ? '#E5E7EB' : '#374151'
            },
            grid: {
              color: document.documentElement.classList.contains('dark') ? '#374151' : '#E5E7EB'
            }
          },
          x: {
            ticks: {
              color: document.documentElement.classList.contains('dark') ? '#E5E7EB' : '#374151'
            },
            grid: {
              color: document.documentElement.classList.contains('dark') ? '#374151' : '#E5E7EB'
            }
          }
        }
      }
    })
  }
}

// Show notification
const showNotification = (type, message) => {
  notification.value = { show: true, type, message }
  setTimeout(() => {
    notification.value.show = false
  }, 3000)
}

// Hide notification
const hideNotification = () => {
  notification.value.show = false
}

// Auto-refresh
const startAutoRefresh = () => {
  refreshInterval = setInterval(() => {
    fetchStatistics()
  }, 30000) // Refresh every 30 seconds
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// Lifecycle
onMounted(() => {
  fetchStatistics()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  if (manufacturerChartInstance) {
    manufacturerChartInstance.destroy()
  }
  if (equipmentChartInstance) {
    equipmentChartInstance.destroy()
  }
})
</script>

<style scoped>
/* Custom styles for charts */
canvas {
  max-height: 300px;
}
</style>