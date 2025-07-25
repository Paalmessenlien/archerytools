<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 dark:bg-gray-800 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <!-- Logo -->
            <svg class="w-8 h-8 text-blue-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/>
              <circle cx="12" cy="12" r="6"/>
              <circle cx="12" cy="12" r="2"/>
            </svg>
            
            <div>
              <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
                <NuxtLink to="/" class="hover:text-blue-600 dark:hover:text-purple-400 transition-colors">
                  ArrowTune
                </NuxtLink>
              </h1>
              <p class="text-sm text-gray-600 dark:text-gray-300 hidden sm:block">
                Professional Arrow Selection
              </p>
            </div>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- Dark Mode Toggle (Desktop) -->
            <div class="hidden md:block">
              <DarkModeToggle />
            </div>
            
            <!-- Mobile menu button -->
            <button 
              @click="toggleMobileMenu"
              class="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
            >
              <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              </svg>
              <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Mobile menu -->
      <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700">
        <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <NuxtLink 
            to="/" 
            @click="closeMobileMenu"
            class="block px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            Bow Setup
          </NuxtLink>
          <NuxtLink 
            to="/database" 
            @click="closeMobileMenu"
            class="block px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            Database
          </NuxtLink>
          
          <!-- Dark Mode Toggle (Mobile) -->
          <div class="px-3 py-2">
            <DarkModeToggle />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex flex-col lg:flex-row gap-6">
        <!-- Sidebar Navigation -->
        <aside class="lg:w-64 flex-shrink-0">
          <nav class="card">
            <div class="flex lg:flex-col gap-2 overflow-x-auto lg:overflow-x-visible">
              <NuxtLink 
                to="/"
                class="nav-tab"
                :class="{ active: $route.path === '/' }"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 1v6m0 6v6"/>
                  <path d="m15.14 8.86 4.24-4.24"/>
                  <path d="m4.86 19.14 4.24-4.24"/>
                  <path d="m8.86 8.86-4.24-4.24"/>
                  <path d="m19.14 19.14-4.24-4.24"/>
                </svg>
                <span class="hidden sm:block">Bow Setup</span>
              </NuxtLink>
              
              
              <NuxtLink 
                to="/database"
                class="nav-tab"
                :class="{ active: $route.path === '/database' }"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="m21 21-4.35-4.35"/>
                </svg>
                <span class="hidden sm:block">Database</span>
              </NuxtLink>
            </div>
          </nav>
        </aside>

        <!-- Page Content -->
        <div class="flex-1 min-w-0">
          <slot />
        </div>
      </div>
    </main>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 dark:border-purple-400"></div>
        <span class="text-gray-700 dark:text-gray-200">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'

const bowConfigStore = useBowConfigStore()
const isLoading = computed(() => bowConfigStore.isLoading)

// Dark mode
const { initializeTheme } = useDarkMode()

// Mobile menu state
const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

// Close mobile menu on route change
const route = useRoute()
watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

// Close mobile menu on escape key and initialize theme
onMounted(() => {
  // Initialize dark mode theme
  initializeTheme()
  
  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      mobileMenuOpen.value = false
    }
  }
  
  document.addEventListener('keydown', handleEscape)
  
  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
  })
})
</script>