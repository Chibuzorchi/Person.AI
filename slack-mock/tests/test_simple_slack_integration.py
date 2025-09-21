#!/usr/bin/env python3
"""
Simple Slack Integration Test Suite
"""
import pytest
import requests
import asyncio
import json
import time
import aiohttp
import os

# Mark all tests in this file as integration tests that require services
pytestmark = pytest.mark.integration

# Skip these tests if running in CI without Docker services
if os.getenv('CI') and not os.getenv('DOCKER_SERVICES_RUNNING'):
    pytestmark = pytest.mark.skip(reason="Integration tests require Docker services")

class TestSimpleSlackIntegration:
    @pytest.fixture(autouse=True)
    def setup_mock(self):
        """Setup test configuration"""
        self.base_url = "http://localhost:8080"
        
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "websocket_clients" in data
    
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
        assert data["message"]["username"] == "Person.ai Bot"
    
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
        assert data["detail"] == "token_expired"
    
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
        data = response2.json()
        assert data["error"] == "ratelimited"
    
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
        
        # Check channel structure
        channel = data["channels"][0]
        assert "id" in channel
        assert "name" in channel
        assert "is_channel" in channel
    
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
        
        # Check user structure
        user = data["members"][0]
        assert "id" in user
        assert "name" in user
        assert "real_name" in user
        assert "profile" in user
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection and event broadcasting"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(f"{self.base_url.replace('http', 'ws')}/ws") as ws:
                    # Send subscription message
                    await ws.send_str(json.dumps({
                        "type": "subscribe",
                        "events": ["message", "app_mention"]
                    }))
                    
                    # Wait for subscription confirmation
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            assert data["type"] == "subscription_confirmed"
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            pytest.fail(f"WebSocket error: {ws.exception()}")
                    
                    # Send ping
                    await ws.send_str(json.dumps({"type": "ping"}))
                    
                    # Wait for pong
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            assert data["type"] == "pong"
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            pytest.fail(f"WebSocket error: {ws.exception()}")
                    
        except Exception as e:
            pytest.fail(f"WebSocket test failed: {e}")
    
    def test_rate_limiter_reset(self):
        """Test that rate limiter resets after time window"""
        # Use a unique token for this test to avoid interference
        test_token = "xoxb-rate-limited-reset-test"
        
        # Make a request to trigger rate limiting
        response1 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"channel": "C1234567890", "text": "First message"}
        )
        assert response1.status_code == 200
        
        # Second request should be rate limited
        response2 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"channel": "C1234567890", "text": "Second message"}
        )
        assert response2.status_code == 429
        
        # Wait for rate limit window to reset (1.1 seconds)
        time.sleep(1.1)
        
        # Third request should succeed
        response3 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"channel": "C1234567890", "text": "Third message"}
        )
        assert response3.status_code == 200
    
    def test_different_tokens_not_rate_limited(self):
        """Test that different tokens don't affect each other's rate limits"""
        # Use different tokens
        token1 = "xoxb-rate-limited-token-1"
        token2 = "xoxb-rate-limited-token-2"
        
        # Both should succeed
        response1 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token1}"},
            json={"channel": "C1234567890", "text": "Token 1 message"}
        )
        assert response1.status_code == 200
        
        response2 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token2}"},
            json={"channel": "C1234567890", "text": "Token 2 message"}
        )
        assert response2.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
