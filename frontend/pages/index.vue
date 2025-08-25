<template>
  <div>
    <!-- Loading State -->
    <div v-if="isCheckingAuth" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
        <p class="text-gray-700 dark:text-gray-300">Loading...</p>
      </div>
    </div>

    <!-- Public Landing Page for Non-Authenticated Users -->
    <div v-else class="text-center py-6 md:py-12 mobile-container">
      <h1 class="mobile-heading-1 md:text-4xl font-bold text-gray-900 dark:text-gray-100 mobile-element-spacing md:mb-4">Welcome to ArcheryTool</h1>
      <p class="mobile-body-large md:text-xl text-gray-600 dark:text-gray-300 mobile-section-spacing md:mb-8">
        Professional archery tools for precision and performance
      </p>
      
      <!-- Beta Notice -->
      <div class="mobile-section-spacing md:mb-8 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3 sm-mobile:p-4 max-w-2xl mx-auto">
        <div class="flex items-center justify-center">
          <i class="fas fa-flask text-orange-600 dark:text-orange-400 mr-2 sm-mobile:mr-3"></i>
          <div class="text-left">
            <h4 class="mobile-body-medium md:text-sm font-medium text-orange-800 dark:text-orange-200 mobile-emphasis-high">Beta Testing Phase</h4>
            <p class="mobile-body-small md:text-xs text-orange-700 dark:text-orange-300 mt-0.5 sm-mobile:mt-1">
              Invitation-only access. Please log in to access the platform.
            </p>
          </div>
        </div>
      </div>

      <!-- Login Button -->
      <div class="mobile-section-spacing md:mb-8">
        <CustomButton
          @click="handleLogin"
          variant="primary"
          size="large"
          class="mobile-primary-action"
        >
          <i class="fab fa-google mr-2"></i>
          Login with Google
        </CustomButton>
      </div>

      <!-- Quick Info -->
      <div class="mobile-emphasis-medium text-gray-600 dark:text-gray-400 mobile-section-spacing">
        <p class="mobile-body-medium md:text-base mobile-tight-spacing md:mb-2">Access 1,100+ arrow specifications, professional spine calculations,</p>
        <p class="mobile-body-medium md:text-base">and personalized bow setup management.</p>
      </div>

      <!-- Learn More Link -->
      <div class="mobile-element-spacing md:mt-8">
        <NuxtLink to="/about" class="mobile-body-large md:text-base text-blue-600 hover:text-blue-700 dark:text-purple-400 dark:hover:text-purple-300 mobile-emphasis-medium">
          Learn more about ArcheryTool →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

const { user, loginWithGoogle, fetchUser } = useAuth()
const isCheckingAuth = ref(true)

// Handle login
const handleLogin = async () => {
  try {
    await loginWithGoogle()
    // After successful login, redirect to my-setup
    await navigateTo('/my-setup')
  } catch (error) {
    console.error('Login failed:', error)
  }
}

// Check authentication and redirect if logged in
onMounted(async () => {
  if (process.client) {
    try {
      await fetchUser()
      if (user.value) {
        // User is authenticated, redirect to my-setup
        await navigateTo('/my-setup')
        return
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    }
    isCheckingAuth.value = false
  }
})

// Set page title
useHead({
  title: 'ArcheryTool - Professional Archery Tools',
  meta: [
    { name: 'description', content: 'Professional archery tools with comprehensive arrow database, spine calculations, and personalized recommendations for archery enthusiasts.' }
  ]
})

// This page is public - no authentication middleware
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
</style>