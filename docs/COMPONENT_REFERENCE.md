# Component Reference Guide

Comprehensive reference for all Vue.js components in the Archery Tools frontend, including props, events, and usage examples.

## Component Categories

### Modal Components
Interactive dialogs for complex user operations.

### Data Display Components  
Components for displaying arrow data, recommendations, and specifications.

### UI Components
Reusable interface elements and controls.

### Feature Components
Specialized components for specific application features.

---

## Modal Components

### `AddBowSetupModal.vue`
**Purpose**: Modal for creating and editing bow setups

#### Props
```typescript
interface Props {
  modelValue: boolean          // Modal visibility
  editingSetup?: BowSetup     // Setup to edit (optional)
  isSaving?: boolean          // Loading state
  error?: string              // Error message
}
```

#### Events
```typescript
interface Emits {
  'update:modelValue': [value: boolean]
  save: [setup: BowSetup]
  close: []
}
```

#### Usage Example
```vue
<template>
  <AddBowSetupModal
    v-model="showModal"
    :editing-setup="currentSetup"
    :is-saving="saving"
    :error="errorMessage"
    @save="handleSave"
    @close="showModal = false"
  />
</template>

<script setup>
const showModal = ref(false)
const currentSetup = ref(null)
const saving = ref(false)
const errorMessage = ref('')

const handleSave = async (setup) => {
  saving.value = true
  try {
    await api.saveBowSetup(setup)
    showModal.value = false
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    saving.value = false
  }
}
</script>
```

#### Key Features
- Form validation with error display
- Support for compound, recurve, and traditional bows
- Component weight calculations
- Material Web form components
- Responsive design

---

### `ArrowSearchModal.vue`
**Purpose**: Modal for searching and selecting arrows

#### Props
```typescript
interface Props {
  modelValue: boolean
  bowConfig: BowConfiguration
  selectedSetupId?: number
}
```

#### Events
```typescript
interface Emits {
  'update:modelValue': [value: boolean]
  selectArrow: [arrow: ArrowSpecification]
  close: []
}
```

#### Usage Example
```vue
<template>
  <ArrowSearchModal
    v-model="showArrowSearch"
    :bow-config="bowConfiguration"
    :selected-setup-id="setupId"
    @select-arrow="handleArrowSelection"
  />
</template>
```

#### Key Features
- Advanced arrow filtering
- Real-time search
- Compatibility scoring
- Responsive arrow cards

---

### `EditArrowModal.vue` 
**Purpose**: Modal for editing arrow configuration in setups

#### Props
```typescript
interface Props {
  arrow: SetupArrow           // Arrow to edit
  setupId: number            // Bow setup ID
}
```

#### Events
```typescript
interface Emits {
  save: [updatedArrow: SetupArrow]
  close: []
}
```

#### Key Features
- Arrow length adjustment
- Point weight modification  
- Component weight tracking
- Total weight calculation

---

## Data Display Components

### `ArrowRecommendationsList.vue`
**Purpose**: Display arrow recommendations with filtering and selection

#### Props
```typescript
interface Props {
  bowConfig: BowConfiguration
  showSearchFilters: boolean
  selectedBowSetup?: BowSetup
}
```

#### Events
```typescript
interface Emits {
  arrowAddedToSetup: [data: { arrow: ArrowSpecification, setup: BowSetup }]
}
```

#### Usage Example
```vue
<template>
  <ArrowRecommendationsList
    :bow-config="bowConfig"
    :show-search-filters="true"
    :selected-bow-setup="currentSetup"
    @arrow-added-to-setup="handleArrowAdded"
  />
</template>
```

#### Key Features
- **Advanced Filtering**: Manufacturer, spine range, GPI weight, diameter
- **Real-time Search**: Instant filtering as user types
- **Compatibility Scoring**: Visual match percentage display
- **Responsive Design**: Card layout adapts to screen size
- **Add to Setup**: Direct integration with bow setups

#### Internal State Management
```typescript
const filters = reactive({
  search: '',
  manufacturer: '',
  spine_min: null,
  spine_max: null,
  gpi_min: null,
  gpi_max: null,
  diameter_category: ''
})

const recommendations = ref<ArrowRecommendation[]>([])
const loading = ref(false)
const stats = ref(null)
```

---

### `BowSetupArrowsList.vue`
**Purpose**: Display arrows selected for a specific bow setup

#### Props
```typescript
interface Props {
  arrows: SetupArrow[]       // Selected arrows
  loading?: boolean          // Loading state
  detailed?: boolean         // Show detailed information
}
```

#### Events
```typescript
interface Emits {
  removeArrow: [arrowId: number]
  viewDetails: [arrow: SetupArrow]
  editArrow: [arrow: SetupArrow]
}
```

