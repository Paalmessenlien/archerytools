#!/usr/bin/env node

/**
 * Test Script for Dropdown Pre-population in Equipment Editing
 * 
 * This script tests the dropdown value persistence fix by:
 * 1. Fetching a bow setup with equipment
 * 2. Simulating the equipment editing workflow 
 * 3. Verifying that dropdown specifications are properly pre-populated
 * 4. Testing the form schema loading and initialization timing
 */

const puppeteer = require('puppeteer');

async function testDropdownPersistence() {
    console.log('🧪 Testing Dropdown Pre-population Fix...\n');
    
    let browser;
    try {
        // Launch browser
        browser = await puppeteer.launch({ 
            headless: false, // Set to false so we can see what's happening
            defaultViewport: { width: 1280, height: 720 },
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        
        // Enable console logging from the browser
        page.on('console', msg => console.log('🌐 Browser:', msg.text()));
        page.on('pageerror', err => console.error('❌ Page Error:', err.message));
        
        console.log('1️⃣ Navigating to frontend...');
        await page.goto('http://localhost:3000', { waitUntil: 'networkidle0' });
        
        console.log('2️⃣ Looking for bow setup links...');
        
        // Wait for page to load and look for setups
        await page.waitForTimeout(2000);
        
        // Try to find a setup link (adjust selector as needed)
        const setupLinks = await page.$$('a[href*="/setups/"]');
        
        if (setupLinks.length === 0) {
            console.log('⚠️  No setup links found. You may need to:\n   - Login first\n   - Create a bow setup\n   - Navigate to the correct page');
            return;
        }
        
        console.log(`3️⃣ Found ${setupLinks.length} setup link(s), clicking first one...`);
        await setupLinks[0].click();
        
        // Wait for setup page to load
        await page.waitForTimeout(3000);
        
        console.log('4️⃣ Looking for Equipment tab...');
        
        // Click on Equipment tab
        const equipmentTab = await page.$('button[aria-label="Tabs"] button:has-text("Equipment"), button:contains("Equipment")');
        if (equipmentTab) {
            await equipmentTab.click();
            console.log('✅ Clicked Equipment tab');
        } else {
            // Try alternative selector
            const tabs = await page.$$('button');
            for (const tab of tabs) {
                const text = await page.evaluate(el => el.textContent, tab);
                if (text && text.includes('Equipment')) {
                    await tab.click();
                    console.log('✅ Found and clicked Equipment tab');
                    break;
                }
            }
        }
        
        await page.waitForTimeout(2000);
        
        console.log('5️⃣ Looking for existing equipment to edit...');
        
        // Look for edit buttons
        const editButtons = await page.$$('button[title*="edit"], button:has([class*="fa-edit"]), button:has(.fa-edit)');
        
        if (editButtons.length === 0) {
            console.log('⚠️  No equipment found to edit. You may need to add equipment first.');
            return;
        }
        
        console.log(`6️⃣ Found ${editButtons.length} edit button(s), clicking first one...`);
        await editButtons[0].click();
        
        // Wait for edit modal to load
        await page.waitForTimeout(3000);
        
        console.log('7️⃣ Checking for dropdown elements with pre-selected values...');
        
        // Check for select elements with selected values
        const dropdowns = await page.$$('select');
        console.log(`   Found ${dropdowns.length} dropdown(s)`);
        
        let testResults = {
            totalDropdowns: dropdowns.length,
            prePopulatedDropdowns: 0,
            emptyDropdowns: 0,
            dropdownDetails: []
        };
        
        for (let i = 0; i < dropdowns.length; i++) {
            const dropdown = dropdowns[i];
            
            // Get dropdown details
            const label = await page.evaluate(dropdown => {
                const labelEl = dropdown.closest('div')?.querySelector('label');
                return labelEl ? labelEl.textContent.trim() : 'Unknown';
            }, dropdown);
            
            const selectedValue = await page.evaluate(dropdown => dropdown.value, dropdown);
            const options = await page.evaluate(dropdown => {
                return Array.from(dropdown.options).map(opt => ({
                    value: opt.value,
                    text: opt.text,
                    selected: opt.selected
                }));
            }, dropdown);
            
            const detail = {
                index: i,
                label: label,
                selectedValue: selectedValue,
                hasValue: selectedValue !== '' && selectedValue !== null,
                optionsCount: options.length
            };
            
            testResults.dropdownDetails.push(detail);
            
            if (detail.hasValue) {
                testResults.prePopulatedDropdowns++;
                console.log(`   ✅ Dropdown "${label}": Pre-populated with "${selectedValue}"`);
            } else {
                testResults.emptyDropdowns++;
                console.log(`   ❌ Dropdown "${label}": Empty (no pre-selected value)`);
            }
        }
        
        console.log('\n📊 Test Results Summary:');
        console.log(`   Total Dropdowns: ${testResults.totalDropdowns}`);
        console.log(`   Pre-populated: ${testResults.prePopulatedDropdowns}`);
        console.log(`   Empty: ${testResults.emptyDropdowns}`);
        
        if (testResults.prePopulatedDropdowns > 0) {
            console.log('\n✅ SUCCESS: At least some dropdowns are pre-populated in editing mode!');
        } else if (testResults.totalDropdowns > 0) {
            console.log('\n❌ ISSUE: No dropdowns are pre-populated - the fix may need review');
        } else {
            console.log('\n⚠️  No dropdowns found - may need different test scenario');
        }
        
        // Keep browser open for manual inspection
        console.log('\n🔍 Browser left open for manual inspection. Press Ctrl+C to close.');
        console.log('   You can now manually verify the dropdown behavior.');
        
        // Wait indefinitely until process is killed
        await new Promise(() => {});
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Check if puppeteer is available
async function checkPuppeteer() {
    try {
        require('puppeteer');
        return true;
    } catch (error) {
        console.log('⚠️  Puppeteer not found. Installing puppeteer...');
        const { execSync } = require('child_process');
        try {
            execSync('npm install puppeteer', { stdio: 'inherit' });
            return true;
        } catch (installError) {
            console.error('❌ Failed to install puppeteer:', installError.message);
            return false;
        }
    }
}

// Main execution
(async () => {
    console.log('🏹 Equipment Dropdown Pre-population Test\n');
    
    const puppeteerAvailable = await checkPuppeteer();
    if (!puppeteerAvailable) {
        console.log('❌ Cannot run test without puppeteer. Manual testing required.');
        console.log('\n📖 Manual Testing Steps:');
        console.log('1. Open http://localhost:3000 in browser');
        console.log('2. Navigate to a bow setup with existing equipment');
        console.log('3. Click Equipment tab');
        console.log('4. Click edit button on any equipment item');
        console.log('5. Verify that dropdown fields show pre-selected values');
        console.log('6. Check that specifications are populated correctly');
        return;
    }
    
    await testDropdownPersistence();
})();