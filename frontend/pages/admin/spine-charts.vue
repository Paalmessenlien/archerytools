<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-4">
          <!-- Navigation -->
          <div class="flex items-center space-x-4">
            <NuxtLink
              to="/admin"
              class="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
            >
              <i class="fas fa-arrow-left mr-2"></i>
              Back to Admin
            </NuxtLink>
            <div class="h-4 w-px bg-gray-300 dark:bg-gray-600"></div>
            <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Spine Chart Editor
            </h1>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center space-x-3">
            <CustomButton
              @click="showImportModal = true"
              variant="outlined"
              class="text-blue-600 border-blue-300 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-600"
            >
              <i class="fas fa-file-import mr-2"></i>
              Import Data
            </CustomButton>
            <CustomButton
              @click="exportAllCharts"
              variant="outlined"
              class="text-green-600 border-green-300 hover:bg-green-50 dark:text-green-400 dark:border-green-600"
            >
              <i class="fas fa-download mr-2"></i>
              Export All
            </CustomButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Chart Selection -->
      <div class="mb-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Select Spine Chart
        </h2>
        
        <!-- Chart Selector -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Bow Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Bow Type
            </label>
            <select
              v-model="selectedBowType"
              @change="loadAvailableManufacturers"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            >
              <option value="">Select Bow Type...</option>
              <option v-for="bowType in bowTypes" :key="bowType" :value="bowType">
                {{ bowType }}
              </option>
            </select>
          </div>

          <!-- Manufacturer -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Manufacturer
            </label>
            <select
              v-model="selectedManufacturer"
              @change="loadSpineChart"
              :disabled="!selectedBowType"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100 disabled:opacity-50"
            >
              <option value="">Select Manufacturer...</option>
              <option v-for="manufacturer in availableManufacturers" :key="manufacturer" :value="manufacturer">
                {{ manufacturer }}
              </option>
            </select>
          </div>

          <!-- Chart Actions -->
          <div class="flex items-end">
            <CustomButton
              @click="createNewChart"
              :disabled="!selectedBowType"
              variant="filled"
              class="bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              <i class="fas fa-plus mr-2"></i>
              New Chart
            </CustomButton>
          </div>
        </div>

        <!-- Chart Info -->
        <div v-if="currentChart" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="font-medium text-gray-900 dark:text-gray-100">
                {{ currentChart.bow_type }} - {{ currentChart.manufacturer }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ currentChart.data.length }} entries • Last modified: {{ formatDate(currentChart.updated_at) }}
              </p>
            </div>
            <div class="flex space-x-2">
              <CustomButton
                @click="duplicateChart"
                variant="outlined"
                size="small"
                class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600"
              >
                <i class="fas fa-copy mr-1"></i>
                Duplicate
              </CustomButton>
              <CustomButton
                @click="deleteChart"
                variant="outlined"
                size="small"
                class="text-red-600 border-red-300 hover:bg-red-50 dark:text-red-400 dark:border-red-600"
              >
                <i class="fas fa-trash mr-1"></i>
                Delete
              </CustomButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart Editor -->
      <div v-if="currentChart" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <!-- Editor Header -->
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              Chart Data
            </h2>
            <div class="flex items-center space-x-3">
              <span class="text-sm text-gray-500 dark:text-gray-400">
                Showing {{ currentChart.data.length }} entries
              </span>
              <CustomButton
                @click="saveChart"
                :disabled="!hasUnsavedChanges || saving"
                variant="filled"
                class="bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
              >
                <i v-if="saving" class="fas fa-spinner fa-spin mr-2"></i>
                <i v-else class="fas fa-save mr-2"></i>
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </CustomButton>
            </div>
          </div>
        </div>

        <!-- DataTable -->
        <div class="p-6">
          <SpineChartDataTable
            :data="currentChart.data"
            :loading="loading"
            :error="error"
            @data-change="handleDataChange"
            @row-add="handleRowAdd"
            @row-edit="handleRowEdit"
            @row-delete="handleRowDelete"
          />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
          <i class="fas fa-chart-line text-gray-400 dark:text-gray-500 text-xl"></i>
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          No Chart Selected
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Select a bow type and manufacturer to edit spine chart data, or create a new chart.
        </p>
        <CustomButton
          @click="selectedBowType = bowTypes[0]"
          variant="filled"
          class="bg-blue-600 text-white hover:bg-blue-700"
        >
          Get Started
        </CustomButton>
      </div>
    </div>

    <!-- Modals -->
    <SpineEntryEditModal
      :show="showEditModal"
      :entry="editingEntry"
      :is-edit="isEditMode"
      @save="handleEntrySave"
      @cancel="closeEditModal"
    />

    <ImportDataModal
      :show="showImportModal"
      :bow-type="selectedBowType"
      :manufacturer="selectedManufacturer"
      @import="handleImport"
      @cancel="showImportModal = false"
    />
  </div>
