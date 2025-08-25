<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Layout System</h2>
      <p class="text-gray-600 dark:text-gray-400">
        Grid systems, spacing utilities, containers, and responsive layout patterns.
      </p>
    </div>

    <!-- Container System -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Container System</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Mobile-first container classes for consistent content width and spacing.
      </p>
      
      <div class="space-y-6">
        <!-- Standard Container -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Standard Container</h4>
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div class="bg-blue-100 dark:bg-blue-800/30 rounded p-4 text-center">
                <code class="text-sm">max-w-7xl mx-auto px-4 sm:px-6 lg:px-8</code>
              </div>
            </div>
          </div>
        </div>

        <!-- Mobile Container -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Mobile Container</h4>
          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <div class="mobile-container">
              <div class="bg-green-100 dark:bg-green-800/30 rounded p-4 text-center">
                <code class="text-sm">mobile-container class</code>
              </div>
            </div>
          </div>
        </div>

        <!-- Minimal Container -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Minimal Container</h4>
          <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
            <div class="mobile-container-minimal">
              <div class="bg-purple-100 dark:bg-purple-800/30 rounded p-4 text-center">
                <code class="text-sm">mobile-container-minimal class</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Grid System -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Grid System</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Responsive grid layouts using CSS Grid and Flexbox utilities.
      </p>
      
      <div class="space-y-8">
        <!-- 12 Column Grid -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">12 Column Grid</h4>
          <div class="grid grid-cols-12 gap-4">
            <div v-for="i in 12" :key="i" class="bg-blue-100 dark:bg-blue-800/30 rounded p-2 text-center text-sm">{{ i }}</div>
          </div>
        </div>

        <!-- Responsive Columns -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Responsive Columns</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div class="bg-green-100 dark:bg-green-800/30 rounded p-4 text-center">
              <div class="text-sm font-medium">1 column</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">mobile</div>
            </div>
            <div class="bg-green-100 dark:bg-green-800/30 rounded p-4 text-center">
              <div class="text-sm font-medium">2 columns</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">tablet</div>
            </div>
            <div class="bg-green-100 dark:bg-green-800/30 rounded p-4 text-center">
              <div class="text-sm font-medium">3 columns</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">desktop</div>
            </div>
            <div class="bg-green-100 dark:bg-green-800/30 rounded p-4 text-center">
              <div class="text-sm font-medium">4 columns</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">large</div>
            </div>
          </div>
        </div>

        <!-- Card Grid -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Card Grid</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
              <h5 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Card 1</h5>
              <p class="text-sm text-gray-600 dark:text-gray-400">Content for first card in the grid layout.</p>
            </div>
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
              <h5 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Card 2</h5>
              <p class="text-sm text-gray-600 dark:text-gray-400">Content for second card in the grid layout.</p>
            </div>
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
              <h5 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Card 3</h5>
              <p class="text-sm text-gray-600 dark:text-gray-400">Content for third card in the grid layout.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Spacing System -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Spacing System</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Consistent spacing scale based on a 4px grid system.
      </p>
      
      <div class="space-y-6">
        <!-- Padding Scale -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Padding Scale</h4>
          <div class="space-y-2">
            <div v-for="space in paddingScale" :key="space.name" class="flex items-center">
              <div class="w-16 text-sm text-gray-600 dark:text-gray-400">{{ space.name }}</div>
              <div :class="space.class" class="bg-blue-100 dark:bg-blue-800/30 border border-blue-300 dark:border-blue-700">
                <div class="bg-blue-200 dark:bg-blue-700">{{ space.size }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Margin Scale -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Margin Scale</h4>
          <div class="space-y-2">
            <div v-for="space in marginScale" :key="space.name" class="flex items-center">
              <div class="w-16 text-sm text-gray-600 dark:text-gray-400">{{ space.name }}</div>
              <div class="bg-orange-100 dark:bg-orange-800/30 border border-orange-300 dark:border-orange-700">
                <div :class="space.class" class="bg-orange-200 dark:bg-orange-700 px-2 py-1 text-xs">{{ space.size }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gap Scale -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Gap Scale</h4>
          <div class="space-y-4">
            <div v-for="gap in gapScale" :key="gap.name" class="space-y-2">
              <div class="text-sm text-gray-600 dark:text-gray-400">{{ gap.name }} ({{ gap.size }})</div>
              <div :class="`flex ${gap.class}`">
                <div class="bg-green-200 dark:bg-green-800 rounded px-3 py-2 text-xs">Item 1</div>
                <div class="bg-green-200 dark:bg-green-800 rounded px-3 py-2 text-xs">Item 2</div>
                <div class="bg-green-200 dark:bg-green-800 rounded px-3 py-2 text-xs">Item 3</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Z-Index Layers -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Z-Index Layers</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Systematic z-index values for proper layering and stacking context.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Layer Stack</h4>
          <div class="space-y-2">
            <div v-for="layer in zIndexLayers" :key="layer.name" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded border">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ layer.name }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">z-{{ layer.value }}</div>
            </div>
          </div>
        </div>
        
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Visual Example</h4>
          <div class="relative h-32 bg-gray-100 dark:bg-gray-700 rounded overflow-hidden">
            <div class="absolute inset-x-0 bottom-0 h-8 bg-blue-200 dark:bg-blue-800 z-0 flex items-center justify-center text-xs">Base (z-0)</div>
            <div class="absolute bottom-4 left-4 w-16 h-16 bg-green-300 dark:bg-green-700 z-10 rounded flex items-center justify-center text-xs">z-10</div>
            <div class="absolute bottom-8 left-8 w-16 h-16 bg-yellow-300 dark:bg-yellow-700 z-20 rounded flex items-center justify-center text-xs">z-20</div>
            <div class="absolute bottom-12 left-12 w-16 h-16 bg-red-300 dark:bg-red-700 z-30 rounded flex items-center justify-center text-xs">z-30</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Responsive Breakpoints -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Responsive Breakpoints</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Mobile-first breakpoint system optimized for all device sizes.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Standard Breakpoints</h4>
          <div class="space-y-3">
            <div v-for="breakpoint in standardBreakpoints" :key="breakpoint.name" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ breakpoint.name }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">{{ breakpoint.size }}</div>
            </div>
          </div>
        </div>
        
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Mobile Breakpoints</h4>
          <div class="space-y-3">
            <div v-for="breakpoint in mobileBreakpoints" :key="breakpoint.name" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ breakpoint.name }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">{{ breakpoint.size }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Layout Patterns -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Common Layout Patterns</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Frequently used layout combinations and patterns.
      </p>
      
      <div class="space-y-8">
        <!-- Header-Content-Footer -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Header-Content-Footer</h4>
          <div class="border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden">
            <div class="bg-blue-100 dark:bg-blue-800/30 p-4 text-center text-sm font-medium">Header</div>
            <div class="bg-gray-50 dark:bg-gray-700 p-8 text-center text-sm">Main Content Area</div>
            <div class="bg-gray-100 dark:bg-gray-600 p-4 text-center text-sm font-medium">Footer</div>
          </div>
        </div>

        <!-- Sidebar Layout -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Sidebar Layout</h4>
          <div class="border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden">
            <div class="grid grid-cols-1 lg:grid-cols-4 min-h-32">
              <div class="bg-purple-100 dark:bg-purple-800/30 p-4 text-center text-sm font-medium">Sidebar</div>
              <div class="lg:col-span-3 bg-gray-50 dark:bg-gray-700 p-4 text-center text-sm">Main Content</div>
            </div>
          </div>
        </div>

        <!-- Card Grid Layout -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Card Grid Layout</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 text-center text-sm">Card 1</div>
            <div class="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 text-center text-sm">Card 2</div>
            <div class="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 text-center text-sm">Card 3</div>
            <div class="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 text-center text-sm">Card 4</div>
            <div class="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 text-center text-sm">Card 5</div>
            <div class="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 text-center text-sm">Card 6</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Data for spacing examples
