<template>
  <div class="tuning-image-upload">
    <!-- Header with Context Info -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-2">
          <i :class="testTypeIcon" class="text-lg text-primary-600 dark:text-primary-400"></i>
          <h3 class="font-medium text-gray-900 dark:text-gray-100">
            {{ testTypeLabel }} Images
          </h3>
        </div>
        <span v-if="imageLabel" class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded-full text-gray-600 dark:text-gray-300">
          {{ imageLabel }}
        </span>
      </div>
      <div class="text-sm text-gray-500 dark:text-gray-400">
        {{ images.length }}/{{ maxFiles }} images
      </div>
    </div>

    <!-- Quick Action Buttons -->
    <div class="grid grid-cols-2 gap-3 mb-4" v-if="showQuickActions">
      <button
        @click="captureImage('before')"
        :disabled="isUploading"
        class="flex items-center justify-center space-x-2 p-3 border-2 border-dashed border-blue-300 dark:border-blue-600 rounded-lg hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
      >
        <i class="fas fa-camera text-blue-500"></i>
        <span class="text-sm font-medium text-blue-600 dark:text-blue-400">Before Shot</span>
      </button>
      <button
        @click="captureImage('after')"
        :disabled="isUploading"
        class="flex items-center justify-center space-x-2 p-3 border-2 border-dashed border-green-300 dark:border-green-600 rounded-lg hover:border-green-400 dark:hover:border-green-500 transition-colors"
      >
        <i class="fas fa-camera text-green-500"></i>
        <span class="text-sm font-medium text-green-600 dark:text-green-400">After Shot</span>
      </button>
    </div>

    <!-- Drag & Drop Upload Area -->
    <div
      @drop="handleDrop"
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
      @click="triggerFileSelect"
      :class="[
        'relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
        dragOver ? 'border-primary-400 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600',
        isUploading ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800'
      ]"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/*"
        @change="handleFileSelect"
        class="hidden"
      />

      <div v-if="isUploading" class="space-y-2">
        <i class="fas fa-spinner fa-spin text-2xl text-primary-500"></i>
        <p class="text-sm text-gray-600 dark:text-gray-400">Uploading...</p>
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div 
            class="bg-primary-500 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${uploadProgress}%` }"
          ></div>
        </div>
      </div>

      <div v-else class="space-y-2">
        <i class="fas fa-images text-3xl text-gray-400"></i>
        <div>
          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
            Drop images here or click to select
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Supports: JPG, PNG, WebP (max {{ maxSize }}MB each)
          </p>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
      <div class="flex items-start space-x-2">
        <i class="fas fa-exclamation-triangle text-red-500 mt-0.5"></i>
        <p class="text-sm text-red-700 dark:text-red-400">{{ error }}</p>
      </div>
    </div>

    <!-- Uploaded Images Gallery -->
    <div v-if="images.length > 0" class="mt-6">
      <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">
        Uploaded Images
      </h4>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        <div
          v-for="(image, index) in images"
          :key="image.id"
          class="relative group"
        >
          <div class="aspect-square bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
            <img
              :src="image.url"
              :alt="image.alt || image.originalName"
              class="w-full h-full object-cover"
            />
            
            <!-- Image Overlay -->
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center">
              <div class="opacity-0 group-hover:opacity-100 transition-opacity flex space-x-2">
                <button
                  @click="viewImage(image)"
                  class="p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100"
                >
                  <i class="fas fa-eye text-gray-700"></i>
                </button>
                <button
                  @click="removeImage(index)"
                  class="p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100"
                >
                  <i class="fas fa-trash text-red-500"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Image Info -->
          <div class="mt-2 text-center">
            <p class="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">
              {{ image.imageLabel || 'Test Image' }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatFileSize(image.size) }}
            </p>
          </div>

          <!-- Status Badge -->
          <div 
            v-if="image.status === 'uploading'"
            class="absolute top-1 right-1 px-1.5 py-0.5 bg-blue-500 text-white text-xs rounded-full"
          >
            <i class="fas fa-spinner fa-spin mr-1"></i>
          </div>
          <div 
            v-else-if="image.status === 'error'"
            class="absolute top-1 right-1 px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full"
          >
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div 
            v-else-if="image.status === 'success'"
            class="absolute top-1 right-1 px-1.5 py-0.5 bg-green-500 text-white text-xs rounded-full"
          >
            <i class="fas fa-check"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Viewer Modal -->
    <div
      v-if="viewingImage"
      class="fixed inset-0 z-50 bg-black bg-opacity-75 flex items-center justify-center p-4"
      @click="closeImageViewer"
    >
      <div class="relative max-w-4xl max-h-full">
        <img
          :src="viewingImage.url"
          :alt="viewingImage.alt"
          class="max-w-full max-h-full object-contain"
        />
        <button
          @click="closeImageViewer"
          class="absolute top-4 right-4 p-2 bg-black bg-opacity-50 text-white rounded-full hover:bg-opacity-75"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useImageUpload, type ImageUploadConfig, type UploadedImage } from '~/composables/useImageUpload'

