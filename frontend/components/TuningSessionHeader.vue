<template>
  <div class="tuning-session-header bg-surface-container rounded-lg p-4 mb-6 shadow-sm">
    <!-- Session Info -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-on-surface mb-2">{{ sessionTitle }}</h1>
        <div class="flex flex-wrap items-center gap-4 text-sm text-on-surface-variant">
          <div class="flex items-center gap-2">
            <md-icon>arrow_forward</md-icon>
            <span>{{ arrowInfo }}</span>
          </div>
          <div class="flex items-center gap-2">
            <md-icon>sports</md-icon>
            <span>{{ bowSetupName }}</span>
          </div>
          <div class="flex items-center gap-2">
            <md-icon>schedule</md-icon>
            <span>{{ sessionDuration }}</span>
          </div>
        </div>
      </div>

      <!-- Session Status -->
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-2 px-3 py-1 rounded-full" :class="statusClasses">
          <div class="w-2 h-2 rounded-full" :class="statusDotClass"></div>
          <span class="text-sm font-medium">{{ sessionStatus }}</span>
        </div>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="mb-4" v-if="showProgress">
      <div class="flex items-center justify-between text-sm text-on-surface-variant mb-2">
        <span>Session Progress</span>
        <span>{{ testsCompleted }}/{{ totalTests }} tests</span>
      </div>
      <div class="w-full bg-surface-container-high rounded-full h-2">
        <div 
          class="bg-primary h-2 rounded-full transition-all duration-300"
          :style="{ width: `${progressPercentage}%` }"
        ></div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <!-- Pause/Resume Button -->
        <md-filled-tonal-button
          @click="handlePauseResume"
          :disabled="sessionStatus === 'completed' || sessionStatus === 'abandoned'"
        >
          <md-icon slot="icon">{{ isPaused ? 'play_arrow' : 'pause' }}</md-icon>
          {{ isPaused ? 'Resume' : 'Pause' }}
        </md-filled-tonal-button>

        <!-- Abandon Button -->
        <md-outlined-button
          @click="handleAbandon"
          :disabled="sessionStatus === 'completed' || sessionStatus === 'abandoned'"
        >
          <md-icon slot="icon">close</md-icon>
          Abandon
        </md-outlined-button>
      </div>

      <div class="flex items-center gap-2">
        <!-- Save & Exit Button -->
        <md-filled-button
          @click="handleSaveExit"
          :disabled="!canSave || sessionStatus === 'abandoned'"
        >
          <md-icon slot="icon">save</md-icon>
          {{ sessionStatus === 'completed' ? 'View in Journal' : 'Save & Exit' }}
        </md-filled-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  sessionId: string
  sessionType: 'paper' | 'bareshaft' | 'walkback'
  arrowInfo: string
  bowSetupName: string
  sessionStatus: 'active' | 'paused' | 'completed' | 'abandoned'
  testsCompleted?: number
  totalTests?: number
  startTime: Date
  canSave?: boolean
  showProgress?: boolean
}

interface Emits {
  (e: 'pause-resume'): void
  (e: 'abandon-session'): void
  (e: 'save-exit'): void
}

const props = withDefaults(defineProps<Props>(), {
  testsCompleted: 0,
  totalTests: 0,
  canSave: false,
  showProgress: true
})

const emit = defineEmits<Emits>()

// Computed properties
const sessionTitle = computed(() => {
  const typeNames = {
    paper: 'Paper Tuning Session',
    bareshaft: 'Bareshaft Tuning Session',
    walkback: 'Walkback Tuning Session'
  }
  return typeNames[props.sessionType]
})

const isPaused = computed(() => props.sessionStatus === 'paused')

const progressPercentage = computed(() => {
  if (props.totalTests === 0) return 0
  return Math.round((props.testsCompleted / props.totalTests) * 100)
})

const statusClasses = computed(() => {
  const baseClasses = 'border'
  switch (props.sessionStatus) {
    case 'active':
      return `${baseClasses} bg-primary-container border-primary text-on-primary-container`
    case 'paused':
      return `${baseClasses} bg-secondary-container border-secondary text-on-secondary-container`
    case 'completed':
      return `${baseClasses} bg-tertiary-container border-tertiary text-on-tertiary-container`
    case 'abandoned':
      return `${baseClasses} bg-error-container border-error text-on-error-container`
    default:
      return `${baseClasses} bg-surface-container-high border-outline-variant text-on-surface-variant`
  }
})

const statusDotClass = computed(() => {
  switch (props.sessionStatus) {
    case 'active':
      return 'bg-primary animate-pulse'
    case 'paused':
      return 'bg-secondary'
    case 'completed':
      return 'bg-tertiary'
    case 'abandoned':
      return 'bg-error'
    default:
      return 'bg-outline-variant'
  }
})

// Session duration tracking
const sessionDuration = ref('00:00')

const updateDuration = () => {
  const now = new Date()
  const diff = now.getTime() - props.startTime.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)
  sessionDuration.value = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// Update duration every second for active sessions
let durationInterval: NodeJS.Timeout | null = null

watchEffect(() => {
  if (durationInterval) {
    clearInterval(durationInterval)
    durationInterval = null
  }

  if (props.sessionStatus === 'active') {
    updateDuration()
    durationInterval = setInterval(updateDuration, 1000)
  } else {
    updateDuration()
  }
})

onUnmounted(() => {
  if (durationInterval) {
    clearInterval(durationInterval)
  }
})

// Event handlers
const handlePauseResume = () => {
  emit('pause-resume')
}

const handleAbandon = () => {
  emit('abandon-session')
}

const handleSaveExit = () => {
  emit('save-exit')
}
</script>

<style scoped>
.tuning-session-header {
  border: 1px solid rgb(var(--md-sys-color-outline-variant));
}

@media (max-width: 640px) {
  .tuning-session-header {
    padding: 1rem;
  }
  
  .tuning-session-header h1 {
    font-size: 1.25rem;
  }
}
</style>