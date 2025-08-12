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
                      {{ equipmentItem.manufacturer }} {{ equipmentItem.model_name }}
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

    <!-- Empty State -->
    <div v-else class="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <i class="fas fa-cogs text-4xl text-gray-400 mb-4"></i>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Equipment Added</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-6">Add equipment to track your bow's complete setup.</p>
      <CustomButton
        @click="openEquipmentSelector"
        variant="outlined"
        class="text-green-600 border-green-600 hover:bg-green-50 dark:text-green-400 dark:border-green-400"
      >
        <i class="fas fa-plus mr-2"></i>
        Add Your First Equipment
      </CustomButton>
    </div>

    <!-- Equipment Selector Modal -->
    <EquipmentSelectorModal
      v-if="showEquipmentSelector"
      :bow-setup="bowSetup"
      :excluded-equipment="excludedEquipmentIds"
      @select="handleEquipmentSelected"
      @close="showEquipmentSelector = false"
    />

    <!-- Equipment Edit Modal -->
    <EquipmentEditModal
      v-if="editingEquipment"
      :equipment="editingEquipment"
      :bow-setup="bowSetup"
      @save="handleEquipmentUpdated"
      @close="editingEquipment = null"
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

const handleEquipmentSelected = async (selectedEquipment) => {
  try {
    const response = await api.post(`/bow-setups/${props.bowSetup.id}/equipment`, {
      equipment_id: selectedEquipment.id,
      installation_notes: selectedEquipment.notes || ''
    })
    
    await loadEquipment()
    emit('show-notification', `${selectedEquipment.manufacturer} ${selectedEquipment.model_name} added successfully`, 'success')
    emit('equipment-updated')
    showEquipmentSelector.value = false
  } catch (error) {
    console.error('Error adding equipment:', error)
    emit('show-notification', 'Failed to add equipment', 'error')
  }
}

const editEquipment = (equipmentItem) => {
  editingEquipment.value = equipmentItem
}

const handleEquipmentUpdated = async (updatedEquipment) => {
  try {
    await api.put(`/bow-setups/${props.bowSetup.id}/equipment/${updatedEquipment.id}`, {
      installation_notes: updatedEquipment.installation_notes,
      custom_specifications: updatedEquipment.custom_specifications,
      is_active: updatedEquipment.is_active
    })
    
    await loadEquipment()
    emit('show-notification', 'Equipment updated successfully', 'success')
    emit('equipment-updated')
    editingEquipment.value = null
  } catch (error) {
    console.error('Error updating equipment:', error)
    emit('show-notification', 'Failed to update equipment', 'error')
  }
}

const removeEquipment = async (equipmentItem) => {
  if (!confirm(`Remove ${equipmentItem.manufacturer} ${equipmentItem.model_name} from this setup?`)) {
    return
  }
  
  try {
    await api.delete(`/bow-setups/${props.bowSetup.id}/equipment/${equipmentItem.id}`)
    await loadEquipment()
    emit('show-notification', 'Equipment removed successfully', 'success')
    emit('equipment-updated')
  } catch (error) {
    console.error('Error removing equipment:', error)
    emit('show-notification', 'Failed to remove equipment', 'error')
  }
}

const toggleCategory = (category) => {
  collapsedCategories.value[category] = !collapsedCategories.value[category]
}

const getCategoryIcon = (categoryName) => {
  const iconMap = {
    'String': 'fas fa-link',
    'Sight': 'fas fa-crosshairs',
    'Stabilizer': 'fas fa-balance-scale',
    'Arrow Rest': 'fas fa-hand-paper',
    'Weight': 'fas fa-weight-hanging'
  }
  return iconMap[categoryName] || 'fas fa-cog'
}

const getCategoryDisplayName = (categoryName) => {
  const displayNames = {
    'String': 'Strings & Cables',
    'Sight': 'Sights',
    'Stabilizer': 'Stabilizers',
    'Arrow Rest': 'Arrow Rests',
    'Weight': 'Weights'
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
    'Weight': ['weight_ounces', 'weight_type']
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