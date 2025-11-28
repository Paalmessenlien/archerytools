<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Animations & Transitions</h2>
      <p class="text-gray-600 dark:text-gray-400">
        Motion design system with transitions, animations, and micro-interactions.
      </p>
    </div>

    <!-- Transition Timing -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Transition Timing</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Standardized durations and easing curves for consistent motion design.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Duration Scale -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Duration Scale</h4>
          <div class="space-y-3">
            <div v-for="duration in durations" :key="duration.name" class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ duration.name }}</span>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ duration.value }}</span>
            </div>
          </div>
        </div>

        <!-- Easing Functions -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Easing Curves</h4>
          <div class="space-y-3">
            <div v-for="easing in easingFunctions" :key="easing.name" class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ easing.name }}</span>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ easing.value }}</span>
            </div>
          </div>
        </div>

        <!-- Usage Guidelines -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Usage</h4>
          <div class="text-sm text-gray-600 dark:text-gray-400 space-y-2">
            <div>• <strong>Fast</strong>: Hover states, focus</div>
            <div>• <strong>Base</strong>: Button interactions</div>
            <div>• <strong>Slow</strong>: Page transitions</div>
            <div>• <strong>Slower</strong>: Complex animations</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Animations -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Loading Animations</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Various loading states and progress indicators for different contexts.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <!-- Spinner -->
        <div class="text-center">
          <div class="flex justify-center mb-4">
            <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent dark:border-purple-500"></div>
          </div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Spinner</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">Standard loading indicator</p>
        </div>

        <!-- Dots -->
        <div class="text-center">
          <div class="flex justify-center space-x-1 mb-4">
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce dark:bg-purple-500"></div>
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce dark:bg-purple-500" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce dark:bg-purple-500" style="animation-delay: 0.2s"></div>
          </div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Bouncing Dots</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">Playful loading animation</p>
        </div>

        <!-- Progress Bar -->
        <div class="text-center">
          <div class="mb-4">
            <div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
              <div class="bg-blue-600 h-2 rounded-full progress-bar dark:bg-purple-600"></div>
            </div>
          </div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Progress Bar</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">Determinate progress</p>
        </div>

        <!-- Pulse -->
        <div class="text-center">
          <div class="flex justify-center mb-4">
            <div class="w-8 h-8 bg-blue-500 rounded-full animate-pulse dark:bg-purple-500"></div>
          </div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Pulse</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">Subtle loading state</p>
        </div>
      </div>
    </div>

    <!-- Button Interactions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Button Interactions</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Interactive button states with hover, focus, and press animations.
      </p>
      
      <div class="space-y-6">
        <!-- Hover Effects -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Hover Effects</h4>
          <div class="flex flex-wrap gap-4">
            <button class="px-4 py-2 bg-blue-600 text-white rounded-lg transition-all duration-200 hover:bg-blue-700 hover:shadow-lg hover:-translate-y-0.5 dark:bg-purple-600 dark:hover:bg-purple-700">
              Lift on Hover
            </button>
            <button class="px-4 py-2 bg-green-600 text-white rounded-lg transition-all duration-200 hover:bg-green-700 hover:scale-105">
              Scale on Hover
            </button>
            <button class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg transition-all duration-200 hover:border-blue-500 hover:text-blue-600 dark:border-gray-600 dark:text-gray-300 dark:hover:border-purple-400 dark:hover:text-purple-400">
              Color Change
            </button>
          </div>
        </div>

        <!-- Focus States -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Focus States</h4>
          <div class="flex flex-wrap gap-4">
            <button class="px-4 py-2 bg-blue-600 text-white rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:bg-purple-600 dark:focus:ring-purple-400">
              Focus Ring
            </button>
            <button class="px-4 py-2 bg-green-600 text-white rounded-lg transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-green-200 dark:focus:ring-green-800">
              Large Focus Ring
            </button>
          </div>
        </div>

        <!-- Loading States -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Loading States</h4>
          <div class="flex flex-wrap gap-4">
            <button class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg opacity-75 cursor-not-allowed dark:bg-purple-600">
              <div class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
              Loading...
            </button>
            <button class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg opacity-75 cursor-not-allowed">
              <div class="flex space-x-1 mr-2">
                <div class="w-1 h-1 bg-white rounded-full animate-bounce"></div>
                <div class="w-1 h-1 bg-white rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-1 h-1 bg-white rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
              Processing...
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Card Animations -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Card Interactions</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Card hover effects and interactive states for better user engagement.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Hover Lift -->
        <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-1 cursor-pointer">
          <div class="flex items-center mb-3">
            <i class="fas fa-crosshairs text-blue-600 dark:text-purple-400 mr-3"></i>
            <h4 class="font-semibold text-gray-900 dark:text-gray-100">Hover Lift</h4>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400">Card lifts up on hover</p>
        </div>

        <!-- Scale Effect -->
        <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm transition-transform duration-300 hover:scale-105 cursor-pointer">
          <div class="flex items-center mb-3">
            <i class="fas fa-chart-line text-green-600 dark:text-green-400 mr-3"></i>
            <h4 class="font-semibold text-gray-900 dark:text-gray-100">Scale Effect</h4>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400">Card scales up on hover</p>
        </div>

        <!-- Glow Effect -->
        <div class="bg-white dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 shadow-sm transition-all duration-300 hover:shadow-xl hover:shadow-purple-100 dark:hover:shadow-purple-900/20 cursor-pointer">
          <div class="flex items-center mb-3">
            <i class="fas fa-star text-purple-600 dark:text-purple-400 mr-3"></i>
            <h4 class="font-semibold text-gray-900 dark:text-gray-100">Glow Effect</h4>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400">Card glows on hover</p>
        </div>
      </div>
    </div>

    <!-- Page Transitions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Page Transitions</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Smooth transitions for page navigation and state changes.
      </p>
      
      <div class="space-y-6">
        <!-- Fade Transition -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Fade Transition</h4>
          <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div :class="{ 'opacity-100': showFade, 'opacity-0': !showFade }" class="transition-opacity duration-500">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">Fade Content</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">This content fades in and out</div>
            </div>
            <button @click="showFade = !showFade" class="px-3 py-1 bg-blue-600 text-white rounded text-sm dark:bg-purple-600">
              Toggle
            </button>
          </div>
        </div>

        <!-- Slide Transition -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Slide Transition</h4>
          <div class="overflow-hidden bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div :class="{ 'translate-x-0': showSlide, '-translate-x-full': !showSlide }" class="transform transition-transform duration-500 p-4">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">Slide Content</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">This content slides in from left</div>
            </div>
            <div class="px-4 pb-4">
              <button @click="showSlide = !showSlide" class="px-3 py-1 bg-green-600 text-white rounded text-sm">
                Toggle
              </button>
            </div>
          </div>
        </div>

        <!-- Scale Transition -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Scale Transition</h4>
          <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div :class="{ 'scale-100': showScale, 'scale-0': !showScale }" class="transform transition-transform duration-300 origin-left">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">Scale Content</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">This content scales in and out</div>
            </div>
            <button @click="showScale = !showScale" class="px-3 py-1 bg-purple-600 text-white rounded text-sm">
              Toggle
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Micro-interactions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Micro-interactions</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Small animations that provide feedback and enhance user experience.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Input Focus -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Input Focus</h4>
          <div class="space-y-3">
            <input type="text" placeholder="Focus me..." class="w-full px-3 py-2 border border-gray-300 rounded-lg transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:focus:ring-purple-400 dark:focus:border-purple-400">
            <input type="text" placeholder="With scale effect..." class="w-full px-3 py-2 border border-gray-300 rounded-lg transition-all duration-200 focus:ring-2 focus:ring-green-500 focus:border-green-500 focus:scale-105 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100">
          </div>
        </div>

        <!-- Checkbox Animation -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Checkbox Animation</h4>
          <div class="space-y-3">
            <label class="flex items-center">
              <input type="checkbox" class="form-checkbox h-5 w-5 text-blue-600 transition duration-200 dark:text-purple-600">
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Animated checkbox</span>
            </label>
            <label class="flex items-center">
              <div class="relative">
                <input type="checkbox" class="sr-only" v-model="customCheck">
                <div :class="{ 'bg-blue-600 border-blue-600': customCheck, 'bg-white border-gray-300': !customCheck }" class="w-5 h-5 border-2 rounded transition-all duration-200 dark:bg-gray-700 dark:border-gray-600">
                  <i v-if="customCheck" class="fas fa-check text-white text-xs flex items-center justify-center h-full transition-all duration-200"></i>
                </div>
              </div>
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Custom animated checkbox</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Animation state
const showFade = ref(true)
const showSlide = ref(true)
const showScale = ref(true)
const customCheck = ref(false)

