<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-6">
      <!-- Header -->
      <div class="mb-6">
        <nav class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
          <NuxtLink to="/info" class="hover:text-blue-600 dark:hover:text-blue-400">
            Information Center
          </NuxtLink>
          <i class="fas fa-chevron-right"></i>
          <span class="text-gray-900 dark:text-white">Quick Reference</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Quick Reference
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Essential charts, formulas, and conversion tables for field use
        </p>
      </div>

      <!-- Download/Print Actions -->
      <div class="bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800 p-6 mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-indigo-800 dark:text-indigo-200 mb-2">
              <i class="fas fa-print mr-2"></i>
              Printable Reference Cards
            </h2>
            <p class="text-indigo-700 dark:text-indigo-300">
              Print these reference cards for quick access in the field.
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="printPage"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-print mr-2"></i>
              Print
            </button>
            <button
              @click="downloadPDF"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-download mr-2"></i>
              Download PDF
            </button>
          </div>
        </div>
      </div>

      <div class="space-y-8">
        
        <!-- Spine Charts -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 print-section">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-chart-line text-blue-600 dark:text-blue-400 mr-3"></i>
            Spine Selection Charts
          </h2>
          
          <!-- Compound Bow Chart -->
          <div class="mb-8">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Compound Bow Spine Chart (28" Arrow)
            </h3>
            <div class="overflow-x-auto">
              <table class="w-full text-sm border-collapse border border-gray-300 dark:border-gray-600">
                <thead>
                  <tr class="bg-gray-100 dark:bg-gray-700">
                    <th class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-left">Draw Weight (lbs)</th>
                    <th class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">100 gr Points</th>
                    <th class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">125 gr Points</th>
                    <th class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">150 gr Points</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in compoundSpineChart" :key="row.weight" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td class="border border-gray-300 dark:border-gray-600 px-3 py-2 font-medium">{{ row.weight }}</td>
                    <td class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">{{ row.gr100 }}</td>
                    <td class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">{{ row.gr125 }}</td>
                    <td class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">{{ row.gr150 }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Recurve Bow Chart -->
          <div class="mb-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recurve Bow Spine Chart (28" Arrow)
            </h3>
            <div class="overflow-x-auto">
              <table class="w-full text-sm border-collapse border border-gray-300 dark:border-gray-600">
                <thead>
                  <tr class="bg-gray-100 dark:bg-gray-700">
                    <th class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-left">Draw Weight (lbs)</th>
                    <th class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">100 gr Points</th>
                    <th class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">125 gr Points</th>
                    <th class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">150 gr Points</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in recurveSpineChart" :key="row.weight" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td class="border border-gray-300 dark:border-gray-600 px-3 py-2 font-medium">{{ row.weight }}</td>
                    <td class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">{{ row.gr100 }}</td>
                    <td class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">{{ row.gr125 }}</td>
                    <td class="border border-gray-300 dark:border-gray-600 px-3 py-2 text-center">{{ row.gr150 }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
            <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
              <i class="fas fa-info-circle mr-2"></i>
              Spine Chart Notes
            </h4>
            <ul class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
              <li>• Charts based on 28" arrow length measured from nock groove to insert</li>
              <li>• Add 5 spine for each inch shorter, subtract 5 for each inch longer</li>
              <li>• Values are starting points - fine-tune with paper testing</li>
              <li>• Consider bow's efficiency and arrow rest type for final selection</li>
            </ul>
          </div>
        </div>

        <!-- Conversion Tables -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 print-section">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-exchange-alt text-green-600 dark:text-green-400 mr-3"></i>
            Conversion Tables
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            
            <!-- Length Conversions -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Length Conversions
              </h3>
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-3">Inches to Millimeters</h4>
                  <div class="grid grid-cols-2 gap-2 text-sm">
                    <div v-for="conversion in lengthConversions" :key="conversion.inches" class="flex justify-between">
                      <span>{{ conversion.inches }}"</span>
                      <span>{{ conversion.mm }} mm</span>
                    </div>
                  </div>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Quick Formula</h4>
                  <p class="text-sm text-blue-700 dark:text-blue-400">
                    <strong>Inches × 25.4 = Millimeters</strong><br>
                    <strong>Millimeters ÷ 25.4 = Inches</strong>
                  </p>
                </div>
              </div>
            </div>

            <!-- Weight Conversions -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Weight Conversions
              </h3>
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-3">Grains to Grams</h4>
                  <div class="grid grid-cols-2 gap-2 text-sm">
                    <div v-for="conversion in weightConversions" :key="conversion.grains" class="flex justify-between">
                      <span>{{ conversion.grains }} gr</span>
                      <span>{{ conversion.grams }} g</span>
                    </div>
                  </div>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Quick Formula</h4>
                  <p class="text-sm text-orange-700 dark:text-orange-400">
                    <strong>Grains × 0.0648 = Grams</strong><br>
                    <strong>Grams × 15.43 = Grains</strong>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tuning Checklists -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 print-section">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-clipboard-check text-orange-600 dark:text-orange-400 mr-3"></i>
            Tuning Checklists
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            
            <!-- Paper Tuning Checklist -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                <i class="fas fa-file-alt text-blue-500 mr-2"></i>
                Paper Tuning Checklist
              </h3>
              
              <div class="space-y-3">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Setup</h4>
                  <div class="space-y-1">
                    <label class="flex items-center text-sm text-blue-700 dark:text-blue-400">
                      <input type="checkbox" class="mr-2"> Set paper 6 feet from target
                    </label>
                    <label class="flex items-center text-sm text-blue-700 dark:text-blue-400">
                      <input type="checkbox" class="mr-2"> Secure paper in frame
                    </label>
                    <label class="flex items-center text-sm text-blue-700 dark:text-blue-400">
                      <input type="checkbox" class="mr-2"> Check shooting distance
                    </label>
                  </div>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Shooting</h4>
                  <div class="space-y-1">
                    <label class="flex items-center text-sm text-green-700 dark:text-green-400">
                      <input type="checkbox" class="mr-2"> Use consistent form
                    </label>
                    <label class="flex items-center text-sm text-green-700 dark:text-green-400">
                      <input type="checkbox" class="mr-2"> Shoot 3-5 arrows
                    </label>
                    <label class="flex items-center text-sm text-green-700 dark:text-green-400">
                      <input type="checkbox" class="mr-2"> Analyze tear patterns
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Equipment Check -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                <i class="fas fa-cogs text-purple-500 mr-2"></i>
                Equipment Check
              </h3>
              
              <div class="space-y-3">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">Arrows</h4>
                  <div class="space-y-1">
                    <label class="flex items-center text-sm text-purple-700 dark:text-purple-400">
                      <input type="checkbox" class="mr-2"> Check straightness
                    </label>
                    <label class="flex items-center text-sm text-purple-700 dark:text-purple-400">
                      <input type="checkbox" class="mr-2"> Inspect fletching
                    </label>
                    <label class="flex items-center text-sm text-purple-700 dark:text-purple-400">
                      <input type="checkbox" class="mr-2"> Verify nock fit
                    </label>
                  </div>
                </div>
                
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">Bow Setup</h4>
                  <div class="space-y-1">
                    <label class="flex items-center text-sm text-red-700 dark:text-red-400">
                      <input type="checkbox" class="mr-2"> Rest alignment
                    </label>
                    <label class="flex items-center text-sm text-red-700 dark:text-red-400">
                      <input type="checkbox" class="mr-2"> Nocking point position
                    </label>
                    <label class="flex items-center text-sm text-red-700 dark:text-red-400">
                      <input type="checkbox" class="mr-2"> String condition
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Safety Guidelines -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 print-section">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-shield-alt text-red-600 dark:text-red-400 mr-3"></i>
            Safety Guidelines
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            
            <!-- Range Safety -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Range Safety Rules
              </h3>
              
              <div class="space-y-3">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-3">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Critical Safety Rules
                  </h4>
                  <ul class="text-sm text-red-700 dark:text-red-400 space-y-2">
                    <li class="flex items-start">
                      <i class="fas fa-circle text-xs mt-2 mr-2"></i>
                      <span>Never shoot if anyone is downrange</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fas fa-circle text-xs mt-2 mr-2"></i>
                      <span>Always know what's beyond your target</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fas fa-circle text-xs mt-2 mr-2"></i>
                      <span>Wait for "all clear" before shooting</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fas fa-circle text-xs mt-2 mr-2"></i>
                      <span>Never dry fire a bow</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fas fa-circle text-xs mt-2 mr-2"></i>
                      <span>Inspect equipment before each use</span>
                    </li>
                  </ul>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-hard-hat mr-2"></i>
                    Protective Equipment
                  </h4>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <li>• Arm guard (mandatory)</li>
                    <li>• Finger tab or glove</li>
                    <li>• Chest guard (if needed)</li>
                    <li>• Safety glasses (recommended)</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Equipment Safety -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Equipment Safety
              </h3>
              
              <div class="space-y-3">
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-3">
                    <i class="fas fa-search mr-2"></i>
                    Pre-Shooting Inspection
                  </h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-400 space-y-1">
                    <li>• Check arrows for cracks or bends</li>
                    <li>• Inspect string and serving</li>
                    <li>• Verify all bolts are tight</li>
                    <li>• Check cam timing (compound)</li>
                    <li>• Test rest function</li>
                  </ul>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-ban mr-2"></i>
                    Never Use If:
                  </h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <li>• Arrows are damaged or bent</li>
                    <li>• String shows fraying</li>
                    <li>• Bow shows cracks or damage</li>
                    <li>• Rest is loose or misaligned</li>
                    <li>• You feel unwell or distracted</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Emergency Procedures -->
        <div class="bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800 p-6 print-section">
          <h2 class="text-2xl font-semibold text-red-800 dark:text-red-300 mb-4">
            <i class="fas fa-ambulance mr-3"></i>
            Emergency Procedures
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-3">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 class="font-medium text-red-800 dark:text-red-300 mb-2">
                <i class="fas fa-phone mr-2"></i>
                Emergency Contacts
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <p><strong>Emergency:</strong> 911</p>
                <p><strong>Range Officer:</strong> _________</p>
                <p><strong>First Aid Kit:</strong> Location _________</p>
              </div>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 class="font-medium text-red-800 dark:text-red-300 mb-2">
                <i class="fas fa-user-injured mr-2"></i>
                Injury Protocol
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <p>1. Stop all shooting immediately</p>
                <p>2. Assess injury severity</p>
                <p>3. Call for help if needed</p>
                <p>4. Apply first aid if trained</p>
              </div>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 class="font-medium text-red-800 dark:text-red-300 mb-2">
                <i class="fas fa-exclamation-circle mr-2"></i>
                Equipment Failure
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <p>1. Stop shooting immediately</p>
                <p>2. Secure the area</p>
                <p>3. Inspect for damage</p>
                <p>4. Do not continue until safe</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Page metadata
definePageMeta({
  middleware: ['auth-check'],
  layout: 'default'
})

useHead({
  title: 'Quick Reference - Archery Tools',
  meta: [
    { name: 'description', content: 'Essential charts, formulas, conversion tables, and safety guidelines for archery. Printable reference cards for field use.' }
  ]
})

// Spine chart data
const compoundSpineChart = ref([
  { weight: '40-45', gr100: '500-600', gr125: '400-500', gr150: '340-400' },
  { weight: '45-50', gr100: '400-500', gr125: '340-400', gr150: '300-340' },
  { weight: '50-55', gr100: '340-400', gr125: '300-340', gr150: '280-300' },
  { weight: '55-60', gr100: '300-340', gr125: '280-300', gr150: '260-280' },
  { weight: '60-65', gr100: '280-300', gr125: '260-280', gr150: '240-260' },
  { weight: '65-70', gr100: '260-280', gr125: '240-260', gr150: '220-240' },
  { weight: '70-75', gr100: '240-260', gr125: '220-240', gr150: '200-220' },
  { weight: '75-80', gr100: '220-240', gr125: '200-220', gr150: '180-200' }
])

const recurveSpineChart = ref([
  { weight: '25-30', gr100: '700-800', gr125: '600-700', gr150: '500-600' },
  { weight: '30-35', gr100: '600-700', gr125: '500-600', gr150: '400-500' },
  { weight: '35-40', gr100: '500-600', gr125: '400-500', gr150: '340-400' },
  { weight: '40-45', gr100: '400-500', gr125: '340-400', gr150: '300-340' },
  { weight: '45-50', gr100: '340-400', gr125: '300-340', gr150: '280-300' },
  { weight: '50-55', gr100: '300-340', gr125: '280-300', gr150: '260-280' },
  { weight: '55-60', gr100: '280-300', gr125: '260-280', gr150: '240-260' }
])

// Conversion data
const lengthConversions = ref([
  { inches: '1/8', mm: '3.2' },
  { inches: '1/4', mm: '6.4' },
  { inches: '1/2', mm: '12.7' },
  { inches: '1', mm: '25.4' },
  { inches: '2', mm: '50.8' },
  { inches: '3', mm: '76.2' },
  { inches: '6', mm: '152.4' },
  { inches: '12', mm: '304.8' }
])

const weightConversions = ref([
  { grains: '25', grams: '1.6' },
  { grains: '50', grams: '3.2' },
  { grains: '75', grams: '4.9' },
  { grains: '100', grams: '6.5' },
  { grains: '125', grams: '8.1' },
  { grains: '150', grams: '9.7' },
  { grains: '200', grams: '13.0' },
  { grains: '300', grams: '19.4' }
])

// Methods
const printPage = () => {
  window.print()
}

const downloadPDF = () => {
  // In a real implementation, you would generate a PDF
  alert('PDF download functionality would be implemented here')
}
</script>

<style scoped>
/* Print styles */
@media print {
  .print-section {
    page-break-inside: avoid;
    break-inside: avoid;
  }
  
  .no-print {
    display: none;
  }
  
  .bg-gradient-to-br {
    background: white !important;
  }
}

/* Table styles for better readability */
table {
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  table {
    font-size: 0.75rem;
  }
}
</style>