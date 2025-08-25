<template>
  <div :class="groupClasses">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  spacing: {
    type: String,
    default: 'normal', // compact, normal, relaxed
    validator: (value) => ['compact', 'normal', 'relaxed'].includes(value)
  },
  orientation: {
    type: String,
    default: 'vertical', // vertical, horizontal
    validator: (value) => ['vertical', 'horizontal'].includes(value)
  },
  align: {
    type: String,
    default: 'stretch', // start, center, end, stretch (for horizontal orientation)
    validator: (value) => ['start', 'center', 'end', 'stretch'].includes(value)
  }
})

const groupClasses = computed(() => {
  const baseClasses = ['form-group']
  
  // Spacing classes
  const spacingClasses = {
    compact: props.orientation === 'vertical' ? 'space-y-3' : 'space-x-3',
    normal: props.orientation === 'vertical' ? 'space-y-4' : 'space-x-4',
    relaxed: props.orientation === 'vertical' ? 'space-y-6' : 'space-x-6'
  }
  
  // Orientation classes
  const orientationClasses = {
    vertical: 'flex flex-col',
    horizontal: 'flex flex-row flex-wrap'
  }
  
  // Alignment classes (only for horizontal orientation)
  const alignmentClasses = props.orientation === 'horizontal' ? {
    start: 'items-start',
    center: 'items-center', 
    end: 'items-end',
    stretch: 'items-stretch'
  } : {}
  
  return [
    ...baseClasses,
    orientationClasses[props.orientation],
    spacingClasses[props.spacing],
    alignmentClasses[props.align] || ''
  ].filter(Boolean)
})
</script>

<style scoped>
.form-group {
  width: 100%;
}

/* Ensure proper spacing in horizontal layouts */
.form-group.flex-row > * {
  flex: 1;
  min-width: 0; /* Prevent flex items from overflowing */
}

/* Mobile-first responsive adjustments */
@media (max-width: 640px) {
  .form-group.flex-row {
    flex-direction: column;
  }
  
  .form-group.flex-row.space-x-3 {
    @apply space-x-0 space-y-3;
  }
  
  .form-group.flex-row.space-x-4 {
    @apply space-x-0 space-y-4;
  }
  
  .form-group.flex-row.space-x-6 {
    @apply space-x-0 space-y-6;
  }
}
</style>