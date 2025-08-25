<template>
  <div class="journal-form-fields">
    <!-- Title Field -->
    <div class="form-group">
      <div class="form-label-section">
        <label class="form-label">Title *</label>
        <div class="character-count" :class="{ 'over-limit': characterCounts?.title > limits?.title?.max }">
          {{ characterCounts?.title || 0 }} / {{ limits?.title?.max || 200 }}
        </div>
      </div>
      <md-outlined-text-field
        :value="formData.title"
        @input="(e) => $emit('update:form-data', 'title', e.target.value)"
        placeholder="Enter entry title..."
        required
        class="form-input"
        :class="{ 
          'has-error': showValidation && validationResults?.title && !validationResults.title.isValid,
          'has-success': showValidation && validationResults?.title && validationResults.title.isValid && formData.title
        }"
      />
      <div v-if="showValidation && validationResults?.title && !validationResults.title.isValid" class="field-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ validationResults.title.message }}
      </div>
    </div>

    <!-- Bow Setup Field -->
    <div class="form-group">
      <label class="form-label">Bow Setup (Optional)</label>
      <select
        :value="formData.bow_setup_id || ''"
        @change="(e) => $emit('update:form-data', 'bow_setup_id', e.target.value || null)"
        class="form-select"
      >
        <option value="">General Notes (not about a specific setup)</option>
        <option 
          v-for="setup in bowSetups" 
          :key="setup.id"
          :value="setup.id"
        >
          {{ setup.name }} - {{ setup.bow_type }} • {{ getSetupDetails(setup) }}
        </option>
      </select>
    </div>

    <!-- Entry Type Field -->
    <div class="form-group">
      <label class="form-label">Entry Type *</label>
      <select
        :value="formData.entry_type || ''"
        @change="(e) => $emit('update:form-data', 'entry_type', e.target.value)"
        required
        class="form-select"
        :class="{ 
          'has-error': showValidation && validationResults?.entry_type && !validationResults.entry_type.isValid,
          'has-success': showValidation && validationResults?.entry_type && validationResults.entry_type.isValid && formData.entry_type
        }"
      >
        <option value="" disabled>Select entry type...</option>
        <option 
          v-for="type in entryTypes" 
          :key="type.value"
          :value="type.value"
        >
          {{ type.label }} - {{ getEntryTypeDescription(type.value) }}
        </option>
      </select>
      <div v-if="showValidation && validationResults?.entry_type && !validationResults.entry_type.isValid" class="field-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ validationResults.entry_type.message }}
      </div>
    </div>

    <!-- Content Field -->
    <div class="form-group">
      <div class="form-label-section">
        <label class="form-label">Content *</label>
        <div class="character-count" :class="{ 'over-limit': characterCounts?.content > limits?.content?.max }">
          {{ characterCounts?.content || 0 }} / {{ limits?.content?.max || 5000 }}
        </div>
      </div>
      <md-outlined-text-field
        :value="formData.content"
        @input="(e) => $emit('update:form-data', 'content', e.target.value)"
        placeholder="Write your journal entry..."
        required
        type="textarea"
        rows="6"
        class="form-input content-textarea"
        :class="{ 
          'has-error': showValidation && validationResults?.content && !validationResults.content.isValid,
          'has-success': showValidation && validationResults?.content && validationResults.content.isValid && formData.content
        }"
      />
      <div v-if="showValidation && validationResults?.content && !validationResults.content.isValid" class="field-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ validationResults.content.message }}
      </div>
      <div v-if="characterCounts?.content >= limits?.content?.min" class="field-success">
        <i class="fas fa-check-circle"></i>
        Good length for a detailed entry
      </div>
    </div>

    <!-- Image Upload Section -->
    <div class="form-group">
      <label class="form-label">Images ({{ attachedImages?.length || 0 }}/10)</label>
      <div class="image-upload-section">
        <!-- Current Images Display -->
        <div v-if="attachedImages?.length" class="attached-images-grid">
          <div v-for="(image, index) in attachedImages" :key="index" class="image-preview-item">
            <img :src="image.url" :alt="image.alt || 'Journal image'" class="preview-image" />
            <div class="image-overlay">
              <button 
                @click="removeImage(index)" 
                class="remove-image-btn"
                type="button"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Image Upload Component -->
        <div v-if="!attachedImages?.length || attachedImages.length < 10" class="upload-area">
          <ImageUpload
            :current-image-url="''"
            alt-text="Journal image"
            upload-path="journal"
            :max-size-bytes="5242880"
            @upload-success="handleImageUpload"
            @upload-error="handleImageError"
          />
        </div>
        
        <!-- Upload Guidelines -->
        <div class="upload-guidelines">
          <p class="guideline-text">
            <i class="fas fa-info-circle"></i>
            Add up to 10 photos to document your archery journey (max 5MB each)
          </p>
        </div>
      </div>
    </div>

    <!-- Tags Field -->
    <div class="form-group">
      <div class="form-label-section">
        <label class="form-label">Tags (comma-separated)</label>
        <div class="character-count" :class="{ 'over-limit': characterCounts?.tags > limits?.tags?.max }">
          {{ characterCounts?.tags || 0 }} / {{ limits?.tags?.max || 500 }}
        </div>
      </div>
      <md-outlined-text-field
        :value="formData.tagsString"
        @input="(e) => $emit('update:form-data', 'tagsString', e.target.value)"
        placeholder="e.g. tuning, sight, arrows..."
        class="form-input"
        :class="{ 
          'has-error': showValidation && validationResults?.tags && !validationResults.tags.isValid,
          'has-success': formData.tagsString && (!showValidation || !validationResults?.tags || validationResults.tags.isValid)
        }"
      />
      <div v-if="showValidation && validationResults?.tags && !validationResults.tags.isValid" class="field-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ validationResults.tags.message }}
      </div>
      <div v-if="formData.tagsString" class="field-hint">
        <i class="fas fa-info-circle"></i>
        {{ getTagCount(formData.tagsString) }} tag{{ getTagCount(formData.tagsString) === 1 ? '' : 's' }}
      </div>
    </div>

    <!-- Private Entry Checkbox -->
    <div class="form-group">
      <md-checkbox 
        :checked="formData.is_private"
        @change="(e) => $emit('update:form-data', 'is_private', e.target.checked)"
      >
        Private entry (only visible to you)
      </md-checkbox>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  formData: Object,
  bowSetups: Array,
  entryTypes: Array,
  validationResults: Object,
  characterCounts: Object,
  limits: Object,
  showValidation: Boolean,
  attachedImages: Array
})

