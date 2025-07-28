<template>
  <div>
    <!-- Beta Notice Banner -->
    <div class="mb-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-book text-blue-600 dark:text-blue-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-blue-800 dark:text-blue-200">Archery Guides</h4>
          <p class="text-xs text-blue-700 dark:text-blue-300 mt-1">
            Comprehensive guides to help you improve your archery skills and equipment setup.
          </p>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Archery Guides</h1>
      <p class="text-gray-600 dark:text-gray-300">Learn essential archery techniques and equipment setup from our comprehensive guide collection.</p>
    </div>

    <!-- Guide Categories -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      
      <!-- Equipment Setup Guides -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center mb-4">
          <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <i class="fas fa-tools text-blue-600 dark:text-blue-400 text-xl"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 ml-3">Equipment Setup</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Essential guides for setting up and tuning your archery equipment.</p>
        
        <div class="space-y-3">
          <NuxtLink 
            to="/guides/draw-length"
            class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <i class="fas fa-ruler text-blue-600 dark:text-blue-400 mr-3"></i>
                <div>
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                    How to Measure Draw Length
                  </h4>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    Step-by-step guide to accurately measure your draw length
                  </p>
                </div>
              </div>
              <i class="fas fa-chevron-right text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400"></i>
            </div>
          </NuxtLink>

          <div class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
            <div class="flex items-center">
              <i class="fas fa-weight-hanging text-gray-400 mr-3"></i>
              <div>
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Bow Weight Selection
                </h4>
                <p class="text-xs text-gray-400">
                  Coming soon
                </p>
              </div>
            </div>
          </div>

          <div class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
            <div class="flex items-center">
              <i class="fas fa-bullseye text-gray-400 mr-3"></i>
              <div>
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Sight Setup & Tuning
                </h4>
                <p class="text-xs text-gray-400">
                  Coming soon
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Shooting Technique Guides -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center mb-4">
          <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
            <i class="fas fa-crosshairs text-green-600 dark:text-green-400 text-xl"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 ml-3">Shooting Technique</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Master proper shooting form and technique.</p>
        
        <div class="space-y-3">
          <div class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
            <div class="flex items-center">
              <i class="fas fa-hand-paper text-gray-400 mr-3"></i>
              <div>
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Proper Grip & Stance
                </h4>
                <p class="text-xs text-gray-400">
                  Coming soon
                </p>
              </div>
            </div>
          </div>

          <div class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
            <div class="flex items-center">
              <i class="fas fa-eye text-gray-400 mr-3"></i>
              <div>
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Aiming Techniques
                </h4>
                <p class="text-xs text-gray-400">
                  Coming soon
                </p>
              </div>
            </div>
          </div>

          <div class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
            <div class="flex items-center">
              <i class="fas fa-hand-point-up text-gray-400 mr-3"></i>
              <div>
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Release Techniques
                </h4>
                <p class="text-xs text-gray-400">
                  Coming soon
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tuning & Maintenance Guides -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center mb-4">
          <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <i class="fas fa-cogs text-purple-600 dark:text-purple-400 text-xl"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 ml-3">Tuning & Maintenance</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Learn to tune and maintain your equipment for optimal performance.</p>
        
        <div class="space-y-3">
          <div class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
            <div class="flex items-center">
              <i class="fas fa-arrows-alt-h text-gray-400 mr-3"></i>
              <div>
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Paper Tuning Guide
                </h4>
                <p class="text-xs text-gray-400">
                  Coming soon
                </p>
              </div>
            </div>
          </div>

          <div class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
            <div class="flex items-center">
              <i class="fas fa-wrench text-gray-400 mr-3"></i>
              <div>
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Rest Adjustment
                </h4>
                <p class="text-xs text-gray-400">
                  Coming soon
                </p>
              </div>
            </div>
          </div>

          <div class="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
            <div class="flex items-center">
              <i class="fas fa-broom text-gray-400 mr-3"></i>
              <div>
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Equipment Maintenance
                </h4>
                <p class="text-xs text-gray-400">
                  Coming soon
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Featured Guide Section -->
    <div class="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
      <div class="flex items-start space-x-4">
        <div class="p-3 bg-blue-100 dark:bg-blue-900/50 rounded-xl">
          <i class="fas fa-star text-blue-600 dark:text-blue-400 text-2xl"></i>
        </div>
        <div class="flex-1">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Featured Guide</h3>
          <h4 class="text-lg font-medium text-blue-900 dark:text-blue-100 mb-2">How to Measure Draw Length</h4>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            Accurate draw length measurement is crucial for proper bow setup and optimal shooting performance. 
            This comprehensive guide covers multiple measurement methods and explains why draw length matters.
          </p>
          <NuxtLink 
            to="/guides/draw-length"
            class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
          >
            Read Guide
            <i class="fas fa-arrow-right ml-2"></i>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Set page title and meta
useHead({
  title: 'Archery Guides - Learn Essential Techniques',
  meta: [
    { name: 'description', content: 'Comprehensive archery guides covering equipment setup, shooting technique, and maintenance. Learn from step-by-step tutorials.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})
</script>