<template>
  <div v-if="savedSetups.length > 0" class="mt-8 space-y-4">
    <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
      <i class="fas fa-bookmark mr-2 text-green-600"></i>
      Saved Arrow Setups
    </h3>

    <div class="space-y-3">
      <div 
        v-for="setup in savedSetups" 
        :key="setup.id"
        class="p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg border border-green-200 dark:border-green-700"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <!-- Configuration Name -->
            <div class="flex items-center mb-2">
              <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ setup.arrow_config.name }}</h4>
              <span class="ml-2 px-2 py-1 text-xs rounded-full" 
                    :class="getMatchClass(setup.match_percentage)">
                {{ setup.match_percentage }}% match
              </span>
            </div>

            <!-- Arrow Information -->
            <div class="bg-white dark:bg-gray-800 rounded-lg p-3 mb-3">
              <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-2">
                {{ setup.database_arrow.manufacturer }} {{ setup.database_arrow.model_name }}
              </h5>
              
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <span class="text-gray-600 dark:text-gray-400">Spine:</span>
                  <span class="font-medium ml-1">{{ setup.spine_spec.spine }}</span>
                </div>
                <div>
                  <span class="text-gray-600 dark:text-gray-400">Diameter:</span>
                  <span class="font-medium ml-1">{{ setup.spine_spec.outer_diameter }}"</span>
                </div>
                <div>
                  <span class="text-gray-600 dark:text-gray-400">GPI:</span>
                  <span class="font-medium ml-1">{{ setup.spine_spec.gpi_weight }}</span>
                </div>
                <div v-if="setup.database_arrow.material">
                  <span class="text-gray-600 dark:text-gray-400">Material:</span>
                  <span class="font-medium ml-1">{{ setup.database_arrow.material }}</span>
                </div>
              </div>

              <div v-if="setup.database_arrow.arrow_type" class="mt-2 text-sm">
                <span class="text-gray-600 dark:text-gray-400">Type:</span>
                <span class="inline-block ml-1 px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                  {{ formatArrowType(setup.database_arrow.arrow_type) }}
                </span>
              </div>
            </div>

            <!-- Configuration Details -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div>
                <span class="text-gray-600 dark:text-gray-400">Length:</span>
                <span class="font-medium ml-1">{{ setup.arrow_config.arrow_length }}"</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">Point:</span>
                <span class="font-medium ml-1">{{ setup.arrow_config.point_weight }}gr</span>
              </div>
              <div v-if="setup.arrow_config.total_weight">
                <span class="text-gray-600 dark:text-gray-400">Total Weight:</span>
                <span class="font-medium ml-1">{{ setup.arrow_config.total_weight }}gr</span>
              </div>
              <div v-if="setup.arrow_config.calculated_foc">
                <span class="text-gray-600 dark:text-gray-400">FOC:</span>
                <span class="font-medium ml-1">{{ setup.arrow_config.calculated_foc }}%</span>
              </div>
            </div>

            <div v-if="setup.arrow_config.notes" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              <i class="fas fa-sticky-note mr-1"></i>
              {{ setup.arrow_config.notes }}
            </div>

            <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
              Saved: {{ formatDate(setup.saved_at) }}
            </div>
          </div>

          <div class="flex flex-col space-y-2 ml-4">
            <CustomButton
              @click="editSetup(setup)"
              variant="outlined"
              size="small"
              class="text-orange-600 border-orange-600 hover:bg-orange-50 dark:text-orange-400 dark:border-orange-400 dark:hover:bg-orange-900/20"
            >
              <i class="fas fa-edit mr-1"></i>
              Edit
            </CustomButton>
            <CustomButton
              @click="duplicateSetup(setup)"
              variant="outlined"
              size="small"
              class="text-purple-600 border-purple-600 hover:bg-purple-50 dark:text-purple-400 dark:border-purple-400 dark:hover:bg-purple-900/20"
            >
              <i class="fas fa-copy mr-1"></i>
              Duplicate
            </CustomButton>
            <CustomButton
              @click="viewArrowDetails(setup.database_arrow)"
              variant="outlined"
              size="small"
              class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900/20"
            >
              <i class="fas fa-info-circle mr-1"></i>
              Details
            </CustomButton>
            <CustomButton
              @click="removeSetup(setup)"
              variant="outlined"
              size="small"
              class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900/20"
            >
              <i class="fas fa-trash mr-1"></i>
              Remove
            </CustomButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  savedSetups: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['remove-setup', 'confirm-remove', 'edit-setup', 'duplicate-setup'])

const editSetup = (setup) => {
  emit('edit-setup', setup)
}

const duplicateSetup = (setup) => {
  emit('duplicate-setup', setup)
}

const removeSetup = (setup) => {
  // Emit confirmation request to parent instead of using browser confirm
  emit('confirm-remove', {
    setup,
    message: `Remove ${setup.database_arrow.manufacturer} ${setup.database_arrow.model_name} from "${setup.arrow_config.name}"?`
  })
}

const viewArrowDetails = (arrow) => {
  // Navigate to arrow details page
  navigateTo(`/arrows/${arrow.id}`)
}

const getMatchClass = (percentage) => {
  if (percentage >= 90) {
    return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  } else if (percentage >= 70) {
    return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  } else {
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
}

const formatArrowType = (arrowType) => {
  if (!arrowType) return 'Unknown'
  
  return arrowType
    .split(/[-_\s]+/)
    .filter(word => word && word.length > 0)
    .map(word => word && word.length > 0 ? word.charAt(0).toUpperCase() + word.slice(1).toLowerCase() : '')
    .filter(word => word.length > 0)
    .join(' ')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateString
  }
}
</script>