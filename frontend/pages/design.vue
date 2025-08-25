<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Access Denied for Non-Admins -->
    <div v-if="!isAdmin" class="flex items-center justify-center min-h-screen">
      <div class="text-center max-w-md mx-auto p-6">
        <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <i class="fas fa-shield-alt text-4xl text-red-600 dark:text-red-400 mb-4"></i>
          <h2 class="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">Access Restricted</h2>
          <p class="text-red-700 dark:text-red-300 mb-4">
            The Design System is only available to administrators.
          </p>
          <CustomButton @click="$router.push('/')" variant="outlined" class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400">
            <i class="fas fa-home mr-2"></i>
            Return Home
          </CustomButton>
        </div>
      </div>
    </div>

    <!-- Design System Content for Admins -->
    <div v-else>
      <!-- Header -->
      <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center">
              <i class="fas fa-palette text-2xl text-blue-600 dark:text-purple-400 mr-4"></i>
              <div>
                <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Design System</h1>
                <p class="text-sm text-gray-600 dark:text-gray-400">Archery Tools UI Components</p>
              </div>
            </div>
            <DarkModeToggle />
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav class="flex space-x-8 overflow-x-auto">
            <button
              v-for="section in sections"
              :key="section.id"
              @click="activeSection = section.id"
              :class="[
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeSection === section.id
                  ? 'border-blue-500 text-blue-600 dark:border-purple-400 dark:text-purple-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              ]"
            >
              <i :class="section.icon" class="mr-2"></i>
              {{ section.name }}
            </button>
          </nav>
        </div>
      </div>

      <!-- Content -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <!-- Sidebar Navigation -->
          <div class="lg:col-span-1">
            <div class="sticky top-24">
              <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-4">Quick Navigation</h3>
                <nav class="space-y-2">
                  <button
                    v-for="section in sections"
                    :key="section.id"
                    @click="activeSection = section.id"
                    :class="[
                      'w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      activeSection === section.id
                        ? 'bg-blue-50 text-blue-700 dark:bg-purple-900/30 dark:text-purple-300'
                        : 'text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                    ]"
                  >
                    <i :class="section.icon" class="mr-2 w-4"></i>
                    {{ section.name }}
                  </button>
                </nav>
              </div>
            </div>
          </div>

          <!-- Main Content -->
          <div class="lg:col-span-3">
            <!-- Overview Section -->
            <div v-if="activeSection === 'overview'" class="space-y-8">
              <DesignSystemOverview />
            </div>

            <!-- Colors Section -->
            <div v-if="activeSection === 'colors'" class="space-y-8">
              <DesignSystemColors />
            </div>

            <!-- Typography Section -->
            <div v-if="activeSection === 'typography'" class="space-y-8">
              <DesignSystemTypography />
            </div>

            <!-- Components Section -->
            <div v-if="activeSection === 'components'" class="space-y-8">
              <DesignSystemComponents />
            </div>

            <!-- Layout Section -->
            <div v-if="activeSection === 'layout'" class="space-y-8">
              <DesignSystemLayout />
            </div>

            <!-- Mobile Section -->
            <div v-if="activeSection === 'mobile'" class="space-y-8">
              <DesignSystemMobile />
            </div>

            <!-- Icons Section -->
            <div v-if="activeSection === 'icons'" class="space-y-8">
              <DesignSystemIcons />
            </div>

            <!-- Animations Section -->
            <div v-if="activeSection === 'animations'" class="space-y-8">
              <DesignSystemAnimations />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineAsyncComponent, h } from 'vue'
import { useAuth } from '~/composables/useAuth'
import DarkModeToggle from '~/components/DarkModeToggle.vue'
import CustomButton from '~/components/CustomButton.vue'

// Lazy import design system components for better performance
const DesignSystemOverview = defineAsyncComponent({
  loader: () => import('~/components/design-system/DesignSystemOverview.vue'),
  delay: 200,
  timeout: 3000,
  errorComponent: () => h('div', { class: 'text-red-600 p-4' }, 'Failed to load component'),
  loadingComponent: () => h('div', { class: 'animate-pulse p-4' }, 'Loading...')
})

const DesignSystemColors = defineAsyncComponent({
  loader: () => import('~/components/design-system/DesignSystemColors.vue'),
  delay: 200,
  timeout: 3000
})

const DesignSystemTypography = defineAsyncComponent({
  loader: () => import('~/components/design-system/DesignSystemTypography.vue'),
  delay: 200,
  timeout: 3000
})

const DesignSystemComponents = defineAsyncComponent({
  loader: () => import('~/components/design-system/DesignSystemComponents.vue'),
  delay: 200,
  timeout: 3000
})

const DesignSystemLayout = defineAsyncComponent({
  loader: () => import('~/components/design-system/DesignSystemLayout.vue'),
  delay: 200,
  timeout: 3000
})

const DesignSystemMobile = defineAsyncComponent({
  loader: () => import('~/components/design-system/DesignSystemMobile.vue'),
  delay: 200,
  timeout: 3000
})

const DesignSystemIcons = defineAsyncComponent({
  loader: () => import('~/components/design-system/DesignSystemIcons.vue'),
  delay: 200,
  timeout: 3000
})

const DesignSystemAnimations = defineAsyncComponent({
  loader: () => import('~/components/design-system/DesignSystemAnimations.vue'),
  delay: 200,
  timeout: 3000
})

// Meta
useHead({
  title: 'Design System - Archery Tools',
  meta: [
    { name: 'description', content: 'Complete design system and component library for Archery Tools application' }
  ]
})

// Authentication
const { user } = useAuth()
const isAdmin = computed(() => {
  return user.value?.email === 'messenlien@gmail.com'
})

// Navigation
const activeSection = ref('overview')

const sections = [
  { id: 'overview', name: 'Overview', icon: 'fas fa-home' },
  { id: 'colors', name: 'Colors', icon: 'fas fa-palette' },
  { id: 'typography', name: 'Typography', icon: 'fas fa-font' },
  { id: 'components', name: 'Components', icon: 'fas fa-cube' },
  { id: 'layout', name: 'Layout', icon: 'fas fa-th-large' },
  { id: 'mobile', name: 'Mobile', icon: 'fas fa-mobile-alt' },
  { id: 'icons', name: 'Icons', icon: 'fas fa-icons' },
  { id: 'animations', name: 'Animations', icon: 'fas fa-play' }
]
</script>

<style scoped>
/* Custom scrollbar for navigation */
nav::-webkit-scrollbar {
  display: none;
}

nav {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>