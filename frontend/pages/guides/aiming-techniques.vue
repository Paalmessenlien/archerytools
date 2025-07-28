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
          <span class="text-gray-900 dark:text-gray-100">Aiming Techniques</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl mr-4">
          <i class="fas fa-eye text-green-600 dark:text-green-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Aiming Techniques Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Master different aiming methods and develop consistent accuracy for various archery disciplines</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          20 min read
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-layer-group mr-2"></i>
          Beginner to Advanced
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-user mr-2"></i>
          Shooting Technique
        </span>
      </div>
    </div>

    <!-- Table of Contents -->
    <div class="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 mb-8 border border-green-200 dark:border-green-800">
      <h2 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#aiming-fundamentals" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">1. Aiming Fundamentals</a>
        <a href="#sight-aiming" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">2. Sight Aiming</a>
        <a href="#instinctive-aiming" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">3. Instinctive Aiming</a>
        <a href="#gap-shooting" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">4. Gap Shooting</a>
        <a href="#string-walking" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">5. String Walking</a>
        <a href="#practice-drills" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">6. Practice Drills</a>
        <a href="#troubleshooting" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">7. Troubleshooting</a>
        <a href="#advanced-tips" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">8. Advanced Tips</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Aiming Fundamentals -->
      <section id="aiming-fundamentals" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-crosshairs text-blue-500 mr-3"></i>
          Aiming Fundamentals
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Consistent aiming is the foundation of accurate archery. Understanding different aiming methods 
            allows you to choose the technique that best suits your discipline, equipment, and natural shooting style.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-eye mr-2"></i>
                Visual Alignment Principles
              </h3>
              <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                <li>• Consistent anchor point placement</li>
                <li>• Proper sight picture alignment</li>
                <li>• Dominant eye identification</li>
                <li>• Focus point determination</li>
                <li>• Visual reference establishment</li>
              </ul>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-brain mr-2"></i>
                Mental Components
              </h3>
              <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                <li>• Target focus and concentration</li>
                <li>• Aiming routine consistency</li>
                <li>• Breathing control during aim</li>
                <li>• Mental visualization</li>
                <li>• Shot execution timing</li>
              </ul>
            </div>
          </div>

          <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <h4 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">
              <i class="fas fa-lightbulb mr-2"></i>
              Key Success Factor
            </h4>
            <p class="text-amber-800 dark:text-amber-200">
              <strong>Consistency is more important than perfection.</strong> Develop a repeatable aiming process 
              that you can execute the same way on every shot, regardless of conditions or pressure.
            </p>
          </div>
        </div>
      </section>

      <!-- Sight Aiming -->
      <section id="sight-aiming" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-bullseye text-purple-500 mr-3"></i>
          Sight Aiming Method
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            The most precise aiming method for target archery and hunting, using mechanical sights 
            to align with the target. This method provides consistent reference points and is essential 
            for competitive shooting.
          </p>

          <div class="space-y-6">
            <!-- Sight Types and Setup -->
            <div class="border border-purple-200 dark:border-purple-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-4">
                <i class="fas fa-cog mr-2"></i>
                Sight Setup Process
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Pin Sight Alignment</h4>
                  <ol class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>1. Level the bow with bubble level</li>
                    <li>2. Align sight pin with target center</li>
                    <li>3. Maintain consistent sight picture</li>
                    <li>4. Focus on the target, not the pin</li>
                    <li>5. Execute smooth release</li>
                  </ol>
                </div>
                
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Multi-Pin Systems</h4>
                  <ol class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>1. Sight in each pin for specific distances</li>
                    <li>2. Use appropriate pin for target distance</li>
                    <li>3. Estimate distances accurately</li>
                    <li>4. Practice pin selection speed</li>
                    <li>5. Verify zero regularly</li>
                  </ol>
                </div>
              </div>
            </div>

            <!-- Sight Picture -->
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                <i class="fas fa-search mr-2"></i>
                Perfect Sight Picture Elements
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Pin Placement</h4>
                  <p class="text-sm text-purple-700 dark:text-purple-300">
                    Center the pin precisely on your aiming point. Avoid "pining" or moving the pin around the target.
                  </p>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Eye Focus</h4>
                  <p class="text-sm text-purple-700 dark:text-purple-300">
                    Keep your eye focused on the target, not the pin. The pin should appear slightly blurred.
                  </p>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Consistent Hold</h4>
                  <p class="text-sm text-purple-700 dark:text-purple-300">
                    Maintain steady hold with minimal pin movement. Accept natural tremor rather than fighting it.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Instinctive Aiming -->
      <section id="instinctive-aiming" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-magic text-orange-500 mr-3"></i>
          Instinctive Aiming Method
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            The most natural aiming method, relying on hand-eye coordination and subconscious distance judgment. 
            Popular with traditional archers and those seeking a more intuitive shooting experience.
          </p>

          <div class="space-y-6">
            <!-- Learning Process -->
            <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-4">
                <i class="fas fa-graduation-cap mr-2"></i>
                Development Process
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Phase 1: Foundation (Weeks 1-4)</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>• Start at very close range (5-10 yards)</li>
                    <li>• Focus on consistent form and anchor</li>
                    <li>• Shoot blank bale to develop muscle memory</li>
                    <li>• Practice drawing and releasing smoothly</li>
                    <li>• Avoid analyzing shots initially</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Phase 2: Development (Weeks 5-12)</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>• Gradually increase distance</li>
                    <li>• Begin targeting with large targets</li>
                    <li>• Trust your subconscious aim</li>
                    <li>• Maintain focus on target center</li>
                    <li>• Record and analyze progress</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Mental Approach -->
            <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-orange-900 dark:text-orange-100 mb-3">
                <i class="fas fa-brain mr-2"></i>
                Mental Training for Instinctive Shooting
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-2">Visualization Techniques</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                    <li>• Imagine the arrow's flight path</li>
                    <li>• Visualize hitting the target center</li>
                    <li>• Practice mental rehearsal</li>
                    <li>• Trust your first instinct</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-2">Focus Points</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                    <li>• Concentrate on target center</li>
                    <li>• Avoid overthinking the shot</li>
                    <li>• Maintain soft, relaxed focus</li>
                    <li>• Execute with confidence</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Gap Shooting -->
      <section id="gap-shooting" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-arrows-alt-v text-red-500 mr-3"></i>
          Gap Shooting Method
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            A systematic aiming method that uses the arrow point as a reference, calculating the vertical 
            "gap" between point of aim and target center for different distances. Combines precision with versatility.
          </p>

          <div class="space-y-6">
            <!-- Gap Calculation -->
            <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-4">
                <i class="fas fa-calculator mr-2"></i>
                Gap Calculation Process
              </h3>
              
              <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 mb-4">
                <h4 class="font-semibold text-red-900 dark:text-red-100 mb-2">Step-by-Step Gap Development</h4>
                <ol class="text-sm text-red-800 dark:text-red-200 space-y-2">
                  <li><strong>1. Find Point-On Distance:</strong> The distance where arrow point aligns with target center</li>
                  <li><strong>2. Map Shorter Distances:</strong> Measure gap below target for closer ranges</li>
                  <li><strong>3. Map Longer Distances:</strong> Measure gap above target for farther ranges</li>
                  <li><strong>4. Create Reference Chart:</strong> Document all gaps for quick reference</li>
                  <li><strong>5. Practice Application:</strong> Use gaps consistently in shooting</li>
                </ol>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Sample Gap Chart</h4>
                  <div class="bg-white dark:bg-gray-800 rounded border text-sm">
                    <div class="p-2 border-b font-semibold bg-gray-50 dark:bg-gray-700">Distance → Gap</div>
                    <div class="p-2 border-b">10 yards → 6" low</div>
                    <div class="p-2 border-b">15 yards → 3" low</div>
                    <div class="p-2 border-b">20 yards → Point-on</div>
                    <div class="p-2 border-b">25 yards → 2" high</div>
                    <div class="p-2">30 yards → 5" high</div>
                  </div>
                </div>
                
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Gap Application Tips</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Use consistent anchor point</li>
                    <li>• Practice distance estimation</li>
                    <li>• Memorize common distances</li>
                    <li>• Adjust for shooting angles</li>
                    <li>• Account for environmental factors</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- String Walking -->
      <section id="string-walking" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-hand-point-down text-indigo-500 mr-3"></i>
          String Walking Method
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            An advanced technique where you adjust your string hand position (below the nock) to change 
            the arrow's point of impact. Popular in field archery and barebow competitions.
          </p>

          <div class="space-y-6">
            <!-- Technique Explanation -->
            <div class="border border-indigo-200 dark:border-indigo-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-indigo-900 dark:text-indigo-100 mb-4">
                <i class="fas fa-hand-paper mr-2"></i>
                String Walking Technique
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-3">Finger Placement System</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-2">
                    <li>• <strong>High Anchor:</strong> Fingers close to nock (longer distances)</li>
                    <li>• <strong>Medium Walk:</strong> 1/2" below nock (medium distances)</li>
                    <li>• <strong>Low Walk:</strong> 1" below nock (shorter distances)</li>
                    <li>• <strong>Crawl:</strong> 1.5"+ below nock (very short distances)</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-3">Advantages & Applications</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-2">
                    <li>• Precise distance control</li>
                    <li>• Point-on aiming at all distances</li>
                    <li>• Excellent for field archery</li>
                    <li>• Competitive barebow technique</li>
                    <li>• Versatile for various targets</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Safety and Considerations -->
            <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-3">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                Important Considerations
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Technique Requirements</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Consistent finger pressure</li>
                    <li>• Stable bow hand positioning</li>
                    <li>• Precise string hand placement</li>
                    <li>• Regular practice and mapping</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Potential Challenges</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Increased string pinch risk</li>
                    <li>• Requires excellent form</li>
                    <li>• Complex distance mapping</li>
                    <li>• Not legal in all competitions</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Practice Drills -->
      <section id="practice-drills" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-target text-teal-500 mr-3"></i>
          Practice Drills & Exercises
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Systematic practice drills to develop and maintain aiming accuracy across different techniques and distances.
          </p>

          <div class="space-y-6">
            <!-- Basic Drills -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
                <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-3">
                  <i class="fas fa-circle mr-2"></i>
                  Blank Bale Training
                </h3>
                <p class="text-sm text-teal-800 dark:text-teal-200 mb-3">
                  Focus on form and consistency without target pressure
                </p>
                <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                  <li>• Shoot at unmarked target from 5-10 yards</li>
                  <li>• Focus solely on consistent form</li>
                  <li>• Practice aiming routine timing</li>
                  <li>• Build muscle memory patterns</li>
                </ul>
              </div>

              <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
                <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-3">
                  <i class="fas fa-bullseye mr-2"></i>
                  Dot Torture
                </h3>
                <p class="text-sm text-teal-800 dark:text-teal-200 mb-3">
                  Precision aiming at very small targets
                </p>
                <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                  <li>• Use 1" dots at various distances</li>
                  <li>• Aim for center of each dot</li>
                  <li>• Track hit percentage</li>
                  <li>• Gradually reduce dot size</li>
                </ul>
              </div>
            </div>

            <!-- Progressive Exercises -->
            <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-4">
                <i class="fas fa-chart-line mr-2"></i>
                Progressive Distance Training
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Week 1-2: Foundation</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• 10-15 yards maximum</li>
                    <li>• Large targets (8" circles)</li>
                    <li>• Focus on consistency</li>
                    <li>• 30 arrows per session</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Week 3-4: Expansion</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• 15-25 yards range</li>
                    <li>• Medium targets (6" circles)</li>
                    <li>• Multiple distances</li>
                    <li>• 40 arrows per session</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Week 5+: Challenge</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Full range practice</li>
                    <li>• Standard target faces</li>
                    <li>• Unknown distances</li>
                    <li>• Competition simulation</li>
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
          <i class="fas fa-wrench text-yellow-500 mr-3"></i>
          Troubleshooting Common Issues
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Accuracy Issues -->
              <div class="border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <h3 class="font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
                  <i class="fas fa-times-circle mr-2"></i>
                  Accuracy Problems
                </h3>
                <div class="space-y-3">
                  <div>
                    <h4 class="font-medium text-yellow-800 dark:text-yellow-200">Inconsistent Groups</h4>
                    <p class="text-sm text-yellow-700 dark:text-yellow-300">
                      <strong>Causes:</strong> Varying anchor point, inconsistent draw length, form breakdown
                    </p>
                    <p class="text-sm text-yellow-700 dark:text-yellow-300">
                      <strong>Solutions:</strong> Return to blank bale, check form fundamentals, use mirror practice
                    </p>
                  </div>
                  <div>
                    <h4 class="font-medium text-yellow-800 dark:text-yellow-200">Left/Right Misses</h4>
                    <p class="text-sm text-yellow-700 dark:text-yellow-300">
                      <strong>Causes:</strong> Torque in bow hand, plucking string, wind drift
                    </p>
                    <p class="text-sm text-yellow-700 dark:text-yellow-300">
                      <strong>Solutions:</strong> Check grip pressure, practice back tension release, wind compensation
                    </p>
                  </div>
                </div>
              </div>

              <!-- Technique Issues -->
              <div class="border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <h3 class="font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
                  <i class="fas fa-exclamation-triangle mr-2"></i>
                  Technique Challenges
                </h3>
                <div class="space-y-3">
                  <div>
                    <h4 class="font-medium text-yellow-800 dark:text-yellow-200">Target Panic/Freezing</h4>
                    <p class="text-sm text-yellow-700 dark:text-yellow-300">
                      <strong>Symptoms:</strong> Can't hold on target, premature release, inability to aim
                    </p>
                    <p class="text-sm text-yellow-700 dark:text-yellow-300">
                      <strong>Solutions:</strong> Blank bale therapy, holding exercises, shot process reset
                    </p>
                  </div>
                  <div>
                    <h4 class="font-medium text-yellow-800 dark:text-yellow-200">Overthinking Shots</h4>
                    <p class="text-sm text-yellow-700 dark:text-yellow-300">
                      <strong>Symptoms:</strong> Extended hold times, second-guessing, analysis paralysis
                    </p>
                    <p class="text-sm text-yellow-700 dark:text-yellow-300">
                      <strong>Solutions:</strong> Set shot timer, trust first instinct, simplify process
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Advanced Tips -->
      <section id="advanced-tips" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-medal text-purple-500 mr-3"></i>
          Advanced Aiming Strategies
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <!-- Environmental Factors -->
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                <i class="fas fa-wind mr-2"></i>
                Environmental Adaptations
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Wind Compensation</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Read wind flags and vegetation</li>
                    <li>• Aim into the wind direction</li>
                    <li>• Use wind-cut arrows</li>
                    <li>• Practice in windy conditions</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Lighting Conditions</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Adjust sight picture for shadows</li>
                    <li>• Use appropriate pin colors</li>
                    <li>• Practice in various light</li>
                    <li>• Consider scope lenses</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Terrain Angles</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Compensate for uphill/downhill</li>
                    <li>• Use horizontal distance</li>
                    <li>• Practice on slopes</li>
                    <li>• Adjust for gravity effects</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Mental Game -->
            <div class="border border-purple-200 dark:border-purple-800 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                <i class="fas fa-brain mr-2"></i>
                Mental Performance Enhancement
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Pressure Management</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Develop pre-shot routine</li>
                    <li>• Use breathing techniques</li>
                    <li>• Focus on process, not outcome</li>
                    <li>• Practice under pressure</li>
                    <li>• Maintain positive self-talk</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Competitive Strategies</h4>
                  <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>• Simulate competition conditions</li>
                    <li>• Practice shot timing</li>
                    <li>• Develop contingency plans</li>
                    <li>• Use visualization techniques</li>
                    <li>• Build confidence through preparation</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Conclusion -->
      <section class="mb-12">
        <div class="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
          <h2 class="text-2xl font-bold text-green-900 dark:text-green-100 mb-4">
            <i class="fas fa-trophy mr-3"></i>
            Aiming Mastery
          </h2>
          <p class="text-green-800 dark:text-green-200 mb-4">
            Successful aiming combines technical knowledge, consistent practice, and mental discipline. 
            Choose the method that best suits your goals, equipment, and natural abilities. Remember that 
            consistency trumps perfection – develop a reliable process you can execute under any conditions.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-green-200 dark:border-green-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Practice Priorities</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Consistent form and anchor point</li>
                <li>• Regular practice schedule</li>
                <li>• Progressive distance challenges</li>
                <li>• Mental game development</li>
              </ul>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-green-200 dark:border-green-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Long-term Goals</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Master your chosen aiming method</li>
                <li>• Develop all-weather capability</li>
                <li>• Build confidence through competence</li>
                <li>• Enjoy the journey of improvement</li>
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
            to="/guides/grip-stance"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-orange-300 dark:hover:border-orange-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-hand-paper text-orange-600 dark:text-orange-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-orange-600 dark:group-hover:text-orange-400">
                Proper Grip & Stance
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Master the fundamental foundation for accurate aiming.
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
              Configure your bow sight for optimal aiming precision.
            </p>
          </NuxtLink>

          <div class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 opacity-60">
            <div class="flex items-center mb-2">
              <i class="fas fa-hand-point-up text-gray-400 mr-3"></i>
              <h3 class="font-semibold text-gray-500 dark:text-gray-400">
                Release Techniques
              </h3>
            </div>
            <p class="text-sm text-gray-400">
              Coming soon - Master consistent release execution.
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
  title: 'Aiming Techniques Guide - Master Different Archery Aiming Methods',
  meta: [
    { name: 'description', content: 'Comprehensive guide to archery aiming techniques including sight aiming, instinctive shooting, gap shooting, and string walking methods.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})
</script>