interface Props {
  sessionId: number
  testType: 'paper' | 'bareshaft' | 'walkback'
  imageLabel?: string
  maxFiles?: number
  maxSize?: number
  showQuickActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxFiles: 10,
  maxSize: 50,
  showQuickActions: true
})

const emit = defineEmits<{
  imagesUploaded: [images: UploadedImage[]]
  imageRemoved: [image: UploadedImage]
}>()

// Image upload configuration
const uploadConfig: ImageUploadConfig = {
  context: 'tuning',
  sessionId: props.sessionId,
  testType: props.testType,
  imageLabel: props.imageLabel,
  maxFiles: props.maxFiles,
  maxSize: props.maxSize
}

// Use the image upload composable
const {
  state,
  uploadFiles,
  removeImage: removeImageFromState
} = useImageUpload(uploadConfig)

// Reactive references
const fileInput = ref<HTMLInputElement>()
const viewingImage = ref<UploadedImage | null>(null)
const dragOver = ref(false)

// Computed properties
const { isUploading, uploadProgress, error, images } = state

const testTypeIcon = computed(() => {
  const icons = {
    paper: 'fas fa-bullseye',
    bareshaft: 'fas fa-arrow-right',
    walkback: 'fas fa-crosshairs'
  }
  return icons[props.testType] || 'fas fa-camera'
})

const testTypeLabel = computed(() => {
  const labels = {
    paper: 'Paper Tuning',
    bareshaft: 'Bareshaft Tuning', 
    walkback: 'Walkback Tuning'
  }
  return labels[props.testType] || 'Tuning'
})

// Methods
const triggerFileSelect = () => {
  if (!isUploading.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files?.length) {
    uploadFiles(Array.from(target.files))
    target.value = '' // Reset input
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = false
  
  if (event.dataTransfer?.files.length && !isUploading.value) {
    uploadFiles(Array.from(event.dataTransfer.files))
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (!isUploading.value) {
    dragOver.value = true
  }
}

const handleDragLeave = () => {
  dragOver.value = false
}

const captureImage = (type: 'before' | 'after') => {
  // Set the image label based on the capture type
  uploadConfig.imageLabel = type === 'before' ? 'Before Adjustment' : 'After Adjustment'
  triggerFileSelect()
}

const removeImage = (index: number) => {
  const image = images.value[index]
  if (image) {
    removeImageFromState(index)
    emit('imageRemoved', image)
  }
}

const viewImage = (image: UploadedImage) => {
  viewingImage.value = image
}

const closeImageViewer = () => {
  viewingImage.value = null
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Watch for image changes and emit to parent
watch(images, (newImages) => {
  emit('imagesUploaded', newImages)
}, { deep: true })
</script>

<style scoped>
/* Additional styling if needed */
.tuning-image-upload {
  @apply max-w-full;
}

/* Smooth transitions for drag states */
.tuning-image-upload [class*="border-dashed"] {
  transition: all 0.2s ease-in-out;
}

/* Image grid responsive adjustments */
@media (max-width: 640px) {
  .tuning-image-upload .grid-cols-2 {
    @apply grid-cols-1;
  }
}
</style>