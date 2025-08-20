<template>
  <div class="bow-equipment-manager">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
        <i class="fas fa-cogs mr-2 text-green-600 dark:text-green-400"></i>
        Equipment
      </h2>
      <CustomButton
        @click="openEquipmentSelector"
        variant="filled"
        class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-600 dark:hover:bg-green-700 w-full sm:w-auto"
      >
        <i class="fas fa-plus mr-2"></i>
        Add Equipment
      </CustomButton>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 dark:border-green-400 mx-auto mb-3"></div>
      <p class="text-gray-600 dark:text-gray-400">Loading equipment...</p>
    </div>

    <!-- Equipment List -->
    <div v-else-if="equipment.length > 0" class="space-y-4">
      <div
        v-for="item in groupedEquipment"
        :key="item.category"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
      >
        <!-- Category Header -->
        <div class="px-4 py-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <i :class="getCategoryIcon(item.category)" class="mr-3 text-lg text-gray-600 dark:text-gray-400"></i>
              <h3 class="font-medium text-gray-900 dark:text-gray-100">{{ getCategoryDisplayName(item.category) }}</h3>
              <span class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full">
                {{ item.items.length }}
              </span>
            </div>
            <button
              @click="toggleCategory(item.category)"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <i :class="collapsedCategories[item.category] ? 'fas fa-chevron-down' : 'fas fa-chevron-up'"></i>
            </button>
          </div>
        </div>

        <!-- Equipment Items -->
        <div v-if="!collapsedCategories[item.category]" class="divide-y divide-gray-200 dark:divide-gray-600">
          <div
            v-for="equipmentItem in item.items"
            :key="equipmentItem.id"
            class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="flex items-start justify-between">
              <!-- Equipment Info -->
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <!-- Equipment Image/Icon -->
                  <div class="w-12 h-12 bg-gray-100 dark:bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <img
                      v-if="equipmentItem.image_url"
                      :src="equipmentItem.image_url"
                      :alt="equipmentItem.model_name"
                      class="w-full h-full object-cover rounded-lg"
                    />
                    <i v-else :class="getCategoryIcon(equipmentItem.category_name)" class="text-xl text-gray-400"></i>
                  </div>

                  <!-- Equipment Details -->
                  <div class="flex-1 min-w-0">
                    <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 truncate">
                      {{ equipmentItem.manufacturer_name || equipmentItem.manufacturer }} {{ equipmentItem.model_name }}
                    </h4>
                    <p v-if="equipmentItem.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                      {{ equipmentItem.description }}
                    </p>
                    
                    <!-- Key Specifications -->
                    <div v-if="equipmentItem.specifications" class="mt-2 flex flex-wrap gap-2">
                      <span
                        v-for="(value, key) in getKeySpecs(equipmentItem.specifications, equipmentItem.category_name)"
                        :key="key"
                        class="inline-flex items-center px-2 py-1 text-xs bg-gray-100 text-gray-700 dark:bg-gray-600 dark:text-gray-300 rounded-full"
                      >
                        {{ formatSpecKey(key) }}: {{ formatSpecValue(value) }}
                      </span>
                    </div>

                    <!-- Installation Info -->
                    <div v-if="equipmentItem.installation_date" class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      Added {{ formatDate(equipmentItem.installation_date) }}
                      <span v-if="equipmentItem.installation_notes" class="ml-2">
                        - {{ equipmentItem.installation_notes }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center space-x-2 ml-4">
                <CustomButton
                  @click="editEquipment(equipmentItem)"
                  variant="text"
                  size="small"
                  class="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  <i class="fas fa-edit"></i>
                </CustomButton>
                <CustomButton
                  @click="removeEquipment(equipmentItem)"
                  variant="text"
                  size="small"
                  class="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                >
                  <i class="fas fa-trash"></i>
                </CustomButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Mobile-Optimized Empty State -->
    <div v-else class="empty-state-container bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 sm:p-12">
      <!-- Mobile-first layout with enhanced visual hierarchy -->
      <div class="text-center max-w-sm mx-auto">
        <!-- Enhanced Icon Design -->
        <div class="mb-6 sm:mb-8">
          <div class="w-20 h-20 sm:w-24 sm:h-24 mx-auto mb-4 bg-gradient-to-br from-green-100 to-green-200 dark:from-green-900/30 dark:to-green-800/30 rounded-full flex items-center justify-center">
            <i class="fas fa-cogs text-3xl sm:text-4xl text-green-600 dark:text-green-400"></i>
          </div>
          
          <!-- Contextual Equipment Icons -->
          <div class="flex justify-center space-x-3 opacity-50">
            <div class="w-8 h-8 sm:w-10 sm:h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <i class="fas fa-bullseye text-blue-500 text-sm"></i>
            </div>
            <div class="w-8 h-8 sm:w-10 sm:h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <i class="fas fa-balance-scale text-purple-500 text-sm"></i>
            </div>
            <div class="w-8 h-8 sm:w-10 sm:h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <i class="fas fa-arrow-up text-orange-500 text-sm"></i>
            </div>
          </div>
        </div>
        
        <!-- Enhanced Content with Mobile-first Typography -->
        <h3 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100 mb-3 sm:mb-4">Ready to Track Your Equipment?</h3>
        <p class="text-base sm:text-lg text-gray-600 dark:text-gray-400 mb-6 sm:mb-8 leading-relaxed">
          Add your bow accessories like sights, stabilizers, and rests to get the complete picture of your setup.
        </p>
        
        <!-- Enhanced Mobile-First CTA Section -->
        <div class="space-y-3 sm:space-y-4">
          <!-- Primary CTA - Enhanced Touch Target -->
          <button
            @click="openEquipmentSelector"
            class="primary-cta-button w-full flex items-center justify-center p-4 sm:p-5 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] bg-green-600 border-green-600 text-white hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:bg-green-600 dark:hover:bg-green-700"
          >
            <div class="flex items-center">
              <div class="w-6 h-6 sm:w-7 sm:h-7 mr-3 flex items-center justify-center rounded-full bg-green-500 flex-shrink-0">
                <i class="fas fa-plus text-white text-sm"></i>
              </div>
              <span class="font-semibold text-lg">Add Your First Equipment</span>
            </div>
          </button>
          
          <!-- Secondary Information - Mobile Optimized -->
          <div class="text-center pt-2">
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
              Popular equipment to track:
            </p>
            <div class="flex flex-wrap justify-center gap-2 text-xs">
              <span class="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full">
                <i class="fas fa-bullseye mr-1.5 text-blue-500"></i>Sight
              </span>
              <span class="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full">
                <i class="fas fa-balance-scale mr-1.5 text-purple-500"></i>Stabilizer
              </span>
              <span class="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full">
                <i class="fas fa-arrow-up mr-1.5 text-orange-500"></i>Rest
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>


    <!-- Equipment Form Modal (Add/Edit) -->
    <div v-if="showEquipmentSelector || editingEquipment" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
              <i :class="editingEquipment ? 'fas fa-edit text-blue-600' : 'fas fa-cogs text-green-600'" class="mr-2"></i>
              {{ editingEquipment ? 'Edit Equipment' : 'Add Equipment to' }} 
              {{ editingEquipment ? '' : bowSetup.name }}
              <span v-if="editingEquipment" class="text-base font-normal text-gray-600 dark:text-gray-400">
                - {{ editingEquipment.manufacturer_name || editingEquipment.manufacturer }} {{ editingEquipment.model_name }}
              </span>
            </h3>
            <CustomButton @click="closeEquipmentModal" variant="text" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times text-xl"></i>
            </CustomButton>
          </div>
        </div>

        <!-- Content -->
        <div class="p-6">
          <CustomEquipmentForm
            :bow-setup="bowSetup"
            :initial-equipment="editingEquipment"
            :is-editing="!!editingEquipment"
            @equipment-added="handleEquipmentAdded"
            @equipment-updated="handleEquipmentUpdated"
            @cancel="closeEquipmentModal"
          />
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmDeleteModal
      v-if="equipmentToDelete"
      :title="`Remove Equipment`"
      :message="`Are you sure you want to remove this equipment from your bow setup?`"
      :item-name="`${equipmentToDelete.manufacturer_name || equipmentToDelete.manufacturer} ${equipmentToDelete.model_name}`"
      :confirm-text="`Remove`"
      :loading="deletingEquipment"
      :error="deleteError"
      @confirm="confirmRemoveEquipment"
      @cancel="cancelRemoveEquipment"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['equipment-updated', 'show-notification'])

