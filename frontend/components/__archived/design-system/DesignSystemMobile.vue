<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Mobile Design Patterns</h2>
      <p class="text-gray-600 dark:text-gray-400">
        Mobile-first design patterns optimized for touch interaction and small screens.
      </p>
    </div>

    <!-- Touch Targets -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Touch Targets</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Minimum 44px tap targets for optimal mobile usability and accessibility.
      </p>
      
      <div class="space-y-6">
        <!-- Touch Target Sizes -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Recommended Sizes</h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center">
              <div class="inline-flex items-center justify-center w-11 h-11 bg-blue-100 text-blue-800 rounded-lg border border-blue-200 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-800 mb-2">
                <i class="fas fa-check"></i>
              </div>
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">44px × 44px</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">Minimum size</div>
            </div>
            <div class="text-center">
              <div class="inline-flex items-center justify-center w-12 h-12 bg-green-100 text-green-800 rounded-lg border border-green-200 dark:bg-green-900/30 dark:text-green-200 dark:border-green-800 mb-2">
                <i class="fas fa-heart"></i>
              </div>
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">48px × 48px</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">Comfortable</div>
            </div>
            <div class="text-center">
              <div class="inline-flex items-center justify-center w-14 h-14 bg-purple-100 text-purple-800 rounded-lg border border-purple-200 dark:bg-purple-900/30 dark:text-purple-200 dark:border-purple-800 mb-2">
                <i class="fas fa-star"></i>
              </div>
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">56px × 56px</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">Large targets</div>
            </div>
          </div>
        </div>

        <!-- Button Examples -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Mobile Buttons</h4>
          <div class="space-y-4">
            <div class="flex flex-wrap gap-4">
              <button class="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium min-h-[44px] hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700">
                Primary Action
              </button>
              <button class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium min-h-[44px] hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
                Secondary Action
              </button>
            </div>
            <button class="w-full px-4 py-3 bg-green-600 text-white rounded-lg font-medium min-h-[44px] hover:bg-green-700">
              Full Width Button
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mobile Navigation</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Bottom navigation and mobile-optimized menu patterns.
      </p>
      
      <div class="space-y-6">
        <!-- Bottom Navigation -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Bottom Navigation</h4>
          <div class="max-w-sm mx-auto border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden">
            <div class="bg-gray-50 dark:bg-gray-700 p-4 text-center text-sm">Content Area</div>
            <nav class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
              <div class="grid grid-cols-4 gap-1">
                <button class="flex flex-col items-center py-3 text-blue-600 dark:text-purple-400">
                  <i class="fas fa-home text-lg mb-1"></i>
                  <span class="text-xs">Home</span>
                </button>
                <button class="flex flex-col items-center py-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                  <i class="fas fa-search text-lg mb-1"></i>
                  <span class="text-xs">Search</span>
                </button>
                <button class="flex flex-col items-center py-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                  <i class="fas fa-chart-line text-lg mb-1"></i>
                  <span class="text-xs">Analytics</span>
                </button>
                <button class="flex flex-col items-center py-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                  <i class="fas fa-user text-lg mb-1"></i>
                  <span class="text-xs">Profile</span>
                </button>
              </div>
            </nav>
          </div>
        </div>

        <!-- Tab Navigation -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Mobile Tabs</h4>
          <nav class="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button class="flex-1 py-2 px-4 text-sm font-medium text-white bg-blue-600 rounded-md dark:bg-purple-600">
              Active
            </button>
            <button class="flex-1 py-2 px-4 text-sm font-medium text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100">
              Tab 2
            </button>
            <button class="flex-1 py-2 px-4 text-sm font-medium text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100">
              Tab 3
            </button>
          </nav>
        </div>
      </div>
    </div>

    <!-- Mobile Cards -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mobile Card Patterns</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Card layouts optimized for mobile screens with proper spacing and touch targets.
      </p>
      
      <div class="space-y-6">
        <!-- Stacked Cards -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Stacked Cards</h4>
          <div class="space-y-4 max-w-sm mx-auto">
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
              <div class="flex items-center justify-between mb-3">
                <h5 class="font-semibold text-gray-900 dark:text-gray-100">Arrow Setup #1</h5>
                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full dark:bg-green-900/30 dark:text-green-300">Complete</span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">Easton ACE 400 spine with 100gr points</p>
              <button class="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium dark:bg-purple-600">
                View Details
              </button>
            </div>
            
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
              <div class="flex items-center justify-between mb-3">
                <h5 class="font-semibold text-gray-900 dark:text-gray-100">Arrow Setup #2</h5>
                <span class="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full dark:bg-yellow-900/30 dark:text-yellow-300">In Progress</span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">Gold Tip Pierce 340 spine tuning</p>
              <button class="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium dark:bg-purple-600">
                Continue Setup
              </button>
            </div>
          </div>
        </div>

        <!-- Horizontal Scrolling Cards -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Horizontal Scroll</h4>
          <div class="overflow-x-auto">
            <div class="flex space-x-4 w-max">
              <div class="w-64 bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
                <h5 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Quick Stats</h5>
                <div class="text-2xl font-bold text-blue-600 dark:text-purple-400 mb-1">285 fps</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Arrow Speed</div>
              </div>
              
              <div class="w-64 bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
                <h5 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Energy</h5>
                <div class="text-2xl font-bold text-green-600 dark:text-green-400 mb-1">64.2 ft·lbs</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Kinetic Energy</div>
              </div>
              
              <div class="w-64 bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
                <h5 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Balance</h5>
                <div class="text-2xl font-bold text-purple-600 dark:text-purple-400 mb-1">12.8%</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">FOC</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Actions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mobile Action Patterns</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Action sheets, floating buttons, and mobile-optimized interaction patterns.
      </p>
      
      <div class="space-y-6">
        <!-- Action Sheet -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Action Sheet</h4>
          <div class="max-w-sm mx-auto">
            <div class="bg-white dark:bg-gray-800 rounded-t-2xl border border-gray-200 dark:border-gray-600 border-b-0">
              <div class="p-4 text-center border-b border-gray-200 dark:border-gray-700">
                <div class="w-12 h-1 bg-gray-300 dark:bg-gray-600 rounded-full mx-auto mb-3"></div>
                <h5 class="font-semibold text-gray-900 dark:text-gray-100">Choose Action</h5>
              </div>
              <div class="divide-y divide-gray-200 dark:divide-gray-700">
                <button class="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center">
                  <i class="fas fa-edit text-blue-600 dark:text-purple-400 mr-3"></i>
                  <span class="text-gray-900 dark:text-gray-100">Edit Setup</span>
                </button>
                <button class="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center">
                  <i class="fas fa-copy text-green-600 dark:text-green-400 mr-3"></i>
                  <span class="text-gray-900 dark:text-gray-100">Duplicate</span>
                </button>
                <button class="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center">
                  <i class="fas fa-share text-purple-600 dark:text-purple-400 mr-3"></i>
                  <span class="text-gray-900 dark:text-gray-100">Share</span>
                </button>
                <button class="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center text-red-600 dark:text-red-400">
                  <i class="fas fa-trash mr-3"></i>
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating Action Button -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Floating Action Button</h4>
          <div class="relative max-w-sm mx-auto h-32 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="absolute bottom-4 right-4">
              <button class="w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 flex items-center justify-center">
                <i class="fas fa-plus text-xl"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Swipe Actions -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Swipe Actions</h4>
          <div class="max-w-sm mx-auto bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden">
            <div class="p-4 bg-gradient-to-r from-transparent via-blue-50 to-blue-100 dark:from-transparent dark:via-blue-900/20 dark:to-blue-800/30 border-l-4 border-blue-500">
              <div class="flex items-center justify-between">
                <div>
                  <h5 class="font-semibold text-gray-900 dark:text-gray-100">Arrow Configuration</h5>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Swipe left to reveal actions</p>
                </div>
                <div class="text-xs text-blue-600 dark:text-blue-400">← Swipe</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Safe Areas -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Safe Area Considerations</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Layout considerations for modern mobile devices with notches and home indicators.
      </p>
      
      <div class="space-y-6">
        <!-- iPhone Safe Areas -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">iPhone Safe Areas</h4>
          <div class="max-w-sm mx-auto bg-black rounded-3xl p-2">
            <!-- Phone Frame -->
            <div class="bg-white dark:bg-gray-900 rounded-2xl overflow-hidden relative">
              <!-- Notch -->
              <div class="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-6 bg-black rounded-b-2xl z-10"></div>
              
              <!-- Content Area -->
              <div class="pt-8 pb-6 px-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
                  <div class="text-sm text-gray-900 dark:text-gray-100">Safe Area Content</div>
                  <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">Respects notch and home indicator</div>
                </div>
              </div>
              
              <!-- Home Indicator -->
              <div class="absolute bottom-2 left-1/2 transform -translate-x-1/2 w-32 h-1 bg-gray-400 rounded-full"></div>
            </div>
          </div>
        </div>

        <!-- Safe Area CSS -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">CSS Implementation</h4>
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <code class="text-sm text-gray-800 dark:text-gray-200">
              <div>/* Safe area padding */</div>
              <div>padding-top: env(safe-area-inset-top);</div>
              <div>padding-bottom: env(safe-area-inset-bottom);</div>
              <div>padding-left: env(safe-area-inset-left);</div>
              <div>padding-right: env(safe-area-inset-right);</div>
            </code>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Forms -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mobile Form Patterns</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Form layouts and input patterns optimized for mobile interaction.
      </p>
      
      <div class="space-y-6 max-w-sm mx-auto">
        <!-- Stacked Form -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Stacked Layout</h4>
          <form class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Arrow Length</label>
              <input type="number" placeholder="30" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Point Weight</label>
              <input type="number" placeholder="125" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Arrow Type</label>
              <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100">
                <option>Hunting</option>
                <option>Target</option>
                <option>3D</option>
              </select>
            </div>
            <button type="submit" class="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700">
              Calculate Performance
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Mobile patterns component
</script>

<style scoped>
/* Custom scrollbar for horizontal scroll */
.overflow-x-auto::-webkit-scrollbar {
  height: 4px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: theme('colors.gray.100');
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: theme('colors.gray.400');
  border-radius: 2px;
}

.dark .overflow-x-auto::-webkit-scrollbar-track {
  background: theme('colors.gray.700');
}

.dark .overflow-x-auto::-webkit-scrollbar-thumb {
  background: theme('colors.gray.500');
}
</style>