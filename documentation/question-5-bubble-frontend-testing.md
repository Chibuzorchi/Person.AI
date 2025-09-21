# Question 5: Bubble Frontend Testing Strategy

## Question
"Our front-end is built in Bubble. How would you structure automated tests for workflows (e.g., scheduling a briefing, toggling preferences) given that Bubble doesn't expose a traditional codebase? What tools or approaches would you use?"

## Comprehensive Answer

### Architecture Overview
I would design a multi-layered testing strategy that works around Bubble's no-code limitations by focusing on API-level testing, browser automation, and visual regression testing to ensure Person.ai's frontend workflows function correctly.

### Testing Strategy Framework

#### 1. **Multi-Layer Testing Approach**
```python
# bubble_testing_framework.py
import pytest
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from playwright.async_api import async_playwright, Page, Browser
import asyncio

class TestLayer(Enum):
    API_LEVEL = "api_level"
    BROWSER_AUTOMATION = "browser_automation"
    VISUAL_REGRESSION = "visual_regression"
    INTEGRATION = "integration"

@dataclass
class BubbleTestConfig:
    bubble_app_url: str
    api_base_url: str
    test_user_credentials: Dict[str, str]
    test_data: Dict[str, Any]
    visual_baselines_path: str

class BubbleTestingFramework:
    def __init__(self, config: BubbleTestConfig):
        self.config = config
        self.session = requests.Session()
        self.browser = None
        self.page = None
        self.test_results = []
    
    async def setup_browser(self):
        """Setup Playwright browser for UI testing"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        # Set viewport for consistent testing
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
    
    async def teardown_browser(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
```

### API-Level Testing

