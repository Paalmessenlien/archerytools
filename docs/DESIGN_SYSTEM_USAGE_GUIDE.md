# Design System Usage Guide

Practical guide for developers using the Archery Tools Design System in daily development work.

## Quick Start

### 1. Access the Design System

```bash
# Start development environment
./start-unified.sh dev start

# Navigate to design system (requires admin login)
# http://localhost:3000/design
```

**Login Requirements:**
- Login with Google OAuth
- Must use admin email: `messenlien@gmail.com`
- Design system link appears in admin section of navigation menu

### 2. Design System Navigation

The design system is organized into 8 sections:
- **Overview**: Technology stack and introduction
- **Colors**: Color palette and semantic usage guidelines  
- **Typography**: Text styles and responsive scaling
- **Components**: Interactive component library with live examples
- **Layout**: Grid systems and spacing utilities
- **Mobile**: Mobile-specific patterns and touch interactions
- **Icons**: FontAwesome icon library organized by categories
- **Animations**: Motion design and transition patterns

## Common Development Workflows

### Creating Form Components

#### Step 1: Reference Design System
1. Go to `/design` → Components section
2. Find "Form Controls" section
3. Copy the desired form element pattern

#### Step 2: Basic Text Input

```vue
<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      Field Label
    </label>
    <input 
      type="text" 
      v-model="fieldValue"
      placeholder="Enter value..." 
      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400"
    >
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fieldValue = ref('')
</script>
```

#### Step 3: Interactive Slider

```vue
<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      Draw Weight: <span class="text-blue-600 dark:text-purple-400">{{ drawWeight }}lbs</span>
    </label>
    <input 
      type="range" 
      v-model="drawWeight"
      min="20" 
      max="80" 
      class="slider w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
    >
    <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
      <span>20lbs</span>
      <span>80lbs</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const drawWeight = ref(50)
</script>

<style scoped>
.slider {
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
  cursor: pointer;
}

.slider::-webkit-slider-track {
  background: #d1d5db;
  border-radius: 0.375rem;
  height: 0.5rem;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  background: #3b82f6;
  border-radius: 50%;
  height: 1.25rem;
  width: 1.25rem;
  margin-top: -0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dark .slider::-webkit-slider-track {
  background: #374151;
}

.dark .slider::-webkit-slider-thumb {
  background: #8b5cf6;
}
</style>
```

### Creating Card Components

#### Step 1: Basic Card Pattern

```vue
<template>
  <!-- Basic Card -->
  <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
    <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Card Title</h4>
    <p class="text-sm text-gray-600 dark:text-gray-400">Card content goes here.</p>
  </div>
</template>
```

#### Step 2: Status Cards

```vue
<template>
  <!-- Success Card -->
  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
    <div class="flex items-center mb-2">
      <i class="fas fa-check-circle text-green-600 dark:text-green-400 mr-2"></i>
      <h4 class="font-semibold text-green-800 dark:text-green-200">Success</h4>
    </div>
    <p class="text-sm text-green-700 dark:text-green-300">Operation completed successfully.</p>
  </div>

  <!-- Warning Card -->
  <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
    <div class="flex items-center mb-2">
      <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 mr-2"></i>
      <h4 class="font-semibold text-yellow-800 dark:text-yellow-200">Warning</h4>
    </div>
    <p class="text-sm text-yellow-700 dark:text-yellow-300">Please review this information.</p>
  </div>

  <!-- Error Card -->
  <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
    <div class="flex items-center mb-2">
      <i class="fas fa-times-circle text-red-600 dark:text-red-400 mr-2"></i>
      <h4 class="font-semibold text-red-800 dark:text-red-200">Error</h4>
    </div>
    <p class="text-sm text-red-700 dark:text-red-300">An error occurred during processing.</p>
  </div>
</template>
```

### Button Usage Patterns

#### Standard Buttons

```vue
<template>
  <!-- Use CustomButton component -->
  <CustomButton variant="filled">Primary Action</CustomButton>
  <CustomButton variant="outlined">Secondary Action</CustomButton>
  <CustomButton variant="text">Tertiary Action</CustomButton>

  <!-- Specialized buttons -->
  <button class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
    Success Action
  </button>
  <button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
    Delete Action
  </button>
</template>

<script setup>
import CustomButton from '~/components/CustomButton.vue'
</script>
```

### Performance Metrics Display

#### Archery Performance Cards

