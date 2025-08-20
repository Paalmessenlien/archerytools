<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Interactive Tuning Guides</h1>
      <p class="text-gray-600 dark:text-gray-300">Advanced tuning interfaces with real-time testing and permanent history tracking.</p>
    </div>

    <!-- Guide Selection -->
    <div v-if="!currentSession" class="space-y-6">
      <!-- TuningSessionStarter replaces old guide selection -->
      <TuningSessionStarter 
        @session-started="onSessionStarted"
        @cancel="resetSelection"
      />
    </div>

    <!-- Active Session Interface - Enhanced Components -->
    <div v-if="currentSession" class="space-y-6">
      <!-- Paper Tuning Interface -->
      <PaperTuningInterface 
        v-if="currentSession.guide_type === 'paper_tuning'"
        :session-data="currentSession"
        @test-recorded="onTestRecorded"
        @cancel="exitSession"
      />
      
      <!-- Bareshaft Tuning Interface -->
      <BareshaftTuningInterface 
        v-if="currentSession.guide_type === 'bareshaft_tuning'"
        :session-data="currentSession"
        @test-recorded="onTestRecorded"
        @cancel="exitSession"
      />
      
      <!-- Walkback Tuning Interface -->
      <WalkbackTuningInterface 
        v-if="currentSession.guide_type === 'walkback_tuning'"
        :session-data="currentSession"
        @test-recorded="onTestRecorded"
        @cancel="exitSession"
      />
      
      <!-- Fallback for other guide types -->
      <div v-if="!['paper_tuning', 'bareshaft_tuning', 'walkback_tuning'].includes(currentSession.guide_type)" 
           class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
        <div class="flex items-center mb-4">
          <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 mr-3"></i>
          <h3 class="text-lg font-medium text-yellow-800 dark:text-yellow-200">
            Guide Type Not Yet Supported
          </h3>
        </div>
        <p class="text-yellow-700 dark:text-yellow-300 mb-4">
          The {{ currentSession.guide_type }} guide is not yet supported with the enhanced interface. 
          This guide will be added in a future update.
        </p>
        <button 
          @click="exitSession"
          class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
        >
          Go Back
        </button>
      </div>
    </div>

    <!-- Tuning History -->
    <div class="mt-8">
      <ArrowTuningHistoryViewer />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TuningSessionStarter from '~/components/TuningSessionStarter.vue'
import PaperTuningInterface from '~/components/PaperTuningInterface.vue'
import BareshaftTuningInterface from '~/components/BareshaftTuningInterface.vue'
import WalkbackTuningInterface from '~/components/WalkbackTuningInterface.vue'
import ArrowTuningHistoryViewer from '~/components/ArrowTuningHistoryViewer.vue'

// Set page title and meta
useHead({
  title: 'Interactive Tuning Guides',
  meta: [
    { name: 'description', content: 'Advanced tuning interfaces with real-time testing and permanent history tracking for archery equipment.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})

// Reactive data
const currentSession = ref(null)

// Methods
const onSessionStarted = (sessionData) => {
  console.log('Session started:', sessionData)
  currentSession.value = sessionData
}

const onTestRecorded = (testResult) => {
  console.log('Test recorded:', testResult)
  // Test recording is handled by the individual interface components
  // The ArrowTuningHistoryViewer will automatically refresh to show new tests
}

const exitSession = () => {
  currentSession.value = null
}

const resetSelection = () => {
  currentSession.value = null
}
</script>