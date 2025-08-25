# Design System Documentation

Comprehensive design system for the Archery Tools platform featuring Material Design 3 components, interactive demos, and usage guidelines.

## Overview

The Archery Tools Design System is a complete UI component library built with Vue 3, Tailwind CSS, and Material Design 3 principles. It provides a unified visual language and consistent user experience across the entire platform.

### 🎯 Purpose
- **Consistency**: Standardized components and patterns across all pages
- **Developer Experience**: Clear guidelines and reusable components
- **User Experience**: Professional, accessible, and intuitive interface
- **Maintenance**: Centralized styling and component documentation

### 🔧 Technology Stack
- **Vue 3**: Composition API with reactive components
- **Tailwind CSS**: Utility-first CSS framework with custom utilities
- **Material Design 3**: Google's latest design system principles
- **FontAwesome**: Icon library with semantic usage
- **TypeScript**: Type safety and developer tooling

## Access & Authentication

The design system is accessible at `/design` and requires admin authentication:

```vue
// Admin check in layouts/default.vue
const isAdmin = computed(() => {
  return user.value?.email === 'messenlien@gmail.com'
})
```

**Access Requirements:**
- Must be logged in via Google OAuth
- Email must match admin user: `messenlien@gmail.com`
- Navigation link appears in admin section of main menu

## Design System Structure

### Navigation Sections

The design system is organized into 8 comprehensive sections:

1. **Overview** - Introduction and technology stack
2. **Colors** - Complete color palette and semantic usage
3. **Typography** - Text scales, responsive classes, and mobile-first design
4. **Components** - Interactive component library with live examples
5. **Layout** - Grid systems, spacing utilities, and responsive patterns
6. **Mobile** - Mobile-specific patterns and touch interactions
7. **Icons** - FontAwesome icon library organized by categories
8. **Animations** - Motion design system with transitions and micro-interactions

## Component Library

### Form Elements

#### Interactive Sliders
Professional range controls with live value updates:

```vue
<!-- Draw Weight Slider -->
<input 
  type="range" 
  v-model="drawWeight"
  min="20" 
  max="80" 
  class="slider w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
>
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
  Draw Weight: <span class="text-blue-600 dark:text-purple-400">{{ drawWeight }}lbs</span>
</label>
```

**Available Sliders:**
- **Draw Weight**: 20-80 lbs (archery bow specifications)
- **Draw Length**: 24-32 inches with 0.25" increments
- **Point Weight**: 75-200 grains in 5-grain steps
- **Arrow Length**: 26-32 inches with 0.5" increments

#### Form Controls
- **Text Inputs**: Standard, number, and icon-enhanced inputs
- **Select Dropdowns**: Single and multi-select options
- **Checkboxes**: Bow feature selections (rest, stabilizer, sight, peep)
- **Radio Buttons**: Arrow type selection (hunting, target, 3D, field)
- **Toggle Switches**: Custom-styled boolean controls
- **Text Areas**: Multi-line input with resize controls
- **Special Inputs**: Date, time, and color picker inputs

#### Reactive Form Summary
Real-time display of current form values:

```vue
<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
  <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Current Form Values</h5>
  <div class="text-sm space-y-1">
    <div class="flex justify-between">
      <span class="text-gray-600 dark:text-gray-400">Draw Weight:</span>
      <span class="text-gray-900 dark:text-gray-100">{{ drawWeight }}lbs</span>
    </div>
    <!-- Additional form values -->
  </div>
</div>
```

### Button Components

#### Variants
- **Filled**: Primary action buttons with solid backgrounds
- **Outlined**: Secondary actions with border styling
- **Text**: Minimal buttons for tertiary actions

#### Sizes & States
- **Sizes**: Small, medium, large with consistent scaling
- **States**: Normal, disabled, loading, with icons
- **Specialized**: Success, error, warning, primary color variants

### Card Components

#### Card Types
- **Basic Card**: Standard content containers
- **Info Card**: Blue-themed informational content
- **Success Card**: Green-themed confirmation messages
- **Glass Card**: Glassmorphism effect with backdrop blur
- **Gradient Card**: Subtle gradient backgrounds
- **Elevated Card**: Enhanced shadow for prominence

### Performance Components

Specialized archery-specific components:

