<template>
  <!-- Mobile Menu Overlay -->
  <div v-if="menuOpen" class="fixed inset-0 bg-black bg-opacity-50 modal-overlay transition-opacity duration-300 z-[1100]" @click="closeMenu"></div>
  
  <!-- Mobile Menu with Enhanced UX -->
  <div v-if="menuOpen" class="fixed inset-0 bg-white dark:bg-gray-800 shadow-lg transform transition-all duration-500 ease-out backdrop-blur-sm bg-white/95 dark:bg-gray-800/95 z-[1200] flex flex-col" :class="menuOpen ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'">
    <!-- Quick Actions Header -->
    <div class="absolute top-4 left-4 right-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <!-- Brand/Context -->
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400">
          ArcheryTool Menu
        </div>
      </div>
      <!-- Enhanced Close Options -->
      <div class="flex items-center space-x-2">
        <DarkModeToggle />
        <button
          @click="closeMenu"
          class="p-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-all duration-200 hover:scale-105"
          aria-label="Close menu"
        >
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>
    </div>
    
    <!-- Tap to close hint -->
    <div class="absolute top-1/3 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
      <div class="text-xs text-gray-400 dark:text-gray-500 text-center opacity-50">
        Tap anywhere to close
      </div>
    </div>
    
    <!-- Spacer to push content to bottom -->
    <div class="flex-grow"></div>
    
    <!-- Menu Content at Very Bottom -->
    <div class="px-4 pb-4 pt-6 bg-gradient-to-t from-white via-white to-transparent dark:from-gray-800 dark:via-gray-800 dark:to-transparent" style="padding-bottom: calc(env(safe-area-inset-bottom) + 100px);">
      
      <!-- Primary Actions (Most Used) -->
      <div class="space-y-2 mb-6">
        <div class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-4 mb-3">
          Main Navigation
        </div>
        
        <NuxtLink 
          :to="user ? '/my-setup' : '/'" 
          @click="closeMenu"
          class="flex items-center px-5 py-4 text-lg font-semibold transition-all duration-200 rounded-2xl hover:scale-[1.02] active:scale-[0.98]"
          :class="{ 
            'bg-blue-500 text-white shadow-lg shadow-blue-500/25': (user && $route.path === '/my-setup') || (!user && $route.path === '/'),
            'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700': !((user && $route.path === '/my-setup') || (!user && $route.path === '/'))
          }"
        >
          <div class="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900 flex items-center justify-center mr-4">
            <i class="fas fa-home text-blue-600 dark:text-blue-400"></i>
          </div>
          <div>
            <div class="text-lg font-semibold">{{ user ? 'Dashboard' : 'Home' }}</div>
            <div class="text-sm opacity-70">{{ user ? 'Your bow setups' : 'Get started' }}</div>
          </div>
        </NuxtLink>
        
        <NuxtLink 
          to="/calculator" 
          @click="closeMenu"
          class="flex items-center px-5 py-4 text-lg font-semibold transition-all duration-200 rounded-2xl hover:scale-[1.02] active:scale-[0.98]"
          :class="{ 
            'bg-green-500 text-white shadow-lg shadow-green-500/25': $route.path === '/calculator',
            'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700': $route.path !== '/calculator'
          }"
        >
          <div class="w-10 h-10 rounded-xl bg-green-100 dark:bg-green-900 flex items-center justify-center mr-4">
            <i class="fas fa-calculator text-green-600 dark:text-green-400"></i>
          </div>
          <div>
            <div class="text-lg font-semibold">Spine Calculator</div>
            <div class="text-sm opacity-70">Find your perfect arrow</div>
          </div>
        </NuxtLink>
        
        <NuxtLink 
          to="/database" 
          @click="closeMenu"
          class="flex items-center px-5 py-4 text-lg font-semibold transition-all duration-200 rounded-2xl hover:scale-[1.02] active:scale-[0.98]"
          :class="{ 
            'bg-purple-500 text-white shadow-lg shadow-purple-500/25': $route.path === '/database',
            'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700': $route.path !== '/database'
          }"
        >
          <div class="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900 flex items-center justify-center mr-4">
            <i class="fas fa-database text-purple-600 dark:text-purple-400"></i>
          </div>
          <div>
            <div class="text-lg font-semibold">Arrow Database</div>
            <div class="text-sm opacity-70">Browse arrow specs</div>
          </div>
        </NuxtLink>
      </div>
      
      <!-- Secondary Actions (Compact) -->
      <div class="space-y-1 mb-6">
        <div class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-4 mb-2">
          Tools & Guides
        </div>
        
        <NuxtLink 
          to="/tuning" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 dark:text-gray-200 transition-colors rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700"
          :class="{ 'bg-orange-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400': $route.path === '/tuning' }"
        >
          <i class="fas fa-bullseye w-6 mr-3 text-orange-500"></i>
          Interactive Tuning
        </NuxtLink>
        
        <NuxtLink 
          to="/change-history" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 dark:text-gray-200 transition-colors rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700"
          :class="{ 'bg-gray-50 text-gray-700 dark:bg-gray-700 dark:text-gray-200': $route.path === '/change-history' }"
        >
          <i class="fas fa-history w-6 mr-3 text-gray-500"></i>
          Change History
        </NuxtLink>
        
        <NuxtLink 
          to="/journal" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 dark:text-gray-200 transition-colors rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700"
          :class="{ 'bg-gray-50 text-gray-700 dark:bg-gray-700 dark:text-gray-200': $route.path === '/journal' }"
        >
          <i class="fas fa-book w-6 mr-3 text-orange-500"></i>
          Journal
        </NuxtLink>
        
        <NuxtLink 
          to="/info" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 dark:text-gray-200 transition-colors rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400': $route.path.startsWith('/info') }"
        >
          <i class="fas fa-info-circle w-6 mr-3 text-blue-500"></i>
          Information Center
        </NuxtLink>
        
        <NuxtLink 
          to="/about" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 dark:text-gray-200 transition-colors rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700"
          :class="{ 'bg-gray-50 text-gray-700 dark:bg-gray-700 dark:text-gray-200': $route.path === '/about' }"
        >
          <i class="fas fa-question-circle w-6 mr-3 text-gray-500"></i>
          About
        </NuxtLink>
      </div>
      
      <!-- User Actions -->
      <div v-if="user" class="space-y-2">
        <div class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-4 mb-2">
          Account
        </div>
        
        <NuxtLink
          v-if="user && isAdmin"
          to="/admin"
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-red-700 dark:text-red-400 transition-all duration-200 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20 hover:scale-[1.01]"
        >
          <i class="fas fa-shield-alt w-6 mr-3"></i>
          Admin Panel
        </NuxtLink>
        
        <button
          @click="handleLogout"
          class="flex items-center w-full px-4 py-3 text-base font-medium text-gray-600 dark:text-gray-400 transition-all duration-200 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 hover:scale-[1.01]"
        >
          <i class="fas fa-sign-out-alt w-6 mr-3"></i>
          Logout
        </button>
      </div>
      
      <div v-else class="space-y-2">
        <button
          @click="handleLogin"
          class="flex items-center justify-center w-full px-6 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-2xl transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
        >
          <i class="fab fa-google mr-3 text-xl"></i>
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

// Define emits to prevent warnings
const emit = defineEmits(['login'])

const { user, logout, loginWithGoogle } = useAuth()
const route = useRoute()
const { isAdmin } = useAuth()

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