// Animation data
const durations = [
  { name: 'Fast', value: '150ms' },
  { name: 'Base', value: '200ms' },
  { name: 'Slow', value: '300ms' },
  { name: 'Slower', value: '500ms' }
]

const easingFunctions = [
  { name: 'Linear', value: 'linear' },
  { name: 'Ease', value: 'ease' },
  { name: 'Ease In', value: 'ease-in' },
  { name: 'Ease Out', value: 'ease-out' },
  { name: 'Ease In Out', value: 'ease-in-out' }
]
</script>

<style scoped>
/* Progress bar animation */
@keyframes progress {
  0% { width: 0%; }
  100% { width: 75%; }
}

.progress-bar {
  animation: progress 2s ease-in-out infinite alternate;
}

/* Form checkbox styling */
.form-checkbox {
  appearance: none;
  background-color: #fff;
  border: 2px solid #d1d5db;
  border-radius: 0.25rem;
  display: inline-block;
  vertical-align: middle;
  background-origin: border-box;
  user-select: none;
  flex-shrink: 0;
}

.form-checkbox:checked {
  background-color: currentColor;
  border-color: currentColor;
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-6.5 6.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L7 9.293l6.146-6.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e");
}

.form-checkbox:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  box-shadow: 0 0 0 2px #3b82f6;
}
</style>