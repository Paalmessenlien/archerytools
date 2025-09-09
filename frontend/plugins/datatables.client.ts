import DataTable from 'datatables.net-dt'

export default defineNuxtPlugin(() => {
  // Only initialize on client side
  if (process.client) {
    // Make DataTable available globally
    return {
      provide: {
        DataTable
      }
    }
  }
  
  // Return empty provider for server-side
  return {
    provide: {
      DataTable: null
    }
  }
})