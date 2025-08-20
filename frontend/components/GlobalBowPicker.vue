<template>
  <!-- Mobile Full-Width Bow Manager Button - Sticky Position -->
  <div v-if="user" class="md:hidden sticky top-0 global-bow-picker bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-lg z-[900]">
    <div class="px-4 py-2">
      <button
        @click="toggleBowManager"
        @keydown.enter="toggleBowManager"
        @keydown.space.prevent="toggleBowManager"
        @keydown.escape="closeDropdown"
        class="w-full bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 px-4 py-3 rounded-lg font-medium mobile-nav-button flex items-center justify-between shadow-sm"
        :aria-label="showDropdown ? 'Close bow selector' : 'Open bow selector'"
        :aria-expanded="showDropdown"
        :aria-describedby="bowSetups.length > 0 ? 'bow-count' : undefined"
      >
        <div class="flex items-center space-x-2">
          <i class="fas fa-bow-arrow text-sm"></i>
          <span v-if="bowSetups.length > 0 && selectedBowSetup">{{ selectedBowSetup.name }}</span>
          <span v-else-if="bowSetups.length > 0">Select Bow</span>
          <span v-else>Add Setup</span>
          <!-- Setup Count Badge -->
          <span v-if="bowSetups.length > 0" id="bow-count" class="bg-white/20 text-xs px-2 py-1 rounded-full">
            {{ bowSetups.length }}
          </span>
        </div>
        <div class="flex items-center space-x-2">
          <!-- Loading indicator -->
          <i v-if="isLoading" class="fas fa-spinner fa-spin text-xs"></i>
          <i class="fas fa-chevron-down text-xs transition-transform duration-200" :class="{ 'rotate-180': showDropdown }"></i>
        </div>
      </button>
    </div>
    
    <!-- Dropdown Modal with Enhanced Animation -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="transform -translate-y-4 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform -translate-y-4 opacity-0"
    >
      <div v-if="showDropdown" class="absolute top-full left-0 right-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-xl max-h-[70vh] overflow-hidden modal-container z-[950]">
      <div class="p-4">
        <!-- Add New Setup Button -->
        <button
          @click="handleAddFromGlobal"
          class="w-full p-3 mb-4 bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 rounded-lg font-medium mobile-nav-button flex items-center justify-center space-x-2"
        >
          <i class="fas fa-plus text-sm"></i>
          <span>{{ bowSetups.length > 0 ? 'Add New Bow Setup' : 'Create Your First Bow Setup' }}</span>
        </button>
        
        <!-- Existing Bow Setups -->
        <div v-if="bowSetups.length > 0" class="space-y-2 max-h-60 overflow-y-auto">
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Active Bow:</h4>
          <button
            v-for="setup in bowSetups"
            :key="setup.id"
            @click="selectBowFromGlobal(setup)"
            class="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 transition-colors"
            :class="selectedBowSetup?.id === setup.id 
              ? 'bg-blue-50 border-blue-300 dark:bg-blue-950 dark:border-blue-700' 
              : 'hover:bg-gray-50 dark:hover:bg-gray-700'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <i class="fas fa-bow-arrow text-blue-600 dark:text-blue-400"></i>
                <div>
                  <div class="font-medium text-gray-900 dark:text-gray-100">{{ setup.name }}</div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    {{ setup.draw_weight }}lbs • {{ formatBowType(setup.bow_type) }}
                  </div>
                </div>
              </div>
              <div v-if="selectedBowSetup?.id === setup.id" class="w-2 h-2 bg-blue-500 rounded-full"></div>
            </div>
          </button>
        </div>
      </div>
    </div>
    </Transition>
    
    <!-- Enhanced Overlay with backdrop blur -->
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showDropdown" class="fixed inset-0 modal-overlay z-[940]" @click="closeDropdown"></div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useRouter } from 'vue-router'

const { user, fetchBowSetups } = useAuth()
const router = useRouter()

// State
const showDropdown = ref(false)
const bowSetups = ref([])
const selectedBowSetup = ref(null)
const isLoading = ref(false)

// Methods
const toggleBowManager = () => {
  if (showDropdown.value) {
    closeDropdown()
  } else {
    openDropdown()
  }
}

const openDropdown = async () => {
  // Load bow setups when opening dropdown
  if (user.value && bowSetups.value.length === 0) {
    await loadBowSetups()
  }
  showDropdown.value = true
}

const closeDropdown = () => {
  showDropdown.value = false
}

const handleAddFromGlobal = () => {
  closeDropdown()
  // Navigate to my-setup page with add query parameter
  router.push('/my-setup?add=true')
}

const selectBowFromGlobal = (setup) => {
  selectedBowSetup.value = setup
  // Store the selected setup for other components
  if (process.client) {
    localStorage.setItem('selectedBowSetup', JSON.stringify(setup))
  }
  closeDropdown()
}

const loadBowSetups = async () => {
  try {
    isLoading.value = true
    const setups = await fetchBowSetups()
    bowSetups.value = setups || []
  } catch (error) {
    console.error('Error loading bow setups:', error)
    bowSetups.value = []
  } finally {
    isLoading.value = false
  }
}

// Helper functions
const formatBowType = (type) => {
  const typeMap = {
    'compound': 'Compound',
    'recurve': 'Recurve',
    'longbow': 'Longbow',
    'traditional': 'Traditional'
  }
  return typeMap[type] || type
}

// Initialize selected bow setup from localStorage
onMounted(async () => {
  if (process.client && user.value) {
    const savedSetup = localStorage.getItem('selectedBowSetup')
    if (savedSetup) {
      try {
        selectedBowSetup.value = JSON.parse(savedSetup)
      } catch (error) {
        console.error('Error parsing saved bow setup:', error)
      }
    }
  }
})

// Watch for user changes to reload bow setups
watch(user, async (newUser) => {
  if (newUser) {
    await loadBowSetups()
    
    // Initialize selected bow setup from localStorage if available
    if (process.client) {
      const savedSetup = localStorage.getItem('selectedBowSetup')
      if (savedSetup) {
        try {
          selectedBowSetup.value = JSON.parse(savedSetup)
        } catch (error) {
          console.error('Error parsing saved bow setup:', error)
        }
      }
    }
  } else {
    // Clear data when user logs out
    bowSetups.value = []
    selectedBowSetup.value = null
  }
})

// Close dropdown when route changes
watch(() => router.currentRoute.value.path, () => {
  closeDropdown()
})
</script>

<style scoped>
/* Custom scrollbar for bow setups list */
.max-h-60::-webkit-scrollbar {
  width: 4px;
}

.max-h-60::-webkit-scrollbar-track {
  @apply bg-transparent;
}

.max-h-60::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

.max-h-60::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}
</style>