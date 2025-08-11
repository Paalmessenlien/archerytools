<template>
  <div>
    <!-- Search and Filter Controls -->
    <div class="mb-6 flex flex-col sm:flex-row gap-4">
      <div class="flex-1">
        <div class="relative">
          <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search arrows by manufacturer, model, or description..."
            class="form-input w-full pl-10"
            @input="debouncedSearch"
          />
        </div>
      </div>
      
      <div class="flex gap-2">
        <select v-model="selectedManufacturer" @change="loadArrows" class="form-select">
          <option value="">All Manufacturers</option>
          <option v-for="manufacturer in manufacturers" :key="manufacturer" :value="manufacturer">
            {{ manufacturer }}
          </option>
        </select>
        
        <CustomButton
          @click="showColumnSettings = true"
          variant="outlined"
          class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700 whitespace-nowrap"
        >
          <i class="fas fa-columns mr-2"></i>
          Columns
        </CustomButton>
        
        <CustomButton
          @click="openCreateModal"
          variant="filled"
          class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800 whitespace-nowrap"
        >
          <i class="fas fa-plus mr-2"></i>
          Add Arrow
        </CustomButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-2xl text-gray-400 mb-2"></i>
      <p class="text-gray-500 dark:text-gray-400">Loading arrows...</p>
    </div>

    <!-- Arrows Table -->
    <div v-else-if="arrows.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th v-if="visibleColumns.arrow" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Arrow
              </th>
              <th v-if="visibleColumns.material" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Material
              </th>
              <th v-if="visibleColumns.type" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Type
              </th>
              <th v-if="visibleColumns.spineRange" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Spine Range
              </th>
              <th v-if="visibleColumns.lengthStatus" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Length Status
              </th>
              <th v-if="visibleColumns.updated" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Updated
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="arrow in arrows" :key="arrow.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td v-if="visibleColumns.arrow" class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <img 
                    v-if="arrow.primary_image_url" 
                    :src="arrow.primary_image_url" 
                    :alt="arrow.model_name"
                    class="h-10 w-10 rounded object-cover mr-3"
                    @error="handleImageError"
                  />
                  <div class="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded mr-3 flex items-center justify-center" v-else>
                    <i class="fas fa-image text-gray-400"></i>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ arrow.model_name }}
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                      {{ arrow.manufacturer }}
                    </div>
                  </div>
                </div>
              </td>
              <td v-if="visibleColumns.material" class="px-6 py-4 whitespace-nowrap">
                <span v-if="arrow.material" :class="getMaterialBadgeClass(arrow.material)" 
                      class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                  {{ arrow.material }}
                </span>
                <span v-else class="text-gray-400 text-sm">N/A</span>
              </td>
              <td v-if="visibleColumns.type" class="px-6 py-4 whitespace-nowrap">
                <span v-if="arrow.arrow_type" :class="getTypeBadgeClass(arrow.arrow_type)" 
                      class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                  {{ formatArrowType(arrow.arrow_type) }}
                </span>
                <span v-else class="text-gray-400 text-sm">N/A</span>
              </td>
              <td v-if="visibleColumns.spineRange" class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                <div v-if="arrow.spine_count > 0">
                  <span class="font-medium">{{ arrow.min_spine }}-{{ arrow.max_spine }}</span>
                  <span class="text-gray-500 dark:text-gray-400 ml-1">({{ arrow.spine_count }} spines)</span>
                </div>
                <span v-else class="text-gray-400">No spines</span>
              </td>
              <td v-if="visibleColumns.lengthStatus" class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center">
                  <span :class="getLengthStatusBadgeClass(arrow.length_status)" 
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ arrow.length_status || 'Unknown' }}
                  </span>
                  <span v-if="arrow.length_info" class="text-gray-500 dark:text-gray-400 ml-2 text-xs">
                    {{ arrow.length_info }}
                  </span>
                </div>
              </td>
              <td v-if="visibleColumns.updated" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(arrow.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <CustomButton
                  @click="editArrow(arrow)"
                  variant="outlined"
                  size="small"
                  class="text-indigo-600 border-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
                >
                  <i class="fas fa-edit mr-1"></i>
                  Edit
                </CustomButton>
                <CustomButton
                  @click="confirmDelete(arrow)"
                  variant="outlined"
                  size="small"
                  class="text-red-600 border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <i class="fas fa-trash mr-1"></i>
                  Delete
                </CustomButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.pages > 1" class="bg-gray-50 dark:bg-gray-700 px-6 py-3 border-t border-gray-200 dark:border-gray-600">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ ((pagination.page - 1) * pagination.per_page) + 1 }} to 
            {{ Math.min(pagination.page * pagination.per_page, pagination.total) }} of 
            {{ pagination.total }} arrows
          </div>
          <div class="flex space-x-2">
            <CustomButton
              @click="changePage(pagination.page - 1)"
              :disabled="pagination.page <= 1"
              variant="outlined"
              size="small"
            >
              <i class="fas fa-chevron-left"></i>
            </CustomButton>
            
            <div class="flex space-x-1">
              <CustomButton
                v-for="page in getPageNumbers()"
                :key="page"
                @click="changePage(page)"
                :class="page === pagination.page ? 'bg-indigo-600 text-white' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300'"
                variant="outlined"
                size="small"
                class="min-w-[2.5rem]"
              >
                {{ page }}
              </CustomButton>
            </div>
            
            <CustomButton
              @click="changePage(pagination.page + 1)"
              :disabled="pagination.page >= pagination.pages"
              variant="outlined"
              size="small"
            >
              <i class="fas fa-chevron-right"></i>
            </CustomButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
      <i class="fas fa-search text-4xl text-gray-400 mb-4"></i>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No arrows found</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-4">
        {{ searchQuery || selectedManufacturer ? 'Try adjusting your search criteria.' : 'Get started by adding your first arrow.' }}
      </p>
      <CustomButton
        @click="openCreateModal"
        variant="filled"
        class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800"
      >
        <i class="fas fa-plus mr-2"></i>
        Add First Arrow
      </CustomButton>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message.show" class="fixed top-4 right-4 z-50 transition-all duration-300">
      <div 
        :class="[
          'p-4 rounded-lg shadow-lg max-w-sm',
          message.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i :class="message.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'" class="mr-2"></i>
            <span class="text-sm">{{ message.text }}</span>
          </div>
          <button @click="message.show = false" class="ml-4 opacity-70 hover:opacity-100">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Column Settings Modal -->
    <div v-if="showColumnSettings" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-columns mr-2 text-indigo-600"></i>
            Column Settings
          </h3>
          <button @click="showColumnSettings = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <p class="text-gray-600 dark:text-gray-400 text-sm mb-4">
          Choose which columns to display in the arrows table. Changes are saved automatically.
        </p>

        <div class="space-y-3">
          <div v-for="column in columnOptions" :key="column.key" class="flex items-center justify-between">
            <div class="flex items-center">
              <i :class="column.icon" class="text-gray-500 dark:text-gray-400 mr-3 w-4"></i>
              <div>
                <div class="font-medium text-gray-900 dark:text-gray-100">{{ column.label }}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ column.description }}</div>
              </div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                class="sr-only peer"
                v-model="visibleColumns[column.key]"
                @change="saveColumnSettings"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 dark:peer-focus:ring-indigo-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-600"></div>
            </label>
          </div>
        </div>

        <div class="mt-6 flex justify-between">
          <CustomButton
            @click="resetColumns"
            variant="outlined"
            size="small"
            class="text-gray-600 border-gray-300 dark:text-gray-300 dark:border-gray-600"
          >
            <i class="fas fa-undo mr-2"></i>
            Reset to Default
          </CustomButton>

          <div class="space-x-2">
            <CustomButton
              @click="showColumnSettings = false"
              variant="outlined"
              class="text-gray-700 dark:text-gray-200"
            >
              Close
            </CustomButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Arrow {
  id: number;
  manufacturer: string;
  model_name: string;
  material?: string;
  arrow_type?: string;
  description?: string;
  primary_image_url?: string;
  spine_count: number;
  min_spine: number;
  max_spine: number;
  created_at: string;
  length_status?: string;
  length_info?: string;
}

