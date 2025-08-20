<template>
  <div class="mobile-card-stack" :class="stackClasses">
    <!-- Mobile-Optimized Card Grid -->
    <div 
      class="card-grid"
      :class="gridClasses"
    >
      <div
        v-for="(item, index) in items"
        :key="getItemKey(item, index)"
        class="card-item"
        :class="getCardClasses(item, index)"
        @click="handleCardClick(item, index)"
        @touchstart="handleTouchStart($event, item, index)"
        @touchmove="handleTouchMove($event, item, index)"
        @touchend="handleTouchEnd($event, item, index)"
      >
        <!-- Card Content Slot -->
        <slot 
          name="card" 
          :item="item" 
          :index="index"
          :isExpanded="expandedCard === getItemKey(item, index)"
          :toggleExpansion="() => toggleExpansion(getItemKey(item, index))"
        >
          <!-- Default Card Content -->
          <div class="default-card">
            <h3 class="mobile-heading-3">{{ item.title || item.name || `Item ${index + 1}` }}</h3>
            <p class="mobile-body-medium text-gray-600 dark:text-gray-400">
              {{ item.description || item.subtitle || 'No description available' }}
            </p>
          </div>
        </slot>

        <!-- Card Actions Overlay -->
        <div 
          v-if="showActions && swipeState[getItemKey(item, index)]"
          class="card-actions-overlay"
          :class="getActionsOverlayClasses(item, index)"
        >
          <!-- Left Actions -->
          <div class="actions-left" v-if="swipeState[getItemKey(item, index)].showActionsLeft">
            <slot 
              name="actions-left" 
              :item="item" 
              :index="index"
              :closeActions="() => resetSwipe(getItemKey(item, index))"
            >
              <button class="action-button action-edit" @click.stop="$emit('edit', item, index)">
                <i class="fas fa-edit"></i>
              </button>
            </slot>
          </div>

          <!-- Right Actions -->
          <div class="actions-right" v-if="swipeState[getItemKey(item, index)].showActions">
            <slot 
              name="actions-right" 
              :item="item" 
              :index="index"
              :closeActions="() => resetSwipe(getItemKey(item, index))"
            >
              <button class="action-button action-delete" @click.stop="$emit('delete', item, index)">
                <i class="fas fa-trash"></i>
              </button>
            </slot>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="items.length === 0" class="empty-state">
      <slot name="empty">
        <div class="text-center py-12">
          <i class="fas fa-inbox text-4xl text-gray-300 dark:text-gray-600 mb-4"></i>
          <h3 class="mobile-heading-3 text-gray-500 dark:text-gray-400 mb-2">{{ emptyTitle }}</h3>
          <p class="mobile-body-medium text-gray-400 dark:text-gray-500">{{ emptyMessage }}</p>
        </div>
      </slot>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div v-for="n in loadingCount" :key="n" class="loading-card">
        <div class="animate-pulse space-y-3 p-4">
          <div class="flex justify-between items-start">
            <div class="space-y-2 flex-1">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
          </div>
          <div class="space-y-2">
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

// Props
const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingCount: {
    type: Number,
    default: 3
  },
  layout: {
    type: String,
    default: 'responsive', // 'single', 'responsive', 'masonry'
    validator: (value) => ['single', 'responsive', 'masonry'].includes(value)
  },
  spacing: {
    type: String,
    default: 'normal', // 'tight', 'normal', 'relaxed'
    validator: (value) => ['tight', 'normal', 'relaxed'].includes(value)
  },
  showActions: {
    type: Boolean,
    default: true
  },
  expandable: {
    type: Boolean,
    default: false
  },
  itemKey: {
    type: String,
    default: 'id'
  },
  emptyTitle: {
    type: String,
    default: 'No Items'
  },
  emptyMessage: {
    type: String,
    default: 'There are no items to display.'
  }
})

// Emits
const emit = defineEmits(['click', 'edit', 'delete', 'expand', 'action'])

// State
const expandedCard = ref(null)
const swipeState = ref({})
const touchStartX = ref(0)
const touchStartY = ref(0)
const touchStartTime = ref(0)

