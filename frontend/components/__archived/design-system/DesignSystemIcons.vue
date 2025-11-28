<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Icon Library</h2>
      <p class="text-gray-600 dark:text-gray-400">
        FontAwesome icons used throughout the Archery Tools application with usage guidelines.
      </p>
    </div>

    <!-- Icon Categories -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Icon Categories</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Icons organized by functional categories and usage contexts.
      </p>
      
      <div class="space-y-8">
        <!-- Navigation Icons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-4">Navigation & Interface</h4>
          <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-4">
            <div v-for="icon in navigationIcons" :key="icon.name" class="text-center group">
              <div class="flex items-center justify-center w-12 h-12 bg-gray-50 hover:bg-blue-50 dark:bg-gray-700 dark:hover:bg-blue-900/20 rounded-lg border border-gray-200 dark:border-gray-600 mb-2 transition-colors">
                <i :class="icon.class" class="text-lg text-gray-700 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400"></i>
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 truncate">{{ icon.name }}</div>
            </div>
          </div>
        </div>

        <!-- Archery Specific Icons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-4">Archery & Sports</h4>
          <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-4">
            <div v-for="icon in archeryIcons" :key="icon.name" class="text-center group">
              <div class="flex items-center justify-center w-12 h-12 bg-gray-50 hover:bg-green-50 dark:bg-gray-700 dark:hover:bg-green-900/20 rounded-lg border border-gray-200 dark:border-gray-600 mb-2 transition-colors">
                <i :class="icon.class" class="text-lg text-gray-700 dark:text-gray-300 group-hover:text-green-600 dark:group-hover:text-green-400"></i>
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 truncate">{{ icon.name }}</div>
            </div>
          </div>
        </div>

        <!-- Data & Analytics Icons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-4">Data & Analytics</h4>
          <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-4">
            <div v-for="icon in dataIcons" :key="icon.name" class="text-center group">
              <div class="flex items-center justify-center w-12 h-12 bg-gray-50 hover:bg-purple-50 dark:bg-gray-700 dark:hover:bg-purple-900/20 rounded-lg border border-gray-200 dark:border-gray-600 mb-2 transition-colors">
                <i :class="icon.class" class="text-lg text-gray-700 dark:text-gray-300 group-hover:text-purple-600 dark:group-hover:text-purple-400"></i>
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 truncate">{{ icon.name }}</div>
            </div>
          </div>
        </div>

        <!-- Status & Feedback Icons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-4">Status & Feedback</h4>
          <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-4">
            <div v-for="icon in statusIcons" :key="icon.name" class="text-center group">
              <div class="flex items-center justify-center w-12 h-12 bg-gray-50 hover:bg-orange-50 dark:bg-gray-700 dark:hover:bg-orange-900/20 rounded-lg border border-gray-200 dark:border-gray-600 mb-2 transition-colors">
                <i :class="[icon.class, getStatusColor(icon.type)]" class="text-lg"></i>
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 truncate">{{ icon.name }}</div>
            </div>
          </div>
        </div>

        <!-- Actions & Tools Icons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-4">Actions & Tools</h4>
          <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-4">
            <div v-for="icon in actionIcons" :key="icon.name" class="text-center group">
              <div class="flex items-center justify-center w-12 h-12 bg-gray-50 hover:bg-indigo-50 dark:bg-gray-700 dark:hover:bg-indigo-900/20 rounded-lg border border-gray-200 dark:border-gray-600 mb-2 transition-colors">
                <i :class="icon.class" class="text-lg text-gray-700 dark:text-gray-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400"></i>
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 truncate">{{ icon.name }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Icon Sizes -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Icon Sizes</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Standardized icon sizes for different contexts and use cases.
      </p>
      
      <div class="space-y-6">
        <!-- Size Examples -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div class="text-center">
            <div class="flex items-center justify-center mb-3">
              <i class="fas fa-crosshairs text-xs text-blue-600 dark:text-blue-400"></i>
            </div>
            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">Extra Small</div>
            <div class="text-xs text-gray-600 dark:text-gray-400">text-xs (12px)</div>
          </div>
          
          <div class="text-center">
            <div class="flex items-center justify-center mb-3">
              <i class="fas fa-crosshairs text-sm text-green-600 dark:text-green-400"></i>
            </div>
            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">Small</div>
            <div class="text-xs text-gray-600 dark:text-gray-400">text-sm (14px)</div>
          </div>
          
          <div class="text-center">
            <div class="flex items-center justify-center mb-3">
              <i class="fas fa-crosshairs text-base text-purple-600 dark:text-purple-400"></i>
            </div>
            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">Base</div>
            <div class="text-xs text-gray-600 dark:text-gray-400">text-base (16px)</div>
          </div>
          
          <div class="text-center">
            <div class="flex items-center justify-center mb-3">
              <i class="fas fa-crosshairs text-lg text-orange-600 dark:text-orange-400"></i>
            </div>
            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">Large</div>
            <div class="text-xs text-gray-600 dark:text-gray-400">text-lg (18px)</div>
          </div>
        </div>

        <!-- Size Guidelines -->
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Size Guidelines</h4>
          <div class="text-sm text-blue-700 dark:text-blue-300 space-y-1">
            <div>• <strong>text-xs</strong>: Inline text icons, small buttons</div>
            <div>• <strong>text-sm</strong>: Standard buttons, form controls</div>
            <div>• <strong>text-base</strong>: Navigation icons, cards</div>
            <div>• <strong>text-lg</strong>: Headers, large buttons, mobile nav</div>
            <div>• <strong>text-xl+</strong>: Hero icons, empty states</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Icon Colors -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Icon Colors</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Semantic color usage for icons in different contexts and states.
      </p>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <!-- Primary Colors -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Primary</h4>
          <div class="space-y-3">
            <div class="flex items-center">
              <i class="fas fa-home text-blue-600 dark:text-purple-400 mr-3"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">blue-600 / purple-400</span>
            </div>
            <div class="flex items-center">
              <i class="fas fa-star text-blue-500 dark:text-purple-300 mr-3"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">blue-500 / purple-300</span>
            </div>
          </div>
        </div>

        <!-- Success Colors -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Success</h4>
          <div class="space-y-3">
            <div class="flex items-center">
              <i class="fas fa-check-circle text-green-600 dark:text-green-400 mr-3"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">green-600 / green-400</span>
            </div>
            <div class="flex items-center">
              <i class="fas fa-shield-alt text-green-500 dark:text-green-300 mr-3"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">green-500 / green-300</span>
            </div>
          </div>
        </div>

        <!-- Warning Colors -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Warning</h4>
          <div class="space-y-3">
            <div class="flex items-center">
              <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 mr-3"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">yellow-600 / yellow-400</span>
            </div>
            <div class="flex items-center">
              <i class="fas fa-clock text-orange-600 dark:text-orange-400 mr-3"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">orange-600 / orange-400</span>
            </div>
          </div>
        </div>

        <!-- Error Colors -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Error</h4>
          <div class="space-y-3">
            <div class="flex items-center">
              <i class="fas fa-times-circle text-red-600 dark:text-red-400 mr-3"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">red-600 / red-400</span>
            </div>
            <div class="flex items-center">
              <i class="fas fa-exclamation-circle text-red-500 dark:text-red-300 mr-3"></i>
              <span class="text-sm text-gray-700 dark:text-gray-300">red-500 / red-300</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Usage Examples -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Usage Examples</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Real-world examples of icon usage in different UI contexts.
      </p>
      
      <div class="space-y-6">
        <!-- Buttons with Icons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Buttons with Icons</h4>
          <div class="flex flex-wrap gap-4">
            <button class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700">
              <i class="fas fa-plus mr-2"></i>
              Add Arrow
            </button>
            <button class="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
              <i class="fas fa-download mr-2"></i>
              Export Data
            </button>
            <button class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
              <i class="fas fa-calculator mr-2"></i>
              Calculate
            </button>
          </div>
        </div>

        <!-- Navigation with Icons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Navigation Items</h4>
          <nav class="space-y-2">
            <a href="#" class="flex items-center p-3 text-blue-600 bg-blue-50 rounded-lg dark:text-purple-400 dark:bg-purple-900/20">
              <i class="fas fa-home mr-3"></i>
              <span>Dashboard</span>
            </a>
            <a href="#" class="flex items-center p-3 text-gray-700 hover:bg-gray-50 rounded-lg dark:text-gray-300 dark:hover:bg-gray-700">
              <i class="fas fa-crosshairs mr-3"></i>
              <span>Arrow Database</span>
            </a>
            <a href="#" class="flex items-center p-3 text-gray-700 hover:bg-gray-50 rounded-lg dark:text-gray-300 dark:hover:bg-gray-700">
              <i class="fas fa-chart-line mr-3"></i>
              <span>Performance</span>
            </a>
          </nav>
        </div>

        <!-- Status Indicators -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Status Indicators</h4>
          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg dark:bg-green-900/20 dark:border-green-800">
              <div class="flex items-center">
                <i class="fas fa-check-circle text-green-600 dark:text-green-400 mr-3"></i>
                <span class="text-green-800 dark:text-green-200">Setup Complete</span>
              </div>
            </div>
            <div class="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg dark:bg-yellow-900/20 dark:border-yellow-800">
              <div class="flex items-center">
                <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 mr-3"></i>
                <span class="text-yellow-800 dark:text-yellow-200">Needs Attention</span>
              </div>
            </div>
            <div class="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg dark:bg-red-900/20 dark:border-red-800">
              <div class="flex items-center">
                <i class="fas fa-times-circle text-red-600 dark:text-red-400 mr-3"></i>
                <span class="text-red-800 dark:text-red-200">Error Occurred</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Icon data
