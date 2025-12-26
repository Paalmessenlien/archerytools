<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Color System</h2>
      <p class="text-gray-600 dark:text-gray-400">
        Comprehensive color palette with light and dark mode support, following Material Design 3 principles.
      </p>
    </div>

    <!-- Primary Colors -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Primary Colors</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Blue for light mode, Purple for dark mode. Used for primary actions and emphasis.
      </p>
      
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div v-for="shade in primaryColors" :key="shade.name" class="text-center">
          <div 
            :class="shade.class"
            :style="{ backgroundColor: shade.hex }"
            class="h-20 rounded-lg mb-2 border border-gray-200 dark:border-gray-600"
          ></div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ shade.name }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">{{ shade.hex }}</div>
        </div>
      </div>
    </div>

    <!-- Semantic Colors -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Semantic Colors</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Colors with specific meanings for success, warning, error, and info states.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <!-- Success -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Success</h4>
          <div class="space-y-2">
            <div v-for="shade in successColors" :key="shade.name" class="flex items-center justify-between">
              <div class="flex items-center">
                <div 
                  :style="{ backgroundColor: shade.hex }"
                  class="w-6 h-6 rounded border border-gray-200 dark:border-gray-600 mr-3"
                ></div>
                <span class="text-sm text-gray-900 dark:text-gray-100">{{ shade.name }}</span>
              </div>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ shade.hex }}</span>
            </div>
          </div>
        </div>

        <!-- Warning -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Warning</h4>
          <div class="space-y-2">
            <div v-for="shade in warningColors" :key="shade.name" class="flex items-center justify-between">
              <div class="flex items-center">
                <div 
                  :style="{ backgroundColor: shade.hex }"
                  class="w-6 h-6 rounded border border-gray-200 dark:border-gray-600 mr-3"
                ></div>
                <span class="text-sm text-gray-900 dark:text-gray-100">{{ shade.name }}</span>
              </div>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ shade.hex }}</span>
            </div>
          </div>
        </div>

        <!-- Error -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Error</h4>
          <div class="space-y-2">
            <div v-for="shade in errorColors" :key="shade.name" class="flex items-center justify-between">
              <div class="flex items-center">
                <div 
                  :style="{ backgroundColor: shade.hex }"
                  class="w-6 h-6 rounded border border-gray-200 dark:border-gray-600 mr-3"
                ></div>
                <span class="text-sm text-gray-900 dark:text-gray-100">{{ shade.name }}</span>
              </div>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ shade.hex }}</span>
            </div>
          </div>
        </div>

        <!-- Info -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Info</h4>
          <div class="space-y-2">
            <div v-for="shade in infoColors" :key="shade.name" class="flex items-center justify-between">
              <div class="flex items-center">
                <div 
                  :style="{ backgroundColor: shade.hex }"
                  class="w-6 h-6 rounded border border-gray-200 dark:border-gray-600 mr-3"
                ></div>
                <span class="text-sm text-gray-900 dark:text-gray-100">{{ shade.name }}</span>
              </div>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ shade.hex }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Neutral Colors -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Neutral Colors</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Gray scale colors used for text, backgrounds, and borders in both light and dark modes.
      </p>
      
      <div class="grid grid-cols-2 md:grid-cols-10 gap-3">
        <div v-for="shade in neutralColors" :key="shade.name" class="text-center">
          <div 
            :style="{ backgroundColor: shade.hex }"
            class="h-16 rounded-lg mb-2 border border-gray-200 dark:border-gray-600"
          ></div>
          <div class="text-xs font-medium text-gray-900 dark:text-gray-100">{{ shade.name }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">{{ shade.hex }}</div>
        </div>
      </div>
    </div>

    <!-- Gradients -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Gradients</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Commonly used gradient combinations for backgrounds and visual elements.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="gradient in gradients" :key="gradient.name">
          <div 
            :class="gradient.class"
            class="h-24 rounded-lg mb-2 border border-gray-200 dark:border-gray-600"
          ></div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ gradient.name }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">{{ gradient.class }}</div>
        </div>
      </div>
    </div>

    <!-- Usage Examples -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Usage Examples</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Examples of how colors are applied in real components.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Buttons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Buttons</h4>
          <div class="space-y-3">
            <button class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700">
              Primary Button
            </button>
            <button class="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
              Success Button
            </button>
            <button class="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
              Error Button
            </button>
            <button class="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600">
              Secondary Button
            </button>
          </div>
        </div>

        <!-- Cards -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Cards</h4>
          <div class="space-y-3">
            <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-900/20 dark:border-blue-800">
              <div class="text-sm font-medium text-blue-800 dark:text-blue-200">Info Card</div>
              <div class="text-xs text-blue-600 dark:text-blue-300">Information message</div>
            </div>
            <div class="p-4 bg-green-50 border border-green-200 rounded-lg dark:bg-green-900/20 dark:border-green-800">
              <div class="text-sm font-medium text-green-800 dark:text-green-200">Success Card</div>
              <div class="text-xs text-green-600 dark:text-green-300">Success message</div>
            </div>
            <div class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg dark:bg-yellow-900/20 dark:border-yellow-800">
              <div class="text-sm font-medium text-yellow-800 dark:text-yellow-200">Warning Card</div>
              <div class="text-xs text-yellow-600 dark:text-yellow-300">Warning message</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Color data
