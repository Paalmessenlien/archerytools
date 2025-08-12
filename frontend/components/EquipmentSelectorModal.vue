<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-cogs mr-2 text-green-600"></i>
            Add Equipment to {{ bowSetup.name }}
          </h3>
          <CustomButton @click="$emit('close')" variant="text" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </CustomButton>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-hidden">
        <EquipmentSelector
          @select="handleEquipmentSelect"
          :excluded-equipment="excludedEquipment"
          :show-add-notes="true"
        />
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
        <div class="flex justify-end space-x-3">
          <CustomButton @click="$emit('close')" variant="outlined">
            Cancel
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  bowSetup: {
    type: Object,
    required: true
  },
  excludedEquipment: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select', 'close'])

const handleEquipmentSelect = (equipment) => {
  emit('select', equipment)
}
</script>