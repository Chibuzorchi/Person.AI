#!/usr/bin/env python3
"""
Test Client - Demonstrates how to use the Slack Mock Server
"""
import asyncio
import websockets
import json
import requests
import time

class SlackTestClient:
    def __init__(self, wiremock_url="http://localhost:8080", websocket_url="ws://localhost:8765"):
        self.wiremock_url = wiremock_url
        self.websocket_url = websocket_url
    
    async def test_api_endpoints(self):
        """Test Slack API endpoints via WireMock"""
        print("Testing Slack API endpoints...")
        
        # Test successful message post
        print("\n1. Testing successful message post...")
        response = requests.post(
            f"{self.wiremock_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-valid-token"},
            json={
                "channel": "C1234567890",
                "text": "Hello from Person.ai test client!"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test expired token
        print("\n2. Testing expired token...")
        response = requests.post(
            f"{self.wiremock_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-expired-token"},
            json={
                "channel": "C1234567890",
                "text": "This should fail"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test rate limiting
        print("\n3. Testing rate limiting...")
        response1 = requests.post(
            f"{self.wiremock_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-rate-limited-token"},
            json={"channel": "C1234567890", "text": "First message"}
        )
        print(f"First request status: {response1.status_code}")
        
        response2 = requests.post(
            f"{self.wiremock_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-rate-limited-token"},
            json={"channel": "C1234567890", "text": "Second message (should be rate limited)"}
        )
        print(f"Second request status: {response2.status_code}")
        print(f"Rate limit response: {response2.json()}")
        
        # Test conversations list
        print("\n4. Testing conversations.list...")
        response = requests.get(
            f"{self.wiremock_url}/api/conversations.list",
            headers={"Authorization": "Bearer xoxb-valid-token"}
        )
        print(f"Status: {response.status_code}")
        print(f"Channels: {len(response.json()['channels'])}")
        
        # Test users list
        print("\n5. Testing users.list...")
        response = requests.get(
            f"{self.wiremock_url}/api/users.list",
            headers={"Authorization": "Bearer xoxb-valid-token"}
        )
        print(f"Status: {response.status_code}")
        print(f"Users: {len(response.json()['members'])}")
    
    async def test_websocket_events(self):
        """Test WebSocket event handling"""
        print("\nTesting WebSocket events...")
        
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                print("Connected to WebSocket server")
                
                # Subscribe to events
                await websocket.send(json.dumps({
                    "type": "subscribe",
                    "events": ["message", "app_mention", "member_joined_channel"]
                }))
                
                # Wait for subscription confirmation
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Subscription confirmed: {data}")
                
                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))
                pong = await websocket.recv()
                print(f"Pong received: {json.loads(pong)}")
                
                print("WebSocket test completed successfully!")
                
        except Exception as e:
            print(f"WebSocket test failed: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("=== Slack Mock Server Test Client ===")
        print("Make sure WireMock and WebSocket servers are running!")
        print("Start them with: docker-compose up")
        print()
        
        # Test API endpoints
        await self.test_api_endpoints()
        
        # Test WebSocket events
        await self.test_websocket_events()
        
        print("\n=== All tests completed ===")

async def main():
    """Main function"""
    client = SlackTestClient()
    await client.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