const primaryColors = [
  { name: 'Blue 50', hex: '#eff6ff', class: 'bg-blue-50' },
  { name: 'Blue 500', hex: '#3b82f6', class: 'bg-blue-500' },
  { name: 'Blue 600', hex: '#2563eb', class: 'bg-blue-600' },
  { name: 'Purple 500', hex: '#8b5cf6', class: 'bg-purple-500' },
  { name: 'Purple 600', hex: '#7c3aed', class: 'bg-purple-600' }
]

const successColors = [
  { name: 'Green 50', hex: '#f0fdf4' },
  { name: 'Green 500', hex: '#22c55e' },
  { name: 'Green 600', hex: '#16a34a' },
  { name: 'Green 800', hex: '#166534' }
]

const warningColors = [
  { name: 'Yellow 50', hex: '#fefce8' },
  { name: 'Orange 500', hex: '#f97316' },
  { name: 'Orange 600', hex: '#ea580c' },
  { name: 'Orange 800', hex: '#9a3412' }
]

const errorColors = [
  { name: 'Red 50', hex: '#fef2f2' },
  { name: 'Red 500', hex: '#ef4444' },
  { name: 'Red 600', hex: '#dc2626' },
  { name: 'Red 800', hex: '#991b1b' }
]

const infoColors = [
  { name: 'Blue 50', hex: '#eff6ff' },
  { name: 'Blue 500', hex: '#3b82f6' },
  { name: 'Blue 600', hex: '#2563eb' },
  { name: 'Blue 800', hex: '#1e40af' }
]

const neutralColors = [
  { name: 'Gray 50', hex: '#f9fafb' },
  { name: 'Gray 100', hex: '#f3f4f6' },
  { name: 'Gray 200', hex: '#e5e7eb' },
  { name: 'Gray 300', hex: '#d1d5db' },
  { name: 'Gray 400', hex: '#9ca3af' },
  { name: 'Gray 500', hex: '#6b7280' },
  { name: 'Gray 600', hex: '#4b5563' },
  { name: 'Gray 700', hex: '#374151' },
  { name: 'Gray 800', hex: '#1f2937' },
  { name: 'Gray 900', hex: '#111827' }
]

const gradients = [
  { name: 'Primary Gradient', class: 'bg-gradient-to-r from-blue-500 to-purple-600' },
  { name: 'Success Gradient', class: 'bg-gradient-to-r from-green-400 to-blue-500' },
  { name: 'Warning Gradient', class: 'bg-gradient-to-r from-yellow-400 to-orange-500' },
  { name: 'Sunset Gradient', class: 'bg-gradient-to-r from-orange-400 to-red-500' },
  { name: 'Ocean Gradient', class: 'bg-gradient-to-r from-blue-400 to-cyan-500' },
  { name: 'Forest Gradient', class: 'bg-gradient-to-r from-green-400 to-green-600' }
]
</script>