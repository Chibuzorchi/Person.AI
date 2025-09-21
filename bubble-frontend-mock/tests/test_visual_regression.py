import pytest
from playwright.async_api import async_playwright, Page
import asyncio
from typing import Dict, Any
import os
from pathlib import Path
import hashlib

class VisualRegressionTester:
    def __init__(self, app_url: str, baseline_path: str):
        self.app_url = app_url
        self.baseline_path = Path(baseline_path)
        self.baseline_path.mkdir(parents=True, exist_ok=True)
        self.browser = None
        self.page = None
    
    async def setup_browser(self):
        """Setup browser for visual testing"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        
        # Set consistent viewport
        await self.page.set_viewport_size({"width": 1280, "height": 720})
    
    async def teardown_browser(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
    
    async def capture_page_screenshot(self, page_name: str, selector: str = None) -> str:
        """Capture screenshot of page or element"""
        screenshot_path = self.baseline_path / f"{page_name}.png"
        
        if selector:
            element = await self.page.locator(selector)
            await element.screenshot(path=str(screenshot_path))
        else:
            await self.page.screenshot(path=str(screenshot_path))
        
        return str(screenshot_path)
    
    async def compare_screenshots(self, current_path: str, baseline_path: str) -> Dict[str, Any]:
        """Compare current screenshot with baseline"""
        # Simple file comparison using hash
        with open(current_path, 'rb') as f:
            current_hash = hashlib.md5(f.read()).hexdigest()
        
        with open(baseline_path, 'rb') as f:
            baseline_hash = hashlib.md5(f.read()).hexdigest()
        
        return {
            "identical": current_hash == baseline_hash,
            "current_hash": current_hash,
            "baseline_hash": baseline_hash,
            "difference_percentage": 0 if current_hash == baseline_hash else 100
        }
    
    async def test_login_page_visual_regression(self) -> Dict[str, Any]:
        """Test login page visual regression"""
        try:
            await self.page.goto(f"{self.app_url}/index.html")
            await self.page.wait_for_selector('[data-testid="email-input"]', timeout=10000)
            
            # Capture screenshot
            current_screenshot = await self.capture_page_screenshot("login_page")
            baseline_screenshot = self.baseline_path / "login_page_baseline.png"
            
            if baseline_screenshot.exists():
                comparison = await self.compare_screenshots(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": comparison["identical"],
                    "difference_percentage": comparison["difference_percentage"],
                    "current_screenshot": current_screenshot,
                    "baseline_screenshot": str(baseline_screenshot)
                }
            else:
                # First run - save as baseline
                import shutil
                shutil.copy(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": True,
                    "difference_percentage": 0,
                    "baseline_created": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_dashboard_visual_regression(self) -> Dict[str, Any]:
        """Test dashboard visual regression"""
        try:
            # Login first
            await self.page.goto(f"{self.app_url}/index.html")
            await self.page.wait_for_selector('[data-testid="email-input"]', timeout=10000)
            await self.page.fill('[data-testid="email-input"]', "test@personai.com")
            await self.page.fill('[data-testid="password-input"]', "test_password")
            await self.page.click('[data-testid="login-button"]')
            await self.page.wait_for_selector('[data-testid="dashboard"]', timeout=15000)
            
            # Capture screenshot
            current_screenshot = await self.capture_page_screenshot("dashboard")
            baseline_screenshot = self.baseline_path / "dashboard_baseline.png"
            
            if baseline_screenshot.exists():
                comparison = await self.compare_screenshots(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": comparison["identical"],
                    "difference_percentage": comparison["difference_percentage"],
                    "current_screenshot": current_screenshot,
                    "baseline_screenshot": str(baseline_screenshot)
                }
            else:
                # First run - save as baseline
                import shutil
                shutil.copy(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": True,
                    "difference_percentage": 0,
                    "baseline_created": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_briefing_form_visual_regression(self) -> Dict[str, Any]:
        """Test briefing form visual regression"""
        try:
            # Login first
            await self.page.goto(f"{self.app_url}/index.html")
            await self.page.wait_for_selector('[data-testid="email-input"]', timeout=10000)
            await self.page.fill('[data-testid="email-input"]', "test@personai.com")
            await self.page.fill('[data-testid="password-input"]', "test_password")
            await self.page.click('[data-testid="login-button"]')
            await self.page.wait_for_selector('[data-testid="dashboard"]', timeout=15000)
            
            # Navigate to briefing form
            await self.page.goto(f"{self.app_url}/index.html#schedule-briefing")
            await self.page.wait_for_selector('[data-testid="schedule-form"]', timeout=10000)
            
            # Capture form screenshot
            current_screenshot = await self.capture_page_screenshot("briefing_form", '[data-testid="schedule-form"]')
            baseline_screenshot = self.baseline_path / "briefing_form_baseline.png"
            
            if baseline_screenshot.exists():
                comparison = await self.compare_screenshots(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": comparison["identical"],
                    "difference_percentage": comparison["difference_percentage"]
                }
            else:
                # First run - save as baseline
                import shutil
                shutil.copy(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": True,
                    "difference_percentage": 0,
                    "baseline_created": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_integrations_page_visual_regression(self) -> Dict[str, Any]:
        """Test integrations page visual regression"""
        try:
            # Login first
            await self.page.goto(f"{self.app_url}/index.html")
            await self.page.wait_for_selector('[data-testid="email-input"]', timeout=10000)
            await self.page.fill('[data-testid="email-input"]', "test@personai.com")
            await self.page.fill('[data-testid="password-input"]', "test_password")
            await self.page.click('[data-testid="login-button"]')
            await self.page.wait_for_selector('[data-testid="dashboard"]', timeout=15000)
            
            # Navigate to integrations
            await self.page.goto(f"{self.app_url}/index.html#integrations")
            await self.page.wait_for_selector('[data-testid="integrations-list"]', timeout=10000)
            
            # Capture screenshot
            current_screenshot = await self.capture_page_screenshot("integrations_page")
            baseline_screenshot = self.baseline_path / "integrations_page_baseline.png"
            
            if baseline_screenshot.exists():
                comparison = await self.compare_screenshots(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": comparison["identical"],
                    "difference_percentage": comparison["difference_percentage"]
                }
            else:
                # First run - save as baseline
                import shutil
                shutil.copy(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": True,
                    "difference_percentage": 0,
                    "baseline_created": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_settings_page_visual_regression(self) -> Dict[str, Any]:
        """Test settings page visual regression"""
        try:
            # Login first
            await self.page.goto(f"{self.app_url}/index.html")
            await self.page.wait_for_selector('[data-testid="email-input"]', timeout=10000)
            await self.page.fill('[data-testid="email-input"]', "test@personai.com")
            await self.page.fill('[data-testid="password-input"]', "test_password")
            await self.page.click('[data-testid="login-button"]')
            await self.page.wait_for_selector('[data-testid="dashboard"]', timeout=15000)
            
            # Navigate to settings
            await self.page.goto(f"{self.app_url}/index.html#settings")
            await self.page.wait_for_selector('[data-testid="preferences-form"]', timeout=10000)
            
            # Capture screenshot
            current_screenshot = await self.capture_page_screenshot("settings_page")
            baseline_screenshot = self.baseline_path / "settings_page_baseline.png"
            
            if baseline_screenshot.exists():
                comparison = await self.compare_screenshots(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": comparison["identical"],
                    "difference_percentage": comparison["difference_percentage"]
                }
            else:
                # First run - save as baseline
                import shutil
                shutil.copy(current_screenshot, str(baseline_screenshot))
                return {
                    "success": True,
                    "identical": True,
                    "difference_percentage": 0,
                    "baseline_created": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class TestVisualRegression:
    @pytest.fixture
    def visual_tester(self):
        return VisualRegressionTester(
            app_url="http://localhost:8081",
            baseline_path="./visual_baselines"
        )
    
    @pytest.mark.asyncio
    async def test_login_page_visual_regression(self, visual_tester):
        """Test login page visual regression"""
        await visual_tester.setup_browser()
        try:
            result = await visual_tester.test_login_page_visual_regression()
            assert result["success"], f"Login page visual test failed: {result.get('error')}"
            
            if not result.get("baseline_created", False):
                assert result["identical"], f"Login page visual regression detected: {result['difference_percentage']}% difference"
        finally:
            await visual_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_dashboard_visual_regression(self, visual_tester):
        """Test dashboard visual regression"""
        await visual_tester.setup_browser()
        try:
            result = await visual_tester.test_dashboard_visual_regression()
            assert result["success"], f"Dashboard visual test failed: {result.get('error')}"
            
            if not result.get("baseline_created", False):
                assert result["identical"], f"Dashboard visual regression detected: {result['difference_percentage']}% difference"
        finally:
            await visual_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_briefing_form_visual_regression(self, visual_tester):
        """Test briefing form visual regression"""
        await visual_tester.setup_browser()
        try:
            result = await visual_tester.test_briefing_form_visual_regression()
            assert result["success"], f"Briefing form visual test failed: {result.get('error')}"
            
            if not result.get("baseline_created", False):
                assert result["identical"], f"Briefing form visual regression detected: {result['difference_percentage']}% difference"
        finally:
            await visual_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_integrations_page_visual_regression(self, visual_tester):
        """Test integrations page visual regression"""
        await visual_tester.setup_browser()
        try:
            result = await visual_tester.test_integrations_page_visual_regression()
            assert result["success"], f"Integrations page visual test failed: {result.get('error')}"
            
            if not result.get("baseline_created", False):
                assert result["identical"], f"Integrations page visual regression detected: {result['difference_percentage']}% difference"
        finally:
            await visual_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_settings_page_visual_regression(self, visual_tester):
        """Test settings page visual regression"""
        await visual_tester.setup_browser()
        try:
            result = await visual_tester.test_settings_page_visual_regression()
            assert result["success"], f"Settings page visual test failed: {result.get('error')}"
            
            if not result.get("baseline_created", False):
                assert result["identical"], f"Settings page visual regression detected: {result['difference_percentage']}% difference"
        finally:
            await visual_tester.teardown_browser()