#### 1. **Bubble API Connector Testing**
```python
# bubble_api_tests.py
import pytest
import requests
from typing import Dict, Any
import json

class BubbleAPITester:
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def test_user_authentication(self) -> Dict[str, Any]:
        """Test user authentication via Bubble API"""
        try:
            response = self.session.post(f"{self.api_base_url}/api/user/login", json={
                "email": "test@personai.com",
                "password": "test_password"
            })
            
            if response.status_code == 200:
                auth_data = response.json()
                return {
                    "success": True,
                    "user_id": auth_data.get("user_id"),
                    "session_token": auth_data.get("session_token"),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }
    
    def test_briefing_scheduling(self, user_id: str, session_token: str) -> Dict[str, Any]:
        """Test briefing scheduling workflow"""
        try:
            # Set session token
            self.session.headers.update({'X-Session-Token': session_token})
            
            # Create briefing schedule
            schedule_data = {
                "user_id": user_id,
                "title": "Daily Morning Brief",
                "time": "09:00",
                "frequency": "daily",
                "channels": ["slack", "email"],
                "enabled": True
            }
            
            response = self.session.post(f"{self.api_base_url}/api/briefings/schedule", json=schedule_data)
            
            if response.status_code in [200, 201]:
                briefing_data = response.json()
                return {
                    "success": True,
                    "briefing_id": briefing_data.get("briefing_id"),
                    "schedule_id": briefing_data.get("schedule_id"),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }
    
    def test_preferences_toggle(self, user_id: str, session_token: str) -> Dict[str, Any]:
        """Test user preferences toggle workflow"""
        try:
            self.session.headers.update({'X-Session-Token': session_token})
            
            # Get current preferences
            get_response = self.session.get(f"{self.api_base_url}/api/user/{user_id}/preferences")
            
            if get_response.status_code == 200:
                preferences = get_response.json()
                
                # Toggle a preference
                new_preferences = preferences.copy()
                new_preferences["slack_notifications"] = not preferences.get("slack_notifications", False)
                new_preferences["email_notifications"] = not preferences.get("email_notifications", False)
                
                # Update preferences
                update_response = self.session.put(
                    f"{self.api_base_url}/api/user/{user_id}/preferences",
                    json=new_preferences
                )
                
                if update_response.status_code == 200:
                    return {
                        "success": True,
                        "updated_preferences": update_response.json(),
                        "response_time": update_response.elapsed.total_seconds()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Update failed: HTTP {update_response.status_code}",
                        "response_time": update_response.elapsed.total_seconds()
                    }
            else:
                return {
                    "success": False,
                    "error": f"Get preferences failed: HTTP {get_response.status_code}",
                    "response_time": get_response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }
    
    def test_integration_connection(self, user_id: str, session_token: str, integration_type: str) -> Dict[str, Any]:
        """Test integration connection workflow"""
        try:
            self.session.headers.update({'X-Session-Token': session_token})
            
            # Test integration connection
            connection_data = {
                "user_id": user_id,
                "integration_type": integration_type,
                "config": {
                    "webhook_url": "https://hooks.slack.com/test",
                    "channel": "#general"
                }
            }
            
            response = self.session.post(f"{self.api_base_url}/api/integrations/connect", json=connection_data)
            
            if response.status_code in [200, 201]:
                integration_data = response.json()
                return {
                    "success": True,
                    "integration_id": integration_data.get("integration_id"),
                    "status": integration_data.get("status"),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }

class TestBubbleAPI:
    @pytest.fixture
    def api_tester(self):
        return BubbleAPITester(
            api_base_url="https://personai.bubbleapps.io/api",
            api_key="test_api_key"
        )
    
    def test_authentication_flow(self, api_tester):
        """Test complete authentication flow"""
        auth_result = api_tester.test_user_authentication()
        
        assert auth_result["success"], f"Authentication failed: {auth_result['error']}"
        assert "user_id" in auth_result
        assert "session_token" in auth_result
        assert auth_result["response_time"] < 5.0, "Authentication too slow"
    
    def test_briefing_scheduling_workflow(self, api_tester):
        """Test briefing scheduling workflow"""
        # First authenticate
        auth_result = api_tester.test_user_authentication()
        assert auth_result["success"], "Authentication required for briefing test"
        
        # Test briefing scheduling
        briefing_result = api_tester.test_briefing_scheduling(
            auth_result["user_id"],
            auth_result["session_token"]
        )
        
        assert briefing_result["success"], f"Briefing scheduling failed: {briefing_result['error']}"
        assert "briefing_id" in briefing_result
        assert briefing_result["response_time"] < 10.0, "Briefing scheduling too slow"
    
    def test_preferences_workflow(self, api_tester):
        """Test preferences toggle workflow"""
        # First authenticate
        auth_result = api_tester.test_user_authentication()
        assert auth_result["success"], "Authentication required for preferences test"
        
        # Test preferences toggle
        preferences_result = api_tester.test_preferences_toggle(
            auth_result["user_id"],
            auth_result["session_token"]
        )
        
        assert preferences_result["success"], f"Preferences toggle failed: {preferences_result['error']}"
        assert "updated_preferences" in preferences_result
        assert preferences_result["response_time"] < 5.0, "Preferences update too slow"
    
    def test_integration_workflow(self, api_tester):
        """Test integration connection workflow"""
        # First authenticate
        auth_result = api_tester.test_user_authentication()
        assert auth_result["success"], "Authentication required for integration test"
        
        # Test Slack integration
        slack_result = api_tester.test_integration_connection(
            auth_result["user_id"],
            auth_result["session_token"],
            "slack"
        )
        
        assert slack_result["success"], f"Slack integration failed: {slack_result['error']}"
        assert "integration_id" in slack_result
        assert slack_result["response_time"] < 15.0, "Integration connection too slow"
```

### Browser Automation Testing

