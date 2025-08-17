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
          <span class="text-gray-900 dark:text-gray-100">How to Measure Draw Length</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl mr-4">
          <i class="fas fa-ruler text-blue-600 dark:text-blue-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">How to Measure Draw Length</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">A comprehensive guide to accurately measuring your draw length for optimal bow setup</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          15 min read
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-layer-group mr-2"></i>
          Beginner friendly
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-tools mr-2"></i>
          Equipment Setup
        </span>
      </div>
    </div>

    <!-- Table of Contents -->
    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 mb-8 border border-blue-200 dark:border-blue-800">
      <h2 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#why-important" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">1. Why Draw Length Matters</a>
        <a href="#method-1" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">2. Wingspan Method</a>
        <a href="#method-2" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">3. Wall Method</a>
        <a href="#method-3" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">4. Draw Length Arrow Method</a>
        <a href="#professional" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">5. Professional Measurement</a>
        <a href="#adjustments" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">6. Fine-Tuning Your Draw</a>
        <a href="#common-mistakes" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">7. Common Mistakes</a>
        <a href="#conclusion" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">8. Conclusion</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Why Draw Length Matters -->
      <section id="why-important" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-exclamation-triangle text-orange-500 mr-3"></i>
          Why Draw Length Matters
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-4">
            Draw length is one of the most critical measurements in archery. It directly affects:
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex items-start space-x-3">
              <div class="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Accuracy</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Proper draw length ensures consistent anchor point and sight picture</p>
              </div>
            </div>
            <div class="flex items-start space-x-3">
              <div class="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Power</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Optimal draw length maximizes bow energy transfer</p>
              </div>
            </div>
            <div class="flex items-start space-x-3">
              <div class="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Comfort</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Reduces strain and allows for proper shooting form</p>
              </div>
            </div>
            <div class="flex items-start space-x-3">
              <div class="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Safety</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Prevents overdraw and potential equipment damage</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
          <div class="flex">
            <i class="fas fa-info-circle text-amber-600 dark:text-amber-400 mt-1 mr-3"></i>
            <div>
              <h4 class="font-semibold text-amber-800 dark:text-amber-200">Important Note</h4>
              <p class="text-amber-700 dark:text-amber-300 text-sm mt-1">
                A draw length that's off by even 1 inch can significantly impact your shooting performance and comfort.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Method 1: Wingspan Method -->
      <section id="method-1" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">1</span>
          Wingspan Method (Quick Estimate)
        </h2>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center mb-4">
            <i class="fas fa-tachometer-alt text-green-500 mr-2"></i>
            <span class="text-sm font-medium text-green-600 dark:text-green-400">Easiest • 2 minutes • ±0.5" accuracy</span>
          </div>

          <!-- Illustration -->
          <div class="illustration-container mb-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
            <!-- TODO: Add wingspan method illustration -->
            <div class="w-full max-w-lg mx-auto h-48 bg-blue-100 dark:bg-blue-800 rounded-lg flex items-center justify-center">
              <div class="text-center text-blue-600 dark:text-blue-300">
                <i class="fas fa-image text-4xl mb-2"></i>
                <p class="text-sm">Wingspan Method Illustration</p>
              </div>
            </div>
            <p class="text-sm text-blue-700 dark:text-blue-300 text-center mt-3">
              <i class="fas fa-info-circle mr-2"></i>
              Stand with arms extended, measure fingertip to fingertip, divide by 2.5
            </p>
          </div>

          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">What You Need:</h3>
          <ul class="list-disc list-inside text-gray-700 dark:text-gray-300 mb-6 space-y-1">
            <li>Measuring tape or ruler</li>
            <li>A helper (recommended)</li>
            <li>Wall or flat surface</li>
          </ul>

          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Step-by-Step Process:</h3>
          
          <div class="space-y-4">
            <div class="flex items-start space-x-4">
              <div class="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">1</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Stand Against Wall</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Stand with your back against a wall, arms spread wide horizontally at shoulder height.</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">2</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Measure Wingspan</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Have someone measure from the tip of one middle finger to the tip of the other middle finger.</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">3</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Calculate Draw Length</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Divide your wingspan by 2.5 to get your approximate draw length.</p>
              </div>
            </div>
          </div>

          <div class="mt-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">
              <i class="fas fa-calculator mr-2"></i>
              Quick Calculator
            </h4>
            <p class="text-blue-800 dark:text-blue-200 text-sm mb-2">
              <strong>Formula:</strong> Draw Length = Wingspan ÷ 2.5
            </p>
            <div class="text-sm text-blue-700 dark:text-blue-300">
              <strong>Examples:</strong><br>
              • 70" wingspan = 28" draw length<br>
              • 67.5" wingspan = 27" draw length<br>
              • 72.5" wingspan = 29" draw length
            </div>
          </div>
        </div>
      </section>

      <!-- Method 2: Wall Method -->
      <section id="method-2" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
          Wall Method (More Accurate)
        </h2>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center mb-4">
            <i class="fas fa-crosshairs text-orange-500 mr-2"></i>
            <span class="text-sm font-medium text-orange-600 dark:text-orange-400">Moderate • 5 minutes • ±0.25" accuracy</span>
          </div>

          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">What You Need:</h3>
          <ul class="list-disc list-inside text-gray-700 dark:text-gray-300 mb-6 space-y-1">
            <li>Wall with corner or doorway</li>
            <li>Measuring tape</li>
            <li>Pencil or marker</li>
            <li>A helper</li>
          </ul>

          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Step-by-Step Process:</h3>
          
          <div class="space-y-4">
            <div class="flex items-start space-x-4">
              <div class="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">1</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Position Yourself</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Stand with your bow side against a wall, feet shoulder-width apart in your normal shooting stance.</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">2</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Extend Bow Arm</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Extend your bow arm straight toward the wall, making a fist with your bow hand.</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">3</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Mark Wall Position</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Have someone mark on the wall where your knuckles touch (or would touch if slightly away from wall).</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">4</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Draw to Anchor</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Pull your drawing hand back to your normal anchor point (corner of mouth, under chin, etc.).</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">5</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Mark Anchor Position</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Have someone measure and mark where your drawing hand is positioned.</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">6</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Measure Distance</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Measure the distance between the two marks. Add 1.75" for compound bows or 1.5" for recurve bows.</p>
              </div>
            </div>
          </div>

          <div class="mt-6 bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
            <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">
              <i class="fas fa-plus-circle mr-2"></i>
              Final Calculation
            </h4>
            <div class="text-sm text-green-700 dark:text-green-300 space-y-1">
              <p><strong>Compound Bow:</strong> Measured Distance + 1.75" = Draw Length</p>
              <p><strong>Recurve/Traditional:</strong> Measured Distance + 1.5" = Draw Length</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Method 3: Draw Length Arrow -->
      <section id="method-3" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
          Draw Length Arrow Method (Most Accurate)
        </h2>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center mb-4">
            <i class="fas fa-bullseye text-red-500 mr-2"></i>
            <span class="text-sm font-medium text-red-600 dark:text-red-400">Precise • 10 minutes • ±0.125" accuracy</span>
          </div>

          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
            <div class="flex">
              <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 mt-1 mr-3"></i>
              <div>
                <h4 class="font-semibold text-red-800 dark:text-red-200">Safety Warning</h4>
                <p class="text-red-700 dark:text-red-300 text-sm mt-1">
                  This method requires drawing a bow. Ensure proper safety measures and consider having an experienced archer assist you.
                </p>
              </div>
            </div>
          </div>

          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">What You Need:</h3>
          <ul class="list-disc list-inside text-gray-700 dark:text-gray-300 mb-6 space-y-1">
            <li>A bow you can safely draw</li>
            <li>A long wooden arrow or dowel (36" minimum)</li>
            <li>Measuring tape or ruler</li>
            <li>Marker or tape</li>
            <li>Experienced helper (recommended)</li>
          </ul>

          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Step-by-Step Process:</h3>
          
          <div class="space-y-4">
            <div class="flex items-start space-x-4">
              <div class="bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">1</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Mark the Arrow</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Mark the arrow at 29" from the nock end (this gives you reference points for measurement).</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">2</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Nock the Arrow</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Place the arrow on the string and assume your normal shooting stance.</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">3</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Draw to Full Draw</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Draw the bow to your normal, comfortable anchor point. Hold steady.</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">4</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Mark the Measurement</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Have someone carefully mark where the arrow meets the back of the riser (front of the bow).</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4">
              <div class="bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">5</div>
              <div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">Measure Draw Length</h4>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Safely let down the bow and measure from the nock groove to your mark. This is your draw length.</p>
              </div>
            </div>
          </div>

          <div class="mt-6 bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
            <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">
              <i class="fas fa-lightbulb mr-2"></i>
              Pro Tips
            </h4>
            <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
              <li>• Repeat this process 3-5 times to ensure consistency</li>
              <li>• Use your normal anchor point - don't force a different position</li>
              <li>• Make sure the bow is properly fitted to your general size range</li>
              <li>• Consider having a pro shop technician assist with this method</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Professional Measurement -->
      <section id="professional" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">4</span>
          Professional Measurement
        </h2>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            For the most accurate results, especially for competitive archery or expensive equipment purchases, 
            consider getting professionally measured at an archery pro shop.
          </p>

          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">What Professionals Do:</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <div>
                  <h4 class="font-semibold text-gray-900 dark:text-gray-100">Multiple Methods</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Use several measurement techniques for cross-validation</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <div>
                  <h4 class="font-semibold text-gray-900 dark:text-gray-100">Proper Equipment</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Specialized measuring tools and draw length arrows</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <div>
                  <h4 class="font-semibold text-gray-900 dark:text-gray-100">Form Analysis</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Evaluate your shooting form and anchor point</p>
                </div>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <div>
                  <h4 class="font-semibold text-gray-900 dark:text-gray-100">Equipment Fit</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Ensure bow specifications match your measurements</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <div>
                  <h4 class="font-semibold text-gray-900 dark:text-gray-100">Experience</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Trained to spot common measurement errors</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <div>
                  <h4 class="font-semibold text-gray-900 dark:text-gray-100">Recommendations</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Suggest equipment based on your specific needs</p>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
            <h4 class="font-medium text-indigo-900 dark:text-indigo-100 mb-2">
              <i class="fas fa-store mr-2"></i>
              When to See a Professional
            </h4>
            <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
              <li>• Buying your first bow</li>
              <li>• Upgrading to high-end equipment</li>
              <li>• Experiencing consistent accuracy issues</li>
              <li>• Competitive archery participation</li>
              <li>• Physical changes affecting your draw</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Fine-Tuning Your Draw -->
      <section id="adjustments" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">5</span>
          Fine-Tuning Your Draw Length
        </h2>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Once you have your base measurement, you may need to make small adjustments based on shooting experience and comfort.
          </p>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-red-800 dark:text-red-200 mb-3">
                <i class="fas fa-minus-circle mr-2"></i>
                Signs Your Draw is Too Long:
              </h3>
              <ul class="text-sm text-red-700 dark:text-red-300 space-y-2">
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Difficulty reaching comfortable anchor point</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Inconsistent anchor point position</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Shoulder pain or overextension</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Bow arm collapses or trembles</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>String hits arm guard or clothing</span>
                </li>
              </ul>
            </div>

            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-green-800 dark:text-green-200 mb-3">
                <i class="fas fa-plus-circle mr-2"></i>
                Signs Your Draw is Too Short:
              </h3>
              <ul class="text-sm text-green-700 dark:text-green-300 space-y-2">
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Feeling cramped at full draw</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Unable to reach proper anchor point</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Reduced power and accuracy</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Bow arm too bent at full draw</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-dot-circle text-xs mt-2 mr-2 flex-shrink-0"></i>
                  <span>Difficulty maintaining consistent form</span>
                </li>
              </ul>
            </div>
          </div>

          <div class="mt-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">
              <i class="fas fa-adjust mr-2"></i>
              Making Adjustments
            </h4>
            <div class="text-sm text-blue-700 dark:text-blue-300 space-y-2">
              <p><strong>Start Small:</strong> Make 1/4" adjustments and test thoroughly before making further changes.</p>
              <p><strong>Give it Time:</strong> Allow several shooting sessions to adapt to a new draw length.</p>
              <p><strong>Document Changes:</strong> Keep notes on how adjustments affect your shooting.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Common Mistakes -->
      <section id="common-mistakes" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-exclamation-triangle text-red-500 mr-3"></i>
          Common Mistakes to Avoid
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center mb-4">
              <i class="fas fa-times-circle text-red-500 mr-3"></i>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Measurement Errors</h3>
            </div>
            <ul class="space-y-3 text-sm">
              <li class="flex items-start">
                <i class="fas fa-dot-circle text-red-400 mt-1 mr-2 flex-shrink-0"></i>
                <span class="text-gray-700 dark:text-gray-300">Measuring with poor posture or unnatural stance</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-dot-circle text-red-400 mt-1 mr-2 flex-shrink-0"></i>
                <span class="text-gray-700 dark:text-gray-300">Not using consistent anchor points during measurement</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-dot-circle text-red-400 mt-1 mr-2 flex-shrink-0"></i>
                <span class="text-gray-700 dark:text-gray-300">Relying on a single measurement method</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-dot-circle text-red-400 mt-1 mr-2 flex-shrink-0"></i>
                <span class="text-gray-700 dark:text-gray-300">Ignoring personal comfort for "standard" measurements</span>
              </li>
            </ul>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center mb-4">
              <i class="fas fa-times-circle text-red-500 mr-3"></i>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Equipment Setup Errors</h3>
            </div>
            <ul class="space-y-3 text-sm">
              <li class="flex items-start">
                <i class="fas fa-dot-circle text-red-400 mt-1 mr-2 flex-shrink-0"></i>
                <span class="text-gray-700 dark:text-gray-300">Setting draw length without considering shooting style</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-dot-circle text-red-400 mt-1 mr-2 flex-shrink-0"></i>
                <span class="text-gray-700 dark:text-gray-300">Making large adjustments all at once</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-dot-circle text-red-400 mt-1 mr-2 flex-shrink-0"></i>
                <span class="text-gray-700 dark:text-gray-300">Not accounting for different anchor points (mouth vs. chin)</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-dot-circle text-red-400 mt-1 mr-2 flex-shrink-0"></i>
                <span class="text-gray-700 dark:text-gray-300">Assuming draw length never changes over time</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Conclusion -->
      <section id="conclusion" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-flag-checkered text-green-500 mr-3"></i>
          Conclusion
        </h2>

        <div class="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
          <p class="text-gray-800 dark:text-gray-200 mb-4">
            Accurate draw length measurement is fundamental to archery success. While the wingspan method provides a quick estimate, 
            the wall method or draw length arrow method will give you more precise results.
          </p>
          
          <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">Key Takeaways:</h3>
          <ul class="space-y-2 text-gray-700 dark:text-gray-300">
            <li class="flex items-start">
              <i class="fas fa-check text-green-600 dark:text-green-400 mt-1 mr-3 flex-shrink-0"></i>
              <span>Use multiple measurement methods for accuracy</span>
            </li>
            <li class="flex items-start">
              <i class="fas fa-check text-green-600 dark:text-green-400 mt-1 mr-3 flex-shrink-0"></i>
              <span>Consider professional measurement for expensive equipment</span>
            </li>
            <li class="flex items-start">
              <i class="fas fa-check text-green-600 dark:text-green-400 mt-1 mr-3 flex-shrink-0"></i>
              <span>Fine-tune based on comfort and shooting performance</span>
            </li>
            <li class="flex items-start">
              <i class="fas fa-check text-green-600 dark:text-green-400 mt-1 mr-3 flex-shrink-0"></i>
              <span>Re-measure periodically as your form develops</span>
            </li>
          </ul>
          
          <div class="mt-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              <strong>Remember:</strong> The "perfect" draw length is the one that allows you to shoot consistently, 
              comfortably, and accurately. Don't be afraid to make small adjustments as you develop your shooting technique.
            </p>
          </div>
        </div>
      </section>
    </div>

    <!-- Related Guides -->
    <div class="mt-12 bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-book-open mr-2"></i>
        Related Guides
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white dark:bg-gray-700 rounded-lg p-4 opacity-60">
          <h3 class="font-medium text-gray-500 dark:text-gray-400 mb-2">Bow Weight Selection</h3>
          <p class="text-sm text-gray-400">Learn how to choose the right draw weight for your needs - Coming Soon</p>
        </div>
        <div class="bg-white dark:bg-gray-700 rounded-lg p-4 opacity-60">
          <h3 class="font-medium text-gray-500 dark:text-gray-400 mb-2">Arrow Length & Selection</h3>
          <p class="text-sm text-gray-400">Complete guide to choosing the right arrow length - Coming Soon</p>
        </div>
      </div>
    </div>

    <!-- Back to Guides -->
    <div class="mt-8 text-center">
      <NuxtLink 
        to="/guides"
        class="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
      >
        <i class="fas fa-arrow-left mr-2"></i>
        Back to All Guides
      </NuxtLink>
    </div>
  </div>
</template>

<script setup>
// Set page title and meta
useHead({
  title: 'How to Measure Draw Length - Complete Archery Guide',
  meta: [
    { name: 'description', content: 'Learn how to accurately measure your draw length with multiple proven methods. Step-by-step guide with illustrations for compound and recurve bows.' },
    { name: 'keywords', content: 'draw length, archery measurement, bow setup, wingspan method, wall method, draw length arrow' }
  ]
})

// Protect this page with authentication
definePageMeta({
  // No authentication required - public guide
})
</script>

<style scoped>
/* Smooth scrolling for anchor links */
html {
  scroll-behavior: smooth;
}

/* Custom styling for the guide content */
.prose h2 {
  scroll-margin-top: 2rem;
}

.prose h3 {
  scroll-margin-top: 2rem;
}
</style>