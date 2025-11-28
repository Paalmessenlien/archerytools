<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h2 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
        Archery Tools Design System
      </h2>
      <p class="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
        A comprehensive, mobile-first design system built with Vue 3, Tailwind CSS, and Material Design 3 principles.
        Optimized for archery professionals and enthusiasts.
      </p>
    </div>

    <!-- Key Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="text-center">
          <div class="text-3xl font-bold text-blue-600 dark:text-purple-400 mb-2">60+</div>
          <div class="text-sm text-gray-600 dark:text-gray-400">Vue Components</div>
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">100+</div>
          <div class="text-sm text-gray-600 dark:text-gray-400">Color Variables</div>
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="text-center">
          <div class="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">2</div>
          <div class="text-sm text-gray-600 dark:text-gray-400">Theme Modes</div>
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="text-center">
          <div class="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-2">Mobile</div>
          <div class="text-sm text-gray-600 dark:text-gray-400">First Design</div>
        </div>
      </div>
    </div>

    <!-- Technology Stack -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-8 border border-gray-200 dark:border-gray-700">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Technology Stack</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Frontend Framework -->
        <div class="space-y-4">
          <div class="flex items-center">
            <i class="fab fa-vuejs text-2xl text-green-500 mr-3"></i>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100">Frontend</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">Nuxt 3 + Vue 3 + TypeScript</p>
            </div>
          </div>
          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <li>• Composition API</li>
            <li>• Auto-imports</li>
            <li>• SSR/SPA modes</li>
            <li>• TypeScript support</li>
          </ul>
        </div>

        <!-- Styling -->
        <div class="space-y-4">
          <div class="flex items-center">
            <i class="fas fa-paint-brush text-2xl text-blue-500 mr-3"></i>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100">Styling</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">Tailwind CSS + Material Design 3</p>
            </div>
          </div>
          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <li>• Utility-first CSS</li>
            <li>• Dark mode support</li>
            <li>• Custom properties</li>
            <li>• Responsive design</li>
          </ul>
        </div>

        <!-- Components -->
        <div class="space-y-4">
          <div class="flex items-center">
            <i class="fas fa-cube text-2xl text-purple-500 mr-3"></i>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100">Components</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">Material Web + Custom Vue</p>
            </div>
          </div>
          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <li>• Material Design 3</li>
            <li>• Custom components</li>
            <li>• Accessibility focused</li>
            <li>• Mobile optimized</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Design Principles -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-8 border border-gray-200 dark:border-gray-700">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Design Principles</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="space-y-6">
          <!-- Mobile First -->
          <div class="flex items-start">
            <div class="flex-shrink-0 w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mr-4">
              <i class="fas fa-mobile-alt text-blue-600 dark:text-blue-400"></i>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Mobile First</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Designed primarily for mobile devices with enhanced touch targets and optimized layouts.
              </p>
            </div>
          </div>

          <!-- Accessibility -->
          <div class="flex items-start">
            <div class="flex-shrink-0 w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mr-4">
              <i class="fas fa-universal-access text-green-600 dark:text-green-400"></i>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Accessibility</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                WCAG 2.1 compliant with proper color contrast, keyboard navigation, and screen reader support.
              </p>
            </div>
          </div>

          <!-- Performance -->
          <div class="flex items-start">
            <div class="flex-shrink-0 w-10 h-10 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center mr-4">
              <i class="fas fa-tachometer-alt text-orange-600 dark:text-orange-400"></i>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Performance</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Optimized for fast loading with lazy-loaded components and efficient rendering.
              </p>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <!-- Consistency -->
          <div class="flex items-start">
            <div class="flex-shrink-0 w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mr-4">
              <i class="fas fa-equals text-purple-600 dark:text-purple-400"></i>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Consistency</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Unified design patterns and interactions across all components and pages.
              </p>
            </div>
          </div>

          <!-- Material Design -->
          <div class="flex items-start">
            <div class="flex-shrink-0 w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center mr-4">
              <i class="fab fa-google text-red-600 dark:text-red-400"></i>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Material Design 3</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Following Google's latest Material Design principles with dynamic color and improved theming.
              </p>
            </div>
          </div>

          <!-- Scalability -->
          <div class="flex items-start">
            <div class="flex-shrink-0 w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center mr-4">
              <i class="fas fa-expand-arrows-alt text-indigo-600 dark:text-indigo-400"></i>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Scalability</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Component-based architecture that scales from simple apps to complex enterprise solutions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Start -->
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-8 border border-blue-200 dark:border-blue-800">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Quick Start</h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Use the navigation above to explore different sections of the design system:
      </p>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button class="flex items-center justify-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
          <div class="text-center">
            <i class="fas fa-palette text-2xl text-blue-600 dark:text-purple-400 mb-2"></i>
            <div class="text-sm font-medium">Colors</div>
          </div>
        </button>
        <button class="flex items-center justify-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
          <div class="text-center">
            <i class="fas fa-font text-2xl text-green-600 dark:text-green-400 mb-2"></i>
            <div class="text-sm font-medium">Typography</div>
          </div>
        </button>
        <button class="flex items-center justify-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
          <div class="text-center">
            <i class="fas fa-cube text-2xl text-purple-600 dark:text-purple-400 mb-2"></i>
            <div class="text-sm font-medium">Components</div>
          </div>
        </button>
        <button class="flex items-center justify-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
          <div class="text-center">
            <i class="fas fa-mobile-alt text-2xl text-orange-600 dark:text-orange-400 mb-2"></i>
            <div class="text-sm font-medium">Mobile</div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// This component provides an overview of the design system
</script>