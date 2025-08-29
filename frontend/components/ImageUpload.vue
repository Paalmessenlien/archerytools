<template>
  <div class="image-upload-container">
    <!-- Current Image Display -->
    <div class="mb-4 text-center">
      <div class="relative inline-block">
        <img 
          v-if="currentImageUrl" 
          :src="currentImageUrl" 
          :alt="altText"
          class="w-32 h-32 rounded-full object-cover border-4 border-gray-200 dark:border-gray-600"
        />
        <div 
          v-else 
          class="w-32 h-32 rounded-full bg-gray-200 dark:bg-gray-700 border-4 border-gray-200 dark:border-gray-600 flex items-center justify-center"
        >
          <i class="fas fa-user text-4xl text-gray-400 dark:text-gray-500"></i>
        </div>
        
        <!-- Upload Status Overlay -->
        <div 
          v-if="isUploading" 
          class="absolute inset-0 rounded-full bg-black bg-opacity-50 flex items-center justify-center"
        >
          <i class="fas fa-spinner fa-spin text-white text-2xl"></i>
        </div>
      </div>
    </div>

    <!-- Upload Controls -->
    <div class="text-center space-y-3">
      <!-- File Input (Hidden) -->
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleFileSelect"
        class="hidden"
      />

      <!-- Upload Button -->
      <CustomButton
        @click="triggerFileSelect"
        :disabled="isUploading"
        variant="outlined"
        size="small"
        class="w-full"
      >
        <i class="fas fa-camera mr-2"></i>
        {{ currentImageUrl ? 'Change Photo' : 'Upload Photo' }}
      </CustomButton>

      <!-- Remove Button (only show if image exists) -->
      <CustomButton
        v-if="currentImageUrl && !isUploading"
        @click="removeImage"
        variant="text"
        size="small"
        class="w-full text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
      >
        <i class="fas fa-trash mr-2"></i>
        Remove Photo
      </CustomButton>

      <!-- Upload Progress -->
      <div v-if="isUploading" class="text-sm text-gray-600 dark:text-gray-400">
        Uploading image...
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="text-sm text-red-600">
        <i class="fas fa-exclamation-circle mr-1"></i>
        {{ errorMessage }}
      </div>
      
      <!-- General State Error -->
      <div v-if="imageUpload.state.error && !errorMessage" class="text-sm text-red-600">
        <i class="fas fa-exclamation-circle mr-1"></i>
        {{ imageUpload.state.error }}
      </div>
    </div>

    <!-- Upload Guidelines -->
    <div class="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
      <p>Recommended: Square image, max 50MB</p>
      <p>Supported formats: JPG, PNG, GIF, WebP</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// Import the universal image upload composable
import { useImageUpload } from '~/composables/useImageUpload'

interface Props {
  currentImageUrl?: string
  altText?: string
  uploadPath?: string // e.g., 'profile', 'arrow', 'bow'
  maxSizeBytes?: number
  allowedTypes?: string[]
  entityId?: string | number // For linking images to specific entities
}

interface Emits {
  (e: 'upload-success', imageUrl: string): void
  (e: 'upload-error', error: string): void
  (e: 'image-removed'): void
}

const props = withDefaults(defineProps<Props>(), {
  altText: 'Uploaded image',
  uploadPath: 'profile',
  maxSizeBytes: 50 * 1024 * 1024, // 50MB default
  allowedTypes: () => ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
})

const emit = defineEmits<Emits>()

// Use universal image upload composable
const imageUpload = useImageUpload({
  context: props.uploadPath as 'journal' | 'equipment' | 'profile' | 'setup' | 'arrow',
  maxFiles: 1, // Single image upload for this component
  maxSize: Math.round(props.maxSizeBytes / (1024 * 1024)), // Convert bytes to MB
  allowedTypes: props.allowedTypes,
  entityId: props.entityId ? Number(props.entityId) : undefined
})

// Reactive state
const fileInput = ref<HTMLInputElement>()

// Computed properties
const isUploading = computed(() => imageUpload.uploadingImages.value.length > 0)
const errorMessage = computed(() => {
  const errorImages = imageUpload.failedImages.value
  if (errorImages.length > 0) {
    return errorImages[0].error || 'Upload failed'
  }
  return imageUpload.state.error || ''
})

// Methods
const triggerFileSelect = () => {
  if (!isUploading.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  
  if (!files?.length) return
  
  try {
    // Clear any previous images since this is a single image component
    imageUpload.clearImages()
    
    // Upload the new image
    const result = await imageUpload.uploadSingleImage(files[0])
    
    if (result.status === 'success') {
      emit('upload-success', result.cdnUrl || result.url)
    } else {
      emit('upload-error', result.error || 'Upload failed')
    }
    
  } catch (error: any) {
    console.error('Upload error:', error)
    const errorMsg = error.message || 'Upload failed. Please try again.'
    emit('upload-error', errorMsg)
  } finally {
    // Clear the input so the same file can be selected again
    target.value = ''
  }
}

const removeImage = () => {
  imageUpload.clearImages()
  emit('image-removed')
}

// Clear errors when image changes
watch(() => props.currentImageUrl, () => {
  if (props.currentImageUrl) {
    imageUpload.clearImages()
  }
})
</script>

<style scoped>
.image-upload-container {
  @apply max-w-xs mx-auto;
}

/* Hover effect for image */
.image-upload-container img:hover {
  @apply transform scale-105 transition-transform duration-200;
}

/* Loading animation */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.fa-spin {
  animation: spin 1s linear infinite;
}
</style>