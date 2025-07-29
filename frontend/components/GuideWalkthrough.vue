<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Session Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ guide?.name }}</h2>
        <p class="text-gray-600 dark:text-gray-300">{{ guide?.description }}</p>
      </div>
      <button 
        @click="$emit('exit-session')"
        class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
      >
        Exit Session
      </button>
    </div>

    <!-- Progress Bar -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
          Step {{ currentStep }} of {{ session.total_steps }}
        </span>
        <span class="text-sm text-gray-500 dark:text-gray-400">
          {{ Math.round((currentStep / session.total_steps) * 100) }}% Complete
        </span>
      </div>
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div 
          class="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
          :style="{ width: `${(currentStep / session.total_steps) * 100}%` }"
        ></div>
      </div>
    </div>

    <!-- Step Content -->
    <div class="space-y-6">
      <!-- Current Step Display -->
      <div class="border border-blue-200 dark:border-blue-800 rounded-lg p-6 bg-blue-50 dark:bg-blue-900/20">
        <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
          {{ currentStepData.title }}
        </h3>
        <div class="prose dark:prose-invert max-w-none">
          <div v-html="currentStepData.content"></div>
        </div>
        
        <!-- Step Image (if available) -->
        <div v-if="currentStepData.image" class="mt-4">
          <img 
            :src="currentStepData.image" 
            :alt="currentStepData.title"
            class="rounded-lg max-w-full h-auto"
          />
        </div>
      </div>

      <!-- Step Input Form -->
      <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6">
        <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Record Your Results</h4>
        
        <!-- Result Type Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Result Type
          </label>
          <select 
            v-model="stepResult.result_type"
            class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="">Select result type...</option>
            <option value="measurement">Measurement</option>
            <option value="observation">Observation</option>
            <option value="adjustment">Adjustment Made</option>
            <option value="test_result">Test Result</option>
          </select>
        </div>

        <!-- Result Value -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Result/Observation
          </label>
          <textarea 
            v-model="stepResult.result_value"
            placeholder="Describe what you observed or measured..."
            class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            rows="3"
          ></textarea>
        </div>

        <!-- Measurements -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Specific Measurements (optional)
          </label>
          <input 
            v-model="stepResult.measurements"
            placeholder="e.g., 2 inches left, 1/8 inch gap"
            class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          />
        </div>

        <!-- Adjustments Made -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Adjustments Made (optional)
          </label>
          <textarea 
            v-model="stepResult.adjustments_made"
            placeholder="Describe any adjustments you made..."
            class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            rows="2"
          ></textarea>
        </div>

        <!-- Notes -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Additional Notes (optional)
          </label>
          <textarea 
            v-model="stepResult.notes"
            placeholder="Any additional observations or notes..."
            class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            rows="2"
          ></textarea>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-between">
          <button 
            v-if="currentStep > 1"
            @click="previousStep"
            class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            Previous Step
          </button>
          <div v-else></div>
          
          <div class="space-x-3">
            <button 
              @click="skipStep"
              class="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white font-medium rounded-lg transition-colors"
            >
              Skip Step
            </button>
            <button 
              @click="completeStep"
              :disabled="!stepResult.result_type"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
            >
              {{ currentStep === session.total_steps ? 'Complete Guide' : 'Next Step' }}
              <i class="fas fa-arrow-right ml-2"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useApi } from '~/composables/useApi'

