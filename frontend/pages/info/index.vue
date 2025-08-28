<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-6">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Archery Information Center
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Comprehensive guides and resources for arrow tuning and archery equipment
        </p>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <i class="fas fa-atom text-blue-600 dark:text-blue-400 text-xl"></i>
            </div>
            <div class="ml-4">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Materials</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ materialCount }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <i class="fas fa-tools text-green-600 dark:text-green-400 text-xl"></i>
            </div>
            <div class="ml-4">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Tuning Methods</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ tuningMethodCount }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 text-xl"></i>
            </div>
            <div class="ml-4">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Problems Covered</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ problemCount }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <i class="fas fa-calculator text-purple-600 dark:text-purple-400 text-xl"></i>
            </div>
            <div class="ml-4">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Calculations</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ calculationCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Information Categories -->
      <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        
        <!-- Arrow Materials -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <i class="fas fa-atom text-blue-600 dark:text-blue-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Arrow Materials</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Properties and characteristics</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Learn about different arrow shaft materials, their properties, and how they affect performance.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Carbon fiber arrows
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Aluminum arrows
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Wood arrows
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Hybrid materials
              </div>
            </div>
            
            <NuxtLink
              to="/info/materials"
              class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Learn More
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Tuning Methodologies (Expanded) -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden col-span-full">
          <div class="p-6">
            <div class="flex items-center mb-6">
              <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <i class="fas fa-tools text-green-600 dark:text-green-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-2xl font-semibold text-gray-900 dark:text-white">Arrow Tuning Methodologies</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Step-by-step guides for achieving perfect arrow flight</p>
              </div>
            </div>

            <!-- Tuning Overview -->
            <div class="mb-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Understanding Arrow Tuning
              </h3>
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                Arrow tuning is the process of adjusting your bow and arrow setup to achieve the most 
                accurate and consistent arrow flight possible. Proper tuning eliminates erratic arrow 
                behavior and maximizes your shooting potential.
              </p>
              
              <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-900 dark:text-blue-300 mb-2">Consistency</h4>
                  <p class="text-sm text-blue-700 dark:text-blue-400">
                    Achieve repeatable, predictable arrow flight
                  </p>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-900 dark:text-green-300 mb-2">Accuracy</h4>
                  <p class="text-sm text-green-700 dark:text-green-400">
                    Improve grouping and hit probability
                  </p>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-900 dark:text-yellow-300 mb-2">Efficiency</h4>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400">
                    Maximize energy transfer and arrow speed
                  </p>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-900 dark:text-purple-300 mb-2">Forgiveness</h4>
                  <p class="text-sm text-purple-700 dark:text-purple-400">
                    Reduce the impact of minor form errors
                  </p>
                </div>
              </div>
            </div>

            <!-- Tuning Methods Grid -->
            <div class="grid gap-6 lg:grid-cols-2">
              
              <!-- Paper Tuning -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
                <div class="flex items-start mb-4">
                  <div class="flex-shrink-0 p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                    <i class="fas fa-file-alt text-blue-600 dark:text-blue-400 text-xl"></i>
                  </div>
                  <div class="ml-4 flex-1">
                    <div class="flex justify-between items-start">
                      <div>
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                          Paper Tuning
                        </h4>
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          The foundation of arrow tuning - reveals arrow flight characteristics
                        </p>
                      </div>
                      <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <i class="fas fa-clock mr-1"></i>
                        30-45 min
                      </div>
                    </div>
                    
                    <div class="mt-4">
                      <div class="grid gap-4 md:grid-cols-2">
                        <div>
                          <h5 class="font-medium text-gray-900 dark:text-white mb-2">Equipment Needed</h5>
                          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>• Paper frame (newspaper works)</li>
                            <li>• Target backstop</li>
                            <li>• Tape measure</li>
                            <li>• Arrows and bow</li>
                          </ul>
                        </div>
                        
                        <div>
                          <h5 class="font-medium text-gray-900 dark:text-white mb-2">Step-by-Step Process</h5>
                          <ol class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>1. Set paper frame 6 feet from target</li>
                            <li>2. Shoot arrow through paper</li>
                            <li>3. Analyze tear pattern</li>
                            <li>4. Make adjustments accordingly</li>
                            <li>5. Repeat until perfect hole</li>
                          </ol>
                        </div>
                      </div>
                      
                      <div class="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <h5 class="font-medium text-blue-900 dark:text-blue-300 mb-2">Reading Paper Tears</h5>
                        <div class="grid gap-2 md:grid-cols-2">
                          <div class="text-sm text-blue-700 dark:text-blue-400">
                            <strong>Left tear:</strong> Arrow spine too weak, move rest right, or reduce draw weight
                          </div>
                          <div class="text-sm text-blue-700 dark:text-blue-400">
                            <strong>Right tear:</strong> Arrow spine too stiff, move rest left, or increase point weight
                          </div>
                          <div class="text-sm text-blue-700 dark:text-blue-400">
                            <strong>High tear:</strong> Nocking point too low, raise nocking point
                          </div>
                          <div class="text-sm text-blue-700 dark:text-blue-400">
                            <strong>Low tear:</strong> Nocking point too high, lower nocking point
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Bare Shaft Tuning -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
                <div class="flex items-start mb-4">
                  <div class="flex-shrink-0 p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                    <i class="fas fa-arrows-alt-h text-green-600 dark:text-green-400 text-xl"></i>
                  </div>
                  <div class="ml-4 flex-1">
                    <div class="flex justify-between items-start">
                      <div>
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                          Bare Shaft Tuning
                        </h4>
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          Advanced method using unfletched arrows for precise tuning
                        </p>
                      </div>
                      <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <i class="fas fa-clock mr-1"></i>
                        45-60 min
                      </div>
                    </div>
                    
                    <div class="mt-4">
                      <div class="grid gap-4 md:grid-cols-2">
                        <div>
                          <h5 class="font-medium text-gray-900 dark:text-white mb-2">Why Bare Shaft?</h5>
                          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>• No fletching to mask problems</li>
                            <li>• More sensitive to tune issues</li>
                            <li>• Better for precision tuning</li>
                            <li>• Reveals true arrow flight</li>
                          </ul>
                        </div>
                        
                        <div>
                          <h5 class="font-medium text-gray-900 dark:text-white mb-2">Process Overview</h5>
                          <ol class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>1. Shoot fletched arrows at 20 yards</li>
                            <li>2. Shoot bare shaft arrows</li>
                            <li>3. Compare impact points</li>
                            <li>4. Adjust rest position</li>
                            <li>5. Test at longer distances</li>
                          </ol>
                        </div>
                      </div>
                      
                      <div class="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <h5 class="font-medium text-green-900 dark:text-green-300 mb-2">Adjustments Guide</h5>
                        <div class="grid gap-2 md:grid-cols-2">
                          <div class="text-sm text-green-700 dark:text-green-400">
                            <strong>Bare shaft left:</strong> Move rest right, or stiffen arrow spine
                          </div>
                          <div class="text-sm text-green-700 dark:text-green-400">
                            <strong>Bare shaft right:</strong> Move rest left, or weaken arrow spine
                          </div>
                          <div class="text-sm text-green-700 dark:text-green-400">
                            <strong>Bare shaft high:</strong> Lower nocking point, check arrow spine
                          </div>
                          <div class="text-sm text-green-700 dark:text-green-400">
                            <strong>Bare shaft low:</strong> Raise nocking point, check form
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Walk-Back Tuning -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
                <div class="flex items-start mb-4">
                  <div class="flex-shrink-0 p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                    <i class="fas fa-walking text-yellow-600 dark:text-yellow-400 text-xl"></i>
                  </div>
                  <div class="ml-4 flex-1">
                    <div class="flex justify-between items-start">
                      <div>
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                          Walk-Back Tuning
                        </h4>
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          Fine-tune arrow rest centershot for perfect alignment
                        </p>
                      </div>
                      <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <i class="fas fa-clock mr-1"></i>
                        20-30 min
                      </div>
                    </div>
                    
                    <div class="mt-4">
                      <div class="grid gap-4 md:grid-cols-2">
                        <div>
                          <h5 class="font-medium text-gray-900 dark:text-white mb-2">Method</h5>
                          <ol class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>1. Shoot at 20 yards, aim at bullseye</li>
                            <li>2. Walk back to 30, 40, 50 yards</li>
                            <li>3. Aim at same point, note impacts</li>
                            <li>4. Adjust rest left/right as needed</li>
                            <li>5. Repeat until vertical line</li>
                          </ol>
                        </div>
                        
                        <div>
                          <h5 class="font-medium text-gray-900 dark:text-white mb-2">What to Look For</h5>
                          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>• Vertical line of impacts</li>
                            <li>• No left/right drift</li>
                            <li>• Consistent horizontal grouping</li>
                            <li>• Same sight picture at all distances</li>
                          </ul>
                        </div>
                      </div>
                      
                      <div class="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                        <h5 class="font-medium text-yellow-900 dark:text-yellow-300 mb-2">Pro Tips</h5>
                        <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                          <div>• Use a tall target or multiple targets for clear impact points</div>
                          <div>• Mark your rest position before making adjustments</div>
                          <div>• Small adjustments - 1/32" at a time</div>
                          <div>• Perform after paper tuning and bare shaft tuning</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Group Tuning -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6">
                <div class="flex items-start mb-4">
                  <div class="flex-shrink-0 p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
                    <i class="fas fa-bullseye text-purple-600 dark:text-purple-400 text-xl"></i>
                  </div>
                  <div class="ml-4 flex-1">
                    <div class="flex justify-between items-start">
                      <div>
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                          Group Tuning
                        </h4>
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          Fine-tune for the tightest possible groups
                        </p>
                      </div>
                      <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <i class="fas fa-clock mr-1"></i>
                        60+ min
                      </div>
                    </div>
                    
                    <div class="mt-4">
                      <div class="grid gap-4 md:grid-cols-2">
                        <div>
                          <h5 class="font-medium text-gray-900 dark:text-white mb-2">Variables to Test</h5>
                          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>• Nocking point height</li>
                            <li>• Rest position micro-adjustments</li>
                            <li>• Arrow spine selection</li>
                            <li>• Point weight variations</li>
                            <li>• Fletching configurations</li>
                          </ul>
                        </div>
                        
                        <div>
                          <h5 class="font-medium text-gray-900 dark:text-white mb-2">Testing Protocol</h5>
                          <ol class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>1. Shoot baseline 5-arrow groups</li>
                            <li>2. Make single small adjustment</li>
                            <li>3. Shoot another 5-arrow group</li>
                            <li>4. Compare group sizes</li>
                            <li>5. Keep improvements, revert others</li>
                          </ol>
                        </div>
                      </div>
                      
                      <div class="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                        <h5 class="font-medium text-purple-900 dark:text-purple-300 mb-2">Success Metrics</h5>
                        <div class="grid gap-2 md:grid-cols-2">
                          <div class="text-sm text-purple-700 dark:text-purple-400">
                            <strong>Beginner:</strong> 3-inch groups at 20 yards
                          </div>
                          <div class="text-sm text-purple-700 dark:text-purple-400">
                            <strong>Intermediate:</strong> 2-inch groups at 20 yards
                          </div>
                          <div class="text-sm text-purple-700 dark:text-purple-400">
                            <strong>Advanced:</strong> 1-inch groups at 20 yards
                          </div>
                          <div class="text-sm text-purple-700 dark:text-purple-400">
                            <strong>Expert:</strong> Sub-1-inch groups at 20 yards
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tuning Sequence -->
            <div class="mt-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Recommended Tuning Sequence
              </h3>
              <p class="text-gray-600 dark:text-gray-400 mb-6">
                Follow this sequence for the most effective tuning process:
              </p>
              
              <div class="space-y-4">
                <div v-for="(step, index) in tuningSequence" :key="index" class="flex items-start">
                  <div class="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    {{ index + 1 }}
                  </div>
                  <div class="ml-4">
                    <h4 class="font-medium text-gray-900 dark:text-white">{{ step.title }}</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ step.description }}</p>
                  </div>
                </div>
              </div>

              <div class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h4 class="font-medium text-blue-900 dark:text-blue-300 mb-2">Interactive Implementation</h4>
                <p class="text-sm text-blue-700 dark:text-blue-400 mb-3">
                  Ready to put these methods into practice? Use our interactive tuning guides for step-by-step assistance.
                </p>
                <NuxtLink
                  to="/tuning"
                  class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Start Interactive Tuning
                  <i class="fas fa-arrow-right ml-2"></i>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>

        <!-- Problem Diagnostics -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Flight Problems</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Diagnosis and solutions</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Identify and solve common arrow flight problems with our comprehensive diagnostic guide.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Left/right tears
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                High/low impacts
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Erratic grouping
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Poor clearance
              </div>
            </div>
            
            <NuxtLink
              to="/info/flight-problems"
              class="inline-flex items-center px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Diagnose Issues
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Spine Calculator -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <i class="fas fa-calculator text-purple-600 dark:text-purple-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Spine Calculator</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Calculation methods</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Understanding how spine calculations work and the factors that influence arrow selection.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Draw weight factors
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Arrow length adjustments
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Point weight effects
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Bow type differences
              </div>
            </div>
            
            <NuxtLink
              to="/info/spine-calculator"
              class="inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Learn Calculations
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Equipment Guide -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                <i class="fas fa-bow-arrow text-red-600 dark:text-red-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Equipment Guide</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Components and accessories</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Learn about different arrow components and how they affect performance and tuning.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Points and inserts
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Nocks and bushings
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Fletching options
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Wraps and crests
              </div>
            </div>
            
            <NuxtLink
              to="/info/equipment"
              class="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Equipment Guide
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Quick Reference -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
                <i class="fas fa-book text-indigo-600 dark:text-indigo-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Quick Reference</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Charts and formulas</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Quick reference charts, formulas, and conversion tables for field use.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Spine charts
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Conversion tables
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Tuning checklists
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Safety guidelines
              </div>
            </div>
            
            <NuxtLink
              to="/info/reference"
              class="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Quick Reference
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

