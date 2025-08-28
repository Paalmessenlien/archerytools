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
          <span class="text-gray-900 dark:text-gray-100">Rest Adjustment Guide</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-xl mr-4">
          <i class="fas fa-wrench text-yellow-600 dark:text-yellow-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Rest Adjustment Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Optimize arrow rest position for perfect clearance and consistent arrow flight</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          18 min read
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
    <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-6 mb-8 border border-yellow-200 dark:border-yellow-800">
      <h2 class="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#rest-basics" class="text-yellow-700 dark:text-yellow-300 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors">1. Arrow Rest Basics</a>
        <a href="#rest-types" class="text-yellow-700 dark:text-yellow-300 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors">2. Rest Types & Selection</a>
        <a href="#initial-setup" class="text-yellow-700 dark:text-yellow-300 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors">3. Initial Setup Process</a>
        <a href="#horizontal-adjustment" class="text-yellow-700 dark:text-yellow-300 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors">4. Horizontal Adjustment</a>
        <a href="#vertical-adjustment" class="text-yellow-700 dark:text-yellow-300 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors">5. Vertical Adjustment</a>
        <a href="#timing-adjustment" class="text-yellow-700 dark:text-yellow-300 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors">6. Rest Timing</a>
        <a href="#fine-tuning" class="text-yellow-700 dark:text-yellow-300 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors">7. Fine-Tuning Process</a>
        <a href="#troubleshooting" class="text-yellow-700 dark:text-yellow-300 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors">8. Troubleshooting</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Rest Basics -->
      <section id="rest-basics" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-info-circle text-blue-500 mr-3"></i>
          Arrow Rest Fundamentals
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            The arrow rest is the critical interface between your arrow and bow. Proper rest adjustment 
            ensures consistent arrow positioning, optimal clearance, and predictable flight characteristics. 
            Even small rest misalignments can significantly impact accuracy and consistency.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-bullseye mr-2"></i>
                Rest Functions
              </h3>
              <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                <li>• Support arrow during draw and hold</li>
                <li>• Provide consistent positioning reference</li>
                <li>• Allow clean arrow clearance on release</li>
                <li>• Maintain proper spine tuning relationship</li>
                <li>• Enable precise horizontal/vertical adjustment</li>
                <li>• Accommodate different arrow diameters</li>
              </ul>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-check-circle mr-2"></i>
                Proper Rest Setup Benefits
              </h3>
              <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                <li>• Improved accuracy and consistency</li>
                <li>• Better broadhead flight performance</li>
                <li>• Reduced fletching wear and damage</li>
                <li>• Enhanced arrow clearance</li>
                <li>• Optimal spine tuning results</li>
                <li>• Increased shooting confidence</li>
              </ul>
            </div>
          </div>

          <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <h4 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Critical Rest Adjustment Principle
            </h4>
            <p class="text-amber-800 dark:text-amber-200">
              <strong>Always start with mechanical soundness:</strong> Ensure your bow is properly timed, 
              cams are synchronized (compounds), and all components are securely fastened before beginning 
              rest adjustments. A mechanically unsound bow cannot be properly tuned.
            </p>
          </div>
        </div>
      </section>

      <!-- Rest Types -->
      <section id="rest-types" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-th-large text-orange-500 mr-3"></i>
          Arrow Rest Types & Selection
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Understanding different rest types and their adjustment characteristics is crucial for 
            selecting the right rest for your bow and shooting style. Each type has unique advantages 
            and adjustment procedures.
          </p>

          <div class="space-y-6">
            <!-- Compound Bow Rests -->
            <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-4">
                <i class="fas fa-cog mr-2"></i>
                Compound Bow Rests
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Drop-Away Rests</h4>
                  <div class="space-y-2 text-sm text-orange-700 dark:text-orange-300">
                    <p><strong>Characteristics:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• Full arrow containment during draw</li>
                      <li>• Complete clearance on release</li>
                      <li>• Timing-dependent operation</li>
                      <li>• Excellent for broadheads</li>
                    </ul>
                    
                    <p><strong>Adjustment considerations:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• Requires precise timing setup</li>
                      <li>• Horizontal/vertical micro-adjustments</li>
                      <li>• Launcher blade tension settings</li>
                    </ul>
                  </div>
                </div>
                
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Containment Rests</h4>
                  <div class="space-y-2 text-sm text-orange-700 dark:text-orange-300">
                    <p><strong>Characteristics:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• Two-prong or whisker biscuit design</li>
                      <li>• Constant arrow contact</li>
                      <li>• No timing requirements</li>
                      <li>• Forgiving and reliable</li>
                    </ul>
                    
                    <p><strong>Adjustment considerations:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• Simple horizontal/vertical adjustments</li>
                      <li>• Center shot alignment critical</li>
                      <li>• May require fletching clearance tuning</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Recurve Bow Rests -->
            <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-4">
                <i class="fas fa-bow-arrow mr-2"></i>
                Recurve Bow Rests
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Stick-On Rests</h4>
                  <div class="space-y-2 text-sm text-orange-700 dark:text-orange-300">
                    <p><strong>Characteristics:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• Simple plastic or metal shelf</li>
                      <li>• Minimal arrow contact</li>
                      <li>• Low profile and lightweight</li>
                      <li>• Cost-effective solution</li>
                    </ul>
                    
                    <p><strong>Adjustment limitations:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• Fixed vertical position</li>
                      <li>• Limited horizontal adjustment</li>
                      <li>• Requires precise initial placement</li>
                    </ul>
                  </div>
                </div>
                
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Magnetic/Pressure Button</h4>
                  <div class="space-y-2 text-sm text-orange-700 dark:text-orange-300">
                    <p><strong>Characteristics:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• Adjustable pressure button system</li>
                      <li>• Magnetic arrow support</li>
                      <li>• Fine-tuning capabilities</li>
                      <li>• Olympic/target archery standard</li>
                    </ul>
                    
                    <p><strong>Adjustment features:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• Precise horizontal positioning</li>
                      <li>• Spring tension adjustment</li>
                      <li>• Micro-adjustment capabilities</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Initial Setup -->
      <section id="initial-setup" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-play-circle text-purple-500 mr-3"></i>
          Initial Setup Process
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Proper initial setup creates a solid foundation for fine-tuning. Starting with correct 
            basic positioning saves time and ensures optimal results throughout the adjustment process.
          </p>

          <div class="space-y-6">
            <!-- Basic Positioning -->
            <div class="border border-purple-200 dark:border-purple-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-4">
                <i class="fas fa-crosshairs mr-2"></i>
                Center Shot Alignment
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-3">Finding Center Shot</h4>
                  <ol class="text-sm text-purple-700 dark:text-purple-300 space-y-2">
                    <li>1. <strong>Berger hole method:</strong> Look through riser from back</li>
                    <li>2. Position arrow so shaft appears centered in hole</li>
                    <li>3. Adjust rest horizontally to achieve alignment</li>
                    <li>4. Use bow square to verify measurements</li>
                    <li>5. Mark initial position for reference</li>
                  </ol>
                </div>
                
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-3">Alternative Methods</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-2">
                    <li>• <strong>String alignment:</strong> Sight down string to arrow</li>
                    <li>• <strong>Measurement method:</strong> Equal distances from riser</li>
                    <li>• <strong>Laser alignment:</strong> Use laser bore sighter</li>
                    <li>• <strong>Professional setup:</strong> Bow shop alignment</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Vertical Positioning -->
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-4">
                <i class="fas fa-arrows-alt-v mr-2"></i>
                Initial Vertical Positioning
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-3">Compound Bow Setup</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-2">
                    <li>• Position rest for level arrow at full draw</li>
                    <li>• Nock point 1/8" above square (starting point)</li>
                    <li>• Ensure arrow clears rest at full draw</li>
                    <li>• Allow for drop-away rest timing</li>
                    <li>• Check clearance with broadheads</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-3">Recurve Bow Setup</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-2">
                    <li>• Set nock point 3/8" to 1/2" above square</li>
                    <li>• Position rest to support arrow shaft center</li>
                    <li>• Ensure proper pressure button contact</li>
                    <li>• Allow for arrow flexing during paradox</li>
                    <li>• Test with intended arrow spine</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Tools and Measurements -->
            <div class="border border-purple-200 dark:border-purple-800 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                <i class="fas fa-tools mr-2"></i>
                Essential Setup Tools
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Measurement Tools</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Bow square</li>
                    <li>• Measuring tape</li>
                    <li>• Calipers (precision work)</li>
                    <li>• String level</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Adjustment Tools</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Allen wrench set</li>
                    <li>• Screwdrivers</li>
                    <li>• Needle-nose pliers</li>
                    <li>• Rest-specific tools</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Marking/Reference</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Permanent marker</li>
                    <li>• Masking tape</li>
                    <li>• Notebook for records</li>
                    <li>• Camera for documentation</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Horizontal Adjustment -->
      <section id="horizontal-adjustment" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-arrows-alt-h text-green-500 mr-3"></i>
          Horizontal Rest Adjustment
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Horizontal rest position directly affects arrow spine tuning and left/right impact. 
            Small adjustments can have significant effects on accuracy and consistency.
          </p>

          <div class="space-y-6">
            <!-- Paper Tuning Integration -->
            <div class="border border-green-200 dark:border-green-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
                <i class="fas fa-file-alt mr-2"></i>
                Using Paper Tuning for Horizontal Adjustment
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">Reading Horizontal Tears</h4>
                  <div class="space-y-2 text-sm text-green-700 dark:text-green-300">
                    <p><strong>Right-hand shooter:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• <strong>Left tear:</strong> Arrow too stiff, move rest left</li>
                      <li>• <strong>Right tear:</strong> Arrow too weak, move rest right</li>
                    </ul>
                    
                    <p><strong>Left-hand shooter:</strong></p>
                    <ul class="space-y-1 ml-4">
                      <li>• <strong>Left tear:</strong> Arrow too weak, move rest right</li>
                      <li>• <strong>Right tear:</strong> Arrow too stiff, move rest left</li>
                    </ul>
                  </div>
                </div>
                
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">Adjustment Increments</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-2">
                    <li>• <strong>Initial adjustments:</strong> 1/16" (1.5mm)</li>
                    <li>• <strong>Fine-tuning:</strong> 1/32" (0.8mm)</li>
                    <li>• <strong>Micro-adjustments:</strong> 1/64" (0.4mm)</li>
                    <li>• <strong>Test after each change:</strong> 3-shot groups</li>
                    <li>• <strong>Document all changes:</strong> Keep records</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Walk-Back Tuning -->
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-4">
                <i class="fas fa-walking mr-2"></i>
                Walk-Back Tuning Method
              </h3>
              
              <div class="space-y-4">
                <div class="border border-green-200 dark:border-green-700 rounded p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Setup Process</h4>
                  <ol class="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>1. Set up target at 20 yards with vertical tape line</li>
                    <li>2. Shoot one arrow at 20 yards, mark impact</li>
                    <li>3. Move back to 30, 40, and 50 yards</li>
                    <li>4. Aim at same point, shoot without sight adjustment</li>
                    <li>5. Check if arrows track straight up/down</li>
                  </ol>
                </div>
                
                <div class="border border-green-200 dark:border-green-700 rounded p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Reading Results</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p class="text-sm text-green-700 dark:text-green-300 font-medium mb-1">Perfect Tune:</p>
                      <p class="text-xs text-green-600 dark:text-green-400">All arrows hit in vertical line</p>
                    </div>
                    <div>
                      <p class="text-sm text-green-700 dark:text-green-300 font-medium mb-1">Needs Adjustment:</p>
                      <p class="text-xs text-green-600 dark:text-green-400">Arrows drift left or right with distance</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Rest-Specific Adjustments -->
            <div class="border border-green-200 dark:border-green-800 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-cogs mr-2"></i>
                Rest-Specific Horizontal Adjustments
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Drop-Away Rests</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>• Use windage adjustment screws</li>
                    <li>• Make adjustments with rest armed</li>
                    <li>• Check launcher blade alignment</li>
                    <li>• Verify timing after adjustments</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Containment Rests</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>• Adjust entire rest assembly</li>
                    <li>• Maintain equal fletching clearance</li>
                    <li>• Check for center shot alignment</li>
                    <li>• Verify arrow retention security</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Vertical Adjustment -->
      <section id="vertical-adjustment" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-arrows-alt-v text-red-500 mr-3"></i>
          Vertical Rest Adjustment
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Vertical rest position works in conjunction with nocking point height to control 
            arrow flight trajectory and vertical impact patterns. Both components must be 
            properly coordinated for optimal results.
          </p>

          <div class="space-y-6">
            <!-- Nock Point Relationship -->
            <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-4">
                <i class="fas fa-link mr-2"></i>
                Rest Height and Nock Point Coordination
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-3">Compound Bow Coordination</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-2">
                    <li>• Rest height affects arrow angle at full draw</li>
                    <li>• Nock point provides upper reference</li>
                    <li>• Both influence vertical impact</li>
                    <li>• Adjust one parameter at a time</li>
                    <li>• Usually adjust nock point first</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-3">Recurve Bow Considerations</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-2">
                    <li>• Rest height affects arrow paradox</li>
                    <li>• Higher rest reduces clearance issues</li>
                    <li>• Lower rest may improve consistency</li>
                    <li>• Pressure button height coordination</li>
                    <li>• Balance with nock point position</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Vertical Tuning Methods -->
            <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-red-900 dark:text-red-100 mb-4">
                <i class="fas fa-target mr-2"></i>
                Vertical Tuning Techniques
              </h3>
              
              <div class="space-y-4">
                <div class="border border-red-200 dark:border-red-700 rounded p-3">
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Paper Tuning Method</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p class="text-sm text-red-700 dark:text-red-300 mb-1"><strong>High Tear Pattern:</strong></p>
                      <ul class="text-xs text-red-600 dark:text-red-400 space-y-1">
                        <li>• Nock point too low</li>
                        <li>• Or rest position too high</li>
                        <li>• Move nock point up 1/32"</li>
                        <li>• Or lower rest slightly</li>
                      </ul>
                    </div>
                    <div>
                      <p class="text-sm text-red-700 dark:text-red-300 mb-1"><strong>Low Tear Pattern:</strong></p>
                      <ul class="text-xs text-red-600 dark:text-red-400 space-y-1">
                        <li>• Nock point too high</li>
                        <li>• Or rest position too low</li>
                        <li>• Move nock point down 1/32"</li>
                        <li>• Or raise rest slightly</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <div class="border border-red-200 dark:border-red-700 rounded p-3">
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Group Tuning Method</h4>
                  <ol class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>1. Shoot 3-arrow groups at known distance</li>
                    <li>2. Make small vertical adjustments</li>
                    <li>3. Look for tightest vertical grouping</li>
                    <li>4. Fine-tune for best overall group size</li>
                    <li>5. Verify with multiple distances</li>
                  </ol>
                </div>
              </div>
            </div>

            <!-- Clearance Considerations -->
            <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
              <h3 class="font-semibold text-red-900 dark:text-red-100 mb-3">
                <i class="fas fa-eye mr-2"></i>
                Clearance and Safety Checks
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Minimum Clearances</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Arrow to shelf: 1/8" minimum</li>
                    <li>• Fletching to riser: 1/4" minimum</li>
                    <li>• Broadhead to rest: 1/16" minimum</li>
                    <li>• Account for arrow flex</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Testing Methods</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Lipstick test on fletching</li>
                    <li>• Powder spray on contact points</li>
                    <li>• Visual inspection after shots</li>
                    <li>• Listen for contact sounds</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Rest Timing -->
      <section id="timing-adjustment" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-clock text-teal-500 mr-3"></i>
          Drop-Away Rest Timing
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Drop-away rest timing is critical for proper arrow support and clearance. The rest must 
            drop at precisely the right moment to ensure clean arrow departure while maintaining 
            support throughout the shot cycle.
          </p>

          <div class="space-y-6">
            <!-- Timing Principles -->
            <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-teal-900 dark:text-teal-100 mb-4">
                <i class="fas fa-info-circle mr-2"></i>
                Timing Fundamentals
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-3">Optimal Timing Window</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-2">
                    <li>• Rest drops when arrow clears nock</li>
                    <li>• Occurs approximately 65-75% let-off point</li>
                    <li>• Arrow maintains contact until fletching clears</li>
                    <li>• Complete drop before fletching passes</li>
                    <li>• Consistent timing across draw speeds</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-3">Timing Problems</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-2">
                    <li>• <strong>Early drop:</strong> Arrow falls before release</li>
                    <li>• <strong>Late drop:</strong> Fletching contact with rest</li>
                    <li>• <strong>Inconsistent:</strong> Variable arrow flight</li>
                    <li>• <strong>No drop:</strong> Mechanical failure</li>
                    <li>• <strong>Partial drop:</strong> Incomplete clearance</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Timing Adjustment Methods -->
            <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-4">
                <i class="fas fa-wrench mr-2"></i>
                Timing Adjustment Procedures
              </h3>
              
              <div class="space-y-4">
                <div class="border border-teal-200 dark:border-teal-700 rounded p-3">
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Cable-Driven Rests</h4>
                  <ol class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>1. Locate timing cable attachment point</li>
                    <li>2. Adjust cable position on cam or draw stop</li>
                    <li>3. Later timing: Move attachment toward cam</li>
                    <li>4. Earlier timing: Move attachment away from cam</li>
                    <li>5. Test timing with slow-motion video if possible</li>
                  </ol>
                </div>
                
                <div class="border border-teal-200 dark:border-teal-700 rounded p-3">
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Limb-Driven Rests</h4>
                  <ol class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>1. Adjust limb attachment position</li>
                    <li>2. Higher on limb = earlier drop</li>
                    <li>3. Lower on limb = later drop</li>
                    <li>4. Ensure secure attachment</li>
                    <li>5. Check for limb clearance issues</li>
                  </ol>
                </div>
              </div>
            </div>

            <!-- Timing Verification -->
            <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
              <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-3">
                <i class="fas fa-check-double mr-2"></i>
                Timing Verification Methods
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Visual Inspection</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Draw bow slowly and observe</li>
                    <li>• Check drop point consistency</li>
                    <li>• Look for smooth operation</li>
                    <li>• Verify complete retraction</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Sound Testing</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Listen for contact sounds</li>
                    <li>• Fletching should be silent</li>
                    <li>• Mechanical sounds indicate issues</li>
                    <li>• Record for comparison</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Performance Testing</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Shoot groups for consistency</li>
                    <li>• Check fletching for wear</li>
                    <li>• Test with different arrows</li>
                    <li>• Verify broadhead performance</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Fine-Tuning -->
      <section id="fine-tuning" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-adjust text-indigo-500 mr-3"></i>
          Fine-Tuning Process
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Fine-tuning rest adjustments requires systematic testing and incremental changes. 
            The goal is to achieve the smallest possible groups while maintaining consistent 
            arrow flight across different conditions.
          </p>

          <div class="space-y-6">
            <!-- Systematic Testing -->
            <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-4">
                <i class="fas fa-chart-line mr-2"></i>
                Systematic Testing Protocol
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-3">Testing Sequence</h4>
                  <ol class="text-sm text-indigo-700 dark:text-indigo-300 space-y-2">
                    <li>1. <strong>Baseline:</strong> Shoot 5-shot group, record</li>
                    <li>2. <strong>Adjust:</strong> Make single small change</li>
                    <li>3. <strong>Test:</strong> Shoot another 5-shot group</li>
                    <li>4. <strong>Compare:</strong> Measure group size improvement</li>
                    <li>5. <strong>Iterate:</strong> Continue in same direction if better</li>
                    <li>6. <strong>Reverse:</strong> Go opposite direction if worse</li>
                  </ol>
                </div>
                
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-3">Documentation</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-2">
                    <li>• Record all adjustment measurements</li>
                    <li>• Photo document target results</li>
                    <li>• Note environmental conditions</li>
                    <li>• Track which direction improves groups</li>
                    <li>• Mark optimal settings for reference</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Group Analysis -->
            <div class="border border-indigo-200 dark:border-indigo-800 rounded-lg p-4">
              <h3 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-3">
                <i class="fas fa-search-plus mr-2"></i>
                Group Analysis Techniques
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Measurement Methods</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Center-to-center distances</li>
                    <li>• Extreme spread measurements</li>
                    <li>• Vertical vs. horizontal dispersion</li>
                    <li>• Statistical group analysis</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Pattern Recognition</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Consistent directional misses</li>
                    <li>• Vertical or horizontal stringing</li>
                    <li>• Flyer arrow patterns</li>
                    <li>• Group shape characteristics</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Optimization Targets -->
            <div class="border border-indigo-200 dark:border-indigo-800 rounded-lg p-4">
              <h3 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-3">
                <i class="fas fa-bullseye mr-2"></i>
                Optimization Goals
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Target Archery</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Smallest possible groups</li>
                    <li>• Consistent point of impact</li>
                    <li>• Wind resistance optimization</li>
                    <li>• Competition distance accuracy</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Hunting</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Broadhead/field point matching</li>
                    <li>• Multiple distance consistency</li>
                    <li>• Maximum kinetic energy retention</li>
                    <li>• Field condition reliability</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">3D Archery</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Unknown distance accuracy</li>
                    <li>• Angle compensation ability</li>
                    <li>• Varied target size precision</li>
                    <li>• Weather condition stability</li>
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
          Troubleshooting Rest Issues
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Mechanical Problems -->
              <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
                <h3 class="font-semibold text-red-900 dark:text-red-100 mb-3">
                  <i class="fas fa-cog mr-2"></i>
                  Mechanical Issues
                </h3>
                <div class="space-y-3">
                  <div>
                    <h4 class="font-medium text-red-800 dark:text-red-200">Rest Won't Drop</h4>
                    <div class="text-sm text-red-700 dark:text-red-300">
                      <p><strong>Causes:</strong> Cable binding, inadequate force, mechanical failure</p>
                      <p><strong>Solutions:</strong> Check cable routing, adjust tension, lubricate pivots</p>
                    </div>
                  </div>
                  <div>
                    <h4 class="font-medium text-red-800 dark:text-red-200">Inconsistent Operation</h4>
                    <div class="text-sm text-red-700 dark:text-red-300">
                      <p><strong>Causes:</strong> Loose fasteners, worn components, debris</p>
                      <p><strong>Solutions:</strong> Tighten all screws, clean mechanism, replace worn parts</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Flight Problems -->
              <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                <h3 class="font-semibold text-orange-900 dark:text-orange-100 mb-3">
                  <i class="fas fa-crosshairs mr-2"></i>
                  Arrow Flight Issues
                </h3>
                <div class="space-y-3">
                  <div>
                    <h4 class="font-medium text-orange-800 dark:text-orange-200">Erratic Groups</h4>
                    <div class="text-sm text-orange-700 dark:text-orange-300">
                      <p><strong>Causes:</strong> Timing inconsistency, contact issues, rest movement</p>
                      <p><strong>Solutions:</strong> Verify timing, check clearances, secure all adjustments</p>
                    </div>
                  </div>
                  <div>
                    <h4 class="font-medium text-orange-800 dark:text-orange-200">Poor Broadhead Flight</h4>
                    <div class="text-sm text-orange-700 dark:text-orange-300">
                      <p><strong>Causes:</strong> Rest contact, timing issues, insufficient support</p>
                      <p><strong>Solutions:</strong> Optimize timing, ensure complete drop, check spine match</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Diagnostic Procedures -->
            <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-red-900 dark:text-red-100 mb-3">
                <i class="fas fa-stethoscope mr-2"></i>
                Diagnostic Procedures
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Contact Testing</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Spray powder on fletching</li>
                    <li>• Use lipstick on rest contact points</li>
                    <li>• Listen for contact sounds</li>
                    <li>• Examine fletching for wear marks</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Timing Analysis</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Film shot cycle in slow motion</li>
                    <li>• Mark rest position during draw</li>
                    <li>• Check consistency across shots</li>
                    <li>• Verify complete retraction</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Common Solutions -->
            <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
              <h3 class="font-semibold text-red-900 dark:text-red-100 mb-3">
                <i class="fas fa-tools mr-2"></i>
                Common Solutions
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Maintenance Tasks</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Regular cleaning and lubrication</li>
                    <li>• Tighten all fasteners</li>
                    <li>• Replace worn components</li>
                    <li>• Check cable condition</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Adjustment Checks</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Verify all settings after transport</li>
                    <li>• Re-check after bow tuning changes</li>
                    <li>• Confirm timing after cam work</li>
                    <li>• Test with different arrow types</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Replacement Indicators</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Excessive wear on pivot points</li>
                    <li>• Cracked or bent components</li>
                    <li>• Inconsistent operation despite adjustment</li>
                    <li>• Unable to achieve proper timing</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Conclusion -->
      <section class="mb-12">
        <div class="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-xl p-6 border border-yellow-200 dark:border-yellow-800">
          <h2 class="text-2xl font-bold text-yellow-900 dark:text-yellow-100 mb-4">
            <i class="fas fa-trophy mr-3"></i>
            Rest Adjustment Mastery
          </h2>
          <p class="text-yellow-800 dark:text-yellow-200 mb-4">
            Proper rest adjustment is a cornerstone of accurate archery. A well-adjusted rest provides 
            consistent arrow positioning, optimal clearance, and predictable flight characteristics. 
            Take time to understand your rest's operation and make systematic adjustments for best results.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-yellow-200 dark:border-yellow-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Key Success Principles</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Start with mechanical soundness</li>
                <li>• Make small, systematic adjustments</li>
                <li>• Test thoroughly after each change</li>
                <li>• Document settings and results</li>
              </ul>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-yellow-200 dark:border-yellow-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Maintenance Schedule</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Weekly: Visual inspection and cleaning</li>
                <li>• Monthly: Comprehensive adjustment check</li>
                <li>• Seasonally: Complete rest service</li>
                <li>• As needed: After bow modifications</li>
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
            to="/guides/paper-tuning"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-arrows-alt-h text-indigo-600 dark:text-indigo-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                Paper Tuning Guide
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Use paper tuning to optimize your rest adjustments.
            </p>
          </NuxtLink>

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
              Configure your sight after optimizing rest position.
            </p>
          </NuxtLink>

          <div class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 opacity-60">
            <div class="flex items-center mb-2">
              <i class="fas fa-broom text-gray-400 mr-3"></i>
              <h3 class="font-semibold text-gray-500 dark:text-gray-400">
                Equipment Maintenance
              </h3>
            </div>
            <p class="text-sm text-gray-400">
              Coming soon - Keep your rest in perfect working condition.
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
  title: 'Rest Adjustment Guide - Optimize Arrow Rest Position for Perfect Flight',
  meta: [
    { name: 'description', content: 'Complete arrow rest adjustment guide covering horizontal, vertical, and timing adjustments for compound and recurve bows. Achieve perfect arrow clearance and flight.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})
</script>