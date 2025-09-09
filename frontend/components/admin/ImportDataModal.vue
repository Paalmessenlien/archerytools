<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-black bg-opacity-50" @click="cancel"></div>
      
      <!-- Modal -->
      <div class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-xl rounded-lg">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-file-import mr-2"></i>
            Import Spine Chart Data
          </h3>
          <CustomButton
            @click="cancel"
            variant="text"
            size="small"
            class="text-gray-400 hover:text-gray-600"
          >
            <i class="fas fa-times"></i>
          </CustomButton>
        </div>

        <!-- Import Options -->
        <div class="space-y-6">
          <!-- Import Method -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Import Method
            </label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                @click="importMethod = 'file'"
                :class="[
                  'p-4 border-2 rounded-lg text-left transition-colors',
                  importMethod === 'file'
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                ]"
              >
                <div class="flex items-center">
                  <i class="fas fa-file-upload text-blue-600 dark:text-blue-400 mr-3"></i>
                  <div>
                    <div class="font-medium text-gray-900 dark:text-gray-100">Upload File</div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">CSV, Excel, or JSON</div>
                  </div>
                </div>
              </button>
              
              <button
                @click="importMethod = 'paste'"
                :class="[
                  'p-4 border-2 rounded-lg text-left transition-colors',
                  importMethod === 'paste'
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                ]"
              >
                <div class="flex items-center">
                  <i class="fas fa-clipboard text-blue-600 dark:text-blue-400 mr-3"></i>
                  <div>
                    <div class="font-medium text-gray-900 dark:text-gray-100">Paste Data</div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">CSV or JSON text</div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- File Upload -->
          <div v-if="importMethod === 'file'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select File
              </label>
              <div 
                @drop="handleFileDrop"
                @dragover.prevent
                @dragenter.prevent
                class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept=".csv,.xlsx,.xls,.json"
                  @change="handleFileSelect"
                  class="hidden"
                >
                <div v-if="!selectedFile">
                  <i class="fas fa-cloud-upload-alt text-gray-400 text-3xl mb-3"></i>
                  <p class="text-gray-600 dark:text-gray-400 mb-2">
                    Drop your file here or <button @click="$refs.fileInput.click()" class="text-blue-600 dark:text-blue-400 hover:underline">browse</button>
                  </p>
                  <p class="text-sm text-gray-500 dark:text-gray-500">
                    Supports CSV, Excel (.xlsx, .xls), and JSON files
                  </p>
                </div>
                <div v-else class="flex items-center justify-center space-x-3">
                  <i class="fas fa-file text-green-600 dark:text-green-400 text-2xl"></i>
                  <div>
                    <p class="font-medium text-gray-900 dark:text-gray-100">{{ selectedFile.name }}</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">{{ formatFileSize(selectedFile.size) }}</p>
                  </div>
                  <button @click="clearFile" class="text-red-600 dark:text-red-400 hover:text-red-700">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Paste Data -->
          <div v-if="importMethod === 'paste'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Paste Data
              </label>
              <textarea
                v-model="pasteData"
                rows="8"
                placeholder="Paste your CSV or JSON data here..."
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100 font-mono text-sm"
              ></textarea>
              <div class="flex justify-between mt-2">
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  Expected format: CSV with headers or JSON array
                </p>
                <button 
                  v-if="pasteData"
                  @click="pasteData = ''"
                  class="text-xs text-red-600 dark:text-red-400 hover:underline"
                >
                  Clear
                </button>
              </div>
            </div>
          </div>

          <!-- Data Format Guide -->
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h4 class="flex items-center text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
              <i class="fas fa-info-circle mr-2"></i>
              Expected Data Format
            </h4>
            <div class="space-y-2 text-sm text-blue-700 dark:text-blue-300">
              <p><strong>CSV Format:</strong></p>
              <code class="block bg-blue-100 dark:bg-blue-800 p-2 rounded text-xs">
                Draw Weight (lbs),Arrow Length (in),Recommended Spine,Arrow Size<br>
                "40-50",28,"400","2314"<br>
                "45",30,"350-400","2413"
              </code>
              <p class="mt-3"><strong>JSON Format:</strong></p>
              <code class="block bg-blue-100 dark:bg-blue-800 p-2 rounded text-xs">
                [{"draw_weight_range_lbs":"40-50","arrow_length_in":28,"spine":"400","arrow_size":"2314"}]
              </code>
            </div>
          </div>

          <!-- Import Options -->
          <div class="space-y-3">
            <div class="flex items-center">
              <input
                id="replace-data"
                v-model="replaceExistingData"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
              >
              <label for="replace-data" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Replace all existing data (instead of appending)
              </label>
            </div>
            <div class="flex items-center">
              <input
                id="validate-data"
                v-model="validateData"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
              >
              <label for="validate-data" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Validate data before import (recommended)
              </label>
            </div>
          </div>

          <!-- Preview -->
          <div v-if="previewData.length > 0" class="space-y-3">
            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">
              Preview (first 5 rows)
            </h4>
            <div class="overflow-x-auto border border-gray-200 dark:border-gray-600 rounded-lg">
              <table class="min-w-full text-sm">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-3 py-2 text-left font-medium text-gray-700 dark:text-gray-300">Draw Weight</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-700 dark:text-gray-300">Length</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-700 dark:text-gray-300">Spine</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-700 dark:text-gray-300">Size</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in previewData.slice(0, 5)" :key="index" class="border-t border-gray-200 dark:border-gray-600">
                    <td class="px-3 py-2 text-gray-900 dark:text-gray-100">{{ row.draw_weight_range_lbs }}</td>
                    <td class="px-3 py-2 text-gray-900 dark:text-gray-100">{{ row.arrow_length_in }}"</td>
                    <td class="px-3 py-2 text-gray-900 dark:text-gray-100">{{ row.spine }}</td>
                    <td class="px-3 py-2 text-gray-900 dark:text-gray-100">{{ row.arrow_size || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              Found {{ previewData.length }} valid entries
              <span v-if="invalidRows.length > 0" class="text-red-600 dark:text-red-400">
                ({{ invalidRows.length }} invalid rows will be skipped)
              </span>
            </p>
          </div>

          <!-- Validation Errors -->
          <div v-if="validationErrors.length > 0" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <h4 class="flex items-center text-sm font-medium text-red-800 dark:text-red-200 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Validation Errors
            </h4>
            <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
              <li v-for="error in validationErrors.slice(0, 10)" :key="error">• {{ error }}</li>
              <li v-if="validationErrors.length > 10" class="font-medium">
                ... and {{ validationErrors.length - 10 }} more errors
              </li>
            </ul>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-600 mt-6">
          <CustomButton
            @click="cancel"
            type="button"
            variant="outlined"
            class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="processImport"
            :disabled="!canImport || processing"
            variant="filled"
            class="bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            <i v-if="processing" class="fas fa-spinner fa-spin mr-2"></i>
            <i v-else class="fas fa-file-import mr-2"></i>
            {{ processing ? 'Processing...' : 'Import Data' }}
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface SpineGridEntry {
  draw_weight_range_lbs: string | number
  arrow_length_in: number
  spine: string
  arrow_size?: string
}

interface Props {
  show: boolean
  bowType?: string
  manufacturer?: string
}

interface Emits {
  import: [data: SpineGridEntry[]]
  cancel: []
}

const props = withDefaults(defineProps<Props>(), {
  bowType: '',
  manufacturer: ''
})

const emit = defineEmits<Emits>()

// State
const importMethod = ref<'file' | 'paste'>('file')
const selectedFile = ref<File | null>(null)
const pasteData = ref('')
const previewData = ref<SpineGridEntry[]>([])
const invalidRows = ref<string[]>([])
const validationErrors = ref<string[]>([])
const processing = ref(false)
const replaceExistingData = ref(false)
const validateData = ref(true)

// Computed
const canImport = computed(() => {
  if (importMethod.value === 'file') {
    return selectedFile.value && previewData.value.length > 0
  }
  return pasteData.value.trim().length > 0 && previewData.value.length > 0
})

// File handling
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    processFile(target.files[0])
  }
}

const handleFileDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
    processFile(event.dataTransfer.files[0])
  }
}

const clearFile = () => {
  selectedFile.value = null
  previewData.value = []
  invalidRows.value = []
  validationErrors.value = []
}

const processFile = async (file: File) => {
  try {
    const text = await file.text()
    
    if (file.name.endsWith('.json')) {
      processJsonData(text)
    } else if (file.name.endsWith('.csv')) {
      processCsvData(text)
    } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
      // For Excel files, you'd need a library like xlsx
      validationErrors.value = ['Excel files are not yet supported. Please export as CSV.']
    }
  } catch (error) {
    validationErrors.value = [`Failed to read file: ${error instanceof Error ? error.message : 'Unknown error'}`]
  }
}

// Data processing
const processCsvData = (csvText: string) => {
  try {
    const lines = csvText.trim().split('\n')
    if (lines.length < 2) {
      validationErrors.value = ['CSV file must have at least a header row and one data row']
      return
    }

    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
    const dataRows = lines.slice(1)
    
    const data: SpineGridEntry[] = []
    const errors: string[] = []
    const invalid: string[] = []

    dataRows.forEach((line, index) => {
      try {
        const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
        
        const entry: SpineGridEntry = {
          draw_weight_range_lbs: values[0] || '',
          arrow_length_in: parseFloat(values[1]) || 0,
          spine: values[2] || '',
          arrow_size: values[3] || ''
        }

        if (validateData.value) {
          const entryErrors = validateEntry(entry, index + 2)
          if (entryErrors.length > 0) {
            errors.push(...entryErrors)
            invalid.push(`Row ${index + 2}: ${line}`)
            return
          }
        }

        data.push(entry)
      } catch (error) {
        invalid.push(`Row ${index + 2}: ${line}`)
        errors.push(`Row ${index + 2}: Failed to parse data`)
      }
    })

    previewData.value = data
    invalidRows.value = invalid
    validationErrors.value = errors
  } catch (error) {
    validationErrors.value = [`Failed to parse CSV: ${error instanceof Error ? error.message : 'Unknown error'}`]
  }
}

