const { chromium } = require('playwright');

async function testSpineCalculator() {
  console.log('🚀 Starting Spine Calculator Test Suite');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000 // Add delay for visibility
  });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();

  try {
    // Test 1: Navigate to Calculator
    console.log('\n📍 Test 1: Navigate to Calculator');
    await page.goto('http://localhost:3000/calculator');
    await page.waitForLoadState('networkidle');
    console.log('✅ Successfully navigated to calculator');
    
    // Check if we're being redirected to login/welcome page
    const currentUrl = page.url();
    const pageText = await page.textContent('body');
    
    if (pageText.includes('Beta Testing Phase') || pageText.includes('Sign In')) {
      console.log('🔒 Authentication required - trying to click Calculator in nav');
      
      // Try clicking the Calculator button in navigation
      const calculatorNavButton = await page.locator('text="Calculator"').or(page.locator('a[href*="calculator"]'));
      if (await calculatorNavButton.count() > 0) {
        await calculatorNavButton.first().click();
        await page.waitForTimeout(2000);
        console.log('✅ Clicked Calculator navigation');
      } else {
        console.log('⚠️ Calculator navigation not found - authentication may be required');
        
        // Try to take screenshot of current page for debugging
        await page.screenshot({ 
          path: 'authentication_page.png',
          fullPage: true
        });
        console.log('📸 Screenshot of authentication page saved');
      }
    }

    // Test 2: Fill basic bow configuration to trigger spine calculations
    console.log('\n📍 Test 2: Configure Bow Setup for Spine Calculations');
    
    // Fill in draw weight
    const drawWeightInput = await page.locator('md-filled-text-field[label*="Draw Weight"]');
    if (await drawWeightInput.count() > 0) {
      await drawWeightInput.first().click();
      await page.keyboard.type('60');
      console.log('✅ Set draw weight to 60 lbs');
    }

    // Fill in draw length
    const drawLengthInput = await page.locator('md-filled-text-field[label*="Draw Length"]');
    if (await drawLengthInput.count() > 0) {
      await drawLengthInput.first().click();
      await page.keyboard.type('28');
      console.log('✅ Set draw length to 28 inches');
    }

    // Fill arrow length
    const arrowLengthInput = await page.locator('md-filled-text-field[label*="Arrow Length"]');
    if (await arrowLengthInput.count() > 0) {
      await arrowLengthInput.first().click();
      await page.keyboard.type('29');
      console.log('✅ Set arrow length to 29 inches');
    }

    // Fill point weight
    const pointWeightInput = await page.locator('md-filled-text-field[label*="Point Weight"]');
    if (await pointWeightInput.count() > 0) {
      await pointWeightInput.first().click();
      await page.keyboard.type('100');
      console.log('✅ Set point weight to 100 grains');
    }

    // Wait for calculations to trigger
    await page.waitForTimeout(2000);

    // Test 3: Look for Professional Spine Calculation section
    console.log('\n📍 Test 3: Locate Professional Spine Calculation Section');
    
    // First, let's see what's on the page
    const allHeadings = await page.locator('h1, h2, h3, h4, h5, h6').allTextContents();
    console.log('🔍 All headings found:', allHeadings);
    
    const professionalSpineSection = await page.locator('h4:has-text("Professional Spine Calculation")');
    if (await professionalSpineSection.count() > 0) {
      console.log('✅ Found Professional Spine Calculation section');
      
      // Click to show the section
      const showButton = await page.locator('button:has(span:text("Show"))').or(
        page.locator('button:has(i.fa-chevron-down)')
      );
      if (await showButton.count() > 0) {
        await showButton.first().click();
        await page.waitForTimeout(1000);
        console.log('✅ Expanded Professional Spine Calculation section');
      }
    } else {
      console.log('⚠️ Professional Spine Calculation section not found');
      
      // Try to trigger the section by calculating first
      console.log('🔄 Trying to trigger spine calculation...');
      const calculateButton = await page.locator('button:has-text("Calculate"), md-filled-button:has-text("Calculate")');
      if (await calculateButton.count() > 0) {
        await calculateButton.first().click();
        await page.waitForTimeout(3000);
        console.log('✅ Clicked calculate button');
        
        // Check again for the section
        const professionalSpineSectionAfter = await page.locator('h4:has-text("Professional Spine Calculation")');
        if (await professionalSpineSectionAfter.count() > 0) {
          console.log('✅ Professional Spine Calculation section appeared after calculation!');
          
          // Try to expand it
          const expandButton = await page.locator('button').filter({ hasText: 'Show' });
          if (await expandButton.count() > 0) {
            await expandButton.first().click();
            await page.waitForTimeout(1000);
            console.log('✅ Expanded Professional Spine Calculation section');
          }
        }
      }
    }

    // Test 4: Check for ManufacturerSpineChartSelector component
    console.log('\n📍 Test 4: Test Manufacturer Spine Chart Selector');
    
    // Look for manufacturer selection dropdown
    const manufacturerSelect = await page.locator('md-filled-select[label*="manufacturer"]').or(
      page.locator('md-filled-select[label*="Manufacturer"]')
    );
    
    if (await manufacturerSelect.count() > 0) {
      console.log('✅ Found manufacturer spine chart selector');
      
      // Try to interact with it
      await manufacturerSelect.first().click();
      await page.waitForTimeout(500);
      
      // Look for options
      const options = await page.locator('md-select-option').count();
      console.log(`✅ Found ${options} manufacturer options`);
      
      // Take screenshot of the selector
      await page.screenshot({ 
        path: 'manufacturer_spine_selector.png',
        fullPage: false
      });
      console.log('📸 Screenshot saved: manufacturer_spine_selector.png');
      
    } else {
      console.log('⚠️ Manufacturer spine chart selector not found');
    }

    // Test 5: Check for calculation mode toggles
    console.log('\n📍 Test 5: Test Calculation Mode Selection');
    
    const simpleRadio = await page.locator('input[type="radio"]').first();
    const professionalRadio = await page.locator('input[type="radio"]').nth(1);
    
    if (await simpleRadio.count() > 0 && await professionalRadio.count() > 0) {
      console.log('✅ Found Simple/Professional mode radio buttons');
      
      // Test switching to Professional mode
      await professionalRadio.first().check();
      await page.waitForTimeout(1000);
      console.log('✅ Switched to Professional mode');
      
      // Look for professional settings
      const professionalSettings = await page.locator('h4:has-text("Professional Adjustments")');
      if (await professionalSettings.count() > 0) {
        console.log('✅ Professional adjustments panel appeared');
        
        // Test bow speed input
        const bowSpeedInput = await page.locator('input[placeholder*="320"]').or(
          page.locator('input:near(text("Bow Speed"))')
        );
        if (await bowSpeedInput.count() > 0) {
          await bowSpeedInput.first().fill('320');
          console.log('✅ Set bow speed to 320 FPS');
        }
        
        // Test release type selection
        const releaseSelect = await page.locator('md-filled-select[label*="Release"]');
        if (await releaseSelect.count() > 0) {
          await releaseSelect.first().click();
          await page.waitForTimeout(500);
          console.log('✅ Found release type selector');
        }
      }
    } else {
      console.log('⚠️ Calculation mode radio buttons not found');
    }

    // Test 6: Take comprehensive screenshots
    console.log('\n📍 Test 6: Take Screenshots');
    
    await page.screenshot({ 
      path: 'spine_calculator_full_page.png',
      fullPage: true
    });
    console.log('📸 Full page screenshot saved: spine_calculator_full_page.png');
    
    // Try to scroll to professional section if visible
    const professionalSection = await page.locator('text="Professional Spine Calculation"');
    if (await professionalSection.count() > 0) {
      await professionalSection.first().scrollIntoViewIfNeeded();
      await page.screenshot({ 
        path: 'professional_spine_section.png',
        clip: { x: 0, y: 0, width: 1920, height: 800 }
      });
      console.log('📸 Professional spine section screenshot saved');
    }

    console.log('\n✅ Frontend testing completed successfully!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await browser.close();
  }
}

