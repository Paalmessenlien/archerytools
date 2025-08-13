<template>
  <div class="equipment-list">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        <i class="fas fa-cogs mr-2 text-blue-600 dark:text-purple-400"></i>
        Equipment
      </h3>
      <CustomButton
        v-if="showAddButton"
        @click="$emit('add-equipment')"
        variant="outlined"
        size="small"
        class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-purple-400 dark:border-purple-400"
      >
        <i class="fas fa-plus mr-1"></i>
        Add Equipment
      </CustomButton>
    </div>

    <!-- Equipment Items -->
    <div v-if="loading" class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Loading equipment...</p>
    </div>

    <div v-else-if="equipment.length === 0" class="text-center py-8">
      <i class="fas fa-cogs text-3xl text-gray-400 mb-4"></i>
      <p class="text-gray-600 dark:text-gray-400 mb-4">No equipment added yet.</p>
      <CustomButton
        v-if="showAddButton"
        @click="$emit('add-equipment')"
        variant="filled"
        class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
      >
        <i class="fas fa-plus mr-2"></i>
        Add Your First Equipment
      </CustomButton>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in groupedEquipment"
        :key="item.category_name"
        class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4"
      >
        <!-- Category Header -->
        <div class="flex items-center mb-3">
          <i :class="getCategoryIcon(item.category_name)" class="text-lg text-blue-600 dark:text-purple-400 mr-2"></i>
          <h4 class="font-semibold text-gray-900 dark:text-gray-100">{{ item.category_name }}</h4>
          <span class="ml-2 text-sm text-gray-500 dark:text-gray-400">({{ item.items.length }})</span>
        </div>

        <!-- Equipment Items in Category -->
        <div class="space-y-3">
          <div
            v-for="equipment in item.items"
            :key="equipment.id"
            class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600"
          >
            <div class="flex items-start justify-between">
              <!-- Equipment Info -->
              <div class="flex-1">
                <div class="flex items-start justify-between mb-2">
                  <div>
                    <h5 class="font-semibold text-gray-900 dark:text-gray-100">
                      {{ equipment.manufacturer }} {{ equipment.model_name }}
                    </h5>
                    <p v-if="equipment.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {{ equipment.description }}
                    </p>
                  </div>

                  <!-- Weight Badge -->
                  <span 
                    v-if="equipment.weight_grams" 
                    class="ml-4 px-2 py-1 text-xs bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 rounded-full"
                  >
                    {{ equipment.weight_grams }}g
                  </span>
                </div>

                <!-- Specifications -->
                <div v-if="equipment.specifications" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 mb-3">
                  <div
                    v-for="(value, key) in getDisplaySpecs(equipment.specifications)"
                    :key="key"
                    class="text-sm"
                  >
                    <span class="text-gray-500 dark:text-gray-400">{{ formatSpecKey(key) }}:</span>
                    <span class="ml-1 text-gray-700 dark:text-gray-300 font-medium">{{ formatSpecValue(value) }}</span>
                  </div>
                </div>

                <!-- Custom Specifications (if any) -->
                <div v-if="equipment.custom_specifications && Object.keys(equipment.custom_specifications).length > 0" class="mb-3">
                  <p class="text-sm text-blue-600 dark:text-purple-400 font-medium mb-1">Custom Settings:</p>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <div
                      v-for="(value, key) in equipment.custom_specifications"
                      :key="key"
                      class="text-sm"
                    >
                      <span class="text-gray-500 dark:text-gray-400">{{ formatSpecKey(key) }}:</span>
                      <span class="ml-1 text-gray-700 dark:text-gray-300 font-medium">{{ formatSpecValue(value) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Installation Notes -->
                <div v-if="equipment.installation_notes" class="mb-3">
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    <i class="fas fa-sticky-note mr-1"></i>
                    {{ equipment.installation_notes }}
                  </p>
                </div>

                <!-- Installation Date -->
                <div v-if="equipment.installation_date" class="text-xs text-gray-500 dark:text-gray-400">
                  Installed: {{ formatDate(equipment.installation_date) }}
                </div>
              </div>

              <!-- Actions -->
              <div v-if="showActions" class="ml-4 flex space-x-2">
                <button
                  @click="$emit('edit-equipment', equipment)"
                  class="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-purple-400 transition-colors"
                  title="Edit equipment"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button
                  @click="$emit('remove-equipment', equipment)"
                  class="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Remove equipment"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Total Weight Summary -->
      <div v-if="totalWeight > 0" class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-blue-800 dark:text-blue-300">
            <i class="fas fa-weight-hanging mr-2"></i>
            Total Equipment Weight
          </span>
          <span class="text-lg font-bold text-blue-900 dark:text-blue-200">
            {{ totalWeight }}g ({{ (totalWeight / 28.35).toFixed(1) }}oz)
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  equipment: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  showAddButton: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['add-equipment', 'edit-equipment', 'remove-equipment'])

// Computed
const groupedEquipment = computed(() => {
  const groups = {}
  
  props.equipment.forEach(item => {
    const category = item.category_name
    if (!groups[category]) {
      groups[category] = {
        category_name: category,
        items: []
      }
    }
    groups[category].items.push(item)
  })
  
  return Object.values(groups).sort((a, b) => a.category_name.localeCompare(b.category_name))
})

const totalWeight = computed(() => {
  return props.equipment.reduce((total, item) => {
    return total + (item.weight_grams || 0)
  }, 0)
})

// Methods
const getCategoryIcon = (categoryName) => {
  const iconMap = {
    'String': 'fas fa-link',
    'Sight': 'fas fa-crosshairs',
    'Scope': 'fas fa-search',
    'Stabilizer': 'fas fa-balance-scale',
    'Arrow Rest': 'fas fa-hand-paper',
    'Plunger': 'fas fa-bullseye',
    'Weight': 'fas fa-weight-hanging',
    'Other': 'fas fa-cog'
  }
  return iconMap[categoryName] || 'fas fa-cog'
}

const getDisplaySpecs = (specs) => {
  if (!specs) return {}
  
  // Show the most important specs, limit to avoid clutter
  const important = {}
  let count = 0
  const maxSpecs = 6
  
  for (const [key, value] of Object.entries(specs)) {
    if (count >= maxSpecs) break
    if (value !== undefined && value !== null && value !== '') {
      important[key] = value
      count++
    }
  }
  
  return important
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
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return dateString
  }
}
</script>