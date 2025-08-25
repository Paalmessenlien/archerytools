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
  is_private: false
})

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
    is_private: false
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
      is_private: entry.is_private || false
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
    is_private: formData.value.is_private
  }

  emit('save', submitData)
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
  --md-dialog-container-max-width: 600px;
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
}
</style>