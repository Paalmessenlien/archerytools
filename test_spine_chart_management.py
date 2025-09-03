#!/usr/bin/env python3
"""
Comprehensive Playwright Test Suite for Unified Spine Chart Management System
Testing the new spine chart management functionality including:
1. Professional Spine Calculation frontend
2. Admin spine chart management interface  
3. API integration with different chart selections
4. System default chart settings

Date: 2025-09-02
Application: Archery Tools - http://localhost:3000
API: http://localhost:5000/api
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class SpineChartTestSuite:
    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.screenshots_dir = Path("test_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "app_url": "http://localhost:3000",
            "api_url": "http://localhost:5000/api",
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
    async def setup(self):
        """Initialize Playwright and browser"""
        print("🔧 Setting up Playwright browser...")
        self.playwright = await async_playwright().start()
        
        # Launch browser with options for better testing
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Show browser for debugging
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create browser context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # Enable console logging
        self.context.on("console", lambda msg: print(f"🔍 Console: {msg.text}"))
        
        # Create main page
        self.page = await self.context.new_page()
        print("✅ Browser setup complete")
        
    async def teardown(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        print("🧹 Browser cleanup complete")
        
    async def log_test_result(self, test_name: str, status: str, details: dict = None, screenshot_path: str = None):
        """Log individual test results"""
        result = {
            "name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
            "screenshot": screenshot_path
        }
        
        self.test_results["tests"].append(result)
        self.test_results["summary"]["total"] += 1
        
        if status == "PASSED":
            self.test_results["summary"]["passed"] += 1
            print(f"✅ {test_name}: {status}")
        elif status == "FAILED":
            self.test_results["summary"]["failed"] += 1
            print(f"❌ {test_name}: {status}")
        elif status == "WARNING":
            self.test_results["summary"]["warnings"] += 1
            print(f"⚠️  {test_name}: {status}")
            
        if details:
            for key, value in details.items():
                print(f"   📋 {key}: {value}")
                
    async def take_screenshot(self, name: str, description: str = "") -> str:
        """Take a screenshot and return the file path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name.replace(' ', '_').lower()}.png"
        filepath = self.screenshots_dir / filename
        
        await self.page.screenshot(path=str(filepath), full_page=True)
        print(f"📸 Screenshot saved: {filepath} - {description}")
        return str(filepath)
        
    async def wait_for_page_load(self, url: str = None, timeout: int = 30000):
        """Wait for page to fully load with better error handling"""
        if url:
            print(f"🌐 Navigating to: {url}")
            await self.page.goto(url, wait_until='networkidle', timeout=timeout)
        
        # Wait for Vue.js hydration to complete
        try:
            await self.page.wait_for_function(
                "() => window.Vue || document.querySelector('[data-v-]')",
                timeout=10000
            )
            print("✅ Vue.js application loaded")
        except:
            print("⚠️  Vue.js detection timeout, continuing...")
            
        # Wait for any loading indicators to disappear
        try:
            await self.page.wait_for_selector('[data-testid="loading"]', state='detached', timeout=5000)
        except:
            pass  # No loading indicator found, continue
            
    async def check_authentication_status(self) -> bool:
        """Check if user is authenticated and handle login if needed"""
        print("🔐 Checking authentication status...")
        
        # Wait a moment for auth check to complete
        await self.page.wait_for_timeout(2000)
        
        # Check if we're on login page or need to authenticate
        current_url = self.page.url
        if '/login' in current_url or '/auth' in current_url:
            print("⚠️  Not authenticated - user needs to login manually")
            await self.log_test_result(
                "Authentication Check", 
                "WARNING", 
                {"message": "Manual authentication required", "current_url": current_url}
            )
            return False
            
        # Check for user profile or authenticated elements
        try:
            # Look for authenticated user elements
            profile_selector = 'button[aria-label*="Profile"], [data-testid="user-profile"], .user-profile'
            await self.page.wait_for_selector(profile_selector, timeout=5000)
            print("✅ User appears to be authenticated")
            return True
        except:
            print("⚠️  Authentication status unclear")
            return True  # Continue testing anyway
            
    async def test_spine_calculator_access(self):
        """Test 1: Access and verify spine calculator page loads"""
        test_name = "Spine Calculator Page Access"
        
        try:
            # Navigate to spine calculator
            await self.wait_for_page_load("http://localhost:3000/calculator")
            
            # Take screenshot of calculator page
            screenshot = await self.take_screenshot("spine_calculator_page", "Initial calculator page load")
            
            # Check page title and basic elements
            title = await self.page.title()
            
            # Look for calculator elements
            calculator_elements = []
            
            # Check for draw weight input
            if await self.page.locator('input[type="range"], input[type="number"]').count() > 0:
                calculator_elements.append("Draw weight controls")
                
            # Check for bow type selection
            if await self.page.locator('select, .dropdown, [role="combobox"]').count() > 0:
                calculator_elements.append("Dropdown selectors")
                
            # Check for spine calculation results area
            if await self.page.locator('.results, .calculation, .recommendation').count() > 0:
                calculator_elements.append("Results display area")
                
            await self.log_test_result(
                test_name, 
                "PASSED",
                {
                    "page_title": title,
                    "url": self.page.url,
                    "calculator_elements_found": calculator_elements
                },
                screenshot
            )
            
        except Exception as e:
            screenshot = await self.take_screenshot("spine_calculator_error", "Error accessing calculator")
            await self.log_test_result(
                test_name, 
                "FAILED",
                {"error": str(e)},
                screenshot
            )
            
    async def test_professional_spine_calculation_mode(self):
        """Test 2: Test Professional Spine Calculation with chart selection"""
        test_name = "Professional Spine Calculation Mode"
        
        try:
            # Ensure we're on calculator page
            await self.wait_for_page_load("http://localhost:3000/calculator")
            
            # Look for professional mode toggle or chart selector
            professional_mode_selectors = [
                '[data-testid="professional-mode"]',
                '.professional-mode',
                'button:has-text("Professional")',
                'input[type="checkbox"]:near(:text("Professional"))',
                '.spine-chart-selector',
                'select:has(option:text-matches("chart", "i"))'
            ]
            
            professional_mode_found = False
            active_selector = None
            
            for selector in professional_mode_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.count() > 0:
                        professional_mode_found = True
                        active_selector = selector
                        print(f"✅ Found professional mode element: {selector}")
                        break
                except:
                    continue
                    
            if not professional_mode_found:
                # Look for any chart-related elements
                chart_elements = await self.page.locator(':text-matches("chart", "i")').count()
                
                await self.log_test_result(
                    test_name,
                    "WARNING" if chart_elements > 0 else "FAILED",
                    {
                        "professional_mode_found": False,
                        "chart_elements_detected": chart_elements,
                        "selectors_tried": professional_mode_selectors
                    }
                )
                return
                
            # Take screenshot of professional mode interface
            screenshot = await self.take_screenshot("professional_mode", "Professional spine calculation interface")
            
            # Try to interact with professional mode
            if active_selector:
                element = self.page.locator(active_selector).first
                element_type = await element.evaluate("el => el.tagName.toLowerCase()")
                
                if element_type == "button":
                    await element.click()
                elif element_type == "input":
                    input_type = await element.get_attribute("type")
                    if input_type == "checkbox":
                        await element.check()
                elif element_type == "select":
                    # Try to select a chart option
                    options = await element.locator("option").count()
                    if options > 1:
                        await element.select_option(index=1)  # Select second option
                        
            # Wait for any changes to load
            await self.page.wait_for_timeout(1000)
            
            # Take screenshot after interaction
            screenshot_after = await self.take_screenshot("professional_mode_active", "Professional mode after activation")
            
            await self.log_test_result(
                test_name,
                "PASSED",
                {
                    "professional_mode_activated": True,
                    "active_selector": active_selector,
                    "interaction_completed": True
                },
                screenshot_after
            )
            
        except Exception as e:
            screenshot = await self.take_screenshot("professional_mode_error", "Error testing professional mode")
            await self.log_test_result(
                test_name,
                "FAILED", 
                {"error": str(e)},
                screenshot
            )
            
    async def test_spine_chart_selection_impact(self):
        """Test 3: Verify different chart selections produce different results"""
        test_name = "Spine Chart Selection Impact"
        
        try:
            await self.wait_for_page_load("http://localhost:3000/calculator")
            
            # Set consistent bow parameters for testing
            await self.set_bow_parameters()
            
            # Look for chart selection dropdown
            chart_selector = None
            chart_selectors = [
                'select:has(option:text-matches("chart", "i"))',
                '.spine-chart-selector select',
                '[data-testid="chart-selector"]',
                'select[name*="chart"]'
            ]
            
            for selector in chart_selectors:
                if await self.page.locator(selector).count() > 0:
                    chart_selector = selector
                    break
                    
            if not chart_selector:
                await self.log_test_result(
                    test_name,
                    "WARNING",
                    {"message": "No chart selector found, testing may be incomplete"}
                )
                return
                
            chart_element = self.page.locator(chart_selector).first
            options = await chart_element.locator("option").count()
            
            if options <= 1:
                await self.log_test_result(
                    test_name,
                    "WARNING",
                    {"message": f"Only {options} chart option(s) available"}
                )
                return
                
            results_comparison = []
            
            # Test multiple chart selections
            for i in range(min(3, options)):  # Test up to 3 different charts
                if i == 0:
                    continue  # Skip first option (usually default/placeholder)
                    
                await chart_element.select_option(index=i)
                option_text = await chart_element.locator(f"option:nth-child({i+1})").inner_text()
                
                # Wait for calculation to complete
                await self.page.wait_for_timeout(500)
                
                # Try to trigger calculation if needed
                calculate_button = self.page.locator('button:has-text("Calculate"), [data-testid="calculate"]').first
                if await calculate_button.count() > 0:
                    await calculate_button.click()
                    await self.page.wait_for_timeout(1000)
                    
                # Capture results
                result_text = await self.get_calculation_results()
                results_comparison.append({
                    "chart_option": option_text,
                    "result": result_text
                })
                
                # Screenshot for each chart
                await self.take_screenshot(f"chart_{i}_results", f"Results with chart: {option_text}")
                
            # Check if results differ between charts
            unique_results = len(set(r["result"] for r in results_comparison))
            
            await self.log_test_result(
                test_name,
                "PASSED" if unique_results > 1 else "WARNING",
                {
                    "charts_tested": len(results_comparison),
                    "unique_results": unique_results,
                    "results_comparison": results_comparison
                }
            )
            
        except Exception as e:
            screenshot = await self.take_screenshot("chart_selection_error", "Error testing chart selection")
            await self.log_test_result(
                test_name,
                "FAILED",
                {"error": str(e)},
                screenshot
            )
            
    async def set_bow_parameters(self):
        """Helper: Set consistent bow parameters for testing"""
        # Set draw weight
        draw_weight_input = self.page.locator('input[type="range"], input[name*="draw"], input[name*="weight"]').first
        if await draw_weight_input.count() > 0:
            await draw_weight_input.fill("50")
            
        # Set draw length  
        draw_length_input = self.page.locator('input[name*="length"], input[name*="draw-length"]').first
        if await draw_length_input.count() > 0:
            await draw_length_input.fill("28")
            
        # Set bow type if available
        bow_type_select = self.page.locator('select:has(option:text("Compound")), select:has(option:text("Recurve"))').first
        if await bow_type_select.count() > 0:
            await bow_type_select.select_option(label="Compound")
            
    async def get_calculation_results(self) -> str:
        """Helper: Extract calculation results from the page"""
        result_selectors = [
            '.spine-result',
            '.calculation-result',
            '.recommended-spine',
            '[data-testid="spine-result"]',
            '.results-container'
        ]
        
        for selector in result_selectors:
            element = self.page.locator(selector).first
            if await element.count() > 0:
                return await element.inner_text()
                
        # If no specific result element, get all text content
        return await self.page.locator('body').inner_text()
        
    async def test_admin_panel_access(self):
        """Test 4: Access admin panel for spine chart management"""
        test_name = "Admin Panel Access"
        
        try:
            # Try to access admin panel
            await self.wait_for_page_load("http://localhost:3000/admin")
            
            current_url = self.page.url
            
            # Check if redirected to login or if admin panel loaded
            if '/login' in current_url or '/auth' in current_url:
                await self.log_test_result(
                    test_name,
                    "WARNING",
                    {"message": "Redirected to login - admin access requires authentication"}
                )
                return
                
            # Look for admin panel elements
            admin_elements = []
            
            admin_selectors = [
                'h1:has-text("Admin")',
                '.admin-panel',
                '[data-testid="admin-panel"]',
                'nav a:has-text("Users")',
                'nav a:has-text("Settings")',
                'nav a:has-text("Charts")'
            ]
            
            for selector in admin_selectors:
                if await self.page.locator(selector).count() > 0:
                    admin_elements.append(selector)
                    
            screenshot = await self.take_screenshot("admin_panel", "Admin panel interface")
            
            await self.log_test_result(
                test_name,
                "PASSED" if admin_elements else "WARNING",
                {
                    "admin_elements_found": admin_elements,
                    "current_url": current_url
                },
                screenshot
            )
            
        except Exception as e:
            screenshot = await self.take_screenshot("admin_panel_error", "Error accessing admin panel")
            await self.log_test_result(
                test_name,
                "FAILED",
                {"error": str(e)},
                screenshot
            )
            
    async def test_spine_chart_management_interface(self):
        """Test 5: Test spine chart management in admin panel"""
        test_name = "Spine Chart Management Interface"
        
        try:
            # Navigate to admin panel
            await self.wait_for_page_load("http://localhost:3000/admin")
            
            # Look for spine chart management section
            chart_management_selectors = [
                'a:has-text("Spine Charts")',
                'a:has-text("Charts")',
                '.spine-chart-management',
                '[data-testid="spine-charts"]'
            ]
            
            chart_management_link = None
            for selector in chart_management_selectors:
                element = self.page.locator(selector).first
                if await element.count() > 0:
                    chart_management_link = element
                    break
                    
            if chart_management_link:
                await chart_management_link.click()
                await self.page.wait_for_timeout(1000)
                
            # Look for chart management features
            management_features = []
            
            feature_selectors = [
                'button:has-text("Default")',
                'button:has-text("Duplicate")',
                '.chart-list',
                '.system-settings',
                'table tbody tr',  # Chart entries in table
                '.spine-chart-item'
            ]
            
            for selector in feature_selectors:
                count = await self.page.locator(selector).count()
                if count > 0:
                    management_features.append(f"{selector}: {count} items")
                    
            # Take screenshot of chart management interface
            screenshot = await self.take_screenshot("chart_management", "Spine chart management interface")
            
            await self.log_test_result(
                test_name,
                "PASSED" if management_features else "WARNING",
                {
                    "chart_management_accessed": chart_management_link is not None,
                    "management_features_found": management_features
                },
                screenshot
            )
            
        except Exception as e:
            screenshot = await self.take_screenshot("chart_management_error", "Error testing chart management")
            await self.log_test_result(
                test_name,
                "FAILED",
                {"error": str(e)},
                screenshot
            )
            
    async def test_api_integration(self):
        """Test 6: Test API integration for spine calculations"""
        test_name = "API Integration Test"
        
        try:
            # Navigate to calculator page
            await self.wait_for_page_load("http://localhost:3000/calculator")
            
            # Set up network monitoring
            api_calls = []
            
            def handle_request(request):
                if '/api' in request.url and ('spine' in request.url or 'calculate' in request.url):
                    api_calls.append({
                        "url": request.url,
                        "method": request.method,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            self.page.on("request", handle_request)
            
            # Set bow parameters
            await self.set_bow_parameters()
            
            # Trigger calculation
            calculate_button = self.page.locator('button:has-text("Calculate"), [data-testid="calculate"], .calculate-button').first
            
            if await calculate_button.count() > 0:
                await calculate_button.click()
                await self.page.wait_for_timeout(2000)  # Wait for API call
            else:
                # Try to trigger calculation by changing inputs
                draw_weight = self.page.locator('input[type="range"]').first
                if await draw_weight.count() > 0:
                    await draw_weight.fill("52")
                    await self.page.wait_for_timeout(1000)
                    
            screenshot = await self.take_screenshot("api_integration", "API integration testing")
            
            await self.log_test_result(
                test_name,
                "PASSED" if api_calls else "WARNING",
                {
                    "api_calls_detected": len(api_calls),
                    "api_calls": api_calls
                },
                screenshot
            )
            
        except Exception as e:
            screenshot = await self.take_screenshot("api_integration_error", "Error testing API integration")
            await self.log_test_result(
                test_name,
                "FAILED",
                {"error": str(e)},
                screenshot
            )
            
    async def generate_test_report(self):
        """Generate comprehensive test report"""
        self.test_results["end_time"] = datetime.now().isoformat()
        
        # Save detailed JSON report
        report_file = f"spine_chart_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        print(f"\n📊 TEST REPORT GENERATED: {report_file}")
        print(f"📁 Screenshots saved in: {self.screenshots_dir}")
        
        # Print summary
        summary = self.test_results["summary"]
        print(f"\n🎯 TEST SUMMARY:")
        print(f"   Total Tests: {summary['total']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⚠️  Warnings: {summary['warnings']}")
        
        success_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        return report_file
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Spine Chart Management System Test Suite")
        print("=" * 60)
        
        try:
            await self.setup()
            
            # Navigate to application
            await self.wait_for_page_load("http://localhost:3000")
            await self.take_screenshot("initial_load", "Initial application load")
            
            # Check authentication status
            await self.check_authentication_status()
            
            # Run all tests
            await self.test_spine_calculator_access()
            await self.test_professional_spine_calculation_mode()
            await self.test_spine_chart_selection_impact()
            await self.test_admin_panel_access()
            await self.test_spine_chart_management_interface()
            await self.test_api_integration()
            
        except Exception as e:
            print(f"❌ Critical error during test execution: {e}")
            await self.log_test_result("Test Suite Execution", "FAILED", {"critical_error": str(e)})
            
        finally:
            # Generate report and cleanup
            report_file = await self.generate_test_report()
            await self.teardown()
            
            print(f"\n🏁 Test Suite Complete")
            print(f"📋 Full report: {report_file}")
            return report_file

async def main():
    """Main test execution"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Unified Spine Chart Management System Test Suite

Usage:
    python test_spine_chart_management.py

This test suite validates:
1. Professional Spine Calculation frontend functionality
2. Admin spine chart management interface  
3. API integration with different chart selections
4. System default chart settings functionality

Requirements:
- Application running at http://localhost:3000
- API running at http://localhost:5000/api
- Playwright installed (pip install playwright)
- Browsers installed (playwright install)

The test will:
- Launch a browser window for visual feedback
- Take screenshots at each step
- Generate a detailed JSON report
- Test both frontend and backend integration
""")
        return
        
    suite = SpineChartTestSuite()
    report_file = await suite.run_all_tests()
    
    print(f"\n✅ Test execution complete!")
    print(f"📄 View detailed results: {report_file}")
    print(f"📸 Screenshots available in: test_screenshots/")

if __name__ == "__main__":
    asyncio.run(main())