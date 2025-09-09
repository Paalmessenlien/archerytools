<template>
  <div class="spine-chart-datatable">
    <!-- Toolbar -->
    <div v-if="!props.readonly" class="flex flex-wrap items-center justify-between gap-2 mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
      <div class="flex flex-wrap gap-2">
        <CustomButton
          @click="addNewEntry"
          variant="filled"
          size="small"
          class="bg-green-600 text-white hover:bg-green-700"
        >
          <i class="fas fa-plus mr-1"></i>
          Add Entry
        </CustomButton>
        <CustomButton
          @click="exportToCsv"
          variant="outlined"
          size="small"
          class="text-blue-600 border-blue-300 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-600"
        >
          <i class="fas fa-download mr-1"></i>
          Export CSV
        </CustomButton>
        <CustomButton
          @click="sortByWeight"
          variant="outlined"
          size="small"
          class="text-purple-600 border-purple-300 hover:bg-purple-50 dark:text-purple-400 dark:border-purple-600"
        >
          <i class="fas fa-sort-amount-up mr-1"></i>
          Sort by Weight
        </CustomButton>
      </div>
      <div class="text-xs text-gray-500 dark:text-gray-400">
        {{ props.data.length }} {{ props.data.length === 1 ? 'entry' : 'entries' }}
      </div>
    </div>

    <!-- DataTables will be initialized here -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <table
        ref="tableRef"
        class="display responsive nowrap"
        style="width: 100%"
      >
        <thead>
          <tr>
            <th>Draw Weight (lbs)</th>
            <th>Arrow Length (in)</th>
            <th>Recommended Spine</th>
            <th>Arrow Size</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <!-- Data will be populated by DataTables -->
        </tbody>
      </table>
    </div>

    <!-- Loading overlay -->
    <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-75 dark:bg-gray-800 dark:bg-opacity-75 flex items-center justify-center rounded-lg">
      <div class="flex items-center space-x-2">
        <div class="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent dark:border-purple-400"></div>
        <span class="text-sm text-gray-600 dark:text-gray-400">Loading table...</span>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="error" class="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
      <p class="text-sm text-red-700 dark:text-red-300">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Api } from 'datatables.net-dt'

interface SpineGridEntry {
  draw_weight_range_lbs: string | number
  arrow_length_in: number
  spine: string
  arrow_size?: string
}

interface Props {
  data: SpineGridEntry[]
  readonly?: boolean
  loading?: boolean
  error?: string
}

interface Emits {
  dataChange: [data: SpineGridEntry[]]
  rowAdd: [entry: SpineGridEntry]
  rowEdit: [index: number, entry: SpineGridEntry]
  rowDelete: [index: number]
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
  loading: false,
  error: ''
})

const emit = defineEmits<Emits>()

// Template refs
const tableRef = ref<HTMLTableElement>()

// DataTables instance
let dataTable: Api<any> | null = null

// State
const loading = toRef(props, 'loading')
const error = toRef(props, 'error')

// DataTables configuration (simplified without extensions)
const getDataTablesConfig = () => {
  const config: any = {
    data: props.data,
    pageLength: 25,
    lengthMenu: [10, 25, 50, 100],
    order: [[0, 'asc']], // Sort by draw weight by default
    columns: [
      {
        data: 'draw_weight_range_lbs',
        title: 'Draw Weight (lbs)',
        width: '25%',
        render: (data: any) => {
          return typeof data === 'string' ? data : `${data}`
        }
      },
      {
        data: 'arrow_length_in',
        title: 'Arrow Length (in)',
        width: '20%',
        render: (data: number) => `${data}"`
      },
      {
        data: 'spine',
        title: 'Recommended Spine',
        width: '25%',
        className: 'font-medium text-blue-600 dark:text-blue-400'
      },
      {
        data: 'arrow_size',
        title: 'Arrow Size',
        width: '20%',
        render: (data: string) => data || '—',
        className: 'text-gray-600 dark:text-gray-400'
      },
      {
        data: null,
        title: 'Actions',
        width: '10%',
        orderable: false,
        searchable: false,
        render: (data: any, type: string, row: SpineGridEntry, meta: any) => {
          if (props.readonly) {
            return '<span class="text-gray-400 text-xs">Read-only</span>'
          }
          
          return `
            <div class="flex space-x-1">
              <button class="edit-btn text-blue-600 hover:bg-blue-100 dark:text-blue-400 p-1 rounded" 
                      data-row-index="${meta.row}" title="Edit entry">
                <i class="fas fa-edit text-xs"></i>
              </button>
              <button class="delete-btn text-red-600 hover:bg-red-100 dark:text-red-400 p-1 rounded" 
                      data-row-index="${meta.row}" title="Delete entry">
                <i class="fas fa-trash text-xs"></i>
              </button>
            </div>
          `
        }
      }
    ],
    dom: '<"spine-controls flex flex-col sm:flex-row justify-between items-center mb-4"lf>rtip',
    language: {
      search: '',
      searchPlaceholder: 'Search spine entries...',
      lengthMenu: 'Show _MENU_ entries',
      info: 'Showing _START_ to _END_ of _TOTAL_ entries',
      infoEmpty: 'No entries available',
      infoFiltered: '(filtered from _MAX_ total entries)',
      zeroRecords: 'No matching entries found',
      emptyTable: 'No spine entries available. Use the "Add Entry" button to create recommendations.'
    },
    drawCallback: function() {
      // Reattach event listeners after redraw
      attachRowEventListeners()
    }
  }

  return config
}