```vue
<!-- Performance Metrics Grid -->
<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
  <!-- Speed Metric -->
  <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
    <div class="text-lg font-bold text-blue-600 dark:text-blue-400 mb-1">285.4 fps</div>
    <div class="text-sm text-blue-800 dark:text-blue-200 font-medium">Speed</div>
    <div class="text-xs text-blue-600 dark:text-blue-400 mt-1">Fast</div>
  </div>
</div>
```

## Styling System

### Custom Slider Styling

Cross-browser compatible slider styling:

```css
/* WebKit Browsers (Chrome, Safari, Edge) */
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

/* Firefox */
.slider::-moz-range-track {
  background: #d1d5db;
  border-radius: 0.375rem;
  height: 0.5rem;
  border: none;
}

.slider::-moz-range-thumb {
  background: #3b82f6;
  border: none;
  border-radius: 50%;
  height: 1.25rem;
  width: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
```

### Dark Mode Support

All components include comprehensive dark mode styling:

```css
/* Dark mode slider styling */
.dark .slider::-webkit-slider-track {
  background: #374151;
}

.dark .slider::-webkit-slider-thumb {
  background: #8b5cf6;
}

.dark .slider::-webkit-slider-thumb:hover {
  background: #7c3aed;
}
```

### Color System

#### Primary Colors
- **Light Mode**: Blue-600 (#3B82F6) for primary actions
- **Dark Mode**: Purple-400 (#A78BFA) for primary actions
- **Semantic Colors**: Green (success), Yellow/Orange (warning), Red (error)

#### Usage Guidelines
- **Blue/Purple**: Primary actions, navigation, interactive elements
- **Green**: Success states, confirmations, positive metrics
- **Yellow/Orange**: Warnings, pending states, neutral information
- **Red**: Errors, destructive actions, critical alerts
- **Gray**: Text, borders, backgrounds, secondary information

## Icons & Typography

### Icon Categories
- **Navigation & Interface**: Core UI navigation elements
- **Archery & Sports**: Sport-specific icons (target, bullseye, trophy)
- **Data & Analytics**: Charts, tables, calculations
- **Status & Feedback**: Success, warning, error indicators
- **Actions & Tools**: Edit, delete, save, print functions

### Typography Scale
- **Mobile-First**: Responsive text sizes with mobile optimization
- **Accessibility**: High contrast ratios and readable font sizes
- **Hierarchy**: Clear visual hierarchy with consistent spacing

## Reactive Components

### Vue 3 Implementation

All interactive components use Vue 3 Composition API:

```vue
<script setup>
import { ref, computed } from 'vue'

// Reactive form data
const drawWeight = ref(50)
const drawLength = ref(28)
const pointWeight = ref(125)
const arrowLength = ref(29)

// Form controls
const features = ref({
  rest: true,
  stabilizer: false,
  sight: true,
  peep: true
})

const arrowType = ref('hunting')

// Computed properties
const activeFeatures = computed(() => {
  const active = Object.keys(features.value).filter(key => features.value[key])
  return active.length > 0 ? active.join(', ') : 'None'
})
</script>
```

## Usage Guidelines

### For Developers

#### Component Integration
1. **Import Components**: Use existing components from `/components/` directory
2. **Follow Patterns**: Copy established patterns from design system examples
3. **Maintain Consistency**: Use standardized classes and component structures
4. **Test Dark Mode**: Ensure all new components work in both light and dark themes

#### Development Workflow
1. **Reference Design System**: Check `/design` page for component examples
2. **Copy Component Code**: Use design system components as templates
3. **Adapt for Context**: Modify examples for specific use cases
4. **Test Responsiveness**: Verify components work on mobile and desktop

### Component Creation Checklist

When creating new components:

- [ ] **Light & Dark Mode**: Include both theme variants
- [ ] **Responsive Design**: Mobile-first approach with breakpoints
- [ ] **Accessibility**: Proper ARIA labels and keyboard navigation
- [ ] **Loading States**: Show loading indicators for async operations
- [ ] **Error Handling**: Display user-friendly error messages
- [ ] **Type Safety**: Use TypeScript for component props
- [ ] **Documentation**: Update design system with new components

### Color Usage Guidelines

#### Primary Actions
```vue
<!-- Primary button -->
<button class="bg-blue-600 hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700">
  Primary Action
</button>

<!-- Primary text -->
<span class="text-blue-600 dark:text-purple-400">Primary Text</span>
```

#### Status Indicators
```vue
<!-- Success state -->
<div class="bg-green-50 border border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-200">
  Success Message
</div>

<!-- Warning state -->
<div class="bg-yellow-50 border border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-200">
  Warning Message
</div>
```

### Animation Guidelines

#### Transition Timing
- **Fast (150ms)**: Hover states, focus changes
- **Base (200ms)**: Button interactions, color changes
- **Slow (300ms)**: Page transitions, modal animations
- **Slower (500ms)**: Complex animations, loading states

#### Easing Functions
- **Ease-out**: Most UI transitions (natural deceleration)
- **Ease-in-out**: Modal and page transitions
- **Linear**: Progress bars and loading indicators

## File Structure

### Design System Files

```
/frontend/pages/design.vue                           # Main design system page
/frontend/components/design-system/
├── DesignSystemOverview.vue                         # Introduction and tech stack
├── DesignSystemColors.vue                           # Color palette and usage
├── DesignSystemTypography.vue                       # Text styles and hierarchy
├── DesignSystemComponents.vue                       # Interactive component library
├── DesignSystemLayout.vue                          # Grid systems and spacing
├── DesignSystemMobile.vue                          # Mobile-specific patterns
├── DesignSystemIcons.vue                           # Icon library showcase
└── DesignSystemAnimations.vue                      # Motion design patterns
```

### Component Dependencies

The design system relies on:

- **CustomButton.vue**: Reusable button component
- **DarkModeToggle.vue**: Theme switching component
- **Material Web Components**: Google's Material Design 3 components
- **FontAwesome**: Icon library for UI elements

## Best Practices

### Component Development

1. **Consistency First**: Always check design system before creating new patterns
2. **Mobile-First**: Design for mobile screens first, then scale up
3. **Accessibility**: Include proper ARIA labels and keyboard navigation
4. **Performance**: Optimize components for fast loading and smooth interactions
5. **Maintainability**: Use clear, descriptive class names and component structure

### Code Quality

1. **TypeScript**: Use type definitions for component props and events
2. **Vue 3 Composition API**: Prefer composition API for reactive logic
3. **Scoped Styles**: Use scoped CSS to prevent style conflicts
4. **Component Testing**: Test components in isolation and integration
5. **Documentation**: Keep design system updated with new components

### Design Principles

1. **Progressive Enhancement**: Start with basic functionality, enhance with JavaScript
2. **Semantic HTML**: Use proper HTML elements for accessibility
3. **Visual Hierarchy**: Clear information architecture with consistent spacing
4. **Color Contrast**: Ensure accessibility compliance for all text and backgrounds
5. **Touch-Friendly**: Design for touch interaction on mobile devices

## Maintenance & Updates

### Regular Tasks

1. **Component Audits**: Review design system quarterly for consistency
2. **Performance Monitoring**: Check component rendering performance
3. **Accessibility Testing**: Regular accessibility compliance checks
4. **Design System Updates**: Keep design system current with new components
5. **Documentation Updates**: Maintain accurate usage guidelines

### Version Control

- **Component Versioning**: Track major component changes
- **Breaking Changes**: Document any breaking changes to existing components
- **Migration Guides**: Provide upgrade paths for component updates
- **Changelog**: Maintain detailed changelog for design system updates

## Integration Examples

### Adding New Components

When adding new components to the design system:

1. **Create Component File**: Add to appropriate design system section
2. **Add Navigation**: Update main design system navigation
3. **Document Usage**: Include usage examples and code snippets
4. **Test Integration**: Verify component works in actual application context

### Example Integration

```vue
<!-- Add new component to DesignSystemComponents.vue -->
<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">New Component</h3>
    <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
      Description of the new component and its usage.
    </p>
    
    <!-- Component examples -->
    <div class="space-y-4">
      <!-- Interactive examples here -->
    </div>
  </div>
</template>
```

---

## Conclusion

The Archery Tools Design System provides a comprehensive foundation for building consistent, accessible, and maintainable user interfaces. By following the guidelines and patterns established in this system, developers can create high-quality components that provide an excellent user experience across all devices and contexts.

For questions or suggestions about the design system, reference the live examples at `/design` or consult this documentation for detailed implementation guidance.