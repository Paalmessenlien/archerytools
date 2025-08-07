# Styling System - Tailwind CSS + Material Design 3

Comprehensive documentation for the styling architecture using Tailwind CSS with Material Design 3 components and theming.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Material Design 3 Integration](#material-design-3-integration)
- [Tailwind CSS Configuration](#tailwind-css-configuration)
- [Dark Mode System](#dark-mode-system)
- [Component Styling](#component-styling)
- [Responsive Design](#responsive-design)
- [Custom CSS Classes](#custom-css-classes)
- [Best Practices](#best-practices)

---

## Architecture Overview

### Technology Stack
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Material Web Components**: Google's official Material Design 3 web components
- **CSS Custom Properties**: Material Design 3 color system implementation
- **PostCSS**: CSS processing and optimization
- **Google Fonts**: Roboto typography and Material Symbols icons

### Styling Philosophy
1. **Utility-First**: Tailwind classes for most styling needs
2. **Component Theming**: Material Web components with custom theming
3. **Design System**: Consistent Material Design 3 principles
4. **Responsive**: Mobile-first responsive design approach
5. **Accessible**: WCAG compliant color contrasts and interactions

---

## Material Design 3 Integration

### Color System Implementation (`assets/css/main.css`)

#### Light Theme Colors
```css
:root {
  /* Primary Colors */
  --md-sys-color-primary: 103 80 164;
  --md-sys-color-on-primary: 255 255 255;
  --md-sys-color-primary-container: 234 221 255;
  --md-sys-color-on-primary-container: 33 0 93;

  /* Secondary Colors */
  --md-sys-color-secondary: 98 91 113;
  --md-sys-color-on-secondary: 255 255 255;
  --md-sys-color-secondary-container: 232 222 248;
  --md-sys-color-on-secondary-container: 29 25 43;

  /* Tertiary Colors */
  --md-sys-color-tertiary: 125 82 96;
  --md-sys-color-on-tertiary: 255 255 255;
  --md-sys-color-tertiary-container: 255 216 228;
  --md-sys-color-on-tertiary-container: 55 11 30;

  /* Surface Colors */
  --md-sys-color-surface: 255 255 255;
  --md-sys-color-surface-dim: 222 216 225;
  --md-sys-color-surface-bright: 255 255 255;
  --md-sys-color-surface-container-lowest: 255 255 255;
  --md-sys-color-surface-container-low: 247 242 250;
  --md-sys-color-surface-container: 243 237 247;
  --md-sys-color-surface-container-high: 236 230 240;
  --md-sys-color-surface-container-highest: 230 224 233;

  /* Content Colors */
  --md-sys-color-on-surface: 28 27 31;
  --md-sys-color-on-surface-variant: 73 69 78;
  --md-sys-color-outline: 121 116 126;
  --md-sys-color-outline-variant: 196 199 197;

  /* State Colors */
  --md-sys-color-error: 186 26 26;
  --md-sys-color-on-error: 255 255 255;
  --md-sys-color-error-container: 255 218 214;
  --md-sys-color-on-error-container: 65 0 2;

  /* Background */
  --md-sys-color-background: 255 255 255;
  --md-sys-color-on-background: 28 27 31;
  
  /* Additional semantic colors */
  --md-sys-color-success: 46 125 50;
  --md-sys-color-warning: 245 124 0;
  --md-sys-color-info: 25 118 210;
}
```

#### Dark Theme Colors
```css
.dark {
  /* Primary Colors */
  --md-sys-color-primary: 208 188 255;
  --md-sys-color-on-primary: 56 30 114;
  --md-sys-color-primary-container: 79 55 139;
  --md-sys-color-on-primary-container: 234 221 255;

  /* Secondary Colors */
  --md-sys-color-secondary: 204 194 220;
  --md-sys-color-on-secondary: 50 45 65;
  --md-sys-color-secondary-container: 73 68 88;
  --md-sys-color-on-secondary-container: 232 222 248;

  /* Tertiary Colors */
  --md-sys-color-tertiary: 227 187 200;
  --md-sys-color-on-tertiary: 78 37 50;
  --md-sys-color-tertiary-container: 101 58 72;
  --md-sys-color-on-tertiary-container: 255 216 228;

  /* Surface Colors */
  --md-sys-color-surface: 16 16 20;
  --md-sys-color-surface-dim: 16 16 20;
  --md-sys-color-surface-bright: 54 54 59;
  --md-sys-color-surface-container-lowest: 11 11 13;
  --md-sys-color-surface-container-low: 24 24 29;
  --md-sys-color-surface-container: 28 28 33;
  --md-sys-color-surface-container-high: 38 38 43;
  --md-sys-color-surface-container-highest: 49 48 51;

  /* Content Colors */
  --md-sys-color-on-surface: 230 225 229;
  --md-sys-color-on-surface-variant: 202 196 208;
  --md-sys-color-outline: 147 143 153;
  --md-sys-color-outline-variant: 73 69 78;

  /* State Colors */
  --md-sys-color-error: 255 180 171;
  --md-sys-color-on-error: 105 0 5;
  --md-sys-color-error-container: 147 0 10;
  --md-sys-color-on-error-container: 255 218 214;

  /* Background */
  --md-sys-color-background: 16 16 20;
  --md-sys-color-on-background: 230 225 229;
}
```

### Material Web Component Theming
```css
/* Button Components */
md-filled-button {
  --md-filled-button-container-color: rgb(var(--md-sys-color-primary));
  --md-filled-button-label-text-color: rgb(var(--md-sys-color-on-primary));
  --md-filled-button-hover-state-layer-color: rgb(var(--md-sys-color-on-primary));
  --md-filled-button-pressed-state-layer-color: rgb(var(--md-sys-color-on-primary));
}

md-outlined-button {
  --md-outlined-button-outline-color: rgb(var(--md-sys-color-outline));
  --md-outlined-button-label-text-color: rgb(var(--md-sys-color-primary));
  --md-outlined-button-hover-state-layer-color: rgb(var(--md-sys-color-primary));
}

/* Text Field Components */
md-filled-text-field {
  --md-filled-text-field-container-color: rgb(var(--md-sys-color-surface-container-highest));
  --md-filled-text-field-label-text-color: rgb(var(--md-sys-color-on-surface-variant));
  --md-filled-text-field-input-text-color: rgb(var(--md-sys-color-on-surface));
}

/* Select Components */
md-filled-select {
  --md-filled-select-text-field-container-color: rgb(var(--md-sys-color-surface-container-highest));
  --md-filled-select-text-field-label-text-color: rgb(var(--md-sys-color-on-surface-variant));
  --md-filled-select-text-field-input-text-color: rgb(var(--md-sys-color-on-surface));
}

/* Navigation Components */
md-navigation-drawer {
  --md-navigation-drawer-container-color: rgb(var(--md-sys-color-surface-container-low));
}

md-navigation-drawer-item {
  --md-navigation-drawer-item-label-text-color: rgb(var(--md-sys-color-on-surface-variant));
  --md-navigation-drawer-item-icon-color: rgb(var(--md-sys-color-on-surface-variant));
}

md-navigation-drawer-item[active] {
  --md-navigation-drawer-item-label-text-color: rgb(var(--md-sys-color-on-secondary-container));
  --md-navigation-drawer-item-icon-color: rgb(var(--md-sys-color-on-secondary-container));
  --md-navigation-drawer-item-container-color: rgb(var(--md-sys-color-secondary-container));
}
```

---

## Tailwind CSS Configuration

### Configuration File (`tailwind.config.js`)
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}",
    "./app.vue"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Material Design 3 colors with CSS variables
        primary: 'rgb(var(--md-sys-color-primary) / <alpha-value>)',
        'on-primary': 'rgb(var(--md-sys-color-on-primary) / <alpha-value>)',
        'primary-container': 'rgb(var(--md-sys-color-primary-container) / <alpha-value>)',
        'on-primary-container': 'rgb(var(--md-sys-color-on-primary-container) / <alpha-value>)',
        
        secondary: 'rgb(var(--md-sys-color-secondary) / <alpha-value>)',
        'on-secondary': 'rgb(var(--md-sys-color-on-secondary) / <alpha-value>)',
        'secondary-container': 'rgb(var(--md-sys-color-secondary-container) / <alpha-value>)',
        'on-secondary-container': 'rgb(var(--md-sys-color-on-secondary-container) / <alpha-value>)',
        
        tertiary: 'rgb(var(--md-sys-color-tertiary) / <alpha-value>)',
        'on-tertiary': 'rgb(var(--md-sys-color-on-tertiary) / <alpha-value>)',
        'tertiary-container': 'rgb(var(--md-sys-color-tertiary-container) / <alpha-value>)',
        'on-tertiary-container': 'rgb(var(--md-sys-color-on-tertiary-container) / <alpha-value>)',
        
        surface: 'rgb(var(--md-sys-color-surface) / <alpha-value>)',
        'surface-dim': 'rgb(var(--md-sys-color-surface-dim) / <alpha-value>)',
        'surface-bright': 'rgb(var(--md-sys-color-surface-bright) / <alpha-value>)',
        'surface-container-lowest': 'rgb(var(--md-sys-color-surface-container-lowest) / <alpha-value>)',
        'surface-container-low': 'rgb(var(--md-sys-color-surface-container-low) / <alpha-value>)',
        'surface-container': 'rgb(var(--md-sys-color-surface-container) / <alpha-value>)',
        'surface-container-high': 'rgb(var(--md-sys-color-surface-container-high) / <alpha-value>)',
        'surface-container-highest': 'rgb(var(--md-sys-color-surface-container-highest) / <alpha-value>)',
        
        'on-surface': 'rgb(var(--md-sys-color-on-surface) / <alpha-value>)',
        'on-surface-variant': 'rgb(var(--md-sys-color-on-surface-variant) / <alpha-value>)',
        
        background: 'rgb(var(--md-sys-color-background) / <alpha-value>)',
        'on-background': 'rgb(var(--md-sys-color-on-background) / <alpha-value>)',
        
        outline: 'rgb(var(--md-sys-color-outline) / <alpha-value>)',
        'outline-variant': 'rgb(var(--md-sys-color-outline-variant) / <alpha-value>)',
        
        error: 'rgb(var(--md-sys-color-error) / <alpha-value>)',
        'on-error': 'rgb(var(--md-sys-color-on-error) / <alpha-value>)',
        'error-container': 'rgb(var(--md-sys-color-error-container) / <alpha-value>)',
        'on-error-container': 'rgb(var(--md-sys-color-on-error-container) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['Roboto', 'sans-serif'],
      },
      fontSize: {
        // Material Design 3 typography scale
        'display-large': ['57px', { lineHeight: '64px', letterSpacing: '-0.25px' }],
        'display-medium': ['45px', { lineHeight: '52px', letterSpacing: '0px' }],
        'display-small': ['36px', { lineHeight: '44px', letterSpacing: '0px' }],
        'headline-large': ['32px', { lineHeight: '40px', letterSpacing: '0px' }],
        'headline-medium': ['28px', { lineHeight: '36px', letterSpacing: '0px' }],
        'headline-small': ['24px', { lineHeight: '32px', letterSpacing: '0px' }],
        'title-large': ['22px', { lineHeight: '28px', letterSpacing: '0px' }],
        'title-medium': ['16px', { lineHeight: '24px', letterSpacing: '0.15px' }],
        'title-small': ['14px', { lineHeight: '20px', letterSpacing: '0.1px' }],
        'label-large': ['14px', { lineHeight: '20px', letterSpacing: '0.1px' }],
        'label-medium': ['12px', { lineHeight: '16px', letterSpacing: '0.5px' }],
        'label-small': ['11px', { lineHeight: '16px', letterSpacing: '0.5px' }],
        'body-large': ['16px', { lineHeight: '24px', letterSpacing: '0.5px' }],
        'body-medium': ['14px', { lineHeight: '20px', letterSpacing: '0.25px' }],
        'body-small': ['12px', { lineHeight: '16px', letterSpacing: '0.4px' }],
      },
      spacing: {
        // Material Design 3 spacing scale
        '18': '4.5rem',
        '22': '5.5rem',
      },
      borderRadius: {
        // Material Design 3 border radius
        'none': '0',
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '28px',
        'full': '9999px',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    // Form styles plugin for better form control styling
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
  ],
}
```

---

## Dark Mode System

### Dark Mode Implementation
The dark mode system uses Tailwind's `class` strategy combined with CSS custom properties for seamless theme switching.

#### Tailwind Dark Mode Classes
```css
/* Light mode default, dark mode variants */
.bg-surface {
  background-color: rgb(var(--md-sys-color-surface));
}

.text-on-surface {
  color: rgb(var(--md-sys-color-on-surface));
}

/* Usage in components */
.card {
  @apply bg-surface text-on-surface border-outline;
}
```

#### JavaScript Theme Toggle
```javascript
// useDarkMode composable implementation
const toggleDarkMode = () => {
  const isDark = !document.documentElement.classList.contains('dark')
  document.documentElement.classList.toggle('dark', isDark)
  localStorage.setItem('darkMode', isDark ? 'dark' : 'light')
}

// Initialize theme on page load
const initializeDarkMode = () => {
  const stored = localStorage.getItem('darkMode')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const shouldBeDark = stored ? stored === 'dark' : prefersDark
  
  document.documentElement.classList.toggle('dark', shouldBeDark)
}
```

#### Component Dark Mode Usage
```vue
<template>
  <div class="bg-surface text-on-surface border border-outline rounded-lg p-4">
    <!-- Content automatically adapts to theme -->
    <h2 class="text-headline-medium text-on-surface">Card Title</h2>
    <p class="text-body-medium text-on-surface-variant">Card content</p>
    
    <!-- Button with theme-aware styling -->
    <button class="bg-primary text-on-primary hover:bg-primary/90 px-4 py-2 rounded-full">
      Action
    </button>
  </div>
</template>
```

---

## Component Styling

### Card Components
```css
/* Base card styling */
.card {
  @apply bg-surface-container rounded-xl shadow-sm border border-outline-variant;
}

.card-elevated {
  @apply bg-surface-container-low rounded-xl shadow-md;
}

/* Card variants */
.card-filled {
  @apply bg-surface-container-high;
}

.card-outlined {
  @apply bg-surface border-2 border-outline;
}
```

### Form Components
```css
/* Custom form input styling */
.form-input {
  @apply px-3 py-2 border border-outline rounded-lg 
         bg-surface-container-highest text-on-surface
         focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
         placeholder:text-on-surface-variant;
}

.form-select {
  @apply form-input pr-10 bg-no-repeat bg-right;
}

.form-textarea {
  @apply form-input resize-vertical min-h-[100px];
}

.form-label {
  @apply block text-sm font-medium text-on-surface-variant mb-2;
}

.form-error {
  @apply text-sm text-error mt-1;
}
```

### Button Components
```css
/* Custom button variants */
.btn-filled {
  @apply bg-primary text-on-primary hover:bg-primary/90 
         px-6 py-2 rounded-full font-medium
         focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
         disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-outlined {
  @apply border-2 border-primary text-primary hover:bg-primary hover:text-on-primary
         px-6 py-2 rounded-full font-medium
         focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
         disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-text {
  @apply text-primary hover:bg-primary/10
         px-4 py-2 rounded-full font-medium
         focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
         disabled:opacity-50 disabled:cursor-not-allowed;
}
```

### Navigation Components
```css
/* Navigation styling */
.nav-link {
  @apply text-on-surface-variant hover:text-on-surface hover:bg-surface-container
         px-3 py-2 rounded-lg font-medium transition-colors;
}

.nav-link-active {
  @apply text-on-secondary-container bg-secondary-container;
}

/* Mobile navigation */
.mobile-nav {
  @apply fixed bottom-0 left-0 right-0 bg-surface-container border-t border-outline-variant;
}

.mobile-nav-item {
  @apply flex-1 flex flex-col items-center justify-center py-2
         text-on-surface-variant hover:text-on-surface;
}
```

---

## Responsive Design

### Breakpoint System
```css
/* Tailwind breakpoints */
/* sm: 640px and up */
/* md: 768px and up */
/* lg: 1024px and up */
/* xl: 1280px and up */
/* 2xl: 1536px and up */
```

### Responsive Component Examples
```vue
<template>
  <!-- Responsive grid -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    <!-- Items adapt to screen size -->
  </div>
  
  <!-- Responsive text sizes -->
  <h1 class="text-headline-small md:text-headline-medium lg:text-headline-large">
    Responsive Heading
  </h1>
  
  <!-- Responsive padding -->
  <div class="p-4 md:p-6 lg:p-8">
    Responsive padding
  </div>
  
  <!-- Hide/show on different screens -->
  <div class="block md:hidden">Mobile only</div>
  <div class="hidden md:block">Desktop only</div>
</template>
```

### Container System
```css
/* Responsive container */
.container {
  @apply mx-auto px-4 sm:px-6 lg:px-8;
  max-width: 100%;
}

@screen sm {
  .container {
    max-width: 640px;
  }
}

@screen md {
  .container {
    max-width: 768px;
  }
}

@screen lg {
  .container {
    max-width: 1024px;
  }
}

@screen xl {
  .container {
    max-width: 1280px;
  }
}
```

---

## Custom CSS Classes

### Utility Classes
```css
/* Layout utilities */
.flex-center {
  @apply flex items-center justify-center;
}

.absolute-center {
  @apply absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2;
}

/* Animation utilities */
.transition-all {
  @apply transition-all duration-200 ease-in-out;
}

.hover-scale {
  @apply hover:scale-105 transition-transform duration-200;
}

/* Text utilities */
.text-gradient {
  @apply bg-gradient-to-r from-primary to-tertiary bg-clip-text text-transparent;
}

/* Loading states */
.skeleton {
  @apply bg-surface-container-high animate-pulse rounded;
}

.shimmer {
  @apply relative overflow-hidden;
}

.shimmer::before {
  content: '';
  @apply absolute inset-0 bg-gradient-to-r from-transparent via-surface-container-highest to-transparent
         transform -translate-x-full animate-shimmer;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```

### Component-Specific Classes
```css
/* Arrow recommendation cards */
.arrow-card {
  @apply bg-surface-container rounded-lg border border-outline-variant 
         hover:shadow-md hover:bg-surface-container-high
         transition-all duration-200 cursor-pointer;
}

.arrow-card-selected {
  @apply ring-2 ring-primary border-primary bg-primary-container;
}

/* Compatibility scoring */
.compatibility-excellent {
  @apply bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200;
}

.compatibility-good {
  @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200;
}

.compatibility-poor {
  @apply bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200;
}

/* Loading indicators */
.loading-spinner {
  @apply animate-spin rounded-full h-8 w-8 border-b-2 border-primary;
}

.loading-dots::after {
  content: '';
  @apply inline-block animate-bounce;
  animation-delay: 0.1s;
}

.loading-dots::before {
  content: '•••';
  @apply animate-pulse;
}
```

---

## Best Practices

### Class Organization
```vue
<template>
  <!-- Order: Layout, Spacing, Typography, Colors, States -->
  <div class="
    flex flex-col items-center justify-center
    p-6 m-4 space-y-4
    text-lg font-medium
    bg-surface text-on-surface
    hover:bg-surface-container-high focus:ring-2 focus:ring-primary
    transition-all duration-200
  ">
    Content
  </div>
</template>
```

### Component Styling Strategy
1. **Use Tailwind First**: Start with utility classes
2. **Custom Classes for Reuse**: Create custom classes for repeated patterns
3. **Material Tokens**: Use Material Design color and typography tokens
4. **Responsive Mobile-First**: Design for mobile, enhance for desktop
5. **Dark Mode Support**: Always consider dark mode variants

### Performance Considerations
```css
/* Optimize animations */
.optimized-animation {
  @apply transform-gpu; /* Use GPU acceleration */
  will-change: transform; /* Hint browser for optimization */
}

/* Efficient transitions */
.efficient-transition {
  @apply transition-transform duration-200; /* Only animate transform */
}
```

### Accessibility Guidelines
```css
/* Focus indicators */
.focus-visible {
  @apply focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2;
}

/* Color contrast */
.high-contrast {
  @apply text-on-surface bg-surface; /* Ensures WCAG AA compliance */
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .respect-motion-preference {
    @apply transition-none animate-none;
  }
}
```

### Code Organization
```scss
// assets/css/main.css structure
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 1. CSS Custom Properties (Material Design tokens) */
:root { /* ... */ }
.dark { /* ... */ }

/* 2. Base styles and typography */
body { /* ... */ }
h1, h2, h3 { /* ... */ }

/* 3. Component styles */
.card { /* ... */ }
.form-input { /* ... */ }

/* 4. Utility classes */
.flex-center { /* ... */ }
.text-gradient { /* ... */ }

/* 5. Animation keyframes */
@keyframes fadeIn { /* ... */ }
```

This styling system documentation provides comprehensive guidance for maintaining consistent, accessible, and performant UI styling across the Archery Tools frontend.