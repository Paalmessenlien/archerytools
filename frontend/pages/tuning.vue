<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Interactive Tuning Guides</h1>
      <p class="text-gray-600 dark:text-gray-300">Follow step-by-step interactive guides with your bow setup and track your progress.</p>
    </div>

    <!-- Active Sessions -->
    <div v-if="activeSessions.length > 0" class="mb-6 space-y-3">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
        <i class="fas fa-play-circle mr-2"></i>
        Active Sessions ({{ activeSessions.length }})
      </h2>
      <div 
        v-for="session in activeSessions" 
        :key="session.id"
        class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i class="fas fa-play-circle text-blue-600 dark:text-blue-400 mr-3"></i>
            <div>
              <h4 class="text-sm font-medium text-blue-800 dark:text-blue-200">{{ session.guide_name }}</h4>
              <p class="text-xs text-blue-700 dark:text-blue-300 mt-1">
                {{ session.bow_name || 'Unknown bow' }} • Step {{ session.current_step || 1 }} of {{ session.total_steps }}
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-xs text-blue-600 dark:text-blue-400">
              {{ Math.round(((session.current_step || 1) / session.total_steps) * 100) }}% complete
            </span>
            <button 
              @click="resumeSession(session)"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Resume
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Guide Selection -->
    <div v-if="!currentSession" class="space-y-6">
      <!-- Available Guides -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-book-open mr-2"></i>
          Available Guides
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="guide in availableGuides" 
            :key="guide.id"
            class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-500 transition-colors cursor-pointer"
            @click="selectGuide(guide)"
          >
            <div class="flex items-center mb-3">
              <div :class="`p-2 bg-${guide.color}-100 dark:bg-${guide.color}-900/30 rounded-lg`">
                <i :class="`fas fa-${guide.icon} text-${guide.color}-600 dark:text-${guide.color}-400`"></i>
              </div>
              <div class="ml-3">
                <h3 class="font-medium text-gray-900 dark:text-gray-100">{{ guide.name }}</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ guide.difficulty }} • {{ guide.estimated_time }} min</p>
              </div>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-3">{{ guide.description }}</p>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ guide.total_steps }} steps</span>
              <span :class="`px-2 py-1 text-xs font-medium rounded-full bg-${guide.color}-100 dark:bg-${guide.color}-900/30 text-${guide.color}-700 dark:text-${guide.color}-300`">
                {{ guide.type }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Bow Setup Selection -->
      <div v-if="selectedGuide" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-archway mr-2"></i>
          Select Bow Setup
        </h2>
        <div v-if="bowSetups.length === 0" class="text-center py-8">
          <i class="fas fa-archway text-gray-400 text-4xl mb-4"></i>
          <p class="text-gray-500 dark:text-gray-400 mb-4">No bow setups found. Create one first.</p>
          <NuxtLink 
            to="/my-page"
            class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
          >
            Create Bow Setup
            <i class="fas fa-arrow-right ml-2"></i>
          </NuxtLink>
        </div>
        <div v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div 
              v-for="bowSetup in bowSetups" 
              :key="bowSetup.id"
              :class="[
                'border rounded-lg p-4 cursor-pointer transition-colors',
                selectedBowSetup?.id === bowSetup.id 
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                  : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500'
              ]"
              @click="selectedBowSetup = bowSetup"
            >
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-medium text-gray-900 dark:text-gray-100">{{ bowSetup.name }}</h3>
                <span class="text-xs text-gray-500 dark:text-gray-400">{{ formatBowType(bowSetup.bow_type) }}</span>
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">
                <p>Draw Weight: {{ bowSetup.draw_weight }}lbs</p>
                <p>Draw Length: {{ bowSetup.draw_length }}"</p>
              </div>
            </div>
          </div>
          <button 
            @click="startGuideSession"
            :disabled="!selectedBowSetup"
            class="w-full px-4 py-2 bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            Start {{ selectedGuide?.name }} with {{ selectedBowSetup?.name }}
          </button>
        </div>
      </div>
    </div>

    <!-- Active Session Interface -->
    <div v-if="currentSession" class="space-y-6">
      <GuideWalkthrough 
        :session="currentSession" 
        :guide="selectedGuide"
        @step-completed="onStepCompleted"
        @session-completed="onSessionCompleted"
        @exit-session="exitSession"
      />
    </div>

    <!-- Session History -->
    <div class="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-history mr-2"></i>
        All Sessions
      </h2>
      
      <div v-if="sessionHistory.length === 0" class="text-center py-8">
        <i class="fas fa-clock text-gray-400 text-4xl mb-4"></i>
        <p class="text-gray-500 dark:text-gray-400">No guide sessions yet. Start your first guide above!</p>
      </div>
      
      <div v-else class="space-y-6">
        <!-- Paused Sessions -->
        <div v-if="organizedSessions.paused.length > 0">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
            <i class="fas fa-pause text-yellow-500 mr-2"></i>
            Paused Sessions ({{ organizedSessions.paused.length }})
          </h3>
          <div class="space-y-2">
            <div 
              v-for="session in organizedSessions.paused" 
              :key="session.id"
              class="border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/10 rounded-lg p-3"
            >
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ session.guide_name }}</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-300">
                    {{ session.bow_name || 'No bow setup' }} • 
                    {{ session.completed_steps || 0 }}/{{ session.total_steps }} steps • 
                    {{ formatDate(session.started_at) }}
                  </p>
                </div>
                <div class="flex items-center space-x-2">
                  <button 
                    @click="resumeSession(session)"
                    class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition-colors"
                  >
                    <i class="fas fa-play mr-1"></i>
                    Resume
                  </button>
                  <button 
                    @click="viewSessionDetails(session)"
                    class="text-blue-600 dark:text-blue-400 hover:text-blue-700"
                    title="View details"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Completed Sessions -->
        <div v-if="organizedSessions.completed.length > 0">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
            <i class="fas fa-check-circle text-green-500 mr-2"></i>
            Completed Sessions ({{ organizedSessions.completed.length }})
          </h3>
          <div class="space-y-2">
            <div 
              v-for="session in organizedSessions.completed" 
              :key="session.id"
              class="border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/10 rounded-lg p-3"
            >
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ session.guide_name }}</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-300">
                    {{ session.bow_name || 'No bow setup' }} • 
                    Completed {{ formatDate(session.completed_at || session.started_at) }}
                  </p>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300">
                    ✓ Complete
                  </span>
                  <button 
                    @click="viewSessionDetails(session)"
                    class="text-blue-600 dark:text-blue-400 hover:text-blue-700"
                    title="View details"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