#### 1. **Playwright UI Testing**
```python
# bubble_ui_tests.py
import pytest
from playwright.async_api import async_playwright, Page, Browser
import asyncio
from typing import Dict, Any

class BubbleUITester:
    def __init__(self, app_url: str, test_credentials: Dict[str, str]):
        self.app_url = app_url
        self.test_credentials = test_credentials
        self.browser = None
        self.page = None
    
    async def setup_browser(self):
        """Setup Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        # Set viewport for consistent testing
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Add custom data attributes for reliable element selection
        await self.page.add_init_script("""
            // Add data-testid attributes to Bubble elements
            window.addEventListener('DOMContentLoaded', function() {
                // Add test IDs to common elements
                const elements = document.querySelectorAll('[data-testid]');
                elements.forEach(el => {
                    if (!el.getAttribute('data-testid')) {
                        el.setAttribute('data-testid', el.className.replace(/\\s+/g, '-').toLowerCase());
                    }
                });
            });
        """)
    
    async def teardown_browser(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
    
    async def login(self) -> bool:
        """Login to the application"""
        try:
            await self.page.goto(f"{self.app_url}/login")
            
            # Wait for login form to load
            await self.page.wait_for_selector('[data-testid="email-input"]', timeout=10000)
            
            # Fill login form
            await self.page.fill('[data-testid="email-input"]', self.test_credentials["email"])
            await self.page.fill('[data-testid="password-input"]', self.test_credentials["password"])
            
            # Click login button
            await self.page.click('[data-testid="login-button"]')
            
            # Wait for redirect to dashboard
            await self.page.wait_for_selector('[data-testid="dashboard"]', timeout=15000)
            
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    async def test_briefing_scheduling_ui(self) -> Dict[str, Any]:
        """Test briefing scheduling UI workflow"""
        try:
            # Navigate to briefing schedule page
            await self.page.goto(f"{self.app_url}/briefings/schedule")
            await self.page.wait_for_selector('[data-testid="schedule-form"]', timeout=10000)
            
            # Fill briefing form
            await self.page.fill('[data-testid="briefing-title"]', "Test Daily Brief")
            await self.page.select_option('[data-testid="time-select"]', "09:00")
            await self.page.select_option('[data-testid="frequency-select"]', "daily")
            
            # Select channels
            await self.page.check('[data-testid="slack-channel"]')
            await self.page.check('[data-testid="email-channel"]')
            
            # Submit form
            await self.page.click('[data-testid="save-schedule-button"]')
            
            # Wait for success message
            await self.page.wait_for_selector('[data-testid="success-message"]', timeout=10000)
            
            # Verify briefing was created
            success_message = await self.page.text_content('[data-testid="success-message"]')
            
            return {
                "success": True,
                "message": success_message,
                "screenshot": await self.page.screenshot()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "screenshot": await self.page.screenshot()
            }
    
    async def test_preferences_toggle_ui(self) -> Dict[str, Any]:
        """Test preferences toggle UI workflow"""
        try:
            # Navigate to preferences page
            await self.page.goto(f"{self.app_url}/settings/preferences")
            await self.page.wait_for_selector('[data-testid="preferences-form"]', timeout=10000)
            
            # Get initial state
            slack_toggle = await self.page.locator('[data-testid="slack-notifications-toggle"]')
            initial_slack_state = await slack_toggle.is_checked()
            
            # Toggle Slack notifications
            await slack_toggle.click()
            
            # Wait for state change
            await self.page.wait_for_timeout(1000)
            
            # Verify toggle state changed
            new_slack_state = await slack_toggle.is_checked()
            
            # Save preferences
            await self.page.click('[data-testid="save-preferences-button"]')
            
            # Wait for success message
            await self.page.wait_for_selector('[data-testid="success-message"]', timeout=10000)
            
            return {
                "success": True,
                "initial_state": initial_slack_state,
                "new_state": new_slack_state,
                "state_changed": initial_slack_state != new_slack_state,
                "screenshot": await self.page.screenshot()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "screenshot": await self.page.screenshot()
            }
    
    async def test_integration_setup_ui(self, integration_type: str) -> Dict[str, Any]:
        """Test integration setup UI workflow"""
        try:
            # Navigate to integrations page
            await self.page.goto(f"{self.app_url}/integrations")
            await self.page.wait_for_selector('[data-testid="integrations-list"]', timeout=10000)
            
            # Click on specific integration
            await self.page.click(f'[data-testid="{integration_type}-integration-card"]')
            await self.page.wait_for_selector('[data-testid="integration-setup-form"]', timeout=10000)
            
            # Fill integration form
            if integration_type == "slack":
                await self.page.fill('[data-testid="webhook-url"]', "https://hooks.slack.com/test")
                await self.page.fill('[data-testid="channel-name"]', "#general")
            elif integration_type == "email":
                await self.page.fill('[data-testid="smtp-server"]', "smtp.gmail.com")
                await self.page.fill('[data-testid="smtp-port"]', "587")
                await self.page.fill('[data-testid="email-address"]', "test@personai.com")
            
            # Test connection
            await self.page.click('[data-testid="test-connection-button"]')
            
            # Wait for test result
            await self.page.wait_for_selector('[data-testid="connection-test-result"]', timeout=10000)
            
            # Save integration
            await self.page.click('[data-testid="save-integration-button"]')
            
            # Wait for success message
            await self.page.wait_for_selector('[data-testid="success-message"]', timeout=10000)
            
            return {
                "success": True,
                "integration_type": integration_type,
                "screenshot": await self.page.screenshot()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "screenshot": await self.page.screenshot()
            }

class TestBubbleUI:
    @pytest.fixture
    async def ui_tester(self):
        tester = BubbleUITester(
            app_url="https://personai.bubbleapps.io",
            test_credentials={
                "email": "test@personai.com",
                "password": "test_password"
            }
        )
        await tester.setup_browser()
        yield tester
        await tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_login_workflow(self, ui_tester):
        """Test user login workflow"""
        login_success = await ui_tester.login()
        assert login_success, "Login workflow failed"
    
    @pytest.mark.asyncio
    async def test_briefing_scheduling_workflow(self, ui_tester):
        """Test briefing scheduling UI workflow"""
        # First login
        login_success = await ui_tester.login()
        assert login_success, "Login required for briefing test"
        
        # Test briefing scheduling
        result = await ui_tester.test_briefing_scheduling_ui()
        assert result["success"], f"Briefing scheduling UI failed: {result['error']}"
        assert "Test Daily Brief" in result["message"]
    
    @pytest.mark.asyncio
    async def test_preferences_workflow(self, ui_tester):
        """Test preferences toggle UI workflow"""
        # First login
        login_success = await ui_tester.login()
        assert login_success, "Login required for preferences test"
        
        # Test preferences toggle
        result = await ui_tester.test_preferences_toggle_ui()
        assert result["success"], f"Preferences toggle UI failed: {result['error']}"
        assert result["state_changed"], "Toggle state did not change"
    
    @pytest.mark.asyncio
    async def test_slack_integration_workflow(self, ui_tester):
        """Test Slack integration setup UI workflow"""
        # First login
        login_success = await ui_tester.login()
        assert login_success, "Login required for integration test"
        
        # Test Slack integration
        result = await ui_tester.test_integration_setup_ui("slack")
        assert result["success"], f"Slack integration UI failed: {result['error']}"
        assert result["integration_type"] == "slack"
```

