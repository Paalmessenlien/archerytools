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
          <span class="text-gray-900 dark:text-gray-100">Sight Setup & Tuning</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl mr-4">
          <i class="fas fa-bullseye text-purple-600 dark:text-purple-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Sight Setup & Tuning Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Master the art of bow sight installation, calibration, and fine-tuning for precision shooting</p>
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
          <i class="fas fa-tools mr-2"></i>
          Equipment Setup
        </span>
      </div>
    </div>

    <!-- Table of Contents -->
    <div class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-6 mb-8 border border-purple-200 dark:border-purple-800">
      <h2 class="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#sight-types" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">1. Types of Bow Sights</a>
        <a href="#installation" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">2. Installation Process</a>
        <a href="#initial-setup" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">3. Initial Setup</a>
        <a href="#calibration" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">4. Sight Calibration</a>
        <a href="#fine-tuning" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">5. Fine-Tuning Process</a>
        <a href="#maintenance" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">6. Maintenance & Care</a>
        <a href="#troubleshooting" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">7. Troubleshooting</a>
        <a href="#advanced-tips" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">8. Advanced Tips</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Types of Bow Sights -->
      <section id="sight-types" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-eye text-blue-500 mr-3"></i>
          Types of Bow Sights
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Understanding different sight types is crucial for choosing the best option for your shooting style and purpose.
          </p>

          <!-- Illustration -->
          <div class="illustration-container mb-6 bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
            <!-- TODO: Add sight types illustration -->
            <div class="w-full max-w-2xl mx-auto h-48 bg-purple-100 dark:bg-purple-800 rounded-lg flex items-center justify-center">
              <div class="text-center text-purple-600 dark:text-purple-300">
                <i class="fas fa-image text-4xl mb-2"></i>
                <p class="text-sm">Sight Types Comparison</p>
              </div>
            </div>
            <p class="text-sm text-purple-700 dark:text-purple-300 text-center mt-3">
              <i class="fas fa-bullseye mr-2"></i>
              Choose the sight type that matches your archery discipline and skill level
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-dot-circle mr-2"></i>
                Single Pin Sights
              </h3>
              <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                <li>• Adjustable for different distances</li>
                <li>• Clean sight picture with minimal clutter</li>
                <li>• Popular for hunting applications</li>
                <li>• Requires distance estimation skills</li>
              </ul>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-bars mr-2"></i>
                Multi-Pin Sights
              </h3>
              <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                <li>• Fixed pins for preset distances</li>
                <li>• Quick target acquisition</li>
                <li>• Ideal for 3D archery and hunting</li>
                <li>• Usually 3-7 pins (20-70 yards)</li>
              </ul>
            </div>
            
            <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-amber-900 dark:text-amber-100 mb-3">
                <i class="fas fa-crosshairs mr-2"></i>
                Target Sights
              </h3>
              <ul class="text-sm text-amber-800 dark:text-amber-200 space-y-2">
                <li>• Precision micro-adjustments</li>
                <li>• Large aperture with target rings</li>
                <li>• Tournament and target shooting</li>
                <li>• Extension bars for increased accuracy</li>
              </ul>
            </div>
            
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                <i class="fas fa-magic mr-2"></i>
                Pendulum Sights
              </h3>
              <ul class="text-sm text-purple-800 dark:text-purple-200 space-y-2">
                <li>• Gravity-activated pin adjustment</li>
                <li>• Compensates for shooting angles</li>
                <li>• Specialized for treestand hunting</li>
                <li>• Limited effective range</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- Installation Process -->
      <section id="installation" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-wrench text-orange-500 mr-3"></i>
          Installation Process
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 mb-6 border border-red-200 dark:border-red-800">
            <div class="flex items-start">
              <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 mt-1 mr-3"></i>
              <div>
                <h4 class="font-semibold text-red-900 dark:text-red-100 mb-2">Safety First</h4>
                <p class="text-sm text-red-800 dark:text-red-200">
                  Always ensure your bow is unstrung and pointed in a safe direction during sight installation.
                  Use proper torque specifications to avoid damaging the bow riser.
                </p>
              </div>
            </div>
          </div>

          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Step-by-Step Installation</h3>
          
          <div class="space-y-6">
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold">
                1
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Prepare the Bow</h4>
                <p class="text-gray-700 dark:text-gray-300 mb-3">
                  Unstring the bow completely and secure it in a bow vise or have a helper hold it steady. 
                  Clean the riser sight mounting area with alcohol to remove any oils or debris.
                </p>
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    <i class="fas fa-info-circle mr-2"></i>
                    <strong>Pro Tip:</strong> Take photos of your current setup before removing any existing sight for reference.
                  </p>
                </div>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold">
                2
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Check Mounting Holes</h4>
                <p class="text-gray-700 dark:text-gray-300 mb-3">
                  Verify that the sight mounting holes align with the threaded inserts in your bow riser. 
                  Most modern bows use standard 10-32 threads, but some may vary.
                </p>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                  <p class="text-sm text-blue-800 dark:text-blue-200">
                    <i class="fas fa-ruler mr-2"></i>
                    Standard hole spacing is typically 5/8" center-to-center, but always verify with your specific bow model.
                  </p>
                </div>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold">
                3
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Install the Sight Bracket</h4>
                <p class="text-gray-700 dark:text-gray-300 mb-3">
                  Position the sight bracket against the riser and insert the mounting screws. 
                  Hand-tighten initially, then use a torque wrench to achieve the manufacturer's specified torque (typically 15-20 in-lbs).
                </p>
                <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3">
                  <p class="text-sm text-amber-800 dark:text-amber-200">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    <strong>Warning:</strong> Over-tightening can strip threads or crack the riser. Under-tightening can cause sight movement.
                  </p>
                </div>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold">
                4
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Attach Sight Housing</h4>
                <p class="text-gray-700 dark:text-gray-300 mb-3">
                  Mount the sight housing to the bracket, ensuring it's positioned for comfortable viewing when at full draw. 
                  The sight should align naturally with your dominant eye without excessive head movement.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Initial Setup -->
      <section id="initial-setup" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-cog text-green-500 mr-3"></i>
          Initial Setup
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Proper initial setup creates the foundation for accurate shooting and makes fine-tuning much easier.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Sight Alignment</h3>
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">Vertical Alignment</h4>
                  <p class="text-sm text-green-800 dark:text-green-200">
                    Position the sight housing so it's perfectly vertical when viewed from behind the bow. 
                    Use a level or plumb line for accuracy.
                  </p>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Distance from Riser</h4>
                  <p class="text-sm text-blue-800 dark:text-blue-200">
                    Start with the sight housing about 4-6 inches from the riser. 
                    This can be adjusted later based on your shooting form and preferences.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Pin Setup (Multi-Pin)</h3>
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">Pin Spacing</h4>
                  <p class="text-sm text-purple-800 dark:text-purple-200">
                    Start with pins spaced evenly (typically 10-yard increments). 
                    The top pin should be for your closest distance (usually 20 yards).
                  </p>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-2">Pin Colors</h4>
                  <p class="text-sm text-orange-800 dark:text-orange-200">
                    Use bright, contrasting colors for different distances. 
                    Common scheme: Red (20yd), Green (30yd), Yellow (40yd), Blue (50yd).
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Sight Calibration -->
      <section id="calibration" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-target text-red-500 mr-3"></i>
          Sight Calibration
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Calibration is the process of setting your sight pins to hit where you aim at specific distances.
          </p>

          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-6 border border-blue-200 dark:border-blue-800">
            <h4 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              <i class="fas fa-lightbulb mr-2"></i>
              Before You Start
            </h4>
            <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <li>• Ensure your bow is properly tuned (arrow rest, center shot, etc.)</li>
              <li>• Use consistent anchor point and shooting form</li>
              <li>• Shoot with the same arrows you'll use regularly</li>
              <li>• Choose a calm day with minimal wind</li>
              <li>• Have a reliable target and backstop</li>
            </ul>
          </div>

          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Calibration Process</h3>
          
          <div class="space-y-6">
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-semibold">
                1
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Start at 20 Yards</h4>
                <p class="text-gray-700 dark:text-gray-300 mb-3">
                  Begin with your top pin at 20 yards. Shoot a group of 3-5 arrows aiming at the center of your target. 
                  Note where the group hits relative to your aim point.
                </p>
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    <strong>Adjustment Rule:</strong> Move your pin in the direction you want your arrows to go. 
                    If arrows hit low, move the pin down. If arrows hit left, move the pin left.
                  </p>
                </div>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-semibold">
                2
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Fine-Tune 20 Yard Pin</h4>
                <p class="text-gray-700 dark:text-gray-300 mb-3">
                  Make small adjustments and shoot another group. Continue until your arrows consistently hit where you aim. 
                  This pin becomes your reference for all other distances.
                </p>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-semibold">
                3
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Set Additional Distances</h4>
                <p class="text-gray-700 dark:text-gray-300 mb-3">
                  Move to 30 yards and repeat the process with your second pin. 
                  Continue for each pin/distance combination. Work systematically from closest to farthest distance.
                </p>
                <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3">
                  <p class="text-sm text-amber-800 dark:text-amber-200">
                    <i class="fas fa-clock mr-2"></i>
                    <strong>Patience is Key:</strong> Take breaks between distance changes to avoid fatigue affecting your accuracy.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Fine-Tuning Process -->
      <section id="fine-tuning" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-microscope text-indigo-500 mr-3"></i>
          Fine-Tuning Process
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Fine-tuning optimizes your sight for maximum accuracy and consistency across all shooting conditions.
          </p>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Micro-Adjustments</h3>
              
              <div class="space-y-4">
                <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-indigo-900 dark:text-indigo-100 mb-2">
                    <i class="fas fa-arrows-alt-v mr-2"></i>
                    Elevation Adjustments
                  </h4>
                  <p class="text-sm text-indigo-800 dark:text-indigo-200 mb-2">
                    Make small vertical adjustments (1/16" to 1/8" at a time) to fine-tune each pin. 
                    Test after each adjustment.
                  </p>
                  <ul class="text-xs text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Arrows hitting high: Move pin up</li>
                    <li>• Arrows hitting low: Move pin down</li>
                  </ul>
                </div>

                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">
                    <i class="fas fa-arrows-alt-h mr-2"></i>
                    Windage Adjustments
                  </h4>
                  <p class="text-sm text-green-800 dark:text-green-200 mb-2">
                    Horizontal adjustments should affect all pins equally. 
                    If only one pin needs windage correction, check your form first.
                  </p>
                  <ul class="text-xs text-green-700 dark:text-green-300 space-y-1">
                    <li>• Arrows hitting right: Move entire sight right</li>
                    <li>• Arrows hitting left: Move entire sight left</li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Advanced Techniques</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">
                    <i class="fas fa-chart-line mr-2"></i>
                    Gap Shooting
                  </h4>
                  <p class="text-sm text-purple-800 dark:text-purple-200">
                    Learn the gap between your pins for intermediate distances. 
                    For example, if shooting at 25 yards, aim between your 20 and 30-yard pins.
                  </p>
                </div>

                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-2">
                    <i class="fas fa-eye mr-2"></i>
                    Sight Picture Consistency
                  </h4>
                  <p class="text-sm text-orange-800 dark:text-orange-200">
                    Develop a consistent sight picture with proper pin placement in the aperture. 
                    The pin should be centered with equal light gaps around it.
                  </p>
                </div>

                <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-teal-900 dark:text-teal-100 mb-2">
                    <i class="fas fa-stopwatch mr-2"></i>
                    Shot Timing
                  </h4>
                  <p class="text-sm text-teal-800 dark:text-teal-200">
                    Maintain consistent shot timing. Hold at full draw for 3-5 seconds, 
                    allowing time to settle your sight picture before release.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Maintenance & Care -->
      <section id="maintenance" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-tools text-yellow-500 mr-3"></i>
          Maintenance & Care
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Regular maintenance ensures your sight remains accurate and reliable for years to come.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Regular Maintenance</h3>
              
              <div class="space-y-4">
                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Daily Care</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Check for loose screws before shooting</li>
                    <li>• Clean lens/aperture with soft cloth</li>
                    <li>• Protect from moisture and impacts</li>
                    <li>• Store in a protective case</li>
                  </ul>
                </div>

                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Weekly Care</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Detailed cleaning of all components</li>
                    <li>• Check and tighten all hardware</li>
                    <li>• Inspect for wear or damage</li>
                    <li>• Test sight adjustments for smooth operation</li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Troubleshooting Issues</h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
                  <h4 class="font-medium text-red-900 dark:text-red-100 mb-2">Common Problems</h4>
                  <ul class="text-sm text-red-800 dark:text-red-200 space-y-1">
                    <li>• Pins moving during shooting</li>
                    <li>• Inconsistent groups at known distances</li>
                    <li>• Difficulty seeing pins in low light</li>
                    <li>• Sight housing rotation or looseness</li>
                  </ul>
                </div>

                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
                  <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">Quick Solutions</h4>
                  <ul class="text-sm text-green-800 dark:text-green-200 space-y-1">
                    <li>• Apply thread locker to screws</li>
                    <li>• Re-calibrate affected pins</li>
                    <li>• Upgrade to fiber optic or lighted pins</li>
                    <li>• Check and retighten mounting hardware</li>
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
          <i class="fas fa-bug text-red-500 mr-3"></i>
          Troubleshooting Common Issues
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <div class="border-l-4 border-red-500 pl-4">
              <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
                Problem: Groups are inconsistent at different distances
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <p><strong>Possible Causes:</strong></p>
                <ul class="list-disc list-inside ml-4 space-y-1">
                  <li>Inconsistent anchor point or shooting form</li>
                  <li>Bow tuning issues (rest alignment, nocking point)</li>
                  <li>Arrow spine or weight inconsistencies</li>
                  <li>Sight mounting looseness</li>
                </ul>
                <p><strong>Solutions:</strong></p>
                <ul class="list-disc list-inside ml-4 space-y-1">
                  <li>Practice consistent form and anchor point</li>
                  <li>Paper tune your bow setup</li>
                  <li>Use matched arrows from the same batch</li>
                  <li>Check and tighten all sight hardware</li>
                </ul>
              </div>
            </div>

            <div class="border-l-4 border-orange-500 pl-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-2">
                Problem: Pins are difficult to see in low light
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <p><strong>Solutions:</strong></p>
                <ul class="list-disc list-inside ml-4 space-y-1">
                  <li>Upgrade to fiber optic pins for better light gathering</li>
                  <li>Consider lighted pins or sight light attachment</li>
                  <li>Use larger diameter pins for better visibility</li>
                  <li>Ensure proper sight picture with adequate light gap</li>
                </ul>
              </div>
            </div>

            <div class="border-l-4 border-yellow-500 pl-4">
              <h3 class="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
                Problem: Sight settings drift over time
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <p><strong>Solutions:</strong></p>
                <ul class="list-disc list-inside ml-4 space-y-1">
                  <li>Apply thread locker to adjustment screws</li>
                  <li>Check for worn adjustment mechanisms</li>
                  <li>Protect sight from temperature extremes</li>
                  <li>Record sight settings and check regularly</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Advanced Tips -->
      <section id="advanced-tips" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-graduation-cap text-purple-500 mr-3"></i>
          Advanced Tips & Techniques
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Competition Techniques</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">Sight Marks</h4>
                  <p class="text-sm text-purple-800 dark:text-purple-200">
                    Keep detailed records of sight settings for different conditions, distances, and arrow types. 
                    Create a sight tape or reference chart for quick adjustments.
                  </p>
                </div>

                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Environmental Adjustments</h4>
                  <p class="text-sm text-blue-800 dark:text-blue-200">
                    Learn to compensate for wind, temperature, and altitude changes. 
                    Hot weather can affect arrow flight, requiring slight sight adjustments.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Hunting Specific Tips</h3>
              
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">Treestand Adjustments</h4>
                  <p class="text-sm text-green-800 dark:text-green-200">
                    Practice shooting from elevated positions. Steep angles can affect point of impact, 
                    especially at closer ranges where you might aim slightly lower.
                  </p>
                </div>

                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-2">Low Light Performance</h4>
                  <p class="text-sm text-orange-800 dark:text-orange-200">
                    Test your sight setup in dawn and dusk conditions when most hunting occurs. 
                    Consider tritium or battery-powered lighted pins for ultimate low-light performance.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <h4 class="font-semibold text-purple-900 dark:text-purple-100 mb-2">
              <i class="fas fa-star mr-2"></i>
              Master's Secret
            </h4>
            <p class="text-sm text-purple-800 dark:text-purple-200">
              The best sight setup is worthless without consistent shooting form. 
              Spend 80% of your practice time on form and technique, and only 20% on equipment adjustments. 
              A perfectly tuned sight with poor form will never achieve the accuracy of a basic sight with excellent form.
            </p>
          </div>
        </div>
      </section>

      <!-- Conclusion & Next Steps -->
      <section class="mb-12">
        <div class="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
          <h2 class="text-2xl font-bold text-purple-900 dark:text-purple-100 mb-4">
            <i class="fas fa-trophy mr-3"></i>
            Mastering Your Sight Setup
          </h2>
          <p class="text-purple-800 dark:text-purple-200 mb-4">
            A properly set up and tuned sight is your gateway to consistent, accurate shooting. 
            Remember that sight setup is an ongoing process – your needs may change as your shooting improves and your goals evolve.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Key Takeaways</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Proper installation is critical for accuracy</li>
                <li>• Calibration requires patience and consistency</li>
                <li>• Regular maintenance prevents problems</li>
                <li>• Form matters more than equipment</li>
              </ul>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Next Steps</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Practice with your newly set up sight</li>
                <li>• Keep detailed shooting records</li>
                <li>• Learn to make field adjustments</li>
                <li>• Consider upgrading based on experience</li>
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
            to="/guides/draw-length"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-ruler text-blue-600 dark:text-blue-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                Draw Length Measurement
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Learn proper techniques for measuring your draw length accurately.
            </p>
          </NuxtLink>

          <NuxtLink 
            to="/guides/bow-weight"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-weight-hanging text-green-600 dark:text-green-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-green-600 dark:group-hover:text-green-400">
                Bow Weight Selection
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Choose the optimal draw weight for your shooting goals and physical ability.
            </p>
          </NuxtLink>

          <div class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 opacity-60">
            <div class="flex items-center mb-2">
              <i class="fas fa-arrows-alt-h text-gray-400 mr-3"></i>
              <h3 class="font-semibold text-gray-500 dark:text-gray-400">
                Paper Tuning Guide
              </h3>
            </div>
            <p class="text-sm text-gray-400">
              Coming soon - Learn to tune your bow for optimal arrow flight.
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
  title: 'Sight Setup & Tuning Guide - Complete Bow Sight Installation',
  meta: [
    { name: 'description', content: 'Master bow sight installation, calibration, and fine-tuning with our comprehensive guide. Learn professional techniques for precision shooting.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  // No authentication required - public guide
})

// Smooth scrolling for table of contents links
onMounted(() => {
  const links = document.querySelectorAll('a[href^="#"]')
  
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault()
      const targetId = link.getAttribute('href').substring(1)
      const targetElement = document.getElementById(targetId)
      
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        })
      }
    })
  })
})
</script>