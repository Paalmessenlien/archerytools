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
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ manufacturers.length }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Manufacturers</div>
      </div>
      <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
        <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ totalArrows }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Arrows</div>
      </div>
      <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
        <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ totalEquipment }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Equipment</div>
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
              Product Count
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Equipment Categories
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Status
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr 
            v-for="manufacturer in manufacturers" 
            :key="manufacturer.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <i class="fas fa-industry text-gray-400 mr-3"></i>
                <div>
                  <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {{ manufacturer.name }}
                  </div>
                  <div v-if="manufacturer.country" class="text-xs text-gray-500 dark:text-gray-400">
                    {{ manufacturer.country }}
                  </div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="space-y-1">
                <span v-if="manufacturer.arrow_count > 0" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  {{ manufacturer.arrow_count }} arrows
                </span>
                <span v-if="manufacturer.equipment_count > 0" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">
                  {{ manufacturer.equipment_count }} equipment
                </span>
                <span v-if="manufacturer.arrow_count === 0 && manufacturer.equipment_count === 0" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300">
                  No products
                </span>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="category in getSupportedCategories(manufacturer)"
                  :key="category.name"
                  class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                  :class="getCategoryBadgeClass(category.name)"
                >
                  <i :class="getCategoryIcon(category.name)" class="mr-1"></i>
                  {{ getCategoryDisplayName(category.name) }}
                </span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span 
                class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                :class="manufacturer.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'"
              >
                <i :class="manufacturer.is_active ? 'fas fa-check' : 'fas fa-times'" class="mr-1"></i>
                {{ manufacturer.is_active ? 'Active' : 'Inactive' }}
              </span>
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
                @click="openCategoriesModal(manufacturer)"
                variant="outlined"
                size="small"
                class="text-purple-600 border-purple-600 hover:bg-purple-50 dark:text-purple-400 dark:border-purple-400"
              >
                <i class="fas fa-cogs mr-1"></i>
                Categories
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
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-8 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {{ isEditing ? 'Edit Manufacturer' : 'Add New Manufacturer' }}
        </h3>
        
        <form @submit.prevent="saveManufacturer" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="manufacturerName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Manufacturer Name *
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
            
            <div>
              <label for="country" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Country
              </label>
              <input 
                type="text" 
                id="country" 
                v-model="formData.country" 
                class="form-input w-full" 
                placeholder="e.g., United States, Germany"
              />
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="website" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Website URL
              </label>
              <input 
                type="url" 
                id="website" 
                v-model="formData.website_url" 
                class="form-input w-full" 
                placeholder="https://example.com"
              />
            </div>
            
            <div>
              <label for="establishedYear" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Established Year
              </label>
              <input 
                type="number" 
                id="establishedYear" 
                v-model="formData.established_year" 
                class="form-input w-full" 
                placeholder="e.g., 1980"
                min="1800"
                max="2030"
              />
            </div>
          </div>
          
          <div>
            <label for="logoUrl" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Logo URL
            </label>
            <input 
              type="url" 
              id="logoUrl" 
              v-model="formData.logo_url" 
              class="form-input w-full" 
              placeholder="https://example.com/logo.png"
            />
          </div>
          
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea 
              id="description" 
              v-model="formData.description" 
              class="form-input w-full" 
              rows="3"
              placeholder="Brief description of the manufacturer..."
            ></textarea>
          </div>
          
          <div class="flex items-center">
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                v-model="formData.is_active"
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              <span class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">Active Manufacturer</span>
            </label>
          </div>
          
          <div v-if="isEditing" class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div class="flex items-start">
              <i class="fas fa-info-circle text-blue-500 mt-0.5 mr-2"></i>
              <div class="text-sm text-blue-700 dark:text-blue-300">
                <p class="font-medium">Updating manufacturer:</p>
                <p>{{ selectedManufacturer?.arrow_count || 0 }} arrows and {{ selectedManufacturer?.equipment_count || 0 }} equipment items</p>
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
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-8 overflow-y-auto">
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
                  <li><strong>{{ manufacturerToDelete?.arrow_count || 0 }} arrows</strong></li>
                  <li><strong>{{ manufacturerToDelete?.equipment_count || 0 }} equipment items</strong></li>
                  <li>All associated spine specifications</li>
                  <li>All equipment category mappings</li>
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

    <!-- Equipment Categories Modal -->
    <div v-if="showCategoriesModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-8 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl shadow-lg max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-cogs mr-2 text-purple-600"></i>
          Equipment Categories - {{ selectedManufacturer?.name }}
        </h3>
        
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
          Configure which categories this manufacturer supports. This includes equipment categories (arrows, strings, sights, etc.) and bow categories (compound bows, recurve components, traditional bows, etc.).
        </p>
        
        <div v-if="loadingCategories" class="text-center py-8">
          <i class="fas fa-spinner fa-spin text-2xl text-purple-600 mb-2"></i>
          <p class="text-gray-600 dark:text-gray-400">Loading categories...</p>
        </div>
        
        <div v-else class="space-y-4">
          <div 
            v-for="category in availableCategories" 
            :key="category.name"
            class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg"
          >
            <div class="flex items-center space-x-3">
              <i :class="category.icon || getCategoryIcon(category.name)" class="text-lg text-gray-600 dark:text-gray-400"></i>
              <div>
                <div class="font-medium text-gray-900 dark:text-gray-100">
                  {{ category.display_name || getCategoryDisplayName(category.name) }}
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  {{ category.description || `${getCategoryDisplayName(category.name)} manufacturing and support` }}
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <label class="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  :checked="isCategorySupported(category.name)"
                  @change="toggleCategorySupport(category.name, $event.target.checked)"
                  class="sr-only peer"
                >
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
              </label>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <CustomButton
            @click="closeCategoriesModal"
            variant="outlined"
            class="text-gray-700 dark:text-gray-200"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="saveCategoryChanges"
            variant="filled"
            :disabled="isSavingCategories"
            class="bg-purple-600 text-white hover:bg-purple-700"
          >
            <span v-if="isSavingCategories">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              Saving...
            </span>
            <span v-else>
              <i class="fas fa-save mr-2"></i>
              Save Changes
            </span>
          </CustomButton>
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
const showCategoriesModal = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const isSavingCategories = ref(false)
const loadingCategories = ref(false)
const isEditing = ref(false)
const selectedManufacturer = ref(null)
const manufacturerToDelete = ref(null)
const availableCategories = ref([])
const categorySettings = ref({})

