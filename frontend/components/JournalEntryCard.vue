<template>
  <div :class="['journal-entry-card', `card-${viewMode}`]" @click="$emit('view', entry)">
    <div class="entry-header">
      <div class="entry-meta">
        <div class="entry-type-badge" :class="`type-${entry.entry_type}`">
          <md-icon>{{ getEntryTypeIcon(entry.entry_type) }}</md-icon>
          {{ getEntryTypeLabel(entry.entry_type) }}
        </div>
        <span class="entry-date">{{ formatDate(entry.created_at) }}</span>
      </div>
      
      <div class="entry-actions">
        <md-icon-button 
          @click.stop="toggleFavorite" 
          :aria-label="entry.is_favorite ? 'Remove from favorites' : 'Add to favorites'"
          class="favorite-btn"
          :class="{ 'is-favorite': entry.is_favorite }"
        >
          <md-icon>{{ entry.is_favorite ? 'star' : 'star_border' }}</md-icon>
        </md-icon-button>
        <md-icon-button @click.stop="$emit('edit', entry)" aria-label="Edit entry">
          <md-icon>edit</md-icon>
        </md-icon-button>
        <md-icon-button @click.stop="$emit('delete', entry)" aria-label="Delete entry">
          <md-icon>delete</md-icon>
        </md-icon-button>
      </div>
    </div>

    <div class="entry-content">
      <h3 class="entry-title">
        <span class="title-text">{{ entry.title }}</span>
        <md-icon v-if="entry.is_favorite" class="title-favorite-indicator">star</md-icon>
      </h3>
      
      <div class="entry-setup" v-if="entry.setup_name">
        <md-icon class="setup-icon">sports</md-icon>
        {{ entry.setup_name }} ({{ entry.bow_type }})
      </div>
      
      <!-- Entry Images -->
      <div v-if="entry.images && entry.images.length" class="entry-images">
        <div class="image-gallery" :class="{ 'single-image': entry.images.length === 1 }">
          <img 
            v-for="(image, index) in displayImages" 
            :key="index"
            :src="image.url" 
            :alt="image.alt || 'Journal image'"
            class="gallery-image"
            @click="openImageModal(image, index)"
            loading="lazy"
          />
          <div 
            v-if="entry.images.length > maxDisplayImages" 
            class="more-images-indicator"
            @click="showAllImages"
          >
            <span class="more-count">+{{ entry.images.length - maxDisplayImages }}</span>
          </div>
        </div>
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

      <!-- Linked Changes Display -->
      <div v-if="entry.linked_changes && entry.linked_changes.length > 0" class="linked-changes">
        <div class="linked-changes-header">
          <md-icon class="changes-icon">link</md-icon>
          <span class="changes-label">Linked Changes</span>
          <span class="changes-count">({{ entry.linked_changes.length }})</span>
        </div>
        <div class="linked-changes-list">
          <div 
            v-for="change in displayedLinkedChanges" 
            :key="`${change.type}-${change.id}`"
            class="linked-change-chip"
            :class="`change-${change.type}`"
            @click.stop="viewChange(change)"
          >
            <md-icon class="change-icon">{{ getChangeIcon(change.type) }}</md-icon>
            <span class="change-title">{{ truncateChangeTitle(change.title) }}</span>
            <span class="change-date">{{ formatShortDate(change.created_at) }}</span>
          </div>
          <div 
            v-if="entry.linked_changes.length > maxDisplayedChanges"
            class="more-changes-chip"
            @click.stop="showAllChanges"
          >
            <md-icon>more_horiz</md-icon>
            <span>+{{ entry.linked_changes.length - maxDisplayedChanges }} more</span>
          </div>
        </div>
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
  },
  viewMode: {
    type: String,
    default: 'list',
    validator: (value) => ['list', 'grid'].includes(value)
  }
})

const emit = defineEmits(['view', 'edit', 'delete', 'view-change', 'show-all-changes', 'toggle-favorite'])

// Image display configuration
const maxDisplayImages = computed(() => props.viewMode === 'grid' ? 2 : 4)
const displayImages = computed(() => {
  if (!props.entry.images || props.entry.images.length === 0) return []
  return props.entry.images.slice(0, maxDisplayImages.value)
})

// Linked changes display configuration
const maxDisplayedChanges = computed(() => props.viewMode === 'grid' ? 2 : 3)
const displayedLinkedChanges = computed(() => {
  if (!props.entry.linked_changes || props.entry.linked_changes.length === 0) return []
  return props.entry.linked_changes.slice(0, maxDisplayedChanges.value)
})

// Image modal/gallery functions
const openImageModal = (image, index) => {
  // TODO: Implement image modal/lightbox functionality
  // For now, open in new tab
  window.open(image.url, '_blank')
}

const showAllImages = () => {
  // TODO: Implement show all images functionality
  console.log('Show all images:', props.entry.images)
}

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

// Linked changes functions
const viewChange = (change) => {
  emit('view-change', change)
}

const showAllChanges = () => {
  emit('show-all-changes', props.entry)
}

