import DataTable from 'datatables.net-dt'

export default defineNuxtPlugin(() => {
  // Make DataTable available globally
  return {
    provide: {
      DataTable
    }
  }
})