// Form data
const formData = ref({
  name: '',
  website_url: '',
  logo_url: '',
  description: '',
  country: '',
  established_year: null,
  is_active: true
})

// Computed properties
const totalArrows = computed(() => {
  return manufacturers.value.reduce((total, mfg) => total + (mfg.arrow_count || 0), 0)
})

const totalEquipment = computed(() => {
  return manufacturers.value.reduce((total, mfg) => total + (mfg.equipment_count || 0), 0)
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
  formData.value = {
    name: manufacturer.name,
    website_url: manufacturer.website_url || '',
    logo_url: manufacturer.logo_url || '',
    description: manufacturer.description || '',
    country: manufacturer.country || '',
    established_year: manufacturer.established_year || null,
    is_active: manufacturer.is_active
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  isEditing.value = false
  selectedManufacturer.value = null
  formData.value = {
    name: '',
    website_url: '',
    logo_url: '',
    description: '',
    country: '',
    established_year: null,
    is_active: true
  }
}

const saveManufacturer = async () => {
  try {
    isSaving.value = true
    
    if (isEditing.value) {
      // Update manufacturer using ID
      await api.put(`/admin/manufacturers/${selectedManufacturer.value.id}`, formData.value)
      emit('show-notification', 'Manufacturer updated successfully', 'success')
    } else {
      // Create manufacturer
      await api.post('/admin/manufacturers', formData.value)
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
    await api.delete(`/admin/manufacturers/${manufacturerToDelete.value.id}`)
    emit('show-notification', 'Manufacturer and all associated data deleted successfully', 'success')
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

// Equipment category management methods
const openCategoriesModal = async (manufacturer) => {
  selectedManufacturer.value = manufacturer
  showCategoriesModal.value = true
  loadingCategories.value = true
  
  try {
    // Load available categories including bow and equipment categories
    const [categoriesResponse, manufacturerCategoriesResponse, bowEquipmentResponse] = await Promise.all([
      api.get('/admin/equipment-categories'),
      api.get(`/admin/manufacturers/${manufacturer.id}/equipment-categories`),
      api.get('/bow-equipment/manufacturers')
    ])
    
    // Combine equipment categories with bow/equipment categories
    const equipmentCategories = categoriesResponse.categories || []
    const bowEquipmentCategories = [
      { name: 'compound_bows', display_name: 'Compound Bows', description: 'Compound bow manufacturing', icon: 'fas fa-bow-arrow' },
      { name: 'recurve_risers', display_name: 'Recurve Risers', description: 'Recurve bow riser manufacturing', icon: 'fas fa-mountain' },
      { name: 'recurve_limbs', display_name: 'Recurve Limbs', description: 'Recurve bow limb manufacturing', icon: 'fas fa-bezier-curve' },
      { name: 'traditional_risers', display_name: 'Traditional Risers', description: 'Traditional bow riser manufacturing', icon: 'fas fa-tree' },
      { name: 'traditional_limbs', display_name: 'Traditional Limbs', description: 'Traditional bow limb manufacturing', icon: 'fas fa-leaf' },
      { name: 'longbows', display_name: 'Longbows', description: 'Longbow manufacturing', icon: 'fas fa-archway' },
      { name: 'strings', display_name: 'Strings', description: 'Bowstring manufacturing', icon: 'fas fa-grip-lines' },
      { name: 'sights', display_name: 'Sights', description: 'Bow sight manufacturing', icon: 'fas fa-bullseye' },
      { name: 'stabilizers', display_name: 'Stabilizers', description: 'Stabilizer manufacturing', icon: 'fas fa-balance-scale' },
      { name: 'arrow_rests', display_name: 'Arrow Rests', description: 'Arrow rest manufacturing', icon: 'fas fa-hand-paper' },
      { name: 'weights', display_name: 'Weights', description: 'Weight system manufacturing', icon: 'fas fa-weight-hanging' }
    ]
    
    availableCategories.value = [...equipmentCategories, ...bowEquipmentCategories]
    
    // Set up category settings based on manufacturer's current settings
    categorySettings.value = {}
    const manufacturerCategories = manufacturerCategoriesResponse.equipment_categories || []
    
    for (const category of manufacturerCategories) {
      categorySettings.value[category.category_name] = category.is_supported
    }
    
    // Check if manufacturer is in bow equipment categories
    const bowEquipmentData = bowEquipmentResponse.categories || {}
    for (const [categoryName, manufacturers] of Object.entries(bowEquipmentData)) {
      if (manufacturers.includes(manufacturer.name)) {
        categorySettings.value[categoryName] = true
      }
    }
    
    // Set defaults for any missing categories
    for (const category of availableCategories.value) {
      if (!(category.name in categorySettings.value)) {
        categorySettings.value[category.name] = false
      }
    }
    
  } catch (error) {
    console.error('Error loading categories:', error)
    emit('show-notification', 'Failed to load equipment categories', 'error')
  } finally {
    loadingCategories.value = false
  }
}

const closeCategoriesModal = () => {
  showCategoriesModal.value = false
  selectedManufacturer.value = null
  availableCategories.value = []
  categorySettings.value = {}
}

const isCategorySupported = (categoryName) => {
  return categorySettings.value[categoryName] || false
}

const toggleCategorySupport = (categoryName, isSupported) => {
  categorySettings.value[categoryName] = isSupported
}

const saveCategoryChanges = async () => {
  try {
    isSavingCategories.value = true
    
    const categories = Object.keys(categorySettings.value).map(categoryName => ({
      category_name: categoryName,
      is_supported: categorySettings.value[categoryName],
      notes: categorySettings.value[categoryName] ? 'Manually configured' : ''
    }))
    
    await api.put(`/admin/manufacturers/${selectedManufacturer.value.id}/equipment-categories`, {
      categories
    })
    
    emit('show-notification', 'Equipment categories updated successfully', 'success')
    closeCategoriesModal()
    await loadManufacturers()
  } catch (error) {
    console.error('Error saving categories:', error)
    emit('show-notification', error.message || 'Failed to save categories', 'error')
  } finally {
    isSavingCategories.value = false
  }
}

// Utility methods for displaying categories
const getSupportedCategories = (manufacturer) => {
  if (!manufacturer.equipment_categories) return []
  return manufacturer.equipment_categories.filter(cat => cat.is_supported)
}

const getCategoryDisplayName = (categoryName) => {
  const displayNames = {
    'arrows': 'Arrows',
    'strings': 'Strings',
    'sights': 'Sights',
    'stabilizers': 'Stabilizers',
    'arrow_rests': 'Arrow Rests',
    'weights': 'Weights',
    'compound_bows': 'Compound Bows',
    'recurve_risers': 'Recurve Risers',
    'recurve_limbs': 'Recurve Limbs',
    'traditional_risers': 'Traditional Risers',
    'traditional_limbs': 'Traditional Limbs',
    'longbows': 'Longbows'
  }
  return displayNames[categoryName] || categoryName
}

const getCategoryIcon = (categoryName) => {
  const icons = {
    'arrows': 'fas fa-crosshairs',
    'strings': 'fas fa-grip-lines',
    'sights': 'fas fa-bullseye',
    'stabilizers': 'fas fa-balance-scale',
    'arrow_rests': 'fas fa-hand-paper',
    'weights': 'fas fa-weight-hanging',
    'compound_bows': 'fas fa-bow-arrow',
    'recurve_risers': 'fas fa-mountain',
    'recurve_limbs': 'fas fa-bezier-curve',
    'traditional_risers': 'fas fa-tree',
    'traditional_limbs': 'fas fa-leaf',
    'longbows': 'fas fa-archway'
  }
  return icons[categoryName] || 'fas fa-cog'
}

const getCategoryBadgeClass = (categoryName) => {
  const classes = {
    'arrows': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'strings': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'sights': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'stabilizers': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'arrow_rests': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    'weights': 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300',
    'compound_bows': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
    'recurve_risers': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300',
    'recurve_limbs': 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300',
    'traditional_risers': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    'traditional_limbs': 'bg-lime-100 text-lime-800 dark:bg-lime-900/30 dark:text-lime-300',
    'longbows': 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300'
  }
  return classes[categoryName] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
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