#### Usage Example
```vue
<template>
  <BowSetupArrowsList
    :arrows="setupArrows"
    :loading="loadingArrows"
    :detailed="true"
    @remove-arrow="removeArrowFromSetup"
    @view-details="viewArrowDetails"
    @edit-arrow="openEditModal"
  />
</template>
```

#### Key Features
- **Arrow Specifications**: Complete specs display with spine data
- **Weight Calculations**: Total arrow weight with component breakdown
- **Configuration Display**: Arrow length, point weight, custom configurations
- **Action Buttons**: Edit, remove, and view details
- **Responsive Cards**: Mobile-optimized layout

#### Data Structure
```typescript
interface SetupArrow {
  id: number
  setup_id: number
  arrow_id: number
  arrow_length: number
  point_weight: number
  calculated_spine: string
  compatibility_score: number
  arrow: {
    manufacturer: string
    model_name: string
    material: string
    spine_specifications: SpineSpecification[]
  }
}
```

---

### `AdminArrowsTable.vue`
**Purpose**: Administrative table for managing arrow database

#### Props
```typescript
interface Props {
  arrows: ArrowSpecification[]
  loading?: boolean
  totalCount?: number
  currentPage?: number
}
```

#### Events
```typescript
interface Emits {
  editArrow: [arrow: ArrowSpecification]
  deleteArrow: [arrowId: number]
  pageChange: [page: number]
}
```

#### Key Features
- **Sortable Columns**: Click to sort by manufacturer, model, material
- **Pagination**: Navigate through large datasets
- **Bulk Actions**: Select multiple arrows for operations
- **Search Integration**: Real-time filtering
- **Edit/Delete Actions**: Direct arrow management

---

## UI Components

### `CustomButton.vue`
**Purpose**: Fallback button component with Material Design styling

#### Props
```typescript
interface Props {
  variant?: 'filled' | 'outlined' | 'text'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
  class?: string
}
```

#### Usage Example
```vue
<template>
  <CustomButton
    variant="filled"
    size="medium"
    :disabled="loading"
    @click="handleClick"
  >
    <i class="fas fa-save mr-2"></i>
    Save Changes
  </CustomButton>
</template>
```

#### Styling Variants
```css
/* Filled variant */
.btn-filled {
  @apply bg-blue-600 text-white hover:bg-blue-700 px-6 py-2 rounded-full font-medium;
}

/* Outlined variant */
.btn-outlined {
  @apply border-2 border-blue-600 text-blue-600 hover:bg-blue-50 px-6 py-2 rounded-full font-medium;
}

/* Text variant */
.btn-text {
  @apply text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-full font-medium;
}
```

---

### `DarkModeToggle.vue`
**Purpose**: Toggle between light and dark themes

#### Props
```typescript
interface Props {
  size?: 'small' | 'medium' | 'large'
  showLabel?: boolean
}
```

#### Usage Example
```vue
<template>
  <DarkModeToggle 
    size="medium" 
    :show-label="true" 
  />
</template>
```

#### Key Features
- **Persistent Storage**: Remembers user preference
- **System Preference**: Respects OS dark mode setting
- **Smooth Transitions**: Animated theme switching
- **Icon Updates**: Dynamic sun/moon icons
- **SSR Compatible**: Works with server-side rendering

#### Implementation Details
```typescript
const { isDark, toggleDarkMode } = useDarkMode()

const handleToggle = () => {
  toggleDarkMode()
  // Optional callback for analytics
  trackEvent('theme_changed', { theme: isDark.value ? 'dark' : 'light' })
}
```

---

### `MobileBottomNav.vue`
**Purpose**: Mobile navigation bar with primary actions

#### Props
```typescript
interface Props {
  currentRoute: string
  showLabels?: boolean
}
```

#### Usage Example
```vue
<template>
  <MobileBottomNav 
    :current-route="$route.path"
    :show-labels="true"
  />
</template>
```

#### Navigation Items
```typescript
const navItems = [
  { name: 'Home', path: '/', icon: 'fas fa-home' },
  { name: 'Calculator', path: '/calculator', icon: 'fas fa-calculator' },
  { name: 'Database', path: '/database', icon: 'fas fa-search' },
  { name: 'Profile', path: '/my-page', icon: 'fas fa-user' }
]
```

---

## Feature Components

### `GuideWalkthrough.vue`
**Purpose**: Interactive step-by-step tuning guides

#### Props
```typescript
interface Props {
  guideType: string          // Guide identifier
  steps: GuideStep[]         // Guide steps
  currentStep: number        // Current step index
  bowConfig?: BowConfiguration
}
```

#### Events
```typescript
interface Emits {
  stepComplete: [stepIndex: number, data: any]
  guideComplete: [results: GuideResults]
  pause: []
  resume: []
}
```