// Page metadata
definePageMeta({
  middleware: ['auth-check'],
  layout: 'default'
})

// Composables
const api = useApi()

// Reactive data
const materialCount = ref(0)
const tuningMethodCount = ref(0)
const problemCount = ref(0)
const calculationCount = ref(0)

// Tuning sequence data
const tuningSequence = ref([
  {
    title: 'Basic Setup',
    description: 'Set initial nocking point, install rest, and establish basic arrow spine selection based on bow specifications.'
  },
  {
    title: 'Paper Tuning',
    description: 'Shoot through paper to identify major tuning issues and make initial rest and nocking point adjustments.'
  },
  {
    title: 'Bare Shaft Tuning',
    description: 'Fine-tune rest position using unfletched arrows to achieve perfect arrow flight alignment.'
  },
  {
    title: 'Walk-Back Tuning',
    description: 'Verify and fine-tune centershot by shooting at multiple distances with consistent aim point.'
  },
  {
    title: 'Group Tuning',
    description: 'Make micro-adjustments to optimize group size and consistency at your preferred shooting distance.'
  },
  {
    title: 'Field Testing',
    description: 'Test your setup in real shooting conditions and make final adjustments based on performance.'
  }
])

// Methods
async function loadInfoStats() {
  try {
    // These would be actual API calls to get statistics
    materialCount.value = 5 // Example count
    tuningMethodCount.value = 8 // Example count
    problemCount.value = 12 // Example count
    calculationCount.value = 15 // Example count
  } catch (error) {
    console.error('Error loading info stats:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadInfoStats()
})
</script>

<style scoped>
/* Add any component-specific styles here */
</style>