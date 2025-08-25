<template>
  <md-dialog :open="show" @close="$emit('close')" class="journal-viewer">
    <div slot="headline" class="viewer-header">
      <div class="entry-info">
        <div class="entry-type-badge" :class="`type-${entry?.entry_type}`">
          <md-icon>{{ getEntryTypeIcon(entry?.entry_type) }}</md-icon>
          {{ getEntryTypeLabel(entry?.entry_type) }}
        </div>
        <span class="entry-date">{{ formatDate(entry?.created_at) }}</span>
      </div>
      
      <div class="viewer-actions">
        <md-icon-button @click="$emit('edit')" aria-label="Edit entry">
          <md-icon>edit</md-icon>
        </md-icon-button>
        <md-icon-button @click="confirmDelete" aria-label="Delete entry">
          <md-icon>delete</md-icon>
        </md-icon-button>
      </div>
    </div>
    
    <div slot="content" class="viewer-content">
      <h2 class="entry-title">{{ entry?.title }}</h2>
      
      <div class="entry-setup" v-if="entry?.setup_name">
        <md-icon class="setup-icon">sports</md-icon>
        <strong>Setup:</strong> {{ entry.setup_name }} ({{ entry.bow_type }})
      </div>
      
      <div class="entry-body">
        <pre class="content-text">{{ entry?.content }}</pre>
      </div>

      <div class="entry-tags" v-if="entry?.tags && entry.tags.length > 0">
        <strong>Tags:</strong>
        <span 
          v-for="tag in entry.tags" 
          :key="tag" 
          class="tag-chip"
        >
          {{ tag }}
        </span>
      </div>

      <div v-if="entry?.attachments && entry.attachments.length > 0" class="attachments-section">
        <h4>Attachments</h4>
        <div class="attachments-list">
          <div 
            v-for="attachment in entry.attachments" 
            :key="attachment.id"
            class="attachment-item"
          >
            <md-icon>{{ getAttachmentIcon(attachment.file_type) }}</md-icon>
            <span>{{ attachment.original_filename }}</span>
          </div>
        </div>
      </div>

      <div v-if="entry?.equipment_references && entry.equipment_references.length > 0" class="references-section">
        <h4>Referenced Equipment</h4>
        <div class="references-list">
          <div 
            v-for="ref in entry.equipment_references" 
            :key="ref.id"
            class="reference-item"
          >
            <md-icon>{{ ref.bow_equipment_id ? 'hardware' : 'arrow_forward' }}</md-icon>
            <span>
              {{ ref.manufacturer_name || ref.arrow_manufacturer }} 
              {{ ref.model_name || ref.arrow_model }}
              <span class="reference-type">({{ ref.reference_type }})</span>
            </span>
          </div>
        </div>
      </div>

      <div class="entry-meta">
        <div class="meta-item">
          <strong>Created:</strong> {{ formatDate(entry?.created_at) }}
        </div>
        <div class="meta-item" v-if="entry?.updated_at !== entry?.created_at">
          <strong>Updated:</strong> {{ formatDate(entry?.updated_at) }}
        </div>
        <div class="meta-item" v-if="entry?.is_private">
          <md-icon class="private-icon">lock</md-icon>
          <strong>Private Entry</strong>
        </div>
      </div>
    </div>

    <div slot="actions">
      <md-text-button @click="$emit('close')">Close</md-text-button>
    </div>
  </md-dialog>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  show: Boolean,
  entry: Object
})

const emit = defineEmits(['close', 'edit', 'delete'])

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

const getAttachmentIcon = (fileType) => {
  switch (fileType) {
    case 'image': return 'image'
    case 'video': return 'videocam'
    case 'document': return 'description'
    default: return 'attach_file'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const confirmDelete = () => {
  if (confirm(`Are you sure you want to delete "${props.entry?.title}"?`)) {
    emit('delete')
  }
}
</script>

<style scoped>
.journal-viewer {
  --md-dialog-container-max-width: 800px;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.entry-info {
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

.entry-date {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
}

.viewer-actions {
  display: flex;
  gap: 0.25rem;
}

.viewer-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-height: 70vh;
  overflow-y: auto;
}

.entry-title {
  margin: 0;
  color: var(--md-sys-color-on-surface);
  font-size: 1.5rem;
  font-weight: 500;
}

.entry-setup {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-primary);
  font-size: 0.875rem;
}

.setup-icon {
  font-size: 1rem;
}

.entry-body {
  background: var(--md-sys-color-surface-variant);
  border-radius: 8px;
  padding: 1rem;
}

.content-text {
  white-space: pre-wrap;
  font-family: inherit;
  color: var(--md-sys-color-on-surface);
  margin: 0;
  line-height: 1.6;
}

.entry-tags {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag-chip {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.attachments-section,
.references-section {
  border-top: 1px solid var(--md-sys-color-outline-variant);
  padding-top: 1rem;
}

.attachments-section h4,
.references-section h4 {
  margin: 0 0 0.75rem 0;
  color: var(--md-sys-color-on-surface);
  font-size: 1rem;
  font-weight: 500;
}

.attachments-list,
.references-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.attachment-item,
.reference-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-on-surface-variant);
}

.reference-type {
  color: var(--md-sys-color-outline);
  font-style: italic;
}

.entry-meta {
  border-top: 1px solid var(--md-sys-color-outline-variant);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
}

.private-icon {
  color: var(--md-sys-color-error);
  font-size: 1rem;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-viewer {
    --md-dialog-container-max-width: 100%;
    --md-dialog-container-margin: 1rem;
  }

  .viewer-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .entry-tags {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>