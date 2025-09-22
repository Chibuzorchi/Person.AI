import pytest
import requests
import time
from typing import Dict, Any

# Mark as Tier 3 Secondary and Integration
pytestmark = [pytest.mark.tier3_secondary, pytest.mark.integration]

class BubbleAPITester:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
    
    def test_user_authentication(self) -> Dict[str, Any]:
        """Test user authentication via Bubble API"""
        try:
            response = self.session.post(f"{self.api_base_url}/user/login", json={
                "email": "test@personai.com",
                "password": "test_password"
            })
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data.get("session_token")
                self.user_id = auth_data.get("user", {}).get("user_id")
                return {
                    "success": True,
                    "user_id": self.user_id,
                    "session_token": self.auth_token,
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
    
    def test_briefing_scheduling(self) -> Dict[str, Any]:
        """Test briefing scheduling workflow"""
        if not self.auth_token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            # Set session token
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            
            # Create briefing schedule
            schedule_data = {
                "title": "Test Daily Brief",
                "time": "09:00",
                "frequency": "daily",
                "channels": ["slack", "email"]
            }
            
            response = self.session.post(f"{self.api_base_url}/briefings/schedule", json=schedule_data)
            
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
    
    def test_preferences_toggle(self) -> Dict[str, Any]:
        """Test user preferences toggle workflow"""
        if not self.auth_token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            # Set session token
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            
            # Get current preferences
            get_response = self.session.get(f"{self.api_base_url}/user/preferences")
            
            if get_response.status_code == 200:
                preferences = get_response.json()
                
                # Toggle a preference
                new_preferences = preferences.copy()
                new_preferences["slack_notifications"] = not preferences.get("slack_notifications", False)
                new_preferences["email_notifications"] = not preferences.get("email_notifications", False)
                
                # Update preferences
                update_response = self.session.put(
                    f"{self.api_base_url}/user/preferences",
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
    
    def test_integration_connection(self, integration_type: str) -> Dict[str, Any]:
        """Test integration connection workflow"""
        if not self.auth_token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            # Set session token
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            
            # Test integration connection
            connection_data = {
                "integration_type": integration_type,
                "config": {
                    "webhook_url": "https://hooks.slack.com/test",
                    "channel": "#general"
                } if integration_type == "slack" else {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "email_address": "test@personai.com"
                }
            }
            
            response = self.session.post(f"{self.api_base_url}/integrations/connect", json=connection_data)
            
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
        return BubbleAPITester(api_base_url="http://localhost:5001/api")
    
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
        briefing_result = api_tester.test_briefing_scheduling()
        
        assert briefing_result["success"], f"Briefing scheduling failed: {briefing_result['error']}"
        assert "briefing_id" in briefing_result
        assert briefing_result["response_time"] < 10.0, "Briefing scheduling too slow"
    
    def test_preferences_workflow(self, api_tester):
        """Test preferences toggle workflow"""
        # First authenticate
        auth_result = api_tester.test_user_authentication()
        assert auth_result["success"], "Authentication required for preferences test"
        
        # Test preferences toggle
        preferences_result = api_tester.test_preferences_toggle()
        
        assert preferences_result["success"], f"Preferences toggle failed: {preferences_result['error']}"
        assert "updated_preferences" in preferences_result
        assert preferences_result["response_time"] < 5.0, "Preferences update too slow"
    
    def test_slack_integration_workflow(self, api_tester):
        """Test Slack integration connection workflow"""
        # First authenticate
        auth_result = api_tester.test_user_authentication()
        assert auth_result["success"], "Authentication required for integration test"
        
        # Test Slack integration
        slack_result = api_tester.test_integration_connection("slack")
        
        assert slack_result["success"], f"Slack integration failed: {slack_result['error']}"
        assert "integration_id" in slack_result
        assert slack_result["response_time"] < 15.0, "Integration connection too slow"
    
    def test_email_integration_workflow(self, api_tester):
        """Test Email integration connection workflow"""
        # First authenticate
        auth_result = api_tester.test_user_authentication()
        assert auth_result["success"], "Authentication required for integration test"
        
        # Test Email integration
        email_result = api_tester.test_integration_connection("email")
        
        assert email_result["success"], f"Email integration failed: {email_result['error']}"
        assert "integration_id" in email_result
        assert email_result["response_time"] < 15.0, "Integration connection too slow"
    
    def test_api_health_check(self, api_tester):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{api_tester.api_base_url}/health", timeout=10)
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert "service" in health_data
            assert "timestamp" in health_data
        except Exception as e:
            pytest.fail(f"Health check failed: {str(e)}")
    
    def test_invalid_credentials(self, api_tester):
        """Test authentication with invalid credentials"""
        try:
            response = api_tester.session.post(f"{api_tester.api_base_url}/user/login", json={
                "email": "invalid@personai.com",
                "password": "wrong_password"
            })
            
            assert response.status_code == 401, "Should return 401 for invalid credentials"
            data = response.json()
            assert "error" in data
        except Exception as e:
            pytest.fail(f"Invalid credentials test failed: {str(e)}")
    
    def test_unauthorized_access(self, api_tester):
        """Test accessing protected endpoints without authentication"""
        try:
            # Try to access protected endpoint without auth
            response = requests.get(f"{api_tester.api_base_url}/user/preferences")
            assert response.status_code == 401, "Should return 401 for unauthorized access"
        except Exception as e:
            pytest.fail(f"Unauthorized access test failed: {str(e)}")
