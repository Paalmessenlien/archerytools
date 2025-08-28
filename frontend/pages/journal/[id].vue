<template>
  <div class="journal-entry-page">
    <!-- Loading State -->
    <div v-if="pending || !entry" class="loading-container">
      <md-circular-progress indeterminate></md-circular-progress>
      <p>Loading journal entry...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      <h2>Entry Not Found</h2>
      <p>{{ error.message || 'The requested journal entry could not be found.' }}</p>
      <CustomButton @click="goBack" variant="primary" icon="fas fa-arrow-left">
        Go Back
      </CustomButton>
    </div>

    <!-- Main Content -->
    <div v-else class="entry-container">
      <!-- Header -->
      <div class="entry-header">
        <div class="header-actions">
          <CustomButton @click="goBack" variant="ghost" icon="fas fa-arrow-left">
            Back to Journal
          </CustomButton>
          
          <div class="action-buttons">
            <CustomButton @click="editEntry" variant="outline" icon="fas fa-edit">
              Edit Entry
            </CustomButton>
            <CustomButton @click="shareEntry" variant="ghost" icon="fas fa-share-alt">
              Share
            </CustomButton>
            <CustomButton @click="deleteEntry" variant="ghost" icon="fas fa-trash" class="danger">
              Delete
            </CustomButton>
          </div>
        </div>

        <div class="entry-meta">
          <div class="entry-type-badge" :class="`type-${entry.entry_type}`">
            <i :class="getEntryTypeIcon(entry.entry_type)" class="mr-1"></i>
            {{ getEntryTypeLabel(entry.entry_type) }}
          </div>
          
          <div class="entry-dates">
            <div class="date-item">
              <i class="fas fa-calendar-plus mr-1"></i>
              <span>Created: {{ formatDate(entry.created_at) }}</span>
            </div>
            <div v-if="entry.updated_at !== entry.created_at" class="date-item">
              <i class="fas fa-calendar-edit mr-1"></i>
              <span>Updated: {{ formatDate(entry.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Entry Content -->
      <article class="entry-content">
        <header class="content-header">
          <h1 class="entry-title">{{ entry.title }}</h1>
          
          <!-- Setup Information -->
          <div v-if="entry.setup_name" class="entry-setup">
            <div class="setup-card">
              <div class="setup-icon">
                <i class="fas fa-bow-arrow"></i>
              </div>
              <div class="setup-details">
                <div class="setup-name">{{ entry.setup_name }}</div>
                <div class="setup-type">{{ entry.bow_type }}</div>
              </div>
            </div>
          </div>

          <!-- Privacy Badge -->
          <div v-if="entry.is_private" class="privacy-badge">
            <i class="fas fa-lock mr-1"></i>
            Private Entry
          </div>
        </header>

        <!-- Entry Body -->
        <div class="entry-body">
          <div class="content-text" v-html="formatContent(entry.content)"></div>
        </div>

        <!-- Entry Images -->
        <div v-if="entry.images && entry.images.length > 0" class="entry-images">
          <h3 class="section-title">
            <i class="fas fa-images mr-2"></i>
            Images ({{ entry.images.length }})
          </h3>
          <div class="images-gallery">
            <div 
              v-for="(image, index) in entry.images" 
              :key="index"
              class="image-item"
              @click="openImageViewer(image, index)"
            >
              <img :src="image.url" :alt="image.alt" loading="lazy" />
              <div class="image-overlay">
                <i class="fas fa-expand"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Equipment Links -->
        <div v-if="entry.equipment_links && entry.equipment_links.length > 0" class="equipment-links">
          <h3 class="section-title">
            <i class="fas fa-tools mr-2"></i>
            Linked Equipment ({{ entry.equipment_links.length }})
          </h3>
          <div class="equipment-grid">
            <div 
              v-for="link in entry.equipment_links" 
              :key="link.id"
              class="equipment-card"
            >
              <div class="equipment-header">
                <div class="equipment-type">
                  <i :class="getEquipmentIcon(link.equipment_type)" class="mr-1"></i>
                  {{ capitalize(link.equipment_type) }}
                </div>
                <div class="link-type-badge" :class="`link-${link.link_type}`">
                  {{ formatLinkType(link.link_type) }}
                </div>
              </div>
              <div class="equipment-details">
                <div class="equipment-name">{{ link.equipment_name }}</div>
                <div v-if="link.manufacturer || link.model" class="equipment-brand">
                  {{ [link.manufacturer, link.model].filter(Boolean).join(' ') }}
                </div>
                <div v-if="link.specifications" class="equipment-specs">
                  <div v-for="(value, key) in JSON.parse(link.specifications)" :key="key" class="spec-item">
                    <strong>{{ capitalize(key.replace('_', ' ')) }}:</strong> {{ value }}
                  </div>
                </div>
                <div v-if="link.notes" class="equipment-notes">
                  <i class="fas fa-sticky-note mr-1"></i>
                  {{ link.notes }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tags -->
        <div v-if="entry.tags && entry.tags.length > 0" class="entry-tags">
          <h3 class="section-title">
            <i class="fas fa-tags mr-2"></i>
            Tags ({{ entry.tags.length }})
          </h3>
          <div class="tags-list">
            <span 
              v-for="tag in entry.tags" 
              :key="tag" 
              class="tag-chip"
              @click="filterByTag(tag)"
            >
              <i class="fas fa-tag mr-1"></i>
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- Change Log Links -->
        <div v-if="entry.change_log_links && entry.change_log_links.length > 0" class="change-log-links">
          <h3 class="section-title">
            <i class="fas fa-history mr-2"></i>
            Related Changes ({{ entry.change_log_links.length }})
          </h3>
          <div class="changelog-items">
            <div 
              v-for="link in entry.change_log_links" 
              :key="link.id"
              class="changelog-card"
            >
              <div class="changelog-type">{{ link.change_log_type }}</div>
              <div class="changelog-details">ID: {{ link.change_log_id }}</div>
            </div>
          </div>
        </div>
      </article>

      <!-- Entry Footer -->
      <footer class="entry-footer">
        <div class="footer-stats">
          <div class="stat-item">
            <i class="fas fa-eye mr-1"></i>
            <span>{{ entry.view_count || 0 }} views</span>
          </div>
          <div v-if="entry.template_used" class="stat-item">
            <i class="fas fa-magic mr-1"></i>
            <span>Created from template</span>
          </div>
        </div>
        
        <div class="footer-actions">
          <CustomButton @click="shareEntry" variant="ghost" icon="fas fa-share-alt">
            Share Entry
          </CustomButton>
          <CustomButton @click="printEntry" variant="ghost" icon="fas fa-print">
            Print
          </CustomButton>
        </div>
      </footer>
    </div>

    <!-- Image Viewer Modal -->
    <div v-if="imageViewerOpen" class="image-viewer-modal" @click="closeImageViewer">
      <div class="image-viewer-content" @click.stop>
        <button class="close-viewer-btn" @click="closeImageViewer">
          <i class="fas fa-times"></i>
        </button>
        <div class="image-navigation" v-if="entry.images.length > 1">
          <button 
            @click="previousImage" 
            :disabled="currentImageIndex === 0"
            class="nav-btn prev-btn"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <button 
            @click="nextImage" 
            :disabled="currentImageIndex === entry.images.length - 1"
            class="nav-btn next-btn"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
        <img 
          :src="entry.images[currentImageIndex]?.url" 
          :alt="entry.images[currentImageIndex]?.alt" 
          class="viewer-image"
        />
        <div class="image-info">
          <div class="image-alt">{{ entry.images[currentImageIndex]?.alt }}</div>
          <div class="image-counter">{{ currentImageIndex + 1 }} of {{ entry.images.length }}</div>
        </div>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <md-dialog :open="showDeleteConfirm" @close="showDeleteConfirm = false">
      <div slot="headline">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        Confirm Delete
      </div>
      <div slot="content">
        <p>Are you sure you want to delete this journal entry? This action cannot be undone.</p>
        <div class="entry-preview">
          <strong>{{ entry?.title }}</strong>
          <div class="preview-date">{{ formatDate(entry?.created_at) }}</div>
        </div>
      </div>
      <div slot="actions">
        <CustomButton @click="showDeleteConfirm = false" variant="ghost">
          Cancel
        </CustomButton>
        <CustomButton @click="confirmDelete" variant="danger" icon="fas fa-trash">
          Delete Entry
        </CustomButton>
      </div>
    </md-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '~/composables/useAuth'
import { useApi } from '~/composables/useApi'

// Set page meta
definePageMeta({
  title: 'Journal Entry',
  middleware: ['auth-check']
})

// Composables
const route = useRoute()
const router = useRouter()
const { token } = useAuth()
const { get, delete: apiDelete } = useApi()

// Reactive state
const entry = ref(null)
const pending = ref(true)
const error = ref(null)
const showDeleteConfirm = ref(false)

// Image viewer state
const imageViewerOpen = ref(false)
const currentImageIndex = ref(0)

// Get entry ID from route
const entryId = computed(() => route.params.id)

// Load entry data
const loadEntry = async () => {
  if (!entryId.value) {
    error.value = { message: 'Invalid entry ID' }
    pending.value = false
    return
  }

  try {
    pending.value = true
    error.value = null
    
    const response = await get(`/journal/entries/${entryId.value}`)
    entry.value = response.data
    
    // Update page title
    if (entry.value?.title) {
      useHead({ title: `${entry.value.title} - Journal Entry` })
    }
  } catch (err) {
    console.error('Failed to load journal entry:', err)
    error.value = err
  } finally {
    pending.value = false
  }
}

// Navigation methods
const goBack = () => {
  router.push('/journal')
}

const editEntry = () => {
  // Navigate to edit mode (you might want to pass entry data)
  router.push(`/journal?edit=${entryId.value}`)
}

// Image viewer methods
const openImageViewer = (image, index) => {
  currentImageIndex.value = index
  imageViewerOpen.value = true
}

const closeImageViewer = () => {
  imageViewerOpen.value = false
}

const previousImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  }
}

const nextImage = () => {
  if (currentImageIndex.value < entry.value.images.length - 1) {
    currentImageIndex.value++
  }
}

// Action methods
const shareEntry = () => {
  if (navigator.share) {
    navigator.share({
      title: entry.value.title,
      text: `Check out this journal entry: ${entry.value.title}`,
      url: window.location.href
    })
  } else {
    // Fallback - copy to clipboard
    navigator.clipboard.writeText(window.location.href)
    // You might want to show a toast notification here
  }
}

const printEntry = () => {
  window.print()
}

const deleteEntry = () => {
  showDeleteConfirm.value = true
}

const confirmDelete = async () => {
  try {
    await apiDelete(`/journal/entries/${entryId.value}`)
    showDeleteConfirm.value = false
    router.push('/journal')
  } catch (err) {
    console.error('Failed to delete entry:', err)
    // Show error notification
  }
}

const filterByTag = (tag) => {
  router.push(`/journal?tags=${encodeURIComponent(tag)}`)
}

// Utility methods
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

const formatContent = (content) => {
  if (!content) return ''
  // Convert line breaks to HTML
  return content.replace(/\n/g, '<br>')
}

const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const formatLinkType = (linkType) => {
  const types = {
    used_with: 'Used With',
    changed_from: 'Changed From',
    changed_to: 'Changed To',
    tested: 'Tested',
    reviewed: 'Reviewed'
  }
  return types[linkType] || capitalize(linkType.replace('_', ' '))
}

const getEntryTypeIcon = (type) => {
  const icons = {
    general: 'fas fa-sticky-note',
    setup_change: 'fas fa-tools',
    equipment_change: 'fas fa-exchange-alt',
    arrow_change: 'fas fa-arrow-right',
    tuning_session: 'fas fa-crosshairs',
    shooting_notes: 'fas fa-target',
    maintenance: 'fas fa-wrench',
    upgrade: 'fas fa-arrow-up'
  }
  return icons[type] || 'fas fa-sticky-note'
}

const getEntryTypeLabel = (type) => {
  const labels = {
    general: 'General Entry',
    setup_change: 'Setup Change',
    equipment_change: 'Equipment Change',
    arrow_change: 'Arrow Change',
    tuning_session: 'Tuning Session',
    shooting_notes: 'Shooting Notes',
    maintenance: 'Maintenance',
    upgrade: 'Upgrade'
  }
  return labels[type] || 'Journal Entry'
}

const getEquipmentIcon = (type) => {
  const icons = {
    bow: 'fas fa-bow-arrow',
    arrows: 'fas fa-arrow-right',
    sight: 'fas fa-crosshairs',
    rest: 'fas fa-hand-paper',
    stabilizer: 'fas fa-balance-scale',
    release: 'fas fa-hand-pointer',
    quiver: 'fas fa-quiver',
    other: 'fas fa-tools'
  }
  return icons[type] || 'fas fa-tools'
}

// Initialize
onMounted(() => {
  loadEntry()
})
</script>

<style scoped>
.journal-entry-page {
  min-height: 100vh;
  background: var(--md-sys-color-surface);
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  gap: 1.5rem;
}

.error-icon {
  font-size: 3rem;
  color: var(--md-sys-color-error);
}

.entry-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

/* Header Styles */
.entry-header {
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.entry-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.entry-type-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.type-tuning_session { background: var(--md-sys-color-error-container); color: var(--md-sys-color-on-error-container); }
.type-equipment_change { background: var(--md-sys-color-tertiary-container); color: var(--md-sys-color-on-tertiary-container); }
.type-shooting_notes { background: var(--md-sys-color-primary-container); color: var(--md-sys-color-on-primary-container); }

.entry-dates {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.date-item {
  display: flex;
  align-items: center;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
}

.privacy-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface-variant);
  margin-top: 0.5rem;
}

/* Content Styles */
.entry-content {
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 24px;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.content-header {
  margin-bottom: 2rem;
}

.entry-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
  margin: 0 0 1rem 0;
  line-height: 1.2;
}

.setup-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--md-sys-color-primary-container);
  border-radius: 16px;
  margin: 1rem 0;
}