const navigationIcons = [
  { name: 'Home', class: 'fas fa-home' },
  { name: 'Menu', class: 'fas fa-bars' },
  { name: 'Search', class: 'fas fa-search' },
  { name: 'Settings', class: 'fas fa-cog' },
  { name: 'User', class: 'fas fa-user' },
  { name: 'Back', class: 'fas fa-arrow-left' },
  { name: 'Next', class: 'fas fa-arrow-right' },
  { name: 'Close', class: 'fas fa-times' },
  { name: 'More', class: 'fas fa-ellipsis-v' },
  { name: 'Bookmark', class: 'fas fa-bookmark' }
]

const archeryIcons = [
  { name: 'Target', class: 'fas fa-crosshairs' },
  { name: 'Bullseye', class: 'fas fa-bullseye' },
  { name: 'Trophy', class: 'fas fa-trophy' },
  { name: 'Medal', class: 'fas fa-medal' },
  { name: 'Star', class: 'fas fa-star' },
  { name: 'Award', class: 'fas fa-award' },
  { name: 'Crown', class: 'fas fa-crown' },
  { name: 'Flame', class: 'fas fa-fire' },
  { name: 'Lightning', class: 'fas fa-bolt' },
  { name: 'Shield', class: 'fas fa-shield-alt' }
]

