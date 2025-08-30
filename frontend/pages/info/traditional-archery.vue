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
          <span class="text-gray-900 dark:text-white">Traditional Archery</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Traditional Archery Guide
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Understanding archer's paradox, center shot, and traditional bow tuning techniques
        </p>
      </div>

      <!-- Wood Arrow Calculator Link -->
      <div class="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-lg border border-amber-200 dark:border-amber-800 p-6 mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-amber-800 dark:text-amber-200 mb-2">
              <i class="fas fa-tree mr-2"></i>
              Traditional Wood Arrow Calculator
            </h2>
            <p class="text-amber-700 dark:text-amber-300">
              Use our specialized calculator for traditional wood arrow spine calculations and species selection.
            </p>
          </div>
          <NuxtLink
            to="/calculator/wood"
            class="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-calculator mr-2"></i>
            Wood Calculator
          </NuxtLink>
        </div>
      </div>

      <div class="space-y-8">

        <!-- Historical Foundation -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-scroll text-amber-600 dark:text-amber-400 mr-3"></i>
            Historical Foundation & Scientific Discovery
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">The Archer's Paradox Discovery</h3>
              
              <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 mb-4">
                <h4 class="font-medium text-amber-800 dark:text-amber-300 mb-2">
                  <i class="fas fa-camera mr-2"></i>
                  Clarence N. Hickman (1930s)
                </h4>
                <p class="text-sm text-amber-700 dark:text-amber-400 mb-2">
                  Using revolutionary slow-motion photography, Hickman first documented how arrows literally "bend around" the bow riser during traditional archery shots. This discovery explained why arrows could hit targets despite appearing to point away from them.
                </p>
                <p class="text-xs text-amber-600 dark:text-amber-500 italic">
                  "The arrow paradox: How an arrow can hit what it's not pointing at"
                </p>
              </div>
              
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Scientific Validation</h4>
                <p class="text-sm text-blue-700 dark:text-blue-400">
                  Modern high-speed cameras confirm Hickman's findings: arrows flex up to 6 inches laterally during the first few feet of flight from traditional bows. This phenomenon requires precise spine matching for accuracy.
                </p>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Traditional vs. Modern Archery</h3>
              
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Traditional Approach</h4>
                  <ul class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <li>• Built for simplicity and reliability</li>
                    <li>• No arrow rest - shoots off the hand</li>
                    <li>• Inherent archer's paradox challenges</li>
                    <li>• Requires expert spine matching</li>
                  </ul>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">Modern Evolution</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <li>• Center shot risers eliminate paradox</li>
                    <li>• Advanced arrow rest systems</li>
                    <li>• Forgiving spine tolerances</li>
                    <li>• Precision engineering solutions</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Understanding Center Shot -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-crosshairs text-red-600 dark:text-red-400 mr-3"></i>
            Understanding Center Shot in Traditional Archery
          </h2>
          
          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
            <h3 class="font-medium text-red-800 dark:text-red-300 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Critical Concept for Traditional Archers
            </h3>
            <p class="text-sm text-red-700 dark:text-red-400">
              Center shot is THE most important factor affecting arrow spine requirements in traditional archery. Unlike modern compound bows with center shot designs, traditional bows force arrows to flex significantly around the riser.
            </p>
          </div>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Center Shot Measurements</h3>
              
              <div class="space-y-4">
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-ruler mr-2"></i>
                    How to Measure
                  </h4>
                  <ol class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <li>1. <strong>Nock arrow</strong> at normal nocking point</li>
                    <li>2. <strong>View from above</strong> looking down the bow</li>
                    <li>3. <strong>Measure distance</strong> from arrow shaft to bow centerline</li>
                    <li>4. <strong>Record measurement</strong> for spine calculations</li>
                  </ol>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Typical Measurements</h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p><strong>English Longbows:</strong> 1/4" to 3/8" off-center</p>
                    <p><strong>American Longbows:</strong> 1/8" to 1/4" off-center</p>
                    <p><strong>Traditional Recurves:</strong> 0" to 1/8" past center</p>
                    <p><strong>Modern Recurves:</strong> 1/8" to 1/4" past center</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Spine Impact by Center Shot</h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-arrow-left mr-2"></i>
                    Off-Center (Before Center)
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p><strong>Effect:</strong> Maximum arrow flex required</p>
                    <p><strong>Spine Adjustment:</strong> Use 5-15# weaker than bow weight</p>
                    <p><strong>Example:</strong> 50# bow → 35-45# spine arrows</p>
                    <p class="text-xs italic">Common in English longbows</p>
                  </div>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    <i class="fas fa-bullseye mr-2"></i>
                    True Center Shot
                  </h4>
                  <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <p><strong>Effect:</strong> Minimal arrow flex needed</p>
                    <p><strong>Spine Adjustment:</strong> Close to bow weight</p>
                    <p><strong>Example:</strong> 50# bow → 45-55# spine arrows</p>
                    <p class="text-xs italic">Modern compound bow standard</p>
                  </div>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-arrow-right mr-2"></i>
                    Cut Past Center
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p><strong>Effect:</strong> Arrow path slightly inward</p>
                    <p><strong>Spine Adjustment:</strong> May need slightly stiffer</p>
                    <p><strong>Example:</strong> 50# bow → 50-60# spine arrows</p>
                    <p class="text-xs italic">Olympic recurve configuration</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- The Archer's Paradox Explained -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-magic text-purple-600 dark:text-purple-400 mr-3"></i>
            The Archer's Paradox Explained
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-3">
            <div class="lg:col-span-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">The Physics of Arrow Flight</h3>
              
              <div class="space-y-4">
                <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-wave-square mr-2"></i>
                    The Flex Cycle
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-2">
                    <p><strong>Initial Flex:</strong> Arrow bends around riser (left for RH archer)</p>
                    <p><strong>Recovery:</strong> Arrow straightens and flexes opposite direction</p>
                    <p><strong>Oscillation:</strong> Continues flexing in diminishing waves</p>
                    <p><strong>Stabilization:</strong> Fletching dampens flex, arrow flies straight</p>
                  </div>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">Why Proper Spine Matters</h4>
                  <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <p><strong>Too Stiff:</strong> Arrow can't flex enough → impacts right (RH archer)</p>
                    <p><strong>Too Weak:</strong> Arrow flexes too much → impacts left (RH archer)</p>
                    <p><strong>Just Right:</strong> Arrow clears riser perfectly → straight flight</p>
                    <p class="font-medium mt-2">Perfect spine = arrow hits target despite initial misalignment!</p>
                  </div>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    <i class="fas fa-clock mr-2"></i>
                    Timing is Everything
                  </h4>
                  <p class="text-sm text-green-700 dark:text-green-400">
                    The arrow must complete its flex cycle and return to straight flight before the fletching clears the riser. This timing relationship determines the optimal arrow spine for each specific bow and shooting style combination.
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Visual Flight Path</h3>
              
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4">
                <div class="text-center">
                  <h4 class="font-medium text-gray-800 dark:text-gray-300 mb-3">Arrow Flex Sequence</h4>
                  <div class="space-y-2 text-xs text-gray-600 dark:text-gray-400">
                    <div class="bg-red-100 dark:bg-red-900/30 rounded p-2">
                      <strong>Release:</strong> Arrow appears to point left
                    </div>
                    <div class="bg-yellow-100 dark:bg-yellow-900/30 rounded p-2">
                      <strong>0-2 feet:</strong> Bends around riser (right)
                    </div>
                    <div class="bg-green-100 dark:bg-green-900/30 rounded p-2">
                      <strong>2-6 feet:</strong> Oscillates left-right
                    </div>
                    <div class="bg-blue-100 dark:bg-blue-900/30 rounded p-2">
                      <strong>6+ feet:</strong> Straight flight to target
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Key Insight</h4>
                <p class="text-sm text-orange-700 dark:text-orange-400">
                  This is why traditional archers can't simply "aim directly" at targets. The bow's design creates a system where proper arrow spine compensates for the initial misalignment.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Traditional Bow Spine Calculation -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-calculator text-blue-600 dark:text-blue-400 mr-3"></i>
            Traditional Bow Spine Calculation
          </h2>
          
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
            <h3 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
              <i class="fas fa-info-circle mr-2"></i>
              Traditional Spine Formula Difference
            </h3>
            <p class="text-sm text-blue-700 dark:text-blue-400">
              Traditional bows require different spine calculations than modern center shot bows due to the archer's paradox. Standard spine charts assume center shot configuration and must be adjusted for traditional archery.
            </p>
          </div>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Traditional Longbow Formula</h3>
              
              <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 mb-4">
                <h4 class="font-medium text-amber-800 dark:text-amber-300 mb-2">Adjusted Base Formula</h4>
                <div class="text-center">
                  <div class="text-lg font-mono text-amber-600 dark:text-amber-400 mb-2">
                    Traditional Spine = Bow Weight - (5 to 15)
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Weaker spine needed due to off-center shot
                  </p>
                </div>
              </div>
              
              <div class="space-y-3">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <h5 class="font-medium text-red-800 dark:text-red-300 mb-1">High Off-Center (3/8")</h5>
                  <p class="text-sm text-red-700 dark:text-red-400">50# bow → 35-40# spine arrows</p>
                </div>
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3">
                  <h5 class="font-medium text-orange-800 dark:text-orange-300 mb-1">Moderate Off-Center (1/4")</h5>
                  <p class="text-sm text-orange-700 dark:text-orange-400">50# bow → 40-45# spine arrows</p>
                </div>
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3">
                  <h5 class="font-medium text-yellow-800 dark:text-yellow-300 mb-1">Slight Off-Center (1/8")</h5>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400">50# bow → 45-50# spine arrows</p>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Additional Adjustments</h3>
              
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    <i class="fas fa-hand-paper mr-2"></i>
                    Release Style Impact
                  </h4>
                  <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <p><strong>Clean Release:</strong> Use calculated spine</p>
                    <p><strong>Side Pressure:</strong> Go 5# weaker</p>
                    <p><strong>Plucking String:</strong> Go 10# weaker</p>
                    <p class="text-xs italic">Poor form requires compensation</p>
                  </div>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-tree mr-2"></i>
                    Wood Arrow Considerations
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p><strong>Spine Variance:</strong> ±5-10# within same batch</p>
                    <p><strong>Humidity Effect:</strong> Spine changes with moisture</p>
                    <p><strong>Testing Required:</strong> Each batch needs verification</p>
                    <p class="text-xs italic">Less consistent than carbon arrows</p>
                  </div>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-tools mr-2"></i>
                    Adjustment Methods
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p><strong>Strike Plate:</strong> Build out to reduce paradox</p>
                    <p><strong>Point Weight:</strong> Heavier points weaken spine</p>
                    <p><strong>Arrow Length:</strong> Shorter arrows stiffen spine</p>
                    <p class="text-xs italic">Multiple tuning variables available</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Traditional Arrow Materials -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-tree text-green-600 dark:text-green-400 mr-3"></i>
            Traditional Arrow Materials
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Wood Arrow Characteristics</h3>
              
              <div class="space-y-4">
                <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-amber-800 dark:text-amber-300 mb-2">
                    <i class="fas fa-seedling mr-2"></i>
                    Wood Species Properties
                  </h4>
                  <div class="text-sm text-amber-700 dark:text-amber-400 space-y-1">
                    <p><strong>Cedar:</strong> Traditional choice, consistent grain</p>
                    <p><strong>Pine:</strong> Budget option, more variable spine</p>
                    <p><strong>Birch:</strong> Dense, heavier arrows</p>
                    <p><strong>Bamboo:</strong> Extremely consistent, premium choice</p>
                    <p><strong>Sitka Spruce:</strong> Light weight, target archery</p>
                    <p><strong>Douglas Fir:</strong> Strong, hunting applications</p>
                  </div>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Environmental Factors</h4>
                  <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <p><strong>Humidity:</strong> Can change spine by 5-10#</p>
                    <p><strong>Temperature:</strong> Cold stiffens, heat softens</p>
                    <p><strong>Storage:</strong> Keep in consistent environment</p>
                    <p><strong>Sealing:</strong> Proper finish prevents moisture</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Selection Guidelines</h3>
              
              <div class="space-y-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-search mr-2"></i>
                    Choosing Wood Arrows
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p>• <strong>Buy 2-3 singles</strong> in your calculated range</p>
                    <p>• <strong>Test spine response</strong> with bare shaft tuning</p>
                    <p>• <strong>Check grain matching</strong> within each batch</p>
                    <p>• <strong>Consider seasonal changes</strong> in performance</p>
                  </div>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-balance-scale mr-2"></i>
                    Quality Indicators
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p>• <strong>Straight grain:</strong> Parallel to shaft length</p>
                    <p>• <strong>Dense rings:</strong> Consistent annual growth</p>
                    <p>• <strong>Proper seal:</strong> Even finish coverage</p>
                    <p>• <strong>Weight matching:</strong> ±5 grains per dozen</p>
                  </div>
                </div>
                
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Avoid These Issues
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p>• Cross-grain patterns (weak spots)</p>
                    <p>• Visible knots or imperfections</p>
                    <p>• Inconsistent diameter along shaft</p>
                    <p>• Poor nock taper quality</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Traditional Tuning Methods -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-adjust text-orange-600 dark:text-orange-400 mr-3"></i>
            Traditional Tuning Methods
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Bare Shaft Tuning</h3>
              
              <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 mb-4">
                <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">
                  <i class="fas fa-target mr-2"></i>
                  The Gold Standard
                </h4>
                <p class="text-sm text-orange-700 dark:text-orange-400 mb-2">
                  Bare shaft tuning is essential for traditional archery. Shoot unfletched arrows alongside fletched ones to see true spine behavior without fletching compensation.
                </p>
              </div>
              
              <div class="space-y-3">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <h5 class="font-medium text-green-800 dark:text-green-300 mb-1">Procedure</h5>
                  <ol class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <li>1. Shoot fletched arrows, note group center</li>
                    <li>2. Shoot bare shafts from same distance</li>
                    <li>3. Compare impact points</li>
                    <li>4. Adjust spine/point weight accordingly</li>
                  </ol>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                  <h5 class="font-medium text-blue-800 dark:text-blue-300 mb-1">Reading Results</h5>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p><strong>Bare shaft right:</strong> Spine too stiff</p>
                    <p><strong>Bare shaft left:</strong> Spine too weak</p>
                    <p><strong>Same impact:</strong> Perfect spine match</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Advanced Adjustments</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-hammer mr-2"></i>
                    Strike Plate Modification
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p><strong>Build Out:</strong> Move arrow closer to center</p>
                    <p><strong>3/8" Change:</strong> Can use 10# stiffer spine</p>
                    <p><strong>Materials:</strong> Leather, rug rest, velcro</p>
                    <p><strong>Fine Tuning:</strong> Add layers gradually</p>
                  </div>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-weight-hanging mr-2"></i>
                    Point Weight Strategy
                  </h4>
                  <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <p><strong>Heavy Points:</strong> Weaken dynamic spine</p>
                    <p><strong>25gr Increase:</strong> Next weaker spine group</p>
                    <p><strong>Traditional Weights:</strong> 125-200 grains common</p>
                    <p><strong>FOC Target:</strong> 15-25% for traditional</p>
                  </div>
                </div>
                
                <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-teal-800 dark:text-teal-300 mb-2">
                    <i class="fas fa-crosshairs mr-2"></i>
                    Nocking Point Height
                  </h4>
                  <div class="text-sm text-teal-700 dark:text-teal-400 space-y-1">
                    <p><strong>High Nock:</strong> Arrow hits high, may need stiffer</p>
                    <p><strong>Low Nock:</strong> Arrow hits low, may need weaker</p>
                    <p><strong>Traditional Rule:</strong> 1/8" to 1/4" above square</p>
                    <p><strong>Fine Tuning:</strong> Adjust in 1/16" increments</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Common Traditional Archery Issues -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-exclamation-circle text-red-600 dark:text-red-400 mr-3"></i>
            Common Traditional Archery Issues
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Spine-Related Problems</h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-arrow-right mr-2"></i>
                    Arrows Hitting Right (RH Archer)
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p><strong>Cause:</strong> Arrows too stiff for center shot</p>
                    <p><strong>Solutions:</strong></p>
                    <p>• Try next weaker spine group</p>
                    <p>• Increase point weight by 25-50 grains</p>
                    <p>• Build out strike plate</p>
                    <p>• Check for side pressure in release</p>
                  </div>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-arrow-left mr-2"></i>
                    Arrows Hitting Left (RH Archer)
                  </h4>
                  <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <p><strong>Cause:</strong> Arrows too weak for setup</p>
                    <p><strong>Solutions:</strong></p>
                    <p>• Try next stiffer spine group</p>
                    <p>• Reduce point weight</p>
                    <p>• Shorten arrows if possible</p>
                    <p>• Check draw weight measurement</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Fletching Contact Issues</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-feather mr-2"></i>
                    Fletching Hitting Bow
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p><strong>Symptoms:</strong> Torn fletching, erratic flight</p>
                    <p><strong>Causes:</strong></p>
                    <p>• Spine too weak for center shot</p>
                    <p>• Nocking point too low</p>
                    <p>• Fletching too large/tall</p>
                    <p>• Poor arrow rest setup</p>
                  </div>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-tools mr-2"></i>
                    Correction Methods
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p>• Use stiffer spine arrows</p>
                    <p>• Raise nocking point slightly</p>
                    <p>• Switch to lower profile fletching</p>
                    <p>• Improve arrow rest clearance</p>
                    <p>• Check bow grip consistency</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Professional Traditional Shooting -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-medal text-gold-500 mr-3"></i>
            Professional Traditional Shooting
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-3">
            <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
              <h3 class="font-medium text-amber-800 dark:text-amber-300 mb-3">
                <i class="fas fa-graduation-cap mr-2"></i>
                Form Development
              </h3>
              <div class="text-sm text-amber-700 dark:text-amber-400 space-y-1">
                <p>• Consistent anchor point critical</p>
                <p>• Clean release without side pressure</p>
                <p>• Bow grip consistency affects spine</p>
                <p>• String walking for distance</p>
                <p>• Gap shooting techniques</p>
              </div>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-medium text-green-800 dark:text-green-300 mb-3">
                <i class="fas fa-bullseye mr-2"></i>
                Accuracy Factors
              </h3>
              <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                <p>• Perfect spine matching essential</p>
                <p>• Arrow weight consistency</p>
                <p>• Fletching orientation matters</p>
                <p>• Environmental compensation</p>
                <p>• Distance-specific tuning</p>
              </div>
            </div>
            
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-medium text-blue-800 dark:text-blue-300 mb-3">
                <i class="fas fa-trophy mr-2"></i>
                Competition Prep
              </h3>
              <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                <p>• Multiple spine groups for conditions</p>
                <p>• Weather backup arrows</p>
                <p>• Equipment redundancy</p>
                <p>• Pre-competition tuning checks</p>
                <p>• Distance-specific arrow sets</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Traditional Equipment Links -->
        <div class="bg-gradient-to-br from-green-50 to-amber-50 dark:from-green-900/20 dark:to-amber-900/20 rounded-lg border border-green-200 dark:border-green-800 p-6 text-center">
          <h3 class="text-xl font-semibold text-green-800 dark:text-green-200 mb-2">
            <i class="fas fa-bow-arrow mr-2"></i>
            Explore Traditional Archery Tools
          </h3>
          <p class="text-green-700 dark:text-green-300 mb-4">
            Use our specialized tools designed for traditional archery calculations and equipment management.
          </p>
          <div class="flex justify-center space-x-4">
            <NuxtLink
              to="/calculator/wood"
              class="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-tree mr-2"></i>
              Wood Calculator
            </NuxtLink>
            <NuxtLink
              to="/info/wood-arrows"
              class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-info-circle mr-2"></i>
              Wood Arrow Guide
            </NuxtLink>
            <NuxtLink
              to="/my-setup"
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-cog mr-2"></i>
              Equipment Setup
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
  title: 'Traditional Archery Guide - Archery Tools',
  meta: [
    { name: 'description', content: 'Comprehensive guide to traditional archery including archer\'s paradox, center shot considerations, wood arrow selection, and traditional bow tuning methods.' }
  ]
})
</script>

<style scoped>
/* Component specific styles */
</style>