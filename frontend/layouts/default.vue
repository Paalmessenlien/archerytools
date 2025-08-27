<template>
  <div class="min-h-screen transition-colors duration-300 bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 shadow-sm dark:bg-gray-800 dark:border-gray-700 sticky top-0 sticky-header">
      <div class="px-3 mx-auto max-w-6xl sm:px-6 lg:px-6">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <!-- Logo -->
            <svg class="w-8 h-8 text-blue-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/>
              <circle cx="12" cy="12" r="6"/>
              <circle cx="12" cy="12" r="2"/>
            </svg>
            
            <div>
              <div class="flex items-center space-x-2">
                <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  <NuxtLink to="/" class="transition-colors hover:text-blue-600 dark:hover:text-purple-400">
                    ArcheryTool
                  </NuxtLink>
                </h1>
                <span class="px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 rounded-full">
                  BETA
                </span>
              </div>
              <p class="hidden text-sm text-gray-600 dark:text-gray-300 lg:block">
                Professional Archery Tools - Invitation Only
              </p>
            </div>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- Desktop Navigation -->
            <div class="items-center hidden space-x-4 md:flex">
                  <!-- Mega Menu -->
                  <div class="relative">
                    <button
                      @click="toggleDesktopMenu"
                      class="flex items-center space-x-2 px-3 py-2 text-gray-700 transition-colors hover:text-blue-600 dark:text-gray-200 dark:hover:text-purple-400 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                      <i class="fas fa-th-large"></i>
                      <span>Menu</span>
                      <i class="fas fa-chevron-down text-sm transition-transform" :class="{ 'rotate-180': desktopMenuOpen }"></i>
                    </button>
                    
                    <!-- Mega Menu Dropdown -->
                    <div v-if="desktopMenuOpen" class="absolute top-full right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 desktop-menu-dropdown">
                      <div class="p-6">
                        <div class="grid grid-cols-2 gap-4">
                          <!-- Navigation Section -->
                          <div class="space-y-3">
                            <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100 uppercase tracking-wide">Navigation</h3>
                            
                            <NuxtLink
                              :to="(isInitialized && isLoggedIn && user) ? '/my-setup' : '/'"
                              @click="closeDesktopMenu"
                              class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                              :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': ((isInitialized && isLoggedIn && user) && $route.path === '/my-setup') || ((!isInitialized || !isLoggedIn || !user) && $route.path === '/') }"
                            >
                              <i class="fas fa-home text-blue-600 dark:text-purple-400 w-5"></i>
                              <div>
                                <div class="font-medium text-gray-900 dark:text-gray-100">{{ (isInitialized && isLoggedIn && user) ? 'Dashboard' : 'Home' }}</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">{{ (isInitialized && isLoggedIn && user) ? 'My bow setups' : 'Welcome page' }}</div>
                              </div>
                            </NuxtLink>
                            
                            <NuxtLink
                              to="/database"
                              @click="closeDesktopMenu"
                              class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                              :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/database' }"
                            >
                              <i class="fas fa-database text-green-600 dark:text-green-400 w-5"></i>
                              <div>
                                <div class="font-medium text-gray-900 dark:text-gray-100">Arrow Database</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">Browse 1,100+ arrows</div>
                              </div>
                            </NuxtLink>
                            
                            
                            <NuxtLink
                              to="/journal"
                              @click="closeDesktopMenu"
                              class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                              :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/journal' }"
                            >
                              <i class="fas fa-book text-orange-600 dark:text-orange-400 w-5"></i>
                              <div>
                                <div class="font-medium text-gray-900 dark:text-gray-100">Journal</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">Document your journey</div>
                              </div>
                            </NuxtLink>
                            
                            <NuxtLink
                              to="/calculator"
                              @click="closeDesktopMenu"
                              class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                              :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/calculator' }"
                            >
                              <i class="fas fa-calculator text-purple-600 dark:text-purple-400 w-5"></i>
                              <div>
                                <div class="font-medium text-gray-900 dark:text-gray-100">Spine Calculator</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">Professional calculations</div>
                              </div>
                            </NuxtLink>
                          </div>
                          
                          <!-- Tools Section -->
                          <div class="space-y-3">
                            <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100 uppercase tracking-wide">Tuning Tools</h3>
                            
                            
                            <NuxtLink
                              to="/tuning"
                              @click="closeDesktopMenu"
                              class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                              :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/tuning' }"
                            >
                              <i class="fas fa-bullseye text-red-600 dark:text-red-400 w-5"></i>
                              <div>
                                <div class="font-medium text-gray-900 dark:text-gray-100">Interactive Tuning</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">Guided tuning sessions</div>
                              </div>
                            </NuxtLink>
                            
                            <NuxtLink
                              to="/info"
                              @click="closeDesktopMenu"
                              class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                              :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path.startsWith('/info') }"
                            >
                              <i class="fas fa-info-circle text-blue-600 dark:text-blue-400 w-5"></i>
                              <div>
                                <div class="font-medium text-gray-900 dark:text-gray-100">Information Center</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">Materials & guides</div>
                              </div>
                            </NuxtLink>
                            
                            <NuxtLink
                              v-if="user"
                              to="/my-setup"
                              @click="closeDesktopMenu"
                              class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                              :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/my-setup' }"
                            >
                              <i class="fas fa-user text-indigo-600 dark:text-indigo-400 w-5"></i>
                              <div>
                                <div class="font-medium text-gray-900 dark:text-gray-100">My Setup</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">Bow configurations</div>
                              </div>
                            </NuxtLink>
                          </div>
                        </div>
                        
                        <!-- Admin Section -->
                        <div v-if="isInitialized && isLoggedIn && user && isAdmin" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                          <NuxtLink
                            to="/admin"
                            @click="closeDesktopMenu"
                            class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-red-100 dark:hover:bg-red-900/20 text-red-700 dark:text-red-200"
                          >
                            <i class="fas fa-shield-alt text-red-600 dark:text-red-400 w-5"></i>
                            <div>
                              <div class="font-medium">Admin Panel</div>
                              <div class="text-xs text-red-500 dark:text-red-400">System administration</div>
                            </div>
                          </NuxtLink>
                          
                          <NuxtLink
                            to="/design"
                            @click="closeDesktopMenu"
                            class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                            :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/design' }"
                          >
                            <i class="fas fa-palette text-purple-600 dark:text-purple-400 w-5"></i>
                            <div>
                              <div class="font-medium">Design System</div>
                              <div class="text-xs text-purple-500 dark:text-purple-400">UI components & patterns</div>
                            </div>
                          </NuxtLink>
                        </div>
                        
                        <!-- About Section -->
                        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                          <NuxtLink
                            to="/about"
                            @click="closeDesktopMenu"
                            class="flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                            :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/about' }"
                          >
                            <i class="fas fa-info-circle text-gray-600 dark:text-gray-400 w-5"></i>
                            <div>
                              <div class="font-medium text-gray-900 dark:text-gray-100">About</div>
                              <div class="text-xs text-gray-500 dark:text-gray-400">Platform features & info</div>
                            </div>
                          </NuxtLink>
                        </div>

                        <!-- Settings Section -->
                        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                          <div class="flex items-center justify-between p-3">
                            <div class="flex items-center space-x-3">
                              <i class="fas fa-moon text-gray-600 dark:text-gray-400 w-5"></i>
                              <span class="font-medium text-gray-900 dark:text-gray-100">Dark Mode</span>
                            </div>
                            <DarkModeToggle />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- User Actions -->
                  <!-- Show placeholder during initialization to prevent hydration mismatch -->
                  <div v-if="!isInitialized" class="w-32 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
                  <CustomButton
                    v-else-if="isLoggedIn && user"
                    @click="logout"
                    variant="outlined"
                    class="text-gray-700 dark:text-gray-200"
                  >
                    Logout
                  </CustomButton>
                  <CustomButton
                    v-else
                    @click="handleLogin"
                    variant="filled"
                    class="text-white bg-blue-600 hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                  >
                    Login with Google
                  </CustomButton>
                </div>
            
            <!-- Mobile header - no navigation needed -->
          </div>
        </div>
      </div>
      
      <!-- Mobile menu removed - navigation now handled by bottom nav -->
    </header>

    <!-- Bow Setup Picker - All Screen Sizes -->
    <BowSetupPicker v-if="isInitialized && isLoggedIn && user" class="sticky top-16 bow-setup-picker sticky-element-fix" />

    <!-- Main Content -->
    <main 
      class="px-3 py-4 mx-auto max-w-6xl sm:px-6 lg:px-6"
      :class="isInitialized && isLoggedIn && user ? 'min-h-[calc(100vh-107px)]' : 'min-h-[calc(100vh-65px)]'"
    >
      <slot />
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12 mb-20 md:mb-0">
      <div class="px-3 py-8 mx-auto max-w-6xl sm:px-6 lg:px-6">
        <div class="text-center space-y-4">
          <!-- Beta Warning -->
          <div class="inline-flex items-center px-4 py-2 bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-200 rounded-lg text-sm font-medium">
            <i class="fas fa-exclamation-triangle mr-2"></i>
            <span>BETA SOFTWARE - Features may change and data may be reset</span>
          </div>
          
          <!-- Copyright and Info -->
          <div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <p>&copy; {{ new Date().getFullYear() }} ArcheryTool Beta - Professional Archery Tools</p>
            <p>Invitation-only access during beta testing phase</p>
          </div>
          
          <!-- Links -->
          <div class="flex justify-center space-x-6 text-sm">
            <NuxtLink to="/about" class="text-blue-600 dark:text-purple-400 hover:text-blue-700 dark:hover:text-purple-300 transition-colors">
              About
            </NuxtLink>
            <NuxtLink to="/info" class="text-blue-600 dark:text-purple-400 hover:text-blue-700 dark:hover:text-purple-300 transition-colors">
              Help
            </NuxtLink>
          </div>
        </div>
      </div>
    </footer>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="fixed inset-0 loading-overlay flex items-center justify-center bg-black bg-opacity-50">
      <div class="flex items-center p-6 space-x-3 bg-white dark:bg-gray-800 rounded-xl">
        <div class="w-6 h-6 border-b-2 border-blue-600 rounded-full animate-spin dark:border-purple-400"></div>
        <span class="text-gray-700 dark:text-gray-200">Loading...</span>
      </div>
    </div>
    
    <!-- Mobile Bottom Navigation -->
    <MobileBottomNav @login="handleLogin" />
    
    <!-- Global Notifications -->
    <NotificationContainer />
  </div>