#### Usage Example
```vue
<template>
  <GuideWalkthrough
    guide-type="paper_tuning"
    :steps="paperTuningSteps"
    :current-step="currentStep"
    :bow-config="bowConfiguration"
    @step-complete="handleStepComplete"
    @guide-complete="handleGuideComplete"
  />
</template>
```

#### Guide Step Structure
```typescript
interface GuideStep {
  id: string
  title: string
  description: string
  instructions: string[]
  image?: string
  video?: string
  inputs?: GuideInput[]
  validation?: ValidationRule[]
}

interface GuideInput {
  name: string
  type: 'text' | 'number' | 'select' | 'checkbox'
  label: string
  options?: string[]
  required?: boolean
}
```

#### Key Features
- **Progress Tracking**: Visual progress bar and step indicators
- **Interactive Inputs**: Form inputs for measurements and observations
- **Media Support**: Images and videos for instruction clarity
- **Validation**: Input validation with error messages
- **Session Persistence**: Resume guides later
- **Multiple Guides**: Paper tuning, sight setup, etc.

---

### `ImageUpload.vue`
**Purpose**: Handle image uploads with preview and validation

#### Props
```typescript
interface Props {
  modelValue: File | null
  accept?: string            // File type restrictions
  maxSize?: number          // Max file size in MB
  preview?: boolean         // Show image preview
  multiple?: boolean        // Allow multiple files
}
```

#### Events
```typescript
interface Emits {
  'update:modelValue': [file: File | File[] | null]
  upload: [file: File]
  error: [message: string]
}
```

#### Usage Example
```vue
<template>
  <ImageUpload
    v-model="selectedImage"
    accept="image/*"
    :max-size="5"
    :preview="true"
    @upload="handleImageUpload"
    @error="handleError"
  />
</template>
```

#### Key Features
- **Drag and Drop**: File drop zone
- **Preview Generation**: Automatic image previews
- **File Validation**: Size and type checking
- **Progress Tracking**: Upload progress indication
- **Error Handling**: User-friendly error messages

---

## Component Usage Patterns

### Composition API Patterns

#### State Management
```typescript
// Component state with reactivity
const state = reactive({
  loading: false,
  data: [],
  error: null,
  filters: {
    search: '',
    category: ''
  }
})

// Computed properties
const filteredData = computed(() => {
  return state.data.filter(item => 
    item.name.toLowerCase().includes(state.filters.search.toLowerCase())
  )
})
```

#### API Integration
```typescript
// Using composables for API calls
const { data, loading, error, refetch } = useAsyncData('arrows', () => 
  api.getArrows(state.filters)
)

// Manual API calls
const fetchData = async () => {
  state.loading = true
  try {
    const response = await api.getData()
    state.data = response.data
  } catch (err) {
    state.error = err.message
  } finally {
    state.loading = false
  }
}
```

#### Event Handling
```typescript
// Emit events to parent components
const emit = defineEmits<{
  save: [data: FormData]
  cancel: []
  error: [message: string]
}>()

const handleSave = async (formData: FormData) => {
  try {
    await saveData(formData)
    emit('save', formData)
  } catch (error) {
    emit('error', error.message)
  }
}
```

### Material Web Integration

#### Form Components
```vue
<template>
  <form @submit.prevent="handleSubmit">
    <md-filled-text-field
      v-model="formData.name"
      label="Name"
      required
      :error="errors.name"
    ></md-filled-text-field>
    
    <md-filled-select
      v-model="formData.category"
      label="Category"
    >
      <md-select-option value="option1">Option 1</md-select-option>
      <md-select-option value="option2">Option 2</md-select-option>
    </md-filled-select>
    
    <md-filled-button type="submit">
      Submit
    </md-filled-button>
  </form>
</template>
```

#### Navigation Components
```vue
<template>
  <md-navigation-drawer>
    <md-navigation-drawer-item 
      v-for="item in navItems" 
      :key="item.path"
      :active="$route.path === item.path"
      @click="navigateTo(item.path)"
    >
      <md-icon slot="icon">{{ item.icon }}</md-icon>
      {{ item.label }}
    </md-navigation-drawer-item>
  </md-navigation-drawer>
</template>
```

### Responsive Design Patterns

#### Mobile-First Approach
```vue
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Responsive grid layout -->
  </div>
  
  <!-- Mobile-specific components -->
  <MobileBottomNav class="md:hidden" />
  
  <!-- Desktop-specific components -->
  <SidebarNav class="hidden md:block" />
</template>
```

#### Conditional Rendering
```vue
<template>
  <!-- Show different layouts based on screen size -->
  <div class="block md:hidden">
    <!-- Mobile layout -->
    <MobileArrowCard :arrow="arrow" />
  </div>
  
  <div class="hidden md:block">
    <!-- Desktop layout -->
    <DesktopArrowTable :arrows="arrows" />
  </div>
</template>
```

This component reference provides comprehensive documentation for all major components in the frontend, including their interfaces, usage patterns, and integration examples.