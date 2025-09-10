<template>
  <div class="spine-chart-datatable">
    <!-- Read-only notification -->
    <div v-if="props.readonly" 
         class="mb-4 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg"
         role="alert"
         aria-live="polite">
      <div class="flex items-center">
        <i class="fas fa-info-circle text-amber-600 dark:text-amber-400 mr-3 flex-shrink-0"></i>
        <div>
          <h3 class="text-sm font-medium text-amber-800 dark:text-amber-200">
            Read-Only View
          </h3>
          <p class="text-xs text-amber-700 dark:text-amber-300 mt-1">
            This chart cannot be modified. Return to the main page to copy this chart for editing.
          </p>
        </div>
      </div>
    </div>

    <!-- Enhanced Toolbar -->
    <div v-if="!props.readonly" class="flex flex-wrap items-center justify-between gap-2 mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
      <div class="flex flex-wrap gap-2">
        <CustomButton
          @click="addNewEntry"
          variant="filled"
          size="small"
          class="bg-green-600 text-white hover:bg-green-700 min-h-[36px]"
          aria-label="Add new spine entry to chart"
        >
          <i class="fas fa-plus mr-1"></i>
          Add Entry
        </CustomButton>
        <CustomButton
          @click="exportToCsv"
          variant="outlined"
          size="small"
          class="text-blue-600 border-blue-300 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-600 min-h-[36px]"
          aria-label="Export spine chart data as CSV file"
        >
          <i class="fas fa-download mr-1"></i>
          Export CSV
        </CustomButton>
        <CustomButton
          @click="sortByWeight"
          variant="outlined"
          size="small"
          class="text-purple-600 border-purple-300 hover:bg-purple-50 dark:text-purple-400 dark:border-purple-600 min-h-[36px]"
          aria-label="Sort table entries by draw weight"
        >
          <i class="fas fa-sort-amount-up mr-1"></i>
          Sort by Weight
        </CustomButton>
      </div>
      <div class="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
        <span class="inline-flex items-center px-2 py-1 rounded-md bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 font-medium">
          {{ props.data.length }} {{ props.data.length === 1 ? 'entry' : 'entries' }}
        </span>
        <span v-if="props.loading" class="inline-flex items-center">
          <i class="fas fa-spinner fa-spin mr-1"></i>
          Loading...
        </span>
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
            <th>Speed (fps)</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <!-- Data will be populated by DataTables -->
        </tbody>
      </table>
    </div>

    <!-- Enhanced Loading overlay -->
    <div v-if="loading" class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm flex items-center justify-center rounded-lg z-10">
      <div class="flex flex-col items-center space-y-3">
        <div class="relative">
          <div class="animate-spin rounded-full h-8 w-8 border-3 border-blue-200 dark:border-purple-200"></div>
          <div class="animate-spin rounded-full h-8 w-8 border-3 border-blue-600 dark:border-purple-400 border-t-transparent absolute inset-0"></div>
        </div>
        <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Loading spine chart data...</p>
        <p class="text-xs text-gray-500 dark:text-gray-400">Please wait while we fetch the data</p>
      </div>
    </div>

    <!-- Enhanced Error state -->
    <div v-if="error" class="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex items-start">
        <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 mt-0.5 mr-3 flex-shrink-0"></i>
        <div class="flex-1">
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Error Loading Data</h3>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
          <div class="mt-3">
            <button @click="$emit('retry')" 
                    class="text-xs bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-3 py-1.5 rounded hover:bg-red-200 dark:hover:bg-red-900/50 font-medium transition-colors">
              <i class="fas fa-redo mr-1"></i>
              Try Again
            </button>
          </div>
        </div>
      </div>
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
  speed?: number
}

interface Props {
  data: SpineGridEntry[]
  readonly?: boolean
  loading?: boolean
  error?: string
  manufacturer?: string
  model?: string
  bow_type?: string
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
  error: '',
  manufacturer: '',
  model: '',
  bow_type: ''
})

const emit = defineEmits<Emits>()

// Template refs
const tableRef = ref<HTMLTableElement>()

// DataTables instance
let dataTable: Api<any> | null = null

// State
const loading = toRef(props, 'loading')
const error = toRef(props, 'error')

// Inline editing state - use global objects that can be accessed by render functions
let editingRowsGlobal: Set<number> = new Set()
let editingValuesGlobal: { [key: string]: any } = {}