// Computed
const stackClasses = computed(() => ({
  [`spacing-${props.spacing}`]: true,
  'expandable': props.expandable,
  'show-actions': props.showActions
}))

const gridClasses = computed(() => {
  const baseClasses = 'w-full'
  
  switch (props.layout) {
    case 'single':
      return `${baseClasses} grid grid-cols-1 gap-3 md-mobile:gap-4`
    case 'responsive':
      return `${baseClasses} grid grid-cols-1 md-mobile:grid-cols-2 lg-mobile:grid-cols-2 md:grid-cols-2 xl:grid-cols-3 gap-3 md-mobile:gap-4`
    case 'masonry':
      return `${baseClasses} columns-1 md-mobile:columns-2 lg-mobile:columns-2 md:columns-2 xl:columns-3 gap-3 md-mobile:gap-4`
    default:
      return `${baseClasses} grid grid-cols-1 md-mobile:grid-cols-2 gap-3 md-mobile:gap-4`
  }
})

// Methods
const getItemKey = (item, index) => {
  return item[props.itemKey] || item.id || index
}

const getCardClasses = (item, index) => {
  const key = getItemKey(item, index)
  const baseClasses = [
    'mobile-card',
    'bg-white dark:bg-gray-800',
    'rounded-xl border border-gray-200 dark:border-gray-700',
    'shadow-sm hover:shadow-lg',
    'transition-all duration-300',
    'cursor-pointer touch-target',
    'overflow-hidden',
    'relative'
  ]

  // Layout-specific classes
  if (props.layout === 'masonry') {
    baseClasses.push('break-inside-avoid', 'mb-3', 'md-mobile:mb-4')
  } else {
    baseClasses.push('w-full max-w-md md-mobile:max-w-none mx-auto')
  }

  // Expanded state
  if (props.expandable && expandedCard.value === key) {
    baseClasses.push('expanded', 'md-mobile:col-span-2', 'lg-mobile:col-span-2', 'xl:col-span-2')
  }

  // Swipe state
  if (swipeState.value[key]) {
    baseClasses.push('swiping')
  }

  return baseClasses
}

const getActionsOverlayClasses = (item, index) => {
  const key = getItemKey(item, index)
  const state = swipeState.value[key]
  
  return {
    'actions-visible': state?.showActions || state?.showActionsLeft,
    'actions-left-visible': state?.showActionsLeft,
    'actions-right-visible': state?.showActions
  }
}

// Card Interaction Methods
const handleCardClick = (item, index) => {
  const key = getItemKey(item, index)
  
  // Don't trigger click if swiping
  if (swipeState.value[key]?.isDragging) return
  
  emit('click', item, index)
}

const toggleExpansion = (key) => {
  if (!props.expandable) return
  
  if (expandedCard.value === key) {
    expandedCard.value = null
  } else {
    expandedCard.value = key
  }
  
  emit('expand', key, expandedCard.value === key)
}

// Touch/Swipe Methods
const initSwipeState = (key) => {
  if (!swipeState.value[key]) {
    swipeState.value[key] = {
      transform: 'translateX(0)',
      showActions: false,
      showActionsLeft: false,
      isDragging: false
    }
  }
}

const handleTouchStart = (event, item, index) => {
  if (!props.showActions) return
  
  const key = getItemKey(item, index)
  initSwipeState(key)
  
  const touch = event.touches[0]
  touchStartX.value = touch.clientX
  touchStartY.value = touch.clientY
  touchStartTime.value = Date.now()
  swipeState.value[key].isDragging = true
}

const handleTouchMove = (event, item, index) => {
  if (!props.showActions) return
  
  const key = getItemKey(item, index)
  const state = swipeState.value[key]
  
  if (!state?.isDragging) return
  
  const touch = event.touches[0]
  const deltaX = touch.clientX - touchStartX.value
  const deltaY = touch.clientY - touchStartY.value
  
  // Only handle horizontal swipes
  if (Math.abs(deltaY) > Math.abs(deltaX)) return
  
  event.preventDefault()
  
  // Limit swipe distance
  const maxSwipe = 120
  const clampedDelta = Math.max(-maxSwipe, Math.min(maxSwipe, deltaX))
  
  state.transform = `translateX(${clampedDelta}px)`
  state.showActions = clampedDelta < -40
  state.showActionsLeft = clampedDelta > 40
}

