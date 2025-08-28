<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="px-1 py-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div class="animate-pulse">
        <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-64 mb-6"></div>
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-4"></div>
          <div class="space-y-3">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="px-1 py-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <i class="fas fa-exclamation-triangle text-4xl text-red-600 dark:text-red-400 mb-4"></i>
        <h2 class="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">Equipment Not Found</h2>
        <p class="text-red-600 dark:text-red-400 mb-4">{{ error }}</p>
        <NuxtLink
          to="/my-setup"
          class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          <i class="fas fa-arrow-left mr-2"></i>
          Back to Equipment
        </NuxtLink>
      </div>
    </div>

    <!-- Equipment Details -->
    <div v-else-if="equipment" class="px-1 py-4 mx-auto max-w-7xl sm:px-6 lg:px-8 pb-24 md:pb-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
        <div class="min-w-0">
          <div class="flex items-center space-x-2 mb-2">
            <NuxtLink
              :to="returnPath"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              <i class="fas fa-arrow-left mr-1"></i>
              {{ returnLabel }}
            </NuxtLink>
          </div>
          <div class="flex items-center space-x-3 mb-2">
            <div :class="[
              'w-12 h-12 flex items-center justify-center rounded-lg flex-shrink-0',
              getCategoryIcon(equipment.category_name).bgClass
            ]">
              <i :class="[
                'text-xl',
                getCategoryIcon(equipment.category_name).iconClass
              ]"></i>
            </div>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
                {{ equipment.manufacturer }} {{ equipment.model_name }}
              </h1>
              <p class="text-gray-600 dark:text-gray-300">{{ equipment.category_name }}</p>
            </div>
          </div>
        </div>
        
        <div class="flex gap-2">
          <CustomButton @click="editEquipment" variant="outlined">
            <i class="fas fa-edit mr-2"></i>
            Edit
          </CustomButton>
        </div>
      </div>

      <!-- Quick Stats -->
      <md-chip-set class="mb-6">
        <md-assist-chip :label="'Category: ' + equipment.category_name">
          <i :class="getCategoryIcon(equipment.category_name).iconClass + ' fa-icon'" slot="icon"></i>
        </md-assist-chip>
        <md-assist-chip v-if="equipment.is_active" label="Active">
          <i class="fas fa-check-circle fa-icon" slot="icon" style="color: #16a34a;"></i>
        </md-assist-chip>
        <md-assist-chip v-else label="Inactive">
          <i class="fas fa-times-circle fa-icon" slot="icon" style="color: #dc2626;"></i>
        </md-assist-chip>
        <md-assist-chip v-if="equipment.bow_setups?.length" :label="`${equipment.bow_setups.length} setup${equipment.bow_setups.length === 1 ? '' : 's'}`">
          <i class="fas fa-crosshairs fa-icon" slot="icon" style="color: #7c3aed;"></i>
        </md-assist-chip>
      </md-chip-set>

      <!-- Equipment Image -->
      <div v-if="equipment.image_url" class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">Equipment Image</h3>
        <img 
          :src="equipment.image_url" 
          :alt="`${equipment.manufacturer} ${equipment.model_name}`"
          class="max-w-md mx-auto rounded-lg shadow-md"
          @error="imageError = true"
        />
        <div v-if="imageError" class="text-center text-gray-500 py-8">
          Image not available
        </div>
      </div>

      <!-- Basic Information -->
      <div class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">Equipment Information</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Manufacturer</label>
            <p class="text-lg text-gray-900 dark:text-gray-100">{{ equipment.manufacturer }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Model</label>
            <p class="text-lg text-gray-900 dark:text-gray-100">{{ equipment.model_name }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
            <p class="text-lg text-gray-900 dark:text-gray-100">{{ equipment.category_name }}</p>
          </div>
          
          <div v-if="equipment.specifications && Object.keys(equipment.specifications).length > 0" class="md:col-span-2 lg:col-span-3">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Specifications</label>
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <div
                  v-for="(value, key) in equipment.specifications"
                  :key="key"
                  class="flex items-center justify-between py-2"
                >
                  <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {{ formatSpecificationKey(key) }}:
                  </span>
                  <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    {{ formatSpecificationValue(value) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
            <span :class="[
              'px-3 py-1 rounded-full text-sm font-medium',
              equipment.is_active 
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
            ]">
              {{ equipment.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          
          <div v-if="equipment.purchase_date">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Purchase Date</label>
            <p class="text-lg text-gray-900 dark:text-gray-100">{{ formatDate(equipment.purchase_date) }}</p>
          </div>
        </div>

        <!-- Notes -->
        <div v-if="equipment.notes" class="mt-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Notes</label>
          <p class="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">{{ equipment.notes }}</p>
        </div>
      </div>

      <!-- Settings/Specifications -->
      <div v-if="equipment.settings && Object.keys(equipment.settings).length > 0" class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">Settings & Configuration</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="(value, key) in equipment.settings" :key="key">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ formatFieldName(key) }}
            </label>
            <p class="text-lg text-gray-900 dark:text-gray-100">{{ value }}</p>
          </div>
        </div>
      </div>

      <!-- Usage in Setups -->
      <div v-if="equipment.bow_setups && equipment.bow_setups.length > 0" class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">
          Used in Bow Setups
          <span class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full">
            {{ equipment.bow_setups.length }}
          </span>
        </h3>
        
        <div class="space-y-3">
          <div
            v-for="setup in equipment.bow_setups"
            :key="setup.id"
            class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
          >
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <i class="fas fa-crosshairs text-blue-600 dark:text-blue-400"></i>
              </div>
              <div>
                <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ setup.name }}</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">{{ setup.bow_type }} Setup</p>
              </div>
            </div>
            <NuxtLink
              :to="`/setups/${setup.id}`"
              class="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              <i class="fas fa-external-link-alt"></i>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">Quick Actions</h3>
        
        <div class="flex flex-wrap gap-3">
          <CustomButton @click="editEquipment" variant="primary">
            <i class="fas fa-edit mr-2"></i>
            Edit Equipment
          </CustomButton>
          
          <CustomButton @click="toggleActive" variant="outlined" :disabled="toggleLoading">
            <i :class="[
              'mr-2',
              equipment.is_active ? 'fas fa-pause' : 'fas fa-play'
            ]"></i>
            {{ equipment.is_active ? 'Deactivate' : 'Activate' }}
          </CustomButton>
          
          <CustomButton @click="duplicateEquipment" variant="outlined">
            <i class="fas fa-copy mr-2"></i>
            Duplicate
          </CustomButton>
          
          <CustomButton @click="exportEquipment" variant="outlined">
            <i class="fas fa-download mr-2"></i>
            Export Info
          </CustomButton>
        </div>
      </div>

      <!-- Equipment Journal -->
      <EquipmentJournal
        :equipment-id="equipmentId"
        :equipment="equipment"
        @statistics-updated="handleJournalStatistics"
      />
    </div>

    <!-- Equipment Edit Modal -->
    <div v-if="editingEquipment && equipment" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-edit text-blue-600 mr-2"></i>
              Edit Equipment
              <span class="text-base font-normal text-gray-600 dark:text-gray-400">
                - {{ equipment.manufacturer }} {{ equipment.model_name }}
              </span>
            </h3>
            <CustomButton @click="editingEquipment = false" variant="text" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times text-xl"></i>
            </CustomButton>
          </div>
        </div>

        <!-- Content -->
        <div class="p-6">
          <CustomEquipmentForm
            :bow-setup="equipment.setup_context"
            :initial-equipment="equipment"
            :is-editing="true"
            @equipment-updated="handleEquipmentUpdated"
            @cancel="editingEquipment = false"
          />
        </div>
      </div>
    </div>

    <!-- Notification Toast -->
    <div
      v-if="notification.show"
      class="fixed bottom-4 right-4 z-50 transition-all duration-300"
      :class="getNotificationClasses(notification.type)"
    >
      <div class="flex items-center">
        <i :class="getNotificationIcon(notification.type)" class="mr-2"></i>
        {{ notification.message }}
        <button @click="hideNotification" class="ml-4 opacity-70 hover:opacity-100">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import EquipmentJournal from '~/components/EquipmentJournal.vue'
import CustomButton from '~/components/CustomButton.vue'
import CustomEquipmentForm from '~/components/CustomEquipmentForm.vue'

// Meta information
definePageMeta({
  title: 'Equipment Details',
  middleware: ['auth-check']
})

// Composables
const route = useRoute()
const router = useRouter()
const api = useApi()

// State
const equipment = ref(null)
const loading = ref(true)
const error = ref('')
const imageError = ref(false)
const toggleLoading = ref(false)
const journalStatistics = ref({})
const editingEquipment = ref(false)

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Get equipment ID from route
const equipmentId = computed(() => route.params.id)

// Navigation helpers
const returnPath = computed(() => {
  const from = route.query.from
  switch (from) {
    case 'setup':
      return `/setups/${route.query.setup_id}`
    default:
      return '/my-setup'
  }
})

const returnLabel = computed(() => {
  const from = route.query.from
  switch (from) {
    case 'setup':
      return 'Back to Setup'
    default:
      return 'Back to Equipment'
  }
})

// Methods
const loadEquipmentDetails = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await api.get(`/equipment/${equipmentId.value}`)
    equipment.value = response.equipment
    
  } catch (err) {
    console.error('Error loading equipment details:', err)
    error.value = err.message || 'Failed to load equipment details'
  } finally {
    loading.value = false
  }
}

