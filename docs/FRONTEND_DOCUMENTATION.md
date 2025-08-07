# Frontend Documentation - Nuxt 3 Architecture

Comprehensive documentation for the Archery Tools frontend built with Nuxt 3, Vue.js 3, and Material Web Components.

## Table of Contents
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Pages & Routing](#pages--routing)
- [Components Architecture](#components-architecture)
- [State Management](#state-management)
- [Styling System](#styling-system)
- [Authentication & Security](#authentication--security)
- [Development Workflow](#development-workflow)
- [Build & Deployment](#build--deployment)

---

## Technology Stack

### Core Framework
- **Nuxt 3** (v3.17.7) - Vue.js full-stack framework with SSR/SPA
- **Vue.js 3** (v3.3.8) - Progressive JavaScript framework with Composition API
- **TypeScript** - Type-safe development with strict typing disabled for flexibility

### UI & Styling
- **Material Web Components** (@material/web v2.3.0) - Google's official Material Design 3 components
- **Tailwind CSS** (v6.8.4) - Utility-first CSS framework
- **Font Awesome** (v7.0.0) - Icon library for additional icons
- **Google Fonts** - Roboto font family and Material Symbols

### State Management & Data
- **Pinia** (v2.1.7) - Vue.js state management with @pinia/nuxt integration
- **Custom Composables** - Reusable composition functions for API, auth, and utilities

### Authentication & External Services
- **vue3-google-login** (v2.0.33) - Google OAuth integration
- **JWT Tokens** - Secure authentication with localStorage persistence

### Development Tools
- **Nuxt DevTools** - Enhanced development experience
- **TypeScript Support** - Type definitions and IntelliSense
- **Hot Module Replacement** - Fast development iteration

---

## Project Structure

```
frontend/
├── assets/                     # Static assets
│   ├── css/
│   │   └── main.css           # Main Tailwind CSS + Material theming
│   └── images/
│       └── guides/            # Guide illustration assets
├── components/                 # Vue.js components
│   ├── Modal Components/       # User interaction modals
│   │   ├── AddBowSetupModal.vue
│   │   ├── ArrowSearchModal.vue
│   │   ├── EditArrowModal.vue
│   │   └── ConfirmDeleteModal.vue
│   ├── Data Display Components/
│   │   ├── ArrowRecommendationsList.vue
│   │   ├── BowSetupArrowsList.vue
│   │   ├── AdminArrowsTable.vue
│   │   └── SavedArrowSetups.vue
│   ├── UI Components/
│   │   ├── CustomButton.vue    # Fallback button component
│   │   ├── DarkModeToggle.vue  # Theme switching
│   │   └── MobileBottomNav.vue # Mobile navigation
│   └── Feature Components/
│       ├── GuideWalkthrough.vue # Interactive guides
│       ├── ImageUpload.vue     # Image handling
│       └── ArrowConfigurationsList.vue
├── composables/               # Vue 3 composition functions
│   ├── useApi.ts             # API communication layer
│   ├── useAuth.ts            # Authentication management
│   ├── useDarkMode.js        # Dark mode state
│   └── useMaterialWeb.ts     # Material Web utilities
├── layouts/
│   └── default.vue           # Main application layout
├── middleware/               # Route middleware
│   ├── auth-check.ts         # Authentication verification
│   ├── auth.global.ts        # Global authentication state
│   └── redirect-to-login.ts  # Login redirection
├── pages/                    # File-based routing (Nuxt 3)
│   ├── index.vue            # Home page
│   ├── calculator.vue       # Arrow calculator
│   ├── database.vue         # Arrow database browser
│   ├── my-page.vue          # User profile & bow setups
│   ├── admin.vue            # Admin panel
│   ├── arrows/[id].vue      # Dynamic arrow detail pages
│   ├── bow/[id].vue         # Dynamic bow detail pages
│   ├── guides/              # Interactive tuning guides
│   └── tuning/              # Tuning session management
├── plugins/                 # Nuxt plugins
│   ├── material-web.client.ts    # Material Web setup
│   ├── google-login.client.ts    # Google OAuth
│   └── fix-material-buttons.client.ts # Button styling fixes
├── stores/                  # Pinia state management
│   └── bowConfig.ts         # Bow configuration store
├── types/                   # TypeScript definitions
│   └── arrow.ts             # Complete type definitions
├── nuxt.config.ts          # Nuxt configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── package.json            # Dependencies and scripts
```

---

## Configuration

### Nuxt Configuration (`nuxt.config.ts`)

**Key Features:**
- **SSR Enabled**: Server-side rendering for SEO and performance
- **Material Web Integration**: Custom element support for md- components
- **API Configuration**: Runtime config for backend communication
- **Security Headers**: CSP and COOP policies for secure operation
- **Dark Mode**: Default dark theme with SSR compatibility

**Environment Variables:**
```env
NUXT_PUBLIC_API_BASE=http://localhost:5000/api  # API base URL
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id     # Google OAuth
NODE_ENV=development                            # Environment
```

**Runtime Configuration:**
```typescript
runtimeConfig: {
  public: {
    apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5000/api',
    googleClientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID
  }
}
```

### Tailwind Configuration (`tailwind.config.js`)

**Material Design 3 Integration:**
- Custom color palette with CSS variables
- Dark mode support with 'class' strategy
- Material typography scale
- Responsive breakpoints

**Key Features:**
```javascript
theme: {
  extend: {
    colors: {
      primary: 'rgb(var(--md-sys-color-primary) / <alpha-value>)',
      surface: 'rgb(var(--md-sys-color-surface) / <alpha-value>)',
      // Complete Material color system
    },
    fontFamily: {
      sans: ['Roboto', 'sans-serif'],
    }
  }
}
```

---

## Pages & Routing

### Core Pages

#### `pages/index.vue` - Home Page
**Purpose**: Landing page with platform overview and quick access
**Features**:
- Beta notice banner
- Feature highlights grid
- Quick access to Calculator and Database
- Responsive design with mobile optimization

#### `pages/calculator.vue` - Arrow Calculator
**Purpose**: Professional spine calculation and arrow recommendations
**Features**:
- Bow configuration form with Material Web components
- Real-time spine calculations
- Arrow recommendations with compatibility scoring
- Bow setup integration and selection
- Advanced component weight calculations

**Key Components Used:**
- `ArrowRecommendationsList.vue` - Displays recommendations
- Pinia `bowConfig` store - State management
- `useApi` composable - Backend communication

#### `pages/database.vue` - Arrow Database
**Purpose**: Browse and search arrow specifications
**Features**:
- Advanced filtering (manufacturer, spine, diameter, material)
- Pagination and sorting
- Database statistics display
- Arrow detail navigation

#### `pages/my-page.vue` - User Profile & Bow Management
**Purpose**: Personal user dashboard and bow setup management
**Features**:
- User profile editing
- Bow setup cards with simplified display
- Navigation to detailed bow pages
- Profile customization (draw length, shooting style, preferences)

#### `pages/bow/[id].vue` - Bow Detail Pages
**Purpose**: Comprehensive bow setup management and arrow selection
**Features**:
- Complete bow specifications display
- Selected arrows management
- Add/remove arrows from setup
- Edit bow configuration
- Component weight tracking

### Dynamic Routing

#### `pages/arrows/[id].vue` - Arrow Detail Pages
**Route**: `/arrows/:id`
**Purpose**: Detailed arrow specifications and compatibility
**Data Loading**: Server-side arrow specification fetching

#### `pages/guides/[slug].vue` - Interactive Tuning Guides
**Route**: `/guides/:slug`
**Available Guides**:
- Paper tuning walkthrough
- Sight setup procedures
- Draw length measurement
- Equipment maintenance

### Admin Pages

#### `pages/admin.vue` - Admin Panel
**Access**: Requires `is_admin: true`
**Features**:
- User management interface
- Arrow database editing
- Backup and restore operations
- System administration tools

---

## Components Architecture

### Component Categories

#### 1. Modal Components
Complex user interaction dialogs with form handling.

**`AddBowSetupModal.vue`**
```vue
<template>
  <div class="modal-overlay">
    <form @submit.prevent="saveBowSetup">
      <!-- Bow configuration form -->
    </form>
  </div>
</template>

<script setup>
// Props, emits, and form logic
defineProps<{
  modelValue: boolean
  editingSetup?: BowSetup
}>()

defineEmits<{
  close: []
  save: [setup: BowSetup]
}>()
</script>
```

**Key Features:**
- Form validation and error handling
- Material Web form components
- Reactive form state management
- Emit-based parent communication

#### 2. Data Display Components

**`ArrowRecommendationsList.vue`**
**Purpose**: Display arrow recommendations with advanced filtering
**Props**:
```typescript
interface Props {
  bowConfig: BowConfiguration
  showSearchFilters: boolean
  selectedBowSetup?: BowSetup
}
```

**Key Features:**
- Real-time filtering and search
- Compatibility scoring display
- Manufacturer filtering with dropdowns
- Responsive card layout
- Add to setup functionality

**`BowSetupArrowsList.vue`**
**Purpose**: Display selected arrows for a bow setup
**Features**:
- Arrow specification display
- Remove arrow functionality
- Configuration editing
- Total weight calculations

#### 3. UI Components

**`CustomButton.vue`** - Fallback Button Component
**Purpose**: Material Design button with fallback styling
```vue
<template>
  <button 
    :class="buttonClasses"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup>
interface Props {
  variant?: 'filled' | 'outlined' | 'text'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
}
</script>
```

**`DarkModeToggle.vue`** - Theme Switching Component
**Features**:
- Material Web icon button
- Persistent theme preference
- Smooth theme transitions
- SSR compatibility

### Component Communication Patterns

#### Parent-Child Communication
```vue
<!-- Parent Component -->
<AddBowSetupModal
  v-model="showModal"
  :editing-setup="currentSetup"
  @save="handleSave"
  @close="showModal = false"
/>

<!-- Child Component -->
<script setup>
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  save: [setup: BowSetup]
  close: []
}>()

const saveBowSetup = (setup: BowSetup) => {
  emit('save', setup)
  emit('update:modelValue', false)
}
</script>
```

#### Store Integration
```vue
<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'

const bowConfigStore = useBowConfigStore()
const { bowConfig, recommendedSpine } = storeToRefs(bowConfigStore)
const { updateBowConfig, calculateRecommendedSpine } = bowConfigStore

// Reactive store integration
watch(bowConfig, () => {
  calculateRecommendedSpine()
}, { deep: true })
</script>
```

---

## State Management

### Pinia Store Architecture

#### `stores/bowConfig.ts` - Bow Configuration Store

**State Management:**
```typescript
const bowConfig = ref<BowConfiguration>({
  draw_weight: 45,
  draw_length: user.value?.draw_length || 28,
  bow_type: 'compound',
  arrow_length: 29,
  point_weight: 125,
  arrow_material: 'carbon',
  // ... additional configuration
})

const recommendedSpine = ref<number | string | null>(null)
const recommendations = ref<ArrowRecommendation[]>([])
```

**Key Actions:**
- `updateBowConfig(updates: Partial<BowConfiguration>)` - Update configuration
- `calculateRecommendedSpine()` - Calculate spine recommendations
- `getArrowRecommendations()` - Fetch arrow recommendations
- `syncWithUserProfile()` - Sync with user profile data

**Computed Properties:**
```typescript
const isCompoundBow = computed(() => bowConfig.value.bow_type === 'compound')
const arrowSetupDescription = computed(() => 
  `${bowConfig.value.arrow_length}" ${bowConfig.value.arrow_material} arrow with ${bowConfig.value.point_weight}gn point`
)
```

**Reactive Updates:**
```typescript
// Automatic recalculation on configuration changes
watch(shouldRecalculate, async () => {
  await nextTick()
  setTimeout(() => {
    calculateRecommendedSpine()
  }, 500)
}, { deep: true })
```

### Store Usage Patterns

#### Component Integration
```vue
<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'

const bowConfigStore = useBowConfigStore()

// Reactive references
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)

// Actions
const { updateBowConfig } = bowConfigStore

// Update configuration
const handleDrawWeightChange = (weight: number) => {
  updateBowConfig({ draw_weight: weight })
}
</script>
```

---

## Styling System

### Tailwind CSS + Material Design 3

#### CSS Architecture (`assets/css/main.css`)

**Material Design 3 Variables:**
```css
:root {
  /* Light theme colors */
  --md-sys-color-primary: 103 80 164;
  --md-sys-color-surface: 255 255 255;
  --md-sys-color-on-surface: 28 27 31;
  /* ... complete color system */
}

.dark {
  /* Dark theme colors */
  --md-sys-color-primary: 208 188 255;
  --md-sys-color-surface: 16 16 20;
  --md-sys-color-on-surface: 230 225 229;
  /* ... complete dark color system */
}
```

**Component Styling:**
```css
/* Material Web Component Theming */
md-filled-button {
  --md-filled-button-container-color: rgb(var(--md-sys-color-primary));
  --md-filled-button-label-text-color: rgb(var(--md-sys-color-on-primary));
}

/* Custom Component Classes */
.card {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700;
}

.form-input {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600;
}
```

#### Dark Mode Implementation

**Theme Toggle Logic:**
```javascript
// useDarkMode.js
export const useDarkMode = () => {
  const isDark = ref(false)

  const toggleDarkMode = () => {
    isDark.value = !isDark.value
    document.documentElement.classList.toggle('dark', isDark.value)
    localStorage.setItem('darkMode', isDark.value ? 'dark' : 'light')
  }

  // Initialize from localStorage
  onMounted(() => {
    const stored = localStorage.getItem('darkMode')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    isDark.value = stored ? stored === 'dark' : prefersDark
    document.documentElement.classList.toggle('dark', isDark.value)
  })

  return { isDark, toggleDarkMode }
}
```

#### Responsive Design

**Breakpoint Strategy:**
```css
/* Mobile-first approach */
.container {
  @apply px-4 mx-auto;
}

@screen sm {
  .container {
    @apply max-w-screen-sm px-6;
  }
}

@screen md {
  .container {
    @apply max-w-screen-md px-8;
  }
}

@screen lg {
  .container {
    @apply max-w-screen-lg;
  }
}
```

### Material Web Components Integration

#### Component Registration
```typescript
// plugins/material-web.client.ts
import '@material/web/all'

export default defineNuxtPlugin(() => {
  // Material Web components are automatically registered
  // Custom element support configured in nuxt.config.ts
})
```

#### Component Usage Patterns
```vue
<template>
  <md-filled-select 
    :value="selectedValue" 
    @change="handleChange($event.target.value)"
    label="Select Option"
  >
    <md-select-option value="option1">
      <div slot="headline">Option 1</div>
    </md-select-option>
  </md-filled-select>
</template>
```

---

## Authentication & Security

### Google OAuth Integration

#### Authentication Flow
```typescript
// composables/useAuth.ts
export const useAuth = () => {
  const user = ref<UserProfile | null>(null)
  const token = ref<string | null>(null)

  const loginWithGoogle = async (tokenResponse: any) => {
    try {
      const response = await api.post('/auth/google', {
        token: tokenResponse.access_token
      })
      
      token.value = response.token
      user.value = response.user
      
      // Store token in localStorage
      localStorage.setItem('token', response.token)
      
      return { needsProfileCompletion: response.needsProfileCompletion }
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  return { user, token, loginWithGoogle, logout, fetchUser }
}
```

#### Route Protection
```typescript
// middleware/auth-check.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { user } = useAuth()
  
  if (!user.value) {
    return navigateTo('/login')
  }
})
```

#### JWT Token Management
```typescript
// API requests with authentication
const api = useApi()
const token = process.client ? localStorage.getItem('token') : null

const headers = {
  'Content-Type': 'application/json',
  ...(token && { 'Authorization': `Bearer ${token}` })
}
```

### Security Features

#### Content Security Policy
```typescript
// nuxt.config.ts
nitro: {
  headers: {
    'Content-Security-Policy': "default-src 'self'; connect-src 'self' http://localhost https://accounts.google.com; script-src 'self' 'unsafe-inline' https://accounts.google.com;"
  }
}
```

#### Cross-Origin Protection
```typescript
headers: {
  'Cross-Origin-Opener-Policy': 'unsafe-none'
}
```

---

## Development Workflow

### Development Commands

```bash
# Install dependencies
npm install

# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Generate static site
npm run generate

# Prepare Nuxt (run after dependency changes)
npm run postinstall
```

### Development Server
- **URL**: http://localhost:3000
- **Hot Module Replacement**: Automatic component reloading
- **TypeScript**: Real-time type checking
- **DevTools**: Nuxt DevTools integration

### File Structure Conventions

#### Pages
- Use kebab-case for file names: `my-page.vue`
- Dynamic routes with brackets: `[id].vue`
- Nested routes with directories: `guides/paper-tuning.vue`

#### Components
- Use PascalCase: `ArrowRecommendationsList.vue`
- Group by functionality in subdirectories
- Include TypeScript props and emits definitions

#### Composables
- Use camelCase with 'use' prefix: `useApi.ts`
- Export default function with same name
- Include TypeScript return type definitions

### Code Style Guidelines

#### Vue.js Components
```vue
<template>
  <!-- Use semantic HTML -->
  <main class="container">
    <!-- Prefer composition over options API -->
    <section v-if="loading">Loading...</section>
  </main>
</template>

<script setup lang="ts">
// Import order: Vue, composables, components, types
import { ref, computed } from 'vue'
import { useApi } from '~/composables/useApi'
import type { ArrowSpecification } from '~/types/arrow'

// Props with TypeScript
interface Props {
  arrowId: number
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: true
})

// Emits with TypeScript
interface Emits {
  select: [arrow: ArrowSpecification]
  close: []
}

const emit = defineEmits<Emits>()

// Reactive state
const loading = ref(false)
const arrow = ref<ArrowSpecification | null>(null)

// Computed properties
const arrowTitle = computed(() => 
  arrow.value ? `${arrow.value.manufacturer} ${arrow.value.model_name}` : 'Loading...'
)

// Methods
const handleSelect = () => {
  if (arrow.value) {
    emit('select', arrow.value)
  }
}
</script>

<style scoped>
/* Use Tailwind classes primarily */
/* Custom CSS only when necessary */
</style>
```

#### TypeScript Usage
```typescript
// Type definitions
interface ComponentState {
  loading: boolean
  data: ArrowSpecification[]
  error: string | null
}

// Composable patterns
export const useArrowData = () => {
  const state = reactive<ComponentState>({
    loading: false,
    data: [],
    error: null
  })

  const fetchArrows = async (filters: ArrowSearchFilters) => {
    state.loading = true
    try {
      const response = await api.getArrows(filters)
      state.data = response.arrows
    } catch (error) {
      state.error = error.message
    } finally {
      state.loading = false
    }
  }

  return {
    ...toRefs(state),
    fetchArrows
  }
}
```

---

## Build & Deployment

### Build Process

#### Development Build
```bash
npm run dev
# Features:
# - Hot module replacement
# - Source maps
# - Development warnings
# - TypeScript checking
```

#### Production Build
```bash
npm run build
# Output: .output/
# Features:
# - Code minification
# - Tree shaking
# - Bundle optimization
# - Static asset optimization
```

#### Static Generation
```bash
npm run generate
# Output: .output/public/
# Features:
# - Pre-rendered HTML
# - Static site deployment
# - SEO optimization
```

### Deployment Configurations

#### Environment Variables
```bash
# Development
NODE_ENV=development
NUXT_PUBLIC_API_BASE=http://localhost:5000/api
NUXT_PUBLIC_GOOGLE_CLIENT_ID=dev_client_id

# Production
NODE_ENV=production  
NUXT_PUBLIC_API_BASE=https://yourdomain.com/api
NUXT_PUBLIC_GOOGLE_CLIENT_ID=prod_client_id
```

#### Docker Deployment
```dockerfile
# frontend/Dockerfile.enhanced
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/.output .output
COPY --from=build /app/package*.json ./

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

#### Production Optimization

**Bundle Analysis:**
```bash
# Analyze bundle size
npm run build --analyze

# Check for unused dependencies
npm run build --unused
```

**Performance Features:**
- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Component and route lazy loading
- **Image Optimization**: Automatic image compression
- **CSS Optimization**: Critical CSS inlining
- **Caching**: Browser and CDN caching headers

### Deployment Checklist

#### Pre-deployment
- [ ] Run `npm run build` successfully
- [ ] Test production build with `npm run preview`
- [ ] Verify all environment variables are set
- [ ] Check TypeScript compilation
- [ ] Test authentication flow
- [ ] Verify Material Web components render correctly

#### Post-deployment
- [ ] Verify frontend loads correctly
- [ ] Test API connectivity
- [ ] Check authentication integration
- [ ] Verify dark mode functionality
- [ ] Test responsive design on mobile
- [ ] Confirm SEO meta tags are present

This comprehensive frontend documentation provides developers with everything needed to understand, develop, and maintain the Nuxt 3 frontend of the Archery Tools platform.