```vue
<template>
  <!-- Performance Metrics Grid -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Speed Metric -->
    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
      <div class="text-lg font-bold text-blue-600 dark:text-blue-400 mb-1">{{ speed }} fps</div>
      <div class="text-sm text-blue-800 dark:text-blue-200 font-medium">Speed</div>
      <div class="text-xs text-blue-600 dark:text-blue-400 mt-1">{{ speedCategory }}</div>
    </div>
    
    <!-- Kinetic Energy -->
    <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
      <div class="text-lg font-bold text-green-600 dark:text-green-400 mb-1">{{ kineticEnergy }} ft·lbs</div>
      <div class="text-sm text-green-800 dark:text-green-200 font-medium">KE @40yd</div>
      <div class="text-xs text-green-600 dark:text-green-400 mt-1">{{ keCategory }}</div>
    </div>

    <!-- FOC -->
    <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
      <div class="text-lg font-bold text-purple-600 dark:text-purple-400 mb-1">{{ foc }}%</div>
      <div class="text-sm text-purple-800 dark:text-purple-200 font-medium">FOC</div>
      <div class="text-xs text-purple-600 dark:text-purple-400 mt-1">{{ focCategory }}</div>
    </div>

    <!-- Performance Score -->
    <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
      <div class="text-lg font-bold text-green-600 dark:text-green-400 mb-1">{{ score }}/100</div>
      <div class="text-sm text-orange-800 dark:text-orange-200 font-medium">Score</div>
      <div class="text-xs text-orange-600 dark:text-orange-400 mt-1">{{ scoreCategory }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  speed: { type: Number, required: true },
  kineticEnergy: { type: Number, required: true },
  foc: { type: Number, required: true },
  score: { type: Number, required: true }
})

const speedCategory = computed(() => {
  return props.speed >= 300 ? 'Very Fast' : props.speed >= 280 ? 'Fast' : 'Moderate'
})

const keCategory = computed(() => {
  return props.kineticEnergy >= 60 ? 'Excellent' : props.kineticEnergy >= 40 ? 'Good' : 'Fair'
})

const focCategory = computed(() => {
  return props.foc >= 15 ? 'High' : props.foc >= 10 ? 'Good' : 'Low'
})

const scoreCategory = computed(() => {
  return props.score >= 90 ? 'Excellent' : props.score >= 75 ? 'Good' : 'Fair'
})
</script>
```

## Color Usage Reference

### Primary Colors

```vue
<!-- Light Mode: Blue | Dark Mode: Purple -->
<div class="text-blue-600 dark:text-purple-400">Primary text</div>
<div class="bg-blue-600 dark:bg-purple-600">Primary background</div>
<div class="border-blue-600 dark:border-purple-600">Primary border</div>
```

### Semantic Colors

```vue
<!-- Success (Green) -->
<div class="text-green-600 dark:text-green-400">Success text</div>
<div class="bg-green-50 dark:bg-green-900/20">Success background</div>

<!-- Warning (Yellow/Orange) -->
<div class="text-yellow-600 dark:text-yellow-400">Warning text</div>
<div class="bg-yellow-50 dark:bg-yellow-900/20">Warning background</div>

<!-- Error (Red) -->
<div class="text-red-600 dark:text-red-400">Error text</div>
<div class="bg-red-50 dark:bg-red-900/20">Error background</div>

<!-- Neutral (Gray) -->
<div class="text-gray-600 dark:text-gray-400">Neutral text</div>
<div class="bg-gray-50 dark:bg-gray-900/20">Neutral background</div>
```

## Icon Usage Patterns

### Basic Icon Usage

```vue
<template>
  <!-- Navigation icons -->
  <i class="fas fa-home text-blue-600 dark:text-purple-400"></i>
  <i class="fas fa-search text-gray-600 dark:text-gray-400"></i>
  
  <!-- Status icons -->
  <i class="fas fa-check-circle text-green-600 dark:text-green-400"></i>
  <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400"></i>
  <i class="fas fa-times-circle text-red-600 dark:text-red-400"></i>
  
  <!-- Archery specific icons -->
  <i class="fas fa-crosshairs text-blue-600 dark:text-purple-400"></i>
  <i class="fas fa-bullseye text-red-600 dark:text-red-400"></i>
  <i class="fas fa-trophy text-yellow-600 dark:text-yellow-400"></i>
</template>
```

### Icon Sizes

```vue
<!-- Size classes -->
<i class="fas fa-home text-xs"></i>     <!-- 12px -->
<i class="fas fa-home text-sm"></i>     <!-- 14px -->
<i class="fas fa-home text-base"></i>   <!-- 16px -->
<i class="fas fa-home text-lg"></i>     <!-- 18px -->
<i class="fas fa-home text-xl"></i>     <!-- 20px -->
```

## Animation Guidelines

### Button Hover Effects

```vue
<template>
  <!-- Hover lift effect -->
  <button class="px-4 py-2 bg-blue-600 text-white rounded-lg transition-all duration-200 hover:bg-blue-700 hover:shadow-lg hover:-translate-y-0.5">
    Lift on Hover
  </button>

  <!-- Hover scale effect -->
  <button class="px-4 py-2 bg-green-600 text-white rounded-lg transition-all duration-200 hover:bg-green-700 hover:scale-105">
    Scale on Hover
  </button>
</template>
```

