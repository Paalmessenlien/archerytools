<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Interactive Tuning & Equipment Setup</h1>
      <p class="text-gray-600 dark:text-gray-300">Professional tuning guides and equipment documentation system for optimal archery performance.</p>
    </div>

    <!-- Enhanced Guide Menu -->
    <div v-if="!showEquipmentCreator" class="space-y-6">
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

    <!-- Tuning History -->
    <div class="mt-8">
      <ArrowTuningHistoryViewer />
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