// Reactive refs for component state
const editingRows = ref<Set<number>>(new Set())
const editingValues = ref<{ [key: string]: any }>({})

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
        render: (data: any, type: string, row: SpineGridEntry, meta: any) => {
          if (props.readonly) {
            return typeof data === 'string' ? data : `${data}`
          }
          
          // Check if this row is currently being edited
          const isEditing = editingRowsGlobal.has(meta.row)
          console.log(`🔍 Rendering draw_weight_range_lbs for row ${meta.row}, isEditing:`, isEditing, 'editingRowsGlobal:', Array.from(editingRowsGlobal), 'timestamp:', Date.now())
          
          if (isEditing) {
            const editKey = `${meta.row}_draw_weight_range_lbs`
            const currentValue = editingValuesGlobal[editKey] ?? data
            console.log(`📝 Rendering input field for ${editKey} with value:`, currentValue)
            return `
              <input 
                type="text" 
                value="${currentValue}" 
                class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                data-field="draw_weight_range_lbs" 
                data-row="${meta.row}"
                placeholder="e.g., 40-50"
              />`
          } else {
            console.log(`👁️ Rendering display span for row ${meta.row}`)
            return `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${meta.row}" data-field="draw_weight_range_lbs">${typeof data === 'string' ? data : `${data}`}</span>`
          }
        }
      },
      {
        data: 'arrow_length_in',
        title: 'Arrow Length (in)',
        width: '20%',
        render: (data: number, type: string, row: SpineGridEntry, meta: any) => {
          if (props.readonly) {
            return `${data}"`
          }
          
          const isEditing = editingRowsGlobal.has(meta.row)
          console.log(`🔍 Rendering arrow_length_in for row ${meta.row}, isEditing:`, isEditing)
          
          if (isEditing) {
            const editKey = `${meta.row}_arrow_length_in`
            const currentValue = editingValuesGlobal[editKey] ?? data
            return `
              <input 
                type="number" 
                value="${currentValue}" 
                step="0.5"
                min="20"
                max="36"
                class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                data-field="arrow_length_in" 
                data-row="${meta.row}"
                placeholder="28"
              />`
          } else {
            return `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${meta.row}" data-field="arrow_length_in">${data}"</span>`
          }
        }
      },
      {
        data: 'spine',
        title: 'Recommended Spine',
        width: '25%',
        className: 'font-medium text-blue-600 dark:text-blue-400',
        render: (data: string, type: string, row: SpineGridEntry, meta: any) => {
          if (props.readonly) {
            return data
          }
          
          const isEditing = editingRowsGlobal.has(meta.row)
          console.log(`🔍 Rendering spine for row ${meta.row}, isEditing:`, isEditing)
          
          if (isEditing) {
            const editKey = `${meta.row}_spine`
            const currentValue = editingValuesGlobal[editKey] ?? data
            return `
              <input 
                type="text" 
                value="${currentValue}" 
                class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                data-field="spine" 
                data-row="${meta.row}"
                placeholder="e.g., 400, 300-400"
              />`
          } else {
            return `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded font-medium text-blue-600 dark:text-blue-400" data-row="${meta.row}" data-field="spine">${data}</span>`
          }
        }
      },
      {
        data: 'arrow_size',
        title: 'Arrow Size',
        width: '15%',
        className: 'text-gray-600 dark:text-gray-400',
        render: (data: string, type: string, row: SpineGridEntry, meta: any) => {
          if (props.readonly) {
            return data || '—'
          }
          
          const isEditing = editingRowsGlobal.has(meta.row)
          console.log(`🔍 Rendering arrow_size for row ${meta.row}, isEditing:`, isEditing)
          
          if (isEditing) {
            const editKey = `${meta.row}_arrow_size`
            const currentValue = editingValuesGlobal[editKey] ?? (data || '')
            return `
              <input 
                type="text" 
                value="${currentValue}" 
                class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                data-field="arrow_size" 
                data-row="${meta.row}"
                placeholder="e.g., 2314"
              />`
          } else {
            return `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded text-gray-600 dark:text-gray-400" data-row="${meta.row}" data-field="arrow_size">${data || '—'}</span>`
          }
        }
      },
      {
        data: 'speed',
        title: 'Speed (fps)',
        width: '15%',
        className: 'text-gray-600 dark:text-gray-400',
        render: (data: number, type: string, row: SpineGridEntry, meta: any) => {
          if (props.readonly) {
            return data ? `${data}` : '—'
          }
          
          const isEditing = editingRowsGlobal.has(meta.row)
          console.log(`🔍 Rendering speed for row ${meta.row}, isEditing:`, isEditing)
          
          if (isEditing) {
            const editKey = `${meta.row}_speed`
            const currentValue = editingValuesGlobal[editKey] ?? (data || '')
            return `
              <input 
                type="number" 
                value="${currentValue}" 
                step="1"
                min="100"
                max="400"
                class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                data-field="speed" 
                data-row="${meta.row}"
                placeholder="fps"
              />`
          } else {
            return `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded text-gray-600 dark:text-gray-400" data-row="${meta.row}" data-field="speed">${data ? `${data} fps` : '—'}</span>`
          }
        }
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
          
          const isEditing = editingRowsGlobal.has(meta.row)
          console.log(`🔍 Rendering actions for row ${meta.row}, isEditing:`, isEditing)
          
          if (isEditing) {
            return `
              <div class="flex space-x-1">
                <button class="save-btn text-green-600 hover:bg-green-100 dark:text-green-400 p-1 rounded" 
                        data-row-index="${meta.row}" title="Save changes">
                  <i class="fas fa-check text-xs"></i>
                </button>
                <button class="cancel-btn text-gray-600 hover:bg-gray-100 dark:text-gray-400 p-1 rounded" 
                        data-row-index="${meta.row}" title="Cancel editing">
                  <i class="fas fa-times text-xs"></i>
                </button>
              </div>
            `
          } else {
            return `
              <div class="flex space-x-1">
                <button class="edit-btn text-blue-600 hover:bg-blue-100 dark:text-blue-400 p-1 rounded" 
                        data-row-index="${meta.row}" title="Edit entry">
                  <i class="fas fa-edit text-xs"></i>
                </button>
                <button class="duplicate-btn text-green-600 hover:bg-green-100 dark:text-green-400 p-1 rounded" 
                        data-row-index="${meta.row}" title="Duplicate entry">
                  <i class="fas fa-copy text-xs"></i>
                </button>
                <button class="delete-btn text-red-600 hover:bg-red-100 dark:text-red-400 p-1 rounded" 
                        data-row-index="${meta.row}" title="Delete entry">
                  <i class="fas fa-trash text-xs"></i>
                </button>
              </div>
            `
          }
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
      // Event delegation handles this automatically, no need to reattach
      console.log('DataTable redraw complete, using event delegation')
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
    
    // Set up event delegation (persists through redraws)
    setupEventDelegation()
    
  } catch (err) {
    console.error('Failed to initialize DataTable:', err)
    emit('dataChange', [])
  }
}

