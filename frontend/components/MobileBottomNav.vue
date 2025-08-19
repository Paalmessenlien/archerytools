<template>
  <div 
    class="fixed bottom-0 left-0 right-0 mobile-bottom-nav bg-white dark:bg-gray-900 md:hidden shadow-lg border-t border-gray-200 dark:border-gray-700 transition-transform duration-300 ease-out backdrop-blur-sm bg-white/95 dark:bg-gray-900/95" 
    style="padding-bottom: env(safe-area-inset-bottom);"
    :class="{ 'translate-y-full': isHidden }"
  >
    <div class="flex items-center justify-around px-4" :class="menuOpen ? 'h-20' : 'h-16 md-mobile:h-18'">
      <!-- Home/Menu -->
      <button
        @click="toggleMenu"
        class="mobile-nav-button flex flex-col items-center justify-center p-2 rounded-2xl transition-all duration-200 active:scale-95"
        :class="[
          menuOpen 
            ? 'bg-primary-100 text-primary-700 dark:bg-primary-800 dark:text-primary-200' 
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
          menuOpen ? 'w-16 h-16' : 'w-14 h-14 md-mobile:w-16 md-mobile:h-16'
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
          menuOpen ? 'w-16 h-16' : 'w-14 h-14 md-mobile:w-16 md-mobile:h-16'
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
    
    <!-- Mobile Menu Overlay -->
    <div v-if="menuOpen" class="fixed inset-0 bg-black bg-opacity-50 modal-overlay transition-opacity duration-300" @click="closeMenu"></div>
    
    <!-- Mobile Menu -->
    <div v-if="menuOpen" class="fixed left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 modal-container shadow-lg transform transition-all duration-300 ease-out backdrop-blur-sm bg-white/95 dark:bg-gray-800/95" :class="menuOpen ? 'bottom-16 md-mobile:bottom-18 translate-y-0' : 'bottom-0 translate-y-full'">
      <div class="px-4 py-6 space-y-4">
        <NuxtLink 
          :to="user ? '/my-setup' : '/'" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': (user && $route.path === '/my-setup') || (!user && $route.path === '/') }"
        >
          <i class="fas fa-home w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          {{ user ? 'Dashboard' : 'Home' }}
        </NuxtLink>
        
        <NuxtLink 
          to="/database" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/database' }"
        >
          <i class="fas fa-database w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          Arrow Database
        </NuxtLink>
        
        <NuxtLink 
          to="/change-history" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/change-history' }"
        >
          <i class="fas fa-history w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          Change History
        </NuxtLink>
        
        <NuxtLink 
          to="/calculator" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/calculator' }"
        >
          <i class="fas fa-calculator w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          Spine Calculator
        </NuxtLink>
        
        
        <NuxtLink 
          to="/tuning" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/tuning' }"
        >
          <i class="fas fa-bullseye w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          Interactive Tuning
        </NuxtLink>
        
        <NuxtLink 
          to="/info" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path.startsWith('/info') }"
        >
          <i class="fas fa-info-circle w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          Information Center
        </NuxtLink>
        
        <NuxtLink 
          to="/about" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/about' }"
        >
          <i class="fas fa-question-circle w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          About
        </NuxtLink>
        
        <hr class="border-gray-200 dark:border-gray-700">
        
        <div v-if="user" class="space-y-2">
          <NuxtLink
            v-if="user && isAdmin"
            to="/admin"
            @click="closeMenu"
            class="flex items-center px-4 py-3 text-base font-medium text-red-700 transition-colors rounded-lg hover:bg-red-100 dark:text-red-200 dark:hover:bg-red-900/20"
          >
            <i class="fas fa-shield-alt w-6 mr-3"></i>
            Admin Panel
          </NuxtLink>
          
          <button
            @click="handleLogout"
            class="flex items-center w-full px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            <i class="fas fa-sign-out-alt w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
            Logout
          </button>
        </div>
        
        <div v-else class="space-y-2">
          <button
            @click="handleLogin"
            class="flex items-center w-full px-4 py-3 text-base font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 rounded-lg transition-colors"
          >
            <i class="fab fa-google w-6 mr-3"></i>
            Login with Google
          </button>
        </div>
        
        <!-- Dark Mode Toggle -->
        <div class="flex items-center justify-between px-4 py-3">
          <span class="text-base font-medium text-gray-700 dark:text-gray-300">Dark Mode</span>
          <DarkModeToggle />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const { user, logout, loginWithGoogle } = useAuth()
const route = useRoute()
const { isAdmin } = useAuth()

// Menu state
const menuOpen = ref(false)

// Auto-hide functionality
const isHidden = ref(false)
const lastScrollY = ref(0)
const scrollThreshold = 50 // Minimum scroll distance to trigger hide/show

// Scroll handling
const handleScroll = () => {
  // Don't hide when menu is open
  if (menuOpen.value) return
  
  const currentScrollY = window.scrollY
  const scrollDifference = currentScrollY - lastScrollY.value
  
  // Show when scrolling up or at top
  if (scrollDifference < -scrollThreshold || currentScrollY < 100) {
    isHidden.value = false
  }
  // Hide when scrolling down significantly
  else if (scrollDifference > scrollThreshold && currentScrollY > 200) {
    isHidden.value = true
  }
  
  lastScrollY.value = currentScrollY
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