const processJsonData = (jsonText: string) => {
  try {
    const jsonData = JSON.parse(jsonText)
    
    if (!Array.isArray(jsonData)) {
      validationErrors.value = ['JSON data must be an array of spine entries']
      return
    }

    const data: SpineGridEntry[] = []
    const errors: string[] = []
    const invalid: string[] = []

    jsonData.forEach((item, index) => {
      try {
        const entry: SpineGridEntry = {
          draw_weight_range_lbs: item.draw_weight_range_lbs || '',
          arrow_length_in: parseFloat(item.arrow_length_in) || 0,
          spine: item.spine || '',
          arrow_size: item.arrow_size || ''
        }

        if (validateData.value) {
          const entryErrors = validateEntry(entry, index + 1)
          if (entryErrors.length > 0) {
            errors.push(...entryErrors)
            invalid.push(`Entry ${index + 1}: ${JSON.stringify(item)}`)
            return
          }
        }

        data.push(entry)
      } catch (error) {
        invalid.push(`Entry ${index + 1}: ${JSON.stringify(item)}`)
        errors.push(`Entry ${index + 1}: Failed to parse data`)
      }
    })

    previewData.value = data
    invalidRows.value = invalid
    validationErrors.value = errors
  } catch (error) {
    validationErrors.value = [`Failed to parse JSON: ${error instanceof Error ? error.message : 'Unknown error'}`]
  }
}

const validateEntry = (entry: SpineGridEntry, rowNumber: number): string[] => {
  const errors: string[] = []

  // Validate draw weight
  if (!entry.draw_weight_range_lbs) {
    errors.push(`Row ${rowNumber}: Draw weight is required`)
  } else {
    const weightStr = entry.draw_weight_range_lbs.toString()
    if (!/^(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)$/.test(weightStr.trim())) {
      errors.push(`Row ${rowNumber}: Invalid draw weight format. Use a number (e.g., 45) or range (e.g., 40-50)`)
    }
  }

  // Validate arrow length
  if (!entry.arrow_length_in || isNaN(entry.arrow_length_in)) {
    errors.push(`Row ${rowNumber}: Arrow length must be a valid number`)
  } else if (entry.arrow_length_in < 20 || entry.arrow_length_in > 36) {
    errors.push(`Row ${rowNumber}: Arrow length must be between 20 and 36 inches`)
  }

  // Validate spine
  if (!entry.spine) {
    errors.push(`Row ${rowNumber}: Spine value is required`)
  }

  return errors
}

// Process paste data
watch(() => pasteData.value, (newData) => {
  if (!newData.trim()) {
    previewData.value = []
    invalidRows.value = []
    validationErrors.value = []
    return
  }

  // Try to detect format and process
  if (newData.trim().startsWith('[') || newData.trim().startsWith('{')) {
    processJsonData(newData)
  } else {
    processCsvData(newData)
  }
})

// Actions
const processImport = async () => {
  if (!canImport.value) return

  processing.value = true
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate processing
    emit('import', previewData.value)
  } finally {
    processing.value = false
  }
}

const cancel = () => {
  // Reset state
  importMethod.value = 'file'
  selectedFile.value = null
  pasteData.value = ''
  previewData.value = []
  invalidRows.value = []
  validationErrors.value = []
  processing.value = false
  replaceExistingData.value = false
  validateData.value = true
  
  emit('cancel')
}

// Utilities
const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`
}
</script>

<style scoped>
/* Modal backdrop styling */
.fixed.inset-0 {
  backdrop-filter: blur(2px);
}

/* Drag and drop styling */
.border-dashed:hover {
  @apply border-blue-400 dark:border-blue-500;
}
</style>