// Use event delegation for better performance and persistence
const setupEventDelegation = () => {
  if (!tableRef.value) return

  // Remove existing listeners first
  tableRef.value.removeEventListener('click', handleTableClick)
  tableRef.value.removeEventListener('input', handleTableInput)
  tableRef.value.removeEventListener('keydown', handleTableKeydown)
  
  // Add event delegation listeners
  tableRef.value.addEventListener('click', handleTableClick)
  tableRef.value.addEventListener('input', handleTableInput)
  tableRef.value.addEventListener('keydown', handleTableKeydown)
}

// Centralized click handler using event delegation
const handleTableClick = (e: Event) => {
  const target = e.target as HTMLElement
  const button = target.closest('button') as HTMLButtonElement
  const cell = target.closest('.inline-edit-cell') as HTMLElement
  
  console.log('🖱️ Table click detected:', {
    target: target.tagName,
    targetClasses: target.className,
    button: button?.className,
    cell: cell?.className,
    readonly: props.readonly
  })
  
  if (button) {
    e.preventDefault()
    const rowIndex = parseInt(button.dataset.rowIndex || '0')
    console.log('🔘 Button clicked:', button.className, 'Row:', rowIndex)
    
    if (button.classList.contains('edit-btn')) {
      console.log('✏️ Edit button clicked, starting inline edit for row:', rowIndex)
      startInlineEdit(rowIndex)
    } else if (button.classList.contains('duplicate-btn')) {
      console.log('📋 Duplicate button clicked for row:', rowIndex)
      duplicateRow(rowIndex)
    } else if (button.classList.contains('delete-btn')) {
      console.log('🗑️ Delete button clicked for row:', rowIndex)
      deleteRow(rowIndex)
    } else if (button.classList.contains('save-btn')) {
      console.log('💾 Save button clicked for row:', rowIndex)
      saveInlineEdit(rowIndex)
    } else if (button.classList.contains('cancel-btn')) {
      console.log('❌ Cancel button clicked for row:', rowIndex)
      cancelInlineEdit(rowIndex)
    }
  } else if (cell && !props.readonly) {
    e.preventDefault()
    const rowIndex = parseInt(cell.dataset.row || '0')
    console.log('📝 Cell clicked, starting inline edit for row:', rowIndex)
    startInlineEdit(rowIndex)
  } else {
    console.log('👆 Click not handled - button:', !!button, 'cell:', !!cell, 'readonly:', props.readonly)
  }
}

