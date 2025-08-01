<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center px-4">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Header -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 flex items-center justify-center bg-indigo-600 dark:bg-purple-600 rounded-full shadow-lg mb-4">
          <i class="fas fa-crosshairs text-white text-2xl"></i>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Archery Tools
        </h1>
        <div class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 mb-4">
          <i class="fas fa-flask mr-2"></i>
          BETA VERSION
        </div>
      </div>

      <!-- Beta Disclaimer Card -->
      <div class="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="text-center mb-6">
          <i class="fas fa-info-circle text-blue-600 dark:text-blue-400 text-4xl mb-3"></i>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Invitation-Only Beta Access
          </h2>
        </div>

        <div class="space-y-4 text-sm text-gray-600 dark:text-gray-300">
          <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
            <div class="flex items-start">
              <i class="fas fa-exclamation-triangle text-amber-600 dark:text-amber-400 mr-3 mt-0.5"></i>
              <div>
                <h3 class="font-medium text-amber-800 dark:text-amber-200 mb-2">Beta Status Notice</h3>
                <p class="text-amber-700 dark:text-amber-300 text-sm">
                  This platform is currently in <strong>beta testing</strong>. Features may be incomplete, 
                  data may be reset, and functionality is subject to change without notice.
                </p>
              </div>
            </div>
          </div>

          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div class="flex items-start">
              <i class="fas fa-users text-blue-600 dark:text-blue-400 mr-3 mt-0.5"></i>
              <div>
                <h3 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Invitation-Only Access</h3>
                <p class="text-blue-700 dark:text-blue-300 text-sm">
                  Access to this platform is currently limited to invited users only. 
                  You must be specifically invited by the development team to participate in the beta program.
                </p>
              </div>
            </div>
          </div>

          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <div class="flex items-start">
              <i class="fas fa-shield-alt text-green-600 dark:text-green-400 mr-3 mt-0.5"></i>
              <div>
                <h3 class="font-medium text-green-800 dark:text-green-200 mb-2">What We Offer</h3>
                <ul class="text-green-700 dark:text-green-300 text-sm space-y-1">
                  <li>• Professional arrow tuning calculations</li>
                  <li>• Comprehensive arrow database (13 manufacturers)</li>
                  <li>• Bow setup management</li>
                  <li>• Personalized arrow recommendations</li>
                  <li>• Arrow configuration tracking</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Login Section -->
        <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div v-if="!user" class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              If you have been invited to participate in the beta program, please sign in with your Google account:
            </p>
            <CustomButton
              @click="handleLogin"
              variant="filled"
              :disabled="isLoggingIn"
              class="w-full bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 mb-3"
            >
              <i class="fab fa-google mr-2"></i>
              <span v-if="isLoggingIn">Signing in...</span>
              <span v-else>Sign in with Google</span>
            </CustomButton>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Only invited Google accounts will be granted access
            </p>
          </div>

          <div v-else class="text-center">
            <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-4">
              <i class="fas fa-check-circle text-green-600 dark:text-green-400 text-2xl mb-2"></i>
              <p class="text-green-800 dark:text-green-200 font-medium">Welcome, {{ user.name || user.email }}!</p>
              <p class="text-green-700 dark:text-green-300 text-sm">You have beta access to the platform.</p>
            </div>
            <CustomButton
              @click="enterPlatform"
              variant="filled"
              class="w-full bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800"
            >
              <i class="fas fa-arrow-right mr-2"></i>
              Enter Arrow Tuning Platform
            </CustomButton>
          </div>
        </div>

        <!-- Contact Info -->
        <div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            Need an invitation? Contact the development team for access.
          </p>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center text-xs text-gray-500 dark:text-gray-400">
        <p>&copy; 2025 Arrow Tuning Platform. Beta Version {{ betaVersion }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

const { user, loginWithGoogle } = useAuth()

const isLoggingIn = ref(false)
const betaVersion = ref('1.0.0-beta')

const handleLogin = () => {
  console.log('🚀 handleLogin called in login.vue');
  isLoggingIn.value = true;
  loginWithGoogle();
  // No longer need to handle result here, as the callback will redirect.
  // The isLoggingIn state might not be reset if the user closes the popup,
  // but that's a minor UX issue for now.
};

const enterPlatform = () => {
  navigateTo('/')
}

// Check if user is already logged in and redirect
onMounted(() => {
  if (user.value) {
    // User is already authenticated, could redirect or show enter button
    // For now, we'll show the enter platform button
  }
})

// Set page title
useHead({
  title: 'Login - Arrow Tuning Platform Beta',
  meta: [
    { name: 'description', content: 'Access the Arrow Tuning Platform beta - Invitation only' }
  ]
})
</script>

<style scoped>
/* Additional styles for the login page if needed */
</style>