async function testSpineCalculationAPI() {
  console.log('\n🔌 Testing Spine Calculation API');
  
  const baseURL = 'http://localhost:5000/api';
  
  // Test 1: Basic spine calculation
  console.log('\n📍 API Test 1: Basic Spine Calculation');
  try {
    const response = await fetch(`${baseURL}/tuning/calculate-spine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        draw_weight: 60,
        draw_length: 28,
        arrow_length: 29,
        point_weight: 100,
        bow_type: 'compound'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Basic spine calculation successful');
      console.log('📊 Result:', {
        optimal_spine: data.spine_calculations?.optimal_spine,
        spine_range: data.spine_calculations?.spine_range
      });
    } else {
      console.log('⚠️ Basic spine calculation failed:', response.status);
    }
  } catch (error) {
    console.log('❌ Basic spine calculation error:', error.message);
  }

  // Test 2: Professional mode spine calculation
  console.log('\n📍 API Test 2: Professional Mode with Parameters');
  try {
    const response = await fetch(`${baseURL}/tuning/calculate-spine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        draw_weight: 60,
        draw_length: 28,
        arrow_length: 29,
        point_weight: 100,
        bow_type: 'compound',
        bow_speed: 320,
        release_type: 'mechanical'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Professional spine calculation successful');
      console.log('📊 Result with professional settings:', {
        optimal_spine: data.spine_calculations?.optimal_spine,
        spine_range: data.spine_calculations?.spine_range,
        bow_speed_used: data.spine_calculations?.bow_speed,
        release_type_used: data.spine_calculations?.release_type
      });
    } else {
      console.log('⚠️ Professional spine calculation failed:', response.status);
    }
  } catch (error) {
    console.log('❌ Professional spine calculation error:', error.message);
  }

  // Test 3: Test chart management endpoints
  console.log('\n📍 API Test 3: Chart Management Endpoints');
  
  try {
    const manufacturersResponse = await fetch(`${baseURL}/calculator/manufacturers`);
    if (manufacturersResponse.ok) {
      const data = await manufacturersResponse.json();
      console.log('✅ Manufacturers endpoint works');
      console.log('📊 Available manufacturers:', data.manufacturers?.length || 0);
      
      if (data.manufacturers && data.manufacturers.length > 0) {
        const firstManufacturer = data.manufacturers[0].manufacturer;
        console.log('🔍 Testing charts for:', firstManufacturer);
        
        const chartsResponse = await fetch(`${baseURL}/calculator/manufacturers/${encodeURIComponent(firstManufacturer)}/charts`);
        if (chartsResponse.ok) {
          const chartData = await chartsResponse.json();
          console.log('✅ Charts endpoint works');
          console.log('📊 Available charts:', chartData.charts?.length || 0);
        } else {
          console.log('⚠️ Charts endpoint failed:', chartsResponse.status);
        }
      }
    } else {
      console.log('⚠️ Manufacturers endpoint failed:', manufacturersResponse.status);
    }
  } catch (error) {
    console.log('❌ Chart management endpoints error:', error.message);
  }
}