// Composables
const api = useApi()

// State
const equipment = ref([])
const loading = ref(false)
const showEquipmentSelector = ref(false)
const editingEquipment = ref(null)
const collapsedCategories = ref({})
const equipmentToDelete = ref(null)
const deletingEquipment = ref(false)
const deleteError = ref('')

// Computed
const groupedEquipment = computed(() => {
  const groups = {}
  equipment.value.forEach(item => {
    const category = item.category_name || 'Other'
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(item)
  })
  
  return Object.keys(groups).map(category => ({
    category,
    items: groups[category]
  })).sort((a, b) => a.category.localeCompare(b.category))
})

const excludedEquipmentIds = computed(() => {
  return equipment.value.map(item => item.equipment_id)
})

// Methods
const loadEquipment = async () => {
  if (!props.bowSetup?.id) return
  
  try {
    loading.value = true
    const response = await api.get(`/bow-setups/${props.bowSetup.id}/equipment`)
    equipment.value = response.equipment || []
  } catch (error) {
    console.error('Error loading equipment:', error)
    emit('show-notification', 'Failed to load equipment', 'error')
  } finally {
    loading.value = false
  }
}

const openEquipmentSelector = () => {
  showEquipmentSelector.value = true
}

const closeEquipmentModal = () => {
  showEquipmentSelector.value = false
  editingEquipment.value = null
}

