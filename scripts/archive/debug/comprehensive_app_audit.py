#!/usr/bin/env python3
"""
Comprehensive Playwright Application Audit
Senior Full Stack Developer Testing Suite

This script performs extensive testing of the Archery Tools application including:
- Mobile responsiveness testing
- Equipment management workflows
- Bow setup creation and management
- Error handling and console monitoring
- Performance analysis
- Cross-page functionality validation
"""

import asyncio
import sys
import time
import json
from datetime import datetime
from playwright.async_api import async_playwright, expect
from pathlib import Path

class ArcheryToolsAudit:
    def __init__(self):
        self.test_results = {
            'mobile_issues': [],
            'console_errors': [],
            'functionality_issues': [],
            'performance_issues': [],
            'ui_issues': [],
            'success_tests': []
        }
        
        # Viewport configurations for responsive testing
        self.viewports = {
            'mobile_small': {'width': 375, 'height': 667},  # iPhone SE
            'mobile_standard': {'width': 390, 'height': 844},  # iPhone 12 Pro
            'tablet': {'width': 768, 'height': 1024},  # iPad
            'desktop': {'width': 1920, 'height': 1080}  # Desktop
        }
        
        self.screenshot_dir = Path("/home/paal/arrowtuner2/audit_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
    async def run_comprehensive_audit(self):
        """Execute the complete application audit"""
        print("🔍 Starting Comprehensive Archery Tools Application Audit")
        print("=" * 80)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=500)
            
            try:
                # Phase 1: Desktop functionality audit
                await self.phase1_desktop_audit(browser)
                
                # Phase 2: Mobile responsiveness testing
                await self.phase2_mobile_testing(browser)
                
                # Phase 3: Equipment management testing
                await self.phase3_equipment_testing(browser)
                
                # Phase 4: Bow and arrow management
                await self.phase4_bow_arrow_testing(browser)
                
                # Phase 5: Cross-page navigation testing
                await self.phase5_navigation_testing(browser)
                
                # Phase 6: Error handling and edge cases
                await self.phase6_error_testing(browser)
                
                # Generate comprehensive report
                await self.generate_audit_report()
                
            finally:
                await browser.close()
    
    async def phase1_desktop_audit(self, browser):
        """Phase 1: Desktop functionality and console error audit"""
        print("📋 Phase 1: Desktop Functionality Audit")
        print("-" * 50)
        
        context = await browser.new_context(viewport=self.viewports['desktop'])
        page = await context.new_page()
        
        # Monitor console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            'type': msg.type,
            'text': msg.text,
            'location': msg.location
        }))
        
        try:
            # Navigate to application
            print("1.1 🌐 Loading application...")
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            
            # Take baseline screenshot
            await page.screenshot(path=self.screenshot_dir / "01_desktop_home.png", full_page=True)
            
            # Check for immediate console errors
            await asyncio.sleep(2)
            critical_errors = [msg for msg in console_messages if msg['type'] == 'error']
            if critical_errors:
                self.test_results['console_errors'].extend(critical_errors)
                print(f"   ⚠️  Found {len(critical_errors)} console errors on load")
            else:
                print("   ✅ No critical console errors on initial load")
                self.test_results['success_tests'].append("Desktop application loads without console errors")
            
            # Test main navigation
            print("1.2 🧭 Testing main navigation...")
            nav_items = await page.locator('nav a, header a').all()
            print(f"   📍 Found {len(nav_items)} navigation items")
            
            # Test page title and meta information
            title = await page.title()
            print(f"   📄 Page title: {title}")
            if "ArrowTune" in title or "Archery" in title:
                self.test_results['success_tests'].append("Page has appropriate title")
            else:
                self.test_results['ui_issues'].append("Page title may not be descriptive enough")
            
            # Check for authentication status
            login_button = page.locator('button:has-text("Login"), button:has-text("Logout")')
            if await login_button.count() > 0:
                auth_text = await login_button.first.inner_text()
                print(f"   🔐 Authentication status: {auth_text}")
                if "Logout" in auth_text:
                    self.test_results['success_tests'].append("User is authenticated")
                else:
                    print("   ℹ️  User not authenticated - testing public functionality")
            
        except Exception as e:
            self.test_results['functionality_issues'].append(f"Phase 1 error: {str(e)}")
            print(f"   ❌ Error in Phase 1: {e}")
        
        finally:
            await context.close()
    
    async def phase2_mobile_testing(self, browser):
        """Phase 2: Mobile responsiveness comprehensive testing"""
        print("\n📱 Phase 2: Mobile Responsiveness Testing")
        print("-" * 50)
        
        for device_name, viewport in self.viewports.items():
            print(f"2.{list(self.viewports.keys()).index(device_name) + 1} Testing {device_name} ({viewport['width']}x{viewport['height']})")
            
            context = await browser.new_context(viewport=viewport)
            page = await context.new_page()
            
            try:
                await page.goto("http://localhost:3000")
                await page.wait_for_load_state("networkidle")
                
                # Take viewport screenshot
                await page.screenshot(path=self.screenshot_dir / f"02_{device_name}_home.png", full_page=True)
                
                # Test mobile menu if on mobile viewport
                if 'mobile' in device_name:
                    await self.test_mobile_navigation(page, device_name)
                
                # Test form elements responsiveness
                await self.test_form_responsiveness(page, device_name)
                
                # Test touch targets
                await self.test_touch_targets(page, device_name)
                
                # Test horizontal scrolling issues
                await self.test_horizontal_scroll(page, device_name)
                
            except Exception as e:
                self.test_results['mobile_issues'].append(f"{device_name}: {str(e)}")
            
            finally:
                await context.close()
    
    async def test_mobile_navigation(self, page, device_name):
        """Test mobile navigation menu functionality"""
        # Look for mobile menu button
        menu_button = page.locator('button:has-text("Menu"), [aria-label*="menu"], .menu-toggle')
        
        if await menu_button.count() > 0:
            print(f"   📱 Testing mobile menu for {device_name}")
            await menu_button.first.click()
            await page.wait_for_timeout(500)
            
            # Check if menu opened
            nav_menu = page.locator('nav, .mobile-menu, [role="navigation"]')
            if await nav_menu.is_visible():
                self.test_results['success_tests'].append(f"Mobile menu works on {device_name}")
                print("   ✅ Mobile menu opens correctly")
            else:
                self.test_results['mobile_issues'].append(f"Mobile menu doesn't open properly on {device_name}")
                print("   ❌ Mobile menu doesn't open properly")
        else:
            self.test_results['mobile_issues'].append(f"No mobile menu button found on {device_name}")
    
    async def test_form_responsiveness(self, page, device_name):
        """Test form elements on different screen sizes"""
        forms = await page.locator('form, input, select, textarea').all()
        
        if forms:
            print(f"   📝 Testing {len(forms)} form elements on {device_name}")
            
            # Test first form element for sizing
            first_form = forms[0]
            if await first_form.is_visible():
                box = await first_form.bounding_box()
                if box and box['width'] < 50:  # Too narrow
                    self.test_results['mobile_issues'].append(f"Form elements too narrow on {device_name}")
                elif box and box['width'] > 0:
                    self.test_results['success_tests'].append(f"Form elements properly sized on {device_name}")
    
    async def test_touch_targets(self, page, device_name):
        """Test touch target sizes for mobile devices"""
        if 'mobile' in device_name:
            buttons = await page.locator('button, a, [role="button"]').all()
            
            small_targets = 0
            for button in buttons[:5]:  # Test first 5 buttons
                if await button.is_visible():
                    box = await button.bounding_box()
                    if box and (box['height'] < 44 or box['width'] < 44):  # iOS guidelines
                        small_targets += 1
            
            if small_targets > 0:
                self.test_results['mobile_issues'].append(f"{small_targets} touch targets too small on {device_name}")
            else:
                self.test_results['success_tests'].append(f"Touch targets appropriately sized on {device_name}")
    
    async def test_horizontal_scroll(self, page, device_name):
        """Check for unwanted horizontal scrolling"""
        if 'mobile' in device_name:
            # Check if page has horizontal scroll
            scroll_width = await page.evaluate("document.documentElement.scrollWidth")
            viewport_width = await page.evaluate("window.innerWidth")
            
            if scroll_width > viewport_width + 5:  # 5px tolerance
                self.test_results['mobile_issues'].append(f"Horizontal scroll detected on {device_name}")
            else:
                self.test_results['success_tests'].append(f"No horizontal scroll issues on {device_name}")
    
    async def phase3_equipment_testing(self, browser):
        """Phase 3: Equipment management comprehensive testing"""
        print("\n🔧 Phase 3: Equipment Management Testing")
        print("-" * 50)
        
        context = await browser.new_context(viewport=self.viewports['desktop'])
        page = await context.new_page()
        
        try:
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            
            # Navigate to bow setups to test equipment
            await self.navigate_to_bow_setups(page)
            
            # Test equipment categories
            equipment_categories = ['String', 'Sight', 'Scope', 'Stabilizer', 'Arrow Rest', 'Plunger', 'Weight', 'Other']
            
            for category in equipment_categories:
                await self.test_equipment_category(page, category)
            
            await page.screenshot(path=self.screenshot_dir / "03_equipment_testing.png", full_page=True)
            
        except Exception as e:
            self.test_results['functionality_issues'].append(f"Equipment testing error: {str(e)}")
        
        finally:
            await context.close()
    
    async def navigate_to_bow_setups(self, page):
        """Navigate to bow setups page"""
        # Look for bow setup navigation
        setup_link = page.locator('a:has-text("Setup"), a:has-text("Bow"), a[href*="setup"]')
        
        if await setup_link.count() > 0:
            await setup_link.first.click()
            await page.wait_for_load_state("networkidle")
            print("   🏹 Navigated to bow setups")
        else:
            print("   ⚠️  Could not find bow setup navigation")
    
    async def test_equipment_category(self, page, category):
        """Test adding equipment for a specific category"""
        print(f"   🔧 Testing {category} equipment")
        
        try:
            # Look for equipment management button/section
            equipment_button = page.locator(f'button:has-text("Equipment"), button:has-text("{category}"), a:has-text("Equipment")')
            
            if await equipment_button.count() > 0:
                await equipment_button.first.click()
                await page.wait_for_timeout(1000)
                
                # Look for add equipment option
                add_button = page.locator('button:has-text("Add"), button:has-text("Manage")')
                if await add_button.count() > 0:
                    await add_button.first.click()
                    await page.wait_for_timeout(500)
                    
                    # Check if category-specific form appears
                    category_form = page.locator(f'text="{category}", [data-category="{category.lower()}"]')
                    if await category_form.count() > 0:
                        self.test_results['success_tests'].append(f"Equipment form opens for {category}")
                    else:
                        self.test_results['functionality_issues'].append(f"No form found for {category} equipment")
                        
        except Exception as e:
            self.test_results['functionality_issues'].append(f"Error testing {category} equipment: {str(e)}")
    
    async def phase4_bow_arrow_testing(self, browser):
        """Phase 4: Bow and arrow management testing"""
        print("\n🏹 Phase 4: Bow and Arrow Management Testing")
        print("-" * 50)
        
        context = await browser.new_context(viewport=self.viewports['desktop'])
        page = await context.new_page()
        
        try:
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            
            # Test bow creation workflow
            await self.test_bow_creation(page)
            
            # Test arrow management
            await self.test_arrow_management(page)
            
            # Test calculator functionality
            await self.test_calculator_functionality(page)
            
            await page.screenshot(path=self.screenshot_dir / "04_bow_arrow_testing.png", full_page=True)
            
        except Exception as e:
            self.test_results['functionality_issues'].append(f"Bow/Arrow testing error: {str(e)}")
        
        finally:
            await context.close()
    
    async def test_bow_creation(self, page):
        """Test bow setup creation workflow"""
        print("   🎯 Testing bow creation workflow")
        
        # Look for new bow/setup creation
        new_bow_button = page.locator('button:has-text("Add"), button:has-text("New"), button:has-text("Create")')
        
        if await new_bow_button.count() > 0:
            await new_bow_button.first.click()
            await page.wait_for_timeout(1000)
            
            # Check for bow type selection
            bow_types = page.locator('select, input[type="radio"], text="Compound", text="Recurve", text="Traditional"')
            if await bow_types.count() > 0:
                self.test_results['success_tests'].append("Bow creation form accessible")
            else:
                self.test_results['functionality_issues'].append("Bow creation form not found")
        else:
            self.test_results['functionality_issues'].append("No bow creation button found")
    
    async def test_arrow_management(self, page):
        """Test arrow management functionality"""
        print("   🎯 Testing arrow management")
        
        # Look for arrow-related functionality
        arrow_elements = page.locator('text="Arrow", a[href*="arrow"], button:has-text("Arrow")')
        
        if await arrow_elements.count() > 0:
            self.test_results['success_tests'].append("Arrow management interface found")
        else:
            self.test_results['functionality_issues'].append("Arrow management interface not accessible")
    
    async def test_calculator_functionality(self, page):
        """Test calculator and analysis tools"""
        print("   🧮 Testing calculator functionality")
        
        # Look for calculator links
        calc_link = page.locator('a:has-text("Calculator"), a[href*="calculator"], button:has-text("Calculate")')
        
        if await calc_link.count() > 0:
            await calc_link.first.click()
            await page.wait_for_load_state("networkidle")
            
            # Check for calculator interface
            calc_elements = page.locator('input[type="number"], input[placeholder*="weight"], input[placeholder*="length"]')
            if await calc_elements.count() > 0:
                self.test_results['success_tests'].append("Calculator interface functional")
            else:
                self.test_results['functionality_issues'].append("Calculator interface missing elements")
        else:
            self.test_results['functionality_issues'].append("Calculator not accessible")
    
    async def phase5_navigation_testing(self, browser):
        """Phase 5: Cross-page navigation testing"""
        print("\n🧭 Phase 5: Navigation and Page Testing")
        print("-" * 50)
        
        context = await browser.new_context(viewport=self.viewports['desktop'])
        page = await context.new_page()
        
        try:
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            
            # Test all main navigation links
            nav_links = await page.locator('nav a, header a').all()
            
            for i, link in enumerate(nav_links[:8]):  # Test first 8 links
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    
                    if href and href.startswith('/'):
                        print(f"   🔗 Testing navigation to: {text} ({href})")
                        
                        await link.click()
                        await page.wait_for_load_state("networkidle")
                        
                        # Check if page loaded correctly
                        current_url = page.url
                        if href in current_url:
                            self.test_results['success_tests'].append(f"Navigation to {text} works")
                        else:
                            self.test_results['functionality_issues'].append(f"Navigation to {text} failed")
                        
                        # Take screenshot of each page
                        await page.screenshot(path=self.screenshot_dir / f"05_page_{i:02d}_{text.replace(' ', '_')}.png")
                        
                except Exception as e:
                    self.test_results['functionality_issues'].append(f"Navigation error for {text}: {str(e)}")
            
        except Exception as e:
            self.test_results['functionality_issues'].append(f"Navigation testing error: {str(e)}")
        
        finally:
            await context.close()
    
    async def phase6_error_testing(self, browser):
        """Phase 6: Error handling and edge cases"""
        print("\n🚨 Phase 6: Error Handling and Edge Cases")
        print("-" * 50)
        
        context = await browser.new_context(viewport=self.viewports['desktop'])
        page = await context.new_page()
        
        # Monitor console for errors during testing
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg) if msg.type == 'error' else None)
        
        try:
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            
            # Test invalid form submissions
            await self.test_form_validation(page)
            
            # Test network error handling
            await self.test_network_errors(page)
            
            # Test browser back/forward navigation
            await self.test_browser_navigation(page)
            
            # Report console errors found during testing
            if console_errors:
                self.test_results['console_errors'].extend([{
                    'type': msg.type,
                    'text': msg.text,
                    'location': str(msg.location)
                } for msg in console_errors])
            
        except Exception as e:
            self.test_results['functionality_issues'].append(f"Error testing failed: {str(e)}")
        
        finally:
            await context.close()
    
    async def test_form_validation(self, page):
        """Test form validation and error handling"""
        print("   📝 Testing form validation")
        
        # Find forms and test empty submissions
        forms = await page.locator('form').all()
        
        for form in forms[:3]:  # Test first 3 forms
            try:
                submit_button = form.locator('button[type="submit"], input[type="submit"], button:has-text("Save"), button:has-text("Submit")')
                
                if await submit_button.count() > 0:
                    await submit_button.first.click()
                    await page.wait_for_timeout(500)
                    
                    # Check for validation messages
                    validation_msgs = page.locator('.error, .validation, [aria-invalid="true"], .field-error')
                    if await validation_msgs.count() > 0:
                        self.test_results['success_tests'].append("Form validation working")
                    
            except Exception as e:
                # Expected - forms might prevent submission
                pass
    
    async def test_network_errors(self, page):
        """Test handling of network errors"""
        print("   🌐 Testing network error handling")
        
        # This is a basic test - in real scenarios you'd mock network failures
        try:
            # Test navigation to non-existent page
            await page.goto("http://localhost:3000/non-existent-page")
            await page.wait_for_timeout(2000)
            
            # Check if there's appropriate error handling
            error_elements = page.locator('text="404", text="Not Found", text="Error"')
            if await error_elements.count() > 0:
                self.test_results['success_tests'].append("404 error handling present")
            else:
                self.test_results['functionality_issues'].append("No 404 error handling found")
                
        except Exception as e:
            self.test_results['functionality_issues'].append(f"Network error testing failed: {str(e)}")
    
    async def test_browser_navigation(self, page):
        """Test browser back/forward navigation"""
        print("   ⬅️  Testing browser navigation")
        
        try:
            # Navigate to a few pages
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            
            # Click a link
            link = page.locator('a[href^="/"]').first
            if await link.count() > 0:
                await link.click()
                await page.wait_for_load_state("networkidle")
                
                # Test back navigation
                await page.go_back()
                await page.wait_for_load_state("networkidle")
                
                # Test forward navigation
                await page.go_forward()
                await page.wait_for_load_state("networkidle")
                
                self.test_results['success_tests'].append("Browser navigation working")
            
        except Exception as e:
            self.test_results['functionality_issues'].append(f"Browser navigation test failed: {str(e)}")
    
    async def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE AUDIT REPORT")
        print("=" * 80)
        
        # Summary statistics
        total_tests = sum(len(issues) for issues in self.test_results.values())
        success_count = len(self.test_results['success_tests'])
        issue_count = total_tests - success_count
        
        print(f"📈 SUMMARY:")
        print(f"   ✅ Successful Tests: {success_count}")
        print(f"   ⚠️  Issues Found: {issue_count}")
        print(f"   📱 Mobile Issues: {len(self.test_results['mobile_issues'])}")
        print(f"   🚨 Console Errors: {len(self.test_results['console_errors'])}")
        print(f"   🔧 Functionality Issues: {len(self.test_results['functionality_issues'])}")
        print(f"   🎨 UI Issues: {len(self.test_results['ui_issues'])}")
        print(f"   ⚡ Performance Issues: {len(self.test_results['performance_issues'])}")
        
        # Detailed findings
        print(f"\n🔍 DETAILED FINDINGS:")
        
        if self.test_results['mobile_issues']:
            print(f"\n📱 MOBILE RESPONSIVENESS ISSUES:")
            for issue in self.test_results['mobile_issues']:
                print(f"   • {issue}")
        
        if self.test_results['console_errors']:
            print(f"\n🚨 CONSOLE ERRORS:")
            for error in self.test_results['console_errors']:
                print(f"   • {error.get('type', 'error')}: {error.get('text', 'Unknown error')}")
        
        if self.test_results['functionality_issues']:
            print(f"\n🔧 FUNCTIONALITY ISSUES:")
            for issue in self.test_results['functionality_issues']:
                print(f"   • {issue}")
        
        if self.test_results['ui_issues']:
            print(f"\n🎨 UI/UX ISSUES:")
            for issue in self.test_results['ui_issues']:
                print(f"   • {issue}")
        
        # Success highlights
        if self.test_results['success_tests']:
            print(f"\n✅ WORKING FUNCTIONALITY:")
            for success in self.test_results['success_tests'][:10]:  # Show first 10
                print(f"   • {success}")
            if len(self.test_results['success_tests']) > 10:
                print(f"   ... and {len(self.test_results['success_tests']) - 10} more")
        
        # Save detailed report to file
        report_file = Path("/home/paal/arrowtuner2/audit_report.json")
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'success_count': success_count,
                    'issue_count': issue_count
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        print(f"📸 Screenshots saved to: {self.screenshot_dir}")
        
        # Generate priority fix list
        await self.generate_fix_priority_list()
    
    async def generate_fix_priority_list(self):
        """Generate prioritized list of fixes needed"""
        print(f"\n🔧 PRIORITY FIX LIST:")
        print("-" * 50)
        
        # High Priority (Critical Issues)
        high_priority = []
        high_priority.extend(self.test_results['console_errors'])
        high_priority.extend([issue for issue in self.test_results['functionality_issues'] if 'error' in issue.lower()])
        
        if high_priority:
            print("🚨 HIGH PRIORITY (Critical Fixes):")
            for i, issue in enumerate(high_priority[:5], 1):
                print(f"   {i}. {issue}")
        
        # Medium Priority (UX/Mobile Issues)
        medium_priority = []
        medium_priority.extend(self.test_results['mobile_issues'])
        medium_priority.extend(self.test_results['ui_issues'])
        
        if medium_priority:
            print("\n⚠️  MEDIUM PRIORITY (UX Improvements):")
            for i, issue in enumerate(medium_priority[:5], 1):
                print(f"   {i}. {issue}")
        
        # Low Priority (Enhancement Opportunities)
        low_priority = []
        low_priority.extend([issue for issue in self.test_results['functionality_issues'] if 'not found' in issue.lower()])
        
        if low_priority:
            print("\n📋 LOW PRIORITY (Enhancements):")
            for i, issue in enumerate(low_priority[:3], 1):
                print(f"   {i}. {issue}")
        
        print(f"\n🎯 RECOMMENDED NEXT STEPS:")
        print("   1. Fix all console errors (affects user experience)")
        print("   2. Resolve mobile responsiveness issues")
        print("   3. Test and fix equipment management workflows")
        print("   4. Enhance form validation and error handling")
        print("   5. Optimize performance and loading times")


async def main():
    """Run the comprehensive audit"""
    audit = ArcheryToolsAudit()
    await audit.run_comprehensive_audit()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        sys.exit(1)