const editEquipment = () => {
  editingEquipment.value = true
}

const toggleActive = async () => {
  try {
    toggleLoading.value = true
    
    const response = await api.patch(`/equipment/${equipmentId.value}`, {
      is_active: !equipment.value.is_active
    })
    
    equipment.value = { ...equipment.value, is_active: response.is_active }
    
    showNotification(
      `Equipment ${response.is_active ? 'activated' : 'deactivated'} successfully`, 
      'success'
    )
    
  } catch (err) {
    console.error('Error toggling equipment status:', err)
    showNotification('Failed to update equipment status', 'error')
  } finally {
    toggleLoading.value = false
  }
}

const duplicateEquipment = async () => {
  try {
    const duplicateData = {
      manufacturer: equipment.value.manufacturer,
      model_name: `${equipment.value.model_name} (Copy)`,
      category_name: equipment.value.category_name,
      specifications: equipment.value.specifications,
      settings: equipment.value.settings,
      notes: equipment.value.notes,
      image_url: equipment.value.image_url,
      is_active: false // Start as inactive
    }
    
    const response = await api.post('/equipment', duplicateData)
    
    showNotification('Equipment duplicated successfully', 'success')
    
    // Navigate to the new equipment
    router.push(`/equipment/${response.id}`)
    
  } catch (err) {
    console.error('Error duplicating equipment:', err)
    showNotification('Failed to duplicate equipment', 'error')
  }
}

const exportEquipment = () => {
  const exportData = {
    manufacturer: equipment.value.manufacturer,
    model: equipment.value.model_name,
    category: equipment.value.category_name,
    specifications: equipment.value.specifications,
    settings: equipment.value.settings,
    notes: equipment.value.notes,
    status: equipment.value.is_active ? 'Active' : 'Inactive',
    created: equipment.value.created_at
  }
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
    type: 'application/json' 
  })
  
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `equipment-${equipment.value.id}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Handle journal statistics updates
const handleJournalStatistics = (stats) => {
  journalStatistics.value = stats
  console.log('Equipment journal statistics updated:', stats)
}

// Handle equipment update from form
const handleEquipmentUpdated = async (updatedEquipment) => {
  try {
    // Refresh equipment details to show updated data
    await loadEquipmentDetails()
    
    // Close the modal
    editingEquipment.value = false
    
    // Show success notification
    showNotification(
      `${updatedEquipment.manufacturer_name} ${updatedEquipment.model_name} updated successfully`, 
      'success'
    )
  } catch (error) {
    console.error('Error handling equipment update:', error)
    showNotification('Failed to refresh equipment details', 'error')
  }
}

// Helper functions
const getCategoryIcon = (category) => {
  const icons = {
    'Sight': { 
      iconClass: 'fas fa-crosshairs text-blue-600 dark:text-blue-400', 
      bgClass: 'bg-blue-100 dark:bg-blue-900/30' 
    },
    'Stabilizer': { 
      iconClass: 'fas fa-balance-scale text-green-600 dark:text-green-400', 
      bgClass: 'bg-green-100 dark:bg-green-900/30' 
    },
    'Arrow Rest': { 
      iconClass: 'fas fa-hand-paper text-purple-600 dark:text-purple-400', 
      bgClass: 'bg-purple-100 dark:bg-purple-900/30' 
    },
    'String': { 
      iconClass: 'fas fa-link text-red-600 dark:text-red-400', 
      bgClass: 'bg-red-100 dark:bg-red-900/30' 
    },
    'Weight': { 
      iconClass: 'fas fa-weight-hanging text-gray-600 dark:text-gray-400', 
      bgClass: 'bg-gray-100 dark:bg-gray-900/30' 
    },
    'Scope': { 
      iconClass: 'fas fa-search text-indigo-600 dark:text-indigo-400', 
      bgClass: 'bg-indigo-100 dark:bg-indigo-900/30' 
    }
  }
  return icons[category] || { 
    iconClass: 'fas fa-cog text-gray-600 dark:text-gray-400', 
    bgClass: 'bg-gray-100 dark:bg-gray-900/30' 
  }
}

const formatFieldName = (fieldName) => {
  if (!fieldName) return ''
  return fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return dateString
  }
}

// Notification methods
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  }
  
  setTimeout(() => {
    hideNotification()
  }, 5000)
}

const hideNotification = () => {
  notification.value.show = false
}

const getNotificationClasses = (type) => {
  const baseClasses = 'p-4 rounded-lg shadow-lg max-w-sm'
  switch (type) {
    case 'success':
      return `${baseClasses} bg-green-600 text-white`
    case 'error':
      return `${baseClasses} bg-red-600 text-white`
    case 'warning':
      return `${baseClasses} bg-yellow-600 text-white`
    case 'info':
      return `${baseClasses} bg-blue-600 text-white`
    default:
      return `${baseClasses} bg-gray-600 text-white`
  }
}

const getNotificationIcon = (type) => {
  switch (type) {
    case 'success':
      return 'fas fa-check-circle'
    case 'error':
      return 'fas fa-exclamation-circle'
    case 'warning':
      return 'fas fa-exclamation-triangle'
    case 'info':
      return 'fas fa-info-circle'
    default:
      return 'fas fa-bell'
  }
}

// Specification formatting functions
const formatSpecificationKey = (key) => {
  // Convert snake_case to Title Case
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const formatSpecificationValue = (value) => {
  if (value === null || value === undefined) {
    return 'N/A'
  }
  
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return 'None'
    }
    return value.join(', ')
  }
  
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }
  
  if (typeof value === 'string') {
    // Convert snake_case values to Title Case
    return value
      .split(/[-_]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }
  
  return String(value)
}

// Watch for route changes
watch(() => equipmentId.value, (newId) => {
  if (newId) {
    loadEquipmentDetails()
  }
})

// Lifecycle
onMounted(() => {
  if (equipmentId.value) {
    loadEquipmentDetails()
  }
})

// Set dynamic page title
watchEffect(() => {
  if (equipment.value) {
    useHead({
      title: `${equipment.value.manufacturer} ${equipment.value.model_name} - Equipment Details`,
      meta: [
        { 
          name: 'description', 
          content: `Detailed information and journal entries for ${equipment.value.manufacturer} ${equipment.value.model_name} ${equipment.value.category_name}.` 
        }
      ]
    })
  } else {
    useHead({
      title: 'Equipment Details',
      meta: [
        { name: 'description', content: 'Detailed equipment specifications and tracking information' }
      ]
    })
  }
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.dark .card {
  background: #1f2937;
  border-color: #374151;
}

/* Material Design chip styling */
md-chip-set {
  margin-bottom: 1.5rem;
}

.fa-icon {
  width: 16px;
  height: 16px;
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .card {
    padding: 1rem;
  }
  
  .text-2xl {
    font-size: 1.5rem;
  }
  
  .grid-cols-1.md\:grid-cols-2.lg\:grid-cols-3 {
    grid-template-columns: 1fr;
  }
}
</style>