const emit = defineEmits(['update:form-data', 'image-uploaded', 'image-removed', 'image-error'])

// Handle image upload success
const handleImageUpload = (imageUrl) => {
  const imageData = {
    url: imageUrl,
    uploadedAt: new Date().toISOString(),
    alt: 'Journal image'
  }
  emit('image-uploaded', imageData)
}

// Handle image upload error
const handleImageError = (error) => {
  emit('image-error', error)
}

// Remove attached image
const removeImage = (index) => {
  emit('image-removed', index)
}

// Helper function to count tags
const getTagCount = (tagsString) => {
  if (!tagsString?.trim()) return 0
  return tagsString.split(',').map(tag => tag.trim()).filter(Boolean).length
}

// Helper functions
const getSetupDetails = (setup) => {
  const details = []
  if (setup.draw_weight) details.push(`${setup.draw_weight}#`)
  if (setup.draw_length) details.push(`${setup.draw_length}"`)
  return details.join(' • ') || 'No details'
}

const getEntryTypeIcon = (typeValue) => {
  const icons = {
    general: 'fas fa-sticky-note',
    setup_change: 'fas fa-tools',
    equipment_change: 'fas fa-cog',
    arrow_change: 'fas fa-bullseye',
    tuning_session: 'fas fa-crosshairs',
    shooting_notes: 'fas fa-target',
    maintenance: 'fas fa-wrench',
    upgrade: 'fas fa-arrow-up'
  }
  return icons[typeValue] || 'fas fa-sticky-note'
}

const getEntryTypeDescription = (typeValue) => {
  const descriptions = {
    general: 'General thoughts, observations, or notes',
    setup_change: 'Changes to bow configuration or settings',
    equipment_change: 'Installing, removing, or swapping equipment',
    arrow_change: 'Switching arrows or spine adjustments',
    tuning_session: 'Detailed tuning process and results',
    shooting_notes: 'Performance observations and scores',
    maintenance: 'Cleaning, servicing, or repairs',
    upgrade: 'New equipment purchases and upgrades'
  }
  return descriptions[typeValue] || 'Document your archery journey'
}
</script>

<style scoped>
.journal-form-fields {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  font-size: 0.875rem;
}

.form-input {
  width: 100%;
}

.form-select {
  width: 100%;
  padding: 1rem;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.form-select:focus {
  outline: none;
  border-color: var(--md-sys-color-primary);
}

.form-select:hover {
  border-color: var(--md-sys-color-on-surface-variant);
}

.form-select.has-error {
  border-color: var(--md-sys-color-error);
}

.form-select.has-success {
  border-color: var(--md-sys-color-primary);
}

.content-textarea {
  min-height: 120px;
}

/* Enhanced form styling for validation feedback */
.form-label-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.character-count {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
}

.character-count.over-limit {
  color: var(--md-sys-color-error);
  background: var(--md-sys-color-error-container);
}

.form-input.has-error {
  border-color: var(--md-sys-color-error) !important;
  --md-outlined-text-field-outline-color: var(--md-sys-color-error);
}

.form-input.has-success {
  --md-outlined-text-field-outline-color: var(--md-sys-color-primary);
}

.field-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-error);
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--md-sys-color-error-container);
  border-radius: 8px;
}

.field-success {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-primary);
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--md-sys-color-primary-container);
  border-radius: 8px;
}

.field-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
}

/* Image Upload Section Styles */
.image-upload-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.attached-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid var(--md-sys-color-outline-variant);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview-item:hover .image-overlay {
  opacity: 1;
}

.remove-image-btn {
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remove-image-btn:hover {
  background: var(--md-sys-color-error-container);
  transform: scale(1.1);
}

.upload-area {
  border: 2px dashed var(--md-sys-color-outline-variant);
  border-radius: 8px;
  padding: 1rem;
}

.upload-guidelines {
  padding: 0.75rem 1rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
}

.guideline-text {
  margin: 0;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  /* Mobile responsiveness for image grid */
  .attached-images-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 0.75rem;
  }
  
  .remove-image-btn {
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
  
  .upload-area {
    padding: 0.75rem;
  }
}
</style>