</template>

<script setup lang="ts">
// Component imports
import CustomButton from '@/components/CustomButton.vue'
import SpineChartDataTable from '~/components/admin/SpineChartDataTable.vue'
import SpineEntryEditModal from '~/components/admin/SpineEntryEditModal.vue'
import ImportDataModal from '~/components/admin/ImportDataModal.vue'

interface SpineGridEntry {
  draw_weight_range_lbs: string | number
  arrow_length_in: number
  spine: string
  arrow_size?: string
}

interface SpineChart {
  bow_type: string
  manufacturer: string
  data: SpineGridEntry[]
  updated_at: string
}

// Meta
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

// SEO
useSeoMeta({
  title: 'Spine Chart Editor - Admin',
  description: 'Full-page spine chart editor with import/export functionality'
})

// API - initialized lazily to avoid Pinia issues
let api: ReturnType<typeof useApi>
const getApi = () => {
  if (!api) { api = useApi() }
  return api
}

// State
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const hasUnsavedChanges = ref(false)

// Chart data
const bowTypes = ref(['Recurve', 'Compound', 'Traditional', 'Barebow'])
const selectedBowType = ref('')
const selectedManufacturer = ref('')
const availableManufacturers = ref<string[]>([])
const currentChart = ref<SpineChart | null>(null)

// Modals
const showEditModal = ref(false)
const showImportModal = ref(false)
const editingEntry = ref<SpineGridEntry | null>(null)
const editingIndex = ref(-1)
const isEditMode = ref(false)

// Methods
const loadAvailableManufacturers = async () => {
  if (!selectedBowType.value) return
  
  try {
    loading.value = true
    // Load manufacturers that have spine charts for this bow type
    const api = getApi()
    const response = await api.get(`/admin/spine-charts/manufacturers?bow_type=${selectedBowType.value}`)
    availableManufacturers.value = response.manufacturers || []
    
    // Reset manufacturer selection
    selectedManufacturer.value = ''
    currentChart.value = null
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load manufacturers'
  } finally {
    loading.value = false
  }
}

