<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay modal-open fixed inset-0 z-[1100] bg-white dark:bg-gray-900 md:bg-black md:bg-opacity-50 md:flex md:items-center md:justify-center md:p-4 mobile-modal-overlay">
      <div class="modal-container relative z-[1150] bg-white dark:bg-gray-800 md:shadow-lg md:rounded-xl md:max-w-3xl md:max-h-[90vh] md:w-full flex flex-col mobile-modal-container">
        <!-- Header -->
        <div class="modal-mobile-header md:px-6 md:py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Import Spine Chart Data
          </h3>
          <button 
            @click="$emit('cancel')"
            class="md:hidden mobile-touch-target p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg"
            aria-label="Close modal"
          >
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <!-- Content -->
        <div class="modal-mobile-content p-3 sm:p-4 md:px-6 pb-6 flex-1 overflow-y-auto">
          <!-- File Upload Section -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select CSV File
            </label>
            <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-md">
              <div class="space-y-1 text-center">
                <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 dark:text-gray-500 mb-3"></i>
                <div class="flex text-sm text-gray-600 dark:text-gray-400">
                  <label for="file-upload" class="relative cursor-pointer bg-white dark:bg-gray-800 rounded-md font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                    <span>Upload a CSV file</span>
                    <input id="file-upload" name="file-upload" type="file" accept=".csv" class="sr-only" @change="handleFileSelect" />
                  </label>
                  <p class="pl-1">or drag and drop</p>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  CSV files with Draw Weight, Arrow Length, Recommended Spine, Arrow Size, Speed columns
                </p>
              </div>
            </div>
            <div v-if="selectedFile" class="mt-3 text-sm text-gray-600 dark:text-gray-400">
              Selected: {{ selectedFile.name }}
            </div>
          </div>

          <!-- Import Options -->
          <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Import Options</h4>
            <div class="space-y-3">
              <label class="flex items-center">
                <input type="checkbox" v-model="skipDuplicates" class="form-checkbox h-4 w-4 text-blue-600" />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Skip duplicate entries (recommended)</span>
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="validateData" class="form-checkbox h-4 w-4 text-blue-600" />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Validate data format</span>
              </label>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="previewData.length > 0" class="mb-6">
            <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
              Preview ({{ previewData.length }} entries {{ duplicateCount > 0 ? `, ${duplicateCount} duplicates` : '' }})
            </h4>
            <div class="max-h-64 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-lg">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
                <thead class="bg-gray-50 dark:bg-gray-700 sticky top-0">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Draw Weight</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Arrow Length</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Spine</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Size</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Speed</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-600">
                  <tr v-for="(entry, index) in previewData.slice(0, 10)" :key="index" 
                      :class="entry.isDuplicate ? 'bg-yellow-50 dark:bg-yellow-900/20' : ''">
                    <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{{ entry.draw_weight_range_lbs }}</td>
                    <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{{ entry.arrow_length_in }}</td>
                    <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{{ entry.spine }}</td>
                    <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{{ entry.arrow_size || '-' }}</td>
                    <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{{ entry.speed || '-' }}</td>
                    <td class="px-3 py-2 whitespace-nowrap text-sm">
                      <span v-if="entry.isDuplicate" class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full">
                        Duplicate
                      </span>
                      <span v-else class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                        New
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="previewData.length > 10" class="p-2 text-center text-sm text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-600">
                ... and {{ previewData.length - 10 }} more entries
              </div>
            </div>
          </div>

          <!-- Error Messages -->
          <div v-if="errors.length > 0" class="mb-6">
            <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
              <div class="flex">
                <i class="fas fa-exclamation-circle text-red-400 mr-2 mt-0.5"></i>
                <div>
                  <h4 class="text-sm font-medium text-red-800 dark:text-red-400 mb-2">Import Errors:</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 list-disc list-inside">
                    <li v-for="error in errors" :key="error">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-600">
            <button
              type="button"
              @click="$emit('cancel')"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="importData"
              :disabled="!canImport"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Import {{ importCount }} Entries
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
interface SpineGridEntry {
  draw_weight_range_lbs: string;
  arrow_length_in: number;
  spine: string;
  arrow_size?: string;
  speed?: number;
  isDuplicate?: boolean;
}

interface Props {
  show: boolean;
  bowType: string;
  manufacturer: string;
  existingData: SpineGridEntry[];
}

