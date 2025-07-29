<template>
  <div>
    <!-- Breadcrumb Navigation -->
    <nav class="mb-6">
      <ol class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
        <li>
          <NuxtLink to="/tuning" class="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            Interactive Tuning
          </NuxtLink>
        </li>
        <li class="flex items-center">
          <i class="fas fa-chevron-right mx-2"></i>
          <span class="text-gray-900 dark:text-gray-100">Session Details</span>
        </li>
      </ol>
    </nav>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-blue-500 text-4xl mb-4"></i>
      <p class="text-gray-600 dark:text-gray-300">Loading session details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
      <p class="text-red-600 dark:text-red-400 mb-4">{{ error }}</p>
      <NuxtLink 
        to="/tuning"
        class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
      >
        <i class="fas fa-arrow-left mr-2"></i>
        Back to Tuning
      </NuxtLink>
    </div>

    <!-- Session Content -->
    <div v-else-if="sessionData" class="space-y-6">
      <!-- Session Header -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ sessionData.session.guide_name }}</h1>
            <p class="text-gray-600 dark:text-gray-300">{{ sessionData.session.guide_type }} guide session</p>
          </div>
          <span :class="[
            'px-3 py-1 text-sm font-medium rounded-full',
            sessionData.session.status === 'completed' 
              ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
              : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
          ]">
            {{ formatStatus(sessionData.session.status) }}
          </span>
        </div>

        <!-- Session Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
            <div class="flex items-center">
              <i class="fas fa-archway text-blue-600 dark:text-blue-400 mr-3"></i>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400">Bow Setup</p>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ sessionData.session.bow_name || 'No bow selected' }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
            <div class="flex items-center">
              <i class="fas fa-calendar text-green-600 dark:text-green-400 mr-3"></i>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400">Started</p>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ formatDate(sessionData.session.started_at) }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
            <div class="flex items-center">
              <i class="fas fa-check text-purple-600 dark:text-purple-400 mr-3"></i>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400">Progress</p>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ sessionData.steps.length }}/{{ sessionData.session.total_steps }} steps</p>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
            <div class="flex items-center">
              <i class="fas fa-clock text-orange-600 dark:text-orange-400 mr-3"></i>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400">Duration</p>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ calculateDuration() }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Bow Details (if available) -->
        <div v-if="sessionData.session.bow_type" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
          <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Bow Configuration</h3>
          <div class="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-300">
            <span><strong>Type:</strong> {{ formatBowType(sessionData.session.bow_type) }}</span>
            <span v-if="sessionData.session.draw_weight"><strong>Draw Weight:</strong> {{ sessionData.session.draw_weight }}lbs</span>
            <span v-if="sessionData.session.draw_length"><strong>Draw Length:</strong> {{ sessionData.session.draw_length }}"</span>
          </div>
        </div>
      </div>

      <!-- Progress Visualization -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-chart-line mr-2"></i>
          Progress Overview
        </h2>
        
        <!-- Progress Bar -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">Completion Progress</span>
            <span class="text-sm text-gray-500 dark:text-gray-400">
              {{ Math.round((sessionData.steps.length / sessionData.session.total_steps) * 100) }}%
            </span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div 
              class="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-300"
              :style="{ width: `${(sessionData.steps.length / sessionData.session.total_steps) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Step Timeline -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">Step Timeline</h3>
          <div class="space-y-3">
            <div 
              v-for="(step, index) in sessionData.steps" 
              :key="step.id"
              class="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
            >
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-green-700 dark:text-green-300">{{ step.step_number }}</span>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ step.step_name }}</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatDate(step.completed_at) }}</p>
                
                <!-- Step Details -->
                <div class="mt-2 space-y-1">
                  <div v-if="step.result_type" class="text-sm">
                    <span class="font-medium text-gray-700 dark:text-gray-300">Type:</span>
                    <span class="ml-1 px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs">
                      {{ formatResultType(step.result_type) }}
                    </span>
                  </div>
                  <div v-if="step.result_value" class="text-sm text-gray-600 dark:text-gray-300">
                    <span class="font-medium text-gray-700 dark:text-gray-300">Result:</span>
                    {{ step.result_value }}
                  </div>
                  <div v-if="step.measurements" class="text-sm text-gray-600 dark:text-gray-300">
                    <span class="font-medium text-gray-700 dark:text-gray-300">Measurements:</span>
                    {{ step.measurements }}
                  </div>
                  <div v-if="step.adjustments_made" class="text-sm text-gray-600 dark:text-gray-300">
                    <span class="font-medium text-gray-700 dark:text-gray-300">Adjustments:</span>
                    {{ step.adjustments_made }}
                  </div>
                  <div v-if="step.notes" class="text-sm text-gray-600 dark:text-gray-300">
                    <span class="font-medium text-gray-700 dark:text-gray-300">Notes:</span>
                    {{ step.notes }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Session Notes -->
      <div v-if="sessionData.session.notes" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-sticky-note mr-2"></i>
          Session Notes
        </h2>
        <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p class="text-gray-700 dark:text-gray-300">{{ sessionData.session.notes }}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between">
        <NuxtLink 
          to="/tuning"
          class="inline-flex items-center px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
        >
          <i class="fas fa-arrow-left mr-2"></i>
          Back to Tuning
        </NuxtLink>
        
        <div class="space-x-3">
          <button 
            @click="exportSession"
            class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-download mr-2"></i>
            Export Session
          </button>
          
          <button 
            v-if="sessionData.session.status === 'in_progress'"
            @click="resumeSession"
            class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-play mr-2"></i>
            Resume Session
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '~/composables/useApi'

// Set page title and meta
useHead({
  title: 'Session Details - Interactive Tuning',
  meta: [
    { name: 'description', content: 'View detailed information about your tuning guide session including progress and results.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})

// Route and API
const route = useRoute()
const { $fetch } = useApi()

// Reactive data
const sessionData = ref(null)
const loading = ref(true)
const error = ref(null)

// Methods
const loadSessionDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const sessionId = route.params.id
    const response = await $fetch(`/api/guide-sessions/${sessionId}`)
    sessionData.value = response
  } catch (err) {
    console.error('Error loading session details:', err)
    error.value = err.response?.status === 404 ? 'Session not found' : 'Failed to load session details'
  } finally {
    loading.value = false
  }
}

const calculateDuration = () => {
  if (!sessionData.value) return 'N/A'
  
  const start = new Date(sessionData.value.session.started_at)
  const end = sessionData.value.session.completed_at 
    ? new Date(sessionData.value.session.completed_at)
    : new Date()
  
  const diffMs = end - start
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  
  if (diffHours > 0) {
    return `${diffHours}h ${diffMins % 60}m`
  } else {
    return `${diffMins}m`
  }
}

const exportSession = () => {
  if (!sessionData.value) return
  
  const exportData = {
    session: sessionData.value.session,
    steps: sessionData.value.steps,
    exported_at: new Date().toISOString()
  }
  
  const dataStr = JSON.stringify(exportData, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `tuning-session-${sessionData.value.session.id}-${new Date().toISOString().split('T')[0]}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}

const resumeSession = () => {
  navigateTo('/tuning')
}

// Helper functions
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')
}

const formatBowType = (bowType) => {
  return bowType.charAt(0).toUpperCase() + bowType.slice(1)
}

const formatResultType = (type) => {
  return type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Load data on mount
onMounted(() => {
  loadSessionDetails()
})
</script>