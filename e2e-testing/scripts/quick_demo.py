#!/usr/bin/env python3
"""
Quick demo script for E2E testing system
"""
import requests
import time
import json

# Configuration
GMAIL_URL = "http://localhost:5004"
CONTENT_URL = "http://localhost:5005"
MEDIA_URL = "http://localhost:5006"
DELIVERY_URL = "http://localhost:5007"

def test_gmail_mock():
    """Test Gmail mock service"""
    print("🔍 Testing Gmail Mock...")
    
    try:
        # Test health
        response = requests.get(f"{GMAIL_URL}/health", timeout=10)
        print(f"   Health: {response.status_code} - {response.json()}")
        
        # Test messages
        response = requests.get(f"{GMAIL_URL}/gmail/v1/users/me/messages?maxResults=3", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Messages: Found {len(data.get('messages', []))} messages")
        else:
            print(f"   Messages failed: {response.status_code}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Gmail mock failed: {e}")
        return False

def test_content_engine():
    """Test content engine mock"""
    print("🔍 Testing Content Engine...")
    
    try:
        # Test health
        response = requests.get(f"{CONTENT_URL}/health", timeout=10)
        print(f"   Health: {response.status_code} - {response.json()}")
        
        # Test brief generation
        test_data = {
            'gmail_data': {
                'emails': [
                    {'subject': 'Test Email', 'sender': 'test@example.com', 'body': 'Test body'}
                ]
            }
        }
        response = requests.post(f"{CONTENT_URL}/generate-brief", json=test_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Brief generation: Success")
            print(f"   Text length: {len(data['content']['text_content'])}")
        else:
            print(f"   Brief generation failed: {response.status_code}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Content engine failed: {e}")
        return False

def test_media_engine():
    """Test media engine mock"""
    print("🔍 Testing Media Engine...")
    
    try:
        # Test health
        response = requests.get(f"{MEDIA_URL}/health", timeout=10)
        print(f"   Health: {response.status_code} - {response.json()}")
        
        # Test audio generation
        test_data = {'text': 'Hello, this is a test audio generation.'}
        response = requests.post(f"{MEDIA_URL}/generate-audio", json=test_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Audio generation: Success")
            print(f"   Audio file: {data['result']['filename']}")
            print(f"   Duration: {data['result']['duration']:.2f}s")
        else:
            print(f"   Audio generation failed: {response.status_code}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Media engine failed: {e}")
        return False

def test_delivery_gateway():
    """Test delivery gateway mock"""
    print("🔍 Testing Delivery Gateway...")
    
    try:
        # Test health
        response = requests.get(f"{DELIVERY_URL}/health", timeout=10)
        print(f"   Health: {response.status_code} - {response.json()}")
        
        # Test delivery
        test_data = {
            'content': {'text_content': 'Test brief', 'audio_script': 'Test audio script'},
            'audio_file': 'test.wav'
        }
        response = requests.post(f"{DELIVERY_URL}/deliver/all", json=test_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Delivery: Success")
            for channel, result in data['results'].items():
                status = "✅" if result['status'] == 'delivered' else "❌"
                print(f"     {status} {channel.title()}: {result['status']}")
        else:
            print(f"   Delivery failed: {response.status_code}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Delivery gateway failed: {e}")
        return False

def main():
    """Main demo function"""
    print("🚀 E2E Testing System - Quick Demo")
    print("=" * 50)
    
    # Wait for services
    print("⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Test each service
    results = []
    results.append(test_gmail_mock())
    results.append(test_content_engine())
    results.append(test_media_engine())
    results.append(test_delivery_gateway())
    
    # Summary
    print("\n" + "=" * 50)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print("✅ All services are working correctly!")
        print("\n📝 Next steps:")
        print("   • Run full E2E test: python test_runner/e2e_test_runner.py")
        print("   • Check generated audio files in /app/output/")
        print("   • View delivery logs: curl http://localhost:5007/delivery-logs")
    else:
        print(f"❌ {total_count - success_count}/{total_count} services failed")
        print("   Check the errors above and ensure all services are running")

if __name__ == '__main__':
    main()