const handleTouchEnd = (event, item, index) => {
  if (!props.showActions) return
  
  const key = getItemKey(item, index)
  const state = swipeState.value[key]
  
  if (!state?.isDragging) return
  
  const touch = event.changedTouches[0]
  const deltaX = touch.clientX - touchStartX.value
  const deltaTime = Date.now() - touchStartTime.value
  
  state.isDragging = false
  
  // Determine final state
  const swipeThreshold = 60
  const isQuickSwipe = deltaTime < 200 && Math.abs(deltaX) > 30
  
  if (deltaX < -swipeThreshold || (isQuickSwipe && deltaX < 0)) {
    // Show right actions
    state.transform = 'translateX(-120px)'
    state.showActions = true
    state.showActionsLeft = false
  } else if (deltaX > swipeThreshold || (isQuickSwipe && deltaX > 0)) {
    // Show left actions
    state.transform = 'translateX(120px)'
    state.showActions = false
    state.showActionsLeft = true
  } else {
    // Reset
    resetSwipe(key)
  }
}

const resetSwipe = (key) => {
  if (swipeState.value[key]) {
    swipeState.value[key].transform = 'translateX(0)'
    swipeState.value[key].showActions = false
    swipeState.value[key].showActionsLeft = false
  }
}

const resetAllSwipes = () => {
  Object.keys(swipeState.value).forEach(resetSwipe)
}

// Expose methods for parent components
defineExpose({
  toggleExpansion,
  resetSwipe,
  resetAllSwipes,
  expandedCard
})
</script>

<style scoped>
.mobile-card-stack {
  @apply w-full;
}

/* Spacing variants */
.spacing-tight .card-grid {
  @apply gap-2 md-mobile:gap-3;
}

.spacing-normal .card-grid {
  @apply gap-3 md-mobile:gap-4;
}

.spacing-relaxed .card-grid {
  @apply gap-4 md-mobile:gap-6;
}

/* Mobile Card Base Styles */
.mobile-card {
  position: relative;
  transform: translateX(0);
  transition: transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              box-shadow 0.3s ease;
}

.mobile-card.swiping {
  transition: none;
}

.mobile-card.expanded {
  transform: none !important;
}

/* Card Actions Overlay */
.card-actions-overlay {
  @apply absolute inset-0 pointer-events-none;
}

.actions-left,
.actions-right {
  @apply absolute inset-y-0 flex items-center justify-center;
  @apply transition-transform duration-200;
}

.actions-left {
  @apply left-0 bg-gradient-to-r from-green-500 to-green-600;
  @apply w-32 justify-start pl-4;
  transform: translateX(-100%);
}

.actions-right {
  @apply right-0 bg-gradient-to-l from-red-500 to-red-600;
  @apply w-32 justify-end pr-4;
  transform: translateX(100%);
}

.actions-left-visible .actions-left {
  transform: translateX(0);
}

.actions-right-visible .actions-right {
  transform: translateX(0);
}

/* Action Buttons */
.action-button {
  @apply w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm;
  @apply flex items-center justify-center text-white;
  @apply hover:bg-white/30 transition-colors;
  @apply pointer-events-auto;
}

/* Default Card Content */
.default-card {
  @apply p-4 space-y-2;
}

/* Loading Card */
.loading-card {
  @apply bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700;
  @apply shadow-sm w-full max-w-md md-mobile:max-w-none mx-auto;
}

/* Empty State */
.empty-state {
  @apply col-span-full;
}

/* Mobile-specific optimizations */
@media (max-width: 413px) {
  .mobile-card {
    @apply mx-2;
  }
  
  .actions-left,
  .actions-right {
    @apply w-28;
  }
}

/* Enhanced touch targets for mobile */
@media (pointer: coarse) {
  .action-button {
    @apply min-w-11 min-h-11;
  }
}
</style>