// Props
const props = defineProps({
  session: {
    type: Object,
    required: true
  },
  guide: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['step-completed', 'session-completed', 'exit-session'])

// Reactive data
const currentStep = ref(props.session.current_step || 1)
const stepResult = ref({
  result_type: '',
  result_value: '',
  measurements: '',
  adjustments_made: '',
  notes: ''
})

// API composable
const { $fetch } = useApi()

// Guide step data (this would normally come from a guide definition)
const guideSteps = {
  'Paper Tuning Guide': [
    {
      title: 'Setup Paper Frame',
      content: `
        <p>Set up a paper frame 6-8 feet in front of your target. The paper should be large enough to capture arrow holes clearly.</p>
        <ul>
          <li>Use newspaper or wrapping paper</li>
          <li>Ensure the paper is taut and secure</li>
          <li>Position at shoulder height</li>
          <li>Stand 6-8 feet away from the paper</li>
        </ul>
      `
    },
    {
      title: 'Initial Shot Assessment',
      content: `
        <p>Take your first shot through the paper with a properly spined arrow. Observe the tear pattern.</p>
        <ul>
          <li>Use proper shooting form</li>
          <li>Shoot at close range (6-8 feet)</li>
          <li>Look for the arrow hole pattern</li>
          <li>Note the direction and size of any tears</li>
        </ul>
      `
    },
    {
      title: 'Analyze Tear Pattern',
      content: `
        <p>Examine the paper tear to determine what adjustments are needed:</p>
        <ul>
          <li><strong>Perfect hole:</strong> Round hole with no significant tears</li>
          <li><strong>High tear:</strong> Arrow is entering nock-end high</li>
          <li><strong>Low tear:</strong> Arrow is entering nock-end low</li>
          <li><strong>Left tear:</strong> Arrow is entering nock-end left</li>
          <li><strong>Right tear:</strong> Arrow is entering nock-end right</li>
        </ul>
      `
    },
    {
      title: 'Vertical Adjustments',
      content: `
        <p>If you have vertical tears (high or low), adjust your nocking point:</p>
        <ul>
          <li><strong>High tear:</strong> Move nocking point down slightly</li>
          <li><strong>Low tear:</strong> Move nocking point up slightly</li>
          <li>Make small adjustments (1/16" at a time)</li>
          <li>Re-test after each adjustment</li>
        </ul>
      `
    },
    {
      title: 'Horizontal Adjustments',
      content: `
        <p>If you have horizontal tears (left or right), adjust your arrow rest:</p>
        <ul>
          <li><strong>Left tear (RH shooter):</strong> Move rest slightly right</li>
          <li><strong>Right tear (RH shooter):</strong> Move rest slightly left</li>
          <li>Make micro-adjustments</li>
          <li>Consider spine if large adjustments are needed</li>
        </ul>
      `
    },
    {
      title: 'Fine Tuning',
      content: `
        <p>Continue making small adjustments until you achieve a clean bullet hole:</p>
        <ul>
          <li>Test after each adjustment</li>
          <li>Work on one plane at a time (vertical then horizontal)</li>
          <li>Be patient - small changes make big differences</li>
          <li>Consider arrow spine if tuning becomes difficult</li>
        </ul>
      `
    },
    {
      title: 'Final Verification',
      content: `
        <p>Shoot multiple arrows to verify consistent paper tuning:</p>
        <ul>
          <li>Shoot 3-5 arrows through fresh paper</li>
          <li>Ensure consistency across all shots</li>
          <li>Make final micro-adjustments if needed</li>
          <li>Record your final settings for future reference</li>
        </ul>
      `
    },
    {
      title: 'Distance Testing',
      content: `
        <p>Test your tuning at longer distances to confirm accuracy:</p>
        <ul>
          <li>Move back to 20-30 yards</li>
          <li>Shoot groups to verify accuracy</li>
          <li>Fine-tune sight if necessary</li>
          <li>Document your final setup</li>
        </ul>
      `
    }
  ],
  'Rest Adjustment': [
    {
      title: 'Initial Rest Position',
      content: `
        <p>Set your arrow rest to the basic starting position:</p>
        <ul>
          <li>Position arrow shaft level with bow grip</li>
          <li>Center shot should be 13/16" from riser centerline</li>
          <li>Ensure arrow sits securely on rest</li>
          <li>Check for proper clearance</li>
        </ul>
      `
    },
    {
      title: 'Horizontal Alignment',
      content: `
        <p>Adjust the horizontal position of your rest:</p>
        <ul>
          <li>Use a square or alignment tool</li>
          <li>Ensure arrow is perpendicular to string</li>
          <li>Make small adjustments (1/32" at a time)</li>
          <li>Test with practice shots</li>
        </ul>
      `
    },
    {
      title: 'Vertical Alignment',
      content: `
        <p>Set the proper vertical position:</p>
        <ul>
          <li>Arrow should be level with bow grip</li>
          <li>Use a bow square for accuracy</li>
          <li>Ensure consistent nock height</li>
          <li>Verify with multiple arrows</li>
        </ul>
      `
    },
    {
      title: 'Clearance Check',
      content: `
        <p>Verify arrow clearance through the shot cycle:</p>
        <ul>
          <li>Use powder spray or lipstick test</li>
          <li>Check fletching clearance</li>
          <li>Look for contact marks</li>
          <li>Adjust if necessary</li>
        </ul>
      `
    },
    {
      title: 'Fine Tuning',
      content: `
        <p>Make final adjustments for optimal performance:</p>
        <ul>
          <li>Test different arrow spine if needed</li>
          <li>Micro-adjust for best groups</li>
          <li>Verify consistency</li>
          <li>Lock down all adjustments</li>
        </ul>
      `
    },
    {
      title: 'Final Testing',
      content: `
        <p>Conduct final testing to confirm setup:</p>
        <ul>
          <li>Shoot multiple arrow groups</li>
          <li>Test at various distances</li>
          <li>Document final settings</li>
          <li>Record performance notes</li>
        </ul>
      `
    }
  ],
  'Sight Setup & Tuning': [
    {
      title: 'Mount Sight',
      content: `
        <p>Properly mount your bow sight to the riser:</p>
        <ul>
          <li>Use appropriate mounting hardware</li>
          <li>Ensure sight is square to riser</li>
          <li>Tighten to manufacturer specifications</li>
          <li>Check for solid mounting</li>
        </ul>
      `
    },
    {
      title: 'Initial Pin Setup',
      content: `
        <p>Set up your sight pins for different distances:</p>
        <ul>
          <li>Start with 20-yard pin</li>
          <li>Use bright, easy-to-see pins</li>
          <li>Ensure pins don't obstruct each other</li>
          <li>Set initial windage center</li>
        </ul>
      `
    },
    {
      title: '20 Yard Calibration',
      content: `
        <p>Sight in your first pin at 20 yards:</p>
        <ul>
          <li>Shoot groups of 3-5 arrows</li>
          <li>Adjust pin to point of impact</li>
          <li>Move pin toward arrow groups</li>
          <li>Refine until consistently on target</li>
        </ul>
      `
    },
    {
      title: 'Additional Distance Pins',
      content: `
        <p>Set up pins for other distances:</p>
        <ul>
          <li>Add 30, 40, 50+ yard pins as needed</li>
          <li>Use consistent shooting form</li>
          <li>Allow for arrow drop at distance</li>
          <li>Test each pin thoroughly</li>
        </ul>
      `
    },
    {
      title: 'Windage Adjustment',
      content: `
        <p>Fine-tune left/right adjustments:</p>
        <ul>
          <li>Shoot groups to check windage</li>
          <li>Adjust entire sight housing if needed</li>
          <li>Maintain consistent form</li>
          <li>Verify at multiple distances</li>
        </ul>
      `
    },
    {
      title: 'Sight Tape/Marks',
      content: `
        <p>Add sight tape or distance markers:</p>
        <ul>
          <li>Use sight tape for precise yardage</li>
          <li>Mark common hunting distances</li>
          <li>Test accuracy of markings</li>
          <li>Practice with marked distances</li>
        </ul>
      `
    },
    {
      title: 'Final Verification',
      content: `
        <p>Conduct final testing and verification:</p>
        <ul>
          <li>Test all pins at their distances</li>
          <li>Shoot in various conditions</li>
          <li>Make final micro-adjustments</li>
          <li>Document your sight settings</li>
        </ul>
      `
    }
  ]
}

// Computed properties
const currentStepData = computed(() => {
  const steps = guideSteps[props.guide.name] || []
  const stepIndex = currentStep.value - 1
  return steps[stepIndex] || { title: 'Step Not Found', content: 'Step content not available.' }
})

// Watch for session changes
watch(() => props.session, (newSession) => {
  if (newSession) {
    currentStep.value = newSession.current_step || 1
  }
}, { immediate: true })

// Methods
const completeStep = async () => {
  try {
    await recordStepResult()
    
    if (currentStep.value >= props.session.total_steps) {
      // Complete the entire session
      await completeSession()
    } else {
      // Move to next step
      currentStep.value++
      resetStepResult()
    }
  } catch (error) {
    console.error('Error completing step:', error)
  }
}

const recordStepResult = async () => {
  try {
    await $fetch(`/api/guide-sessions/${props.session.id}/steps`, {
      method: 'POST',
      body: {
        step_number: currentStep.value,
        step_name: currentStepData.value.title,
        ...stepResult.value
      }
    })
    
    emit('step-completed', {
      step_number: currentStep.value,
      ...stepResult.value
    })
  } catch (error) {
    console.error('Error recording step result:', error)
    throw error
  }
}

const completeSession = async () => {
  try {
    await $fetch(`/api/guide-sessions/${props.session.id}/complete`, {
      method: 'POST',
      body: {
        notes: `Completed ${props.guide.name} with ${props.session.total_steps} steps`
      }
    })
    
    emit('session-completed')
  } catch (error) {
    console.error('Error completing session:', error)
    throw error
  }
}

const skipStep = async () => {
  stepResult.value = {
    result_type: 'skipped',
    result_value: 'Step was skipped',
    measurements: '',
    adjustments_made: '',
    notes: 'User chose to skip this step'
  }
  
  await completeStep()
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    resetStepResult()
  }
}

const resetStepResult = () => {
  stepResult.value = {
    result_type: '',
    result_value: '',
    measurements: '',
    adjustments_made: '',
    notes: ''
  }
}
</script>