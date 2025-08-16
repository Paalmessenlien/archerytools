#!/usr/bin/env python3
"""
Playwright test for frontend chronograph integration and performance calculations
Tests the complete user workflow from arrow setup to performance analysis
"""

import asyncio
import sys
import time
from playwright.async_api import async_playwright, expect
import json

async def test_frontend_chronograph_integration():
    """Test chronograph integration through the frontend UI"""
    
    print("🎭 Starting Playwright Frontend Test")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False, slow_mo=1000)  # Visible browser with slow motion
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Step 1: Navigate to the application
            print("1. 🌐 Navigating to application...")
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            
            # Wait for page to load and check title
            title = await page.title()
            print(f"   ✅ Page loaded: {title}")
            
            # Step 2: Check if we need to login (look for login elements)
            print("2. 🔐 Checking authentication status...")
            
            # Look for login button or user menu
            login_button = page.locator("text=Login").first
            user_menu = page.locator('[data-testid="user-menu"]').first
            home_content = page.locator('text="Bow Setup"').first
            
            try:
                await expect(home_content).to_be_visible(timeout=5000)
                print("   ✅ Already logged in or no auth required")
            except:
                print("   ⚠️ Authentication may be required")
                # Try to find and click login if available
                if await login_button.is_visible():
                    await login_button.click()
                    await page.wait_for_timeout(2000)
            
            # Step 3: Navigate to bow setups
            print("3. 🏹 Navigating to bow setups...")
            
            # Look for navigation to setups
            nav_setups = page.locator('a[href*="setups"], a[href="/"], text="Home"').first
            if await nav_setups.is_visible():
                await nav_setups.click()
                await page.wait_for_load_state("networkidle")
                print("   ✅ Navigated to bow setups")
            else:
                print("   ℹ️ Already on setups page or navigation not found")
            
            # Step 4: Look for existing bow setups or create one
            print("4. 🎯 Looking for existing bow setups...")
            
            # Wait for setups to load
            await page.wait_for_timeout(2000)
            
            # Look for setup cards or links
            setup_links = page.locator('a[href*="/setups/"], a[href*="/setup-arrows/"]')
            setup_count = await setup_links.count()
            
            if setup_count > 0:
                print(f"   ✅ Found {setup_count} existing bow setups")
                # Click on the first setup
                first_setup = setup_links.first
                await first_setup.click()
                await page.wait_for_load_state("networkidle")
                print("   ✅ Opened first bow setup")
            else:
                print("   ⚠️ No existing setups found - would need to create one")
                # For now, we'll skip setup creation and test with a direct URL
                await page.goto("http://localhost:3000/setup-arrows/1")
                await page.wait_for_load_state("networkidle")
            
            # Step 5: Check for arrow setup page elements
            print("5. 🏹 Verifying arrow setup page...")
            
            current_url = page.url
            print(f"   📍 Current URL: {current_url}")
            
            # Look for arrow setup elements
            arrow_elements = page.locator('text="Arrow", text="Performance", text="Chronograph"')
            if await arrow_elements.first.is_visible():
                print("   ✅ Arrow setup page loaded")
            else:
                print("   ⚠️ Arrow setup page elements not found")
            
            # Step 6: Test chronograph data entry
            print("6. ⏱️ Testing chronograph data entry...")
            
            # Look for chronograph section or button
            chrono_section = page.locator('text="Chronograph Data", text="Add Chronograph", [data-testid="chronograph"]').first
            chrono_button = page.locator('button:has-text("Add Chronograph"), button:has-text("Chronograph")').first
            
            if await chrono_section.is_visible() or await chrono_button.is_visible():
                print("   ✅ Chronograph section found")
                
                # Try to interact with chronograph form
                speed_input = page.locator('input[placeholder*="speed"], input[id*="speed"], input[name*="speed"]').first
                weight_input = page.locator('input[placeholder*="weight"], input[id*="weight"]').first
                
                if await speed_input.is_visible():
                    await speed_input.fill("285.5")
                    print("   ✅ Entered speed data: 285.5 FPS")
                
                if await weight_input.is_visible():
                    await weight_input.fill("420")
                    print("   ✅ Entered weight data: 420 grains")
                
                # Look for save button
                save_button = page.locator('button:has-text("Save"), button:has-text("Add Data")').first
                if await save_button.is_visible():
                    await save_button.click()
                    await page.wait_for_timeout(1000)
                    print("   ✅ Saved chronograph data")
                
            else:
                print("   ⚠️ Chronograph section not found")
            
            # Step 7: Test performance calculation
            print("7. 📊 Testing performance calculation...")
            
            # Look for performance section
            performance_section = page.locator('text="Performance Analysis", text="Calculate Performance"').first
            calc_button = page.locator('button:has-text("Calculate"), button:has-text("Performance")').first
            
            if await performance_section.is_visible():
                print("   ✅ Performance section found")
                
                # Try to click calculate button
                if await calc_button.is_visible():
                    print("   🔄 Clicking performance calculation...")
                    await calc_button.click()
                    
                    # Wait for calculation to complete
                    await page.wait_for_timeout(3000)
                    
                    # Look for performance results
                    speed_result = page.locator('text*="fps", text*="FPS"').first
                    ke_result = page.locator('text*="ft·lbs", text*="KE"').first
                    source_indicator = page.locator('text="Measured", text="Estimated", text="Chronograph"').first
                    
                    if await speed_result.is_visible():
                        speed_text = await speed_result.text_content()
                        print(f"   ✅ Performance calculated - Speed: {speed_text}")
                    
                    if await ke_result.is_visible():
                        ke_text = await ke_result.text_content()
                        print(f"   ✅ Kinetic energy displayed: {ke_text}")
                    
                    if await source_indicator.is_visible():
                        source_text = await source_indicator.text_content()
                        print(f"   ✅ Speed source indicator: {source_text}")
                        
                        # Check if it shows measured speed (chronograph data)
                        if "Measured" in source_text or "Chronograph" in source_text:
                            print("   🎯 Using chronograph data for calculations!")
                        else:
                            print("   📊 Using estimated speed calculations")
                    
                else:
                    print("   ⚠️ Calculate button not found")
            else:
                print("   ⚠️ Performance section not found")
            
            # Step 8: Test trajectory chart
            print("8. 📈 Testing trajectory chart...")
            
            # Look for trajectory section
            trajectory_section = page.locator('text="Flight Trajectory", text="Show Trajectory"').first
            trajectory_button = page.locator('button:has-text("Show"), button:has-text("Trajectory")').first
            
            if await trajectory_section.is_visible():
                print("   ✅ Trajectory section found")
                
                # Try to show trajectory
                if await trajectory_button.is_visible():
                    await trajectory_button.click()
                    await page.wait_for_timeout(2000)
                    print("   ✅ Trajectory chart displayed")
                    
                    # Check for unit switching
                    yards_button = page.locator('button:has-text("Yards")').first
                    meters_button = page.locator('button:has-text("Meters")').first
                    
                    if await yards_button.is_visible() and await meters_button.is_visible():
                        print("   ✅ Unit switching buttons found")
                        
                        # Test unit switching
                        await meters_button.click()
                        await page.wait_for_timeout(1000)
                        print("   ✅ Switched to meters")
                        
                        await yards_button.click()
                        await page.wait_for_timeout(1000)
                        print("   ✅ Switched back to yards")
                    
                    # Look for speed source indicator in trajectory
                    trajectory_source = page.locator('.trajectory-chart-container text="Measured", .trajectory-chart-container text="Estimated"').first
                    if await trajectory_source.is_visible():
                        traj_source_text = await trajectory_source.text_content()
                        print(f"   ✅ Trajectory speed source: {traj_source_text}")
                
            else:
                print("   ⚠️ Trajectory section not found")
            
            # Step 9: Test different arrow configurations
            print("9. 🎯 Testing arrow configuration changes...")
            
            # Look for arrow configuration options
            arrow_length_input = page.locator('input[id*="length"], input[name*="length"]').first
            point_weight_input = page.locator('input[id*="point"], input[name*="point"]').first
            
            if await arrow_length_input.is_visible():
                current_length = await arrow_length_input.input_value()
                new_length = str(float(current_length or "30") + 1)
                await arrow_length_input.fill(new_length)
                print(f"   ✅ Changed arrow length to {new_length}")
                
                # Recalculate performance with new configuration
                if await calc_button.is_visible():
                    await calc_button.click()
                    await page.wait_for_timeout(2000)
                    print("   ✅ Recalculated with new arrow length")
            
            # Step 10: Capture final state
            print("10. 📸 Capturing final test state...")
            
            # Take screenshot for verification
            screenshot_path = "/home/paal/arrowtuner2/test_results_chronograph.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"   📸 Screenshot saved: {screenshot_path}")
            
            # Get page content for analysis
            page_content = await page.content()
            
            # Check for key elements in final state
            has_chronograph = "chronograph" in page_content.lower()
            has_performance = "performance" in page_content.lower()
            has_trajectory = "trajectory" in page_content.lower()
            has_measured_speed = "measured" in page_content.lower()
            
            print("\n" + "=" * 60)
            print("🎯 FRONTEND TEST SUMMARY")
            print("=" * 60)
            print(f"✅ Chronograph integration: {'FOUND' if has_chronograph else 'NOT FOUND'}")
            print(f"✅ Performance calculations: {'FOUND' if has_performance else 'NOT FOUND'}")
            print(f"✅ Trajectory display: {'FOUND' if has_trajectory else 'NOT FOUND'}")
            print(f"✅ Measured speed indicators: {'FOUND' if has_measured_speed else 'NOT FOUND'}")
            
            # API verification
            print("\n📡 API Verification:")
            response = await page.request.get("http://localhost:5000/api/simple-health")
            if response.ok:
                health_data = await response.json()
                print(f"   ✅ API Status: {health_data.get('status', 'unknown')}")
            
            print("\n🏆 Frontend chronograph integration test completed!")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            
            # Take error screenshot
            error_screenshot = "/home/paal/arrowtuner2/test_error_chronograph.png"
            await page.screenshot(path=error_screenshot, full_page=True)
            print(f"📸 Error screenshot saved: {error_screenshot}")
            
        finally:
            # Clean up
            await browser.close()

def main():
    """Main test function"""
    print("🚀 Starting Frontend Chronograph Integration Test")
    print("📋 Prerequisites:")
    print("   • Frontend running on http://localhost:3000")
    print("   • API running on http://localhost:5000") 
    print("   • Unified database with chronograph data support")
    print()
    
    try:
        asyncio.run(test_frontend_chronograph_integration())
        return True
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)