const handleEquipmentAdded = async (addedEquipment) => {
  try {
    await loadEquipment()
    emit('show-notification', `${addedEquipment.manufacturer_name} ${addedEquipment.model_name} added successfully`, 'success')
    emit('equipment-updated')
    closeEquipmentModal()
  } catch (error) {
    console.error('Error handling equipment added:', error)
    emit('show-notification', 'Failed to refresh equipment list', 'error')
  }
}

const editEquipment = (equipmentItem) => {
  editingEquipment.value = equipmentItem
}

const handleEquipmentUpdated = async (updatedEquipment) => {
  try {
    // The CustomEquipmentForm handles the API call, so we just need to refresh and close
    await loadEquipment()
    emit('show-notification', `${updatedEquipment.manufacturer_name} ${updatedEquipment.model_name} updated successfully`, 'success')
    emit('equipment-updated')
    closeEquipmentModal()
  } catch (error) {
    console.error('Error handling equipment update:', error)
    emit('show-notification', 'Failed to refresh equipment list', 'error')
  }
}

const removeEquipment = (equipmentItem) => {
  equipmentToDelete.value = equipmentItem
  deleteError.value = ''
}

const confirmRemoveEquipment = async () => {
  if (!equipmentToDelete.value) return
  
  try {
    deletingEquipment.value = true
    deleteError.value = ''
    
    await api.delete(`/bow-setups/${props.bowSetup.id}/equipment/${equipmentToDelete.value.id}`)
    await loadEquipment()
    
    emit('show-notification', 'Equipment removed successfully', 'success')
    emit('equipment-updated')
    equipmentToDelete.value = null
  } catch (error) {
    console.error('Error removing equipment:', error)
    deleteError.value = error.message || 'Failed to remove equipment'
  } finally {
    deletingEquipment.value = false
  }
}

const cancelRemoveEquipment = () => {
  equipmentToDelete.value = null
  deleteError.value = ''
}

const toggleCategory = (category) => {
  collapsedCategories.value[category] = !collapsedCategories.value[category]
}

const getCategoryIcon = (categoryName) => {
  const iconMap = {
    'String': 'fas fa-link',
    'Sight': 'fas fa-crosshairs',
    'Scope': 'fas fa-search',
    'Stabilizer': 'fas fa-balance-scale',
    'Arrow Rest': 'fas fa-hand-paper',
    'Plunger': 'fas fa-bullseye',
    'Weight': 'fas fa-weight-hanging',
    'Peep Sight': 'fas fa-circle-notch',
    'Other': 'fas fa-cog'
  }
  return iconMap[categoryName] || 'fas fa-cog'
}

const getCategoryDisplayName = (categoryName) => {
  const displayNames = {
    'String': 'Strings & Cables',
    'Sight': 'Sights',
    'Scope': 'Scopes',
    'Stabilizer': 'Stabilizers',
    'Arrow Rest': 'Arrow Rests',
    'Plunger': 'Plungers',
    'Weight': 'Weights',
    'Peep Sight': 'Peep Sights',
    'Other': 'Other Equipment'
  }
  return displayNames[categoryName] || categoryName
}

const getKeySpecs = (specs, category) => {
  if (!specs || typeof specs === 'string') {
    try {
      specs = JSON.parse(specs || '{}')
    } catch {
      return {}
    }
  }
  
  const keySpecsMap = {
    'String': ['material', 'strand_count', 'length_inches'],
    'Sight': ['sight_type', 'pin_count', 'adjustment_type'],
    'Stabilizer': ['length_inches', 'weight_ounces', 'material'],
    'Arrow Rest': ['rest_type', 'activation_type'],
    'Weight': ['weight_ounces', 'weight_type'],
    'Peep Sight': ['aperture_diameter', 'mounting_style', 'material']
  }
  
  const keySpecs = keySpecsMap[category] || Object.keys(specs).slice(0, 3)
  const result = {}
  
  keySpecs.forEach(key => {
    if (specs[key] !== undefined && specs[key] !== null && specs[key] !== '') {
      result[key] = specs[key]
    }
  })
  
  return result
}

const formatSpecKey = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatSpecValue = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  if (typeof value === 'number') {
    return value.toString()
  }
  return String(value)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}

// Watchers
watch(() => props.bowSetup?.id, () => {
  if (props.bowSetup?.id) {
    loadEquipment()
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  if (props.bowSetup?.id) {
    loadEquipment()
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>