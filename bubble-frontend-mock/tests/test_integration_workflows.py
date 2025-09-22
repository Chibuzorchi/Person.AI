import pytest
import asyncio
from typing import Dict, Any
try:
    from .test_bubble_api import BubbleAPITester
    from .test_bubble_ui import BubbleUITester
    # Mark as Tier 3 Secondary and Integration
    pytestmark = [pytest.mark.tier3_secondary, pytest.mark.integration]
except ImportError:
    # Skip all tests in this file if dependencies are not available
    pytestmark = pytest.mark.skip(reason="Test dependencies not available")

class IntegrationWorkflowTester:
    def __init__(self, app_url: str, api_url: str, test_credentials: Dict[str, str]):
        self.app_url = app_url
        self.api_url = api_url
        self.test_credentials = test_credentials
        self.api_tester = BubbleAPITester(api_url)
        self.ui_tester = BubbleUITester(app_url, test_credentials)
    
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
            api_briefing_result = self.api_tester.test_briefing_scheduling()
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
            api_preferences_result = self.api_tester.test_preferences_toggle()
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
    
    async def test_complete_integration_workflow(self, integration_type: str) -> Dict[str, Any]:
        """Test complete integration workflow from UI to API"""
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
            
            # Step 3: UI Integration Setup
            ui_integration_result = await self.ui_tester.test_integration_setup_ui(integration_type)
            results["workflow_steps"].append({
                "step": "ui_integration_setup",
                "success": ui_integration_result["success"],
                "details": ui_integration_result
            })
            
            if not ui_integration_result["success"]:
                results["overall_success"] = False
                results["errors"].append("UI integration setup failed")
                return results
            
            # Step 4: API Integration Verification
            api_integration_result = self.api_tester.test_integration_connection(integration_type)
            results["workflow_steps"].append({
                "step": "api_integration_verification",
                "success": api_integration_result["success"],
                "details": api_integration_result
            })
            
            if not api_integration_result["success"]:
                results["overall_success"] = False
                results["errors"].append("API integration verification failed")
                return results
            
        except Exception as e:
            results["overall_success"] = False
            results["errors"].append(f"Integration workflow execution error: {str(e)}")
        
        finally:
            await self.ui_tester.teardown_browser()
        
        return results
    
    async def test_end_to_end_user_journey(self) -> Dict[str, Any]:
        """Test complete end-to-end user journey"""
        results = {
            "workflow_steps": [],
            "overall_success": True,
            "errors": []
        }
        
        try:
            # Step 1: Login
            await self.ui_tester.setup_browser()
            ui_login_success = await self.ui_tester.login()
            results["workflow_steps"].append({
                "step": "user_login",
                "success": ui_login_success,
                "details": {"login_success": ui_login_success}
            })
            
            if not ui_login_success:
                results["overall_success"] = False
                results["errors"].append("User login failed")
                return results
            
            # Step 2: Dashboard Navigation
            dashboard_result = await self.ui_tester.test_dashboard_ui()
            results["workflow_steps"].append({
                "step": "dashboard_navigation",
                "success": dashboard_result["success"],
                "details": dashboard_result
            })
            
            # Step 3: Schedule Briefing
            briefing_result = await self.ui_tester.test_briefing_scheduling_ui()
            results["workflow_steps"].append({
                "step": "schedule_briefing",
                "success": briefing_result["success"],
                "details": briefing_result
            })
            
            # Step 4: Setup Integration
            integration_result = await self.ui_tester.test_integration_setup_ui("slack")
            results["workflow_steps"].append({
                "step": "setup_integration",
                "success": integration_result["success"],
                "details": integration_result
            })
            
            # Step 5: Update Preferences
            preferences_result = await self.ui_tester.test_preferences_toggle_ui()
            results["workflow_steps"].append({
                "step": "update_preferences",
                "success": preferences_result["success"],
                "details": preferences_result
            })
            
            # Check overall success
            failed_steps = [step for step in results["workflow_steps"] if not step["success"]]
            if failed_steps:
                results["overall_success"] = False
                results["errors"].append(f"Failed steps: {[step['step'] for step in failed_steps]}")
            
        except Exception as e:
            results["overall_success"] = False
            results["errors"].append(f"End-to-end journey error: {str(e)}")
        
        finally:
            await self.ui_tester.teardown_browser()
        
        return results

class TestIntegrationWorkflows:
    @pytest.fixture
    def test_config(self):
        return {
            "app_url": "http://localhost:8081",
            "api_url": "http://localhost:5001/api",
            "test_credentials": {
                "email": "test@personai.com",
                "password": "test_password"
            }
        }
    
    @pytest.fixture
    def integration_tester(self, test_config):
        return IntegrationWorkflowTester(
            app_url=test_config["app_url"],
            api_url=test_config["api_url"],
            test_credentials=test_config["test_credentials"]
        )
    
    @pytest.mark.asyncio
    async def test_complete_briefing_workflow(self, integration_tester):
        """Test complete briefing workflow integration"""
        result = await integration_tester.test_complete_briefing_workflow()
        
        assert result["overall_success"], f"Integration workflow failed: {result['errors']}"
        
        # Verify all steps succeeded
        for step in result["workflow_steps"]:
            assert step["success"], f"Workflow step {step['step']} failed"
    
    @pytest.mark.asyncio
    async def test_slack_integration_workflow(self, integration_tester):
        """Test complete Slack integration workflow"""
        result = await integration_tester.test_complete_integration_workflow("slack")
        
        assert result["overall_success"], f"Slack integration workflow failed: {result['errors']}"
        
        # Verify all steps succeeded
        for step in result["workflow_steps"]:
            assert step["success"], f"Integration step {step['step']} failed"
    
    @pytest.mark.asyncio
    async def test_email_integration_workflow(self, integration_tester):
        """Test complete Email integration workflow"""
        result = await integration_tester.test_complete_integration_workflow("email")
        
        assert result["overall_success"], f"Email integration workflow failed: {result['errors']}"
        
        # Verify all steps succeeded
        for step in result["workflow_steps"]:
            assert step["success"], f"Integration step {step['step']} failed"
    
    @pytest.mark.asyncio
    async def test_end_to_end_user_journey(self, integration_tester):
        """Test complete end-to-end user journey"""
        result = await integration_tester.test_end_to_end_user_journey()
        
        assert result["overall_success"], f"End-to-end journey failed: {result['errors']}"
        
        # Verify critical steps succeeded
        critical_steps = ["user_login", "schedule_briefing", "setup_integration"]
        for step_name in critical_steps:
            step = next((s for s in result["workflow_steps"] if s["step"] == step_name), None)
            assert step and step["success"], f"Critical step {step_name} failed"
    
    @pytest.mark.asyncio
    async def test_workflow_performance(self, integration_tester):
        """Test workflow performance and response times"""
        start_time = asyncio.get_event_loop().time()
        
        result = await integration_tester.test_complete_briefing_workflow()
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        assert result["overall_success"], f"Performance test workflow failed: {result['errors']}"
        assert total_time < 60, f"Workflow took too long: {total_time:.2f} seconds"
        
        # Check individual step response times
        for step in result["workflow_steps"]:
            if "response_time" in step.get("details", {}):
                response_time = step["details"]["response_time"]
                assert response_time < 10, f"Step {step['step']} too slow: {response_time:.2f}s"
