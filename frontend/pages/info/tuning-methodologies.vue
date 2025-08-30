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
          <span class="text-gray-900 dark:text-white">Tuning Methodologies</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Professional Tuning Methodologies
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Comprehensive guide to dynamic spine concepts, scientific foundations, and advanced tuning techniques
        </p>
      </div>

      <!-- Interactive Tuning Link -->
      <div class="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6 mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-2">
              <i class="fas fa-play-circle mr-2"></i>
              Interactive Tuning Guides
            </h2>
            <p class="text-blue-700 dark:text-blue-300">
              Use our step-by-step interactive tuning guides with progress tracking and permanent history recording.
            </p>
          </div>
          <NuxtLink
            to="/tuning"
            class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-arrow-right mr-2"></i>
            Start Tuning
          </NuxtLink>
        </div>
      </div>

      <div class="space-y-8">

        <!-- Scientific Foundation -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-microscope text-blue-600 dark:text-blue-400 mr-3"></i>
            Scientific Foundation of Arrow Tuning
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Historical Research</h3>
              
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-4">
                <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                  <i class="fas fa-camera mr-2"></i>
                  Clarence N. Hickman (1930s)
                </h4>
                <p class="text-sm text-blue-700 dark:text-blue-400 mb-2">
                  First scientist to document the "archer's paradox" using slow-motion photography. His research revealed that arrows flex up to 6 inches laterally during initial flight, establishing the scientific foundation for spine tuning.
                </p>
                <p class="text-xs text-blue-600 dark:text-blue-500 italic">
                  Published in "Archery: The Technical Side" - still referenced today
                </p>
              </div>
              
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Modern Validation</h4>
                <p class="text-sm text-green-700 dark:text-green-400">
                  High-speed cameras and force sensors confirm that proper spine tuning is based on measurable physics principles, not guesswork. Modern research has quantified the relationship between spine deflection and accuracy.
                </p>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Physics of Arrow Flight</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-wave-square mr-2"></i>
                    Oscillation Mechanics
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p><strong>Initial Deflection:</strong> String force creates lateral bend</p>
                    <p><strong>Recovery Oscillation:</strong> Arrow straightens and overcorrects</p>
                    <p><strong>Dampening Phase:</strong> Fletching reduces oscillations</p>
                    <p><strong>Stabilization:</strong> Arrow achieves straight flight</p>
                  </div>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-stopwatch mr-2"></i>
                    Critical Timing
                  </h4>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400">
                    The arrow must complete its oscillation cycle before the fletching clears the bow. This timing relationship determines optimal spine requirements for each specific setup.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dynamic vs Static Spine -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-exchange-alt text-green-600 dark:text-green-400 mr-3"></i>
            Dynamic vs. Static Spine Concepts
          </h2>
          
          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-6">
            <h3 class="font-medium text-green-800 dark:text-green-300 mb-2">
              <i class="fas fa-lightbulb mr-2"></i>
              Understanding the Difference
            </h3>
            <p class="text-sm text-green-700 dark:text-green-400">
              Static spine is what manufacturers measure in controlled conditions. Dynamic spine is how your arrow actually behaves in your specific bow setup. Professional tuning focuses on dynamic spine optimization.
            </p>
          </div>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Static Spine</h3>
              
              <div class="space-y-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-ruler mr-2"></i>
                    Standardized Measurement
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p><strong>Test Conditions:</strong> 28" shaft length</p>
                    <p><strong>Load Position:</strong> 1.94 lb weight at center</p>
                    <p><strong>Support Points:</strong> 26" apart</p>
                    <p><strong>Measurement:</strong> Deflection in thousandths</p>
                  </div>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h4 class="font-medium text-gray-800 dark:text-gray-300 mb-2">Chart Limitations</h4>
                  <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                    <p>• Assumes center shot bow design</p>
                    <p>• Standard 100 grain point weight</p>
                    <p>• Controlled laboratory conditions</p>
                    <p>• No consideration for release style</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Dynamic Spine</h3>
              
              <div class="space-y-4">
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">
                    <i class="fas fa-arrows-alt mr-2"></i>
                    Real-World Behavior
                  </h4>
                  <div class="text-sm text-orange-700 dark:text-orange-400 space-y-1">
                    <p><strong>Actual Arrow Length:</strong> May differ from 28"</p>
                    <p><strong>Point Weight Variation:</strong> Affects spine behavior</p>
                    <p><strong>Center Shot Position:</strong> Changes flex requirements</p>
                    <p><strong>Release Dynamics:</strong> String/finger release differences</p>
                  </div>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-cogs mr-2"></i>
                    Factors Affecting Dynamic Spine
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p>• Arrow length (±5 spine per inch)</p>
                    <p>• Point weight (±5 spine per 25 grains)</p>
                    <p>• Center shot position</p>
                    <p>• Release style and quality</p>
                    <p>• Bow efficiency and design</p>
                    <p>• String material and serving</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Professional Reality Check -->
          <div class="mt-6 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
            <h3 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
              <i class="fas fa-info-circle mr-2"></i>
              Professional Reality Check
            </h3>
            <p class="text-sm text-yellow-700 dark:text-yellow-400">
              <strong>Key Insight:</strong> Real-world spine requirements often differ from manufacturer charts by 10-20 spine units. Professional tuning focuses on achieving optimal dynamic spine through testing, not blind adherence to static spine charts.
            </p>
          </div>
        </div>

        <!-- Advanced Tuning Methods -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-crosshairs text-red-600 dark:text-red-400 mr-3"></i>
            Advanced Tuning Methods
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-3">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Paper Tuning</h3>
              
              <div class="space-y-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-file mr-2"></i>
                    Methodology
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p>• Shoot through paper at 3-6 feet</p>
                    <p>• Analyze tear patterns</p>
                    <p>• Adjust rest and nocking point</p>
                    <p>• Fine-tune until bullet hole achieved</p>
                  </div>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">Limitations</h4>
                  <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <p>• Only shows initial flight path</p>
                    <p>• Doesn't predict long-range behavior</p>
                    <p>• Can mask spine problems</p>
                    <p>• Weather affects results</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Bare Shaft Tuning</h3>
              
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    <i class="fas fa-target mr-2"></i>
                    Gold Standard Method
                  </h4>
                  <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <p>• Shoot fletched and bare arrows</p>
                    <p>• Compare impact points at distance</p>
                    <p>• Reveals true spine behavior</p>
                    <p>• Essential for traditional archery</p>
                  </div>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Advantages</h4>
                  <div class="text-sm text-orange-700 dark:text-orange-400 space-y-1">
                    <p>• Shows true arrow behavior</p>
                    <p>• Predicts long-range performance</p>
                    <p>• Eliminates fletching compensation</p>
                    <p>• Works for all bow types</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Walk-Back Tuning</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-walking mr-2"></i>
                    Distance Verification
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p>• Start at 20 yards, aim at point</p>
                    <p>• Walk back to 30, 40, 50 yards</p>
                    <p>• Maintain same aiming point</p>
                    <p>• Analyze vertical deviation pattern</p>
                  </div>
                </div>
                
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">Applications</h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p>• Verify center shot alignment</p>
                    <p>• Check arrow rest timing</p>
                    <p>• Confirm long-range accuracy</p>
                    <p>• Final tuning verification</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Professional Tuning Sequence -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-list-ol text-orange-600 dark:text-orange-400 mr-3"></i>
            Professional Tuning Sequence
          </h2>
          
          <div class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4 mb-6">
            <h3 class="font-medium text-orange-800 dark:text-orange-300 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Critical: Follow This Order
            </h3>
            <p class="text-sm text-orange-700 dark:text-orange-400">
              Professional tuning must follow a specific sequence. Adjusting components out of order can mask problems and lead to poor accuracy. Each step builds on the previous foundation.
            </p>
          </div>
          
          <div class="space-y-6">
            <!-- Phase 1: Foundation -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                <i class="fas fa-foundation text-blue-600 dark:text-blue-400 mr-2"></i>
                Phase 1: Foundation Setup
              </h3>
              
              <div class="grid gap-4 lg:grid-cols-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-1">
                    <span class="text-xs bg-blue-200 dark:bg-blue-800 rounded px-2 py-1 mr-2">1</span>
                    Bow Setup
                  </h4>
                  <div class="text-xs text-blue-700 dark:text-blue-400">
                    <p>• Verify draw weight/length</p>
                    <p>• Check cam timing (compound)</p>
                    <p>• Set brace height</p>
                  </div>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">
                    <span class="text-xs bg-green-200 dark:bg-green-800 rounded px-2 py-1 mr-2">2</span>
                    Center Shot
                  </h4>
                  <div class="text-xs text-green-700 dark:text-green-400">
                    <p>• Establish center shot position</p>
                    <p>• Set preliminary rest position</p>
                    <p>• Check arrow clearance</p>
                  </div>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-1">
                    <span class="text-xs bg-yellow-200 dark:bg-yellow-800 rounded px-2 py-1 mr-2">3</span>
                    Nocking Point
                  </h4>
                  <div class="text-xs text-yellow-700 dark:text-yellow-400">
                    <p>• Square nocking point start</p>
                    <p>• Check for consistent placement</p>
                    <p>• Verify adequate clearance</p>
                  </div>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-1">
                    <span class="text-xs bg-purple-200 dark:bg-purple-800 rounded px-2 py-1 mr-2">4</span>
                    Arrow Selection
                  </h4>
                  <div class="text-xs text-purple-700 dark:text-purple-400">
                    <p>• Calculate theoretical spine</p>
                    <p>• Account for center shot</p>
                    <p>• Select test spine range</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Phase 2: Coarse Tuning -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                <i class="fas fa-adjust text-green-600 dark:text-green-400 mr-2"></i>
                Phase 2: Coarse Tuning
              </h3>
              
              <div class="grid gap-4 lg:grid-cols-3">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <span class="text-xs bg-red-200 dark:bg-red-800 rounded px-2 py-1 mr-2">5</span>
                    Bare Shaft Testing
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p>• Test spine accuracy at 15-20 yards</p>
                    <p>• Compare bare vs. fletched impacts</p>
                    <p>• Adjust spine/point weight as needed</p>
                    <p>• Achieve consistent bare shaft grouping</p>
                  </div>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <span class="text-xs bg-blue-200 dark:bg-blue-800 rounded px-2 py-1 mr-2">6</span>
                    Paper Tuning
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p>• Shoot through paper at 4-6 feet</p>
                    <p>• Analyze tear patterns</p>
                    <p>• Adjust rest position vertically/horizontally</p>
                    <p>• Work toward clean bullet hole</p>
                  </div>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    <span class="text-xs bg-green-200 dark:bg-green-800 rounded px-2 py-1 mr-2">7</span>
                    Group Testing
                  </h4>
                  <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <p>• Shoot groups at multiple distances</p>
                    <p>• Verify consistency at 30+ yards</p>
                    <p>• Check for distance-specific issues</p>
                    <p>• Document baseline performance</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Phase 3: Fine Tuning -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                <i class="fas fa-crosshairs text-purple-600 dark:text-purple-400 mr-2"></i>
                Phase 3: Fine Tuning & Verification
              </h3>
              
              <div class="grid gap-4 lg:grid-cols-3">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <span class="text-xs bg-purple-200 dark:bg-purple-800 rounded px-2 py-1 mr-2">8</span>
                    Walk-Back Tuning
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p>• Final center shot verification</p>
                    <p>• Test at progressively longer distances</p>
                    <p>• Confirm vertical tracking</p>
                    <p>• Validate rest timing (compounds)</p>
                  </div>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">
                    <span class="text-xs bg-orange-200 dark:bg-orange-800 rounded px-2 py-1 mr-2">9</span>
                    Broadhead Testing
                  </h4>
                  <div class="text-sm text-orange-700 dark:text-orange-400 space-y-1">
                    <p>• Test actual hunting arrows</p>
                    <p>• Compare to field point groups</p>
                    <p>• Adjust for broadhead planing</p>
                    <p>• Final spine verification</p>
                  </div>
                </div>
                
                <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-teal-800 dark:text-teal-300 mb-2">
                    <span class="text-xs bg-teal-200 dark:bg-teal-800 rounded px-2 py-1 mr-2">10</span>
                    Environmental Testing
                  </h4>
                  <div class="text-sm text-teal-700 dark:text-teal-400 space-y-1">
                    <p>• Test in various conditions</p>
                    <p>• Verify performance at hunting distances</p>
                    <p>• Document final specifications</p>
                    <p>• Establish backup arrow setups</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Advanced Troubleshooting -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-search text-yellow-600 dark:text-yellow-400 mr-3"></i>
            Advanced Arrow Flight Troubleshooting
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Left/Right Impact Analysis</h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-arrow-right mr-2"></i>
                    Arrows Hitting Right (RH Archer)
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-2">
                    <p><strong>Primary Causes:</strong></p>
                    <p>• Arrows too stiff for center shot position</p>
                    <p>• Rest positioned too far left</p>
                    <p>• Nocking point too high</p>
                    <p>• Side pressure during release</p>
                    
                    <p class="font-medium mt-2"><strong>Solutions (try in order):</strong></p>
                    <p>• Move rest slightly right (1/32" increments)</p>
                    <p>• Try next weaker spine group</p>
                    <p>• Increase point weight by 25 grains</p>
                    <p>• Lower nocking point slightly</p>
                  </div>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-arrow-left mr-2"></i>
                    Arrows Hitting Left (RH Archer)
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-2">
                    <p><strong>Primary Causes:</strong></p>
                    <p>• Arrows too weak for setup</p>
                    <p>• Rest positioned too far right</p>
                    <p>• Nocking point too low</p>
                    <p>• Insufficient draw weight</p>
                    
                    <p class="font-medium mt-2"><strong>Solutions (try in order):</strong></p>
                    <p>• Move rest slightly left (1/32" increments)</p>
                    <p>• Try next stiffer spine group</p>
                    <p>• Reduce point weight</p>
                    <p>• Raise nocking point slightly</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Distance-Specific Issues</h3>
              
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    <i class="fas fa-bullseye mr-2"></i>
                    Good at 20, Poor at 40+ Yards
                  </h4>
                  <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <p><strong>Symptoms:</strong> Groups open up significantly at distance</p>
                    <p><strong>Likely Causes:</strong></p>
                    <p>• Marginal spine match (close but not perfect)</p>
                    <p>• Fletching masking spine issues at short range</p>
                    <p>• Rest timing problems (compound bows)</p>
                    <p>• Inconsistent release or form</p>
                  </div>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-wind mr-2"></i>
                    Wind Sensitivity Issues
                  </h4>
                  <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <p><strong>Symptoms:</strong> Excessive wind drift, unstable flight</p>
                    <p><strong>Likely Causes:</strong></p>
                    <p>• Poor fletching/arrow balance</p>
                    <p>• Arrows still oscillating at distance</p>
                    <p>• Incorrect spine causing persistent flex</p>
                    <p>• FOC too low or too high</p>
                  </div>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-feather mr-2"></i>
                    Fletching Contact Problems
                  </h4>
                  <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                    <p><strong>Symptoms:</strong> Torn fletching, erratic flight</p>
                    <p><strong>Likely Causes:</strong></p>
                    <p>• Spine too weak causing excessive flex</p>
                    <p>• Nocking point too low</p>
                    <p>• Rest positioned incorrectly</p>
                    <p>• Fletching too large for bow design</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Professional Tuning Reality -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-user-graduate text-indigo-600 dark:text-indigo-400 mr-3"></i>
            Professional Tuning Reality
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Field Wisdom</h3>
              
              <div class="space-y-4">
                <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300 mb-2">
                    <i class="fas fa-quote-left mr-2"></i>
                    Perfect Paper ≠ Perfect Groups
                  </h4>
                  <p class="text-sm text-indigo-700 dark:text-indigo-400 mb-2">
                    Many perfectly tuned bows on paper still struggle at longer distances. Focus on actual target performance over theoretical perfection. Small paper tears may be acceptable if your groups are tight at 40+ yards.
                  </p>
                  <p class="text-xs text-indigo-600 dark:text-indigo-500 italic">
                    "Tune for the target, not the paper" - Professional archery wisdom
                  </p>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Spine Tolerance Reality</h4>
                  <p class="text-sm text-green-700 dark:text-green-400">
                    Professional arrows maintain ±2 spine units within a dozen, while budget arrows may vary ±5-10 spine units. This variance significantly affects consistency at longer distances and explains why some arrows "just don't group well."
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Environmental Factors</h3>
              
              <div class="space-y-4">
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-thermometer-half mr-2"></i>
                    Temperature Effects
                  </h4>
                  <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <p><strong>Cold Weather:</strong> Arrows become slightly stiffer</p>
                    <p><strong>Hot Weather:</strong> Arrows become slightly more flexible</p>
                    <p><strong>Extreme Changes:</strong> May require different spine groups</p>
                    <p><strong>Professional Tip:</strong> Test in actual hunting conditions</p>
                  </div>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-tint mr-2"></i>
                    Humidity Considerations
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p><strong>Wood Arrows:</strong> Gain 5-10 grains in high humidity</p>
                    <p><strong>Carbon Arrows:</strong> Largely unaffected by moisture</p>
                    <p><strong>Fletching:</strong> Natural feathers affected more than vanes</p>
                    <p><strong>String Material:</strong> Some materials stretch with humidity</p>
                  </div>
                </div>
                
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-mountain mr-2"></i>
                    Altitude Effects
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p><strong>Air Density:</strong> Affects arrow stability</p>
                    <p><strong>Higher Elevation:</strong> Reduced air resistance</p>
                    <p><strong>Fletching Performance:</strong> May need larger vanes</p>
                    <p><strong>Tune Locally:</strong> Verify at hunting elevation</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Troubleshooting Quick Reference -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-tools text-orange-600 dark:text-orange-400 mr-3"></i>
            Quick Troubleshooting Reference
          </h2>
          
          <div class="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
            <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <h3 class="font-medium text-red-800 dark:text-red-300 mb-2">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                Immediate Issues
              </h3>
              <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                <p><strong>Robin Hooding:</strong> Arrows hitting each other</p>
                <p><strong>Solution:</strong> Perfect tune - adjust target spacing</p>
                <hr class="border-red-300 dark:border-red-700 my-2">
                <p><strong>Fletching Damage:</strong> Torn or missing vanes</p>
                <p><strong>Solution:</strong> Check spine, rest clearance</p>
              </div>
            </div>
            
            <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
              <h3 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                <i class="fas fa-clock mr-2"></i>
                Distance Problems
              </h3>
              <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                <p><strong>Groups Open Up:</strong> Good close, poor far</p>
                <p><strong>Solution:</strong> Spine too weak, try stiffer</p>
                <hr class="border-yellow-300 dark:border-yellow-700 my-2">
                <p><strong>Vertical Stringing:</strong> Tall groups</p>
                <p><strong>Solution:</strong> Nocking point or form issue</p>
              </div>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-medium text-green-800 dark:text-green-300 mb-2">
                <i class="fas fa-wind mr-2"></i>
                Weather Sensitivity
              </h3>
              <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                <p><strong>Wind Planing:</strong> Arrows drift excessively</p>
                <p><strong>Solution:</strong> Check spine, FOC balance</p>
                <hr class="border-green-300 dark:border-green-700 my-2">
                <p><strong>Rain Performance:</strong> Groups change in wet</p>
                <p><strong>Solution:</strong> Wood arrow moisture issue</p>
              </div>
            </div>
            
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h3 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                <i class="fas fa-crosshairs mr-2"></i>
                Consistency Issues
              </h3>
              <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                <p><strong>Fliers:</strong> Random arrows outside group</p>
                <p><strong>Solution:</strong> Check arrow weight matching</p>
                <hr class="border-purple-300 dark:border-purple-700 my-2">
                <p><strong>Form Sensitivity:</strong> Tune changes with stance</p>
                <p><strong>Solution:</strong> Spine too critical, try weaker</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Professional Standards -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-medal text-gold-500 mr-3"></i>
            Professional Tuning Standards
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-3">
            <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
              <h3 class="font-medium text-amber-800 dark:text-amber-300 mb-3">
                <i class="fas fa-trophy mr-2"></i>
                Competition Standards
              </h3>
              <div class="text-sm text-amber-700 dark:text-amber-400 space-y-1">
                <p><strong>Group Size:</strong> Sub-2" at 40 yards</p>
                <p><strong>Consistency:</strong> 20+ arrow average</p>
                <p><strong>Spine Tolerance:</strong> ±2 units maximum</p>
                <p><strong>Weight Matching:</strong> ±0.5 grain per dozen</p>
                <p><strong>Paper Tune:</strong> Bullet hole ±1/4"</p>
              </div>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-medium text-green-800 dark:text-green-300 mb-3">
                <i class="fas fa-crosshairs mr-2"></i>
                Hunting Standards
              </h3>
              <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                <p><strong>Group Size:</strong> 4" at 40 yards acceptable</p>
                <p><strong>Broadhead Match:</strong> Within 2" of field points</p>
                <p><strong>Spine Tolerance:</strong> ±5 units workable</p>
                <p><strong>Weather Proof:</strong> Consistent in conditions</p>
                <p><strong>Reliability:</strong> Performs under stress</p>
              </div>
            </div>
            
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-medium text-blue-800 dark:text-blue-300 mb-3">
                <i class="fas fa-users mr-2"></i>
                Recreational Standards
              </h3>
              <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                <p><strong>Group Size:</strong> 6" at 30 yards adequate</p>
                <p><strong>Consistency:</strong> Repeatable results</p>
                <p><strong>Spine Tolerance:</strong> ±10 units manageable</p>
                <p><strong>Ease of Tuning:</strong> Forgiving setup</p>
                <p><strong>Cost Effective:</strong> Good value performance</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Links to Interactive Tools -->
        <div class="bg-gradient-to-br from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6 text-center">
          <h3 class="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-2">
            <i class="fas fa-tools mr-2"></i>
            Apply These Concepts
          </h3>
          <p class="text-blue-700 dark:text-blue-300 mb-4">
            Use our professional tuning tools to implement these methodologies with your equipment.
          </p>
          <div class="flex justify-center space-x-4">
            <NuxtLink
              to="/tuning"
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-play-circle mr-2"></i>
              Interactive Tuning
            </NuxtLink>
            <NuxtLink
              to="/calculator"
              class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-calculator mr-2"></i>
              Spine Calculator
            </NuxtLink>
            <NuxtLink
              to="/my-setup"
              class="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
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
  title: 'Tuning Methodologies - Archery Tools',
  meta: [
    { name: 'description', content: 'Professional archery tuning methodologies including dynamic spine concepts, scientific foundations, advanced troubleshooting, and professional standards.' }
  ]
})
</script>

<style scoped>
/* Component specific styles */
</style>