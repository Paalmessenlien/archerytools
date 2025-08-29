<template>
  <!-- Mobile Menu Overlay -->
  <div v-if="menuOpen" class="fixed left-0 right-0 bg-black bg-opacity-50 modal-overlay transition-opacity duration-300 z-[1100]" @click="closeMenu"
       :style="{ top: '0', bottom: 'calc(56px + env(safe-area-inset-bottom))' }"></div>
  
  <!-- Mobile Menu with Enhanced UX -->
  <div v-if="menuOpen" class="fixed left-0 right-0 bg-white dark:bg-gray-800 shadow-lg transform transition-all duration-500 ease-out backdrop-blur-sm bg-white/95 dark:bg-gray-800/95 z-[1200] flex flex-col" 
       :class="menuOpen ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'"
       :style="{ top: '0', bottom: 'calc(56px + env(safe-area-inset-bottom))' }">
    <!-- Quick Actions Header -->
    <div class="absolute top-2 left-3 right-3 flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <!-- Brand/Context -->
        <div class="text-xs font-medium text-gray-500 dark:text-gray-400">
          Menu
        </div>
      </div>
      <!-- Close Button -->
      <div class="flex items-center">
        <button
          @click="closeMenu"
          class="p-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-all duration-200"
          aria-label="Close menu"
        >
          <i class="fas fa-times text-lg"></i>
        </button>
      </div>
    </div>
    
    <!-- Tap to close hint -->
    <div class="absolute top-1/3 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
      <div class="text-xs text-gray-400 dark:text-gray-500 text-center opacity-50">
        Tap anywhere to close
      </div>
    </div>
    
    <!-- Menu Content at Bottom (above toolbar) -->
    <div class="absolute bottom-0 left-0 right-0 px-3 pb-4 pt-6 bg-gradient-to-t from-white via-white/95 to-transparent dark:from-gray-800 dark:via-gray-800/95 dark:to-transparent">
      
      <!-- Primary Actions (Most Used) -->
      <div class="space-y-1 mb-4">
        <div class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-3 mb-2">
          Main Navigation
        </div>
        
        <NuxtLink 
          :to="user ? '/my-setup' : '/'" 
          @click="closeMenu"
          class="flex items-center px-4 py-4 text-base font-semibold transition-all duration-200 rounded-xl hover:scale-[1.01] active:scale-[0.98]"
          :class="{ 
            'bg-blue-500 text-white shadow-lg shadow-blue-500/25': (user && $route.path === '/my-setup') || (!user && $route.path === '/'),
            'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700': !((user && $route.path === '/my-setup') || (!user && $route.path === '/'))
          }"
        >
          <div class="w-10 h-10 rounded-xl flex items-center justify-center mr-4" :class="(user && $route.path === '/my-setup') || (!user && $route.path === '/') ? 'bg-white/20' : 'bg-blue-100 dark:bg-blue-900'">
            <i class="fas fa-home text-lg" :class="(user && $route.path === '/my-setup') || (!user && $route.path === '/') ? 'text-white' : 'text-blue-600 dark:text-blue-400'"></i>
          </div>
          <div>
            <div class="text-lg font-bold">{{ user ? 'Dashboard' : 'Home' }}</div>
            <div class="text-sm opacity-70">{{ user ? 'Your bow setups' : 'Get started' }}</div>
          </div>
        </NuxtLink>
        
        <NuxtLink 
          to="/calculator" 
          @click="closeMenu"
          class="flex items-center px-4 py-4 text-base font-semibold transition-all duration-200 rounded-xl hover:scale-[1.01] active:scale-[0.98]"
          :class="{ 
            'bg-green-500 text-white shadow-lg shadow-green-500/25': $route.path === '/calculator',
            'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700': $route.path !== '/calculator'
          }"
        >
          <div class="w-10 h-10 rounded-xl flex items-center justify-center mr-4" :class="$route.path === '/calculator' ? 'bg-white/20' : 'bg-green-100 dark:bg-green-900'">
            <i class="fas fa-calculator text-lg" :class="$route.path === '/calculator' ? 'text-white' : 'text-green-600 dark:text-green-400'"></i>
          </div>
          <div>
            <div class="text-lg font-bold">Spine Calculator</div>
            <div class="text-sm opacity-70">Find your perfect arrow</div>
          </div>
        </NuxtLink>
        
        <NuxtLink 
          to="/database" 
          @click="closeMenu"
          class="flex items-center px-4 py-4 text-base font-semibold transition-all duration-200 rounded-xl hover:scale-[1.01] active:scale-[0.98]"
          :class="{ 
            'bg-purple-500 text-white shadow-lg shadow-purple-500/25': $route.path === '/database',
            'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700': $route.path !== '/database'
          }"
        >
          <div class="w-10 h-10 rounded-xl flex items-center justify-center mr-4" :class="$route.path === '/database' ? 'bg-white/20' : 'bg-purple-100 dark:bg-purple-900'">
            <i class="fas fa-database text-lg" :class="$route.path === '/database' ? 'text-white' : 'text-purple-600 dark:text-purple-400'"></i>
          </div>
          <div>
            <div class="text-lg font-bold">Arrow Database</div>
            <div class="text-sm opacity-70">Browse arrow specs</div>
          </div>
        </NuxtLink>
      </div>
      
      <!-- Secondary Actions (Compact) -->
      <div class="space-y-1 mb-4">
        <div class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-3 mb-1">
          Tools & Guides
        </div>
        
        <NuxtLink 
          to="/tuning" 
          @click="closeMenu"
          class="flex items-center px-3 py-3 text-base font-medium transition-all duration-200 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 active:scale-[0.98]"
          :class="{ 
            'bg-orange-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400': $route.path === '/tuning',
            'text-gray-700 dark:text-gray-200': $route.path !== '/tuning'
          }"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center mr-3" :class="$route.path === '/tuning' ? 'bg-orange-100 dark:bg-orange-900' : 'bg-gray-100 dark:bg-gray-800'">
            <i class="fas fa-bullseye text-orange-500 text-sm"></i>
          </div>
          Interactive Tuning
        </NuxtLink>
        
        <NuxtLink 
          to="/journal" 
          @click="closeMenu"
          class="flex items-center px-3 py-3 text-base font-medium transition-all duration-200 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 active:scale-[0.98]"
          :class="{ 
            'bg-gray-50 text-gray-700 dark:bg-gray-700 dark:text-gray-200': $route.path === '/journal',
            'text-gray-700 dark:text-gray-200': $route.path !== '/journal'
          }"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center mr-3" :class="$route.path === '/journal' ? 'bg-gray-200 dark:bg-gray-600' : 'bg-gray-100 dark:bg-gray-800'">
            <i class="fas fa-book text-orange-500 text-sm"></i>
          </div>
          Journal
        </NuxtLink>
        
        <NuxtLink 
          to="/info" 
          @click="closeMenu"
          class="flex items-center px-3 py-3 text-base font-medium transition-all duration-200 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 active:scale-[0.98]"
          :class="{ 
            'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400': $route.path.startsWith('/info'),
            'text-gray-700 dark:text-gray-200': !$route.path.startsWith('/info')
          }"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center mr-3" :class="$route.path.startsWith('/info') ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-800'">
            <i class="fas fa-info-circle text-blue-500 text-sm"></i>
          </div>
          Information Center
        </NuxtLink>
        
        <NuxtLink 
          to="/about" 
          @click="closeMenu"
          class="flex items-center px-3 py-3 text-base font-medium transition-all duration-200 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 active:scale-[0.98]"
          :class="{ 
            'bg-gray-50 text-gray-700 dark:bg-gray-700 dark:text-gray-200': $route.path === '/about',
            'text-gray-700 dark:text-gray-200': $route.path !== '/about'
          }"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center mr-3" :class="$route.path === '/about' ? 'bg-gray-200 dark:bg-gray-600' : 'bg-gray-100 dark:bg-gray-800'">
            <i class="fas fa-question-circle text-gray-500 text-sm"></i>
          </div>
          About
        </NuxtLink>
      </div>
      
      <!-- Settings Section -->
      <div class="space-y-1 mb-4">
        <div class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-3 mb-2">
          Settings
        </div>
        
        <!-- Enhanced Dark Mode Toggle -->
        <div class="px-3">
          <button
            @click="toggleDarkMode"
            class="flex items-center justify-between w-full px-4 py-4 text-base font-medium bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-600 transition-all duration-200 active:scale-[0.98]"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center mr-3" :class="isDarkMode ? 'bg-yellow-100 dark:bg-yellow-900' : 'bg-gray-100 dark:bg-gray-800'">
                <i :class="isDarkMode ? 'fas fa-sun text-yellow-600 dark:text-yellow-400' : 'fas fa-moon text-gray-600 dark:text-gray-400'" class="text-lg"></i>
              </div>
              <div>
                <div class="text-left text-gray-900 dark:text-gray-100 font-semibold">
                  {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 text-left">
                  {{ isDarkMode ? 'Switch to light theme' : 'Switch to dark theme' }}
                </div>
              </div>
            </div>
            <div class="ml-2">
              <div class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors" :class="isDarkMode ? 'bg-blue-600' : 'bg-gray-300'">
                <span class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform" :class="isDarkMode ? 'translate-x-6' : 'translate-x-1'"></span>
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- User Actions -->
      <div v-if="user" class="space-y-1">
        <div class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-3 mb-1">
          Account
        </div>
        
        <NuxtLink
          v-if="user && isAdmin"
          to="/admin"
          @click="closeMenu"
          class="flex items-center px-3 py-3 text-base font-medium text-red-700 dark:text-red-400 transition-all duration-200 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20 active:scale-[0.98]"
        >
          <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900 flex items-center justify-center mr-3">
            <i class="fas fa-shield-alt text-red-600 dark:text-red-400 text-sm"></i>
          </div>
          Admin Panel
        </NuxtLink>
        
        <NuxtLink
          v-if="user && isAdmin"
          to="/design"
          @click="closeMenu"
          class="flex items-center px-3 py-3 text-base font-medium text-purple-700 dark:text-purple-400 transition-all duration-200 rounded-xl hover:bg-purple-50 dark:hover:bg-purple-900/20 active:scale-[0.98]"
        >
          <div class="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center mr-3">
            <i class="fas fa-palette text-purple-600 dark:text-purple-400 text-sm"></i>
          </div>
          Design System
        </NuxtLink>
        
        <button
          @click="handleLogout"
          class="flex items-center w-full px-3 py-3 text-base font-medium text-gray-600 dark:text-gray-400 transition-all duration-200 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 active:scale-[0.98]"
        >
          <div class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center mr-3">
            <i class="fas fa-sign-out-alt text-gray-600 dark:text-gray-400 text-sm"></i>
          </div>
          Logout
        </button>
      </div>
      
      <div v-else class="space-y-2">
        <button
          @click="handleLogin"
          class="flex items-center justify-center w-full px-4 py-3 text-base font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          <i class="fab fa-google mr-2 text-lg"></i>
          Sign in with Google
        </button>
      </div>
    </div>
  </div>

  <div 
    class="fixed bottom-0 left-0 right-0 mobile-bottom-nav bg-white dark:bg-gray-900 md:hidden shadow-lg border-t border-gray-200 dark:border-gray-700 transition-transform duration-300 ease-out backdrop-blur-sm bg-white/95 dark:bg-gray-900/95 z-[1000]" 
    style="padding-bottom: env(safe-area-inset-bottom);"
    :class="{ 'translate-y-full': isHidden }"
  >
    <div class="flex items-center justify-around px-3" :class="menuOpen ? 'h-18' : 'h-14 md-mobile:h-16'">
      <!-- Home/Menu -->
      <button
        @click="toggleMenu"
        class="mobile-nav-button flex flex-col items-center justify-center p-2 rounded-2xl transition-all duration-200 active:scale-95"
        :class="[
          menuOpen 
            ? 'bg-primary-100 text-primary-700 dark:bg-primary-800 dark:text-primary-200' 
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
          menuOpen ? 'w-14 h-14' : 'w-12 h-12 md-mobile:w-14 md-mobile:h-14'
        ]"
      >
        <i class="fas mb-1 transition-transform duration-200" :class="[
          menuOpen ? 'fa-times text-2xl' : 'fa-bars text-xl md-mobile:text-2xl',
          menuOpen ? 'rotate-90' : 'rotate-0'
        ]"></i>
        <span class="text-xs font-medium transition-opacity duration-200" :class="menuOpen ? 'opacity-100' : 'opacity-75'">
          {{ menuOpen ? 'Close' : 'Menu' }}
        </span>
      </button>

      <!-- My Setup / Login -->
      <NuxtLink
        v-if="user"
        to="/my-setup"
        class="mobile-nav-button flex flex-col items-center justify-center p-2 rounded-2xl transition-all duration-200 active:scale-95"
        :class="[
          $route.path === '/my-setup'
            ? 'bg-primary-100 text-primary-700 dark:bg-primary-800 dark:text-primary-200'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
          menuOpen ? 'w-14 h-14' : 'w-12 h-12 md-mobile:w-14 md-mobile:h-14'
        ]"
      >
        <i class="fas fa-user mb-1 transition-all duration-200" :class="menuOpen ? 'text-xl' : 'text-lg md-mobile:text-xl'"></i>
        <span class="text-xs font-medium transition-opacity duration-200" :class="menuOpen ? 'opacity-100' : 'opacity-75'">Setup</span>
      </NuxtLink>
      <button
        v-else
        @click="handleLogin"
        class="mobile-nav-button flex flex-col items-center justify-center p-2 rounded-2xl transition-all duration-200 active:scale-95 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
        :class="menuOpen ? 'w-16 h-16' : 'w-14 h-14 md-mobile:w-16 md-mobile:h-16'"
      >
        <i class="fas fa-sign-in-alt mb-1 transition-all duration-200" :class="menuOpen ? 'text-xl' : 'text-lg md-mobile:text-xl'"></i>
        <span class="text-xs font-medium transition-opacity duration-200" :class="menuOpen ? 'opacity-100' : 'opacity-75'">Login</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import DarkModeToggle from '~/components/DarkModeToggle.vue'