interface Emits {
  (e: 'import', data: SpineGridEntry[]): void;
  (e: 'cancel'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// State
const selectedFile = ref<File | null>(null);
const previewData = ref<SpineGridEntry[]>([]);
const skipDuplicates = ref(true);
const validateData = ref(true);
const errors = ref<string[]>([]);

// Computed
const duplicateCount = computed(() => previewData.value.filter(entry => entry.isDuplicate).length);
const importCount = computed(() => {
  if (skipDuplicates.value) {
    return previewData.value.filter(entry => !entry.isDuplicate).length;
  }
  return previewData.value.length;
});
const canImport = computed(() => previewData.value.length > 0 && errors.value.length === 0 && importCount.value > 0);

// Methods
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    selectedFile.value = file;
    parseCSV(file);
  }
};

const parseCSV = async (file: File) => {
  try {
    errors.value = [];
    previewData.value = [];
    
    const text = await file.text();
    const lines = text.split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
      errors.value.push('File is empty');
      return;
    }

    // Parse header
    const headerLine = lines[0];
    const expectedHeaders = ['Draw Weight (lbs)', 'Arrow Length (in)', 'Recommended Spine', 'Arrow Size', 'Speed (fps)'];
    const headers = parseCSVLine(headerLine);
    
    // Validate headers
    const headerMap: { [key: string]: number } = {};
    expectedHeaders.forEach(expectedHeader => {
      const index = headers.findIndex(header => 
        header.toLowerCase().includes(expectedHeader.toLowerCase().split(' ')[0]) ||
        expectedHeader.toLowerCase().includes(header.toLowerCase())
      );
      if (index !== -1) {
        headerMap[expectedHeader] = index;
      }
    });

    // Check required headers
    const requiredHeaders = ['Draw Weight (lbs)', 'Arrow Length (in)', 'Recommended Spine'];
    const missingHeaders = requiredHeaders.filter(header => !(header in headerMap));
    if (missingHeaders.length > 0) {
      errors.value.push(`Missing required columns: ${missingHeaders.join(', ')}`);
      return;
    }

    // Parse data rows
    const parsedData: SpineGridEntry[] = [];
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      try {
        const values = parseCSVLine(line);
        
        if (values.length < Math.max(...Object.values(headerMap)) + 1) {
          if (validateData.value) {
            errors.value.push(`Row ${i + 1}: Insufficient columns`);
            continue;
          }
        }

        const entry: SpineGridEntry = {
          draw_weight_range_lbs: values[headerMap['Draw Weight (lbs)']] || '',
          arrow_length_in: parseFloat(values[headerMap['Arrow Length (in)']] || '0') || 0,
          spine: values[headerMap['Recommended Spine']] || '',
          arrow_size: values[headerMap['Arrow Size']] || undefined,
          speed: values[headerMap['Speed (fps)']] ? parseFloat(values[headerMap['Speed (fps)']]) : undefined
        };

        // Validate required fields
        if (validateData.value) {
          if (!entry.draw_weight_range_lbs) {
            errors.value.push(`Row ${i + 1}: Missing draw weight`);
            continue;
          }
          if (!entry.arrow_length_in || entry.arrow_length_in <= 0) {
            errors.value.push(`Row ${i + 1}: Invalid arrow length`);
            continue;
          }
          if (!entry.spine) {
            errors.value.push(`Row ${i + 1}: Missing spine value`);
            continue;
          }
        }

        // Check for duplicates
        const isDuplicate = props.existingData.some(existing => 
          existing.draw_weight_range_lbs === entry.draw_weight_range_lbs &&
          existing.arrow_length_in === entry.arrow_length_in &&
          existing.spine === entry.spine
        );

        entry.isDuplicate = isDuplicate;
        parsedData.push(entry);

      } catch (err) {
        if (validateData.value) {
          errors.value.push(`Row ${i + 1}: Failed to parse - ${err}`);
        }
      }
    }

    previewData.value = parsedData;

  } catch (err) {
    errors.value.push(`Failed to read file: ${err}`);
  }
};

const parseCSVLine = (line: string): string[] => {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  
  result.push(current.trim());
  return result.map(val => val.replace(/^"(.*)"$/, '$1')); // Remove surrounding quotes
};

const importData = () => {
  let dataToImport = previewData.value;
  
  if (skipDuplicates.value) {
    dataToImport = dataToImport.filter(entry => !entry.isDuplicate);
  }

  // Remove the isDuplicate flag before emitting
  const cleanData = dataToImport.map(entry => {
    const { isDuplicate, ...cleanEntry } = entry;
    return cleanEntry;
  });

  emit('import', cleanData);
};

// Reset when modal closes
watch(() => props.show, (newShow) => {
  if (!newShow) {
    selectedFile.value = null;
    previewData.value = [];
    errors.value = [];
  }
});
</script>