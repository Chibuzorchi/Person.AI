#!/usr/bin/env python3
"""
Quick demo script for the Bubble Frontend Mock
Shows the key workflows and test capabilities
"""

import requests
import time
import webbrowser
from pathlib import Path

def check_services():
    """Check if services are running"""
    print("🔍 Checking services...")
    
    try:
        # Check API
        api_response = requests.get("http://localhost:5001/api/health", timeout=5)
        if api_response.status_code == 200:
            print("✅ API is running at http://localhost:5001")
        else:
            print("❌ API not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ API not accessible")
        return False
    
    try:
        # Check Frontend
        frontend_response = requests.get("http://localhost:8081", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend is running at http://localhost:8081")
        else:
            print("❌ Frontend not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Frontend not accessible")
        return False
    
    return True

def demo_api_endpoints():
    """Demo API endpoints"""
    print("\n🔧 API Endpoints Demo")
    print("-" * 30)
    
    try:
        # Test login
        print("Testing login...")
        login_response = requests.post("http://localhost:5001/api/user/login", json={
            "email": "test@personai.com",
            "password": "test_password"
        })
        
        if login_response.status_code == 200:
            auth_data = login_response.json()
            print(f"✅ Login successful: {auth_data['user']['name']}")
            
            # Test briefing scheduling
            print("Testing briefing scheduling...")
            briefing_response = requests.post("http://localhost:5001/api/briefings/schedule", 
                json={
                    "title": "Demo Briefing",
                    "time": "09:00",
                    "frequency": "daily",
                    "channels": ["slack", "email"]
                },
                headers={"Authorization": f"Bearer {auth_data['session_token']}"}
            )
            
            if briefing_response.status_code == 201:
                briefing_data = briefing_response.json()
                print(f"✅ Briefing scheduled: {briefing_data['briefing_id']}")
            
            # Test preferences
            print("Testing preferences...")
            prefs_response = requests.get("http://localhost:5001/api/user/preferences",
                headers={"Authorization": f"Bearer {auth_data['session_token']}"}
            )
            
            if prefs_response.status_code == 200:
                prefs = prefs_response.json()
                print(f"✅ Preferences retrieved: {prefs}")
            
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ API demo failed: {e}")

def demo_frontend_features():
    """Demo frontend features"""
    print("\n🖥️  Frontend Features Demo")
    print("-" * 30)
    
    print("Available workflows:")
    print("• User Login (test@personai.com / test_password)")
    print("• Dashboard Overview")
    print("• Briefing Scheduling")
    print("• Integration Setup (Slack, Email)")
    print("• Preferences Management")
    print("• Visual Regression Testing")
    
    print(f"\n🌐 Open the frontend in your browser:")
    print(f"   http://localhost:8081")
    
    # Try to open browser
    try:
        webbrowser.open("http://localhost:8081")
        print("✅ Browser opened automatically")
    except Exception:
        print("⚠️  Could not open browser automatically")

def demo_test_capabilities():
    """Demo test capabilities"""
    print("\n🧪 Test Capabilities Demo")
    print("-" * 30)
    
    print("Available test suites:")
    print("• API Tests - Authentication, Briefing, Preferences, Integrations")
    print("• UI Tests - Login, Navigation, Form Interactions")
    print("• Visual Regression Tests - Screenshot comparisons")
    print("• Integration Tests - End-to-end workflows")
    
    print("\nTest commands:")
    print("• Run all tests: python scripts/run_all_tests.py")
    print("• API tests only: pytest tests/test_bubble_api.py -v")
    print("• UI tests only: pytest tests/test_bubble_ui.py -v")
    print("• Visual tests only: pytest tests/test_visual_regression.py -v")
    print("• Integration tests only: pytest tests/test_integration_workflows.py -v")

def main():
    """Main demo function"""
    print("🚀 Person.ai Bubble Frontend Mock - Quick Demo")
    print("=" * 60)
    
    # Check services
    if not check_services():
        print("\n❌ Services not running. Please start them first:")
        print("   docker-compose up -d")
        return
    
    # Demo API
    demo_api_endpoints()
    
    # Demo Frontend
    demo_frontend_features()
    
    # Demo Tests
    demo_test_capabilities()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("\n📝 Next steps:")
    print("   • Explore the frontend at http://localhost:8081")
    print("   • Run tests to validate functionality")
    print("   • Check visual baselines in ./visual_baselines/")
    print("   • Review test results in ./output/")

if __name__ == "__main__":
    main()
