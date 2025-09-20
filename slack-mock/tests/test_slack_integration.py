#!/usr/bin/env python3
"""
Slack Integration Test Suite
"""
import pytest
import requests
import asyncio
import json
import time
from unittest.mock import patch
from slack_mock_server import SlackMockServer
from test_data_factory import SlackDataFactory

class TestSlackIntegration:
    @pytest.fixture(autouse=True)
    def setup_mock(self):
        """Setup mock server before each test"""
        self.mock_server = SlackMockServer()
        self.data_factory = SlackDataFactory()
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
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection and event broadcasting"""
        import websockets
        
        # Connect to WebSocket
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            # Send subscription message
            await websocket.send(json.dumps({
                "type": "subscribe",
                "events": ["message", "app_mention"]
            }))
            
            # Wait for subscription confirmation
            response = await websocket.recv()
            data = json.loads(response)
            assert data["type"] == "subscription_confirmed"
            
            # Simulate a message event
            await self.mock_server.simulate_user_message(
                "C1234567890", 
                "Hello from test user"
            )
            
            # Wait for the event
            event = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            event_data = json.loads(event)
            assert event_data["type"] == "message"
            assert event_data["text"] == "Hello from test user"
    
    def test_data_factory_generation(self):
        """Test data factory generates realistic data"""
        workspace = self.data_factory.generate_workspace()
        assert "id" in workspace
        assert workspace["id"].startswith("T")
        
        channels = self.data_factory.generate_channels(5)
        assert len(channels) == 5
        for channel in channels:
            assert "id" in channel
            assert channel["id"].startswith("C")
        
        users = self.data_factory.generate_users(3)
        assert len(users) == 3
        for user in users:
            assert "id" in user
            assert user["id"].startswith("U")
    
    def test_token_manager(self):
        """Test token management and refresh"""
        token_manager = self.mock_server.token_manager
        
        # Get initial token
        token1 = token_manager.get_valid_token("user1")
        assert token1.startswith("xoxb-refreshed-")
        
        # Get same token again (should be cached)
        token2 = token_manager.get_valid_token("user1")
        assert token1 == token2
        
        # Force token expiration and refresh
        token_data = token_manager.tokens["user1"]
        token_data["expires_at"] = time.time() - 1  # Expired
        
        token3 = token_manager.get_valid_token("user1")
        assert token3 != token1  # Should be different (refreshed)
    
    def test_rate_limiter(self):
        """Test rate limiting functionality"""
        rate_limiter = self.mock_server.rate_limiter
        
        # Should not be rate limited initially
        assert not rate_limiter.is_rate_limited("chat.postMessage", "test-token")
        
        # Record a request
        rate_limiter.record_request("chat.postMessage", "test-token")
        
        # Should be rate limited now (limit is 1 per second)
        assert rate_limiter.is_rate_limited("chat.postMessage", "test-token")
        
        # Wait for rate limit window to reset
        time.sleep(1.1)
        assert not rate_limiter.is_rate_limited("chat.postMessage", "test-token")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
