<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <i class="fas fa-hourglass-half text-6xl text-yellow-500 mb-4"></i>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-gray-100">
          Account Pending Approval
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Your account has been created successfully
        </p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white dark:bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <div class="space-y-6">
          <!-- Status Information -->
          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <i class="fas fa-exclamation-triangle text-yellow-400"></i>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  Approval Required
                </h3>
                <div class="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                  <p>
                    Your account is currently pending administrator approval. This is part of our invitation-only beta program to ensure platform quality and security.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- What's Next -->
          <div class="space-y-4">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">What happens next?</h4>
            <div class="space-y-3">
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900">
                    <span class="text-xs font-medium text-blue-600 dark:text-blue-400">1</span>
                  </div>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-gray-700 dark:text-gray-300">
                    An administrator will review your account request
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900">
                    <span class="text-xs font-medium text-blue-600 dark:text-blue-400">2</span>
                  </div>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-gray-700 dark:text-gray-300">
                    You'll receive email notification when approved
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900">
                    <span class="text-xs font-medium text-blue-600 dark:text-blue-400">3</span>
                  </div>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-gray-700 dark:text-gray-300">
                    Log in again to access all platform features
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Contact Information -->
          <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h5 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Need Help?</h5>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              If you have questions about your account status, please contact our support team.
            </p>
            <div class="mt-3">
              <a 
                href="mailto:support@archerytools.com" 
                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:hover:bg-blue-800 transition-colors"
              >
                <i class="fas fa-envelope mr-2"></i>
                Contact Support
              </a>
            </div>
          </div>

          <!-- Actions -->
          <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
            <div class="space-y-3">
              <button
                @click="checkStatus"
                :disabled="isCheckingStatus"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <i v-if="isCheckingStatus" class="fas fa-spinner fa-spin mr-2"></i>
                <i v-else class="fas fa-refresh mr-2"></i>
                {{ isCheckingStatus ? 'Checking...' : 'Check Status Again' }}
              </button>
              
              <NuxtLink
                to="/"
                class="w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                <i class="fas fa-home mr-2"></i>
                Back to Home
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

// Page meta
definePageMeta({
  layout: false
})

const { loginWithGoogle } = useAuth()
const isCheckingStatus = ref(false)

const checkStatus = async () => {
  isCheckingStatus.value = true
  try {
    // Try to login again to check if status has changed
    await loginWithGoogle()
  } catch (error) {
    console.error('Status check failed:', error)
  } finally {
    isCheckingStatus.value = false
  }
}
</script>