<template>
  <div class="min-h-screen transition-colors duration-300 bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 shadow-sm dark:bg-gray-800 dark:border-gray-700">
      <div class="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
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
              <p class="hidden text-sm text-gray-600 dark:text-gray-300 sm:block">
                Professional Archery Tools - Invitation Only
              </p>
            </div>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- Dark Mode Toggle (Desktop) -->
            <div class="items-center hidden space-x-4 md:flex">
                  <NuxtLink
                    v-if="user"
                    to="/my-page"
                    class="text-gray-700 transition-colors hover:text-blue-600 dark:text-gray-200 dark:hover:text-purple-400"
                  >
                    My Setup
                  </NuxtLink>
                  <CustomButton
                    v-if="user"
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
                  <DarkModeToggle />
                </div>
            
            <!-- Mobile menu button -->
            <button 
              @click="toggleMobileMenu"
              class="p-2 text-gray-600 transition-colors rounded-lg md:hidden hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
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
      <div v-if="mobileMenuOpen" class="bg-white border-t border-gray-200 md:hidden dark:bg-gray-800 dark:border-gray-700">
        <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <NuxtLink 
            to="/" 
            @click="closeMobileMenu"
            class="block px-3 py-2 text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            Home
          </NuxtLink>
          <NuxtLink 
            to="/database" 
            @click="closeMobileMenu"
            class="block px-3 py-2 text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            Arrows
          </NuxtLink>
          <NuxtLink 
            to="/components" 
            @click="closeMobileMenu"
            class="block px-3 py-2 text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            Components
          </NuxtLink>
          <NuxtLink 
            to="/guides" 
            @click="closeMobileMenu"
            class="block px-3 py-2 text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            Guides
          </NuxtLink>
          <NuxtLink 
            to="/tuning" 
            @click="closeMobileMenu"
            class="block px-3 py-2 text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            Interactive Tuning
          </NuxtLink>
          
          <NuxtLink
            v-if="user"
            to="/my-page"
            @click="closeMobileMenu"
            class="block px-3 py-2 text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            My Setup
          </NuxtLink>
          <NuxtLink
            v-if="user && isAdmin"
            to="/admin"
            @click="closeMobileMenu"
            class="block px-3 py-2 text-red-700 transition-colors rounded-lg hover:bg-red-100 dark:text-red-200 dark:hover:bg-red-900/20"
          >
            <i class="fas fa-shield-alt mr-2"></i>
            Admin Panel
          </NuxtLink>
          <div class="px-3 py-2">
            <CustomButton
              v-if="user"
              @click="logout"
              variant="outlined"
              class="w-full text-gray-700 dark:text-gray-200"
            >
              Logout
            </CustomButton>
            <CustomButton
              v-else
              @click="loginWithGoogle"
              variant="filled"
              class="w-full text-white bg-blue-600 hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
            >
              Login with Google
            </CustomButton>
          </div>
          <!-- Dark Mode Toggle (Mobile) -->
          <div class="px-3 py-2">
            <DarkModeToggle />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="px-4 py-6 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div class="flex flex-col gap-6 lg:flex-row">
        <!-- Sidebar Navigation -->
        <aside class="flex-shrink-0 lg:w-64">
          <nav class="card">
            <div class="flex gap-2 overflow-x-auto lg:flex-col lg:overflow-x-visible">
              <!-- Home - Always accessible for logged-in users -->
              <template v-if="user">
                <NuxtLink 
                  to="/"
                  class="nav-tab"
                  :class="{ active: $route.path === '/' }"
                >
                  <svg class="flex-shrink-0 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                  </svg>
                  <span class="hidden sm:block">Home</span>
                </NuxtLink>
                
                <NuxtLink
                  to="/database"
                  class="nav-tab"
                  :class="{ active: $route.path === '/database' }"
                >
                  <svg class="flex-shrink-0 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M8 17l4 4 4-4m-4-5v9"/>
                    <path d="M16 12l-4-4-4 4"/>
                    <path d="M12 1v3"/>
                  </svg>
                  <span class="hidden sm:block">Arrows</span>
                </NuxtLink>
                
                <NuxtLink
                  to="/components"
                  class="nav-tab"
                  :class="{ active: $route.path === '/components' }"
                >
                  <svg class="flex-shrink-0 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <rect x="3" y="3" width="7" height="7"/>
                    <rect x="14" y="3" width="7" height="7"/>
                    <rect x="14" y="14" width="7" height="7"/>
                    <rect x="3" y="14" width="7" height="7"/>
                  </svg>
                  <span class="hidden sm:block">Components</span>
                </NuxtLink>

                <NuxtLink
                  to="/guides"
                  class="nav-tab"
                  :class="{ active: $route.path.startsWith('/guides') }"
                >
                  <svg class="flex-shrink-0 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                  </svg>
                  <span class="hidden sm:block">Guides</span>
                </NuxtLink>

                <NuxtLink
                  to="/tuning"
                  class="nav-tab"
                  :class="{ active: $route.path.startsWith('/tuning') }"
                >
                  <svg class="flex-shrink-0 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  <span class="hidden sm:block">Tuning</span>
                </NuxtLink>

                <NuxtLink
                  to="/my-page"
                  class="nav-tab"
                  :class="{ active: $route.path === '/my-page' }"
                >
                  <svg class="flex-shrink-0 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span class="hidden sm:block">My Setup</span>
                </NuxtLink>

                <NuxtLink
                  v-if="isAdmin"
                  to="/admin"
                  class="nav-tab"
                  :class="{ active: $route.path === '/admin' }"
                >
                  <i class="fas fa-shield-alt flex-shrink-0 w-5 h-5 text-red-600 dark:text-red-400"></i>
                  <span class="hidden sm:block">Admin</span>
                </NuxtLink>
              </template>
              
              <!-- Locked Navigation for Non-authenticated Users -->
              <template v-else>
                <div 
                  @click="redirectToLogin"
                  class="nav-tab cursor-not-allowed opacity-60"
                  title="Login required to access full features"
                >
                  <i class="fas fa-lock flex-shrink-0 w-5 h-5 text-gray-500 dark:text-gray-400"></i>
                  <span class="hidden sm:block">Home</span>
                  <i class="fas fa-lock text-xs text-gray-400 ml-auto"></i>
                </div>
                
                <div 
                  @click="redirectToLogin"
                  class="nav-tab cursor-not-allowed opacity-60"
                  title="Login required to access Arrow Database"
                >
                  <i class="fas fa-lock flex-shrink-0 w-5 h-5 text-gray-500 dark:text-gray-400"></i>
                  <span class="hidden sm:block">Arrows</span>
                  <i class="fas fa-lock text-xs text-gray-400 ml-auto"></i>
                </div>
                
                <div 
                  @click="redirectToLogin"
                  class="nav-tab cursor-not-allowed opacity-60"
                  title="Login required to access Components"
                >
                  <i class="fas fa-lock flex-shrink-0 w-5 h-5 text-gray-500 dark:text-gray-400"></i>
                  <span class="hidden sm:block">Components</span>
                  <i class="fas fa-lock text-xs text-gray-400 ml-auto"></i>
                </div>
              </template>
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
    <div v-if="isLoading" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="flex items-center p-6 space-x-3 bg-white dark:bg-gray-800 rounded-xl">
        <div class="w-6 h-6 border-b-2 border-blue-600 rounded-full animate-spin dark:border-purple-400"></div>
        <span class="text-gray-700 dark:text-gray-200">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'
import { useAuth } from '~/composables/useAuth'

const bowConfigStore = useBowConfigStore()
const isLoading = computed(() => bowConfigStore.isLoading)

const { user, logout, loginWithGoogle, fetchUser, initializeGoogleAuth } = useAuth()
const router = useRouter()

// Check if user is admin
const isAdmin = computed(() => {
  return user.value?.email === 'messenlien@gmail.com'
})

const handleLogin = () => {
  loginWithGoogle();
};

const redirectToLogin = () => {
  router.push('/login')
}

// Fetch user on mount if token exists
onMounted(() => {
  initializeGoogleAuth();
  fetchUser();
});

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