interface Pagination {
  page: number;
  per_page: number;
  total: number;
  pages: number;
}

interface Emits {
  (e: 'edit', arrow: Arrow): void;
  (e: 'create'): void;
  (e: 'delete', arrow: Arrow): void;
}

const emit = defineEmits<Emits>();

// Composables
const api = useApi();

// State
const arrows = ref<Arrow[]>([]);
const manufacturers = ref<string[]>([]);
const isLoading = ref(false);
const searchQuery = ref('');
const selectedManufacturer = ref('');
const showColumnSettings = ref(false);

const pagination = ref<Pagination>({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
});

const message = ref({
  show: false,
  text: '',
  type: 'success' as 'success' | 'error'
});

// Column management
const defaultColumns = {
  arrow: true,
  material: true,
  type: true,
  spineRange: true,
  lengthStatus: true,
  updated: false
};

const visibleColumns = ref({ ...defaultColumns });

const columnOptions = [
  {
    key: 'arrow',
    label: 'Arrow Info',
    description: 'Name, manufacturer and image',
    icon: 'fas fa-bow-arrow'
  },
  {
    key: 'material',
    label: 'Material',
    description: 'Arrow shaft material',
    icon: 'fas fa-layer-group'
  },
  {
    key: 'type',
    label: 'Type',
    description: 'Hunting, target, 3D, etc.',
    icon: 'fas fa-tag'
  },
  {
    key: 'spineRange',
    label: 'Spine Range',
    description: 'Min-max spine with count',
    icon: 'fas fa-ruler-horizontal'
  },
  {
    key: 'lengthStatus',
    label: 'Length Status',
    description: 'Completeness of length data',
    icon: 'fas fa-check-circle'
  },
  {
    key: 'updated',
    label: 'Updated Date',
    description: 'When arrow was last modified',
    icon: 'fas fa-calendar'
  }
];