// Centralized input handler
const handleTableInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.classList.contains('inline-edit-input')) {
    const rowIndex = parseInt(target.dataset.row || '0')
    const field = target.dataset.field || ''
    const editKey = `${rowIndex}_${field}`
    // Update both reactive state and global state
    editingValues.value[editKey] = target.value
    editingValuesGlobal[editKey] = target.value
  }
}

// Centralized keydown handler
const handleTableKeydown = (e: KeyboardEvent) => {
  const target = e.target as HTMLInputElement
  if (target.classList.contains('inline-edit-input')) {
    const rowIndex = parseInt(target.dataset.row || '0')
    
    if (e.key === 'Enter') {
      e.preventDefault()
      saveInlineEdit(rowIndex)
    } else if (e.key === 'Escape') {
      e.preventDefault()
      cancelInlineEdit(rowIndex)
    }
  }
}

// Legacy function for compatibility
const attachRowEventListeners = () => {
  setupEventDelegation()
}

// Row operations
const addNewEntry = () => {
  const newEntry: SpineGridEntry = {
    draw_weight_range_lbs: '',
    arrow_length_in: 28,
    spine: '',
    arrow_size: '',
    speed: undefined
  }
  
  emit('rowAdd', newEntry)
}

const editRow = (rowIndex: number) => {
  if (!dataTable) return
  
  const rowData = dataTable.row(rowIndex).data()
  emit('rowEdit', rowIndex, rowData)
}

const duplicateRow = (rowIndex: number) => {
  if (!dataTable) return
  
  console.log('📋 Duplicating row:', rowIndex)
  
  // Get the original row data
  const originalRowData = dataTable.row(rowIndex).data()
  console.log('🔍 Original row data:', originalRowData)
  
  // Create a copy of the row data
  const duplicatedEntry: SpineGridEntry = {
    draw_weight_range_lbs: originalRowData.draw_weight_range_lbs,
    arrow_length_in: originalRowData.arrow_length_in,
    spine: originalRowData.spine,
    arrow_size: originalRowData.arrow_size || '',
    speed: originalRowData.speed
  }
  
  console.log('✨ Duplicated entry:', duplicatedEntry)
  
  // Add the duplicated row to DataTables
  dataTable.row.add(duplicatedEntry).draw()
  
  console.log('✅ Row duplicated successfully')
  
  // Emit the row add event so parent components know about the new data
  emit('rowAdd', duplicatedEntry)
}

const deleteRow = (rowIndex: number) => {
  emit('rowDelete', rowIndex)
}

