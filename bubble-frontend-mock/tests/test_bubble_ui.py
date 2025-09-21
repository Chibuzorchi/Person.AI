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
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        
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
            await self.page.goto(f"{self.app_url}/index.html")
            
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
            # Navigate to briefings page using JavaScript
            await self.page.goto(f"{self.app_url}/index.html")
            await self.page.evaluate("window.app.showPage('briefings')")
            await self.page.wait_for_selector('.briefings-list', timeout=10000)
            
            # Click schedule briefing button
            await self.page.click('button[onclick="showPage(\'schedule-briefing\')"]')
            await self.page.wait_for_timeout(1000)  # Wait for JavaScript to execute
            await self.page.wait_for_selector('[data-testid="schedule-form"]', timeout=10000)
            
            # Fill briefing form
            await self.page.fill('[data-testid="briefing-title"]', "Test Daily Brief")
            await self.page.select_option('[data-testid="time-select"]', "09:00")
            await self.page.select_option('[data-testid="frequency-select"]', "daily")
            
            # Select channels - click on the label since checkbox is hidden
            await self.page.click('label.checkbox-label:has(input#slack-channel)')
            await self.page.click('label.checkbox-label:has(input#email-channel)')
            
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
            # First ensure we're logged in
            await self.login()
            
            # Navigate to settings page using JavaScript
            await self.page.evaluate("window.app.showPage('settings')")
            await self.page.wait_for_timeout(2000)  # Wait longer for JavaScript to execute
            
            # Debug: Check if settings content is visible
            settings_content = self.page.locator('#settings-content')
            settings_visible = await settings_content.is_visible()
            print(f"DEBUG: Settings content visible: {settings_visible}")
            
            # Debug: Check if preferences form exists
            form_exists = await self.page.locator('#preferences-form').count() > 0
            print(f"DEBUG: Preferences form exists: {form_exists}")
            
            await self.page.wait_for_selector('[data-testid="preferences-form"]', timeout=10000)
            
            # Get initial state
            slack_toggle = self.page.locator('[data-testid="slack-notifications-toggle"]')
            initial_slack_state = await slack_toggle.is_checked()
            
            # Toggle Slack notifications - click on the label since checkbox is hidden
            await self.page.click('label.toggle-label:has(input#slack-notifications-toggle)')
            
            # Wait for state change
            await self.page.wait_for_timeout(1000)
            
            # Verify toggle state changed
            new_slack_state = await slack_toggle.is_checked()
            
            # Save preferences
            await self.page.click('[data-testid="save-preferences-button"]')
            
            # Wait for success message
            await self.page.wait_for_selector('#preferences-success-message', timeout=10000)
            
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
            # Navigate to integrations page using JavaScript
            await self.page.evaluate("window.app.showPage('integrations')")
            await self.page.wait_for_timeout(2000)  # Wait for JavaScript to execute
            await self.page.wait_for_selector('[data-testid="integrations-list"]', timeout=10000)
            
            # Click on specific integration's Configure button to open modal
            await self.page.click(f'[data-testid="{integration_type}-integration-card"] button[onclick="setupIntegration(\'{integration_type}\')"]')
            
            # Wait for modal to appear
            await self.page.wait_for_selector('.modal-content', timeout=10000)
            
            # Wait for integration setup form inside modal
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
            
            # Wait for modal to close (success indicator)
            await self.page.wait_for_selector('.modal-content', state='hidden', timeout=10000)
            
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
    
    async def test_dashboard_ui(self) -> Dict[str, Any]:
        """Test dashboard UI elements"""
        try:
            # Navigate to dashboard
            await self.page.goto(f"{self.app_url}/index.html#dashboard")
            await self.page.wait_for_selector('[data-testid="dashboard"]', timeout=10000)
            
            # Check dashboard elements
            dashboard_title = await self.page.text_content('h1')
            metric_cards = await self.page.locator('.dashboard-card').count()
            
            return {
                "success": True,
                "dashboard_title": dashboard_title,
                "metric_cards_count": metric_cards,
                "screenshot": await self.page.screenshot()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "screenshot": await self.page.screenshot()
            }
    
    async def test_navigation_ui(self) -> Dict[str, Any]:
        """Test navigation between pages"""
        try:
            # Start at dashboard
            await self.page.goto(f"{self.app_url}/index.html#dashboard")
            await self.page.wait_for_selector('[data-testid="dashboard"]', timeout=10000)
            
            # Navigate to briefings - use more specific selector
            await self.page.click('a[onclick="showPage(\'briefings\')"]')
            await self.page.wait_for_selector('[data-testid="briefings-list"]', timeout=10000)
            
            # Navigate to integrations - use more specific selector
            await self.page.click('a[onclick="showPage(\'integrations\')"]')
            await self.page.wait_for_selector('[data-testid="integrations-list"]', timeout=10000)
            
            # Navigate to settings - use more specific selector
            await self.page.click('a[onclick="showPage(\'settings\')"]')
            await self.page.wait_for_selector('[data-testid="preferences-form"]', timeout=10000)
            
            return {
                "success": True,
                "navigation_worked": True,
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
    def ui_tester(self):
        return BubbleUITester(
            app_url="http://localhost:8081",
            test_credentials={
                "email": "test@personai.com",
                "password": "test_password"
            }
        )
    
    @pytest.mark.asyncio
    async def test_login_workflow(self, ui_tester):
        """Test user login workflow"""
        await ui_tester.setup_browser()
        try:
            login_success = await ui_tester.login()
            assert login_success, "Login workflow failed"
        finally:
            await ui_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_dashboard_ui(self, ui_tester):
        """Test dashboard UI elements"""
        await ui_tester.setup_browser()
        try:
            # First login
            login_success = await ui_tester.login()
            assert login_success, "Login required for dashboard test"
            
            # Test dashboard
            result = await ui_tester.test_dashboard_ui()
            assert result["success"], f"Dashboard UI test failed: {result.get('error')}"
            assert result["metric_cards_count"] > 0, "Dashboard should have metric cards"
        finally:
            await ui_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_navigation_workflow(self, ui_tester):
        """Test navigation between pages"""
        await ui_tester.setup_browser()
        try:
            # First login
            login_success = await ui_tester.login()
            assert login_success, "Login required for navigation test"
            
            # Test navigation
            result = await ui_tester.test_navigation_ui()
            assert result["success"], f"Navigation test failed: {result.get('error')}"
            assert result["navigation_worked"], "Navigation between pages failed"
        finally:
            await ui_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_briefing_scheduling_workflow(self, ui_tester):
        """Test briefing scheduling UI workflow"""
        await ui_tester.setup_browser()
        try:
            # First login
            login_success = await ui_tester.login()
            assert login_success, "Login required for briefing test"
            
            # Test briefing scheduling
            result = await ui_tester.test_briefing_scheduling_ui()
            assert result["success"], f"Briefing scheduling UI failed: {result.get('error')}"
            assert "Briefing scheduled successfully" in result["message"]
        finally:
            await ui_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_preferences_workflow(self, ui_tester):
        """Test preferences toggle UI workflow"""
        await ui_tester.setup_browser()
        try:
            # First login
            login_success = await ui_tester.login()
            assert login_success, "Login required for preferences test"
            
            # Test preferences toggle
            result = await ui_tester.test_preferences_toggle_ui()
            assert result["success"], f"Preferences toggle UI failed: {result.get('error')}"
            assert result["state_changed"], "Toggle state did not change"
        finally:
            await ui_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_slack_integration_workflow(self, ui_tester):
        """Test Slack integration setup UI workflow"""
        await ui_tester.setup_browser()
        try:
            # First login
            login_success = await ui_tester.login()
            assert login_success, "Login required for integration test"
            
            # Test Slack integration
            result = await ui_tester.test_integration_setup_ui("slack")
            assert result["success"], f"Slack integration UI failed: {result.get('error')}"
            assert result["integration_type"] == "slack"
        finally:
            await ui_tester.teardown_browser()
    
    @pytest.mark.asyncio
    async def test_email_integration_workflow(self, ui_tester):
        """Test Email integration setup UI workflow"""
        await ui_tester.setup_browser()
        try:
            # First login
            login_success = await ui_tester.login()
            assert login_success, "Login required for integration test"
            
            # Test Email integration
            result = await ui_tester.test_integration_setup_ui("email")
            assert result["success"], f"Email integration UI failed: {result.get('error')}"
            assert result["integration_type"] == "email"
        finally:
            await ui_tester.teardown_browser()