const dataIcons = [
  { name: 'Chart Line', class: 'fas fa-chart-line' },
  { name: 'Chart Bar', class: 'fas fa-chart-bar' },
  { name: 'Analytics', class: 'fas fa-chart-pie' },
  { name: 'Database', class: 'fas fa-database' },
  { name: 'Table', class: 'fas fa-table' },
  { name: 'List', class: 'fas fa-list' },
  { name: 'Filter', class: 'fas fa-filter' },
  { name: 'Sort', class: 'fas fa-sort' },
  { name: 'Calculator', class: 'fas fa-calculator' },
  { name: 'Ruler', class: 'fas fa-ruler' }
]

const statusIcons = [
  { name: 'Success', class: 'fas fa-check-circle', type: 'success' },
  { name: 'Warning', class: 'fas fa-exclamation-triangle', type: 'warning' },
  { name: 'Error', class: 'fas fa-times-circle', type: 'error' },
  { name: 'Info', class: 'fas fa-info-circle', type: 'info' },
  { name: 'Question', class: 'fas fa-question-circle', type: 'info' },
  { name: 'Loading', class: 'fas fa-spinner', type: 'info' },
  { name: 'Clock', class: 'fas fa-clock', type: 'warning' },
  { name: 'Bell', class: 'fas fa-bell', type: 'warning' },
  { name: 'Heart', class: 'fas fa-heart', type: 'error' },
  { name: 'Thumbs Up', class: 'fas fa-thumbs-up', type: 'success' }
]

const actionIcons = [
  { name: 'Edit', class: 'fas fa-edit' },
  { name: 'Delete', class: 'fas fa-trash' },
  { name: 'Copy', class: 'fas fa-copy' },
  { name: 'Share', class: 'fas fa-share' },
  { name: 'Download', class: 'fas fa-download' },
  { name: 'Upload', class: 'fas fa-upload' },
  { name: 'Save', class: 'fas fa-save' },
  { name: 'Print', class: 'fas fa-print' },
  { name: 'Refresh', class: 'fas fa-sync' },
  { name: 'Plus', class: 'fas fa-plus' }
]

// Helper method for status colors
const getStatusColor = (type) => {
  const colors = {
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    error: 'text-red-600 dark:text-red-400',
    info: 'text-blue-600 dark:text-blue-400'
  }
  return colors[type] || 'text-gray-600 dark:text-gray-400'
}
</script>