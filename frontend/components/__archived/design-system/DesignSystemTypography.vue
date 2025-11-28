<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Typography</h2>
      <p class="text-gray-600 dark:text-gray-400">
        Mobile-first typography system with responsive scaling and accessibility features.
      </p>
    </div>

    <!-- Font Stack -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Font Stack</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Primary Font</h4>
          <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="text-2xl font-normal mb-2" style="font-family: 'Roboto', sans-serif;">
              Roboto
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            </div>
          </div>
        </div>
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">System Fallback</h4>
          <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="text-2xl font-normal mb-2" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
              System UI
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Native system fonts for optimal performance
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Typography Scale -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Typography Scale</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Responsive text sizes that adapt to different screen sizes and reading contexts.
      </p>
      
      <div class="space-y-6">
        <div v-for="item in typographyScale" :key="item.name" class="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between mb-2">
            <div class="flex items-center space-x-4">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100 w-24">{{ item.name }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">{{ item.class }}</div>
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-2 lg:mt-0">
              {{ item.size }} • {{ item.lineHeight }} • {{ item.weight }}
            </div>
          </div>
          <div :class="item.class" class="text-gray-900 dark:text-gray-100">
            {{ item.sample }}
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Typography -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mobile Typography</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Optimized text styles for mobile devices with enhanced readability and touch-friendly sizing.
      </p>
      
      <div class="space-y-4">
        <div class="mobile-heading-1 text-gray-900 dark:text-gray-100">
          Mobile Heading 1
        </div>
        <div class="mobile-heading-2 text-gray-900 dark:text-gray-100">
          Mobile Heading 2 - Perfect for section titles
        </div>
        <div class="mobile-heading-3 text-gray-900 dark:text-gray-100">
          Mobile Heading 3 - Ideal for card titles and subsections
        </div>
        <div class="mobile-body-large text-gray-900 dark:text-gray-100">
          Mobile Body Large - Enhanced readability for important content and introductory text on mobile devices.
        </div>
        <div class="mobile-body-medium text-gray-900 dark:text-gray-100">
          Mobile Body Medium - Standard text for most content, optimized for mobile reading with appropriate line height and letter spacing.
        </div>
        <div class="mobile-body-small text-gray-600 dark:text-gray-400">
          Mobile Body Small - Used for captions, labels, and secondary information with good contrast.
        </div>
      </div>
    </div>

    <!-- Text Emphasis -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Text Emphasis</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Different emphasis levels for hierarchy and accessibility.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">High Emphasis</h4>
          <div class="space-y-2">
            <div class="text-gray-900 dark:text-gray-100 font-semibold">Primary headings</div>
            <div class="text-gray-900 dark:text-gray-100 font-medium">Important content</div>
            <div class="text-gray-900 dark:text-gray-100">Body text</div>
          </div>
        </div>
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Medium Emphasis</h4>
          <div class="space-y-2">
            <div class="text-gray-700 dark:text-gray-300 font-medium">Secondary headings</div>
            <div class="text-gray-700 dark:text-gray-300">Supporting text</div>
            <div class="text-gray-600 dark:text-gray-400">Helper text</div>
          </div>
        </div>
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Low Emphasis</h4>
          <div class="space-y-2">
            <div class="text-gray-500 dark:text-gray-500">Disabled text</div>
            <div class="text-gray-400 dark:text-gray-600">Placeholder text</div>
            <div class="text-gray-400 dark:text-gray-600">Caption text</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Text Colors -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Text Colors</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Semantic colors for different types of content and states.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Light Mode</h4>
          <div class="space-y-2">
            <div class="text-gray-900">Primary text (gray-900)</div>
            <div class="text-gray-700">Secondary text (gray-700)</div>
            <div class="text-gray-600">Tertiary text (gray-600)</div>
            <div class="text-blue-600">Primary links (blue-600)</div>
            <div class="text-green-600">Success text (green-600)</div>
            <div class="text-yellow-600">Warning text (yellow-600)</div>
            <div class="text-red-600">Error text (red-600)</div>
          </div>
        </div>
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Dark Mode</h4>
          <div class="space-y-2">
            <div class="text-gray-100 dark:text-gray-100">Primary text (gray-100)</div>
            <div class="text-gray-300 dark:text-gray-300">Secondary text (gray-300)</div>
            <div class="text-gray-400 dark:text-gray-400">Tertiary text (gray-400)</div>
            <div class="text-purple-400 dark:text-purple-400">Primary links (purple-400)</div>
            <div class="text-green-400 dark:text-green-400">Success text (green-400)</div>
            <div class="text-yellow-400 dark:text-yellow-400">Warning text (yellow-400)</div>
            <div class="text-red-400 dark:text-red-400">Error text (red-400)</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Usage Guidelines -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Usage Guidelines</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">✅ Do</h4>
          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-2">
            <li>• Use consistent hierarchy throughout the application</li>
            <li>• Maintain proper contrast ratios for accessibility</li>
            <li>• Use mobile typography classes on small screens</li>
            <li>• Keep line lengths between 45-75 characters</li>
            <li>• Use semantic colors for meaningful text</li>
          </ul>
        </div>
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">❌ Don't</h4>
          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-2">
            <li>• Mix different type scales inconsistently</li>
            <li>• Use colors that fail accessibility standards</li>
            <li>• Make text too small on mobile devices</li>
            <li>• Use too many different font weights</li>
            <li>• Forget to test in both light and dark modes</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const typographyScale = [
  {
    name: 'Display',
    class: 'text-6xl font-bold leading-none',
    size: '3.75rem',
    lineHeight: '1',
    weight: '700',
    sample: 'Display Text'
  },
  {
    name: 'H1',
    class: 'text-4xl font-bold leading-tight',
    size: '2.25rem',
    lineHeight: '1.2',
    weight: '700',
    sample: 'Heading Level 1'
  },
  {
    name: 'H2',
    class: 'text-3xl font-semibold leading-tight',
    size: '1.875rem',
    lineHeight: '1.25',
    weight: '600',
    sample: 'Heading Level 2'
  },
  {
    name: 'H3',
    class: 'text-2xl font-semibold leading-snug',
    size: '1.5rem',
    lineHeight: '1.3',
    weight: '600',
    sample: 'Heading Level 3'
  },
  {
    name: 'H4',
    class: 'text-xl font-medium leading-normal',
    size: '1.25rem',
    lineHeight: '1.4',
    weight: '500',
    sample: 'Heading Level 4'
  },
  {
    name: 'H5',
    class: 'text-lg font-medium leading-normal',
    size: '1.125rem',
    lineHeight: '1.4',
    weight: '500',
    sample: 'Heading Level 5'
  },
  {
    name: 'H6',
    class: 'text-base font-medium leading-normal',
    size: '1rem',
    lineHeight: '1.5',
    weight: '500',
    sample: 'Heading Level 6'
  },
  {
    name: 'Body Large',
    class: 'text-lg leading-relaxed',
    size: '1.125rem',
    lineHeight: '1.6',
    weight: '400',
    sample: 'Large body text for introductions and important content that needs extra emphasis and readability.'
  },
  {
    name: 'Body',
    class: 'text-base leading-normal',
    size: '1rem',
    lineHeight: '1.5',
    weight: '400',
    sample: 'Regular body text for most content. This is the standard reading size with optimal line height for readability.'
  },
  {
    name: 'Body Small',
    class: 'text-sm leading-normal',
    size: '0.875rem',
    lineHeight: '1.4',
    weight: '400',
    sample: 'Small body text for captions, labels, and secondary information.'
  },
  {
    name: 'Caption',
    class: 'text-xs leading-normal',
    size: '0.75rem',
    lineHeight: '1.3',
    weight: '400',
    sample: 'Caption text for very small labels and metadata.'
  }
]
</script>

<style scoped>
/* Mobile Typography Classes */
.mobile-heading-1 {
  font-size: 2rem;
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.mobile-heading-2 {
  font-size: 1.5rem;
  line-height: 1.3;
  font-weight: 600;
  letter-spacing: -0.015em;
}

.mobile-heading-3 {
  font-size: 1.25rem;
  line-height: 1.4;
  font-weight: 600;
}

.mobile-body-large {
  font-size: 1.125rem;
  line-height: 1.6;
  font-weight: 400;
}

.mobile-body-medium {
  font-size: 1rem;
  line-height: 1.5;
  font-weight: 400;
}

.mobile-body-small {
  font-size: 0.875rem;
  line-height: 1.4;
  font-weight: 400;
}

@media (min-width: 640px) {
  .mobile-heading-1 {
    font-size: 2.5rem;
  }
  
  .mobile-heading-2 {
    font-size: 1.875rem;
  }
  
  .mobile-heading-3 {
    font-size: 1.5rem;
  }
}
</style>