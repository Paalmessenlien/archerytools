<template>
  <md-dialog :open="show" @close="$emit('close')">
    <div slot="headline">{{ isEditing ? 'Edit Entry' : 'New Journal Entry' }}</div>
    
    <form slot="content" class="journal-form" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label class="form-label">Title *</label>
        <md-outlined-text-field
          :value="formData.title"
          @input="(e) => formData.title = e.target.value"
          placeholder="Enter entry title..."
          required
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Bow Setup</label>
        <md-outlined-select 
          :value="formData.bow_setup_id?.toString() || ''" 
          @change="(e) => formData.bow_setup_id = e.target.value ? parseInt(e.target.value) : null"
          class="form-input"
        >
          <md-select-option value="">No specific setup</md-select-option>
          <md-select-option 
            v-for="setup in bowSetups" 
            :key="setup.id" 
            :value="setup.id.toString()"
          >
            {{ setup.name }} ({{ setup.bow_type }})
          </md-select-option>
        </md-outlined-select>
      </div>

      <div class="form-group">
        <label class="form-label">Entry Type</label>
        <md-outlined-select 
          :value="formData.entry_type" 
          @change="(e) => formData.entry_type = e.target.value"
          class="form-input"
        >
          <md-select-option 
            v-for="type in entryTypes" 
            :key="type.value" 
            :value="type.value"
          >
            {{ type.label }}
          </md-select-option>
        </md-outlined-select>
      </div>

      <div class="form-group">
        <label class="form-label">Content *</label>
        <md-outlined-text-field
          :value="formData.content"
          @input="(e) => formData.content = e.target.value"
          placeholder="Write your journal entry..."
          required
          type="textarea"
          rows="6"
          class="form-input content-textarea"
        />
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
                  <md-icon>delete</md-icon>
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
              :max-size-bytes="52428800"
              @upload-success="handleImageUpload"
              @upload-error="handleImageError"
            />
          </div>
          
          <!-- Upload Guidelines -->
          <div class="upload-guidelines">
            <p class="guideline-text">
              <md-icon>info</md-icon>
              Add up to 10 photos to document your archery journey (max 50MB each)
            </p>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Tags (comma-separated)</label>
        <md-outlined-text-field
          :value="formData.tagsString"
          @input="(e) => formData.tagsString = e.target.value"
          placeholder="e.g. tuning, sight, arrows..."
          class="form-input"
        />
      </div>

      <div class="form-group">
        <md-checkbox 
          :checked="formData.is_private"
          @change="(e) => formData.is_private = e.target.checked"
        >
          Private entry (only visible to you)
        </md-checkbox>
      </div>
    </form>

    <div slot="actions">
      <md-text-button @click="$emit('close')">Cancel</md-text-button>
      <md-filled-button @click="handleSubmit" :disabled="!isFormValid">
        {{ isEditing ? 'Update' : 'Create' }}
      </md-filled-button>
    </div>
  </md-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  entry: Object,
  bowSetups: Array,
  entryTypes: Array
})

const emit = defineEmits(['close', 'save'])

const isEditing = computed(() => !!props.entry?.id)

const formData = ref({
  title: '',
  content: '',
  bow_setup_id: null,
  entry_type: 'general',
  tagsString: '',
  is_private: false,
  images: []
})

// Image management
const attachedImages = computed(() => formData.value.images || [])

const isFormValid = computed(() => {
  return formData.value.title?.trim() && formData.value.content?.trim()
})

const resetForm = () => {
  formData.value = {
    title: '',
    content: '',
    bow_setup_id: null,
    entry_type: 'general',
    tagsString: '',
    is_private: false,
    images: []
  }
}

const populateForm = (entry) => {
  if (entry) {
    formData.value = {
      title: entry.title || '',
      content: entry.content || '',
      bow_setup_id: entry.bow_setup_id || null,
      entry_type: entry.entry_type || 'general',
      tagsString: entry.tags ? entry.tags.join(', ') : '',
      is_private: entry.is_private || false,
      images: entry.images || []
    }
  }
}

const handleSubmit = () => {
  if (!isFormValid.value) return

  const submitData = {
    title: formData.value.title.trim(),
    content: formData.value.content.trim(),
    bow_setup_id: formData.value.bow_setup_id,
    entry_type: formData.value.entry_type,
    tags: formData.value.tagsString 
      ? formData.value.tagsString.split(',').map(tag => tag.trim()).filter(Boolean)
      : [],
    is_private: formData.value.is_private,
    images: formData.value.images || []
  }

  emit('save', submitData)
}

// Image management functions
const handleImageUpload = (imageUrl) => {
  const imageData = {
    url: imageUrl,
    uploadedAt: new Date().toISOString(),
    alt: 'Journal image'
  }
  
  if (!formData.value.images) {
    formData.value.images = []
  }
  formData.value.images.push(imageData)
}

const removeImage = (index) => {
  if (formData.value.images && index >= 0 && index < formData.value.images.length) {
    formData.value.images.splice(index, 1)
  }
}

const handleImageError = (error) => {
  console.error('Image upload error:', error)
  // Could show a toast or alert here
}

// Watch for dialog open/close and entry changes
watch(() => props.show, (newValue) => {
  if (newValue) {
    if (props.entry) {
      populateForm(props.entry)
    } else {
      resetForm()
    }
  }
})

watch(() => props.entry, (newEntry) => {
  if (props.show && newEntry) {
    populateForm(newEntry)
  }
})
</script>

<style scoped>
.journal-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 500px;
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

.content-textarea {
  min-height: 120px;
}

md-dialog {
  --md-dialog-container-max-width: 700px;
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
  background: var(--md-sys-color-surface-variant);
  transition: all 0.2s ease;
}

.upload-area:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
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
  line-height: 1.4;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-form {
    max-width: none;
  }
  
  md-dialog {
    --md-dialog-container-max-width: 100%;
    --md-dialog-container-margin: 1rem;
  }
  
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