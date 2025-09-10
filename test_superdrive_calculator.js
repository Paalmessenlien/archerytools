/**
 * Playwright MCP Test: Superdrive 23 Arrow Calculator Testing
 * Purpose: Test that Superdrive 23 arrow (ID 2508) appears for 50lbs compound bow
 * Date: 2025-01-20
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;

class SuperdriveCalculatorTest {
    constructor() {
        this.browser = null;
        this.page = null;
        this.testResults = {
            timestamp: new Date().toISOString(),
            testName: 'Superdrive 23 Arrow Calculator Test',
            environment: {
                frontendUrl: 'http://localhost:3000',
                backendUrl: 'http://localhost:5000',
                targetArrow: {
                    id: 2508,
                    name: 'Superdrive 23',
                    manufacturer: 'Easton Archery'
                }
            },
            tests: [],
            screenshots: []
        };
    }

    async init() {
        console.log('🚀 Initializing Superdrive Calculator Test...');
        
        // Launch browser with proper configuration
        this.browser = await chromium.launch({
            headless: false, // Show browser for debugging
            slowMo: 500,     // Slow down for visibility
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const context = await this.browser.newContext({
            viewport: { width: 1280, height: 720 },
            userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        });
        
        this.page = await context.newPage();
        
        // Enable console and error logging
        this.page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log('❌ Browser Error:', msg.text());
            }
        });
        
        this.page.on('pageerror', error => {
            console.log('❌ Page Error:', error.message);
        });
    }

    async testEnvironment() {
        console.log('🔍 Testing Environment...');
        
        const testResult = {
            name: 'Environment Check',
            status: 'pending',
            details: {},
            errors: []
        };
        
        try {
            // Test frontend availability
            console.log('   - Testing frontend at http://localhost:3000');
            const response = await this.page.goto('http://localhost:3000', { 
                waitUntil: 'networkidle',
                timeout: 30000 
            });
            
            if (response && response.ok()) {
                testResult.details.frontend = 'Available';
                console.log('   ✅ Frontend accessible');
            } else {
                throw new Error(`Frontend not accessible: ${response ? response.status() : 'No response'}`);
            }
            
            // Check page title
            const title = await this.page.title();
            testResult.details.title = title;
            console.log(`   ✅ Page title: "${title}"`);
            
            // Test API availability
            console.log('   - Testing API at http://localhost:5000/api/health');
            try {
                const apiResponse = await this.page.evaluate(async () => {
                    const response = await fetch('http://localhost:5000/api/health');
                    return {
                        status: response.status,
                        ok: response.ok,
                        data: response.ok ? await response.json() : null
                    };
                });
                
                if (apiResponse.ok) {
                    testResult.details.api = 'Available';
                    console.log('   ✅ API accessible');
                } else {
                    console.log('   ⚠️ API may not be available, continuing with test');
                    testResult.details.api = `Status: ${apiResponse.status}`;
                }
            } catch (apiError) {
                console.log('   ⚠️ API test failed, but continuing:', apiError.message);
                testResult.details.api = 'Not accessible';
            }
            
            testResult.status = 'passed';
            
        } catch (error) {
            console.log('❌ Environment test failed:', error.message);
            testResult.status = 'failed';
            testResult.errors.push(error.message);
        }
        
        this.testResults.tests.push(testResult);
        return testResult.status === 'passed';
    }

    async waitForManualLogin() {
        console.log('🔐 Waiting for manual login with messenlien@gmail.com...');
        console.log('   👤 Please login manually in the browser window that opened');
        console.log('   ⏳ Test will continue automatically once login is detected...');
        
        const testResult = {
            name: 'Manual Authentication',
            status: 'pending',
            details: {
                email: 'messenlien@gmail.com'
            },
            errors: []
        };
        
        try {
            // Go to home page first
            await this.page.goto('http://localhost:3000');
            await this.page.waitForLoadState('networkidle');
            
            // Wait for user to login manually - check every 2 seconds for up to 2 minutes
            const maxWaitTime = 120000; // 2 minutes
            const checkInterval = 2000; // 2 seconds
            let waitTime = 0;
            let loginDetected = false;
            
            console.log('   🔍 Monitoring for login indicators...');
            
            while (waitTime < maxWaitTime && !loginDetected) {
                // Check if we're logged in by looking for user indicators
                const userIndicators = [
                    'text=messenlien@gmail.com',
                    'text=Paal',
                    'text=Paal Messenlien',
                    '[data-testid="user-profile"]',
                    '.user-profile',
                    'button:has-text("Logout")',
                    'a:has-text("My Setup")',
                    '[data-testid="user-menu"]'
                ];
                
                for (const selector of userIndicators) {
                    if (await this.page.locator(selector).first().isVisible({ timeout: 1000 }).catch(() => false)) {
                        console.log(`   ✅ Login detected! Found: ${selector}`);
                        loginDetected = true;
                        testResult.details.loginIndicator = selector;
                        break;
                    }
                }
                
                if (!loginDetected) {
                    await this.page.waitForTimeout(checkInterval);
                    waitTime += checkInterval;
                    
                    // Show progress every 10 seconds
                    if (waitTime % 10000 === 0) {
                        console.log(`   ⏳ Still waiting... ${Math.round(waitTime/1000)}s elapsed`);
                    }
                }
            }
            
            if (loginDetected) {
                console.log('   🎉 Login successful! Continuing with test...');
                testResult.status = 'passed';
            } else {
                console.log('   ⚠️ Login timeout reached, continuing anyway...');
                testResult.status = 'timeout';
            }
            
        } catch (error) {
            console.log('❌ Login waiting failed:', error.message);
            testResult.status = 'failed';
            testResult.errors.push(error.message);
        }
        
        this.testResults.tests.push(testResult);
        return testResult.status === 'passed' || testResult.status === 'timeout';
    }

    async navigateToCalculator() {
        console.log('🧭 Navigating to Calculator...');
        
        const testResult = {
            name: 'Navigate to Calculator',
            status: 'pending',
            details: {},
            errors: []
        };
        
        try {
            // Try direct calculator URL first
            const calculatorUrl = 'http://localhost:3000/calculator';
            console.log(`   - Attempting direct navigation to ${calculatorUrl}`);
            
            await this.page.goto(calculatorUrl, { 
                waitUntil: 'networkidle',
                timeout: 30000 
            });
            
            // Check if we got redirected or if calculator is accessible
            const currentUrl = this.page.url();
            testResult.details.finalUrl = currentUrl;
            
            if (currentUrl.includes('/calculator')) {
                console.log('   ✅ Calculator accessed directly');
                testResult.details.method = 'direct';
            } else {
                console.log('   ⚠️ Redirected from calculator, trying to access via My Setup');
                
                // Try navigating to My Setup first (authenticated route)
                await this.page.goto('http://localhost:3000/my-setup');
                await this.page.waitForLoadState('networkidle');
                
                // Look for calculator link or try calculator via setup
                const calculatorLinks = [
                    'text=Calculator',
                    'a[href*="calculator"]',
                    'button:has-text("Calculator")',
                    'button:has-text("Tune")',
                    'button:has-text("Find Arrows")'
                ];
                
                let calculatorFound = false;
                for (const selector of calculatorLinks) {
                    const element = this.page.locator(selector).first();
                    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
                        console.log(`   ✅ Found calculator access: ${selector}`);
                        await element.click();
                        await this.page.waitForLoadState('networkidle');
                        calculatorFound = true;
                        testResult.details.method = 'via_setup';
                        break;
                    }
                }
                
                if (!calculatorFound) {
                    // Try direct calculator URL again after authentication
                    await this.page.goto(calculatorUrl);
                    await this.page.waitForLoadState('networkidle');
                    testResult.details.method = 'retry_direct';
                }
            }
            
            // Take screenshot
            const screenshotPath = `/tmp/calculator_navigation_${Date.now()}.png`;
            await this.page.screenshot({ path: screenshotPath, fullPage: true });
            this.testResults.screenshots.push({
                name: 'Calculator Navigation',
                path: screenshotPath,
                description: 'Screenshot after attempting to navigate to calculator'
            });
            
            testResult.status = 'passed';
            
        } catch (error) {
            console.log('❌ Calculator navigation failed:', error.message);
            testResult.status = 'failed';
            testResult.errors.push(error.message);
        }
        
        this.testResults.tests.push(testResult);
        return testResult.status === 'passed';
    }

    async setupCompoundBow() {
        console.log('🏹 Setting up 50lbs Compound Bow...');
        
        const testResult = {
            name: 'Setup 50lbs Compound Bow',
            status: 'pending',
            details: {
                drawWeight: '50 lbs',
                bowType: 'Compound',
                drawLength: '28 inches'
            },
            errors: []
        };
        
        try {
            // Look for bow setup controls or forms
            console.log('   - Looking for bow setup controls...');
            
            // Common selectors for bow setup
            const setupSelectors = [
                'button:has-text("Setup")',
                'button:has-text("Add Setup")',
                'button:has-text("New Setup")',
                'a:has-text("My Setup")',
                '[data-testid="bow-setup"]',
                '.bow-setup-button',
                '#bow-setup'
            ];
            
            let setupButton = null;
            for (const selector of setupSelectors) {
                setupButton = this.page.locator(selector).first();
                if (await setupButton.isVisible({ timeout: 2000 }).catch(() => false)) {
                    console.log(`   ✅ Found setup button: ${selector}`);
                    break;
                }
                setupButton = null;
            }
            
            if (setupButton) {
                console.log('   - Clicking setup button...');
                await setupButton.click();
                await this.page.waitForTimeout(2000);
            } else {
                console.log('   ⚠️ No setup button found, looking for existing bow setups...');
            }
            
            // Look for bow configuration options or use API directly
            console.log('   - Looking for bow configuration form...');
            
            // Check if there's a form for bow setup
            const formSelectors = [
                'form',
                '[data-testid="bow-form"]',
                '.bow-setup-form',
                'input[type="range"]', // Draw weight slider
                'select', // Bow type dropdown
                'input[placeholder*="weight"]',
                'input[placeholder*="draw"]'
            ];
            
            let foundForm = false;
            for (const selector of formSelectors) {
                if (await this.page.locator(selector).first().isVisible({ timeout: 2000 }).catch(() => false)) {
                    console.log(`   ✅ Found form element: ${selector}`);
                    foundForm = true;
                    break;
                }
            }
            
            if (foundForm) {
                // Try to fill out compound bow form
                await this.fillBowSetupForm();
            } else {
                // Use API approach to create bow setup
                await this.createBowSetupViaAPI();
            }
            
            testResult.status = 'passed';
            
        } catch (error) {
            console.log('❌ Bow setup failed:', error.message);
            testResult.status = 'failed';
            testResult.errors.push(error.message);
        }
        
        this.testResults.tests.push(testResult);
        return testResult.status === 'passed';
    }

    async fillBowSetupForm() {
        console.log('   - Filling bow setup form...');
        
        // Try to set draw weight
        const drawWeightInputs = [
            'input[type="range"]',
            'input[name*="weight"]',
            'input[placeholder*="weight"]',
            '[data-testid="draw-weight"]'
        ];
        
        for (const selector of drawWeightInputs) {
            const input = this.page.locator(selector).first();
            if (await input.isVisible({ timeout: 1000 }).catch(() => false)) {
                console.log(`   - Setting draw weight via ${selector}`);
                await input.fill('50');
                break;
            }
        }
        
        // Try to set bow type to Compound
        const bowTypeSelectors = [
            'select[name*="type"]',
            'select[name*="bow"]',
            '[data-testid="bow-type"]',
            'input[name*="type"]'
        ];
        
        for (const selector of bowTypeSelectors) {
            const select = this.page.locator(selector).first();
            if (await select.isVisible({ timeout: 1000 }).catch(() => false)) {
                console.log(`   - Setting bow type via ${selector}`);
                await select.selectOption({ label: 'Compound' }).catch(() => {
                    return select.fill('Compound');
                });
                break;
            }
        }
        
        // Try to set draw length
        const drawLengthInputs = [
            'input[name*="length"]',
            'input[placeholder*="length"]',
            '[data-testid="draw-length"]'
        ];
        
        for (const selector of drawLengthInputs) {
            const input = this.page.locator(selector).first();
            if (await input.isVisible({ timeout: 1000 }).catch(() => false)) {
                console.log(`   - Setting draw length via ${selector}`);
                await input.fill('28');
                break;
            }
        }
        
        // Look for submit button
        const submitButtons = [
            'button[type="submit"]',
            'button:has-text("Save")',
            'button:has-text("Create")',
            'button:has-text("Add")',
            'button:has-text("Submit")'
        ];
        
        for (const selector of submitButtons) {
            const button = this.page.locator(selector).first();
            if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
                console.log(`   - Clicking submit button: ${selector}`);
                await button.click();
                await this.page.waitForTimeout(2000);
                break;
            }
        }
    }

    async createBowSetupViaAPI() {
        console.log('   - Creating bow setup via API...');
        
        // Use API to create bow setup
        const apiResult = await this.page.evaluate(async () => {
            try {
                const response = await fetch('http://localhost:5000/api/bow-setups', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        setup_name: 'Test 50lbs Compound for Superdrive Test',
                        bow_type: 'Compound',
                        draw_weight: 50,
                        draw_length: 28,
                        bow_brand: 'Test',
                        bow_model: 'Test Model',
                        ibo_speed: 320,
                        usage: ['Target', 'Hunting'],
                        description: 'Automated test bow setup for Superdrive 23 arrow testing'
                    })
                });
                
                const data = await response.json();
                return {
                    success: response.ok,
                    status: response.status,
                    data: data
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        });
        
        if (apiResult.success) {
            console.log('   ✅ Bow setup created via API:', apiResult.data);
        } else {
            console.log('   ⚠️ API bow setup failed:', apiResult.error || apiResult.status);
        }
    }

    async testCompatibleArrows() {
        console.log('🎯 Testing Compatible Arrows for Superdrive 23...');
        
        const testResult = {
            name: 'Test Compatible Arrows API',
            status: 'pending',
            details: {
                targetArrow: this.testResults.environment.targetArrow,
                searchResults: {}
            },
            errors: []
        };
        
        try {
            console.log('   - Fetching compatible arrows via API...');
            
            // Test compatible arrows API directly
            const apiResult = await this.page.evaluate(async () => {
                try {
                    const response = await fetch('http://localhost:5000/api/arrows/compatible', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            draw_weight: 50,
                            bow_type: 'compound',
                            draw_length: 28,
                            arrow_material: 'carbon',
                            shooting_style: 'target'
                        })
                    });
                    
                    const data = await response.json();
                    return {
                        success: response.ok,
                        status: response.status,
                        data: data
                    };
                } catch (error) {
                    return {
                        success: false,
                        error: error.message
                    };
                }
            });
            
            if (apiResult.success && apiResult.data) {
                console.log(`   ✅ API returned ${apiResult.data.total_compatible || 0} compatible arrows`);
                
                const compatibleArrows = apiResult.data.compatible_arrows || [];
                testResult.details.searchResults = {
                    totalArrows: compatibleArrows.length,
                    totalCompatible: apiResult.data.total_compatible || 0
                };
                
                // Look for Superdrive 23 (Arrow ID 2508)
                const superdriveArrows = compatibleArrows.filter(arrow => 
                    arrow.id === 2508 || 
                    (arrow.model_name && arrow.model_name.toLowerCase().includes('superdrive')) ||
                    (arrow.model_name && arrow.model_name.includes('23'))
                );
                
                console.log(`   🔍 Found ${superdriveArrows.length} Superdrive arrows`);
                
                if (superdriveArrows.length > 0) {
                    console.log('   ✅ Superdrive arrows found:');
                    superdriveArrows.forEach((arrow, index) => {
                        console.log(`     ${index + 1}. ID: ${arrow.id}, Model: ${arrow.model_name}, Manufacturer: ${arrow.manufacturer}`);
                    });
                    
                    const targetArrow = superdriveArrows.find(arrow => arrow.id === 2508);
                    if (targetArrow) {
                        console.log('   🎯 TARGET ARROW FOUND: Superdrive 23 (ID 2508)!');
                        testResult.details.targetArrowFound = true;
                        testResult.details.targetArrowDetails = targetArrow;
                    } else {
                        console.log('   ⚠️ Superdrive arrows found but not ID 2508 specifically');
                        testResult.details.targetArrowFound = false;
                    }
                } else {
                    console.log('   ❌ No Superdrive arrows found in compatible results');
                    testResult.details.targetArrowFound = false;
                }
                
                // Check for duplicates
                const arrowIds = compatibleArrows.map(arrow => arrow.id);
                const uniqueIds = [...new Set(arrowIds)];
                const hasDuplicates = arrowIds.length !== uniqueIds.length;
                
                testResult.details.hasDuplicates = hasDuplicates;
                if (hasDuplicates) {
                    console.log(`   ⚠️ Found duplicates: ${arrowIds.length} total vs ${uniqueIds.length} unique`);
                } else {
                    console.log('   ✅ No duplicate arrows found');
                }
                
                // Check arrow type variety
                const arrowTypes = compatibleArrows.map(arrow => arrow.arrow_type).filter(Boolean);
                const uniqueTypes = [...new Set(arrowTypes)];
                testResult.details.arrowTypes = uniqueTypes;
                console.log(`   📊 Arrow types found: ${uniqueTypes.join(', ')}`);
                
            } else {
                throw new Error(`API request failed: ${apiResult.error || apiResult.status}`);
            }
            
            testResult.status = 'passed';
            
        } catch (error) {
            console.log('❌ Compatible arrows test failed:', error.message);
            testResult.status = 'failed';
            testResult.errors.push(error.message);
        }
        
        this.testResults.tests.push(testResult);
        return testResult.status === 'passed';
    }

    async testCalculatorUI() {
        console.log('🖥️ Testing Calculator UI...');
        
        const testResult = {
            name: 'Calculator UI Test',
            status: 'pending',
            details: {},
            errors: []
        };
        
        try {
            // Take screenshot of current page
            const screenshotPath = `/tmp/calculator_ui_${Date.now()}.png`;
            await this.page.screenshot({ path: screenshotPath, fullPage: true });
            this.testResults.screenshots.push({
                name: 'Calculator UI',
                path: screenshotPath,
                description: 'Screenshot of calculator interface during testing'
            });
            
            // Look for arrow results in the UI
            const arrowSelectors = [
                '[data-testid="arrow-results"]',
                '.arrow-results',
                '.compatible-arrows',
                'ul li', // Generic list items
                '.arrow-card',
                '.arrow-item'
            ];
            
            let arrowElements = null;
            for (const selector of arrowSelectors) {
                const elements = this.page.locator(selector);
                if (await elements.count() > 0) {
                    console.log(`   ✅ Found arrow elements: ${selector} (${await elements.count()} items)`);
                    arrowElements = elements;
                    break;
                }
            }
            
            if (arrowElements) {
                const arrowCount = await arrowElements.count();
                testResult.details.arrowElementsFound = arrowCount;
                
                // Look for Superdrive text in the UI
                const superdriveElements = this.page.locator('text=Superdrive').or(
                    this.page.locator('text=2508')
                );
                
                if (await superdriveElements.count() > 0) {
                    console.log(`   🎯 Found Superdrive references in UI (${await superdriveElements.count()})`);
                    testResult.details.superdriveInUI = true;
                } else {
                    console.log('   ⚠️ No Superdrive references found in UI');
                    testResult.details.superdriveInUI = false;
                }
            } else {
                console.log('   ⚠️ No arrow result elements found in UI');
                testResult.details.arrowElementsFound = 0;
            }
            
            testResult.status = 'passed';
            
        } catch (error) {
            console.log('❌ Calculator UI test failed:', error.message);
            testResult.status = 'failed';
            testResult.errors.push(error.message);
        }
        
        this.testResults.tests.push(testResult);
        return testResult.status === 'passed';
    }

    async generateReport() {
        console.log('📊 Generating Test Report...');
        
        const reportPath = `/home/paal/archerytoolsonline/main/superdrive_test_report_${Date.now()}.json`;
        
        // Calculate summary
        const totalTests = this.testResults.tests.length;
        const passedTests = this.testResults.tests.filter(t => t.status === 'passed').length;
        const failedTests = this.testResults.tests.filter(t => t.status === 'failed').length;
        
        this.testResults.summary = {
            totalTests,
            passedTests,
            failedTests,
            successRate: totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0
        };
        
        // Check if main objective was achieved
        const compatibleArrowsTest = this.testResults.tests.find(t => t.name === 'Test Compatible Arrows API');
        this.testResults.objectiveAchieved = compatibleArrowsTest && 
            compatibleArrowsTest.details && 
            compatibleArrowsTest.details.targetArrowFound === true;
        
        await fs.writeFile(reportPath, JSON.stringify(this.testResults, null, 2), 'utf8');
        
        console.log('\n📋 TEST REPORT SUMMARY:');
        console.log('=======================');
        console.log(`📊 Tests: ${passedTests}/${totalTests} passed (${this.testResults.summary.successRate}%)`);
        console.log(`🎯 Main Objective: ${this.testResults.objectiveAchieved ? '✅ ACHIEVED' : '❌ NOT ACHIEVED'}`);
        
        if (this.testResults.objectiveAchieved) {
            console.log('🏆 SUCCESS: Superdrive 23 arrow (ID 2508) found for 50lbs compound bow!');
        } else {
            console.log('⚠️ ISSUE: Superdrive 23 arrow (ID 2508) not found in compatible results');
        }
        
        console.log(`📄 Full report saved to: ${reportPath}`);
        console.log(`📷 Screenshots: ${this.testResults.screenshots.length} captured`);
        
        return reportPath;
    }

    async cleanup() {
        console.log('🧹 Cleaning up...');
        
        if (this.browser) {
            await this.browser.close();
        }
    }

    async run() {
        console.log('🎬 Starting Superdrive Calculator Test...\n');
        
        try {
            await this.init();
            
            // Update todo status
            console.log('📋 Starting test execution...');
            
            const envOk = await this.testEnvironment();
            if (!envOk) {
                console.log('⚠️ Environment issues detected, continuing with available services...');
            }
            
            // Wait for manual login with messenlien@gmail.com
            const loginOk = await this.waitForManualLogin();
            if (!loginOk) {
                console.log('⚠️ Login issues detected, continuing with test...');
            }
            
            await this.navigateToCalculator();
            await this.setupCompoundBow();
            await this.testCompatibleArrows();
            await this.testCalculatorUI();
            
            const reportPath = await this.generateReport();
            
            console.log('\n🎉 Test execution completed!');
            return reportPath;
            
        } catch (error) {
            console.log('\n❌ Test execution failed:', error.message);
            console.error(error);
        } finally {
            await this.cleanup();
        }
    }
}

// Execute the test
async function main() {
    const test = new SuperdriveCalculatorTest();
    await test.run();
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = SuperdriveCalculatorTest;