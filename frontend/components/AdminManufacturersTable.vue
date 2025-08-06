<template>
  <div class="manufacturer-table-container">
    <!-- Header with Create Button -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
        <i class="fas fa-industry mr-2 text-indigo-600"></i>
        Manufacturer Management
      </h2>
      <CustomButton
        @click="openCreateModal"
        variant="filled"
        class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800"
      >
        <i class="fas fa-plus mr-2"></i>
        Add Manufacturer
      </CustomButton>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ manufacturers.length }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Manufacturers</div>
      </div>
      <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
        <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ totalArrows }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Arrows</div>
      </div>
      <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
        <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ averageArrowsPerManufacturer }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Avg Arrows/Manufacturer</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-2xl text-indigo-600 mb-2"></i>
      <p class="text-gray-600 dark:text-gray-400">Loading manufacturers...</p>
    </div>

    <!-- Manufacturers Table -->
    <div v-else-if="manufacturers.length > 0" class="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg shadow">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-900">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Manufacturer
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Arrow Count
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              First Added
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Last Updated
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr 
            v-for="manufacturer in manufacturers" 
            :key="manufacturer.name"
            class="hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <i class="fas fa-industry text-gray-400 mr-3"></i>
                <div>
                  <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {{ manufacturer.name }}
                  </div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                {{ manufacturer.arrow_count }} arrows
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
              {{ formatDate(manufacturer.first_added) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
              {{ formatDate(manufacturer.last_added) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
              <CustomButton
                @click="openEditModal(manufacturer)"
                variant="outlined"
                size="small"
                class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400"
              >
                <i class="fas fa-edit mr-1"></i>
                Edit
              </CustomButton>
              <CustomButton
                @click="confirmDelete(manufacturer)"
                variant="outlined"
                size="small"
                class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400"
              >
                <i class="fas fa-trash mr-1"></i>
                Delete
              </CustomButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
      <i class="fas fa-industry text-4xl text-gray-400 mb-4"></i>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Manufacturers Found</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-4">Start by adding your first manufacturer.</p>
      <CustomButton
        @click="openCreateModal"
        variant="filled"
        class="bg-green-600 text-white hover:bg-green-700"
      >
        <i class="fas fa-plus mr-2"></i>
        Add First Manufacturer
      </CustomButton>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {{ isEditing ? 'Edit Manufacturer' : 'Add New Manufacturer' }}
        </h3>
        
        <form @submit.prevent="saveManufacturer">
          <div class="mb-4">
            <label for="manufacturerName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Manufacturer Name
            </label>
            <input 
              type="text" 
              id="manufacturerName" 
              v-model="formData.name" 
              class="form-input w-full" 
              required 
              :placeholder="isEditing ? 'Enter new manufacturer name' : 'Enter manufacturer name'"
            />
          </div>
          
          <div v-if="isEditing" class="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <div class="flex items-start">
              <i class="fas fa-exclamation-triangle text-yellow-500 mt-0.5 mr-2"></i>
              <div class="text-sm text-yellow-700 dark:text-yellow-300">
                <p class="font-medium">Important:</p>
                <p>This will update the manufacturer name for <strong>{{ selectedManufacturer?.arrow_count }} arrows</strong>.</p>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3">
            <CustomButton
              type="button"
              @click="closeModal"
              variant="outlined"
              class="text-gray-700 dark:text-gray-200"
            >
              Cancel
            </CustomButton>
            <CustomButton
              type="submit"
              variant="filled"
              :disabled="isSaving"
              :class="isEditing ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-green-600 text-white hover:bg-green-700'"
            >
              <span v-if="isSaving">
                <i class="fas fa-spinner fa-spin mr-2"></i>
                {{ isEditing ? 'Updating...' : 'Creating...' }}
              </span>
              <span v-else>
                <i :class="isEditing ? 'fas fa-save mr-2' : 'fas fa-plus mr-2'"></i>
                {{ isEditing ? 'Update' : 'Create' }}
              </span>
            </CustomButton>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
        <div class="text-center">
          <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Delete Manufacturer</h3>
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            Are you sure you want to delete <strong>{{ manufacturerToDelete?.name }}</strong>?
          </p>
          <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 mb-6">
            <div class="flex items-start">
              <i class="fas fa-exclamation-triangle text-red-500 mt-0.5 mr-2"></i>
              <div class="text-sm text-red-700 dark:text-red-300">
                <p class="font-medium">This action cannot be undone!</p>
                <p>This will permanently delete:</p>
                <ul class="list-disc list-inside mt-1">
                  <li><strong>{{ manufacturerToDelete?.arrow_count }} arrows</strong></li>
                  <li>All associated spine specifications</li>
                  <li>All manufacturer data</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="flex justify-center space-x-4">
            <CustomButton
              @click="showDeleteModal = false"
              variant="outlined"
              class="text-gray-700 dark:text-gray-200"
            >
              Cancel
            </CustomButton>
            <CustomButton
              @click="deleteManufacturer"
              variant="filled"
              :disabled="isDeleting"
              class="bg-red-600 text-white hover:bg-red-700"
            >
              <span v-if="isDeleting">
                <i class="fas fa-spinner fa-spin mr-2"></i>
                Deleting...
              </span>
              <span v-else>
                <i class="fas fa-trash mr-2"></i>
                Delete Permanently
              </span>
            </CustomButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Props and emits
const emit = defineEmits(['refresh-stats', 'show-notification'])

// API composable
const api = useApi()

// State
const loading = ref(false)
const manufacturers = ref([])
const showModal = ref(false)
const showDeleteModal = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const isEditing = ref(false)
const selectedManufacturer = ref(null)
const manufacturerToDelete = ref(null)

// Form data
const formData = ref({
  name: ''
})

// Computed properties
const totalArrows = computed(() => {
  return manufacturers.value.reduce((total, mfg) => total + mfg.arrow_count, 0)
})

const averageArrowsPerManufacturer = computed(() => {
  if (manufacturers.value.length === 0) return 0
  return Math.round(totalArrows.value / manufacturers.value.length)
})

// Methods
const loadManufacturers = async () => {
  try {
    loading.value = true
    const response = await api.get('/admin/manufacturers')
    manufacturers.value = response.manufacturers || []
    emit('refresh-stats')
  } catch (error) {
    console.error('Error loading manufacturers:', error)
    emit('show-notification', error.message || 'Failed to load manufacturers', 'error')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  selectedManufacturer.value = null
  formData.value = { name: '' }
  showModal.value = true
}

const openEditModal = (manufacturer) => {
  isEditing.value = true
  selectedManufacturer.value = manufacturer
  formData.value = { name: manufacturer.name }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  isEditing.value = false
  selectedManufacturer.value = null
  formData.value = { name: '' }
}

const saveManufacturer = async () => {
  try {
    isSaving.value = true
    
    if (isEditing.value) {
      // Update manufacturer
      const encodedName = encodeURIComponent(selectedManufacturer.value.name)
      await api.put(`/admin/manufacturers/${encodedName}`, {
        new_name: formData.value.name
      })
      emit('show-notification', 'Manufacturer updated successfully', 'success')
    } else {
      // Create manufacturer
      await api.post('/admin/manufacturers', {
        name: formData.value.name
      })
      emit('show-notification', 'Manufacturer created successfully', 'success')
    }
    
    closeModal()
    await loadManufacturers()
  } catch (error) {
    console.error('Error saving manufacturer:', error)
    emit('show-notification', error.message || 'Failed to save manufacturer', 'error')
  } finally {
    isSaving.value = false
  }
}

const confirmDelete = (manufacturer) => {
  manufacturerToDelete.value = manufacturer
  showDeleteModal.value = true
}

const deleteManufacturer = async () => {
  try {
    isDeleting.value = true
    const encodedName = encodeURIComponent(manufacturerToDelete.value.name)
    await api.delete(`/admin/manufacturers/${encodedName}`)
    emit('show-notification', 'Manufacturer and all associated arrows deleted successfully', 'success')
    showDeleteModal.value = false
    manufacturerToDelete.value = null
    await loadManufacturers()
  } catch (error) {
    console.error('Error deleting manufacturer:', error)
    emit('show-notification', error.message || 'Failed to delete manufacturer', 'error')
  } finally {
    isDeleting.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}

// Expose loadManufacturers method for parent component
defineExpose({
  loadManufacturers
})

// Load data on mount
onMounted(() => {
  loadManufacturers()
})
</script>

<style scoped>
.form-input {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}

.manufacturer-table-container {
  @apply space-y-6;
}
</style>