// Define emits to prevent warnings
const emit = defineEmits(['login'])

const { user, logout, loginWithGoogle } = useAuth()
const route = useRoute()
const { isAdmin } = useAuth()
const { isDarkMode, toggleDarkMode } = useDarkMode()

// Menu state
const menuOpen = ref(false)

// Auto-hide functionality
const isHidden = ref(false)
const lastScrollY = ref(0)
const scrollThreshold = 50 // Minimum scroll distance to trigger hide/show

// Scroll handling - Disabled auto-hide for better mobile UX
const handleScroll = () => {
  // Keep navigation always visible on mobile for better accessibility
  isHidden.value = false
  lastScrollY.value = window.scrollY
}

// Menu methods
const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
  // Always show navigation when menu is toggled
  if (menuOpen.value) {
    isHidden.value = false
  }
}

const closeMenu = () => {
  menuOpen.value = false
}

const handleLogin = async () => {
  try {
    emit('login')
    await loginWithGoogle()
    closeMenu()
  } catch (error) {
    console.error('Login failed:', error)
  }
}

const handleLogout = async () => {
  try {
    await logout()
    closeMenu()
  } catch (error) {
    console.error('Logout failed:', error)
  }
}


// Throttled scroll handler for better performance
let scrollTimeout = null
const throttledHandleScroll = () => {
  if (scrollTimeout) return
  scrollTimeout = setTimeout(() => {
    handleScroll()
    scrollTimeout = null
  }, 16) // ~60fps
}

// Lifecycle hooks
onMounted(() => {
  if (process.client) {
    window.addEventListener('scroll', throttledHandleScroll, { passive: true })
    lastScrollY.value = window.scrollY
  }
})

onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('scroll', throttledHandleScroll)
    if (scrollTimeout) {
      clearTimeout(scrollTimeout)
    }
  }
})

// Close menu when route changes
watch(() => route.path, () => {
  closeMenu()
})
</script>