.setup-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  border-radius: 12px;
  font-size: 1.5rem;
}

.setup-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-primary-container);
}

.setup-type {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-primary-container);
  opacity: 0.8;
}

.entry-body {
  margin: 2rem 0;
}

.content-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--md-sys-color-on-surface);
  white-space: pre-wrap;
}

/* Section Styles */
.section-title {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 2rem 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--md-sys-color-outline-variant);
}

/* Images Gallery */
.images-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.image-item {
  position: relative;
  aspect-ratio: 16/9;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.image-item:hover {
  transform: scale(1.02);
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
  color: white;
  font-size: 1.5rem;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

/* Equipment Grid */
.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.equipment-card {
  background: var(--md-sys-color-surface-container);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.equipment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.equipment-type {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.link-type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
}

.equipment-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.equipment-brand {
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 0.75rem;
}

.equipment-specs {
  display: grid;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.spec-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
}

.equipment-notes {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--md-sys-color-surface);
  border-radius: 8px;
  border-left: 3px solid var(--md-sys-color-primary);
  font-size: 0.875rem;
  font-style: italic;
}

/* Tags */
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-chip:hover {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  transform: translateY(-1px);
}

/* Change Log */
.changelog-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.changelog-card {
  padding: 1rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 12px;
  border-left: 4px solid var(--md-sys-color-secondary);
}

.changelog-type {
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.25rem;
}

.changelog-details {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Footer */
.entry-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: var(--md-sys-color-surface-container-low);
  border-radius: 16px;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-stats {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
}

.footer-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* Image Viewer Modal */
.image-viewer-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.image-viewer-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.close-viewer-btn {
  position: absolute;
  top: -60px;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.5rem;
  transition: background 0.2s ease;
}

.close-viewer-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-navigation {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 100%;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  z-index: 10;
}

.nav-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.25rem;
  transition: all 0.2s ease;
  pointer-events: auto;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.prev-btn {
  margin-left: -60px;
}

.next-btn {
  margin-right: -60px;
}

.viewer-image {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
}

.image-info {
  position: absolute;
  bottom: -60px;
  left: 0;
  right: 0;
  color: white;
  text-align: center;
}

.image-alt {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.image-counter {
  font-size: 0.875rem;
  opacity: 0.8;
}

/* Delete Confirmation */
.entry-preview {
  padding: 1rem;
  background: var(--md-sys-color-error-container);
  border-radius: 12px;
  margin: 1rem 0;
}

.entry-preview strong {
  color: var(--md-sys-color-on-error-container);
}

.preview-date {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-error-container);
  opacity: 0.8;
  margin-top: 0.25rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .entry-container {
    padding: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .entry-meta {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .entry-content {
    padding: 1.5rem;
  }
  
  .entry-title {
    font-size: 1.75rem;
  }
  
  .equipment-grid {
    grid-template-columns: 1fr;
  }
  
  .images-gallery {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  
  .footer-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
}

/* Print Styles */
@media print {
  .header-actions,
  .entry-footer,
  .image-overlay {
    display: none !important;
  }
  
  .entry-container {
    max-width: none;
    padding: 0;
  }
  
  .entry-content {
    border: none;
    box-shadow: none;
  }
  
  .images-gallery {
    display: none;
  }
}

/* Danger button style */
:deep(.danger) {
  color: var(--md-sys-color-error) !important;
}

:deep(.danger:hover) {
  background: var(--md-sys-color-error-container) !important;
  color: var(--md-sys-color-on-error-container) !important;
}
</style>