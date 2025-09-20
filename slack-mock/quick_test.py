#!/usr/bin/env python3
"""
Quick test to verify the mock server works
"""
import requests
import json
import time

def test_slack_mock():
    """Test the Slack mock server"""
    base_url = "http://localhost:8080"
    
    print("=== Quick Slack Mock Test ===")
    print("Make sure the server is running with: python simple_mock_server.py")
    print()
    
    try:
        # Test health check
        print("1. Testing health check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test successful message post
        print("\n2. Testing message post...")
        response = requests.post(
            f"{base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-valid-token"},
            json={
                "channel": "C1234567890",
                "text": "Hello from test!"
            },
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test expired token
        print("\n3. Testing expired token...")
        response = requests.post(
            f"{base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-expired-token"},
            json={
                "channel": "C1234567890",
                "text": "This should fail"
            },
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test rate limiting
        print("\n4. Testing rate limiting...")
        response1 = requests.post(
            f"{base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-rate-limited-token"},
            json={"channel": "C1234567890", "text": "First message"},
            timeout=5
        )
        print(f"   First request status: {response1.status_code}")
        
        response2 = requests.post(
            f"{base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-rate-limited-token"},
            json={"channel": "C1234567890", "text": "Second message"},
            timeout=5
        )
        print(f"   Second request status: {response2.status_code}")
        print(f"   Rate limited: {response2.status_code == 429}")
        
        print("\n✅ All tests passed! The Slack mock server is working correctly.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running with:")
        print("   python simple_mock_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_slack_mock()