const getChangeIcon = (changeType) => {
  const icons = {
    equipment_change: 'build',
    setup_change: 'settings',
    arrow_change: 'arrow_forward'
  }
  return icons[changeType] || 'change_history'
}

const truncateChangeTitle = (title) => {
  if (!title) return ''
  return title.length > 25 ? title.substring(0, 25) + '...' : title
}

const formatShortDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
  
  if (diffInDays === 0) return 'Today'
  if (diffInDays === 1) return 'Yesterday'
  if (diffInDays < 7) return `${diffInDays}d ago`
  if (diffInDays < 30) return `${Math.floor(diffInDays / 7)}w ago`
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// Favorites functionality
const toggleFavorite = () => {
  emit('toggle-favorite', props.entry)
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

/* Grid view specific styling */
.journal-entry-card.card-grid {
  height: 300px;
  overflow: hidden;
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr auto;
  gap: 0.75rem;
}

.card-grid .entry-header {
  margin-bottom: 0.5rem;
  grid-column: 1;
  grid-row: 1;
}

.card-grid .entry-content {
  grid-column: 1;
  grid-row: 2;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-grid .entry-title {
  font-size: 1.125rem;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-grid .entry-preview {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  flex: 1;
}

.card-grid .entry-image {
  grid-column: 1;
  grid-row: 3;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
}

.card-grid .entry-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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

.favorite-btn {
  transition: all 0.3s ease;
}

.favorite-btn md-icon {
  transition: all 0.3s ease;
}

.favorite-btn.is-favorite {
  color: var(--md-sys-color-primary);
}

.favorite-btn.is-favorite md-icon {
  color: var(--md-sys-color-primary);
  transform: scale(1.1);
}

.favorite-btn:hover {
  transform: scale(1.05);
}

.favorite-btn.is-favorite:hover md-icon {
  color: var(--md-sys-color-secondary);
}

.entry-content {
  grid-column: 1;
}

.entry-title {
  margin: 0 0 0.75rem 0;
  color: var(--md-sys-color-on-surface);
  font-size: 1.125rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-text {
  flex: 1;
  min-width: 0;
}

.title-favorite-indicator {
  color: var(--md-sys-color-primary);
  font-size: 1rem;
  flex-shrink: 0;
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

/* Image Gallery Styles */
.entry-images {
  margin-bottom: 1rem;
}

.image-gallery {
  display: grid;
  gap: 0.5rem;
  border-radius: 12px;
  overflow: hidden;
}

.image-gallery:not(.single-image) {
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  max-height: 200px;
}

.image-gallery.single-image {
  grid-template-columns: 1fr;
  max-height: 300px;
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
  border-radius: 8px;
  min-height: 120px;
}

.gallery-image:hover {
  transform: scale(1.02);
  opacity: 0.9;
}

.more-images-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.2s ease;
  min-height: 120px;
}

.more-images-indicator:hover {
  background: rgba(0, 0, 0, 0.8);
}

.more-count {
  font-size: 1.5rem;
  font-weight: 600;
}

/* Linked Changes Styles */
.linked-changes {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 8px;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.linked-changes-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
}

.changes-icon {
  font-size: 1rem;
  color: var(--md-sys-color-primary);
}

.changes-label {
  flex: 1;
}

.changes-count {
  font-size: 0.8rem;
  opacity: 0.8;
}

.linked-changes-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.linked-change-chip {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  max-width: 200px;
}

.linked-change-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.linked-change-chip.change-equipment_change {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  border-color: var(--md-sys-color-secondary);
}

.linked-change-chip.change-equipment_change:hover {
  background: var(--md-sys-color-secondary);
  color: var(--md-sys-color-on-secondary);
}

.linked-change-chip.change-setup_change {
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
  border-color: var(--md-sys-color-tertiary);
}

.linked-change-chip.change-setup_change:hover {
  background: var(--md-sys-color-tertiary);
  color: var(--md-sys-color-on-tertiary);
}

.linked-change-chip.change-arrow_change {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
  border-color: var(--md-sys-color-error);
}

.linked-change-chip.change-arrow_change:hover {
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
}

.change-icon {
  font-size: 0.9rem;
  flex-shrink: 0;
}

.change-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.change-date {
  font-size: 0.7rem;
  opacity: 0.8;
  flex-shrink: 0;
}

.more-changes-chip {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  border-radius: 16px;
  background: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-on-surface-variant);
  border: 1px dashed var(--md-sys-color-outline);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.more-changes-chip:hover {
  background: var(--md-sys-color-surface-container-high);
  border-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-primary);
}

.more-changes-chip md-icon {
  font-size: 0.9rem;
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
  
  .image-gallery:not(.single-image) {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    max-height: 150px;
  }
  
  .gallery-image {
    min-height: 100px;
  }
  
  .more-images-indicator {
    min-height: 100px;
  }
  
  .linked-changes {
    padding: 0.5rem;
  }
  
  .linked-changes-list {
    gap: 0.375rem;
  }
  
  .linked-change-chip {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    max-width: 150px;
  }
  
  .change-title {
    max-width: 80px;
  }
  
  .change-date {
    display: none; /* Hide date on mobile for space */
  }
}
</style>