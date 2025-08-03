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
    </div>

    <!-- Upload Guidelines -->
    <div class="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
      <p>Recommended: Square image, max 5MB</p>
      <p>Supported formats: JPG, PNG, GIF, WebP</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  currentImageUrl?: string
  altText?: string
  uploadPath?: string // e.g., 'profile', 'arrow', 'bow'
  maxSizeBytes?: number
  allowedTypes?: string[]
}

interface Emits {
  (e: 'upload-success', imageUrl: string): void
  (e: 'upload-error', error: string): void
  (e: 'image-removed'): void
}

const props = withDefaults(defineProps<Props>(), {
  altText: 'Uploaded image',
  uploadPath: 'profile',
  maxSizeBytes: 5 * 1024 * 1024, // 5MB default
  allowedTypes: () => ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
})

const emit = defineEmits<Emits>()

// Composables
const api = useApi()

// Reactive state
const isUploading = ref(false)
const errorMessage = ref('')
const fileInput = ref<HTMLInputElement>()

// Methods
const triggerFileSelect = () => {
  if (!isUploading.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // Validate file
  const validation = validateFile(file)
  if (!validation.valid) {
    errorMessage.value = validation.error
    return
  }
  
  // Clear any previous errors
  errorMessage.value = ''
  
  // Upload file
  await uploadImage(file)
  
  // Clear the input so the same file can be selected again
  target.value = ''
}

const validateFile = (file: File): { valid: boolean; error: string } => {
  // Check file type
  if (!props.allowedTypes.includes(file.type)) {
    return {
      valid: false, 
      error: `File type not supported. Please use: ${props.allowedTypes.map(t => t.split('/')[1].toUpperCase()).join(', ')}`
    }
  }
  
  // Check file size
  if (file.size > props.maxSizeBytes) {
    const maxSizeMB = Math.round(props.maxSizeBytes / (1024 * 1024))
    return {
      valid: false,
      error: `File too large. Maximum size: ${maxSizeMB}MB`
    }
  }
  
  return { valid: true, error: '' }
}

const uploadImage = async (file: File) => {
  isUploading.value = true
  
  try {
    // Create FormData for file upload
    const formData = new FormData()
    formData.append('image', file)
    formData.append('upload_path', props.uploadPath)
    
    // Generate unique filename
    const timestamp = Date.now()
    const randomStr = Math.random().toString(36).substring(2, 8)
    const extension = file.name.split('.').pop()
    const filename = `${props.uploadPath}_${timestamp}_${randomStr}.${extension}`
    formData.append('filename', filename)
    
    // Upload to API
    const response = await api.post('/upload/image', formData)
    
    if (response.data && response.data.cdn_url) {
      emit('upload-success', response.data.cdn_url)
    } else {
      throw new Error('No CDN URL returned from server')
    }
    
  } catch (error: any) {
    console.error('Upload error:', error)
    
    let errorMsg = 'Upload failed. Please try again.'
    if (error.response?.data?.error) {
      errorMsg = error.response.data.error
    } else if (error.message) {
      errorMsg = error.message
    }
    
    errorMessage.value = errorMsg
    emit('upload-error', errorMsg)
    
  } finally {
    isUploading.value = false
  }
}

const removeImage = () => {
  emit('image-removed')
}

// Clear error when component unmounts or image changes
watch(() => props.currentImageUrl, () => {
  errorMessage.value = ''
})

onUnmounted(() => {
  errorMessage.value = ''
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