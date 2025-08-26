/**
 * Universal Image Upload Composable
 * Reusable across the entire system for journal, equipment, profile, and setup images
 */

import { ref, reactive, computed, readonly } from 'vue'
import { useApi } from './useApi'
import { useGlobalNotifications } from './useNotificationSystem'

export interface ImageUploadConfig {
  context: 'journal' | 'equipment' | 'profile' | 'setup' | 'arrow'
  entityId?: number
  maxFiles?: number
  maxSize?: number // in MB
  allowedTypes?: string[]
  cdnPath?: string
  compressionQuality?: number
}

export interface UploadedImage {
  id?: string
  url: string
  cdnUrl?: string
  originalName: string
  size: number
  type: string
  alt?: string
  uploadedAt: string
  status: 'uploading' | 'success' | 'error'
  error?: string
}

export interface ImageUploadState {
  isUploading: boolean
  uploadProgress: number
  error: string | null
  images: UploadedImage[]
  dragOver: boolean
}

const defaultConfig: Partial<ImageUploadConfig> = {
  maxFiles: 10,
  maxSize: 5, // 5MB
  allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
  compressionQuality: 0.8
}

export const useImageUpload = (config: ImageUploadConfig) => {
  const api = useApi()
  const notifications = useGlobalNotifications()
  
  const mergedConfig = { ...defaultConfig, ...config }
  
  const state = reactive<ImageUploadState>({
    isUploading: false,
    uploadProgress: 0,
    error: null,
    images: [],
    dragOver: false
  })

  // Computed properties
  const canUploadMore = computed(() => {
    return state.images.length < (mergedConfig.maxFiles || 10)
  })

  const hasImages = computed(() => state.images.length > 0)

  const uploadingImages = computed(() => 
    state.images.filter(img => img.status === 'uploading')
  )

  const successfulImages = computed(() => 
    state.images.filter(img => img.status === 'success')
  )

  const failedImages = computed(() => 
    state.images.filter(img => img.status === 'error')
  )

  // Validation functions
  const validateFile = (file: File): { valid: boolean; error?: string } => {
    // Check file type
    if (!mergedConfig.allowedTypes?.includes(file.type)) {
      return {
        valid: false,
        error: `File type ${file.type} not allowed. Allowed types: ${mergedConfig.allowedTypes?.join(', ')}`
      }
    }

    // Check file size
    const maxSizeBytes = (mergedConfig.maxSize || 5) * 1024 * 1024
    if (file.size > maxSizeBytes) {
      return {
        valid: false,
        error: `File size ${(file.size / 1024 / 1024).toFixed(1)}MB exceeds limit of ${mergedConfig.maxSize}MB`
      }
    }

    // Check if can upload more
    if (!canUploadMore.value) {
      return {
        valid: false,
        error: `Cannot upload more than ${mergedConfig.maxFiles} images`
      }
    }

    return { valid: true }
  }

  const generateImageId = (file: File): string => {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(7)
    return `${mergedConfig.context}_${timestamp}_${random}`
  }

  const createImageObject = (file: File): UploadedImage => {
    return {
      id: generateImageId(file),
      url: URL.createObjectURL(file), // Temporary URL for preview
      originalName: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date().toISOString(),
      status: 'uploading'
    }
  }

  // Core upload function
  const uploadSingleImage = async (file: File): Promise<UploadedImage> => {
    const validation = validateFile(file)
    if (!validation.valid) {
      throw new Error(validation.error)
    }

    const imageObj = createImageObject(file)
    
    // Add to images array for immediate preview
    state.images.push(imageObj)

    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('upload_path', mergedConfig.context) // Backend expects 'upload_path'
      formData.append('context', mergedConfig.context) // Keep for metadata
      if (mergedConfig.entityId) {
        formData.append('entityId', mergedConfig.entityId.toString())
      }

      console.log(`🖼️ Uploading image for ${mergedConfig.context}:`, {
        fileName: file.name,
        size: file.size,
        type: file.type,
        entityId: mergedConfig.entityId
      })

      const response = await api.post<{
        success: boolean
        data?: {
          cdn_url: string
          original_url?: string
          image_id?: string
          metadata?: any
        }
        error?: string
      }>('/upload/image', formData)

      console.log('🔍 Upload API Response:', JSON.stringify(response, null, 2))

      if (response.success && response.data?.cdn_url) {
        // Update the image object with CDN URL
        const updatedImage: UploadedImage = {
          ...imageObj,
          url: response.data.cdn_url, // Use CDN URL as primary
          cdnUrl: response.data.cdn_url,
          id: response.data.image_id || imageObj.id,
          status: 'success'
        }

        // Update in state
        const index = state.images.findIndex(img => img.id === imageObj.id)
        if (index !== -1) {
          state.images[index] = updatedImage
        }

        notifications.showSuccess(`Image uploaded successfully: ${file.name}`)
        console.log('✅ Image upload successful:', response.data.cdn_url)
        
        return updatedImage
      } else {
        throw new Error(response.error || 'No CDN URL returned from server')
      }

    } catch (error) {
      console.error('❌ Image upload failed:', error)
      
      // Update image status to error
      const index = state.images.findIndex(img => img.id === imageObj.id)
      if (index !== -1) {
        state.images[index] = {
          ...imageObj,
          status: 'error',
          error: error instanceof Error ? error.message : 'Upload failed'
        }
      }

      const errorMessage = error instanceof Error ? error.message : 'Upload failed'
      notifications.showError(`Failed to upload ${file.name}: ${errorMessage}`)
      throw error
    }
  }

  // Upload multiple images
  const uploadImages = async (files: File[] | FileList): Promise<void> => {
    const fileArray = Array.from(files)
    
    if (fileArray.length === 0) return

    state.isUploading = true
    state.error = null
    state.uploadProgress = 0

    try {
      const uploadPromises = fileArray.map((file, index) => 
        uploadSingleImage(file).then(() => {
          // Update progress
          state.uploadProgress = Math.round(((index + 1) / fileArray.length) * 100)
        })
      )

      await Promise.allSettled(uploadPromises)
      
      const successful = fileArray.length - failedImages.value.length
      if (successful > 0) {
        notifications.showSuccess(`Successfully uploaded ${successful} of ${fileArray.length} images`)
      }

    } catch (error) {
      console.error('❌ Batch upload failed:', error)
      state.error = error instanceof Error ? error.message : 'Batch upload failed'
    } finally {
      state.isUploading = false
      state.uploadProgress = 100
    }
  }

  // Remove image
  const removeImage = (imageId: string): void => {
    const index = state.images.findIndex(img => img.id === imageId)
    if (index !== -1) {
      const image = state.images[index]
      
      // Revoke object URL to prevent memory leaks
      if (image.url.startsWith('blob:')) {
        URL.revokeObjectURL(image.url)
      }
      
      state.images.splice(index, 1)
      notifications.showInfo('Image removed')
    }
  }

  // Clear all images
  const clearImages = (): void => {
    // Revoke all blob URLs
    state.images.forEach(image => {
      if (image.url.startsWith('blob:')) {
        URL.revokeObjectURL(image.url)
      }
    })
    
    state.images = []
    state.error = null
    state.uploadProgress = 0
    notifications.showInfo('All images cleared')
  }

  // Retry failed uploads
  const retryFailedUploads = async (): Promise<void> => {
    const failedImages = state.images.filter(img => img.status === 'error')
    if (failedImages.length === 0) return

    // Note: We can't retry with the original File object since it's lost
    // This would require storing the File objects, which isn't memory efficient
    notifications.showWarning('Please re-select failed images to retry upload')
  }

  // Drag and drop handlers
  const handleDragOver = (event: DragEvent): void => {
    event.preventDefault()
    state.dragOver = true
  }

  const handleDragLeave = (event: DragEvent): void => {
    event.preventDefault()
    state.dragOver = false
  }

  const handleDrop = async (event: DragEvent): Promise<void> => {
    event.preventDefault()
    state.dragOver = false

    const files = event.dataTransfer?.files
    if (files && files.length > 0) {
      await uploadImages(files)
    }
  }

  // File input handler
  const handleFileInput = async (event: Event): Promise<void> => {
    const target = event.target as HTMLInputElement
    const files = target.files
    
    if (files && files.length > 0) {
      await uploadImages(files)
      // Clear the input so the same file can be selected again
      target.value = ''
    }
  }

  // Get images for submission (only successful ones)
  const getImagesForSubmission = (): UploadedImage[] => {
    return successfulImages.value.map(image => ({
      ...image,
      url: image.cdnUrl || image.url // Ensure we use CDN URL
    }))
  }

  // Initialize with existing images
  const initializeImages = (existingImages: UploadedImage[]): void => {
    state.images = existingImages.map(img => ({
      ...img,
      status: img.status || 'success'
    }))
  }

  return {
    // State
    state: readonly(state),
    
    // Computed
    canUploadMore,
    hasImages,
    uploadingImages,
    successfulImages,
    failedImages,
    
    // Methods
    uploadImages,
    uploadSingleImage,
    removeImage,
    clearImages,
    retryFailedUploads,
    validateFile,
    
    // Event handlers
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileInput,
    
    // Utilities
    getImagesForSubmission,
    initializeImages
  }
}