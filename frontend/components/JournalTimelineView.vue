<template>
  <div class="journal-timeline-view">
    <!-- Loading State -->
    <div v-if="loading && items.length === 0" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 dark:border-indigo-400 mx-auto mb-3"></div>
      <p class="text-gray-600 dark:text-gray-400">Loading timeline...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0 && !loading" class="text-center py-12">
      <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="fas fa-timeline text-2xl text-gray-400"></i>
      </div>
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
        No Activity Yet
      </h4>
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        Start by adding a journal entry or making changes to your setup to see activity here.
      </p>
    </div>

    <!-- Timeline -->
    <div v-else class="relative">
      <!-- Timeline line -->
      <div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>
      
      <div class="space-y-6">
        <div
          v-for="(item, index) in items"
          :key="`${item.item_type}-${item.id}-${index}`"
          class="relative flex items-start"
        >
          <!-- Timeline dot -->
          <div :class="[
            'relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-4 bg-white dark:bg-gray-800 shadow-lg',
            getTimelineDotColor(item)
          ]">
            <i :class="getTimelineIcon(item)" class="text-lg"></i>
          </div>
          
          <!-- Timeline content -->
          <div class="ml-6 flex-1">
            <!-- Journal Entry -->
            <div v-if="item.item_type === 'journal'" class="journal-entry">
              <JournalTimelineEntry
                :entry="item"
                :bow-setup="bowSetup"
                @updated="$emit('entry-updated')"
                @deleted="$emit('entry-deleted')"
                @error="$emit('error', $event)"
              />
            </div>
            
            <!-- Change History Entry -->
            <div v-else-if="item.item_type === 'change'" class="change-entry">
              <ChangeTimelineEntry
                :change="item"
                :bow-setup="bowSetup"
                @equipment-restored="$emit('equipment-restored', $event)"
                @error="$emit('error', $event)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import JournalTimelineEntry from '@/components/JournalTimelineEntry.vue'
import ChangeTimelineEntry from '@/components/ChangeTimelineEntry.vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  bowSetup: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['entry-updated', 'entry-deleted', 'equipment-restored', 'error'])

// Timeline styling functions
const getTimelineDotColor = (item) => {
  if (item.item_type === 'journal') {
    // Journal entry colors based on type
    const entryTypeColors = {
      'setup_change': 'border-blue-500',
      'tuning_session': 'border-green-500',
      'shooting_notes': 'border-purple-500',
      'maintenance': 'border-orange-500',
      'equipment_change': 'border-red-500',
      'general': 'border-gray-500'
    }
    return entryTypeColors[item.entry_type] || 'border-indigo-500'
  } else {
    // Change history colors based on change type
    const changeTypeColors = {
      'add': 'border-green-500',
      'remove': 'border-red-500',
      'modify': 'border-blue-500',
      'arrow_added': 'border-emerald-500',
      'arrow_removed': 'border-red-500',
      'arrow_modified': 'border-blue-500',
      'equipment_added': 'border-green-500',
      'equipment_removed': 'border-red-500',
      'equipment_modified': 'border-blue-500'
    }
    return changeTypeColors[item.change_type] || 'border-gray-400'
  }
}

const getTimelineIcon = (item) => {
  if (item.item_type === 'journal') {
    // Journal entry icons
    const entryTypeIcons = {
      'setup_change': 'fas fa-crosshairs text-blue-600',
      'tuning_session': 'fas fa-adjust text-green-600',
      'shooting_notes': 'fas fa-target text-purple-600',
      'maintenance': 'fas fa-wrench text-orange-600',
      'equipment_change': 'fas fa-cogs text-red-600',
      'general': 'fas fa-sticky-note text-gray-600'
    }
    return entryTypeIcons[item.entry_type] || 'fas fa-book text-indigo-600'
  } else {
    // Change history icons
    const changeTypeIcons = {
      'add': 'fas fa-plus text-green-600',
      'remove': 'fas fa-minus text-red-600',
      'modify': 'fas fa-edit text-blue-600',
      'arrow_added': 'fas fa-plus text-emerald-600',
      'arrow_removed': 'fas fa-minus text-red-600',
      'arrow_modified': 'fas fa-edit text-blue-600',
      'equipment_added': 'fas fa-plus text-green-600',
      'equipment_removed': 'fas fa-minus text-red-600',
      'equipment_modified': 'fas fa-edit text-blue-600'
    }
    return changeTypeIcons[item.change_type] || 'fas fa-circle text-gray-400'
  }
}
</script>

<style scoped>
.journal-timeline-view {
  width: 100%;
}

/* Timeline animations */
.journal-entry,
.change-entry {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Enhanced timeline dot effects */
.journal-timeline-view .relative.z-10 {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.journal-timeline-view .relative.z-10:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Timeline line enhancement */
.journal-timeline-view .absolute.left-6 {
  background: linear-gradient(to bottom, 
    rgba(99, 102, 241, 0.3), 
    rgba(156, 163, 175, 0.3),
    rgba(99, 102, 241, 0.3)
  );
}

/* Dark mode timeline line */
.dark .journal-timeline-view .absolute.left-6 {
  background: linear-gradient(to bottom, 
    rgba(129, 140, 248, 0.3), 
    rgba(75, 85, 99, 0.3),
    rgba(129, 140, 248, 0.3)
  );
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .journal-timeline-view .space-y-6 {
    space-y: 1rem;
  }
  
  .journal-timeline-view .ml-6 {
    margin-left: 1rem;
  }
  
  .journal-timeline-view .absolute.left-6 {
    left: 1.5rem;
  }
  
  .journal-timeline-view .w-12.h-12 {
    width: 2.5rem;
    height: 2.5rem;
  }
  
  .journal-timeline-view .w-12.h-12 i {
    font-size: 1rem;
  }
}
</style>