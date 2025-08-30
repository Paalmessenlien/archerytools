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
          <span class="text-gray-900 dark:text-white">Wood Arrows</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Traditional Wood Arrows
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Comprehensive technical analysis of wooden arrow shafts for traditional and modern archery
        </p>
      </div>

      <!-- Overview -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
        <div class="flex items-center mb-4">
          <div class="p-2 bg-amber-100 dark:bg-amber-900 rounded-lg">
            <i class="fas fa-tree text-amber-600 dark:text-amber-400 text-xl"></i>
          </div>
          <div class="ml-3">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">The Science of Wood Arrows</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">Understanding material properties for optimal performance</p>
          </div>
        </div>
        
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Wood arrows represent thousands of years of archery evolution. Modern understanding of material science 
          allows us to select optimal wood species and specifications for any shooting application, from target 
          accuracy to big-game hunting effectiveness.
        </p>

        <div class="grid gap-4 md:grid-cols-3">
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div class="flex items-center mb-2">
              <i class="fas fa-atom text-blue-600 dark:text-blue-400 mr-2"></i>
              <h3 class="font-medium text-blue-900 dark:text-blue-300">Material Science</h3>
            </div>
            <p class="text-sm text-blue-700 dark:text-blue-400">
              Modulus of elasticity, density, and grain structure determine performance characteristics
            </p>
          </div>
          
          <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
            <div class="flex items-center mb-2">
              <i class="fas fa-balance-scale text-green-600 dark:text-green-400 mr-2"></i>
              <h3 class="font-medium text-green-900 dark:text-green-300">Dynamic Spine</h3>
            </div>
            <p class="text-sm text-green-700 dark:text-green-400">
              Real-world arrow behavior differs from static measurements - tuning is critical
            </p>
          </div>
          
          <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
            <div class="flex items-center mb-2">
              <i class="fas fa-leaf text-purple-600 dark:text-purple-400 mr-2"></i>
              <h3 class="font-medium text-purple-900 dark:text-purple-300">Species Selection</h3>
            </div>
            <p class="text-sm text-purple-700 dark:text-purple-400">
              Each wood species offers unique advantages for specific archery applications
            </p>
          </div>
        </div>
      </div>

      <!-- Wood Species Analysis -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-seedling text-green-600 mr-3"></i>
          Wood Species Deep Analysis
        </h2>

        <div class="space-y-8">
          <!-- Port Orford Cedar -->
          <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
            <div class="flex items-start mb-4">
              <div class="flex-shrink-0 p-3 bg-amber-100 dark:bg-amber-900 rounded-lg">
                <i class="fas fa-crown text-amber-600 dark:text-amber-400 text-xl"></i>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Port Orford Cedar (POC)
                </h3>
                <p class="text-sm text-amber-700 dark:text-amber-400 mb-3 font-medium">
                  The Traditional Standard - Gold standard benchmark for wooden shafts
                </p>
                
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                  Port Orford Cedar has long been considered the gold standard for wooden shafts. It offers 
                  straight grain, good elasticity, and an excellent weight-to-spine ratio, enabling consistent 
                  shafts with a distinctive pleasant aroma.
                </p>
                
                <div class="grid gap-4 md:grid-cols-2">
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Performance Characteristics</h4>
                    <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <li>• Light to medium weight for balanced performance</li>
                      <li>• Excellent spine consistency across matched sets</li>
                      <li>• Easy to straighten if bent during use</li>
                      <li>• Versatile for both target and hunting applications</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Considerations</h4>
                    <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <li>• Less durable than Douglas fir or ash</li>
                      <li>• Can be damaged on hard impacts</li>
                      <li>• Supply challenges affect quality consistency</li>
                      <li>• Premium pricing for top-quality stock</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sitka Spruce -->
          <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
            <div class="flex items-start mb-4">
              <div class="flex-shrink-0 p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <i class="fas fa-feather text-green-600 dark:text-green-400 text-xl"></i>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Sitka Spruce
                </h3>
                <p class="text-sm text-green-700 dark:text-green-400 mb-3 font-medium">
                  The Lightweight Performance King - Highest strength-to-weight ratio
                </p>
                
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                  Renowned for the highest strength-to-weight ratio of any wood, historically used for aircraft 
                  frames. Generally lighter than POC, yielding higher speed and flatter trajectory—excellent 
                  for target and 3D shooting at varied distances.
                </p>
                
                <div class="grid gap-4 md:grid-cols-2">
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Ideal Applications</h4>
                    <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <li>• Target archery requiring flat trajectory</li>
                      <li>• 3D shooting at varied distances</li>
                      <li>• High FOC hunting arrows (light shaft + heavy point)</li>
                      <li>• Speed-critical applications</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Technical Advantages</h4>
                    <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <li>• Superior strength-to-weight ratio</li>
                      <li>• Resilient fiber structure resists splitting</li>
                      <li>• Enables heavier points without excessive total weight</li>
                      <li>• Historical aerospace-grade material</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Douglas Fir -->
          <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
            <div class="flex items-start mb-4">
              <div class="flex-shrink-0 p-3 bg-red-100 dark:bg-red-900 rounded-lg">
                <i class="fas fa-mountain text-red-600 dark:text-red-400 text-xl"></i>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Douglas Fir
                </h3>
                <p class="text-sm text-red-700 dark:text-red-400 mb-3 font-medium">
                  The Hard-Hitting Hunting Specialist - Maximum penetration power
                </p>
                
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                  Dense, heavy, and robust with striking grain patterns. A Douglas fir shaft averages 75-100 
                  grains heavier than equivalently spined POC, delivering superior penetration through bone 
                  and thick tissue—ideal for big game hunting.
                </p>
                
                <div class="grid gap-4 md:grid-cols-2">
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Hunting Advantages</h4>
                    <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <li>• 75-100 grains heavier than POC for penetration</li>
                      <li>• Superior bone-breaking capability</li>
                      <li>• Excellent for big game hunting</li>
                      <li>• Durable construction for repeated use</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Trade-offs</h4>
                    <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <li>• Lower speed due to increased mass</li>
                      <li>• More arced trajectory at distance</li>
                      <li>• Harder to straighten than lighter woods</li>
                      <li>• Requires higher draw weights for optimal performance</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Pine Varieties -->
          <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
            <div class="flex items-start mb-4">
              <div class="flex-shrink-0 p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <i class="fas fa-tools text-blue-600 dark:text-blue-400 text-xl"></i>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Pine Varieties (Lodgepole, Scots, White)
                </h3>
                <p class="text-sm text-blue-700 dark:text-blue-400 mb-3 font-medium">
                  The Versatile Workhorse - Reliable all-around performance
                </p>
                
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                  Pine species provide versatile, often more affordable options that fall between POC and 
                  Douglas fir in mass. Scots pine offers good balance of durability and weight, while 
                  Lodgepole and White pine provide reliable training and general hunting performance.
                </p>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-900 dark:text-blue-300 mb-2">Species Comparison</h4>
                  <div class="grid gap-3 md:grid-cols-3">
                    <div class="text-center">
                      <div class="text-sm font-medium text-blue-800 dark:text-blue-200">Lodgepole Pine</div>
                      <div class="text-xs text-blue-600 dark:text-blue-400">Straight grain, consistent</div>
                    </div>
                    <div class="text-center">
                      <div class="text-sm font-medium text-blue-800 dark:text-blue-200">Scots Pine</div>
                      <div class="text-xs text-blue-600 dark:text-blue-400">Denser, more durable</div>
                    </div>
                    <div class="text-center">
                      <div class="text-sm font-medium text-blue-800 dark:text-blue-200">White Pine</div>
                      <div class="text-xs text-blue-600 dark:text-blue-400">Softer, budget-friendly</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Ash -->
          <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
            <div class="flex items-start mb-4">
              <div class="flex-shrink-0 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <i class="fas fa-shield-alt text-gray-600 dark:text-gray-400 text-xl"></i>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Ash
                </h3>
                <p class="text-sm text-gray-700 dark:text-gray-400 mb-3 font-medium">
                  The Indomitable War Arrow - Maximum durability and impact
                </p>
                
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                  A hardwood historically used for war arrows due to extreme durability and high mass. 
                  The same wood used for baseball bats and tool handles, reflecting its ability to absorb 
                  heavy impacts while delivering tremendous kinetic energy.
                </p>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-900 dark:text-yellow-300 mb-2">
                    <i class="fas fa-exclamation-triangle text-yellow-600 mr-2"></i>
                    Specialized Applications
                  </h4>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400">
                    Best suited for high draw-weight traditional bows (warbows) or scenarios where maximum 
                    durability is paramount. Requires strong bows and experienced archers.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Bamboo -->
          <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
            <div class="flex items-start mb-4">
              <div class="flex-shrink-0 p-3 bg-emerald-100 dark:bg-emerald-900 rounded-lg">
                <i class="fas fa-spa text-emerald-600 dark:text-emerald-400 text-xl"></i>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Bamboo
                </h3>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-3 font-medium">
                  The Natural Composite - Centuries of proven performance
                </p>
                
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                  Technically a grass, bamboo has been used for arrows for centuries. Its fibrous, nodal 
                  structure creates a natural composite with remarkable strength, lightness, and spring. 
                  Naturally tapered construction provides unique ballistic characteristics.
                </p>
                
                <div class="bg-emerald-50 dark:bg-emerald-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-emerald-900 dark:text-emerald-300 mb-2">Unique Properties</h4>
                  <div class="text-sm text-emerald-700 dark:text-emerald-400 space-y-1">
                    <div>• Natural composite fiber structure</div>
                    <div>• Inherent taper from base to tip</div>
                    <div>• Exceptional strength-to-weight ratio</div>
                    <div>• Historical significance in Asian archery</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Technical Specifications Tables -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-table text-blue-600 mr-3"></i>
          Technical Specifications
        </h2>
        
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Unlike carbon and aluminum arrows, wooden shafts vary naturally in density and properties. 
          The following tables provide estimated GPI (Grains Per Inch) ranges to standardize comparisons 
          across species and sizes.
        </p>

        <!-- Species Selector -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Wood Species:
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="species in woodSpecies"
              :key="species.id"
              @click="selectedSpecies = species.id"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                selectedSpecies === species.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              ]"
            >
              {{ species.name }}
            </button>
          </div>
        </div>

        <!-- Specification Table -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Spine Rating (lb)
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Diameter (in)
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Typical Length (in)
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Mass Range (gr)
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Est. GPI Range
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="spec in getSelectedSpecifications()" :key="`${spec.spine}-${spec.diameter}`"
                  class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {{ spec.spine }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  {{ spec.diameter }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  {{ spec.length }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  {{ spec.mass_range }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  {{ spec.gpi_range }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
          <div class="flex items-start">
            <i class="fas fa-info-circle text-yellow-600 dark:text-yellow-400 mr-2 mt-1"></i>
            <div class="text-sm text-yellow-700 dark:text-yellow-400">
              <strong>Note:</strong> GPI ranges are estimates based on typical shaft weights. Individual arrows 
              may vary due to natural wood density variations. Weight-matched dozens are recommended for consistency.
            </div>
          </div>
        </div>
      </div>

      <!-- Selection Methodology -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-crosshairs text-purple-600 mr-3"></i>
          Advanced Selection Methodology
        </h2>

        <div class="space-y-6">
          <!-- Dynamic vs Static Spine -->
          <div class="border-l-4 border-blue-500 pl-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Understanding Dynamic vs Static Spine
            </h3>
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Static spine measurement provides standardized comparison, but dynamic spine determines real-world 
              performance. Traditional bows especially require understanding of how arrows flex during acceleration 
              and the archer's paradox.
            </p>
            
            <div class="grid gap-4 md:grid-cols-2">
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h4 class="font-medium text-blue-900 dark:text-blue-300 mb-2">Static Spine Factors</h4>
                <ul class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                  <li>• Wood species and grain quality</li>
                  <li>• Shaft diameter and wall thickness</li>
                  <li>• Moisture content and age</li>
                  <li>• Manufacturing consistency</li>
                </ul>
              </div>
              
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 class="font-medium text-green-900 dark:text-green-300 mb-2">Dynamic Spine Factors</h4>
                <ul class="text-sm text-green-700 dark:text-green-400 space-y-1">
                  <li>• Bow draw weight and efficiency</li>
                  <li>• Arrow length (BOP length)</li>
                  <li>• Point weight and distribution</li>
                  <li>• String type and release style</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Selection Strategy -->
          <div class="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Professional Selection Strategy
            </h3>
            
            <div class="space-y-4">
              <div class="flex items-start">
                <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  1
                </div>
                <div class="ml-4">
                  <h4 class="font-medium text-gray-900 dark:text-white">Define Purpose</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Target/3D: prioritize speed (Sitka Spruce). Hunting: prioritize penetration (Douglas Fir, Ash).
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  2
                </div>
                <div class="ml-4">
                  <h4 class="font-medium text-gray-900 dark:text-white">Calculate Dynamic Spine</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Use dynamic spine calculators (Stu Miller methodology) for precise bow-arrow matching.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  3
                </div>
                <div class="ml-4">
                  <h4 class="font-medium text-gray-900 dark:text-white">Test and Tune</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Buy test sets (adjacent spine groups), bare shaft tune for empirical validation.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Maintenance and Care -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-hand-holding-heart text-red-600 mr-3"></i>
          Wood Arrow Care and Maintenance
        </h2>

        <div class="grid gap-6 md:grid-cols-2">
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Regular Maintenance</h3>
            <div class="space-y-3">
              <div class="flex items-start">
                <i class="fas fa-search text-blue-600 dark:text-blue-400 mr-3 mt-1"></i>
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Pre-Shoot Inspection</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Check for cracks, splinters, or grain separation before each use.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <i class="fas fa-ruler text-green-600 dark:text-green-400 mr-3 mt-1"></i>
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Straightness Check</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Roll arrows on flat surface to identify bends. Minor bends can be straightened.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <i class="fas fa-tint text-purple-600 dark:text-purple-400 mr-3 mt-1"></i>
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Moisture Protection</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Store in dry conditions. Consider sealing with appropriate wood finishes.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Professional Tips</h3>
            <div class="space-y-3">
              <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3">
                <h4 class="font-medium text-amber-900 dark:text-amber-300 mb-1">Straightening Technique</h4>
                <p class="text-xs text-amber-700 dark:text-amber-400">
                  Gentle heat and pressure. POC straightens easily; Douglas fir requires more care.
                </p>
              </div>
              
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                <h4 class="font-medium text-green-900 dark:text-green-300 mb-1">Weight Matching</h4>
                <p class="text-xs text-green-700 dark:text-green-400">
                  Professional sets are weight-matched within ±10 grains for consistency.
                </p>
              </div>
              
              <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                <h4 class="font-medium text-red-900 dark:text-red-300 mb-1">Safety Replacement</h4>
                <p class="text-xs text-red-700 dark:text-red-400">
                  Replace arrows with any cracks, deep gouges, or grain separation immediately.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Calculator Integration -->
      <div class="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          <i class="fas fa-calculator text-blue-600 mr-2"></i>
          Find Your Perfect Wood Arrow
        </h2>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          Ready to select wood arrows for your setup? Our calculator includes comprehensive wood arrow 
          specifications and will recommend the optimal species and spine for your bow configuration.
        </p>
        <NuxtLink
          to="/calculator"
          class="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          <i class="fas fa-bow-arrow mr-2"></i>
          Open Arrow Calculator
        </NuxtLink>
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

// Reactive data
const selectedSpecies = ref('poc')

// Wood species data
const woodSpecies = ref([
  { id: 'poc', name: 'Port Orford Cedar' },
  { id: 'sitka', name: 'Sitka Spruce' },
  { id: 'douglas', name: 'Douglas Fir' },
  { id: 'pine', name: 'Pine Varieties' },
  { id: 'ash', name: 'Ash' },
  { id: 'bamboo', name: 'Bamboo' }
])

// Technical specifications data based on woodarrowdescriptions_en.md
const specifications = ref({
  poc: [
    { spine: '25–30', diameter: '5/16', length: '32', mass_range: '280–360', gpi_range: '8.8–11.3' },
    { spine: '30–35', diameter: '5/16', length: '32', mass_range: '300–380', gpi_range: '9.4–11.9' },
    { spine: '35–40', diameter: '5/16', length: '32', mass_range: '320–400', gpi_range: '10.0–12.5' },
    { spine: '40–45', diameter: '5/16', length: '32', mass_range: '340–420', gpi_range: '10.6–13.1' },
    { spine: '40–45', diameter: '11/32', length: '32–33', mass_range: '350–430', gpi_range: '10.6–13.4' },
    { spine: '45–50', diameter: '11/32', length: '32–33', mass_range: '370–450', gpi_range: '11.2–14.1' },
    { spine: '50–55', diameter: '11/32', length: '32–33', mass_range: '390–470', gpi_range: '11.8–14.7' },
    { spine: '55–60', diameter: '11/32', length: '32–33', mass_range: '410–490', gpi_range: '12.4–15.3' },
    { spine: '60–65', diameter: '11/32', length: '32–33', mass_range: '430–510', gpi_range: '13.0–15.9' },
    { spine: '65–70', diameter: '11/32', length: '32–33', mass_range: '450–530', gpi_range: '13.6–16.6' },
    { spine: '50–55', diameter: '23/64', length: '32–33', mass_range: '410–490', gpi_range: '12.4–15.3' },
    { spine: '55–60', diameter: '23/64', length: '32–33', mass_range: '430–510', gpi_range: '13.0–15.9' },
    { spine: '60–65', diameter: '23/64', length: '32–33', mass_range: '450–530', gpi_range: '13.6–16.6' },
    { spine: '65–70', diameter: '23/64', length: '32–33', mass_range: '470–550', gpi_range: '14.2–17.2' },
    { spine: '70–75', diameter: '23/64', length: '32–33', mass_range: '490–570', gpi_range: '14.8–17.8' },
    { spine: '75–80', diameter: '23/64', length: '32–33', mass_range: '510–590', gpi_range: '15.5–18.4' }
  ],
  sitka: [
    { spine: '35–39', diameter: '11/32', length: '34', mass_range: '340–390', gpi_range: '10.0–11.5' },
    { spine: '40–44', diameter: '11/32', length: '34', mass_range: '360–410', gpi_range: '10.6–12.1' },
    { spine: '45–49', diameter: '11/32', length: '34', mass_range: '380–430', gpi_range: '11.2–12.6' },
    { spine: '50–54', diameter: '11/32', length: '34', mass_range: '400–450', gpi_range: '11.8–13.2' },
    { spine: '55–59', diameter: '11/32', length: '34', mass_range: '420–470', gpi_range: '12.4–13.8' },
    { spine: '60–64', diameter: '11/32', length: '34', mass_range: '440–490', gpi_range: '12.9–14.4' },
    { spine: '45–49', diameter: '23/64', length: '34', mass_range: '400–450', gpi_range: '11.8–13.2' },
    { spine: '50–54', diameter: '23/64', length: '34', mass_range: '420–470', gpi_range: '12.4–13.8' },
    { spine: '55–59', diameter: '23/64', length: '34', mass_range: '440–490', gpi_range: '12.9–14.4' },
    { spine: '60–64', diameter: '23/64', length: '34', mass_range: '460–510', gpi_range: '13.5–15.0' },
    { spine: '65–69', diameter: '23/64', length: '34', mass_range: '480–530', gpi_range: '14.1–15.6' },
    { spine: '70–74', diameter: '23/64', length: '34', mass_range: '500–550', gpi_range: '14.7–16.2' },
    { spine: '75–79', diameter: '23/64', length: '34', mass_range: '520–570', gpi_range: '15.3–16.8' }
  ],
  douglas: [
    { spine: '30–35', diameter: '11/32', length: '32', mass_range: '330–380', gpi_range: '10.3–11.9' },
    { spine: '35–40', diameter: '11/32', length: '32', mass_range: '340–380', gpi_range: '10.6–11.9' },
    { spine: '40–45', diameter: '11/32', length: '32', mass_range: '350–400', gpi_range: '10.9–12.5' },
    { spine: '45–50', diameter: '11/32', length: '32', mass_range: '360–410', gpi_range: '11.3–12.8' },
    { spine: '50–55', diameter: '11/32', length: '32', mass_range: '370–420', gpi_range: '11.6–13.1' },
    { spine: '55–60', diameter: '11/32', length: '32', mass_range: '380–430', gpi_range: '11.9–13.4' },
    { spine: '60–65', diameter: '11/32', length: '32', mass_range: '400–450', gpi_range: '12.5–14.1' },
    { spine: '65–70', diameter: '11/32', length: '32', mass_range: '410–460', gpi_range: '12.8–14.4' },
    { spine: '70–75', diameter: '11/32', length: '32', mass_range: '430–480', gpi_range: '13.4–15.0' },
    { spine: '75–80', diameter: '11/32', length: '32', mass_range: '440–490', gpi_range: '13.8–15.3' },
    { spine: '80–85', diameter: '11/32', length: '32', mass_range: '470–520', gpi_range: '14.7–16.3' },
    { spine: '85–90', diameter: '11/32', length: '32', mass_range: '480–530', gpi_range: '15.0–16.6' },
    { spine: '90–95', diameter: '11/32', length: '32', mass_range: '500–540', gpi_range: '15.6–16.9' },
    { spine: '95–100', diameter: '11/32', length: '32', mass_range: '510–550', gpi_range: '15.9–17.2' }
  ],
  pine: [
    { spine: '<30', diameter: '5/16', length: '30–32', mass_range: '300–360', gpi_range: '9.4–12.0' },
    { spine: '30–35', diameter: '5/16', length: '32', mass_range: '320–380', gpi_range: '10.0–11.9' },
    { spine: '35–40', diameter: '5/16', length: '32', mass_range: '340–400', gpi_range: '10.6–12.5' },
    { spine: '40–45', diameter: '5/16', length: '32', mass_range: '360–420', gpi_range: '11.3–13.1' },
    { spine: '45–50', diameter: '5/16', length: '32', mass_range: '380–440', gpi_range: '11.9–13.8' },
    { spine: '40–45', diameter: '11/32', length: '32', mass_range: '370–430', gpi_range: '11.6–13.4' },
    { spine: '45–50', diameter: '11/32', length: '32', mass_range: '390–450', gpi_range: '12.2–14.1' },
    { spine: '50–55', diameter: '11/32', length: '32', mass_range: '410–470', gpi_range: '12.8–14.7' },
    { spine: '55–60', diameter: '11/32', length: '32', mass_range: '430–490', gpi_range: '13.4–15.3' },
    { spine: '60–65', diameter: '11/32', length: '32', mass_range: '450–510', gpi_range: '14.1–15.9' },
    { spine: '65–70', diameter: '11/32', length: '32', mass_range: '470–530', gpi_range: '14.7–16.6' },
    { spine: '70–75', diameter: '11/32', length: '32', mass_range: '490–550', gpi_range: '15.3–17.2' },
    { spine: '80+', diameter: '11/32', length: '32', mass_range: '520+', gpi_range: '16.3+' },
    { spine: '65–70', diameter: '23/64', length: '32', mass_range: '480–540', gpi_range: '15.0–16.9' }
  ],
  ash: [
    { spine: '45–50', diameter: '11/32', length: '32', mass_range: '450–520', gpi_range: '14.1–16.3' },
    { spine: '50–55', diameter: '11/32', length: '32', mass_range: '470–540', gpi_range: '14.7–16.9' },
    { spine: '55–60', diameter: '11/32', length: '32', mass_range: '490–560', gpi_range: '15.3–17.5' },
    { spine: '60–65', diameter: '11/32', length: '32', mass_range: '510–580', gpi_range: '15.9–18.1' },
    { spine: '65–70', diameter: '11/32', length: '32', mass_range: '530–600', gpi_range: '16.6–18.8' },
    { spine: '70–75', diameter: '11/32', length: '32', mass_range: '550–620', gpi_range: '17.2–19.4' },
    { spine: '75–80', diameter: '11/32', length: '32', mass_range: '570–640', gpi_range: '17.8–20.0' }
  ],
  bamboo: [
    { spine: '<40', diameter: '7.0–7.5mm', length: '33', mass_range: '250–350', gpi_range: '7.6–10.6' },
    { spine: '45–60', diameter: '7.5–8.0mm', length: '33', mass_range: '350–480', gpi_range: '10.6–14.5' },
    { spine: '65+', diameter: '8.0–8.7mm+', length: '33', mass_range: '480–600+', gpi_range: '14.5–18.2+' }
  ]
})

// Methods
const getSelectedSpecifications = () => {
  return specifications.value[selectedSpecies.value] || []
}
</script>

<style scoped>
/* Component-specific styles for wood arrow page */
</style>