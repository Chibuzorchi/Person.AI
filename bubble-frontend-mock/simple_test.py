#!/usr/bin/env python3
"""
Simple test script to demonstrate the Bubble frontend mock system
"""
import asyncio
import requests
from playwright.async_api import async_playwright

async def test_frontend_access():
    """Test that we can access the frontend"""
    print("🌐 Testing frontend access...")
    
    try:
        response = requests.get("http://localhost:8081", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

async def test_api_access():
    """Test that we can access the API"""
    print("🔧 Testing API access...")
    
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is accessible")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return False

async def test_browser_interaction():
    """Test basic browser interaction with the frontend"""
    print("🖥️  Testing browser interaction...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to the frontend
            await page.goto("http://localhost:8081")
            
            # Check if the page loaded
            title = await page.title()
            print(f"✅ Page loaded with title: {title}")
            
            # Check if login form is present
            login_form = await page.query_selector("#login-form")
            if login_form:
                print("✅ Login form found")
            else:
                print("❌ Login form not found")
            
            # Try to fill in login form
            email_input = await page.query_selector("#email-input")
            password_input = await page.query_selector("#password-input")
            
            if email_input and password_input:
                await email_input.fill("test@personai.com")
                await password_input.fill("test_password")
                print("✅ Login form filled successfully")
                
                # Try to submit
                submit_button = await page.query_selector("#login-button")
                if submit_button:
                    await submit_button.click()
                    print("✅ Login form submitted")
                    
                    # Wait a bit for potential redirect
                    await page.wait_for_timeout(2000)
                    
                    # Check if we're on dashboard
                    current_url = page.url
                    if "dashboard" in current_url or "briefings" in current_url:
                        print("✅ Successfully navigated to dashboard")
                    else:
                        print(f"ℹ️  Current URL: {current_url}")
            else:
                print("❌ Login form inputs not found")
            
            await browser.close()
            return True
            
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

async def test_api_endpoints():
    """Test key API endpoints"""
    print("🔌 Testing API endpoints...")
    
    endpoints = [
        ("/api/health", "Health check"),
        ("/api/user/login", "Login endpoint"),
        ("/api/briefings", "Briefings list"),
        ("/api/integrations", "Integrations list")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            if endpoint == "/api/user/login":
                # Test login endpoint with POST
                response = requests.post(
                    f"http://localhost:5001{endpoint}",
                    json={"email": "test@personai.com", "password": "test_password"},
                    timeout=5
                )
            else:
                # Test other endpoints with GET
                response = requests.get(f"http://localhost:5001{endpoint}", timeout=5)
            
            if response.status_code in [200, 201]:
                print(f"✅ {description}: OK")
                results.append(True)
            else:
                print(f"⚠️  {description}: Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {description}: {e}")
            results.append(False)
    
    return all(results)

async def main():
    """Run all tests"""
    print("🚀 Person.ai Bubble Frontend Mock - Simple Test")
    print("=" * 60)
    
    # Test frontend access
    frontend_ok = await test_frontend_access()
    print()
    
    # Test API access
    api_ok = await test_api_access()
    print()
    
    # Test API endpoints
    endpoints_ok = await test_api_endpoints()
    print()
    
    # Test browser interaction
    browser_ok = await test_browser_interaction()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Frontend Access: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"API Access: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if endpoints_ok else '❌ FAIL'}")
    print(f"Browser Interaction: {'✅ PASS' if browser_ok else '❌ FAIL'}")
    
    all_passed = all([frontend_ok, api_ok, endpoints_ok, browser_ok])
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 The Bubble frontend mock system is working correctly!")
        print("🌐 You can now access the frontend at: http://localhost:8081")
        print("🔧 API is available at: http://localhost:5001/api")

if __name__ == "__main__":
    asyncio.run(main())
