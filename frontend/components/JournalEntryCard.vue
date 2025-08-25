<template>
  <div class="journal-entry-card" @click="$emit('view', entry)">
    <div class="entry-header">
      <div class="entry-meta">
        <div class="entry-type-badge" :class="`type-${entry.entry_type}`">
          <md-icon>{{ getEntryTypeIcon(entry.entry_type) }}</md-icon>
          {{ getEntryTypeLabel(entry.entry_type) }}
        </div>
        <span class="entry-date">{{ formatDate(entry.created_at) }}</span>
      </div>
      
      <div class="entry-actions">
        <md-icon-button @click.stop="$emit('edit', entry)" aria-label="Edit entry">
          <md-icon>edit</md-icon>
        </md-icon-button>
        <md-icon-button @click.stop="$emit('delete', entry)" aria-label="Delete entry">
          <md-icon>delete</md-icon>
        </md-icon-button>
      </div>
    </div>

    <div class="entry-content">
      <h3 class="entry-title">{{ entry.title }}</h3>
      
      <div class="entry-setup" v-if="entry.setup_name">
        <md-icon class="setup-icon">sports</md-icon>
        {{ entry.setup_name }} ({{ entry.bow_type }})
      </div>
      
      <div class="entry-preview">
        {{ getContentPreview(entry.content) }}
      </div>

      <div class="entry-tags" v-if="entry.tags && entry.tags.length > 0">
        <span 
          v-for="tag in entry.tags" 
          :key="tag" 
          class="tag-chip"
        >
          {{ tag }}
        </span>
      </div>

      <div class="entry-attachments" v-if="entry.attachment_count > 0">
        <md-icon class="attachment-icon">attach_file</md-icon>
        {{ entry.attachment_count }} attachment{{ entry.attachment_count === 1 ? '' : 's' }}
      </div>
    </div>

    <div class="entry-image" v-if="entry.primary_image_url">
      <img :src="entry.primary_image_url" :alt="entry.title" />
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from 'vue'

const props = defineProps({
  entry: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['view', 'edit', 'delete'])

const entryTypeMap = {
  general: { label: 'General', icon: 'notes' },
  setup_change: { label: 'Setup Change', icon: 'build' },
  equipment_change: { label: 'Equipment', icon: 'hardware' },
  arrow_change: { label: 'Arrow', icon: 'arrow_forward' },
  tuning_session: { label: 'Tuning', icon: 'tune' },
  shooting_notes: { label: 'Shooting', icon: 'target' },
  maintenance: { label: 'Maintenance', icon: 'handyman' },
  upgrade: { label: 'Upgrade', icon: 'upgrade' }
}

const getEntryTypeLabel = (type) => {
  return entryTypeMap[type]?.label || 'General'
}

const getEntryTypeIcon = (type) => {
  return entryTypeMap[type]?.icon || 'notes'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getContentPreview = (content) => {
  if (!content) return ''
  const cleanContent = content.replace(/[#*_\[\]]/g, '').trim()
  return cleanContent.length > 150 
    ? cleanContent.substring(0, 150) + '...' 
    : cleanContent
}
</script>

<style scoped>
.journal-entry-card {
  background: var(--md-sys-color-surface);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  align-items: start;
}

.journal-entry-card:hover {
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.entry-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  grid-column: 1 / -1;
}

.entry-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.entry-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  width: fit-content;
}

.entry-type-badge.type-general {
  background: var(--md-sys-color-surface-variant);
  color: var(--md-sys-color-on-surface-variant);
}

.entry-type-badge.type-setup_change {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.entry-type-badge.type-equipment_change {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.entry-type-badge.type-arrow_change {
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
}

.entry-type-badge.type-tuning_session {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

.entry-type-badge.type-shooting_notes {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.entry-type-badge.type-maintenance {
  background: var(--md-sys-color-surface-variant);
  color: var(--md-sys-color-on-surface-variant);
}

.entry-type-badge.type-upgrade {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.entry-date {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
}

.entry-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.journal-entry-card:hover .entry-actions {
  opacity: 1;
}

.entry-content {
  grid-column: 1;
}

.entry-title {
  margin: 0 0 0.75rem 0;
  color: var(--md-sys-color-on-surface);
  font-size: 1.125rem;
  font-weight: 500;
}

.entry-setup {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: var(--md-sys-color-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.setup-icon {
  font-size: 1rem;
}

.entry-preview {
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.5;
  margin-bottom: 1rem;
}

.entry-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.tag-chip {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.entry-attachments {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
}

.attachment-icon {
  font-size: 1rem;
}

.entry-image {
  grid-column: 2;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}

.entry-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-entry-card {
    grid-template-columns: 1fr;
    padding: 1rem;
  }

  .entry-image {
    grid-column: 1;
    width: 100%;
    height: 120px;
    margin-top: 1rem;
  }

  .entry-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .entry-actions {
    opacity: 1;
  }

  .entry-tags {
    margin-bottom: 0.5rem;
  }
}
</style>