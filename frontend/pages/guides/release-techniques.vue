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
          <span class="text-gray-900 dark:text-gray-100">Release Techniques</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl mr-4">
          <i class="fas fa-hand-point-up text-blue-600 dark:text-blue-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Release Techniques Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Master consistent and clean release methods for improved accuracy and arrow flight</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          22 min read
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
    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 mb-8 border border-blue-200 dark:border-blue-800">
      <h2 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#release-fundamentals" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">1. Release Fundamentals</a>
        <a href="#finger-release" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">2. Finger Release Methods</a>
        <a href="#mechanical-release" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">3. Mechanical Release Aids</a>
        <a href="#back-tension" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">4. Back Tension Technique</a>
        <a href="#release-timing" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">5. Release Timing</a>
        <a href="#common-problems" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">6. Common Problems</a>
        <a href="#practice-exercises" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">7. Practice Exercises</a>
        <a href="#advanced-concepts" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors">8. Advanced Concepts</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Release Fundamentals -->
      <section id="release-fundamentals" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-hand-paper text-red-500 mr-3"></i>
          Release Fundamentals
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            The release is the critical moment where stored bow energy transfers to the arrow. A clean, 
            consistent release is essential for accuracy, as even small variations can significantly 
            affect arrow flight and impact point.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-red-900 dark:text-red-100 mb-3">
                <i class="fas fa-bullseye mr-2"></i>
                Perfect Release Characteristics
              </h3>
              <ul class="text-sm text-red-800 dark:text-red-200 space-y-2">
                <li>• Straight back movement of string hand</li>
                <li>• No lateral string deflection</li>
                <li>• Consistent finger pressure release</li>
                <li>• Minimal bow torque during release</li>
                <li>• Natural follow-through motion</li>
                <li>• Repeatable timing and execution</li>
              </ul>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-times-circle mr-2"></i>
                Release Faults to Avoid
              </h3>
              <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                <li>• Plucking the string laterally</li>
                <li>• Creeping forward during release</li>
                <li>• Collapsing bow arm on release</li>
                <li>• Flinching or jerking motion</li>
                <li>• Inconsistent finger pressure</li>
                <li>• Rushed or hesitant execution</li>
              </ul>
            </div>
          </div>

          <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <h4 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">
              <i class="fas fa-lightbulb mr-2"></i>
              Release Philosophy
            </h4>
            <p class="text-amber-800 dark:text-amber-200">
              Think of the release as <strong>"letting the string go"</strong> rather than actively releasing it. 
              The goal is to create a controlled relaxation of finger tension that allows the string to 
              escape cleanly without disrupting the bow's alignment.
            </p>
          </div>
        </div>
      </section>

      <!-- Finger Release Methods -->
      <section id="finger-release" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-hand-rock text-orange-500 mr-3"></i>
          Finger Release Methods
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Traditional finger release methods are the foundation of archery. Mastering proper finger 
            technique is essential for all archers, even those who primarily use mechanical aids.
          </p>

          <div class="space-y-6">
            <!-- Three Finger Under -->
            <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-4">
                <i class="fas fa-hand-paper mr-2"></i>
                Three Fingers Under (Mediterranean)
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Finger Placement</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>• <strong>Index finger:</strong> Above the nock</li>
                    <li>• <strong>Middle & ring fingers:</strong> Below the nock</li>
                    <li>• <strong>Contact point:</strong> First joint groove</li>
                    <li>• <strong>Pressure distribution:</strong> 40% index, 30% middle, 30% ring</li>
                    <li>• <strong>String angle:</strong> Perpendicular to arrow</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Release Technique</h4>
                  <ol class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>1. Reach full draw with proper finger placement</li>
                    <li>2. Settle into anchor point with even pressure</li>
                    <li>3. Begin back tension buildup gradually</li>
                    <li>4. Relax fingers simultaneously</li>
                    <li>5. Allow natural follow-through motion</li>
                  </ol>
                </div>
              </div>

              <div class="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 rounded border border-orange-200 dark:border-orange-800">
                <p class="text-sm text-orange-800 dark:text-orange-200">
                  <strong>Best for:</strong> Olympic recurve, traditional archery, field archery. 
                  Provides excellent arrow clearance and consistent nocking point pressure.
                </p>
              </div>
            </div>

            <!-- Three Fingers Under -->
            <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-4">
                <i class="fas fa-grip-horizontal mr-2"></i>
                Three Fingers Under (Split)
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Technique Overview</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>• All three fingers below the nock</li>
                    <li>• More consistent pressure distribution</li>
                    <li>• Easier to maintain string alignment</li>
                    <li>• Better for gap shooting and instinctive</li>
                    <li>• Reduces arrow nock pinch</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-3">Advantages</h4>
                  <ul class="text-sm text-orange-700 dark:text-orange-300 space-y-2">
                    <li>• Improved arrow spine consistency</li>
                    <li>• Reduced vertical stringing</li>
                    <li>• Better for heavy draw weights</li>
                    <li>• More forgiving finger pressure</li>
                    <li>• Natural for hunting scenarios</li>
                  </ul>
                </div>
              </div>

              <div class="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 rounded border border-orange-200 dark:border-orange-800">
                <p class="text-sm text-orange-800 dark:text-orange-200">
                  <strong>Best for:</strong> Traditional archery, barebow shooting, hunting, heavy draw weights. 
                  Popular with archers seeking simplicity and consistency.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Mechanical Release Aids -->
      <section id="mechanical-release" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-cog text-purple-500 mr-3"></i>
          Mechanical Release Aids
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Mechanical release aids provide more consistent string release than fingers, eliminating 
            human finger pressure variations. Popular in compound archery and some recurve disciplines.
          </p>

          <div class="space-y-6">
            <!-- Release Types -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Wrist Strap Release -->
              <div class="border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                  <i class="fas fa-hand-point-right mr-2"></i>
                  Wrist Strap Release
                </h3>
                <div class="space-y-3">
                  <div>
                    <h4 class="font-medium text-purple-800 dark:text-purple-200">Characteristics</h4>
                    <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                      <li>• Trigger activated with index finger</li>
                      <li>• Wrist strap provides stability</li>
                      <li>• Quick and intuitive operation</li>
                      <li>• Adjustable trigger sensitivity</li>
                    </ul>
                  </div>
                  <div>
                    <h4 class="font-medium text-purple-800 dark:text-purple-200">Best Applications</h4>
                    <p class="text-sm text-purple-700 dark:text-purple-300">
                      Ideal for beginners, hunting, and situations requiring quick shots. 
                      Most popular choice for compound bow shooters.
                    </p>
                  </div>
                </div>
              </div>

              <!-- Handheld Release -->
              <div class="border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                  <i class="fas fa-hand-paper mr-2"></i>
                  Handheld Release
                </h3>
                <div class="space-y-3">
                  <div>
                    <h4 class="font-medium text-purple-800 dark:text-purple-200">Characteristics</h4>
                    <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                      <li>• No wrist attachment</li>
                      <li>• Thumb or finger trigger activation</li>
                      <li>• More precise hand positioning</li>
                      <li>• Better back tension capability</li>
                    </ul>
                  </div>
                  <div>
                    <h4 class="font-medium text-purple-800 dark:text-purple-200">Best Applications</h4>
                    <p class="text-sm text-purple-700 dark:text-purple-300">
                      Preferred for target archery, competition shooting, and when 
                      maximum precision is required.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Release Aid Technique -->
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-4">
                <i class="fas fa-crosshairs mr-2"></i>
                Proper Release Aid Technique
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Setup and Attachment</h4>
                  <ol class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>1. Attach release to D-loop or string</li>
                    <li>2. Adjust trigger sensitivity appropriately</li>
                    <li>3. Ensure proper hand position and grip</li>
                    <li>4. Verify consistent attachment point</li>
                    <li>5. Practice smooth draw and anchor</li>
                  </ol>
                </div>
                
                <div>
                  <h4 class="font-medium text-purple-800 dark:text-purple-200 mb-2">Execution Process</h4>
                  <ol class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    <li>1. Draw to anchor with release attached</li>
                    <li>2. Settle into consistent anchor point</li>
                    <li>3. Aim and begin back tension buildup</li>
                    <li>4. Apply gradual trigger pressure</li>
                    <li>5. Maintain follow-through after release</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Back Tension Technique -->
      <section id="back-tension" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-expand-arrows-alt text-green-500 mr-3"></i>
          Back Tension Release Technique
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Back tension is the gold standard for consistent releases. By using the large back muscles 
            to continue the draw process through release, this technique eliminates the timing variables 
            of trigger activation or conscious finger release.
          </p>

          <div class="space-y-6">
            <!-- Understanding Back Tension -->
            <div class="border border-green-200 dark:border-green-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
                <i class="fas fa-muscle-man mr-2"></i>
                Understanding Back Tension
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">Muscle Engagement</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-2">
                    <li>• <strong>Rhomboids:</strong> Pull shoulder blades together</li>
                    <li>• <strong>Middle trapezius:</strong> Stabilize shoulder blade</li>
                    <li>• <strong>Posterior deltoid:</strong> Move drawing elbow back</li>
                    <li>• <strong>Latissimus dorsi:</strong> Pull arm down and back</li>
                    <li>• <strong>Rotator cuff:</strong> Stabilize shoulder joint</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">Movement Pattern</h4>
                  <ol class="text-sm text-green-700 dark:text-green-300 space-y-2">
                    <li>1. Establish solid anchor position</li>
                    <li>2. Begin gradual back muscle engagement</li>
                    <li>3. Draw elbow continues moving back slightly</li>
                    <li>4. String hand relaxes as tension builds</li>
                    <li>5. Release occurs naturally from tension</li>
                  </ol>
                </div>
              </div>
            </div>

            <!-- Training Back Tension -->
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-4">
                <i class="fas fa-dumbbell mr-2"></i>
                Developing Back Tension
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Phase 1: Awareness</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>• Practice without arrows</li>
                    <li>• Focus on muscle engagement</li>
                    <li>• Use mirror for form check</li>
                    <li>• Slow, controlled movements</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Phase 2: Integration</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>• Blank bale practice</li>
                    <li>• Consistent anchor timing</li>
                    <li>• Gradual tension increase</li>
                    <li>• Natural release timing</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Phase 3: Application</h4>
                  <ul class="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>• Target practice sessions</li>
                    <li>• Maintain technique focus</li>
                    <li>• Build consistency</li>
                    <li>• Trust the process</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Release Timing -->
      <section id="release-timing" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-stopwatch text-yellow-500 mr-3"></i>
          Release Timing & Rhythm
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Consistent release timing creates rhythm and repeatability in your shot sequence. 
            Poor timing leads to accuracy problems and can develop into target panic or other psychological barriers.
          </p>

          <div class="space-y-6">
            <!-- Shot Sequence Timing -->
            <div class="border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-4">
                <i class="fas fa-clock mr-2"></i>
                Optimal Shot Sequence Timing
              </h3>
              
              <div class="space-y-4">
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded p-3">
                  <div class="flex items-center justify-between text-sm font-medium text-yellow-900 dark:text-yellow-100 mb-2">
                    <span>Pre-Draw Setup</span>
                    <span>2-3 seconds</span>
                  </div>
                  <p class="text-xs text-yellow-800 dark:text-yellow-200">
                    Stance, nocking, initial bow position
                  </p>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded p-3">
                  <div class="flex items-center justify-between text-sm font-medium text-yellow-900 dark:text-yellow-100 mb-2">
                    <span>Draw & Anchor</span>
                    <span>1-2 seconds</span>
                  </div>
                  <p class="text-xs text-yellow-800 dark:text-yellow-200">
                    Smooth draw to consistent anchor point
                  </p>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded p-3">
                  <div class="flex items-center justify-between text-sm font-medium text-yellow-900 dark:text-yellow-100 mb-2">
                    <span>Aim & Hold</span>
                    <span>2-4 seconds</span>
                  </div>
                  <p class="text-xs text-yellow-800 dark:text-yellow-200">
                    Sight alignment, target acquisition
                  </p>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded p-3">
                  <div class="flex items-center justify-between text-sm font-medium text-yellow-900 dark:text-yellow-100 mb-2">
                    <span>Release Execution</span>
                    <span>0.5-1 second</span>
                  </div>
                  <p class="text-xs text-yellow-800 dark:text-yellow-200">
                    Back tension buildup to natural release
                  </p>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded p-3">
                  <div class="flex items-center justify-between text-sm font-medium text-yellow-900 dark:text-yellow-100 mb-2">
                    <span>Follow-Through</span>
                    <span>1-2 seconds</span>
                  </div>
                  <p class="text-xs text-yellow-800 dark:text-yellow-200">
                    Maintain position until arrow hits target
                  </p>
                </div>
              </div>
            </div>

            <!-- Rhythm Development -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                <h3 class="font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
                  <i class="fas fa-metronome mr-2"></i>
                  Building Consistent Rhythm
                </h3>
                <ul class="text-sm text-yellow-800 dark:text-yellow-200 space-y-2">
                  <li>• Use mental counting or breathing cues</li>
                  <li>• Practice with metronome initially</li>
                  <li>• Develop natural internal rhythm</li>
                  <li>• Avoid rushing under pressure</li>
                  <li>• Maintain timing regardless of conditions</li>
                  <li>• Film yourself to analyze consistency</li>
                </ul>
              </div>
              
              <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                <h3 class="font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
                  <i class="fas fa-exclamation-triangle mr-2"></i>
                  Timing Problems to Avoid
                </h3>
                <ul class="text-sm text-yellow-800 dark:text-yellow-200 space-y-2">
                  <li>• Holding too long (muscle fatigue)</li>
                  <li>• Rushing the release (panic shots)</li>
                  <li>• Inconsistent hold times</li>
                  <li>• Freezing at full draw</li>
                  <li>• Premature releases from anticipation</li>
                  <li>• Varying rhythm between shots</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Common Problems -->
      <section id="common-problems" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-exclamation-circle text-red-500 mr-3"></i>
          Common Release Problems
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Technical Problems -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  <i class="fas fa-tools mr-2"></i>
                  Technical Issues
                </h3>
                
                <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">String Plucking</h4>
                  <div class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <p><strong>Symptoms:</strong> String moves laterally, arrows hit left/right</p>
                    <p><strong>Causes:</strong> Active finger movement, poor hand position</p>
                    <p><strong>Solutions:</strong> Focus on straight-back release, use back tension</p>
                  </div>
                </div>
                
                <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Creeping</h4>
                  <div class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <p><strong>Symptoms:</strong> Draw length shortens during aim</p>
                    <p><strong>Causes:</strong> Insufficient back tension, target panic</p>
                    <p><strong>Solutions:</strong> Strengthen draw, practice holding exercises</p>
                  </div>
                </div>
                
                <div class="border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Collapse</h4>
                  <div class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <p><strong>Symptoms:</strong> Bow arm drops during release</p>
                    <p><strong>Causes:</strong> Weak bow arm, anticipation</p>
                    <p><strong>Solutions:</strong> Strengthen bow arm, follow-through practice</p>
                  </div>
                </div>
              </div>

              <!-- Psychological Problems -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  <i class="fas fa-brain mr-2"></i>
                  Mental/Psychological Issues
                </h3>
                
                <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-2">Target Panic</h4>
                  <div class="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                    <p><strong>Symptoms:</strong> Can't hold on target, immediate release</p>
                    <p><strong>Treatment:</strong> Blank bale therapy, shot process rebuild</p>
                    <p><strong>Prevention:</strong> Consistent rhythm, avoid result focus</p>
                  </div>
                </div>
                
                <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-2">Freezing</h4>
                  <div class="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                    <p><strong>Symptoms:</strong> Unable to release, extended hold times</p>
                    <p><strong>Treatment:</strong> Shot clock, pressure reduction</p>
                    <p><strong>Prevention:</strong> Trust training, process focus</p>
                  </div>
                </div>
                
                <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                  <h4 class="font-medium text-orange-800 dark:text-orange-200 mb-2">Flinching</h4>
                  <div class="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                    <p><strong>Symptoms:</strong> Jerky release, bow movement</p>
                    <p><strong>Treatment:</strong> Surprise release training, relaxation</p>
                    <p><strong>Prevention:</strong> Gradual pressure building, confidence</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Practice Exercises -->
      <section id="practice-exercises" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-dumbbell text-teal-500 mr-3"></i>
          Practice Exercises & Drills
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Systematic practice drills to develop and maintain proper release technique across different scenarios and skill levels.
          </p>

          <div class="space-y-6">
            <!-- Basic Drills -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
                <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-3">
                  <i class="fas fa-circle-notch mr-2"></i>
                  Blank Bale Release
                </h3>
                <p class="text-sm text-teal-800 dark:text-teal-200 mb-3">
                  Focus purely on release mechanics without target pressure
                </p>
                <ol class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                  <li>1. Set up 3-5 yards from blank target</li>
                  <li>2. Focus on consistent anchor and release</li>
                  <li>3. Practice 10-20 shots per session</li>
                  <li>4. Analyze string hand follow-through</li>
                  <li>5. Build muscle memory patterns</li>
                </ol>
              </div>

              <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
                <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-3">
                  <i class="fas fa-hand-paper mr-2"></i>
                  Holding Exercises
                </h3>
                <p class="text-sm text-teal-800 dark:text-teal-200 mb-3">
                  Build strength and consistency for extended holds
                </p>
                <ol class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                  <li>1. Draw to anchor without arrow</li>
                  <li>2. Hold for 10-15 seconds</li>
                  <li>3. Focus on back muscle engagement</li>
                  <li>4. Practice controlled let-down</li>
                  <li>5. Gradually increase hold time</li>
                </ol>
              </div>
            </div>

            <!-- Advanced Exercises -->
            <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-4">
                <i class="fas fa-target mr-2"></i>
                Progressive Release Training
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Week 1-2: Foundation</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Blank bale only (no targets)</li>
                    <li>• Focus on form consistency</li>
                    <li>• 30 shots per session</li>
                    <li>• Mirror practice for form</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Week 3-4: Integration</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Large targets at short range</li>
                    <li>• Maintain release focus</li>
                    <li>• 40 shots per session</li>
                    <li>• Film for analysis</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Week 5+: Application</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Normal targets and distances</li>
                    <li>• Competition simulation</li>
                    <li>• Full practice sessions</li>
                    <li>• Performance tracking</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Diagnostic Drills -->
            <div class="border border-teal-200 dark:border-teal-800 rounded-lg p-4">
              <h3 class="font-semibold text-teal-900 dark:text-teal-100 mb-3">
                <i class="fas fa-search mr-2"></i>
                Release Diagnostic Exercises
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">String Tracking Test</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Mark string with powder or chalk</li>
                    <li>• Check string path after release</li>
                    <li>• Straight back = good release</li>
                    <li>• Side marks = plucking problem</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-teal-800 dark:text-teal-200 mb-2">Follow-Through Check</h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-300 space-y-1">
                    <li>• Have partner observe string hand</li>
                    <li>• String hand should move straight back</li>
                    <li>• Should end near or behind ear</li>
                    <li>• No lateral movement patterns</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Advanced Concepts -->
      <section id="advanced-concepts" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-graduation-cap text-indigo-500 mr-3"></i>
          Advanced Release Concepts
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <!-- Biomechanics -->
            <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-3">
                <i class="fas fa-cogs mr-2"></i>
                Release Biomechanics
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Force Vectors</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• String force should be straight back</li>
                    <li>• Minimize lateral force components</li>
                    <li>• Bow hand reaction affects accuracy</li>
                    <li>• Follow-through maintains alignment</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Timing Coordination</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Both hands work together</li>
                    <li>• Bow hand stays stable during release</li>
                    <li>• Core muscles maintain posture</li>
                    <li>• Eye focus remains on target</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Competition Strategies -->
            <div class="border border-indigo-200 dark:border-indigo-800 rounded-lg p-4">
              <h3 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-3">
                <i class="fas fa-trophy mr-2"></i>
                Competition Release Strategies
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Pressure Management</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Trust your training</li>
                    <li>• Maintain normal rhythm</li>
                    <li>• Focus on process</li>
                    <li>• Use pre-shot routine</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Adaptation Strategies</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Adjust for conditions</li>
                    <li>• Modify timing if needed</li>
                    <li>• Have backup techniques</li>
                    <li>• Stay flexible</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Mental Preparation</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Visualize successful releases</li>
                    <li>• Practice under pressure</li>
                    <li>• Build confidence</li>
                    <li>• Stay in present moment</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Equipment Considerations -->
            <div class="border border-indigo-200 dark:border-indigo-800 rounded-lg p-4">
              <h3 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-3">
                <i class="fas fa-bow-arrow mr-2"></i>
                Equipment Impact on Release
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">String & Nocking Point</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• String material affects feel</li>
                    <li>• Nocking point height impacts release</li>
                    <li>• String silencers may help</li>
                    <li>• Serving material matters</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-200 mb-2">Bow Tuning Effects</h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-300 space-y-1">
                    <li>• Proper spine selection crucial</li>
                    <li>• Rest timing affects clearance</li>
                    <li>• Brace height influences feel</li>
                    <li>• Bow balance impacts stability</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Conclusion -->
      <section class="mb-12">
        <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
          <h2 class="text-2xl font-bold text-blue-900 dark:text-blue-100 mb-4">
            <i class="fas fa-trophy mr-3"></i>
            Release Mastery
          </h2>
          <p class="text-blue-800 dark:text-blue-200 mb-4">
            The release is where everything comes together – your stance, grip, draw, anchor, and aim all 
            culminate in this critical moment. A perfect release is smooth, consistent, and surprise-free. 
            Master this technique through patient practice and trust in your training.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Key Principles</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Consistency over perfection</li>
                <li>• Back tension is king</li>
                <li>• Trust your subconscious</li>
                <li>• Practice makes permanent</li>
              </ul>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Continuous Improvement</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Regular form analysis</li>
                <li>• Video review sessions</li>
                <li>• Blank bale maintenance</li>
                <li>• Mental game development</li>
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
            to="/guides/aiming-techniques"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-eye text-green-600 dark:text-green-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-green-600 dark:group-hover:text-green-400">
                Aiming Techniques
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Master different aiming methods for consistent accuracy.
            </p>
          </NuxtLink>

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
              Build the foundation for consistent release execution.
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
              Coming soon - Fine-tune your equipment for perfect arrow flight.
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
  title: 'Release Techniques Guide - Master Consistent Archery Release Methods',
  meta: [
    { name: 'description', content: 'Complete guide to archery release techniques including finger release, mechanical aids, back tension, and release timing for improved accuracy.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})
</script>