// Set page title and meta
useHead({
  title: 'Interactive Tuning Guides',
  meta: [
    { name: 'description', content: 'Follow interactive step-by-step tuning guides for your archery equipment with progress tracking and statistics.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})

// Reactive data
const availableGuides = ref([])
const bowSetups = ref([])
const sessionHistory = ref([])
const selectedGuide = ref(null)
const selectedBowSetup = ref(null)
const currentSession = ref(null)
const activeSessions = ref([])

// API composable
const { apiRequest } = useApi()

// Computed properties
const organizedSessions = computed(() => {
  const sessions = sessionHistory.value || []
  return {
    active: sessions.filter(s => s.status === 'in_progress'),
    completed: sessions.filter(s => s.status === 'completed'),
    paused: sessions.filter(s => s.status === 'paused'),
    other: sessions.filter(s => !['in_progress', 'completed', 'paused'].includes(s.status))
  }
})

// Methods
const loadAvailableGuides = async () => {
  try {
    const response = await apiRequest('/guides')
    availableGuides.value = response.guides
  } catch (error) {
    console.error('Error loading guides:', error)
    // Provide fallback data for development
    availableGuides.value = []
  }
}

const loadBowSetups = async () => {
  try {
    const response = await apiRequest('/bow-setups')
    // API returns bow setups directly as an array, not wrapped in bow_setups property
    bowSetups.value = Array.isArray(response) ? response : (response.bow_setups || [])
  } catch (error) {
    console.error('Error loading bow setups:', error)
    // Provide fallback data
    bowSetups.value = []
  }
}

const loadSessionHistory = async () => {
  try {
    const response = await apiRequest('/guide-sessions')
    sessionHistory.value = response.sessions || []
    
    // Get all active sessions (multiple sessions support)
    activeSessions.value = sessionHistory.value.filter(s => s.status === 'in_progress')
  } catch (error) {
    console.error('Error loading session history:', error)
    // Provide fallback data
    sessionHistory.value = []
    activeSessions.value = []
  }
}

const selectGuide = (guide) => {
  selectedGuide.value = guide
  selectedBowSetup.value = null
}

const startGuideSession = async () => {
  if (!selectedGuide.value || !selectedBowSetup.value) return
  
  try {
    const response = await apiRequest('/guide-sessions', {
      method: 'POST',
      body: JSON.stringify({
        guide_name: selectedGuide.value.name,
        guide_type: selectedGuide.value.type,
        bow_setup_id: selectedBowSetup.value.id,
        total_steps: selectedGuide.value.total_steps
      })
    })
    
    currentSession.value = {
      id: response.session_id,
      guide_name: selectedGuide.value.name,
      guide_type: selectedGuide.value.type,
      bow_setup_id: selectedBowSetup.value.id,
      total_steps: selectedGuide.value.total_steps,
      current_step: 1,
      status: 'in_progress'
    }
    
    // Clear selections
    selectedGuide.value = null
    selectedBowSetup.value = null
  } catch (error) {
    console.error('Error starting guide session:', error)
  }
}

const resumeSession = (session) => {
  if (session) {
    currentSession.value = session
    selectedGuide.value = availableGuides.value.find(g => g.name === session.guide_name)
  }
}

const onStepCompleted = (stepData) => {
  console.log('Step completed:', stepData)
  // Step tracking is handled by the GuideWalkthrough component
}

const onSessionCompleted = () => {
  currentSession.value = null
  selectedGuide.value = null
  loadSessionHistory() // Refresh history
}

const exitSession = async () => {
  // Update session status to paused on server
  if (currentSession.value) {
    try {
      await apiRequest(`/guide-sessions/${currentSession.value.id}/pause`, {
        method: 'POST'
      })
    } catch (error) {
      console.error('Error pausing session:', error)
    }
  }
  
  currentSession.value = null
  selectedGuide.value = null
  
  // Refresh session history to show updated status
  loadSessionHistory()
}

const viewSessionDetails = (session) => {
  // Navigate to detailed session view
  navigateTo(`/tuning/sessions/${session.id}`)
}

// Helper functions
const formatBowType = (bowType) => {
  return bowType.charAt(0).toUpperCase() + bowType.slice(1)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Load data on mount
onMounted(() => {
  loadAvailableGuides()
  loadBowSetups()
  loadSessionHistory()
})
</script>