const loadSpineChart = async () => {
  if (!selectedBowType.value || !selectedManufacturer.value) return
  
  try {
    loading.value = true
    const api = getApi()
    const response = await api.get(`/admin/spine-charts?bow_type=${selectedBowType.value}&manufacturer=${selectedManufacturer.value}`)
    
    if (response.chart) {
      currentChart.value = {
        bow_type: selectedBowType.value,
        manufacturer: selectedManufacturer.value,
        data: response.chart.data || [],
        updated_at: response.chart.updated_at || new Date().toISOString()
      }
      hasUnsavedChanges.value = false
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load spine chart'
    currentChart.value = null
  } finally {
    loading.value = false
  }
}

const createNewChart = () => {
  if (!selectedBowType.value) return
  
  // Set a default manufacturer if none selected
  if (!selectedManufacturer.value) {
    selectedManufacturer.value = 'Custom'
  }
  
  currentChart.value = {
    bow_type: selectedBowType.value,
    manufacturer: selectedManufacturer.value,
    data: [],
    updated_at: new Date().toISOString()
  }
  hasUnsavedChanges.value = true
}

const saveChart = async () => {
  if (!currentChart.value) return
  
  try {
    saving.value = true
    const api = getApi()
    
    await api.post('/admin/spine-charts', {
      bow_type: currentChart.value.bow_type,
      manufacturer: currentChart.value.manufacturer,
      data: currentChart.value.data
    })
    
    hasUnsavedChanges.value = false
    showNotification('Chart saved successfully', 'success')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save chart'
    showNotification('Failed to save chart', 'error')
  } finally {
    saving.value = false
  }
}

const duplicateChart = async () => {
  if (!currentChart.value) return
  
  const newManufacturer = prompt('Enter manufacturer name for the duplicated chart:', `${currentChart.value.manufacturer} Copy`)
  if (!newManufacturer) return
  
  selectedManufacturer.value = newManufacturer
  currentChart.value = {
    ...currentChart.value,
    manufacturer: newManufacturer,
    updated_at: new Date().toISOString()
  }
  hasUnsavedChanges.value = true
}

const deleteChart = async () => {
  if (!currentChart.value) return
  
  const confirmed = confirm(`Are you sure you want to delete the spine chart for ${currentChart.value.bow_type} - ${currentChart.value.manufacturer}?`)
  if (!confirmed) return
  
  try {
    const api = getApi()
    await api.delete(`/admin/spine-charts?bow_type=${currentChart.value.bow_type}&manufacturer=${currentChart.value.manufacturer}`)
    
    currentChart.value = null
    selectedManufacturer.value = ''
    showNotification('Chart deleted successfully', 'success')
    loadAvailableManufacturers()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to delete chart'
    showNotification('Failed to delete chart', 'error')
  }
}

const exportAllCharts = async () => {
  try {
    const api = getApi()
    const response = await api.get('/admin/spine-charts/export')
    
    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', 'all-spine-charts.json')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    showNotification('All charts exported successfully', 'success')
  } catch (err) {
    showNotification('Failed to export charts', 'error')
  }
}

// DataTable event handlers
const handleDataChange = (data: SpineGridEntry[]) => {
  if (currentChart.value) {
    currentChart.value.data = data
    hasUnsavedChanges.value = true
  }
}

const handleRowAdd = (entry: SpineGridEntry) => {
  editingEntry.value = entry
  editingIndex.value = -1
  isEditMode.value = false
  showEditModal.value = true
}

const handleRowEdit = (index: number, entry: SpineGridEntry) => {
  editingEntry.value = { ...entry }
  editingIndex.value = index
  isEditMode.value = true
  showEditModal.value = true
}

const handleRowDelete = (index: number) => {
  if (!currentChart.value) return
  
  const confirmed = confirm('Are you sure you want to delete this entry?')
  if (confirmed) {
    currentChart.value.data.splice(index, 1)
    hasUnsavedChanges.value = true
  }
}

const handleEntrySave = (entry: SpineGridEntry) => {
  if (!currentChart.value) return
  
  if (isEditMode.value && editingIndex.value >= 0) {
    // Edit existing entry
    currentChart.value.data[editingIndex.value] = { ...entry }
  } else {
    // Add new entry
    currentChart.value.data.push({ ...entry })
  }
  
  hasUnsavedChanges.value = true
  closeEditModal()
}

const closeEditModal = () => {
  showEditModal.value = false
  editingEntry.value = null
  editingIndex.value = -1
  isEditMode.value = false
}

const handleImport = (importedData: SpineGridEntry[]) => {
  if (!currentChart.value) return
  
  currentChart.value.data = [...currentChart.value.data, ...importedData]
  hasUnsavedChanges.value = true
  showImportModal.value = false
  showNotification(`Imported ${importedData.length} entries successfully`, 'success')
}

// Utilities
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// Notifications
const notification = ref({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'warning'
})

const showNotification = (message: string, type: 'success' | 'error' | 'warning' = 'success') => {
  notification.value = { show: true, message, type }
  setTimeout(() => {
    notification.value.show = false
  }, 5000)
}

const hideNotification = () => {
  notification.value.show = false
}

// Lifecycle
onMounted(() => {
  // Auto-select first bow type if available
  if (bowTypes.value.length > 0) {
    selectedBowType.value = bowTypes.value[0]
    loadAvailableManufacturers()
  }
})

// Watch for unsaved changes before navigation
onBeforeRouteLeave((to, from) => {
  if (hasUnsavedChanges.value) {
    const confirmed = confirm('You have unsaved changes. Are you sure you want to leave?')
    if (!confirmed) {
      return false
    }
  }
})
</script>

<style scoped>
/* Page-specific styling */
.min-h-screen {
  min-height: 100vh;
}

/* Notification animations */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}
</style>