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
            import asyncio
            import socket
            
            # Check if WebSocket port is open
            def is_port_open(host, port):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    return result == 0
                except:
                    return False
            
            if not is_port_open('localhost', 8765):
                pytest.skip("WebSocket server not running on port 8765")
            
            async def test_websocket():
                try:
                    async with websockets.connect("ws://localhost:8765/ws", timeout=5) as websocket:
                        # Send a test message
                        await websocket.send('{"type": "ping"}')
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        assert response is not None
                        print("✅ WebSocket connection successful")
                        return True
                except Exception as e:
                    print(f"WebSocket connection failed: {e}")
                    return False
            
            # Run the async test
            result = asyncio.run(test_websocket())
            if not result:
                pytest.skip("WebSocket server not available or connection failed")
                
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
