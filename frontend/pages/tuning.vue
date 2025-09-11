<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Interactive Tuning & Equipment Setup</h1>
      <p class="text-gray-600 dark:text-gray-300">Professional tuning guides and equipment documentation system for optimal archery performance.</p>
    </div>

    <!-- Enhanced Guide Menu -->
    <div v-if="!showEquipmentCreator" class="space-y-6">
      <!-- Header with History Button -->
      <div class="flex items-center justify-between">
        <div></div> <!-- Empty div for spacing -->
        <button 
          @click="showTuningHistory = true"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition-colors flex items-center"
        >
          <i class="fas fa-history mr-2"></i>
          View Tuning History
        </button>
      </div>
      
      <TuningGuideMenu 
        @session-started="onSessionStarted"
        @equipment-setup-requested="onEquipmentSetupRequested"
        @cancel="resetSelection"
      />
    </div>

    <!-- Equipment Tuning Creator Modal -->
    <EquipmentTuningCreator
      v-if="showEquipmentCreator"
      :bow-setup="equipmentSetupData.bow_setup"
      :equipment-category="equipmentSetupData.equipment_category"
      @entry-created="onEquipmentEntryCreated"
      @cancel="closeEquipmentCreator"
    />

    <!-- Success Notification -->
    <div v-if="showSuccessNotification" class="fixed top-4 right-4 z-50">
      <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 shadow-lg max-w-md">
        <div class="flex items-center">
          <i class="fas fa-check-circle text-green-600 dark:text-green-400 mr-3"></i>
          <div>
            <h4 class="text-sm font-medium text-green-800 dark:text-green-200">
              {{ successNotification.title }}
            </h4>
            <p class="text-xs text-green-700 dark:text-green-300 mt-1">
              {{ successNotification.message }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tuning History Modal -->
    <div 
      v-if="showTuningHistory" 
      class="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4"
      @click="showTuningHistory = false"
    >
      <div 
        @click.stop
        class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-6xl max-h-[90vh] w-full overflow-hidden"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">
            Tuning History
          </h2>
          <button 
            @click="showTuningHistory = false"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <!-- Modal Content -->
        <div class="overflow-y-auto" style="max-height: calc(90vh - 120px);">
          <ArrowTuningHistoryViewer @close="showTuningHistory = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TuningGuideMenu from '~/components/TuningGuideMenu.vue'
import EquipmentTuningCreator from '~/components/EquipmentTuningCreator.vue'
import ArrowTuningHistoryViewer from '~/components/ArrowTuningHistoryViewer.vue'

// Set page title and meta
useHead({
  title: 'Interactive Tuning & Equipment Setup',
  meta: [
    { name: 'description', content: 'Professional tuning guides and equipment documentation system for optimal archery performance.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})

// Reactive data
const showEquipmentCreator = ref(false)
const showTuningHistory = ref(false)
const equipmentSetupData = ref({})
const showSuccessNotification = ref(false)
const successNotification = ref({
  title: '',
  message: ''
})

// Methods
const onSessionStarted = (sessionData) => {
  console.log('Arrow tuning session started:', sessionData)
  // Redirect to the new tuning session URLs based on guide type
  const router = useRouter()
  
  if (sessionData.guide_type === 'paper_tuning') {
    router.push(`/tuning-session/paper/${sessionData.session_id}`)
  } else if (sessionData.guide_type === 'bareshaft_tuning') {
    router.push(`/tuning-session/bareshaft/${sessionData.session_id}`)
  } else if (sessionData.guide_type === 'walkback_tuning') {
    router.push(`/tuning-session/walkback/${sessionData.session_id}`)
  } else {
    console.error('Unknown guide type:', sessionData.guide_type)
  }
}

const onEquipmentSetupRequested = (setupData) => {
  console.log('Equipment setup requested:', setupData)
  equipmentSetupData.value = setupData
  showEquipmentCreator.value = true
}

const onEquipmentEntryCreated = (entryData) => {
  console.log('Equipment entry created:', entryData)
  
  // Show success notification
  successNotification.value = {
    title: 'Equipment Setup Documented',
    message: `${entryData.equipment_category.label} setup entry created successfully`
  }
  showSuccessNotification.value = true
  
  // Hide notification after 4 seconds
  setTimeout(() => {
    showSuccessNotification.value = false
  }, 4000)
  
  // Close the equipment creator
  closeEquipmentCreator()
}

const closeEquipmentCreator = () => {
  showEquipmentCreator.value = false
  equipmentSetupData.value = {}
}

const resetSelection = () => {
  closeEquipmentCreator()
}
</script>