### Visual Regression Testing

#### 1. **Visual Testing Framework**
```python
# visual_regression_tests.py
import pytest
from playwright.async_api import async_playwright, Page
import asyncio
from typing import Dict, Any
import os
from pathlib import Path

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
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
    
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
        # This would use a visual diff library like pixelmatch
        # For now, we'll do a simple file comparison
        import hashlib
        
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
    
    async def test_dashboard_visual_regression(self) -> Dict[str, Any]:
        """Test dashboard visual regression"""
        try:
            await self.page.goto(f"{self.app_url}/dashboard")
            await self.page.wait_for_selector('[data-testid="dashboard"]', timeout=10000)
            
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
            await self.page.goto(f"{self.app_url}/briefings/schedule")
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

class TestVisualRegression:
    @pytest.fixture
    async def visual_tester(self):
        tester = VisualRegressionTester(
            app_url="https://personai.bubbleapps.io",
            baseline_path="./visual_baselines"
        )
        await tester.setup_browser()
        yield tester
        await tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_dashboard_visual_regression(self, visual_tester):
        """Test dashboard visual regression"""
        result = await visual_tester.test_dashboard_visual_regression()
        assert result["success"], f"Dashboard visual test failed: {result.get('error')}"
        
        if not result.get("baseline_created", False):
            assert result["identical"], f"Dashboard visual regression detected: {result['difference_percentage']}% difference"
    
    @pytest.mark.asyncio
    async def test_briefing_form_visual_regression(self, visual_tester):
        """Test briefing form visual regression"""
        result = await visual_tester.test_briefing_form_visual_regression()
        assert result["success"], f"Briefing form visual test failed: {result.get('error')}"
        
        if not result.get("baseline_created", False):
            assert result["identical"], f"Briefing form visual regression detected: {result['difference_percentage']}% difference"
```

