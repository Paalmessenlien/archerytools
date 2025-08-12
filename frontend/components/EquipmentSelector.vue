<template>
  <div class="equipment-selector">
    <!-- Equipment Category Tabs -->
    <div class="flex flex-wrap gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
      <button
        v-for="category in categories"
        :key="category.id"
        @click="selectedCategory = category.name"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors',
          selectedCategory === category.name
            ? 'text-blue-600 border-blue-600 bg-blue-50 dark:text-purple-400 dark:border-purple-400 dark:bg-purple-900/20'
            : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
        ]"
      >
        <i :class="category.icon" class="mr-2"></i>
        {{ category.name }}
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="mb-6 space-y-4">
      <div class="flex flex-col gap-4 md:flex-row">
        <!-- Search Input -->
        <div class="flex-1">
          <div class="relative">
            <i class="absolute left-3 top-1/2 transform -translate-y-1/2 fas fa-search text-gray-400"></i>
            <input
              v-model="searchKeywords"
              type="text"
              placeholder="Search equipment..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
            />
          </div>
        </div>

        <!-- Manufacturer Filter -->
        <div class="w-full md:w-48">
          <select
            v-model="selectedManufacturer"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          >
            <option value="">All Manufacturers</option>
            <option
              v-for="manufacturer in manufacturers"
              :key="manufacturer"
              :value="manufacturer"
            >
              {{ manufacturer }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Equipment List -->
    <div v-if="loading" class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Loading equipment...</p>
    </div>

    <div v-else-if="filteredEquipment.length === 0" class="text-center py-8">
      <i class="fas fa-search text-3xl text-gray-400 mb-4"></i>
      <p class="text-gray-600 dark:text-gray-400">No equipment found matching your criteria.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="item in filteredEquipment"
        :key="item.id"
        @click="$emit('select', item)"
        class="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer dark:border-gray-600 dark:hover:border-blue-400 dark:bg-gray-800"
      >
        <!-- Equipment Image -->
        <div class="w-full h-32 bg-gray-100 dark:bg-gray-700 rounded-lg mb-3 flex items-center justify-center">
          <i 
            v-if="!item.image_url" 
            :class="getCategoryIcon(item.category_name)" 
            class="text-3xl text-gray-400"
          ></i>
          <img 
            v-else 
            :src="item.image_url" 
            :alt="item.model_name"
            class="w-full h-full object-cover rounded-lg"
          />
        </div>

        <!-- Equipment Info -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-medium text-blue-600 dark:text-purple-400 uppercase tracking-wide">
              {{ item.category_name }}
            </span>
            <span v-if="item.weight_grams" class="text-xs text-gray-500 dark:text-gray-400">
              {{ item.weight_grams }}g
            </span>
          </div>

          <h3 class="font-semibold text-gray-900 dark:text-gray-100 line-clamp-2">
            {{ item.manufacturer }} {{ item.model_name }}
          </h3>

          <p v-if="item.description" class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
            {{ item.description }}
          </p>

          <!-- Key Specifications -->
          <div v-if="item.specifications" class="space-y-1">
            <div
              v-for="(value, key) in getKeySpecs(item.specifications, item.category_name)"
              :key="key"
              class="flex justify-between text-xs"
            >
              <span class="text-gray-500 dark:text-gray-400 capitalize">{{ formatSpecKey(key) }}:</span>
              <span class="text-gray-700 dark:text-gray-300 font-medium">{{ formatSpecValue(value) }}</span>
            </div>
          </div>

          <!-- Price Range -->
          <div v-if="item.price_range" class="pt-2 border-t border-gray-200 dark:border-gray-600">
            <span class="text-sm font-medium text-green-600 dark:text-green-400">
              {{ item.price_range }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const emit = defineEmits(['select'])

// Data
const categories = ref([])
const equipment = ref([])
const loading = ref(false)
const selectedCategory = ref('')
const searchKeywords = ref('')
const selectedManufacturer = ref('')

// Computed
const filteredEquipment = computed(() => {
  let filtered = equipment.value

  // Filter by category
  if (selectedCategory.value) {
    filtered = filtered.filter(item => item.category_name === selectedCategory.value)
  }

  // Filter by manufacturer
  if (selectedManufacturer.value) {
    filtered = filtered.filter(item => 
      item.manufacturer.toLowerCase().includes(selectedManufacturer.value.toLowerCase())
    )
  }

  // Filter by search keywords
  if (searchKeywords.value) {
    const keywords = searchKeywords.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.model_name.toLowerCase().includes(keywords) ||
      item.manufacturer.toLowerCase().includes(keywords) ||
      (item.description && item.description.toLowerCase().includes(keywords))
    )
  }

  return filtered
})

const manufacturers = computed(() => {
  const unique = [...new Set(equipment.value.map(item => item.manufacturer))]
  return unique.sort()
})

// Methods
const loadCategories = async () => {
  try {
    const { $fetch } = useNuxtApp()
    categories.value = await $fetch('/api/equipment/categories')
    
    // Set default category
    if (categories.value.length > 0) {
      selectedCategory.value = categories.value[0].name
    }
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const loadEquipment = async () => {
  loading.value = true
  try {
    const { $fetch } = useNuxtApp()
    const params = new URLSearchParams()
    
    if (selectedCategory.value) {
      params.append('category', selectedCategory.value)
    }
    if (selectedManufacturer.value) {
      params.append('manufacturer', selectedManufacturer.value)
    }
    if (searchKeywords.value) {
      params.append('keywords', searchKeywords.value)
    }

    equipment.value = await $fetch(`/api/equipment/search?${params.toString()}`)
  } catch (error) {
    console.error('Error loading equipment:', error)
    equipment.value = []
  } finally {
    loading.value = false
  }
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

const getKeySpecs = (specs, category) => {
  if (!specs) return {}
  
  const keySpecsMap = {
    'String': ['material', 'strand_count', 'bow_weight_range'],
    'Sight': ['sight_type', 'pin_count', 'adjustment_type'],
    'Stabilizer': ['length_inches', 'weight_ounces', 'material'],
    'Arrow Rest': ['rest_type', 'activation_type', 'arrow_containment'],
    'Weight': ['weight_ounces', 'mounting_location', 'weight_type']
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

// Watchers
watch([selectedCategory, selectedManufacturer, searchKeywords], () => {
  loadEquipment()
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await loadCategories()
  await loadEquipment()
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