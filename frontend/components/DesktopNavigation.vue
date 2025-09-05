<template>
  <nav class="hidden lg:flex items-center space-x-1">
    <!-- Primary Navigation Items -->
    <ClientOnly>
      <NuxtLink
        :to="(user && isLoggedIn) ? '/my-setup' : '/'"
        class="nav-item"
        :class="getNavClass((user && isLoggedIn && $route.path === '/my-setup') || (!user && $route.path === '/'))"
      >
        <i class="fas fa-home text-sm mr-2"></i>
        <span>{{ (user && isLoggedIn) ? 'Dashboard' : 'Home' }}</span>
      </NuxtLink>
      <template #fallback>
        <div class="nav-item text-gray-600 dark:text-gray-300">
          <i class="fas fa-home text-sm mr-2"></i>
          <span>Home</span>
        </div>
      </template>
    </ClientOnly>
    
    <NuxtLink
      to="/calculator"
      class="nav-item"
      :class="getNavClass($route.path === '/calculator')"
    >
      <i class="fas fa-calculator text-sm mr-2"></i>
      <span>Calculator</span>
    </NuxtLink>
    
    <NuxtLink
      to="/database"
      class="nav-item"
      :class="getNavClass($route.path === '/database')"
    >
      <i class="fas fa-database text-sm mr-2"></i>
      <span>Database</span>
    </NuxtLink>
    
    
    <NuxtLink
      to="/journal"
      class="nav-item"
      :class="getNavClass($route.path === '/journal')"
    >
      <i class="fas fa-book text-sm mr-2"></i>
      <span>Journal</span>
    </NuxtLink>

    <!-- Secondary Menu Dropdown -->
    <ClientOnly>
      <div class="relative">
        <button
          @click="toggleSecondaryMenu"
          class="nav-item"
          :class="getNavClass(secondaryMenuOpen || isSecondaryRoute)"
        >
          <i class="fas fa-ellipsis-h text-sm mr-2"></i>
          <span>More</span>
          <i class="fas fa-chevron-down text-xs ml-1 transition-transform duration-200" :class="{ 'rotate-180': secondaryMenuOpen }"></i>
        </button>
        
        <!-- Dropdown Menu -->
        <div v-if="secondaryMenuOpen" class="absolute top-full right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50">
          <NuxtLink
            to="/info"
            @click="closeSecondaryMenu"
            class="dropdown-item"
            :class="{ 'active': $route.path.startsWith('/info') }"
          >
            <i class="fas fa-info-circle text-blue-500 w-5"></i>
            <div>
              <div class="font-medium">Information Center</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">Guides & resources</div>
            </div>
          </NuxtLink>
          
          <NuxtLink
            to="/about"
            @click="closeSecondaryMenu"
            class="dropdown-item"
            :class="{ 'active': $route.path === '/about' }"
          >
            <i class="fas fa-question-circle text-gray-500 w-5"></i>
            <div>
              <div class="font-medium">About</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">Platform info</div>
            </div>
          </NuxtLink>
          
          <!-- Admin Section (if applicable) -->
          <div v-if="user && isAdmin" class="border-t border-gray-200 dark:border-gray-700 mt-2 pt-2">
            <NuxtLink
              to="/admin"
              @click="closeSecondaryMenu"
              class="dropdown-item text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
              :class="{ 'active': $route.path === '/admin' }"
            >
              <i class="fas fa-shield-alt text-red-500 w-5"></i>
              <div>
                <div class="font-medium">Admin Panel</div>
                <div class="text-xs text-red-500 dark:text-red-400">System administration</div>
              </div>
            </NuxtLink>
            
            <NuxtLink
              to="/design"
              @click="closeSecondaryMenu"
              class="dropdown-item text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20"
              :class="{ 'active': $route.path === '/design' }"
            >
              <i class="fas fa-palette text-purple-500 w-5"></i>
              <div>
                <div class="font-medium">Design System</div>
                <div class="text-xs text-purple-500 dark:text-purple-400">UI components & styles</div>
              </div>
            </NuxtLink>
          </div>
          
          <!-- Settings -->
          <div class="border-t border-gray-200 dark:border-gray-700 mt-2 pt-2">
            <div class="dropdown-item cursor-default">
              <i :class="isDarkMode ? 'fas fa-moon' : 'fas fa-sun'" class="text-gray-500 w-5"></i>
              <div class="flex-1 flex items-center justify-between">
                <div>
                  <div class="font-medium">{{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">Toggle theme</div>
                </div>
                <DarkModeToggle />
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #fallback>
        <div class="nav-item text-gray-600 dark:text-gray-300">
          <i class="fas fa-ellipsis-h text-sm mr-2"></i>
          <span>More</span>
          <i class="fas fa-chevron-down text-xs ml-1"></i>
        </div>
      </template>
    </ClientOnly>

    <!-- User Profile & Actions -->
    <ClientOnly>
      <div v-if="user && isLoggedIn" class="flex items-center space-x-3 ml-4 pl-4 border-l border-gray-200 dark:border-gray-700">
        <div class="relative">
          <button
            @click="toggleUserMenu"
            class="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <img 
              v-if="user.picture" 
              :src="user.picture" 
              :alt="user.name"
              class="w-8 h-8 rounded-full"
            >
            <div v-else class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
              <i class="fas fa-user text-white text-sm"></i>
            </div>
            <i class="fas fa-chevron-down text-xs transition-transform duration-200" :class="{ 'rotate-180': userMenuOpen }"></i>
          </button>
          
          <!-- User Dropdown -->
          <div v-if="userMenuOpen" class="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50">
            <div class="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
              <div class="font-medium text-gray-900 dark:text-gray-100">{{ user.name }}</div>
              <div class="text-sm text-gray-500 dark:text-gray-400">{{ user.email }}</div>
            </div>
            
            <NuxtLink
              to="/my-setup"
              @click="closeUserMenu"
              class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <i class="fas fa-user mr-2"></i>
              My Profile
            </NuxtLink>
            
            <button
              @click="handleLogout"
              class="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <i class="fas fa-sign-out-alt mr-2"></i>
              Logout
            </button>
          </div>
        </div>
      </div>
      
      <!-- Login Button (when not logged in) -->
      <div v-else class="ml-4">
        <button
          @click="$emit('login')"
          class="flex items-center space-x-2 px-4 py-2 bg-blue-600 dark:bg-purple-600 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-purple-700 transition-colors"
        >
          <i class="fab fa-google text-sm"></i>
          <span>Sign In</span>
        </button>
      </div>
      <template #fallback>
        <div class="ml-4">
          <div class="w-20 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
        </div>
      </template>
    </ClientOnly>
  </nav>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useAuth } from '~/composables/useAuth'

// Define emits
const emit = defineEmits(['login'])

// Auth composable
const { user, logout, isLoggedIn, isAdmin } = useAuth()
const { isDarkMode } = useDarkMode()

// Local state
const secondaryMenuOpen = ref(false)
const userMenuOpen = ref(false)

// Computed properties
const isSecondaryRoute = computed(() => {
  const route = useRoute()
  return ['/info', '/about', '/admin', '/design'].some(path => route.path.startsWith(path))
})

// Methods
const getNavClass = (isActive) => {
  return isActive 
    ? 'bg-blue-100 text-blue-700 dark:bg-purple-900/30 dark:text-purple-300' 
    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700'
}

const toggleSecondaryMenu = () => {
  secondaryMenuOpen.value = !secondaryMenuOpen.value
  userMenuOpen.value = false // Close user menu
}

const closeSecondaryMenu = () => {
  secondaryMenuOpen.value = false
}

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
  secondaryMenuOpen.value = false // Close secondary menu
}

const closeUserMenu = () => {
  userMenuOpen.value = false
}

const handleLogout = async () => {
  try {
    await logout()
    closeUserMenu()
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

// Close dropdowns when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    secondaryMenuOpen.value = false
    userMenuOpen.value = false
  }
}

// Close dropdowns when route changes
const route = useRoute()
watch(() => route.path, () => {
  secondaryMenuOpen.value = false
  userMenuOpen.value = false
})

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.nav-item {
  @apply flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 whitespace-nowrap;
}

.dropdown-item {
  @apply flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors;
}

.dropdown-item.active {
  @apply bg-blue-50 text-blue-700 dark:bg-purple-900/20 dark:text-purple-300;
}
</style>