### Integration Testing

#### 1. **End-to-End Workflow Testing**
```python
# integration_workflow_tests.py
import pytest
import asyncio
from bubble_testing_framework import BubbleTestingFramework, BubbleTestConfig
from bubble_api_tests import BubbleAPITester
from bubble_ui_tests import BubbleUITester

class IntegrationWorkflowTester:
    def __init__(self, config: BubbleTestConfig):
        self.config = config
        self.api_tester = BubbleAPITester(config.api_base_url, "test_api_key")
        self.ui_tester = BubbleUITester(config.bubble_app_url, config.test_user_credentials)
        self.framework = BubbleTestingFramework(config)
    
    async def test_complete_briefing_workflow(self) -> Dict[str, Any]:
        """Test complete briefing workflow from UI to API"""
        results = {
            "workflow_steps": [],
            "overall_success": True,
            "errors": []
        }
        
        try:
            # Step 1: API Authentication
            auth_result = self.api_tester.test_user_authentication()
            results["workflow_steps"].append({
                "step": "api_authentication",
                "success": auth_result["success"],
                "details": auth_result
            })
            
            if not auth_result["success"]:
                results["overall_success"] = False
                results["errors"].append("API authentication failed")
                return results
            
            # Step 2: UI Login
            await self.ui_tester.setup_browser()
            ui_login_success = await self.ui_tester.login()
            results["workflow_steps"].append({
                "step": "ui_login",
                "success": ui_login_success,
                "details": {"login_success": ui_login_success}
            })
            
            if not ui_login_success:
                results["overall_success"] = False
                results["errors"].append("UI login failed")
                return results
            
            # Step 3: UI Briefing Scheduling
            ui_briefing_result = await self.ui_tester.test_briefing_scheduling_ui()
            results["workflow_steps"].append({
                "step": "ui_briefing_scheduling",
                "success": ui_briefing_result["success"],
                "details": ui_briefing_result
            })
            
            if not ui_briefing_result["success"]:
                results["overall_success"] = False
                results["errors"].append("UI briefing scheduling failed")
                return results
            
            # Step 4: API Briefing Verification
            api_briefing_result = self.api_tester.test_briefing_scheduling(
                auth_result["user_id"],
                auth_result["session_token"]
            )
            results["workflow_steps"].append({
                "step": "api_briefing_verification",
                "success": api_briefing_result["success"],
                "details": api_briefing_result
            })
            
            if not api_briefing_result["success"]:
                results["overall_success"] = False
                results["errors"].append("API briefing verification failed")
                return results
            
            # Step 5: UI Preferences Toggle
            ui_preferences_result = await self.ui_tester.test_preferences_toggle_ui()
            results["workflow_steps"].append({
                "step": "ui_preferences_toggle",
                "success": ui_preferences_result["success"],
                "details": ui_preferences_result
            })
            
            if not ui_preferences_result["success"]:
                results["overall_success"] = False
                results["errors"].append("UI preferences toggle failed")
                return results
            
            # Step 6: API Preferences Verification
            api_preferences_result = self.api_tester.test_preferences_toggle(
                auth_result["user_id"],
                auth_result["session_token"]
            )
            results["workflow_steps"].append({
                "step": "api_preferences_verification",
                "success": api_preferences_result["success"],
                "details": api_preferences_result
            })
            
            if not api_preferences_result["success"]:
                results["overall_success"] = False
                results["errors"].append("API preferences verification failed")
                return results
            
        except Exception as e:
            results["overall_success"] = False
            results["errors"].append(f"Workflow execution error: {str(e)}")
        
        finally:
            await self.ui_tester.teardown_browser()
        
        return results

class TestIntegrationWorkflows:
    @pytest.fixture
    def test_config(self):
        return BubbleTestConfig(
            bubble_app_url="https://personai.bubbleapps.io",
            api_base_url="https://personai.bubbleapps.io/api",
            test_user_credentials={
                "email": "test@personai.com",
                "password": "test_password"
            },
            test_data={
                "briefing_title": "Test Daily Brief",
                "briefing_time": "09:00",
                "briefing_frequency": "daily"
            },
            visual_baselines_path="./visual_baselines"
        )
    
    @pytest.fixture
    def integration_tester(self, test_config):
        return IntegrationWorkflowTester(test_config)
    
    @pytest.mark.asyncio
    async def test_complete_briefing_workflow(self, integration_tester):
        """Test complete briefing workflow integration"""
        result = await integration_tester.test_complete_briefing_workflow()
        
        assert result["overall_success"], f"Integration workflow failed: {result['errors']}"
        
        # Verify all steps succeeded
        for step in result["workflow_steps"]:
            assert step["success"], f"Workflow step {step['step']} failed"
```