// Inline editing functions
const startInlineEdit = (rowIndex: number) => {
  console.log('🚀 startInlineEdit called for row:', rowIndex, 'readonly:', props.readonly)
  
  if (props.readonly) {
    console.log('⛔ Cannot start inline edit - table is readonly')
    return
  }
  
  // Initialize editing values with current row data
  if (dataTable) {
    const rowData = dataTable.row(rowIndex).data()
    console.log('📊 Row data for editing:', rowData)
    
    // Update both reactive state and global state
    const drawWeightKey = `${rowIndex}_draw_weight_range_lbs`
    const arrowLengthKey = `${rowIndex}_arrow_length_in`
    const spineKey = `${rowIndex}_spine`
    const arrowSizeKey = `${rowIndex}_arrow_size`
    const speedKey = `${rowIndex}_speed`
    
    editingValues.value[drawWeightKey] = rowData.draw_weight_range_lbs
    editingValues.value[arrowLengthKey] = rowData.arrow_length_in
    editingValues.value[spineKey] = rowData.spine
    editingValues.value[arrowSizeKey] = rowData.arrow_size || ''
    editingValues.value[speedKey] = rowData.speed || ''
    
    editingValuesGlobal[drawWeightKey] = rowData.draw_weight_range_lbs
    editingValuesGlobal[arrowLengthKey] = rowData.arrow_length_in
    editingValuesGlobal[spineKey] = rowData.spine
    editingValuesGlobal[arrowSizeKey] = rowData.arrow_size || ''
    editingValuesGlobal[speedKey] = rowData.speed || ''
  }
  
  // Add to editing rows (both reactive and global)
  editingRows.value.add(rowIndex)
  editingRowsGlobal.add(rowIndex)
  console.log('✅ Added row to editing set. Current editing rows:', Array.from(editingRows.value), 'Global:', Array.from(editingRowsGlobal))
  
  // DOM-based inline editing - bypass DataTables render functions entirely
  if (dataTable) {
    const rowElement = dataTable.row(rowIndex).node() as HTMLTableRowElement
    if (rowElement) {
      console.log('🔧 Converting cells to editable inputs via DOM manipulation')
      
      // Convert each cell to an input field
      const cells = rowElement.querySelectorAll('td')
      const rowData = dataTable.row(rowIndex).data()
      
      // Draw Weight (column 0)
      if (cells[0]) {
        const currentValue = rowData.draw_weight_range_lbs
        cells[0].innerHTML = `<input type="text" value="${currentValue}" class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" data-field="draw_weight_range_lbs" data-row="${rowIndex}" placeholder="e.g., 40-50" />`
      }
      
      // Arrow Length (column 1)  
      if (cells[1]) {
        const currentValue = rowData.arrow_length_in
        cells[1].innerHTML = `<input type="number" value="${currentValue}" class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" data-field="arrow_length_in" data-row="${rowIndex}" step="0.1" min="20" max="35" placeholder="28.0" />`
      }
      
      // Spine (column 2)
      if (cells[2]) {
        const currentValue = rowData.spine
        cells[2].innerHTML = `<input type="text" value="${currentValue}" class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" data-field="spine" data-row="${rowIndex}" placeholder="400, 500, etc." />`
      }
      
      // Arrow Size (column 3)
      if (cells[3]) {
        const currentValue = rowData.arrow_size || ''
        cells[3].innerHTML = `<input type="text" value="${currentValue}" class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" data-field="arrow_size" data-row="${rowIndex}" placeholder="Optional" />`
      }
      
      // Speed (column 4)
      if (cells[4]) {
        const currentValue = rowData.speed || ''
        cells[4].innerHTML = `<input type="number" value="${currentValue}" class="inline-edit-input w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" data-field="speed" data-row="${rowIndex}" step="1" min="100" max="400" placeholder="fps" />`
      }
      
      // Actions (column 5) - Replace edit button with save/cancel buttons
      if (cells[5]) {
        cells[5].innerHTML = `
          <div class="flex space-x-1">
            <button class="save-btn text-green-600 hover:bg-green-100 dark:text-green-400 p-1 rounded" 
                    data-row-index="${rowIndex}" title="Save changes">
              <i class="fas fa-check text-xs"></i>
            </button>
            <button class="cancel-btn text-gray-600 hover:bg-gray-100 dark:text-gray-400 p-1 rounded" 
                    data-row-index="${rowIndex}" title="Cancel editing">
              <i class="fas fa-times text-xs"></i>
            </button>
          </div>`
      }
      
      // Focus the first input field
      nextTick(() => {
        const firstInput = cells[0]?.querySelector('input') as HTMLInputElement
        if (firstInput) {
          firstInput.focus()
          console.log('✅ DOM-based inline editing activated and focused')
        }
      })
    } else {
      console.log('❌ Could not find row element for DOM manipulation')
    }
  }
}

