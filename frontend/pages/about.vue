<template>
  <div>
    <!-- Beta Notice Banner -->
    <div class="mb-6 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-flask text-orange-600 dark:text-orange-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200">Beta Testing Phase</h4>
          <p class="text-xs text-orange-700 dark:text-orange-300 mt-1">
            This platform is in beta. Features may change and data may be reset. Invitation-only access.
          </p>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">About ArcheryTool Beta</h1>
      <div class="prose dark:prose-invert max-w-none">
        <p class="text-lg text-gray-600 dark:text-gray-300 mb-4">
          Professional archery tools designed for enthusiasts who demand precision and performance.
        </p>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <div class="bg-blue-50 dark:bg-blue-900/20 p-4 sm:p-6 rounded-lg border border-blue-200 dark:border-blue-800">
            <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-3">
              <i class="fas fa-database mr-2"></i>
              Comprehensive Database
            </h3>
            <p class="text-blue-800 dark:text-blue-300">
              Access specifications for 1,100+ arrow models from 13 leading manufacturers including Easton, Gold Tip, Victory, and more.
            </p>
          </div>
          
          <div class="bg-green-50 dark:bg-green-900/20 p-4 sm:p-6 rounded-lg border border-green-200 dark:border-green-800">
            <h3 class="text-lg font-semibold text-green-900 dark:text-green-200 mb-3">
              <i class="fas fa-calculator mr-2"></i>
              Professional Calculations
            </h3>
            <p class="text-green-800 dark:text-green-300">
              Industry-standard spine calculations, FOC optimization, and intelligent arrow matching for your specific bow setup.
            </p>
          </div>
          
          <div class="bg-purple-50 dark:bg-purple-900/20 p-4 sm:p-6 rounded-lg border border-purple-200 dark:border-purple-800">
            <h3 class="text-lg font-semibold text-purple-900 dark:text-purple-200 mb-3">
              <i class="fas fa-user-cog mr-2"></i>
              Personal Setup Management
            </h3>
            <p class="text-purple-800 dark:text-purple-300">
              Save your bow configurations, track tuning sessions, and maintain your archery equipment profiles.
            </p>
          </div>
          
          <div class="bg-orange-50 dark:bg-orange-900/20 p-4 sm:p-6 rounded-lg border border-orange-200 dark:border-orange-800">
            <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-200 mb-3">
              <i class="fas fa-book-open mr-2"></i>
              Interactive Guides
            </h3>
            <p class="text-orange-800 dark:text-orange-300">
              Step-by-step tuning guides for paper tuning, bare shaft testing, and advanced optimization techniques.
            </p>
          </div>
        </div>

        <div class="bg-gray-50 dark:bg-gray-800/50 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
            <i class="fas fa-rocket mr-2"></i>
            Beta Features Available Now
          </h3>
          <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
            <li>Real-time arrow recommendations with compatibility scoring</li>
            <li>Advanced filtering by manufacturer, spine range, and diameter categories</li>
            <li>Multi-language support for international manufacturers</li>
            <li>Professional spine calculation engine with adjustable parameters</li>
            <li>Dark mode support and responsive design for all devices</li>
            <li>Secure Google OAuth authentication and personal data management</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Quick Access Section -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
      <div class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-4 sm:p-6 rounded-lg border border-blue-200 dark:border-blue-800">
        <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-3">
          <i class="fas fa-calculator mr-2"></i>
          Arrow Calculator
        </h3>
        <p class="text-blue-800 dark:text-blue-300 mb-4">
          Professional spine calculations and arrow recommendations based on your bow setup.
        </p>
        <NuxtLink to="/calculator">
          <CustomButton variant="filled" class="bg-blue-600 text-white hover:bg-blue-700">
            <i class="fas fa-calculator mr-2"></i>
            Open Calculator
          </CustomButton>
        </NuxtLink>
      </div>
      
      <div class="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 p-4 sm:p-6 rounded-lg border border-green-200 dark:border-green-800">
        <h3 class="text-lg font-semibold text-green-900 dark:text-green-200 mb-3">
          <i class="fas fa-database mr-2"></i>
          Arrow Database
        </h3>
        <p class="text-green-800 dark:text-green-300 mb-4">
          Browse 1,100+ arrow specifications from 13 leading manufacturers worldwide.
        </p>
        <NuxtLink to="/database">
          <CustomButton variant="filled" class="bg-green-600 text-white hover:bg-green-700">
            <i class="fas fa-search mr-2"></i>
            Browse Arrows
          </CustomButton>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Set page title
useHead({
  title: 'About - ArcheryTool Beta',
  meta: [
    { name: 'description', content: 'Learn about ArcheryTool Beta - Professional archery tools with comprehensive arrow database, spine calculations, and personalized recommendations for archery enthusiasts.' }
  ]
})

// This page is public - no authentication required
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
</style>