### CI/CD Integration

#### 1. **GitHub Actions Workflow**
```yaml
# .github/workflows/bubble-frontend-tests.yml
name: Bubble Frontend Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 8 * * *'  # Run daily at 8 AM

jobs:
  bubble-frontend-tests:
    runs-on: ubuntu-latest
    
    services:
      personai-api:
        image: personai/api:latest
        ports:
          - 8000:8000
        env:
          - NODE_ENV=test
          - DATABASE_URL=postgresql://test:test@localhost:5432/test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install Python dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio requests playwright
    
    - name: Install Playwright browsers
      run: |
        playwright install chromium
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Node dependencies
      run: |
        npm install -g @bubble/cli
        bubble login --token ${{ secrets.BUBBLE_API_TOKEN }}
    
    - name: Deploy test app
      run: |
        bubble deploy --app-id ${{ secrets.BUBBLE_APP_ID }} --version test
    
    - name: Wait for services
      run: |
        timeout 120 bash -c 'until curl -f http://localhost:8000/health; do sleep 5; done'
        timeout 120 bash -c 'until curl -f https://personai.bubbleapps.io; do sleep 5; done'
    
    - name: Run API tests
      run: |
        pytest tests/bubble/bubble_api_tests.py -v --tb=short --html=api_report.html
    
    - name: Run UI tests
      run: |
        pytest tests/bubble/bubble_ui_tests.py -v --tb=short --html=ui_report.html
    
    - name: Run visual regression tests
      run: |
        pytest tests/bubble/visual_regression_tests.py -v --tb=short --html=visual_report.html
    
    - name: Run integration tests
      run: |
        pytest tests/bubble/integration_workflow_tests.py -v --tb=short --html=integration_report.html
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      with:
        name: bubble-frontend-test-reports
        path: |
          api_report.html
          ui_report.html
          visual_report.html
          integration_report.html
    
    - name: Upload visual baselines
      uses: actions/upload-artifact@v3
      with:
        name: visual-baselines
        path: visual_baselines/
    
    - name: Clean up test app
      if: always()
      run: |
        bubble delete --app-id ${{ secrets.BUBBLE_APP_ID }} --version test
```

This comprehensive testing strategy ensures that Person.ai's Bubble frontend is thoroughly tested across all layers, providing confidence in the application's functionality and reliability despite the no-code platform's limitations.
