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
          <span class="text-gray-900 dark:text-white">Arrow Selection Guide</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Arrow Selection Based on Your Setup
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Professional guide to selecting the perfect arrows for your specific bow configuration
        </p>
      </div>

      <!-- Quick Calculator Access -->
      <div class="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-lg border border-orange-200 dark:border-orange-800 p-6 mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-orange-800 dark:text-orange-200 mb-2">
              <i class="fas fa-calculator mr-2"></i>
              Professional Spine Calculator
            </h2>
            <p class="text-orange-700 dark:text-orange-300">
              Use our advanced calculator for precise arrow recommendations based on your exact specifications.
            </p>
          </div>
          <NuxtLink
            to="/calculator"
            class="px-6 py-3 bg-orange-600 hover:bg-orange-700 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-arrow-right mr-2"></i>
            Open Calculator
          </NuxtLink>
        </div>
      </div>

      <div class="space-y-8">

        <!-- Step-by-Step Selection Process -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-list-ol text-blue-600 dark:text-blue-400 mr-3"></i>
            Step-by-Step Arrow Selection Process
          </h2>
          
          <div class="space-y-6">
            <!-- Step 1: Bow Specifications -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">1</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Determine Your Bow Specifications
                </h3>
                
                <div class="grid gap-4 md:grid-cols-3">
                  <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                      <i class="fas fa-weight-hanging mr-2"></i>
                      Draw Weight
                    </h4>
                    <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                      <p><strong>Compound:</strong> Peak weight at your draw length</p>
                      <p><strong>Recurve:</strong> Weight marked on limbs</p>
                      <p><strong>Measure actual:</strong> Use bow scale for accuracy</p>
                      <p class="text-xs italic">Most important factor for spine selection</p>
                    </div>
                  </div>
                  
                  <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                      <i class="fas fa-ruler mr-2"></i>
                      Draw Length
                    </h4>
                    <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                      <p><strong>Measurement:</strong> Nock groove to throat + 1.75"</p>
                      <p><strong>Professional:</strong> Use draw length measurement tool</p>
                      <p><strong>Important:</strong> Affects cam timing and efficiency</p>
                      <p class="text-xs italic">Critical for compound bow performance</p>
                    </div>
                  </div>
                  
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                      <i class="fas fa-archway mr-2"></i>
                      Bow Type
                    </h4>
                    <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                      <p><strong>Compound:</strong> 85-95% let-off typical</p>
                      <p><strong>Recurve:</strong> Traditional shooting style</p>
                      <p><strong>Longbow:</strong> No arrow rest, different dynamics</p>
                      <p class="text-xs italic">Affects efficiency and spine requirements</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 2: Arrow Length -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">2</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Determine Required Arrow Length
                </h3>
                
                <div class="grid gap-4 md:grid-cols-2">
                  <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">Safety Requirements</h4>
                    <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-2">
                      <p><strong>Minimum Clearance:</strong> 1" past arrow rest when at full draw</p>
                      <p><strong>Recommended:</strong> 1.5-2" for safety margin</p>
                      <p><strong>Broadheads:</strong> Additional 0.5" clearance recommended</p>
                      <div class="bg-yellow-100 dark:bg-yellow-800/30 rounded p-2 mt-2">
                        <p class="text-xs font-medium">Formula: Draw Length + 1.5" to 2.5" = Arrow Length</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">Performance Considerations</h4>
                    <div class="text-sm text-purple-700 dark:text-purple-400 space-y-2">
                      <p><strong>Shorter Arrows:</strong> Stiffer effective spine, faster</p>
                      <p><strong>Longer Arrows:</strong> Weaker effective spine, more forgiving</p>
                      <p><strong>Sweet Spot:</strong> Usually draw length + 1.5" to 2"</p>
                      <div class="bg-purple-100 dark:bg-purple-800/30 rounded p-2 mt-2">
                        <p class="text-xs font-medium">Each inch of length = ±5 spine adjustment needed</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 3: Basic Spine Calculation -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">3</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Calculate Basic Spine Requirements
                </h3>
                
                <!-- Critical Understanding Warning -->
                <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
                  <h4 class="text-lg font-semibold text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Critical: Spine = Arrow Length vs. Poundage (NOT Draw Length!)
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p><strong>Common Mistake:</strong> Thinking spine is calculated from draw length</p>
                    <p><strong>Reality:</strong> Spine is calculated based on ARROW LENGTH vs. bow poundage</p>
                    <p><strong>Key Point:</strong> Draw length only determines minimum safe arrow length</p>
                    <p><strong>Optimization:</strong> You can shoot longer arrows for sight window and point-on benefits</p>
                    <p class="font-medium mt-2">Each different arrow length requires a different spine calculation!</p>
                  </div>
                </div>

                <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-6">
                  <h4 class="text-lg font-semibold text-blue-800 dark:text-blue-300 mb-4">
                    <i class="fas fa-calculator mr-2"></i>
                    Manual Spine Calculator for Carbon Arrows
                  </h4>
                  
                  <div class="grid gap-6 lg:grid-cols-2">
                    <div>
                      <h5 class="font-medium text-gray-900 dark:text-white mb-3">Base Formula</h5>
                      <div class="bg-white dark:bg-gray-700 rounded-lg p-4 mb-4">
                        <div class="text-center">
                          <div class="text-lg font-mono text-blue-600 dark:text-blue-400 mb-2">
                            Base Spine = 400 - (Draw Weight - 30) × 2
                          </div>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            Starting point for 28" arrows with 100gr points
                          </p>
                        </div>
                      </div>
                      
                      <div class="space-y-3">
                        <div class="bg-red-50 dark:bg-red-900/20 rounded p-3">
                          <h6 class="font-medium text-red-800 dark:text-red-300 mb-1">Point Weight Adjustment</h6>
                          <p class="text-sm text-red-700 dark:text-red-400">
                            -5 spine per 25 grains over 100gr<br>
                            +5 spine per 25 grains under 100gr
                          </p>
                        </div>
                        
                        <div class="bg-green-50 dark:bg-green-900/20 rounded p-3">
                          <h6 class="font-medium text-green-800 dark:text-green-300 mb-1">Length Adjustment</h6>
                          <p class="text-sm text-green-700 dark:text-green-400">
                            +5 spine per inch over 28"<br>
                            -5 spine per inch under 28"
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h5 class="font-medium text-gray-900 dark:text-white mb-3">Worked Example</h5>
                      <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                        <h6 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                          Example: 60lb Bow, 29" Arrow Length, 125gr Points
                        </h6>
                        <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-2">
                          <p><strong>Step 1:</strong> Base = 400 - (60-30) × 2 = 340 spine</p>
                          <p><strong>Step 2:</strong> Point adj = 340 - 5 = 335 (heavier points need stiffer)</p>
                          <p><strong>Step 3:</strong> Length adj = 335 + 5 = 340 (longer arrows need weaker)</p>
                          <div class="bg-yellow-100 dark:bg-yellow-800/30 rounded p-2 mt-2">
                            <p class="font-medium">Result: 340 spine for this ARROW LENGTH</p>
                            <p class="text-xs mt-1">If using 31" arrows instead: 340 + 10 = 350 spine needed!</p>
                          </div>
                        </div>
                      </div>
                      
                      <div class="mt-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                        <h6 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Safety Range</h6>
                        <p class="text-sm text-orange-700 dark:text-orange-400">
                          Professional recommendation: Test 320-360 spine range for this setup. 
                          Start with 340, then fine-tune based on paper tuning results.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Center Shot Considerations -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center text-lg font-bold">🎯</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Center Shot Impact on Spine Requirements
                </h3>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4 mb-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-info-circle mr-2"></i>
                    What is Center Shot?
                  </h4>
                  <p class="text-sm text-purple-700 dark:text-purple-400">
                    Center shot refers to how the arrow's path aligns with the bow's centerline. Traditional bows are often "off-center" requiring arrows to bend around the riser, while modern compound bows achieve true "center shot" with straight arrow flight.
                  </p>
                </div>
                
                <div class="grid gap-4 lg:grid-cols-3">
                  <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                      <i class="fas fa-archway mr-2"></i>
                      Traditional Longbows
                    </h4>
                    <div class="text-sm text-red-700 dark:text-red-400 space-y-2">
                      <p><strong>Center Shot:</strong> Usually 1/8" to 3/8" off-center</p>
                      <p><strong>Archer's Paradox:</strong> Maximum arrow flex required</p>
                      <p><strong>Spine Effect:</strong> Need arrows 5-15# weaker than bow weight</p>
                      <div class="bg-red-100 dark:bg-red-800/30 rounded p-2 mt-2">
                        <p class="text-xs font-medium">
                          Example: 50# longbow often shoots best with 35-40# spine arrows
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">
                      <i class="fas fa-adjust mr-2"></i>
                      Traditional Recurves
                    </h4>
                    <div class="text-sm text-orange-700 dark:text-orange-400 space-y-2">
                      <p><strong>Center Shot:</strong> Slightly off to cut past center</p>
                      <p><strong>Archer's Paradox:</strong> Moderate arrow flex</p>
                      <p><strong>Spine Effect:</strong> Usually 2-8# weaker than bow weight</p>
                      <div class="bg-orange-100 dark:bg-orange-800/30 rounded p-2 mt-2">
                        <p class="text-xs font-medium">
                          Example: 45# recurve typically uses 40-45# spine arrows
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                      <i class="fas fa-bullseye mr-2"></i>
                      Compound Bows
                    </h4>
                    <div class="text-sm text-green-700 dark:text-green-400 space-y-2">
                      <p><strong>Center Shot:</strong> True center shot design</p>
                      <p><strong>Archer's Paradox:</strong> Minimal arrow flex</p>
                      <p><strong>Spine Effect:</strong> Close to actual bow weight</p>
                      <div class="bg-green-100 dark:bg-green-800/30 rounded p-2 mt-2">
                        <p class="text-xs font-medium">
                          Example: 60# compound uses 55-65# spine arrows
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="mt-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-ruler-combined mr-2"></i>
                    Measuring Your Bow's Center Shot
                  </h4>
                  <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <p>1. <strong>Nock an arrow</strong> on the string at your normal nocking point</p>
                    <p>2. <strong>Measure horizontally</strong> from the arrow to the center of the bow riser</p>
                    <p>3. <strong>Positive measurement:</strong> Arrow is off-center (toward your bow hand)</p>
                    <p>4. <strong>Zero or negative:</strong> Arrow is at or past center shot</p>
                    <p class="font-medium mt-2">Use this measurement to adjust spine calculations!</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 4: Point Weight Selection -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">4</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Select Appropriate Point Weight
                </h3>
                
                <div class="grid gap-4 md:grid-cols-3">
                  <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                      <i class="fas fa-bullseye mr-2"></i>
                      Target Archery
                    </h4>
                    <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                      <p><strong>Optimal:</strong> 100-120 grains</p>
                      <p><strong>Benefits:</strong> Speed and flat trajectory</p>
                      <p><strong>FOC Target:</strong> 7-12%</p>
                      <p><strong>Considerations:</strong> Wind drift, pin gaps</p>
                    </div>
                  </div>
                  
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                      <i class="fas fa-crosshairs mr-2"></i>
                      Hunting Applications
                    </h4>
                    <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                      <p><strong>Range:</strong> 100-150+ grains</p>
                      <p><strong>Match broadheads:</strong> Exact weight critical</p>
                      <p><strong>FOC Target:</strong> 12-20%</p>
                      <p><strong>Benefits:</strong> Penetration, blood trails</p>
                    </div>
                  </div>
                  
                  <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                    <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                      <i class="fas fa-mountain mr-2"></i>
                      3D Archery
                    </h4>
                    <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                      <p><strong>Typical:</strong> 100-125 grains</p>
                      <p><strong>Bullet points:</strong> Reduce target damage</p>
                      <p><strong>FOC Target:</strong> 8-15%</p>
                      <p><strong>Priority:</strong> Accuracy over penetration</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 5: Factor in Intended Use -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">5</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Factor in Your Intended Use
                </h3>
                
                <div class="bg-gradient-to-r from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 rounded-lg p-6">
                  <h4 class="text-lg font-semibold text-green-800 dark:text-green-300 mb-4">
                    Professional Use Case Considerations
                  </h4>
                  
                  <div class="grid gap-4 md:grid-cols-2">
                    <div>
                      <h5 class="font-medium text-gray-900 dark:text-white mb-3">Performance Priorities</h5>
                      <div class="space-y-3">
                        <div class="bg-white dark:bg-gray-700 rounded p-3">
                          <h6 class="font-medium text-green-800 dark:text-green-300 mb-1">Target Competition</h6>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            Prioritize consistency and precision. Lighter arrows (5-6 grains per pound) for flatter trajectory and reduced pin gaps.
                          </p>
                        </div>
                        
                        <div class="bg-white dark:bg-gray-700 rounded p-3">
                          <h6 class="font-medium text-green-800 dark:text-green-300 mb-1">Hunting Success</h6>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            Balance speed with kinetic energy. Heavier arrows (6-8+ grains per pound) for better penetration and blood trails.
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h5 class="font-medium text-gray-900 dark:text-white mb-3">Environmental Factors</h5>
                      <div class="space-y-3">
                        <div class="bg-white dark:bg-gray-700 rounded p-3">
                          <h6 class="font-medium text-blue-800 dark:text-blue-300 mb-1">Wind Conditions</h6>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            Heavier arrows with higher FOC resist wind drift better. Consider lower profile fletching for windy conditions.
                          </p>
                        </div>
                        
                        <div class="bg-white dark:bg-gray-700 rounded p-3">
                          <h6 class="font-medium text-purple-800 dark:text-purple-300 mb-1">Temperature Effects</h6>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            Cold weather increases string tension and effective draw weight. Consider slightly weaker spine for winter hunting.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Professional Selection Workflow -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-sitemap text-purple-600 dark:text-purple-400 mr-3"></i>
            Professional Selection Workflow
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            
            <!-- Decision Tree -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Decision Tree Approach
              </h3>
              
              <div class="space-y-4">
                <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300 mb-3">
                    <i class="fas fa-decision-tree mr-2"></i>
                    Selection Priority Order
                  </h4>
                  <ol class="text-sm text-indigo-700 dark:text-indigo-400 space-y-2">
                    <li><strong>1. Safety First:</strong> Ensure adequate arrow length clearance</li>
                    <li><strong>2. Calculate Base Spine:</strong> Use draw weight and arrow length</li>
                    <li><strong>3. Point Weight Effects:</strong> Adjust spine for your point weight</li>
                    <li><strong>4. Use Case Optimization:</strong> Fine-tune for intended application</li>
                    <li><strong>5. Manufacturer Verification:</strong> Cross-check with spine charts</li>
                    <li><strong>6. Testing Protocol:</strong> Paper tune and field test</li>
                  </ol>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    Professional Safety Margins
                  </h4>
                  <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
                    <p><strong>Spine Range:</strong> Test ±20 spine from calculated value</p>
                    <p><strong>Conservative Approach:</strong> Start stiffer, add point weight to tune</p>
                    <p><strong>Never Compromise:</strong> Arrow length safety clearance</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Real-World Adjustments -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Real-World Adjustments
              </h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Manufacturer Variations
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p><strong>Spine Tolerance:</strong> ±5-10 spine between brands</p>
                    <p><strong>Testing Required:</strong> Single arrows before dozen purchases</p>
                    <p><strong>Chart Differences:</strong> Some manufacturers run stiffer/weaker</p>
                    <p><strong>Quality Matters:</strong> Premium arrows have tighter tolerances</p>
                  </div>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    <i class="fas fa-adjust mr-2"></i>
                    Fine-Tuning Guidelines
                  </h4>
                  <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <p><strong>Left Tears:</strong> Try stiffer spine or lighter points</p>
                    <p><strong>Right Tears:</strong> Try weaker spine or heavier points</p>
                    <p><strong>Broadhead Tuning:</strong> May need different spine than field points</p>
                    <p><strong>Distance Testing:</strong> Verify tune at maximum shooting distance</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Arrow Setup Specifications Guide -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-cogs text-orange-600 dark:text-orange-400 mr-3"></i>
            Complete Arrow Setup Specifications
          </h2>
          
          <div class="space-y-6">
            
            <!-- Component Weight Budget -->
            <div class="bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-orange-800 dark:text-orange-300 mb-4">
                <i class="fas fa-balance-scale mr-2"></i>
                Component Weight Budget
              </h3>
              
              <div class="grid gap-4 md:grid-cols-3">
                <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
                  <h4 class="font-medium text-gray-900 dark:text-white mb-3">Shaft Weight</h4>
                  <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                    <p><strong>Formula:</strong> GPI × Arrow Length</p>
                    <p><strong>Carbon:</strong> 6-9 GPI typical</p>
                    <p><strong>Aluminum:</strong> 8-12 GPI typical</p>
                    <p><strong>Example:</strong> 8.5 GPI × 29" = 247 grains</p>
                  </div>
                </div>
                
                <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
                  <h4 class="font-medium text-gray-900 dark:text-white mb-3">Component Weights</h4>
                  <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                    <p><strong>Insert:</strong> 12-20 grains</p>
                    <p><strong>Point:</strong> 100-150 grains</p>
                    <p><strong>Nock:</strong> 8-12 grains</p>
                    <p><strong>Fletching:</strong> 15-30 grains total</p>
                  </div>
                </div>
                
                <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
                  <h4 class="font-medium text-gray-900 dark:text-white mb-3">Total Arrow Weight</h4>
                  <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                    <p><strong>Example Total:</strong> 247 + 16 + 125 + 10 + 22 = 420 grains</p>
                    <p><strong>Target Range:</strong> 350-450 grains</p>
                    <p><strong>Hunting Range:</strong> 400-550+ grains</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bow Type Specific Considerations -->
            <div class="grid gap-6 lg:grid-cols-3">
              
              <!-- Compound Bow -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  <i class="fas fa-cog text-blue-500 mr-2"></i>
                  Compound Bow Setup
                </h3>
                <div class="space-y-3">
                  <div class="bg-blue-50 dark:bg-blue-900/20 rounded p-3">
                    <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-1">Spine Considerations</h4>
                    <p class="text-sm text-blue-700 dark:text-blue-400">
                      High efficiency requires slightly stiffer arrows. Account for aggressive cam profiles and fast acceleration.
                    </p>
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded p-3">
                    <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">Arrow Rest Compatibility</h4>
                    <p class="text-sm text-green-700 dark:text-green-400">
                      Drop-away rests allow wider spine tolerance. Whisker biscuits require precise spine matching for clearance.
                    </p>
                  </div>
                </div>
              </div>

              <!-- Recurve Bow -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  <i class="fas fa-moon text-purple-500 mr-2"></i>
                  Recurve Bow Setup
                </h3>
                <div class="space-y-3">
                  <div class="bg-purple-50 dark:bg-purple-900/20 rounded p-3">
                    <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-1">Spine Requirements</h4>
                    <p class="text-sm text-purple-700 dark:text-purple-400">
                      Generally need weaker spine than compounds. Longer power stroke and different acceleration curve.
                    </p>
                  </div>
                  <div class="bg-pink-50 dark:bg-pink-900/20 rounded p-3">
                    <h4 class="font-medium text-pink-800 dark:text-pink-300 mb-1">Traditional Considerations</h4>
                    <p class="text-sm text-pink-700 dark:text-pink-400">
                      Center shot tuning more critical. Arrow paradox more pronounced with traditional shooting styles.
                    </p>
                  </div>
                </div>
              </div>

              <!-- Traditional Bow -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  <i class="fas fa-tree text-amber-500 mr-2"></i>
                  Traditional Bow Setup
                </h3>
                <div class="space-y-3">
                  <div class="bg-amber-50 dark:bg-amber-900/20 rounded p-3">
                    <h4 class="font-medium text-amber-800 dark:text-amber-300 mb-1">Arrow Paradox</h4>
                    <p class="text-sm text-amber-700 dark:text-amber-400">
                      More pronounced arrow bending around bow. Spine selection more critical for consistent flight.
                    </p>
                  </div>
                  <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded p-3">
                    <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-1">Weight Preferences</h4>
                    <p class="text-sm text-yellow-700 dark:text-yellow-400">
                      Heavier arrows (8-10+ grains per pound) work better with traditional shooting form and arrow paradox dynamics.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Common Mistakes and Solutions -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-exclamation-circle text-red-600 dark:text-red-400 mr-3"></i>
            Common Mistakes and Professional Solutions
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            
            <!-- Common Mistakes -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Avoid These Common Mistakes
              </h3>
              
              <div class="space-y-3">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-times mr-2"></i>
                    Guessing Draw Weight
                  </h4>
                  <p class="text-sm text-red-700 dark:text-red-400 mb-2">
                    <strong>Problem:</strong> Using bow's marked weight instead of actual draw weight at your length.
                  </p>
                  <p class="text-sm text-red-700 dark:text-red-400">
                    <strong>Solution:</strong> Measure with bow scale. A 70lb bow may only pull 65lbs at your draw length.
                  </p>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">
                    <i class="fas fa-times mr-2"></i>
                    Ignoring Point Weight
                  </h4>
                  <p class="text-sm text-orange-700 dark:text-orange-400 mb-2">
                    <strong>Problem:</strong> Selecting spine without considering final point weight.
                  </p>
                  <p class="text-sm text-orange-700 dark:text-orange-400">
                    <strong>Solution:</strong> Calculate spine for your actual hunting broadhead weight, not practice points.
                  </p>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    <i class="fas fa-times mr-2"></i>
                    Cutting Arrows Too Short
                  </h4>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400 mb-2">
                    <strong>Problem:</strong> Minimal safety clearance to save money or weight.
                  </p>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400">
                    <strong>Solution:</strong> Always maintain 1.5"+ clearance. Safety is never worth the risk.
                  </p>
                </div>
              </div>
            </div>

            <!-- Professional Solutions -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Professional Validation Methods
              </h3>
              
              <div class="space-y-3">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    <i class="fas fa-check mr-2"></i>
                    Cross-Reference Multiple Sources
                  </h4>
                  <p class="text-sm text-green-700 dark:text-green-400">
                    Compare manufacturer spine charts, our calculator results, and manual calculations. Look for consensus in spine recommendations.
                  </p>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-check mr-2"></i>
                    Test Multiple Spine Options
                  </h4>
                  <p class="text-sm text-blue-700 dark:text-blue-400">
                    Buy 1-3 arrows each in adjacent spine categories. Test all options through paper tuning and field testing before committing to a dozen.
                  </p>
                </div>
                
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                    <i class="fas fa-check mr-2"></i>
                    Document Your Results
                  </h4>
                  <p class="text-sm text-purple-700 dark:text-purple-400">
                    Keep detailed records of what works for your setup. Use our bow setup system to track arrow performance and tuning changes over time.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Reference Summary -->
        <div class="bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/30 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
            <i class="fas fa-bookmark mr-2"></i>
            Quick Selection Reference
          </h3>
          
          <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
              <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Target Archery</h4>
              <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p>• 5-6 grains per pound</p>
                <p>• 100-120gr points</p>
                <p>• 7-12% FOC</p>
                <p>• Carbon preferred</p>
              </div>
            </div>
            
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
              <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Hunting</h4>
              <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p>• 6-8+ grains per pound</p>
                <p>• 100-150gr points</p>
                <p>• 12-20% FOC</p>
                <p>• Match broadhead weight</p>
              </div>
            </div>
            
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
              <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">3D Archery</h4>
              <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p>• 5-7 grains per pound</p>
                <p>• 100-125gr points</p>
                <p>• 8-15% FOC</p>
                <p>• Bullet/blunt points</p>
              </div>
            </div>
            
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
              <h4 class="font-medium text-amber-800 dark:text-amber-300 mb-2">Traditional</h4>
              <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p>• 8-10+ grains per pound</p>
                <p>• 125-200gr points</p>
                <p>• 15-25% FOC</p>
                <p>• Wood/carbon options</p>
              </div>
            </div>
          </div>
          
          <div class="mt-6 flex justify-center space-x-4">
            <NuxtLink
              to="/calculator"
              class="px-6 py-3 bg-orange-600 hover:bg-orange-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-calculator mr-2"></i>
              Use Advanced Calculator
            </NuxtLink>
            <NuxtLink
              to="/my-setup"
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-archive mr-2"></i>
              Track Your Setup
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
  title: 'Arrow Selection Guide - Archery Tools',
  meta: [
    { name: 'description', content: 'Professional guide to selecting arrows based on your bow setup specifications. Includes basic spine calculator, component weight budgets, and selection methodology.' }
  ]
})
</script>

<style scoped>
/* Component specific styles */
code {
  @apply bg-gray-200 dark:bg-gray-600 px-1 py-0.5 rounded text-sm font-mono;
}
</style>