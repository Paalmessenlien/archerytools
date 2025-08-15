<template>
  <div class="space-y-4">
    <!-- Bow Setup Name -->
    <div class="flex items-center justify-between">
      <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ bowSetup.name }}</h4>
      <button
        @click="emit('edit-bow')"
        class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
      >
        <i class="fas fa-edit mr-1"></i>
        Edit Setup
      </button>
    </div>
    
    <!-- Bow Specifications -->
    <div class="grid grid-cols-1 gap-3">
      <!-- Bow Type -->
      <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700">
        <span class="text-sm text-gray-600 dark:text-gray-400">Bow Type</span>
        <span class="text-sm font-medium text-gray-900 dark:text-gray-100 capitalize">
          {{ bowSetup.bow_type || 'Unknown' }}
        </span>
      </div>
      
      <!-- Draw Weight -->
      <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700">
        <span class="text-sm text-gray-600 dark:text-gray-400">Draw Weight</span>
        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
          {{ bowSetup.draw_weight || 'N/A' }} lbs
        </span>
      </div>
      
      <!-- Draw Length -->
      <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700">
        <span class="text-sm text-gray-600 dark:text-gray-400">Draw Length</span>
        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
          {{ bowSetup.draw_length || 'N/A' }}"
        </span>
      </div>
      
      <!-- IBO Speed -->
      <div v-if="bowSetup.ibo_speed" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700">
        <span class="text-sm text-gray-600 dark:text-gray-400">IBO Speed</span>
        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
          {{ bowSetup.ibo_speed }} fps
        </span>
      </div>
      
      <!-- Let-off -->
      <div v-if="bowSetup.let_off_percentage" class="flex items-center justify-between py-2">
        <span class="text-sm text-gray-600 dark:text-gray-400">Let-off</span>
        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
          {{ bowSetup.let_off_percentage }}%
        </span>
      </div>
    </div>
    
    <!-- Recommendations -->
    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 mt-4">
      <h5 class="text-xs font-medium text-blue-800 dark:text-blue-200 mb-2">
        <i class="fas fa-lightbulb mr-1"></i>
        Bow Setup Insights
      </h5>
      <div class="space-y-1 text-xs text-blue-700 dark:text-blue-300">
        <div>• {{ getBowTypeInsight() }}</div>
        <div>• {{ getDrawWeightInsight() }}</div>
        <div>• {{ getSpeedInsight() }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit-bow'])

// Helper methods
const getBowTypeInsight = () => {
  const bowType = props.bowSetup.bow_type
  switch (bowType) {
    case 'compound':
      return 'Compound bow - High performance with consistent draw weight'
    case 'recurve':
      return 'Recurve bow - Traditional style with smooth draw cycle'
    case 'traditional':
      return 'Traditional bow - Classic archery with instinctive shooting'
    case 'longbow':
      return 'Longbow - Simple design with smooth release'
    default:
      return 'Bow type affects arrow spine requirements and performance'
  }
}

const getDrawWeightInsight = () => {
  const weight = props.bowSetup.draw_weight
  if (!weight) return 'Draw weight determines arrow spine requirements'
  
  if (weight < 40) return 'Light draw weight - Good for beginners and target shooting'
  if (weight < 60) return 'Medium draw weight - Versatile for target and hunting'
  if (weight < 80) return 'Heavy draw weight - Excellent for hunting applications'
  return 'Very heavy draw weight - Maximum performance for experienced archers'
}

const getSpeedInsight = () => {
  const speed = props.bowSetup.ibo_speed
  if (!speed) return 'IBO speed affects arrow trajectory and kinetic energy'
  
  if (speed < 300) return 'Moderate speed bow - Good accuracy and arrow life'
  if (speed < 340) return 'Fast bow - Good balance of speed and accuracy'
  return 'Very fast bow - Maximum performance with proper arrow selection'
}
</script>