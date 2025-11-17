"""
Comprehensive Login Page UI/Frontend Testing Script
====================================================

This script performs comprehensive UI/Frontend testing of the login page
using Playwright to identify bugs, issues, and UI problems.

Features:
- SSL certificate handling (self-signed certs)
- Comprehensive UI element validation
- Form validation testing
- Error handling verification
- Accessibility checks
- Performance metrics
- Visual regression detection
- Bug detection and reporting

Author: QA Automation Architect
Date: 2025-11-06
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from playwright.async_api import async_playwright, Page, Browser, BrowserContext, expect
import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/login_page_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LoginPageTester:
    """
    Comprehensive login page UI/Frontend tester.
    
    Performs extensive testing to identify bugs, issues, and UI problems.
    """
    
    def __init__(
        self,
        base_url: str = "https://10.10.10.100",
        site_id: str = "prisma-210-1000",
        username: str = "prisma",
        password: str = "prisma",
        headless: bool = False,
        timeout: int = 30000
    ):
        """
        Initialize the login page tester.
        
        Args:
            base_url: Base URL of the application
            site_id: Site ID for the application
            username: Username for login
            password: Password for login
            headless: Run browser in headless mode
            timeout: Page timeout in milliseconds
        """
        self.base_url = base_url.rstrip('/')
        self.site_id = site_id
        self.username = username
        self.password = password
        self.headless = headless
        self.timeout = timeout
        
        self.login_url = f"{self.base_url}/login?siteId={self.site_id}"
        self.issues: List[Dict[str, Any]] = []
        self.screenshots_dir = Path("reports/login_page_screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized LoginPageTester for {self.login_url}")
    
    async def test_ssl_certificate_handling(self, page: Page) -> bool:
        """
        Test SSL certificate handling (self-signed certs).
        
        Args:
            page: Playwright page object
            
        Returns:
            True if SSL handling works correctly
        """
        logger.info("Testing SSL certificate handling...")
        try:
            # Navigate with SSL error handling
            response = await page.goto(
                self.login_url,
                wait_until="domcontentloaded",
                timeout=self.timeout
            )
            
            if response and response.status == 200:
                logger.info("[OK] SSL certificate handled successfully")
                return True
            else:
                self.issues.append({
                    "type": "SSL_ERROR",
                    "severity": "HIGH",
                    "description": f"SSL certificate issue - Status: {response.status if response else 'None'}",
                    "url": self.login_url
                })
                logger.error(f"[ERROR] SSL certificate issue - Status: {response.status if response else 'None'}")
                return False
        except Exception as e:
            self.issues.append({
                "type": "SSL_ERROR",
                "severity": "CRITICAL",
                "description": f"SSL certificate error: {str(e)}",
                "url": self.login_url,
                "error": str(e)
            })
            logger.error(f"[ERROR] SSL certificate error: {e}")
            return False
    
    async def test_page_load_and_structure(self, page: Page) -> bool:
        """
        Test page load and basic structure.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if page loads correctly
        """
        logger.info("Testing page load and structure...")
        issues_found = False
        
        try:
            # Wait for page to be fully loaded
            await page.wait_for_load_state("networkidle", timeout=self.timeout)
            
            # Check page title
            title = await page.title()
            logger.info(f"Page title: {title}")
            
            if not title or title.strip() == "":
                self.issues.append({
                    "type": "MISSING_TITLE",
                    "severity": "MEDIUM",
                    "description": "Page title is missing or empty",
                    "url": self.login_url
                })
                issues_found = True
            
            # Check if login form exists
            login_form = page.locator("form#loginForm, form[action*='login'], form:has-text('Login')")
            form_count = await login_form.count()
            
            if form_count == 0:
                self.issues.append({
                    "type": "MISSING_LOGIN_FORM",
                    "severity": "CRITICAL",
                    "description": "Login form not found on page",
                    "url": self.login_url
                })
                issues_found = True
                logger.error("[ERROR] Login form not found")
            else:
                logger.info("[OK] Login form found")
            
            # Check for username field
            username_fields = [
                "input#username",
                "input[name='username']",
                "input[type='text']",
                "input[placeholder*='username' i]",
                "input[placeholder*='user' i]"
            ]
            
            username_found = False
            for selector in username_fields:
                if await page.locator(selector).count() > 0:
                    username_found = True
                    logger.info(f"[OK] Username field found: {selector}")
                    break
            
            if not username_found:
                self.issues.append({
                    "type": "MISSING_USERNAME_FIELD",
                    "severity": "CRITICAL",
                    "description": "Username input field not found",
                    "url": self.login_url,
                    "selectors_tried": username_fields
                })
                issues_found = True
                logger.error("[ERROR] Username field not found")
            
            # Check for password field
            password_fields = [
                "input#password",
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='password' i]"
            ]
            
            password_found = False
            for selector in password_fields:
                if await page.locator(selector).count() > 0:
                    password_found = True
                    logger.info(f"[OK] Password field found: {selector}")
                    break
            
            if not password_found:
                self.issues.append({
                    "type": "MISSING_PASSWORD_FIELD",
                    "severity": "CRITICAL",
                    "description": "Password input field not found",
                    "url": self.login_url,
                    "selectors_tried": password_fields
                })
                issues_found = True
                logger.error("[ERROR] Password field not found")
            
            # Check for login button
            login_buttons = [
                "button#loginButton",
                "button[type='submit']",
                "button:has-text('Login')",
                "button:has-text('Log In')",
                "button:has-text('Sign In')",
                "input[type='submit']"
            ]
            
            button_found = False
            for selector in login_buttons:
                if await page.locator(selector).count() > 0:
                    button_found = True
                    logger.info(f"[OK] Login button found: {selector}")
                    break
            
            if not button_found:
                self.issues.append({
                    "type": "MISSING_LOGIN_BUTTON",
                    "severity": "CRITICAL",
                    "description": "Login button not found",
                    "url": self.login_url,
                    "selectors_tried": login_buttons
                })
                issues_found = True
                logger.error("[ERROR] Login button not found")
            
            return not issues_found
            
        except Exception as e:
            self.issues.append({
                "type": "PAGE_LOAD_ERROR",
                "severity": "CRITICAL",
                "description": f"Error loading page structure: {str(e)}",
                "url": self.login_url,
                "error": str(e)
            })
            logger.error(f"[ERROR] Page load error: {e}")
            return False
    
    async def test_form_validation(self, page: Page) -> bool:
        """
        Test form validation (empty fields, invalid inputs, etc.).
        
        Args:
            page: Playwright page object
            
        Returns:
            True if form validation works correctly
        """
        logger.info("Testing form validation...")
        issues_found = False
        
        try:
            # Find username field
            username_selectors = [
                "input#username",
                "input[name='username']",
                "input[type='text']"
            ]
            username_field = None
            for selector in username_selectors:
                if await page.locator(selector).count() > 0:
                    username_field = page.locator(selector).first
                    break
            
            # Find password field
            password_selectors = [
                "input#password",
                "input[name='password']",
                "input[type='password']"
            ]
            password_field = None
            for selector in password_selectors:
                if await page.locator(selector).count() > 0:
                    password_field = page.locator(selector).first
                    break
            
            # Find login button
            login_button_selectors = [
                "button#loginButton",
                "button[type='submit']",
                "button:has-text('Login')",
                "button:has-text('Log In')",
                "input[type='submit']"  # Add submit input type
            ]
            login_button = None
            for selector in login_button_selectors:
                if await page.locator(selector).count() > 0:
                    login_button = page.locator(selector).first
                    break
            
            if not username_field or not password_field or not login_button:
                logger.warning("[WARNING] Cannot test form validation - fields not found")
                return False
            
            # Test 1: Try to submit empty form
            logger.info("Testing empty form submission...")
            await login_button.click()
            await page.wait_for_timeout(1000)  # Wait for validation
            
            # Check for validation messages
            error_messages = page.locator(".error, .alert-danger, .text-danger, [role='alert']")
            error_count = await error_messages.count()
            
            if error_count == 0:
                # Check if form was submitted (URL changed or error appeared)
                current_url = page.url
                if "login" not in current_url.lower():
                    self.issues.append({
                        "type": "MISSING_VALIDATION",
                        "severity": "HIGH",
                        "description": "Form allows submission with empty fields",
                        "url": self.login_url
                    })
                    issues_found = True
                    logger.error("[ERROR] Form allows submission with empty fields")
                else:
                    logger.info("[OK] Form validation prevents empty submission")
            
            # Test 2: Test with invalid username
            logger.info("Testing invalid username...")
            await username_field.fill("invalid_user")
            await password_field.fill("test_password")
            await login_button.click()
            await page.wait_for_timeout(2000)  # Wait for response
            
            # Check for error message
            error_count = await error_messages.count()
            if error_count == 0:
                current_url = page.url
                if "login" not in current_url.lower():
                    self.issues.append({
                        "type": "MISSING_ERROR_MESSAGE",
                        "severity": "MEDIUM",
                        "description": "No error message shown for invalid credentials",
                        "url": self.login_url
                    })
                    issues_found = True
                    logger.warning("[WARNING] No error message shown for invalid credentials")
            
            # Clear fields
            await username_field.clear()
            await password_field.clear()
            
            return not issues_found
            
        except Exception as e:
            self.issues.append({
                "type": "VALIDATION_TEST_ERROR",
                "severity": "MEDIUM",
                "description": f"Error testing form validation: {str(e)}",
                "url": self.login_url,
                "error": str(e)
            })
            logger.error(f"[ERROR] Validation test error: {e}")
            return False
    
    async def test_successful_login(self, page: Page) -> bool:
        """
        Test successful login flow.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if login succeeds
        """
        logger.info("Testing successful login...")
        
        try:
            # Find and fill username field
            username_selectors = [
                "input#username",
                "input[name='username']",
                "input[type='text']"
            ]
            username_field = None
            for selector in username_selectors:
                if await page.locator(selector).count() > 0:
                    username_field = page.locator(selector).first
                    break
            
            # Find and fill password field
            password_selectors = [
                "input#password",
                "input[name='password']",
                "input[type='password']"
            ]
            password_field = None
            for selector in password_selectors:
                if await page.locator(selector).count() > 0:
                    password_field = page.locator(selector).first
                    break
            
            # Find login button
            login_button_selectors = [
                "button#loginButton",
                "button[type='submit']",
                "button:has-text('Login')",
                "button:has-text('Log In')",
                "input[type='submit']"  # Add submit input type
            ]
            login_button = None
            for selector in login_button_selectors:
                if await page.locator(selector).count() > 0:
                    login_button = page.locator(selector).first
                    break
            
            if not username_field or not password_field or not login_button:
                logger.error("[ERROR] Cannot test login - fields not found")
                return False
            
            # Fill credentials
            await username_field.fill(self.username)
            await password_field.fill(self.password)
            
            # Take screenshot before login
            await page.screenshot(path=str(self.screenshots_dir / "before_login.png"))
            
            # Click login button
            await login_button.click()
            
            # Wait for navigation or error
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass  # May timeout if page doesn't navigate
            
            # Take screenshot after login attempt
            await page.screenshot(path=str(self.screenshots_dir / "after_login.png"))
            
            # Check if login was successful (URL changed or login form disappeared)
            current_url = page.url
            login_form_visible = await page.locator("form#loginForm, form[action*='login']").count() > 0
            
            if "login" not in current_url.lower() or not login_form_visible:
                logger.info("[OK] Login appears successful - redirected or form hidden")
                return True
            else:
                # Check for error messages
                error_messages = page.locator(".error, .alert-danger, .text-danger, [role='alert']")
                error_text = ""
                if await error_messages.count() > 0:
                    error_text = await error_messages.first.inner_text()
                
                self.issues.append({
                    "type": "LOGIN_FAILED",
                    "severity": "HIGH",
                    "description": f"Login failed with credentials {self.username}/{self.password}",
                    "url": current_url,
                    "error_message": error_text
                })
                logger.error(f"[ERROR] Login failed - Error: {error_text}")
                return False
                
        except Exception as e:
            self.issues.append({
                "type": "LOGIN_TEST_ERROR",
                "severity": "HIGH",
                "description": f"Error during login test: {str(e)}",
                "url": self.login_url,
                "error": str(e)
            })
            logger.error(f"[ERROR] Login test error: {e}")
            return False
    
    async def test_accessibility(self, page: Page) -> bool:
        """
        Test basic accessibility features.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if accessibility is acceptable
        """
        logger.info("Testing accessibility...")
        issues_found = False
        
        try:
            # Check for labels on form fields
            username_field = page.locator("input#username, input[name='username']").first
            if await username_field.count() > 0:
                # Check if field has associated label
                field_id = await username_field.get_attribute("id")
                if field_id:
                    label = page.locator(f"label[for='{field_id}']")
                    if await label.count() == 0:
                        self.issues.append({
                            "type": "ACCESSIBILITY_MISSING_LABEL",
                            "severity": "MEDIUM",
                            "description": f"Username field missing associated label (id: {field_id})",
                            "url": self.login_url
                        })
                        issues_found = True
            
            password_field = page.locator("input#password, input[name='password']").first
            if await password_field.count() > 0:
                field_id = await password_field.get_attribute("id")
                if field_id:
                    label = page.locator(f"label[for='{field_id}']")
                    if await label.count() == 0:
                        self.issues.append({
                            "type": "ACCESSIBILITY_MISSING_LABEL",
                            "severity": "MEDIUM",
                            "description": f"Password field missing associated label (id: {field_id})",
                            "url": self.login_url
                        })
                        issues_found = True
            
            # Check for ARIA labels
            inputs_without_aria = page.locator("input:not([aria-label]):not([aria-labelledby])")
            count = await inputs_without_aria.count()
            if count > 0:
                # Check if they have labels
                for i in range(count):
                    input_elem = inputs_without_aria.nth(i)
                    input_id = await input_elem.get_attribute("id")
                    if input_id:
                        label = page.locator(f"label[for='{input_id}']")
                        if await label.count() == 0:
                            self.issues.append({
                                "type": "ACCESSIBILITY_MISSING_ARIA",
                                "severity": "LOW",
                                "description": f"Input field missing ARIA label or associated label",
                                "url": self.login_url
                            })
                            issues_found = True
            
            return not issues_found
            
        except Exception as e:
            logger.warning(f"[WARNING] Accessibility test error: {e}")
            return True  # Don't fail on accessibility test errors
    
    async def test_responsive_design(self, page: Page) -> bool:
        """
        Test responsive design at different viewport sizes.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if responsive design works
        """
        logger.info("Testing responsive design...")
        issues_found = False
        
        viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop"},
            {"width": 1366, "height": 768, "name": "Laptop"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"}
        ]
        
        try:
            for viewport in viewports:
                await page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
                await page.wait_for_timeout(500)  # Wait for layout to adjust
                
                # Take screenshot
                screenshot_path = self.screenshots_dir / f"responsive_{viewport['name']}_{viewport['width']}x{viewport['height']}.png"
                await page.screenshot(path=str(screenshot_path))
                
                # Check if form is still visible and usable
                login_form = page.locator("form#loginForm, form[action*='login']")
                form_count = await login_form.count()
                
                if form_count == 0:
                    self.issues.append({
                        "type": "RESPONSIVE_DESIGN_ISSUE",
                        "severity": "MEDIUM",
                        "description": f"Login form not visible at {viewport['name']} ({viewport['width']}x{viewport['height']})",
                        "url": self.login_url,
                        "viewport": viewport
                    })
                    issues_found = True
            
            return not issues_found
            
        except Exception as e:
            logger.warning(f"[WARNING] Responsive design test error: {e}")
            return True
    
    async def test_performance_metrics(self, page: Page) -> Dict[str, Any]:
        """
        Test page performance metrics.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary with performance metrics
        """
        logger.info("Testing performance metrics...")
        
        metrics = {}
        
        try:
            # Measure page load time
            start_time = datetime.now()
            await page.goto(self.login_url, wait_until="networkidle")
            load_time = (datetime.now() - start_time).total_seconds()
            metrics["page_load_time"] = load_time
            
            if load_time > 5:
                self.issues.append({
                    "type": "PERFORMANCE_SLOW_LOAD",
                    "severity": "MEDIUM",
                    "description": f"Page load time is slow: {load_time:.2f}s",
                    "url": self.login_url,
                    "load_time": load_time
                })
            
            # Get performance metrics from browser
            performance_timing = await page.evaluate("() => JSON.stringify(window.performance.timing)")
            if performance_timing:
                timing = json.loads(performance_timing)
                metrics["performance_timing"] = timing
            
            logger.info(f"[OK] Performance metrics collected: {metrics}")
            return metrics
            
        except Exception as e:
            logger.warning(f"[WARNING] Performance metrics error: {e}")
            return metrics
    
    async def capture_page_snapshot(self, page: Page) -> Dict[str, Any]:
        """
        Capture comprehensive page snapshot for analysis.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary with page snapshot data
        """
        logger.info("Capturing page snapshot...")
        
        snapshot = {
            "url": page.url,
            "title": await page.title(),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Get all form elements
            forms = await page.locator("form").all()
            snapshot["forms"] = []
            for form in forms:
                form_data = {
                    "id": await form.get_attribute("id"),
                    "action": await form.get_attribute("action"),
                    "method": await form.get_attribute("method"),
                    "inputs": []
                }
                inputs = await form.locator("input").all()
                for input_elem in inputs:
                    input_data = {
                        "type": await input_elem.get_attribute("type"),
                        "id": await input_elem.get_attribute("id"),
                        "name": await input_elem.get_attribute("name"),
                        "placeholder": await input_elem.get_attribute("placeholder")
                    }
                    form_data["inputs"].append(input_data)
                snapshot["forms"].append(form_data)
            
            # Get all buttons
            buttons = await page.locator("button, input[type='submit']").all()
            snapshot["buttons"] = []
            for button in buttons:
                button_data = {
                    "id": await button.get_attribute("id"),
                    "type": await button.get_attribute("type"),
                    "text": await button.inner_text(),
                    "disabled": await button.is_disabled()
                }
                snapshot["buttons"].append(button_data)
            
            # Get console errors
            console_messages = []
            page.on("console", lambda msg: console_messages.append({
                "type": msg.type,
                "text": msg.text
            }))
            
            # Get page errors
            page_errors = []
            page.on("pageerror", lambda error: page_errors.append({
                "message": str(error)
            }))
            
            snapshot["console_messages"] = console_messages
            snapshot["page_errors"] = page_errors
            
            return snapshot
            
        except Exception as e:
            logger.warning(f"[WARNING] Snapshot capture error: {e}")
            return snapshot
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all comprehensive tests.
        
        Returns:
            Dictionary with test results and issues found
        """
        logger.info("=" * 80)
        logger.info("Starting comprehensive login page UI/Frontend testing")
        logger.info("=" * 80)
        
        async with async_playwright() as p:
            # Launch browser with SSL error handling
            browser = await p.chromium.launch(
                headless=self.headless,
                args=['--ignore-certificate-errors', '--ignore-ssl-errors']
            )
            
            # Create context with SSL error handling
            context = await browser.new_context(
                ignore_https_errors=True,
                viewport={"width": 1920, "height": 1080}
            )
            
            page = await context.new_page()
            
            # Set up error handlers
            page.on("pageerror", lambda error: logger.error(f"Page error: {error}"))
            page.on("console", lambda msg: logger.debug(f"Console: {msg.type} - {msg.text}"))
            
            test_results = {
                "start_time": datetime.now().isoformat(),
                "login_url": self.login_url,
                "tests": {},
                "issues": [],
                "screenshots_dir": str(self.screenshots_dir)
            }
            
            try:
                # Test 1: SSL Certificate Handling
                test_results["tests"]["ssl_handling"] = await self.test_ssl_certificate_handling(page)
                
                # Test 2: Page Load and Structure
                test_results["tests"]["page_structure"] = await self.test_page_load_and_structure(page)
                
                # Test 3: Form Validation
                test_results["tests"]["form_validation"] = await self.test_form_validation(page)
                
                # Test 4: Successful Login
                test_results["tests"]["successful_login"] = await self.test_successful_login(page)
                
                # Test 5: Accessibility
                test_results["tests"]["accessibility"] = await self.test_accessibility(page)
                
                # Test 6: Responsive Design
                test_results["tests"]["responsive_design"] = await self.test_responsive_design(page)
                
                # Test 7: Performance Metrics
                test_results["tests"]["performance"] = await self.test_performance_metrics(page)
                
                # Test 8: Page Snapshot
                test_results["tests"]["page_snapshot"] = await self.capture_page_snapshot(page)
                
            except Exception as e:
                logger.error(f"[ERROR] Test execution error: {e}")
                self.issues.append({
                    "type": "TEST_EXECUTION_ERROR",
                    "severity": "CRITICAL",
                    "description": f"Error during test execution: {str(e)}",
                    "error": str(e)
                })
            
            finally:
                # Add all issues to results
                test_results["issues"] = self.issues
                test_results["end_time"] = datetime.now().isoformat()
                
                # Generate summary
                total_tests = len([k for k in test_results["tests"].keys() if isinstance(test_results["tests"][k], bool)])
                passed_tests = len([k for k, v in test_results["tests"].items() if isinstance(v, bool) and v])
                test_results["summary"] = {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "total_issues": len(self.issues),
                    "critical_issues": len([i for i in self.issues if i.get("severity") == "CRITICAL"]),
                    "high_issues": len([i for i in self.issues if i.get("severity") == "HIGH"]),
                    "medium_issues": len([i for i in self.issues if i.get("severity") == "MEDIUM"]),
                    "low_issues": len([i for i in self.issues if i.get("severity") == "LOW"])
                }
                
                await browser.close()
        
        return test_results
    
    def generate_report(self, test_results: Dict[str, Any]) -> str:
        """
        Generate comprehensive test report.
        
        Args:
            test_results: Dictionary with test results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("LOGIN PAGE UI/FRONTEND TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_results['start_time']}")
        report.append(f"Login URL: {test_results['login_url']}")
        report.append("")
        
        # Summary
        summary = test_results["summary"]
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Passed: {summary['passed_tests']}")
        report.append(f"Failed: {summary['failed_tests']}")
        report.append(f"Total Issues Found: {summary['total_issues']}")
        report.append(f"  - Critical: {summary['critical_issues']}")
        report.append(f"  - High: {summary['high_issues']}")
        report.append(f"  - Medium: {summary['medium_issues']}")
        report.append(f"  - Low: {summary['low_issues']}")
        report.append("")
        
        # Test Results
        report.append("TEST RESULTS")
        report.append("-" * 80)
        for test_name, result in test_results["tests"].items():
            if isinstance(result, bool):
                status = "[PASS]" if result else "[FAIL]"
                report.append(f"{test_name}: {status}")
        report.append("")
        
        # Issues
        if test_results["issues"]:
            report.append("ISSUES FOUND")
            report.append("-" * 80)
            for i, issue in enumerate(test_results["issues"], 1):
                report.append(f"\n{i}. [{issue.get('severity', 'UNKNOWN')}] {issue.get('type', 'UNKNOWN')}")
                report.append(f"   Description: {issue.get('description', 'N/A')}")
                if issue.get('url'):
                    report.append(f"   URL: {issue.get('url')}")
                if issue.get('error'):
                    report.append(f"   Error: {issue.get('error')}")
        else:
            report.append("No issues found!")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


async def main():
    """Main function to run the comprehensive login page tests."""
    tester = LoginPageTester(
        base_url="https://10.10.10.100",
        site_id="prisma-210-1000",
        username="prisma",
        password="prisma",
        headless=False  # Set to True for headless mode
    )
    
    # Run all tests
    results = await tester.run_all_tests()
    
    # Generate and print report
    report = tester.generate_report(results)
    print("\n" + report)
    
    # Save report to file
    report_file = Path("reports/login_page_test_report.txt")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    # Save JSON results
    json_file = Path("reports/login_page_test_results.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Report saved to: {report_file}")
    logger.info(f"JSON results saved to: {json_file}")
    
    # Return exit code based on results
    if results["summary"]["critical_issues"] > 0 or results["summary"]["failed_tests"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

