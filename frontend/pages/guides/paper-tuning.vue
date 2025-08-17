<template>
  <div>
    <!-- Breadcrumb Navigation -->
    <nav class="mb-6">
      <ol class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
        <li>
          <NuxtLink to="/guides" class="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            Guides
          </NuxtLink>
        </li>
        <li class="flex items-center">
          <i class="fas fa-chevron-right mx-2"></i>
          <span class="text-gray-900 dark:text-gray-100">Paper Tuning Guide</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl mr-4">
          <i class="fas fa-arrows-alt-h text-indigo-600 dark:text-indigo-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Paper Tuning Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Fine-tune your bow for perfect arrow flight through systematic paper testing and adjustment</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          25 min read
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-layer-group mr-2"></i>
          Intermediate to Advanced
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-cogs mr-2"></i>
          Tuning & Maintenance
        </span>
      </div>
    </div>

    <!-- Table of Contents -->
    <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl p-6 mb-8 border border-indigo-200 dark:border-indigo-800">
      <h2 class="text-lg font-semibold text-indigo-900 dark:text-indigo-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#paper-tuning-basics" class="text-indigo-700 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors">1. Paper Tuning Basics</a>
        <a href="#setup-equipment" class="text-indigo-700 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors">2. Setup & Equipment</a>
        <a href="#reading-tears" class="text-indigo-700 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors">3. Reading Paper Tears</a>
        <a href="#adjustment-process" class="text-indigo-700 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors">4. Making Adjustments</a>
        <a href="#compound-tuning" class="text-indigo-700 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors">5. Compound Bow Tuning</a>
        <a href="#recurve-tuning" class="text-indigo-700 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors">6. Recurve Bow Tuning</a>
        <a href="#troubleshooting" class="text-indigo-700 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors">7. Troubleshooting</a>
        <a href="#advanced-techniques" class="text-indigo-700 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors">8. Advanced Techniques</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Paper Tuning Basics -->
      <section id="paper-tuning-basics" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-info-circle text-blue-500 mr-3"></i>
          Paper Tuning Fundamentals
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Paper tuning is the gold standard for achieving perfect arrow flight. By shooting arrows through 
            paper and analyzing the tear patterns, you can identify and correct bow tuning issues that 
            affect accuracy, consistency, and arrow performance.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-bullseye mr-2"></i>
                What Paper Tuning Reveals
              </h3>
              <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                <li>• Arrow spine matching to bow</li>
                <li>• Rest horizontal alignment</li>
                <li>• Nocking point height accuracy</li>
                <li>• Cam timing synchronization</li>
                <li>• Arrow clearance issues</li>
                <li>• Release consistency problems</li>
              </ul>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-check-circle mr-2"></i>
                Benefits of Proper Tuning
              </h3>
              <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                <li>• Improved accuracy and consistency</li>
                <li>• Better penetration and kinetic energy</li>
                <li>• Reduced flyer arrows</li>
                <li>• Enhanced broadhead flight</li>
                <li>• Increased equipment lifespan</li>
                <li>• Greater shooting confidence</li>
              </ul>
            </div>
          </div>

          <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <h4 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Prerequisites for Paper Tuning
            </h4>
            <p class="text-amber-800 dark:text-amber-200">
              Before starting paper tuning, ensure your bow is mechanically sound, properly timed (for compounds), 
              and that you have consistent shooting form. Paper tuning will only be effective if these 
              fundamentals are already in place.
            </p>
          </div>
        </div>
      </section>

      <!-- Setup & Equipment -->
      <section id="setup-equipment" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-tools text-orange-500 mr-3"></i>
          Setup & Equipment Required
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Proper setup is crucial for accurate paper tuning results. A well-organized testing environment 
            and appropriate equipment will make the tuning process more efficient and reliable.
          </p>

          <div class="space-y-6">
            <!-- Equipment List -->
            <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-4">
                <i class="fas fa-list-check mr-2"></i>
                Required Equipment
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Essential Items</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>• <strong>Paper frame:</strong> 2-3 foot square frame</li>
                    <li>• <strong>Paper:</strong> Newsprint or butcher paper</li>
                    <li>• <strong>Backstop:</strong> Safe target material</li>
                    <li>• <strong>Measuring tape:</strong> For distance measurement</li>
                    <li>• <strong>Good lighting:</strong> Clear tear visibility</li>
                    <li>• <strong>Allen wrenches:</strong> Bow adjustment tools</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Optional but Helpful</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>• Bow square for measurements</li>
                    <li>• Level for rest alignment</li>
                    <li>• Magnifying glass for tear analysis</li>
                    <li>• Camera for documentation</li>
                    <li>• Different spine arrows for testing</li>
                    <li>• Notebook for recording adjustments</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Setup Instructions -->
            <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-orange-900 dark:text-orange-100 mb-4">
                <i class="fas fa-cog mr-2"></i>
                Paper Frame Setup
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Frame Construction</h4>
                  <ol class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>1. Build or buy a 24" x 36" frame</li>
                    <li>2. Use lightweight wood or PVC pipe</li>
                    <li>3. Ensure frame is rigid and square</li>
                    <li>4. Mount on tripod or hanging system</li>
                    <li>5. Position at comfortable shooting height</li>
                  </ol>
                </div>
                
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Distance & Safety</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>• <strong>Testing distance:</strong> 6-8 feet from paper</li>
                    <li>• <strong>Backstop distance:</strong> 2-3 feet behind paper</li>
                    <li>• <strong>Safety zone:</strong> Clear area behind backstop</li>
                    <li>• <strong>Paper placement:</strong> Center of shooting lane</li>
                    <li>• <strong>Lighting:</strong> Even illumination on paper</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Reading Paper Tears -->
      <section id="reading-tears" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-search text-purple-500 mr-3"></i>
          Reading Paper Tear Patterns
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Understanding tear patterns is the key to successful paper tuning. Each type of tear indicates 
            specific tuning issues that can be systematically corrected through proper adjustments.
          </p>

          <div class="space-y-6">
            <!-- Perfect Tear -->
            <div class="border border-green-200 dark:border-green-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
                <i class="fas fa-check-circle mr-2"></i>
                Perfect Bullet Hole
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">Characteristics</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-2">
                    <li>• Clean round hole with minimal tearing</li>
                    <li>• Three small tears from fletching</li>
                    <li>• All tears point toward center</li>
                    <li>• Consistent hole size and shape</li>
                    <li>• No excessive paper disturbance</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">What This Means</h4>
                  <p class="text-sm text-green-700 dark:text-green-300 mb-2">
                    <strong>Perfect tuning achieved!</strong> The arrow is flying straight through 
                    the paper with minimal disturbance.
                  </p>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>• Correct arrow spine for bow</li>
                    <li>• Proper rest alignment</li>
                    <li>• Good nocking point position</li>
                    <li>• Consistent release technique</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- High/Low Tears -->
            <div class="border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
                <i class="fas fa-arrows-alt-v mr-2"></i>
                High and Low Tears
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-3">High Tear Pattern</h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-300 space-y-2">
                    <li>• <strong>Appearance:</strong> Tear extends upward from hole</li>
                    <li>• <strong>Meaning:</strong> Arrow nock end hitting high</li>
                    <li>• <strong>Cause:</strong> Nocking point too low</li>
                    <li>• <strong>Fix:</strong> Raise nocking point slightly</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-3">Low Tear Pattern</h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-300 space-y-2">
                    <li>• <strong>Appearance:</strong> Tear extends downward from hole</li>
                    <li>• <strong>Meaning:</strong> Arrow nock end hitting low</li>
                    <li>• <strong>Cause:</strong> Nocking point too high</li>
                    <li>• <strong>Fix:</strong> Lower nocking point slightly</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Left/Right Tears -->
            <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-4">
                <i class="fas fa-arrows-alt-h mr-2"></i>
                Left and Right Tears
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-3">Left Tear Pattern</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-2">
                    <li>• <strong>RH Shooter:</strong> Arrow too stiff (overspined)</li>
                    <li>• <strong>LH Shooter:</strong> Arrow too weak (underspined)</li>
                    <li>• <strong>Possible causes:</strong> Rest position, arrow spine</li>
                    <li>• <strong>Adjustments:</strong> Move rest or change arrows</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-3">Right Tear Pattern</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-2">
                    <li>• <strong>RH Shooter:</strong> Arrow too weak (underspined)</li>
                    <li>• <strong>LH Shooter:</strong> Arrow too stiff (overspined)</li>
                    <li>• <strong>Possible causes:</strong> Rest position, arrow spine</li>
                    <li>• <strong>Adjustments:</strong> Move rest or change arrows</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Adjustment Process -->
      <section id="adjustment-process" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-wrench text-yellow-500 mr-3"></i>
          Systematic Adjustment Process
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Making adjustments in the correct order and increments is crucial for efficient paper tuning. 
            Small, systematic changes prevent overcorrection and lead to faster results.
          </p>

          <div class="space-y-6">
            <!-- Adjustment Order -->
            <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-yellow-900 dark:text-yellow-100 mb-4">
                <i class="fas fa-list-ol mr-2"></i>
                Proper Adjustment Sequence
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-200 mb-3">Step 1: Vertical Tuning</h4>
                  <ol class="text-sm text-yellow-700 dark:text-yellow-300 space-y-2">
                    <li>1. Address high/low tears first</li>
                    <li>2. Adjust nocking point in small increments</li>
                    <li>3. Test with 3-arrow groups</li>
                    <li>4. Continue until vertical tears eliminated</li>
                    <li>5. Document final nocking point position</li>
                  </ol>
                </div>
                
                <div>
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-200 mb-3">Step 2: Horizontal Tuning</h4>
                  <ol class="text-sm text-yellow-700 dark:text-yellow-300 space-y-2">
                    <li>1. Address left/right tears after vertical</li>
                    <li>2. Move rest left/right in small increments</li>
                    <li>3. Alternative: change arrow spine</li>
                    <li>4. Test with 3-arrow groups</li>
                    <li>5. Achieve bullet hole pattern</li>
                  </ol>
                </div>
              </div>
            </div>

            <!-- Adjustment Guidelines -->
            <div class="border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-4">
                <i class="fas fa-ruler mr-2"></i>
                Adjustment Guidelines
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-200 mb-2">Nocking Point</h4>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                    <li>• Start: 1/8" above square</li>
                    <li>• Adjust: 1/32" increments</li>
                    <li>• Range: 1/16" to 3/16" above</li>
                    <li>• Test after each change</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-200 mb-2">Rest Position</h4>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                    <li>• Start: Center of berger hole</li>
                    <li>• Adjust: 1/32" increments</li>
                    <li>• Range: Usually within 1/8"</li>
                    <li>• Mark positions for reference</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-200 mb-2">Arrow Selection</h4>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                    <li>• Try different spine weights</li>
                    <li>• Adjust point weight</li>
                    <li>• Consider arrow length</li>
                    <li>• Match to bow specifications</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Common Mistakes -->
            <div class="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
              <h4 class="font-semibold text-red-900 dark:text-red-100 mb-2">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                Common Adjustment Mistakes
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ul class="text-sm text-red-800 dark:text-red-200 space-y-1">
                  <li>• Making large adjustments too quickly</li>
                  <li>• Adjusting multiple settings simultaneously</li>
                  <li>• Not testing with enough arrows</li>
                  <li>• Ignoring form consistency issues</li>
                </ul>
                <ul class="text-sm text-red-800 dark:text-red-200 space-y-1">
                  <li>• Overcorrecting based on single shots</li>
                  <li>• Not documenting changes made</li>
                  <li>• Adjusting beyond recommended ranges</li>
                  <li>• Rushing the tuning process</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Compound Bow Tuning -->
      <section id="compound-tuning" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-cog text-green-500 mr-3"></i>
          Compound Bow Paper Tuning
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Compound bows require additional considerations due to their cam systems, let-off, and 
            mechanical complexity. Proper timing and synchronization are prerequisites for successful paper tuning.
          </p>

          <div class="space-y-6">
            <!-- Pre-tuning Checklist -->
            <div class="border border-green-200 dark:border-green-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
                <i class="fas fa-check-square mr-2"></i>
                Pre-Tuning Checklist
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">Mechanical Checks</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-2">
                    <li>• <strong>Cam timing:</strong> Both cams hit stops together</li>
                    <li>• <strong>Cam synchronization:</strong> Equal cam rotation</li>
                    <li>• <strong>Center shot:</strong> Arrow aligned with berger hole</li>
                    <li>• <strong>Rest setup:</strong> Proper arrow support</li>
                    <li>• <strong>D-loop:</strong> Centered and properly tied</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">Arrow Specifications</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-2">
                    <li>• <strong>Spine:</strong> Matched to draw weight/length</li>
                    <li>• <strong>Length:</strong> Proper clearance past rest</li>
                    <li>• <strong>Point weight:</strong> Appropriate for setup</li>
                    <li>• <strong>Fletching:</strong> Consistent and undamaged</li>
                    <li>• <strong>Nocks:</strong> Proper fit and alignment</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Compound-Specific Adjustments -->
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-4">
                <i class="fas fa-tools mr-2"></i>
                Compound Bow Adjustments
              </h3>
              
              <div class="space-y-4">
                <div class="border border-green-200 dark:border-green-700 rounded p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Rest Adjustments</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p class="text-sm text-green-700 dark:text-green-300 mb-1"><strong>Left Tear (RH):</strong></p>
                      <ul class="text-xs text-green-600 dark:text-green-400">
                        <li>• Move rest left (toward riser)</li>
                        <li>• Or try stiffer arrow spine</li>
                        <li>• Check cam timing first</li>
                      </ul>
                    </div>
                    <div>
                      <p class="text-sm text-green-700 dark:text-green-300 mb-1"><strong>Right Tear (RH):</strong></p>
                      <ul class="text-xs text-green-600 dark:text-green-400">
                        <li>• Move rest right (away from riser)</li>
                        <li>• Or try weaker arrow spine</li>
                        <li>• Verify draw length accuracy</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <div class="border border-green-200 dark:border-green-700 rounded p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Nocking Point Adjustments</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p class="text-sm text-green-700 dark:text-green-300 mb-1"><strong>High Tear:</strong></p>
                      <ul class="text-xs text-green-600 dark:text-green-400">
                        <li>• Move nocking point up</li>
                        <li>• Or move rest down slightly</li>
                        <li>• Check for cam lean</li>
                      </ul>
                    </div>
                    <div>
                      <p class="text-sm text-green-700 dark:text-green-300 mb-1"><strong>Low Tear:</strong></p>
                      <ul class="text-xs text-green-600 dark:text-green-400">
                        <li>• Move nocking point down</li>
                        <li>• Or move rest up slightly</li>
                        <li>• Verify proper draw length</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Recurve Bow Tuning -->
      <section id="recurve-tuning" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-bow-arrow text-teal-500 mr-3"></i>
          Recurve Bow Paper Tuning
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Recurve bow tuning focuses on the archer's form consistency and the dynamic interaction 
            between arrow spine and bow characteristics. Form must be consistent before equipment adjustments.
          </p>

          <div class="space-y-6">
            <!-- Recurve Considerations -->
            <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-teal-900 dark:text-teal-100 mb-4">
                <i class="fas fa-user-check mr-2"></i>
                Recurve-Specific Considerations
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-3">Form Dependencies</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-2">
                    <li>• Consistent anchor point critical</li>
                    <li>• Release technique affects results</li>
                    <li>• Bow hand grip influences tuning</li>
                    <li>• Draw length consistency required</li>
                    <li>• String picture must be repeatable</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-3">Equipment Variables</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-2">
                    <li>• Arrow spine more critical</li>
                    <li>• Point weight significantly affects flight</li>
                    <li>• String material influences performance</li>
                    <li>• Brace height affects forgiveness</li>
                    <li>• Rest type impacts arrow clearance</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Recurve Tuning Process -->
            <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-4">
                <i class="fas fa-step-forward mr-2"></i>
                Recurve Tuning Steps
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-3">Form Verification</h4>
                  <ol class="text-sm text-teal-700 dark:text-teal-300 space-y-2">
                    <li>1. Shoot blank bale to verify consistency</li>
                    <li>2. Check anchor point repeatability</li>
                    <li>3. Ensure consistent draw length</li>
                    <li>4. Verify release technique</li>
                    <li>5. Practice proper follow-through</li>
                  </ol>
                </div>
                
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-3">Equipment Adjustments</h4>
                  <ol class="text-sm text-teal-700 dark:text-teal-300 space-y-2">
                    <li>1. Set preliminary nocking point</li>
                    <li>2. Establish proper brace height</li>
                    <li>3. Begin paper tuning process</li>
                    <li>4. Adjust nocking point for vertical</li>
                    <li>5. Fine-tune with arrow selection</li>
                  </ol>
                </div>
              </div>
            </div>

            <!-- Arrow Selection Impact -->
            <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
              <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-3">
                <i class="fas fa-arrows-alt mr-2"></i>
                Arrow Selection for Recurve Tuning
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Spine Selection</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Calculate dynamic spine</li>
                    <li>• Consider draw weight</li>
                    <li>• Account for draw length</li>
                    <li>• Factor in point weight</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Point Weight Effects</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Heavier points weaken spine</li>
                    <li>• Affects vertical impact</li>
                    <li>• Changes FOC balance</li>
                    <li>• Influences penetration</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Length Considerations</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Longer arrows act weaker</li>
                    <li>• Affects clearance</li>
                    <li>• Changes dynamic spine</li>
                    <li>• Impacts arrow speed</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Troubleshooting -->
      <section id="troubleshooting" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-question-circle text-red-500 mr-3"></i>
          Troubleshooting Common Issues
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Inconsistent Results -->
              <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
                <h3 class="font-semibold text-red-900 dark:text-red-100 mb-3">
                  <i class="fas fa-random mr-2"></i>
                  Inconsistent Tear Patterns
                </h3>
                <div class="space-y-3">
                  <div>
                    <h4 class="font-medium text-red-800 dark:text-red-200">Possible Causes</h4>
                    <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                      <li>• Inconsistent shooting form</li>
                      <li>• Damaged or bent arrows</li>
                      <li>• Loose rest or nocking point</li>
                      <li>• Inconsistent release technique</li>
                    </ul>
                  </div>
                  <div>
                    <h4 class="font-medium text-red-800 dark:text-red-200">Solutions</h4>
                    <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                      <li>• Return to blank bale practice</li>
                      <li>• Check arrow straightness</li>
                      <li>• Verify equipment tightness</li>
                      <li>• Use shooting aids if needed</li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- Extreme Tears -->
              <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                <h3 class="font-semibold text-orange-900 dark:text-orange-100 mb-3">
                  <i class="fas fa-exclamation-triangle mr-2"></i>
                  Extreme Tear Patterns
                </h3>
                <div class="space-y-3">
                  <div>
                    <h4 class="font-medium text-orange-800 dark:text-orange-200">Large Tears</h4>
                    <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                      <li>• Major spine mismatch</li>
                      <li>• Significant rest misalignment</li>
                      <li>• Form breakdown issues</li>
                      <li>• Equipment malfunction</li>
                    </ul>
                  </div>
                  <div>
                    <h4 class="font-medium text-orange-800 dark:text-orange-200">Approach</h4>
                    <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                      <li>• Start with basic setup check</li>
                      <li>• Try different arrow spine</li>
                      <li>• Verify form fundamentals</li>
                      <li>• Consider professional help</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Multiple Issues -->
            <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-red-900 dark:text-red-100 mb-3">
                <i class="fas fa-layer-group mr-2"></i>
                Multiple Problem Areas
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Diagonal Tears</h4>
                  <p class="text-sm text-red-700 dark:text-red-300 mb-2">
                    When tears extend diagonally, both vertical and horizontal issues exist.
                  </p>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Address vertical issues first</li>
                    <li>• Then correct horizontal problems</li>
                    <li>• Work systematically</li>
                    <li>• Don't rush the process</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">No Improvement</h4>
                  <p class="text-sm text-red-700 dark:text-red-300 mb-2">
                    When adjustments don't improve tears significantly.
                  </p>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Check equipment fundamentals</li>
                    <li>• Verify measurement accuracy</li>
                    <li>• Consider form coaching</li>
                    <li>• Try different arrow combinations</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Advanced Techniques -->
      <section id="advanced-techniques" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-graduation-cap text-purple-500 mr-3"></i>
          Advanced Paper Tuning Techniques
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <!-- Multiple Distance Testing -->
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                <i class="fas fa-ruler-combined mr-2"></i>
                Multiple Distance Testing
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Distance Variation</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Start at 6 feet for initial tuning</li>
                    <li>• Test at 10 feet for verification</li>
                    <li>• Try 15 feet for fine-tuning</li>
                    <li>• Patterns should remain consistent</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">What Distance Shows</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Closer reveals immediate flight issues</li>
                    <li>• Farther shows stability problems</li>
                    <li>• Consistency across distances = good tune</li>
                    <li>• Changing patterns indicate instability</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Broadhead Tuning -->
            <div class="border border-purple-200 dark:border-purple-800 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                <i class="fas fa-crosshairs mr-2"></i>
                Broadhead Paper Tuning
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Process</h4>
                  <ol class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>1. First achieve perfect field point tune</li>
                    <li>2. Switch to fixed-blade broadheads</li>
                    <li>3. Expect slightly larger tears initially</li>
                    <li>4. Fine-tune rest position if needed</li>
                    <li>5. Verify with multiple broadheads</li>
                  </ol>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Considerations</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Broadheads are less forgiving</li>
                    <li>• Small tune differences become apparent</li>
                    <li>• Wind planning becomes important</li>
                    <li>• May require spine adjustments</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Environmental Factors -->
            <div class="border border-purple-200 dark:border-purple-800 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                <i class="fas fa-wind mr-2"></i>
                Environmental Considerations
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Temperature Effects</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Cold weather stiffens arrows</li>
                    <li>• Heat can soften arrow spine</li>
                    <li>• Bowstring performance changes</li>
                    <li>• Test in actual conditions</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Humidity Impact</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Affects arrow flight slightly</li>
                    <li>• Changes paper behavior</li>
                    <li>• Influences string performance</li>
                    <li>• Consistent conditions preferred</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Altitude Considerations</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Air density affects arrow flight</li>
                    <li>• Higher altitude = less air resistance</li>
                    <li>• May affect spine requirements</li>
                    <li>• Re-verify at hunting elevation</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Conclusion -->
      <section class="mb-12">
        <div class="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl p-6 border border-indigo-200 dark:border-indigo-800">
          <h2 class="text-2xl font-bold text-indigo-900 dark:text-indigo-100 mb-4">
            <i class="fas fa-trophy mr-3"></i>
            Paper Tuning Mastery
          </h2>
          <p class="text-indigo-800 dark:text-indigo-200 mb-4">
            Paper tuning is both an art and a science. Success requires patience, systematic approach, 
            and understanding that perfect tuning is a process, not a destination. A well-tuned bow 
            rewards you with improved accuracy, consistency, and confidence in your equipment.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-indigo-200 dark:border-indigo-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Key Success Factors</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Systematic approach to adjustments</li>
                <li>• Consistent shooting form first</li>
                <li>• Small incremental changes</li>
                <li>• Patience with the process</li>
              </ul>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-indigo-200 dark:border-indigo-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Maintenance Schedule</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Check tune before hunting season</li>
                <li>• Re-verify after equipment changes</li>
                <li>• Test with new arrow batches</li>
                <li>• Annual comprehensive tuning</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- Related Guides -->
      <section class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Related Guides</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <NuxtLink 
            to="/guides/sight-setup"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-bullseye text-purple-600 dark:text-purple-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-purple-600 dark:group-hover:text-purple-400">
                Sight Setup & Tuning
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Configure your bow sight after achieving perfect paper tune.
            </p>
          </NuxtLink>

          <div class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-yellow-300 dark:hover:border-yellow-600 transition-colors group">
            <div class="flex items-center mb-2">
              <i class="fas fa-wrench text-yellow-600 dark:text-yellow-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-yellow-600 dark:group-hover:text-yellow-400">
                Rest Adjustment
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Coming soon - Fine-tune rest position for optimal clearance.
            </p>
          </div>

          <div class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 opacity-60">
            <div class="flex items-center mb-2">
              <i class="fas fa-broom text-gray-400 mr-3"></i>
              <h3 class="font-semibold text-gray-500 dark:text-gray-400">
                Equipment Maintenance
              </h3>
            </div>
            <p class="text-sm text-gray-400">
              Coming soon - Keep your equipment in perfect working order.
            </p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
// Set page title and meta
useHead({
  title: 'Paper Tuning Guide - Perfect Arrow Flight Through Systematic Bow Tuning',
  meta: [
    { name: 'description', content: 'Complete paper tuning guide for compound and recurve bows. Learn to read tear patterns, make systematic adjustments, and achieve perfect arrow flight.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  // No authentication required - public guide
})
</script>