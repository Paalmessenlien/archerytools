<template>
  <div class="mobile-components-demo">
    <div class="demo-section">
      <h2 class="mobile-heading-1 mb-6">Mobile Components Demo</h2>
      
      <!-- Demo Controls -->
      <div class="demo-controls mb-6 space-y-4">
        <div class="flex flex-wrap gap-3">
          <button 
            @click="toggleActionSheet"
            class="demo-button bg-blue-600 text-white"
          >
            Show Action Sheet
          </button>
          <button 
            @click="toggleLayout"
            class="demo-button bg-green-600 text-white"
          >
            Layout: {{ currentLayout }}
          </button>
          <button 
            @click="toggleLoading"
            class="demo-button bg-purple-600 text-white"
          >
            {{ loading ? 'Stop' : 'Start' }} Loading
          </button>
        </div>
      </div>

      <!-- MobileCardStack Demo -->
      <MobileCardStack
        :items="demoItems"
        :loading="loading"
        :layout="currentLayout"
        :expandable="true"
        :show-actions="true"
        spacing="normal"
        empty-title="No Demo Items"
        empty-message="Add some demo items to see the card stack in action."
        @click="handleCardClick"
        @edit="handleCardEdit"
        @delete="handleCardDelete"
        @expand="handleCardExpand"
      >
        <!-- Custom Card Content -->
        <template #card="{ item, index, isExpanded, toggleExpansion }">
          <div class="demo-card">
            <!-- Card Header -->
            <div class="flex items-start justify-between mb-3">
              <div class="flex-1">
                <h3 class="mobile-heading-3 text-gray-900 dark:text-gray-100">
                  {{ item.title }}
                </h3>
                <p class="mobile-body-small text-gray-500 dark:text-gray-400">
                  {{ item.category }}
                </p>
              </div>
              <div class="flex items-center gap-2">
                <span class="px-2 py-1 text-xs font-medium rounded-full"
                      :class="getStatusClass(item.status)">
                  {{ item.status }}
                </span>
                <button 
                  @click.stop="toggleExpansion()"
                  class="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
                >
                  <i class="fas transition-transform duration-200" 
                     :class="isExpanded ? 'fa-compress' : 'fa-expand'"></i>
                </button>
              </div>
            </div>

            <!-- Card Stats -->
            <div class="grid grid-cols-3 gap-4 mb-3">
              <div class="text-center">
                <div class="mobile-body-large font-semibold text-blue-600 dark:text-blue-400">
                  {{ item.metrics.primary }}
                </div>
                <div class="mobile-body-small text-gray-500">Primary</div>
              </div>
              <div class="text-center">
                <div class="mobile-body-large font-semibold text-green-600 dark:text-green-400">
                  {{ item.metrics.secondary }}
                </div>
                <div class="mobile-body-small text-gray-500">Secondary</div>
              </div>
              <div class="text-center">
                <div class="mobile-body-large font-semibold text-purple-600 dark:text-purple-400">
                  {{ item.metrics.tertiary }}
                </div>
                <div class="mobile-body-small text-gray-500">Tertiary</div>
              </div>
            </div>

            <!-- Expanded Content -->
            <div v-if="isExpanded" class="expanded-content animate-fadeIn">
              <div class="pt-3 border-t border-gray-200 dark:border-gray-700">
                <p class="mobile-body-medium text-gray-700 dark:text-gray-300 mb-3">
                  {{ item.description }}
                </p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="tag in item.tags" :key="tag"
                        class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- Custom Left Actions -->
        <template #actions-left="{ item, closeActions }">
          <button 
            @click.stop="handleCardEdit(item); closeActions()"
            class="action-button action-edit"
            title="Edit Item"
          >
            <i class="fas fa-edit"></i>
          </button>
          <button 
            @click.stop="handleCardShare(item); closeActions()"
            class="action-button action-share"
            title="Share Item"
          >
            <i class="fas fa-share"></i>
          </button>
        </template>

        <!-- Custom Right Actions -->
        <template #actions-right="{ item, closeActions }">
          <button 
            @click.stop="handleCardFavorite(item); closeActions()"
            class="action-button action-favorite"
            title="Add to Favorites"
          >
            <i class="fas fa-heart"></i>
          </button>
          <button 
            @click.stop="handleCardDelete(item); closeActions()"
            class="action-button action-delete"
            title="Delete Item"
          >
            <i class="fas fa-trash"></i>
          </button>
        </template>

        <!-- Custom Empty State -->
        <template #empty>
          <div class="text-center py-12">
            <i class="fas fa-box-open text-6xl text-gray-300 dark:text-gray-600 mb-4"></i>
            <h3 class="mobile-heading-2 text-gray-500 dark:text-gray-400 mb-2">
              No Demo Items
            </h3>
            <p class="mobile-body-medium text-gray-400 dark:text-gray-500 mb-6">
              The card stack is empty. Add some demo items to see it in action.
            </p>
            <button 
              @click="addDemoItem"
              class="demo-button bg-blue-600 text-white"
            >
              <i class="fas fa-plus mr-2"></i>
              Add Demo Item
            </button>
          </div>
        </template>
      </MobileCardStack>
    </div>

    <!-- MobileActionSheet Demo -->
    <MobileActionSheet
      v-model="showActionSheet"
      title="Demo Actions"
      subtitle="Choose an action to perform"
      :actions="actionSheetActions"
      :show-cancel="true"
      cancel-text="Cancel"
      size="auto"
      position="bottom"
      :swipe-to-close="true"
      @action="handleActionSheetAction"
      @cancel="handleActionSheetCancel"
    >
      <!-- Custom Header -->
      <template #header>
        <div class="text-center py-4">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mx-auto mb-3 flex items-center justify-center">
            <i class="fas fa-cog text-white text-2xl"></i>
          </div>
          <h3 class="mobile-heading-2 text-gray-900 dark:text-gray-100">
            Demo Action Sheet
          </h3>
          <p class="mobile-body-small text-gray-500 dark:text-gray-400 mt-1">
            Select an action from the options below
          </p>
        </div>
      </template>
    </MobileActionSheet>

    <!-- Demo Results Display -->
    <div v-if="lastAction" class="demo-results mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
      <h4 class="mobile-heading-4 text-blue-900 dark:text-blue-100 mb-2">Last Action</h4>
      <p class="mobile-body-medium text-blue-700 dark:text-blue-300">
        {{ lastAction }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import MobileCardStack from './MobileCardStack.vue'
import MobileActionSheet from './MobileActionSheet.vue'

// State
const loading = ref(false)
const showActionSheet = ref(false)
const currentLayout = ref('responsive')
const lastAction = ref('')

// Demo data
const demoItems = ref([
  {
    id: 1,
    title: 'Mobile Card Demo',
    category: 'UI Component',
    status: 'active',
    description: 'This is a demonstration of the MobileCardStack component with expandable content and swipe actions.',
    metrics: { primary: '95%', secondary: '24ms', tertiary: '4.8' },
    tags: ['mobile', 'responsive', 'touch']
  },
  {
    id: 2,
    title: 'Action Sheet Example',
    category: 'Interaction',
    status: 'pending',
    description: 'Showcases the MobileActionSheet component with native-style action menus and gesture support.',
    metrics: { primary: '87%', secondary: '18ms', tertiary: '4.2' },
    tags: ['native', 'gestures', 'mobile']
  },
  {
    id: 3,
    title: 'Gesture Integration',
    category: 'UX Enhancement',
    status: 'completed',
    description: 'Demonstrates the integration of swipe gestures, pull-to-refresh, and other mobile interactions.',
    metrics: { primary: '92%', secondary: '31ms', tertiary: '4.6' },
    tags: ['swipe', 'pull-refresh', 'touch']
  }
])

const actionSheetActions = ref([
  {
    id: 'edit',
    label: 'Edit Item',
    description: 'Modify the selected item',
    icon: 'fas fa-edit',
    iconColor: 'blue-500'
  },
  {
    id: 'share',
    label: 'Share',
    description: 'Share this item with others',
    icon: 'fas fa-share',
    iconColor: 'green-500',
    badge: 'New',
    badgeType: 'success'
  },
  {
    id: 'duplicate',
    label: 'Duplicate',
    description: 'Create a copy of this item',
    icon: 'fas fa-copy',
    iconColor: 'purple-500'
  },
  {
    id: 'archive',
    label: 'Archive',
    description: 'Move to archived items',
    icon: 'fas fa-archive',
    iconColor: 'yellow-500'
  },
  {
    id: 'delete',
    label: 'Delete',
    description: 'Permanently remove this item',
    icon: 'fas fa-trash',
    iconColor: 'red-500',
    destructive: true
  }
])

// Methods
const toggleActionSheet = () => {
  showActionSheet.value = !showActionSheet.value
}

const toggleLayout = () => {
  const layouts = ['single', 'responsive', 'masonry']
  const currentIndex = layouts.indexOf(currentLayout.value)
  currentLayout.value = layouts[(currentIndex + 1) % layouts.length]
  lastAction.value = `Layout changed to: ${currentLayout.value}`
}

const toggleLoading = () => {
  loading.value = !loading.value
  lastAction.value = loading.value ? 'Loading started' : 'Loading stopped'
}

const addDemoItem = () => {
  const newItem = {
    id: Date.now(),
    title: `Demo Item ${demoItems.value.length + 1}`,
    category: 'Generated',
    status: 'active',
    description: 'This is a dynamically generated demo item.',
    metrics: { 
      primary: `${Math.floor(Math.random() * 100)}%`,
      secondary: `${Math.floor(Math.random() * 50)}ms`,
      tertiary: `${(Math.random() * 5).toFixed(1)}`
    },
    tags: ['demo', 'generated', 'test']
  }
  demoItems.value.push(newItem)
  lastAction.value = `Added new demo item: ${newItem.title}`
}

const handleCardClick = (item, index) => {
  lastAction.value = `Clicked card: ${item.title} (index: ${index})`
}

const handleCardEdit = (item, index) => {
  lastAction.value = `Edit action triggered for: ${item.title}`
}

const handleCardDelete = (item, index) => {
  demoItems.value = demoItems.value.filter(i => i.id !== item.id)
  lastAction.value = `Deleted item: ${item.title}`
}

const handleCardExpand = (key, isExpanded) => {
  lastAction.value = `Card ${key} ${isExpanded ? 'expanded' : 'collapsed'}`
}

const handleCardShare = (item) => {
  lastAction.value = `Share action triggered for: ${item.title}`
}

const handleCardFavorite = (item) => {
  lastAction.value = `Favorite action triggered for: ${item.title}`
}

const handleActionSheetAction = ({ action, index }) => {
  lastAction.value = `Action sheet action: ${action.label} (${action.id})`
}

const handleActionSheetCancel = () => {
  lastAction.value = 'Action sheet canceled'
}

const getStatusClass = (status) => {
  const classes = {
    'active': 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    'pending': 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    'completed': 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    'inactive': 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  }
  return classes[status] || classes.inactive
}
</script>

<style scoped>
.mobile-components-demo {
  @apply p-4 space-y-6;
}

.demo-section {
  @apply space-y-6;
}

.demo-controls {
  @apply bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700;
}

.demo-button {
  @apply px-4 py-2 rounded-lg font-medium;
  @apply hover:opacity-90 transition-opacity;
  @apply mobile-touch-target;
}

.demo-card {
  @apply p-4 space-y-3;
}

.expanded-content {
  animation: fadeIn 0.3s ease-in-out;
}

.action-button.action-edit {
  @apply bg-blue-500/20;
}

.action-button.action-share {
  @apply bg-green-500/20;
}

.action-button.action-favorite {
  @apply bg-pink-500/20;
}

.demo-results {
  @apply border border-blue-200 dark:border-blue-700;
}
</style>