// Debounced search
let searchTimeout: NodeJS.Timeout;
const debouncedSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    pagination.value.page = 1;
    loadArrows();
  }, 500);
};

// Load arrows using the same pattern as database page
const loadArrows = async () => {
  try {
    isLoading.value = true;
    
    // Build filter object like database page does
    const searchFilters = {
      page: pagination.value.page,
      per_page: pagination.value.per_page
    };
    
    // Add search filter if provided
    if (searchQuery.value && searchQuery.value.trim()) {
      searchFilters.search = searchQuery.value.trim();
    }
    
    // Add manufacturer filter if provided
    if (selectedManufacturer.value) {
      searchFilters.manufacturer = selectedManufacturer.value;
    }

    // Use the same API method as database page
    const data = await api.getArrows(searchFilters);
    arrows.value = data.arrows;
    
    // Update pagination from response
    pagination.value = {
      page: data.page,
      per_page: data.per_page,
      total: data.total,
      pages: data.total_pages
    };
  } catch (error) {
    console.error('Error loading arrows:', error);
    showMessage('Failed to load arrows', 'error');
  } finally {
    isLoading.value = false;
  }
};

// Load manufacturers for filter using same pattern as database page
const loadManufacturers = async () => {
  try {
    const data = await api.getManufacturers();
    manufacturers.value = data.map((m: any) => m.manufacturer) || [];
  } catch (error) {
    console.error('Error loading manufacturers:', error);
  }
};

// Pagination
const changePage = (page: number) => {
  if (page >= 1 && page <= pagination.value.pages) {
    pagination.value.page = page;
    loadArrows();
  }
};

const getPageNumbers = () => {
  const current = pagination.value.page;
  const total = pagination.value.pages;
  const delta = 2;
  
  const range = [];
  const rangeWithDots = [];
  
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i);
  }
  
  if (current - delta > 2) {
    rangeWithDots.push(1, '...');
  } else {
    rangeWithDots.push(1);
  }
  
  rangeWithDots.push(...range);
  
  if (current + delta < total - 1) {
    rangeWithDots.push('...', total);
  } else {
    if (total > 1) rangeWithDots.push(total);
  }
  
  return rangeWithDots.filter(item => item !== '...' || rangeWithDots.indexOf(item) !== rangeWithDots.lastIndexOf(item));
};

// Actions
const editArrow = async (arrow: Arrow) => {
  try {
    // Load full arrow details with spine specifications for editing
    const fullArrowDetails = await api.getArrowDetails(arrow.id);
    emit('edit', fullArrowDetails);
  } catch (error) {
    console.error('Error loading arrow details:', error);
    showMessage('Failed to load arrow details for editing', 'error');
  }
};

const openCreateModal = () => {
  emit('create');
};

const confirmDelete = (arrow: Arrow) => {
  emit('delete', arrow);
};

// Utility functions
const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = { show: true, text, type };
  setTimeout(() => {
    message.value.show = false;
  }, 4000);
};

const formatDate = (dateString: string) => {
  if (!dateString) return 'Unknown';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch {
    return 'Unknown';
  }
};

const formatArrowType = (type: string) => {
  if (!type) return '';
  return type.charAt(0).toUpperCase() + type.slice(1);
};

const getMaterialBadgeClass = (material: string) => {
  const classes = {
    'Carbon': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    'Aluminum': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'Carbon / Aluminum': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    'Wood': 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300'
  };
  return classes[material as keyof typeof classes] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
};

const getTypeBadgeClass = (type: string) => {
  const classes = {
    'hunting': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'target': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'indoor': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
    'outdoor': 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300',
    '3d': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    'recreational': 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300'
  };
  return classes[type as keyof typeof classes] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
};

const getLengthStatusBadgeClass = (status: string) => {
  const classes = {
    'Complete': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'Missing': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'Partial': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'No Spines': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400',
    'Unknown': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
};

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.style.display = 'none';
};

// Column management functions
const saveColumnSettings = () => {
  if (process.client) {
    localStorage.setItem('admin-arrows-columns', JSON.stringify(visibleColumns.value));
  }
};

const loadColumnSettings = () => {
  if (process.client) {
    try {
      const saved = localStorage.getItem('admin-arrows-columns');
      if (saved) {
        const savedColumns = JSON.parse(saved);
        // Merge saved settings with defaults to handle new columns
        visibleColumns.value = { ...defaultColumns, ...savedColumns };
      }
    } catch (error) {
      console.warn('Failed to load column settings:', error);
      visibleColumns.value = { ...defaultColumns };
    }
  }
};

const resetColumns = () => {
  visibleColumns.value = { ...defaultColumns };
  saveColumnSettings();
  showMessage('Column settings reset to default', 'success');
};

// Expose refresh method
defineExpose({
  loadArrows,
  showMessage
});

// Initialize
onMounted(() => {
  loadColumnSettings();
  loadArrows();
  loadManufacturers();
});
</script>

<style scoped>
.form-input,
.form-select {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:focus:ring-indigo-400 dark:focus:border-indigo-400;
}
</style>