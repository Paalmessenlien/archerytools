<template>
  <div
    v-if="showUpdateNotification"
    class="fixed top-4 right-4 z-[2000] max-w-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl p-4 transform transition-all duration-500"
    :class="showUpdateNotification ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'"
  >
    <div class="flex items-start space-x-3">
      <div class="flex-shrink-0">
        <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
          <i class="fas fa-sync-alt text-blue-600 dark:text-blue-400 text-lg"></i>
        </div>
      </div>
      <div class="flex-1">
        <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
          App Update Available
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
          A new version is available with improved design and fixes. Reload to get the latest version.
        </p>
        <div class="flex space-x-2">
          <button
            @click="handleReload"
            class="px-3 py-1 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Reload Now
          </button>
          <button
            @click="handleDismiss"
            class="px-3 py-1 text-xs font-medium text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
          >
            Later
          </button>
        </div>
      </div>
      <button
        @click="handleDismiss"
        class="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
      >
        <i class="fas fa-times text-sm"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
const { showUpdateNotification, dismissUpdateNotification, reloadApp } = useAppVersion()

const handleReload = () => {
  reloadApp()
}

const handleDismiss = () => {
  dismissUpdateNotification()
}
</script>