// Initialize DataTables
const initializeDataTable = async () => {
  if (!tableRef.value || !process.client) return

  try {
    // Get DataTable from the plugin
    const { $DataTable } = useNuxtApp()
    
    // Check if DataTable is available (it won't be during SSR)
    if (!$DataTable) {
      console.warn('DataTable not available, skipping initialization')
      return
    }
    
    // Initialize DataTables instance with core functionality only
    dataTable = new $DataTable(tableRef.value, getDataTablesConfig())
    
    // Attach initial event listeners
    attachRowEventListeners()
    
  } catch (err) {
    console.error('Failed to initialize DataTable:', err)
    emit('dataChange', [])
  }
}

// Attach event listeners for row actions
const attachRowEventListeners = () => {
  if (!dataTable) return

  // Edit button listeners
  const editButtons = tableRef.value?.querySelectorAll('.edit-btn')
  editButtons?.forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault()
      const rowIndex = parseInt((e.target as HTMLElement).closest('button')?.dataset.rowIndex || '0')
      editRow(rowIndex)
    })
  })

  // Delete button listeners  
  const deleteButtons = tableRef.value?.querySelectorAll('.delete-btn')
  deleteButtons?.forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault()
      const rowIndex = parseInt((e.target as HTMLElement).closest('button')?.dataset.rowIndex || '0')
      deleteRow(rowIndex)
    })
  })
}

// Row operations
const addNewEntry = () => {
  const newEntry: SpineGridEntry = {
    draw_weight_range_lbs: '',
    arrow_length_in: 28,
    spine: '',
    arrow_size: ''
  }
  
  emit('rowAdd', newEntry)
}

const editRow = (rowIndex: number) => {
  if (!dataTable) return
  
  const rowData = dataTable.row(rowIndex).data()
  emit('rowEdit', rowIndex, rowData)
}

const deleteRow = (rowIndex: number) => {
  emit('rowDelete', rowIndex)
}

// Toolbar methods
const sortByWeight = () => {
  if (dataTable) {
    dataTable.order([0, 'asc']).draw()
  }
}

// Export functionality
const exportToCsv = () => {
  const data = dataTable ? dataTable.data().toArray() : props.data
  const headers = ['Draw Weight (lbs)', 'Arrow Length (in)', 'Recommended Spine', 'Arrow Size']
  
  const csvContent = [
    headers.join(','),
    ...data.map((row: SpineGridEntry) => [
      `"${row.draw_weight_range_lbs}"`,
      row.arrow_length_in,
      `"${row.spine}"`,
      `"${row.arrow_size || ''}"`
    ].join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'spine-chart-data.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Update table data when props change
const updateTableData = () => {
  if (dataTable) {
    dataTable.clear()
    dataTable.rows.add(props.data)
    dataTable.draw()
  }
}

// Cleanup
const destroyDataTable = () => {
  if (dataTable) {
    dataTable.destroy()
    dataTable = null
  }
}

// Public methods
const refreshTable = () => {
  updateTableData()
}

const getCurrentData = (): SpineGridEntry[] => {
  return dataTable?.data().toArray() || []
}

// Expose methods to parent
defineExpose({
  refreshTable,
  getCurrentData
})

// Lifecycle
onMounted(async () => {
  await nextTick()
  await initializeDataTable()
})

onUnmounted(() => {
  destroyDataTable()
})

// Watch for data changes
watch(() => props.data, () => {
  updateTableData()
}, { deep: true })

watch(() => props.readonly, () => {
  // Reinitialize table when readonly status changes
  destroyDataTable()
  nextTick(() => {
    initializeDataTable()
  })
})
</script>

<style scoped>
.spine-chart-datatable {
  @apply relative;
}

/* Custom DataTables styling for dark mode compatibility */
:global(.dataTables_wrapper) {
  @apply text-gray-900 dark:text-gray-100;
}

:global(.dataTables_filter input) {
  @apply bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm;
}

:global(.dataTables_length select) {
  @apply bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm;
}

:global(.dataTables_info) {
  @apply text-sm text-gray-600 dark:text-gray-400;
}

:global(.paginate_button) {
  @apply px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700;
}

:global(.paginate_button:hover) {
  @apply bg-gray-50 dark:bg-gray-600;
}

:global(.paginate_button.current) {
  @apply bg-blue-600 dark:bg-purple-600 text-white border-blue-600 dark:border-purple-600;
}

/* Button styling */
:global(.dt-buttons .btn) {
  @apply inline-flex items-center;
}

/* Table styling */
:global(table.dataTable) {
  @apply bg-white dark:bg-gray-800;
}

:global(table.dataTable thead th) {
  @apply bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-600;
}

:global(table.dataTable tbody td) {
  @apply border-b border-gray-200 dark:border-gray-700 py-2;
}

:global(table.dataTable tbody tr:hover) {
  @apply bg-gray-50 dark:bg-gray-700;
}

/* Responsive styling */
:global(table.dataTable.dtr-inline.collapsed > tbody > tr > td.dtr-control:before) {
  @apply text-blue-600 dark:text-purple-400;
}
</style>