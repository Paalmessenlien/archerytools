<template>
  <div class="tuning-session-card bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <div class="flex justify-between items-start mb-3">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <md-icon :class="sessionTypeIcon.class">{{ sessionTypeIcon.icon }}</md-icon>
          {{ sessionTypeTitle }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ formatDate(sessionData.created_at) }}
        </p>
      </div>
      <div class="flex items-center gap-2">
        <div v-if="qualityScore" class="flex items-center gap-1">
          <md-icon class="text-yellow-500">star</md-icon>
          <span class="text-sm font-medium">{{ qualityScore }}/100</span>
        </div>
        <md-outlined-button size="small" @click="$emit('view-session', sessionData)">
          <md-icon slot="icon">visibility</md-icon>
          View
        </md-outlined-button>
      </div>
    </div>

    <!-- Session Summary based on type -->
    <div class="space-y-3">
      <!-- Paper Tuning Session -->
      <div v-if="sessionType === 'paper'" class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-md">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <span class="text-xs font-medium text-blue-700 dark:text-blue-300">Distance</span>
            <p class="text-sm">{{ sessionData.distance || 'Not recorded' }}y</p>
          </div>
          <div>
            <span class="text-xs font-medium text-blue-700 dark:text-blue-300">Tear Pattern</span>
            <p class="text-sm">{{ formatTearPattern(sessionData.tear_pattern) }}</p>
          </div>
        </div>
        <div v-if="sessionData.recommendations" class="mt-2">
          <span class="text-xs font-medium text-blue-700 dark:text-blue-300">Recommendation</span>
          <p class="text-sm">{{ sessionData.recommendations.primary || 'No recommendation recorded' }}</p>
        </div>
      </div>

      <!-- Bareshaft Tuning Session -->
      <div v-else-if="sessionType === 'bareshaft'" class="bg-green-50 dark:bg-green-900/20 p-3 rounded-md">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <span class="text-xs font-medium text-green-700 dark:text-green-300">Distance</span>
            <p class="text-sm">{{ sessionData.distance || 'Not recorded' }}y</p>
          </div>
          <div>
            <span class="text-xs font-medium text-green-700 dark:text-green-300">Impact Pattern</span>
            <p class="text-sm">{{ formatImpactPattern(sessionData.impact_pattern) }}</p>
          </div>
        </div>
        <div v-if="sessionData.spine_adjustment" class="mt-2">
          <span class="text-xs font-medium text-green-700 dark:text-green-300">Spine Adjustment</span>
          <p class="text-sm">{{ sessionData.spine_adjustment }}</p>
        </div>
      </div>

      <!-- Walkback Tuning Session -->
      <div v-else-if="sessionType === 'walkback'" class="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-md">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <span class="text-xs font-medium text-purple-700 dark:text-purple-300">Distance Range</span>
            <p class="text-sm">{{ formatDistanceRange(sessionData.distances) }}</p>
          </div>
          <div>
            <span class="text-xs font-medium text-purple-700 dark:text-purple-300">Center Shot</span>
            <p class="text-sm">{{ sessionData.center_shot_adjustment || 'No adjustment' }}</p>
          </div>
        </div>
        <div v-if="sessionData.consistency_score" class="mt-2">
          <span class="text-xs font-medium text-purple-700 dark:text-purple-300">Consistency</span>
          <p class="text-sm">{{ sessionData.consistency_score }}%</p>
        </div>
      </div>

      <!-- General Session -->
      <div v-else class="bg-gray-50 dark:bg-gray-700/20 p-3 rounded-md">
        <div v-if="sessionData.notes" class="space-y-2">
          <span class="text-xs font-medium text-gray-700 dark:text-gray-300">Notes</span>
          <p class="text-sm line-clamp-2">{{ sessionData.notes }}</p>
        </div>
        <div v-else class="text-sm text-gray-500 dark:text-gray-400">
          General tuning session
        </div>
      </div>
    </div>

    <!-- Equipment Summary -->
    <div v-if="equipmentSummary" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
      <div class="grid grid-cols-2 gap-3 text-xs">
        <div v-if="equipmentSummary.bow">
          <span class="font-medium text-gray-700 dark:text-gray-300">Bow</span>
          <p class="text-gray-600 dark:text-gray-400 truncate">{{ equipmentSummary.bow }}</p>
        </div>
        <div v-if="equipmentSummary.arrow">
          <span class="font-medium text-gray-700 dark:text-gray-300">Arrow</span>
          <p class="text-gray-600 dark:text-gray-400 truncate">{{ equipmentSummary.arrow }}</p>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="mt-3 flex gap-2">
      <md-text-button size="small" @click="$emit('start-similar', sessionData)">
        <md-icon slot="icon">refresh</md-icon>
        Start Similar
      </md-text-button>
      <md-text-button size="small" @click="$emit('view-journal', sessionData)">
        <md-icon slot="icon">book</md-icon>
        View Journal
      </md-text-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface TuningSessionData {
  session_id?: string
  session_type?: string
  created_at?: string
  distance?: number
  tear_pattern?: any
  impact_pattern?: any
  recommendations?: any
  spine_adjustment?: string
  distances?: number[]
  center_shot_adjustment?: string
  consistency_score?: number
  notes?: string
  bow_setup?: any
  arrow_setup?: any
  session_quality_score?: number
}

interface Props {
  sessionData: TuningSessionData
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  compact: false
})

const emit = defineEmits<{
  'view-session': [data: TuningSessionData]
  'start-similar': [data: TuningSessionData]
  'view-journal': [data: TuningSessionData]
}>()

const sessionType = computed(() => {
  return props.sessionData.session_type || 'general'
})

const sessionTypeIcon = computed(() => {
  const icons = {
    paper: { icon: 'description', class: 'text-blue-600' },
    bareshaft: { icon: 'gps_fixed', class: 'text-green-600' },
    walkback: { icon: 'timeline', class: 'text-purple-600' },
    general: { icon: 'tune', class: 'text-gray-600' }
  }
  return icons[sessionType.value as keyof typeof icons] || icons.general
})

const sessionTypeTitle = computed(() => {
  const titles = {
    paper: 'Paper Tuning',
    bareshaft: 'Bareshaft Tuning', 
    walkback: 'Walkback Tuning',
    general: 'General Tuning'
  }
  return titles[sessionType.value as keyof typeof titles] || 'Tuning Session'
})

const qualityScore = computed(() => {
  return props.sessionData.session_quality_score
    ? Math.round(props.sessionData.session_quality_score)
    : null
})

const equipmentSummary = computed(() => {
  const summary: { bow?: string; arrow?: string } = {}
  
  if (props.sessionData.bow_setup) {
    summary.bow = props.sessionData.bow_setup.manufacturer 
      ? `${props.sessionData.bow_setup.manufacturer} ${props.sessionData.bow_setup.model || ''}`
      : props.sessionData.bow_setup.model || 'Unknown Bow'
  }
  
  if (props.sessionData.arrow_setup) {
    summary.arrow = props.sessionData.arrow_setup.manufacturer
      ? `${props.sessionData.arrow_setup.manufacturer} ${props.sessionData.arrow_setup.model || ''}`
      : props.sessionData.arrow_setup.model || 'Unknown Arrow'
  }
  
  return Object.keys(summary).length > 0 ? summary : null
})

function formatDate(dateStr?: string): string {
  if (!dateStr) return 'Unknown date'
  
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return 'Invalid date'
  }
}

function formatTearPattern(pattern: any): string {
  if (!pattern) return 'No pattern recorded'
  
  if (typeof pattern === 'string') return pattern
  
  if (pattern.horizontal && pattern.vertical) {
    return `${pattern.horizontal}, ${pattern.vertical}`
  }
  
  return 'Pattern recorded'
}

function formatImpactPattern(pattern: any): string {
  if (!pattern) return 'No pattern recorded'
  
  if (typeof pattern === 'string') return pattern
  
  if (pattern.direction) {
    return `${pattern.direction} impact`
  }
  
  return 'Pattern recorded'
}

function formatDistanceRange(distances: number[]): string {
  if (!distances || distances.length === 0) return 'No distances'
  
  if (distances.length === 1) return `${distances[0]}y`
  
  const min = Math.min(...distances)
  const max = Math.max(...distances)
  return `${min}-${max}y`
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>