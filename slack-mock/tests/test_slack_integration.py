#!/usr/bin/env python3
"""
Slack Integration Test Suite
"""
import pytest
import requests
import asyncio
import json
import time
import os
from unittest.mock import patch

# Mark all tests in this file as integration tests that require services
pytestmark = pytest.mark.integration

# Skip these tests if running in CI without Docker services
if os.getenv('CI') and not os.getenv('DOCKER_SERVICES_RUNNING'):
    pytestmark = pytest.mark.skip(reason="Integration tests require Docker services")

class TestSlackIntegration:
    @pytest.fixture(autouse=True)
    def setup_mock(self):
        """Setup test configuration"""
        self.base_url = "http://localhost:8080"
        
    def test_successful_message_post(self):
        """Test successful message posting"""
        response = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-valid-token"},
            json={
                "channel": "C1234567890",
                "text": "Test message from Person.ai"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "ts" in data
        assert data["message"]["text"] == "Test message from Person.ai"
    
    def test_expired_token_handling(self):
        """Test handling of expired tokens"""
        response = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-expired-token"},
            json={
                "channel": "C1234567890",
                "text": "Test message"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["ok"] is False
        assert data["error"] == "invalid_auth"
    
    def test_rate_limiting_handling(self):
        """Test rate limiting behavior"""
        # First request should succeed
        response1 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-rate-limited-token"},
            json={"channel": "C1234567890", "text": "Message 1"}
        )
        assert response1.status_code == 200
        
        # Immediate second request should be rate limited
        response2 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-rate-limited-token"},
            json={"channel": "C1234567890", "text": "Message 2"}
        )
        assert response2.status_code == 429
        assert "Retry-After" in response2.headers
    
    def test_conversations_list(self):
        """Test conversations.list endpoint"""
        response = requests.get(
            f"{self.base_url}/api/conversations.list",
            headers={"Authorization": "Bearer xoxb-valid-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "channels" in data
        assert len(data["channels"]) > 0
    
    def test_users_list(self):
        """Test users.list endpoint"""
        response = requests.get(
            f"{self.base_url}/api/users.list",
            headers={"Authorization": "Bearer xoxb-valid-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "members" in data
        assert len(data["members"]) > 0
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_websocket_connection_skip(self):
        """Test WebSocket connection (skipped if not available)"""
        try:
            import websockets
            # This test is skipped if WebSocket server is not running
            pytest.skip("WebSocket server not available")
        except ImportError:
            pytest.skip("websockets library not available")
    
    def test_rate_limiter_reset(self):
        """Test rate limiter reset functionality"""
        # Use a unique token to avoid conflicts with other tests
        unique_token = f"xoxb-rate-limited-token-{int(time.time())}"
        
        # First request should succeed
        response1 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": f"Bearer {unique_token}"},
            json={"channel": "C1234567890", "text": "Message 1"}
        )
        assert response1.status_code == 200
        
        # Immediate second request should be rate limited
        response2 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": f"Bearer {unique_token}"},
            json={"channel": "C1234567890", "text": "Message 2"}
        )
        assert response2.status_code == 429
        
        # Wait for rate limit to reset
        time.sleep(1.1)
        
        # Third request should succeed again
        response3 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": f"Bearer {unique_token}"},
            json={"channel": "C1234567890", "text": "Message 3"}
        )
        assert response3.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
