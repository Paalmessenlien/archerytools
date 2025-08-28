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
          <span class="text-gray-900 dark:text-white">Equipment Guide</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Archery Equipment Guide
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Complete guide to arrow components and bow accessories for optimal performance
        </p>
      </div>

      <!-- Equipment Management Link -->
      <div class="bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 rounded-lg border border-red-200 dark:border-red-800 p-6 mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">
              <i class="fas fa-cogs mr-2"></i>
              Manage Your Equipment
            </h2>
            <p class="text-red-700 dark:text-red-300">
              Add and track your bow equipment with our comprehensive equipment management system.
            </p>
          </div>
          <NuxtLink
            to="/my-setup"
            class="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-arrow-right mr-2"></i>
            My Equipment
          </NuxtLink>
        </div>
      </div>

      <div class="space-y-8">
        
        <!-- Arrow Components -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-bullseye text-orange-600 dark:text-orange-400 mr-3"></i>
            Arrow Components
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            
            <!-- Points and Inserts -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
              <div class="flex items-center mb-4">
                <div class="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                  <i class="fas fa-dot-circle text-red-600 dark:text-red-400 text-xl"></i>
                </div>
                <div class="ml-3">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Points and Inserts</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Critical for arrow balance and performance</p>
                </div>
              </div>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">Field Points</h4>
                  <ul class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <li>• Standard weights: 75, 100, 125, 150 grains</li>
                    <li>• Match broadhead weight for hunting</li>
                    <li>• Bullet points for 3D archery</li>
                    <li>• Blunt points for small game</li>
                  </ul>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Inserts</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-400 space-y-1">
                    <li>• Standard inserts: 8-32 thread most common</li>
                    <li>• Weight varies: 8-20 grains typically</li>
                    <li>• Outserts for larger diameter shafts</li>
                    <li>• Half-outs for weight reduction</li>
                  </ul>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">Installation Tips</h4>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <li>• Use proper adhesive (hot melt or epoxy)</li>
                    <li>• Ensure square cut on arrow shaft</li>
                    <li>• Check depth for consistent seating</li>
                    <li>• Test pull strength before use</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Nocks and Bushings -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
              <div class="flex items-center mb-4">
                <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                  <i class="fas fa-circle-notch text-blue-600 dark:text-blue-400 text-xl"></i>
                </div>
                <div class="ml-3">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Nocks and Bushings</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">String interface and consistency</p>
                </div>
              </div>
              
              <div class="space-y-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Nock Types</h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <li>• Index nocks: Single orientation for consistency</li>
                    <li>• Conventional nocks: Most common, various sizes</li>
                    <li>• Lighted nocks: For hunting and visibility</li>
                    <li>• Pin nocks: For small diameter arrows</li>
                  </ul>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Nock Sizing</h4>
                  <ul class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <li>• Must fit string serving properly</li>
                    <li>• Too tight: Affects arrow release</li>
                    <li>• Too loose: Inconsistent positioning</li>
                    <li>• Common sizes: .244", .246", .297"</li>
                  </ul>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">Bushings</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <li>• Weight addition to rear of arrow</li>
                    <li>• Brass: Heavy, adjusts FOC backward</li>
                    <li>• Aluminum: Lighter weight option</li>
                    <li>• Weighs 5-25 grains typically</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Fletching Options -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
              <div class="flex items-center mb-4">
                <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                  <i class="fas fa-feather text-green-600 dark:text-green-400 text-xl"></i>
                </div>
                <div class="ml-3">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Fletching Options</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Stabilization and arrow guidance</p>
                </div>
              </div>
              
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Vane Types</h4>
                  <ul class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <li>• Plastic vanes: Durable, consistent</li>
                    <li>• Natural feathers: Better forgiveness</li>
                    <li>• Low profile: Less wind drift</li>
                    <li>• High profile: More stabilization</li>
                  </ul>
                </div>
                
                <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-teal-800 dark:text-teal-300 mb-2">Configuration</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-400 space-y-1">
                    <li>• 3-fletch: Most common, good clearance</li>
                    <li>• 4-fletch: More stabilization, hunting</li>
                    <li>• Helical: Increases spin, forgiveness</li>
                    <li>• Straight: Less drag, target archery</li>
                  </ul>
                </div>
                
                <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300 mb-2">Size Guidelines</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-400 space-y-1">
                    <li>• Length: 2" target, 3-4" hunting</li>
                    <li>• Height: 0.5" low profile, 0.6"+ high</li>
                    <li>• Weight: 5-15 grains per vane</li>
                    <li>• Consider total fletching weight</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Wraps and Crests -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
              <div class="flex items-center mb-4">
                <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                  <i class="fas fa-palette text-purple-600 dark:text-purple-400 text-xl"></i>
                </div>
                <div class="ml-3">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Wraps and Crests</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Identification and personalization</p>
                </div>
              </div>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">Arrow Wraps</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <li>• Protect shaft from adhesive</li>
                    <li>• Easy fletching replacement</li>
                    <li>• Custom colors and patterns</li>
                    <li>• Weight: 3-8 grains typically</li>
                  </ul>
                </div>
                
                <div class="bg-pink-50 dark:bg-pink-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-pink-800 dark:text-pink-300 mb-2">Cresting</h4>
                  <ul class="text-sm text-pink-700 dark:text-pink-400 space-y-1">
                    <li>• Traditional painted bands</li>
                    <li>• Personal identification patterns</li>
                    <li>• Club or team colors</li>
                    <li>• Minimal weight addition</li>
                  </ul>
                </div>
                
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">Considerations</h4>
                  <ul class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <li>• Add to total arrow weight</li>
                    <li>• May affect spine slightly</li>
                    <li>• Consider durability needs</li>
                    <li>• Tournament regulations</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Bow Equipment Categories -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-bow-arrow text-blue-600 dark:text-blue-400 mr-3"></i>
            Bow Equipment Categories
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2 xl:grid-cols-4">
            
            <!-- Strings -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div class="flex items-center mb-3">
                <div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <i class="fas fa-grip-lines text-yellow-600 dark:text-yellow-400"></i>
                </div>
                <h3 class="ml-2 font-semibold text-gray-900 dark:text-white">Strings</h3>
              </div>
              <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Material: Dacron, FastFlight, etc.</li>
                <li>• Strand count and serving</li>
                <li>• String length and loops</li>
                <li>• Maintenance schedule</li>
              </ul>
            </div>

            <!-- Sights -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div class="flex items-center mb-3">
                <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                  <i class="fas fa-crosshairs text-green-600 dark:text-green-400"></i>
                </div>
                <h3 class="ml-2 font-semibold text-gray-900 dark:text-white">Sights</h3>
              </div>
              <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Pin sights: Multiple distance pins</li>
                <li>• Single pin: Adjustable distance</li>
                <li>• Pin size and brightness</li>
                <li>• Housing and mounting</li>
              </ul>
            </div>

            <!-- Arrow Rests -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div class="flex items-center mb-3">
                <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                  <i class="fas fa-hand-paper text-blue-600 dark:text-blue-400"></i>
                </div>
                <h3 class="ml-2 font-semibold text-gray-900 dark:text-white">Arrow Rests</h3>
              </div>
              <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Drop-away: Full arrow support</li>
                <li>• Whisker biscuit: Containment</li>
                <li>• Shoot-through: Minimal contact</li>
                <li>• Timing and adjustment</li>
              </ul>
            </div>

            <!-- Stabilizers -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div class="flex items-center mb-3">
                <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                  <i class="fas fa-balance-scale text-purple-600 dark:text-purple-400"></i>
                </div>
                <h3 class="ml-2 font-semibold text-gray-900 dark:text-white">Stabilizers</h3>
              </div>
              <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Length: 6" to 36" options</li>
                <li>• Weight distribution</li>
                <li>• Vibration dampening</li>
                <li>• Side rod configurations</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Equipment Selection Guidelines -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-clipboard-check text-green-600 dark:text-green-400 mr-3"></i>
            Selection Guidelines
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-3">
            
            <!-- For Target Archery -->
            <div class="border border-green-200 dark:border-green-800 rounded-lg p-6 bg-green-50 dark:bg-green-900/20">
              <h3 class="text-lg font-semibold text-green-800 dark:text-green-300 mb-4">
                <i class="fas fa-bullseye mr-2"></i>
                Target Archery
              </h3>
              
              <div class="space-y-3">
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">Arrow Components</h4>
                  <ul class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <li>• Small diameter shafts (.204"-.246")</li>
                    <li>• Light points (80-120 grains)</li>
                    <li>• Low profile vanes (2" length)</li>
                    <li>• Precision nocks (index preferred)</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">Bow Equipment</h4>
                  <ul class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <li>• Multi-pin or single pin sight</li>
                    <li>• Drop-away or shoot-through rest</li>
                    <li>• Long stabilizer (28-36")</li>
                    <li>• High-quality string materials</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- For Hunting -->
            <div class="border border-red-200 dark:border-red-800 rounded-lg p-6 bg-red-50 dark:bg-red-900/20">
              <h3 class="text-lg font-semibold text-red-800 dark:text-red-300 mb-4">
                <i class="fas fa-crosshairs mr-2"></i>
                Hunting
              </h3>
              
              <div class="space-y-3">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-1">Arrow Components</h4>
                  <ul class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <li>• Larger diameter shafts (.300"-.400")</li>
                    <li>• Heavy points (100-150+ grains)</li>
                    <li>• High profile vanes (3-4" length)</li>
                    <li>• Lighted nocks for tracking</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-1">Bow Equipment</h4>
                  <ul class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <li>• Multi-pin sight with fiber optics</li>
                    <li>• Containment rest (whisker biscuit)</li>
                    <li>• Shorter stabilizer (6-12")</li>
                    <li>• Durable string serving</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- For 3D Archery -->
            <div class="border border-blue-200 dark:border-blue-800 rounded-lg p-6 bg-blue-50 dark:bg-blue-900/20">
              <h3 class="text-lg font-semibold text-blue-800 dark:text-blue-300 mb-4">
                <i class="fas fa-mountain mr-2"></i>
                3D Archery
              </h3>
              
              <div class="space-y-3">
                <div>
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-1">Arrow Components</h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <li>• Medium diameter shafts (.244"-.300")</li>
                    <li>• Moderate points (100-125 grains)</li>
                    <li>• Medium profile vanes (2.5-3")</li>
                    <li>• Bullet or field points</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-1">Bow Equipment</h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <li>• Single pin adjustable sight</li>
                    <li>• Drop-away or hybrid rest</li>
                    <li>• Medium stabilizer (12-20")</li>
                    <li>• Weather-resistant components</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Equipment Maintenance -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-tools text-orange-600 dark:text-orange-400 mr-3"></i>
            Equipment Maintenance
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            
            <!-- Regular Maintenance -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Regular Maintenance Schedule
              </h3>
              
              <div class="space-y-4">
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">
                    <i class="fas fa-calendar-day mr-2"></i>
                    Before Each Session
                  </h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-400 space-y-1">
                    <li>• Check arrow condition and straightness</li>
                    <li>• Inspect fletching for damage</li>
                    <li>• Verify nock fit and condition</li>
                    <li>• Check sight alignment</li>
                  </ul>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-calendar-week mr-2"></i>
                    Weekly/Monthly
                  </h4>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <li>• Clean arrow shafts and points</li>
                    <li>• Check rest alignment and wear</li>
                    <li>• Inspect string and serving</li>
                    <li>• Tighten sight and rest bolts</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Replacement Guidelines -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Replacement Guidelines
              </h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Replace Immediately
                  </h4>
                  <ul class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <li>• Bent or cracked arrows</li>
                    <li>• Damaged fletching or nocks</li>
                    <li>• Loose inserts or points</li>
                    <li>• Frayed string serving</li>
                  </ul>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-clock mr-2"></i>
                    Replace Periodically
                  </h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <li>• Strings: Every 1-2 years</li>
                    <li>• Rest components: As needed</li>
                    <li>• Sight pins: When worn</li>
                    <li>• Stabilizer dampeners: Annually</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Equipment Tracking Link -->
        <div class="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6 text-center">
          <h3 class="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-2">
            Track Your Equipment
          </h3>
          <p class="text-blue-700 dark:text-blue-300 mb-4">
            Use our equipment management system to track specifications, maintenance, and performance of all your archery gear.
          </p>
          <div class="flex justify-center space-x-4">
            <NuxtLink
              to="/my-setup"
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-cog mr-2"></i>
              Manage Equipment
            </NuxtLink>
            <NuxtLink
              to="/database"
              class="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-database mr-2"></i>
              Browse Database
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Page metadata
definePageMeta({
  middleware: ['auth-check'],
  layout: 'default'
})

useHead({
  title: 'Equipment Guide - Archery Tools',
  meta: [
    { name: 'description', content: 'Comprehensive guide to archery equipment including arrow components, bow accessories, selection guidelines, and maintenance tips.' }
  ]
})
</script>

<style scoped>
/* Component specific styles */
</style>