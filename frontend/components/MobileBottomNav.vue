<template>
  <div class="fixed bottom-0 left-0 right-0 mobile-bottom-nav bg-white dark:bg-gray-900 md:hidden shadow-lg">
    <div class="flex h-20 items-center justify-around px-4">
      <!-- Home/Menu -->
      <button
        @click="toggleMenu"
        class="flex flex-col items-center justify-center p-2 w-16 h-16 rounded-2xl transition-all duration-200"
        :class="menuOpen 
          ? 'bg-primary-100 text-primary-700 dark:bg-primary-800 dark:text-primary-200' 
          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'"
      >
        <i class="fas text-2xl mb-1" :class="menuOpen ? 'fa-times' : 'fa-bars'"></i>
        <span class="text-xs font-medium">{{ menuOpen ? 'Close' : 'Menu' }}</span>
      </button>

      <!-- Bow Setup Picker -->
      <div class="flex items-center justify-center">
        <BowSetupPicker v-if="user" :is-mobile="true" />
        <div v-else class="w-16 h-16"></div>
      </div>

      <!-- My Setup / Login -->
      <NuxtLink
        v-if="user"
        to="/my-setup"
        class="flex flex-col items-center justify-center p-2 w-16 h-16 rounded-2xl transition-all duration-200"
        :class="$route.path === '/my-setup'
          ? 'bg-primary-100 text-primary-700 dark:bg-primary-800 dark:text-primary-200'
          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'"
      >
        <i class="fas fa-user text-xl mb-1"></i>
        <span class="text-xs font-medium">Setup</span>
      </NuxtLink>
      <button
        v-else
        @click="handleLogin"
        class="flex flex-col items-center justify-center p-2 w-16 h-16 rounded-2xl transition-all duration-200 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
      >
        <i class="fas fa-sign-in-alt text-xl mb-1"></i>
        <span class="text-xs font-medium">Login</span>
      </button>
    </div>
    
    <!-- Mobile Menu Overlay -->
    <div v-if="menuOpen" class="fixed inset-0 bg-black bg-opacity-50 z-40" @click="closeMenu"></div>
    
    <!-- Mobile Menu -->
    <div v-if="menuOpen" class="fixed bottom-16 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 z-50 shadow-lg">
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
          to="/calculator" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/calculator' }"
        >
          <i class="fas fa-calculator w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          Spine Calculator
        </NuxtLink>
        
        <NuxtLink 
          to="/guides" 
          @click="closeMenu"
          class="flex items-center px-4 py-3 text-base font-medium text-gray-700 transition-colors rounded-lg hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
          :class="{ 'bg-blue-50 text-blue-600 dark:bg-purple-900/20 dark:text-purple-400': $route.path === '/guides' }"
        >
          <i class="fas fa-book-open w-6 mr-3 text-gray-500 dark:text-gray-400"></i>
          Tuning Guides
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
const { user, logout, loginWithGoogle } = useAuth()
const route = useRoute()
const { isAdmin } = useAuth()

// Menu state
const menuOpen = ref(false)

// Menu methods
const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
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

// Close menu when route changes
watch(() => route.path, () => {
  closeMenu()
})
</script>