const saveInlineEdit = (rowIndex: number) => {
  if (!dataTable) return
  
  // Get current values from editing state
  const updatedEntry: SpineGridEntry = {
    draw_weight_range_lbs: editingValues.value[`${rowIndex}_draw_weight_range_lbs`] || '',
    arrow_length_in: parseFloat(editingValues.value[`${rowIndex}_arrow_length_in`]) || 0,
    spine: editingValues.value[`${rowIndex}_spine`] || '',
    arrow_size: editingValues.value[`${rowIndex}_arrow_size`] || '',
    speed: editingValues.value[`${rowIndex}_speed`] ? parseFloat(editingValues.value[`${rowIndex}_speed`]) : undefined
  }
  
  // Basic validation
  if (!updatedEntry.draw_weight_range_lbs || !updatedEntry.arrow_length_in || !updatedEntry.spine) {
    alert('Please fill in all required fields (Draw Weight, Arrow Length, and Spine)')
    return
  }
  
  // Exit edit mode (both reactive and global)
  editingRows.value.delete(rowIndex)
  editingRowsGlobal.delete(rowIndex)
  
  // Clear editing values for this row (both reactive and global)
  delete editingValues.value[`${rowIndex}_draw_weight_range_lbs`]
  delete editingValues.value[`${rowIndex}_arrow_length_in`]
  delete editingValues.value[`${rowIndex}_spine`]
  delete editingValues.value[`${rowIndex}_arrow_size`]
  delete editingValues.value[`${rowIndex}_speed`]
  
  delete editingValuesGlobal[`${rowIndex}_draw_weight_range_lbs`]
  delete editingValuesGlobal[`${rowIndex}_arrow_length_in`]
  delete editingValuesGlobal[`${rowIndex}_spine`]
  delete editingValuesGlobal[`${rowIndex}_arrow_size`]
  delete editingValuesGlobal[`${rowIndex}_speed`]
  
  // Update the DataTables data
  dataTable.row(rowIndex).data(updatedEntry)
  
  // DOM-based restoration - restore cells with updated values
  const rowElement = dataTable.row(rowIndex).node() as HTMLTableRowElement
  if (rowElement) {
    console.log('🔧 Restoring cells with updated values via DOM manipulation')
    
    const cells = rowElement.querySelectorAll('td')
    
    // Restore Draw Weight (column 0)
    if (cells[0]) {
      cells[0].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="draw_weight_range_lbs">${updatedEntry.draw_weight_range_lbs}</span>`
    }
    
    // Restore Arrow Length (column 1)  
    if (cells[1]) {
      cells[1].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="arrow_length_in">${updatedEntry.arrow_length_in}</span>`
    }
    
    // Restore Spine (column 2)
    if (cells[2]) {
      cells[2].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="spine">${updatedEntry.spine}</span>`
    }
    
    // Restore Arrow Size (column 3)
    if (cells[3]) {
      const arrowSize = updatedEntry.arrow_size || ''
      cells[3].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="arrow_size">${arrowSize}</span>`
    }
    
    // Restore Speed (column 4)
    if (cells[4]) {
      const speed = updatedEntry.speed ? `${updatedEntry.speed} fps` : '—'
      cells[4].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="speed">${speed}</span>`
    }
    
    // Restore Actions (column 5) - Back to edit, duplicate, delete buttons
    if (cells[5]) {
      cells[5].innerHTML = `
        <div class="flex space-x-1">
          <button class="edit-btn text-blue-600 hover:bg-blue-100 dark:text-blue-400 p-1 rounded" 
                  data-row-index="${rowIndex}" title="Edit row">
            <i class="fas fa-edit text-xs"></i>
          </button>
          <button class="duplicate-btn text-green-600 hover:bg-green-100 dark:text-green-400 p-1 rounded" 
                  data-row-index="${rowIndex}" title="Duplicate row">
            <i class="fas fa-copy text-xs"></i>
          </button>
          <button class="delete-btn text-red-600 hover:bg-red-100 dark:text-red-400 p-1 rounded" 
                  data-row-index="${rowIndex}" title="Delete row">
            <i class="fas fa-trash text-xs"></i>
          </button>
        </div>`
    }
    
    console.log('✅ DOM-based save restoration completed')
  }
  
  // Emit the edit event
  emit('rowEdit', rowIndex, updatedEntry)
}

const cancelInlineEdit = (rowIndex: number) => {
  // Exit edit mode (both reactive and global)
  editingRows.value.delete(rowIndex)
  editingRowsGlobal.delete(rowIndex)
  
  // Clear editing values for this row (both reactive and global)
  delete editingValues.value[`${rowIndex}_draw_weight_range_lbs`]
  delete editingValues.value[`${rowIndex}_arrow_length_in`]
  delete editingValues.value[`${rowIndex}_spine`]
  delete editingValues.value[`${rowIndex}_arrow_size`]
  delete editingValues.value[`${rowIndex}_speed`]
  
  delete editingValuesGlobal[`${rowIndex}_draw_weight_range_lbs`]
  delete editingValuesGlobal[`${rowIndex}_arrow_length_in`]
  delete editingValuesGlobal[`${rowIndex}_spine`]
  delete editingValuesGlobal[`${rowIndex}_arrow_size`]
  delete editingValuesGlobal[`${rowIndex}_speed`]
  
  // DOM-based restoration - restore original cell content
  if (dataTable) {
    const rowElement = dataTable.row(rowIndex).node() as HTMLTableRowElement
    if (rowElement) {
      console.log('🔧 Restoring original cell content via DOM manipulation')
      
      const cells = rowElement.querySelectorAll('td')
      const rowData = dataTable.row(rowIndex).data()
      
      // Restore Draw Weight (column 0)
      if (cells[0]) {
        cells[0].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="draw_weight_range_lbs">${rowData.draw_weight_range_lbs}</span>`
      }
      
      // Restore Arrow Length (column 1)  
      if (cells[1]) {
        cells[1].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="arrow_length_in">${rowData.arrow_length_in}</span>`
      }
      
      // Restore Spine (column 2)
      if (cells[2]) {
        cells[2].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="spine">${rowData.spine}</span>`
      }
      
      // Restore Arrow Size (column 3)
      if (cells[3]) {
        const arrowSize = rowData.arrow_size || ''
        cells[3].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="arrow_size">${arrowSize}</span>`
      }
      
      // Restore Speed (column 4)
      if (cells[4]) {
        const speed = rowData.speed ? `${rowData.speed} fps` : '—'
        cells[4].innerHTML = `<span class="inline-edit-cell cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-1 rounded" data-row="${rowIndex}" data-field="speed">${speed}</span>`
      }
      
      // Restore Actions (column 5) - Back to edit, duplicate, delete buttons  
      if (cells[5]) {
        cells[5].innerHTML = `
          <div class="flex space-x-1">
            <button class="edit-btn text-blue-600 hover:bg-blue-100 dark:text-blue-400 p-1 rounded" 
                    data-row-index="${rowIndex}" title="Edit row">
              <i class="fas fa-edit text-xs"></i>
            </button>
            <button class="duplicate-btn text-green-600 hover:bg-green-100 dark:text-green-400 p-1 rounded" 
                    data-row-index="${rowIndex}" title="Duplicate row">
              <i class="fas fa-copy text-xs"></i>
            </button>
            <button class="delete-btn text-red-600 hover:bg-red-100 dark:text-red-400 p-1 rounded" 
                    data-row-index="${rowIndex}" title="Delete row">
              <i class="fas fa-trash text-xs"></i>
            </button>
          </div>`
      }
      
      console.log('✅ DOM-based restoration completed')
    }
  }
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
  const headers = ['Draw Weight (lbs)', 'Arrow Length (in)', 'Recommended Spine', 'Arrow Size', 'Speed (fps)']
  
  const csvContent = [
    headers.join(','),
    ...data.map((row: SpineGridEntry) => [
      `"${row.draw_weight_range_lbs}"`,
      row.arrow_length_in,
      `"${row.spine}"`,
      `"${row.arrow_size || ''}"`,
      row.speed || ''
    ].join(','))
  ].join('\n')
  
  // Generate descriptive filename with chart info
  const timestamp = new Date().toISOString().slice(0, 10) // YYYY-MM-DD format
  const sanitize = (str: string) => str.replace(/[^a-zA-Z0-9\-_]/g, '-').replace(/--+/g, '-')
  
  let filename = 'spine-chart'
  if (props.manufacturer) filename += `-${sanitize(props.manufacturer)}`
  if (props.model) filename += `-${sanitize(props.model)}`
  if (props.bow_type) filename += `-${sanitize(props.bow_type)}`
  filename += `-${timestamp}.csv`
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url) // Clean up the object URL
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
  
  // Remove event listeners
  if (tableRef.value) {
    tableRef.value.removeEventListener('click', handleTableClick)
    tableRef.value.removeEventListener('input', handleTableInput)
    tableRef.value.removeEventListener('keydown', handleTableKeydown)
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