### Loading States

```vue
<template>
  <!-- Spinner -->
  <div class="flex items-center">
    <div class="animate-spin rounded-full h-6 w-6 border-2 border-blue-500 border-t-transparent"></div>
    <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading...</span>
  </div>

  <!-- Bouncing dots -->
  <div class="flex space-x-1">
    <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
    <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
    <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
  </div>
</template>
```

## Responsive Design Patterns

### Mobile-First Grid

```vue
<template>
  <!-- Mobile: 1 column, Tablet: 2 columns, Desktop: 4 columns -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg p-4">Item 1</div>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-4">Item 2</div>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-4">Item 3</div>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-4">Item 4</div>
  </div>
</template>
```

### Responsive Typography

```vue
<template>
  <!-- Responsive text sizing -->
  <h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">Main Heading</h1>
  <h2 class="text-xl md:text-2xl lg:text-3xl font-semibold">Sub Heading</h2>
  <p class="text-sm md:text-base">Body text content</p>
</template>
```

## Development Checklist

### Before Creating New Components

- [ ] Check design system for existing patterns
- [ ] Reference color and typography guidelines  
- [ ] Ensure mobile-first responsive design
- [ ] Include dark mode styling
- [ ] Add proper accessibility attributes
- [ ] Test keyboard navigation
- [ ] Verify cross-browser compatibility

### Component Quality Standards

- [ ] **Responsive**: Works on mobile, tablet, desktop
- [ ] **Accessible**: ARIA labels, keyboard navigation
- [ ] **Dark Mode**: Both light and dark theme support
- [ ] **Interactive**: Proper hover/focus states
- [ ] **Loading States**: Shows loading when appropriate
- [ ] **Error Handling**: Graceful error display
- [ ] **Type Safety**: TypeScript prop definitions
- [ ] **Performance**: Optimized rendering

## Common Patterns Library

### Search Input with Icon

```vue
<template>
  <div class="relative">
    <input 
      type="text" 
      v-model="searchQuery"
      placeholder="Search arrows..." 
      class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400"
    >
    <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const searchQuery = ref('')
</script>
```

### Data Table Pattern

```vue
<template>
  <div class="overflow-x-auto">
    <table class="min-w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
      <thead class="bg-gray-50 dark:bg-gray-700">
        <tr>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Column 1
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Column 2
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
        <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
          <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{{ item.name }}</td>
          <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{{ item.value }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

### Modal/Dialog Pattern

```vue
<template>
  <!-- Modal Backdrop -->
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <!-- Modal Content -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full border border-gray-200 dark:border-gray-700">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Modal Title</h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- Content -->
      <div class="mb-6">
        <p class="text-gray-600 dark:text-gray-400">Modal content goes here...</p>
      </div>
      
      <!-- Actions -->
      <div class="flex justify-end space-x-3">
        <CustomButton variant="outlined" @click="closeModal">Cancel</CustomButton>
        <CustomButton variant="filled" @click="confirmAction">Confirm</CustomButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CustomButton from '~/components/CustomButton.vue'

const isOpen = ref(false)

const openModal = () => { isOpen.value = true }
const closeModal = () => { isOpen.value = false }
const confirmAction = () => {
  // Handle confirmation
  closeModal()
}
</script>
```

## Troubleshooting

### Common Issues

#### Dark Mode Not Working
```vue
<!-- Ensure dark: prefix is used -->
<div class="bg-white dark:bg-gray-800">Content</div>
```

#### Icons Not Displaying
```vue
<!-- Check FontAwesome class is correct -->
<i class="fas fa-home"></i> <!-- Correct -->
<i class="fa fa-home"></i>  <!-- May not work -->
```

#### Slider Styling Issues
```vue
<!-- Include custom slider styles -->
<style scoped>
.slider {
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
}
/* Add webkit and moz styles as shown in examples above */
</style>
```

### Performance Tips

1. **Use v-show for toggles** instead of v-if when frequently toggling
2. **Lazy load components** for better initial page load
3. **Minimize reactive computations** in tight loops
4. **Use CSS transforms** for animations instead of changing layout properties

## Getting Help

### Resources
- **Live Design System**: `/design` page with interactive examples
- **Documentation**: This guide and Design System Documentation
- **Component Files**: Check existing components in `/components/` directory
- **Examples**: Look at existing pages for implementation patterns

### Best Practices for Questions
1. Check design system first for existing patterns
2. Reference this guide for common use cases
3. Look at similar components in the codebase
4. Test your implementation in both light and dark modes

---

This guide provides practical examples and patterns for using the Archery Tools Design System effectively. Always refer to the live design system at `/design` for the most up-to-date component examples and interactive demonstrations.