const paddingScale = [
  { name: 'p-1', size: '4px', class: 'p-1' },
  { name: 'p-2', size: '8px', class: 'p-2' },
  { name: 'p-3', size: '12px', class: 'p-3' },
  { name: 'p-4', size: '16px', class: 'p-4' },
  { name: 'p-6', size: '24px', class: 'p-6' },
  { name: 'p-8', size: '32px', class: 'p-8' }
]

const marginScale = [
  { name: 'm-1', size: '4px', class: 'm-1' },
  { name: 'm-2', size: '8px', class: 'm-2' },
  { name: 'm-3', size: '12px', class: 'm-3' },
  { name: 'm-4', size: '16px', class: 'm-4' },
  { name: 'm-6', size: '24px', class: 'm-6' },
  { name: 'm-8', size: '32px', class: 'm-8' }
]

const gapScale = [
  { name: 'gap-1', size: '4px', class: 'gap-1' },
  { name: 'gap-2', size: '8px', class: 'gap-2' },
  { name: 'gap-4', size: '16px', class: 'gap-4' },
  { name: 'gap-6', size: '24px', class: 'gap-6' }
]

const zIndexLayers = [
  { name: 'Maximum (Tooltips)', value: '9999' },
  { name: 'Overlay (Modals)', value: '1000' },
  { name: 'Dropdown', value: '100' },
  { name: 'Sticky Header', value: '40' },
  { name: 'Fixed Elements', value: '30' },
  { name: 'Floating Elements', value: '20' },
  { name: 'Elevated Content', value: '10' },
  { name: 'Base Layer', value: '0' }
]

const standardBreakpoints = [
  { name: 'xs', size: '0px (default)' },
  { name: 'sm', size: '640px' },
  { name: 'md', size: '768px' },
  { name: 'lg', size: '1024px' },
  { name: 'xl', size: '1280px' },
  { name: '2xl', size: '1536px' }
]

const mobileBreakpoints = [
  { name: 'xs-mobile', size: '320px (iPhone SE)' },
  { name: 'sm-mobile', size: '375px (iPhone)' },
  { name: 'md-mobile', size: '414px (iPhone Plus)' },
  { name: 'lg-mobile', size: '428px (iPhone Pro Max)' }
]
</script>

<style scoped>
/* Mobile Container Classes */
.mobile-container {
  max-width: 100%;
  padding-left: 1rem;
  padding-right: 1rem;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 640px) {
  .mobile-container {
    max-width: 640px;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}

@media (min-width: 1024px) {
  .mobile-container {
    max-width: 1024px;
    padding-left: 2rem;
    padding-right: 2rem;
  }
}

.mobile-container-minimal {
  max-width: 100%;
  padding-left: 0.75rem;
  padding-right: 0.75rem;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 640px) {
  .mobile-container-minimal {
    max-width: 640px;
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>