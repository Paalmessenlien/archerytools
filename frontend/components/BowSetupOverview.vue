<template>
  <div class="bow-setup-overview space-y-6">
    <!-- Basic Information Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-info-circle mr-2 text-blue-600 dark:text-blue-400"></i>
        Bow Information
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Bow Type -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-archway text-blue-600 dark:text-blue-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Bow Type</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.bow_type }}</p>
          </div>
        </div>

        <!-- Draw Weight -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-dumbbell text-green-600 dark:text-green-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Draw Weight</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.draw_weight }}#</p>
          </div>
        </div>

        <!-- Usage -->
        <div v-if="setup.bow_usage" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-target text-purple-600 dark:text-purple-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Usage</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ formatUsage(setup.bow_usage) }}</p>
          </div>
        </div>

        <!-- Draw Length (if available) -->
        <div v-if="setup.draw_length" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-ruler text-orange-600 dark:text-orange-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Draw Length</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.draw_length }}"</p>
          </div>
        </div>

        <!-- IBO Speed (if available) -->
        <div v-if="setup.ibo_speed" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-tachometer-alt text-red-600 dark:text-red-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">IBO Speed</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.ibo_speed }} fps</p>
          </div>
        </div>

        <!-- Created Date -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
            <i class="fas fa-calendar text-gray-600 dark:text-gray-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Created</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ formatDate(setup.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bow Details (for compound/recurve bows) -->
    <div v-if="showBowDetails" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-cogs mr-2 text-green-600 dark:text-green-400"></i>
        {{ setup.bow_type === 'Compound' ? 'Compound Bow Details' : 'Recurve Bow Details' }}
      </h3>
      
      <!-- Compound Bow Details -->
      <div v-if="setup.bow_type === 'Compound'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-if="setup.compound_brand" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-tag text-blue-600 dark:text-blue-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Brand</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.compound_brand }}</p>
          </div>
        </div>

        <div v-if="setup.compound_model" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-barcode text-green-600 dark:text-green-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Model</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.compound_model }}</p>
          </div>
        </div>
      </div>

      <!-- Recurve Bow Details -->
      <div v-else-if="setup.bow_type === 'Recurve'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Riser Details -->
        <div v-if="setup.riser_brand" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-grip-vertical text-blue-600 dark:text-blue-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Riser Brand</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.riser_brand }}</p>
          </div>
        </div>

        <div v-if="setup.riser_model" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-barcode text-green-600 dark:text-green-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Riser Model</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.riser_model }}</p>
          </div>
        </div>

        <div v-if="setup.riser_length" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-ruler-horizontal text-purple-600 dark:text-purple-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Riser Length</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.riser_length }}"</p>
          </div>
        </div>

        <!-- Limb Details -->
        <div v-if="setup.limb_brand" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-grip-lines text-orange-600 dark:text-orange-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Limb Brand</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.limb_brand }}</p>
          </div>
        </div>

        <div v-if="setup.limb_model" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-barcode text-red-600 dark:text-red-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Limb Model</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.limb_model }}</p>
          </div>
        </div>

        <div v-if="setup.limb_length" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-ruler-horizontal text-yellow-600 dark:text-yellow-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Limb Length</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.limb_length }}"</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Description -->
    <div v-if="setup.description" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-file-alt mr-2 text-purple-600 dark:text-purple-400"></i>
        Description
      </h3>
      <p class="text-gray-700 dark:text-gray-300 leading-relaxed">{{ setup.description }}</p>
    </div>

    <!-- Statistics Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Arrows Count -->
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1">Arrows</p>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">{{ statistics.arrow_count || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-200 dark:bg-blue-800 rounded-lg flex items-center justify-center">
            <i class="fas fa-bullseye text-blue-600 dark:text-blue-400 text-xl"></i>
          </div>
        </div>
      </div>

      <!-- Equipment Count -->
      <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-green-600 dark:text-green-400 mb-1">Equipment</p>
            <p class="text-2xl font-bold text-green-900 dark:text-green-100">{{ statistics.equipment_count || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-green-200 dark:bg-green-800 rounded-lg flex items-center justify-center">
            <i class="fas fa-cogs text-green-600 dark:text-green-400 text-xl"></i>
          </div>
        </div>
      </div>

      <!-- Changes Count -->
      <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-purple-600 dark:text-purple-400 mb-1">Changes</p>
            <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">{{ statistics.total_changes || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-200 dark:bg-purple-800 rounded-lg flex items-center justify-center">
            <i class="fas fa-history text-purple-600 dark:text-purple-400 text-xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-lightning-bolt mr-2 text-yellow-600 dark:text-yellow-400"></i>
        Quick Actions
      </h3>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <CustomButton
          @click="$emit('switch-tab', 'arrows')"
          variant="outlined"
          class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900/20"
        >
          <i class="fas fa-bullseye mr-2"></i>
          Manage Arrows
        </CustomButton>

        <CustomButton
          @click="$emit('switch-tab', 'equipment')"
          variant="outlined"
          class="text-green-600 border-green-600 hover:bg-green-50 dark:text-green-400 dark:border-green-400 dark:hover:bg-green-900/20"
        >
          <i class="fas fa-cogs mr-2"></i>
          Manage Equipment
        </CustomButton>

        <CustomButton
          @click="$emit('switch-tab', 'history')"
          variant="outlined"
          class="text-purple-600 border-purple-600 hover:bg-purple-50 dark:text-purple-400 dark:border-purple-400 dark:hover:bg-purple-900/20"
        >
          <i class="fas fa-history mr-2"></i>
          View History
        </CustomButton>

        <CustomButton
          @click="$emit('switch-tab', 'settings')"
          variant="outlined"
          class="text-gray-600 border-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-400 dark:hover:bg-gray-700"
        >
          <i class="fas fa-cog mr-2"></i>
          Settings
        </CustomButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CustomButton from './CustomButton.vue'

const props = defineProps({
  setup: {
    type: Object,
    required: true
  },
  statistics: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['switch-tab'])

// Computed properties
const showBowDetails = computed(() => {
  return (props.setup.bow_type === 'Compound' && (props.setup.compound_brand || props.setup.compound_model)) ||
         (props.setup.bow_type === 'Recurve' && (props.setup.riser_brand || props.setup.riser_model || props.setup.limb_brand || props.setup.limb_model))
})

// Methods
const formatUsage = (usage) => {
  if (!usage) return 'Not specified'
  
  // Handle array format (JSON string or actual array)
  if (typeof usage === 'string' && usage.startsWith('[')) {
    try {
      const parsed = JSON.parse(usage)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed.join(', ')
      }
    } catch (e) {
      // If parsing fails, treat as regular string
    }
  }
  
  // Handle actual array
  if (Array.isArray(usage) && usage.length > 0) {
    return usage.join(', ')
  }
  
  // Handle regular string
  if (typeof usage === 'string') {
    return usage.charAt(0).toUpperCase() + usage.slice(1)
  }
  
  return 'Not specified'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return 'Unknown'
  }
}
</script>

<style scoped>
/* Component-specific styles if needed */
.bow-setup-overview {
  /* Any custom styling for the overview component */
}
</style>