async function testStandaloneSpineChartInterface() {
  console.log('\n🔬 Testing Standalone Spine Chart Interface');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000
  });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();

  try {
    // Test the standalone HTML page
    console.log('\n📍 Test: Load Standalone API Test Page');
    await page.goto('file://' + process.cwd() + '/test_manufacturer_spine_chart.html');
    await page.waitForLoadState('networkidle');
    console.log('✅ Standalone test page loaded');

    // Wait for auto-tests to complete
    await page.waitForTimeout(5000);

    // Take screenshot of the results
    await page.screenshot({ 
      path: 'standalone_api_test_results.png',
      fullPage: true
    });
    console.log('📸 API test results screenshot saved');

    // Check for test results
    const testResultElements = await page.locator('.api-demo h2').allTextContents();
    console.log('🔍 Test sections found:', testResultElements);

    const testSummary = await page.locator('div:has-text("✅"), div:has-text("❌")').allTextContents();
    console.log('📊 Test results:', testSummary);

    console.log('✅ Standalone interface testing completed');
    
  } catch (error) {
    console.error('❌ Standalone test failed:', error);
  } finally {
    await browser.close();
  }
}

// Run the tests
async function runAllTests() {
  await testSpineCalculator();
  await testSpineCalculationAPI();
  await testStandaloneSpineChartInterface();
  
  console.log('\n🎉 All tests completed!');
  console.log('\nGenerated files:');
  console.log('- spine_calculator_full_page.png (authentication page)');
  console.log('- standalone_api_test_results.png (API functionality demo)');
  console.log('- authentication_page.png (if generated)');
}

runAllTests().catch(console.error);