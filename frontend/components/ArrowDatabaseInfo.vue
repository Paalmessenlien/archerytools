<template>
  <div class="space-y-4">
    <!-- Basic Information -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Manufacturer</label>
        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ arrow?.manufacturer || 'Unknown' }}</p>
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Model</label>
        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ arrow?.model_name || 'Unknown' }}</p>
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Material</label>
        <p class="text-sm text-gray-700 dark:text-gray-300">{{ arrow?.material || 'Not specified' }}</p>
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Arrow Type</label>
        <p class="text-sm text-gray-700 dark:text-gray-300">{{ arrow?.arrow_type || 'Not specified' }}</p>
      </div>
    </div>
    
    <!-- Additional Details -->
    <div v-if="arrow?.carbon_content || arrow?.straightness_tolerance || arrow?.weight_tolerance" class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <h5 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Technical Specifications</h5>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div v-if="arrow.carbon_content">
          <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Carbon Content</label>
          <p class="text-sm text-gray-700 dark:text-gray-300">{{ arrow.carbon_content }}</p>
        </div>
        
        <div v-if="arrow.straightness_tolerance">
          <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Straightness</label>
          <p class="text-sm text-gray-700 dark:text-gray-300">{{ arrow.straightness_tolerance }}</p>
        </div>
        
        <div v-if="arrow.weight_tolerance">
          <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Weight Tolerance</label>
          <p class="text-sm text-gray-700 dark:text-gray-300">{{ arrow.weight_tolerance }}</p>
        </div>
      </div>
    </div>
    
    <!-- Spine Options Summary -->
    <div v-if="spineSpecifications.length > 0" class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <h5 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
        Available Spine Options ({{ spineSpecifications.length }})
      </h5>
      
      <div class="flex flex-wrap gap-2">
        <span 
          v-for="spec in spineSpecifications.slice(0, 8)" 
          :key="spec.spine"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
        >
          {{ spec.spine }} ({{ spec.gpi_weight?.toFixed(1) || 'N/A' }} GPI)
        </span>
        <span 
          v-if="spineSpecifications.length > 8"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
        >
          +{{ spineSpecifications.length - 8 }} more
        </span>
      </div>
    </div>
    
    <!-- Description -->
    <div v-if="arrow?.description" class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Description</label>
      <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
        {{ arrow.description }}
      </p>
    </div>
    
    <!-- Image -->
    <div v-if="arrow?.primary_image_url" class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Product Image</label>
      <img 
        :src="arrow.primary_image_url" 
        :alt="`${arrow.manufacturer} ${arrow.model_name}`"
        class="max-w-full h-32 object-contain rounded-lg border border-gray-200 dark:border-gray-700"
        @error="imageError = true"
      />
      <div v-if="imageError" class="text-center text-gray-500 py-8 text-sm">
        Image not available
      </div>
    </div>
    
    <!-- Source Link -->
    <div v-if="arrow?.source_url" class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <a 
        :href="arrow.source_url" 
        target="_blank" 
        rel="noopener noreferrer"
        class="inline-flex items-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
      >
        <i class="fas fa-external-link-alt mr-2"></i>
        View Original Source
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  arrow: {
    type: Object,
    default: null
  },
  spineSpecifications: {
    type: Array,
    default: () => []
  }
})

const imageError = ref(false)
</script>