</template>

<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'
import { useAuth } from '~/composables/useAuth'

const bowConfigStore = useBowConfigStore()
const isLoading = computed(() => bowConfigStore.isLoading)

const { user, logout, loginWithGoogle, fetchUser, initializeGoogleAuth, isInitialized, isLoggedIn, initializeClientAuth } = useAuth()
const router = useRouter()

// Desktop menu state
const desktopMenuOpen = ref(false)

// Check if user is admin
const isAdmin = computed(() => {
  return user.value?.email === 'messenlien@gmail.com'
})

// Desktop menu methods
const toggleDesktopMenu = () => {
  desktopMenuOpen.value = !desktopMenuOpen.value
}

const closeDesktopMenu = () => {
  desktopMenuOpen.value = false
}

// Close menu when clicking outside
const handleClickOutside = (event) => {
  if (desktopMenuOpen.value && !event.target.closest('.relative')) {
    closeDesktopMenu()
  }
}

// Close menu when route changes
watch(() => router.currentRoute.value.path, () => {
  closeDesktopMenu()
})

const handleLogin = () => {
  loginWithGoogle();
};

const redirectToLogin = () => {
  router.push('/login')
}

// Initialize auth on mount
onMounted(() => {
  initializeClientAuth()
  fetchUser()
  initializeGoogleAuth()
  
  // Add click outside listener
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Set mobile-friendly meta tags
useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' },
    { name: 'format-detection', content: 'telephone=no' },
    { name: 'mobile-web-app-capable', content: 'yes' },
    { name: 'apple-mobile-web-app-capable', content: 'yes' },
    { name: 'apple-mobile-web-app-status-bar-style', content: 'default' }
  ]
})
</script>

<style scoped>
.nav-tab {
  @apply flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 whitespace-nowrap border-none cursor-pointer bg-transparent text-gray-600 hover:bg-gray-100;
}

.nav-tab.active {
  @apply bg-blue-50 text-blue-600 font-medium;
}

.dark .nav-tab {
  @apply text-gray-300 hover:bg-gray-700;
}

.dark .nav-tab.active {
  @apply bg-purple-900/20 text-purple-400;
}
</style>