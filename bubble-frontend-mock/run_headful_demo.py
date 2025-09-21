#!/usr/bin/env python3
"""
Run Bubble Frontend Tests in Headful Mode
This will show the browser automation in action!
"""
import asyncio
import sys
import os
from playwright.async_api import async_playwright

async def run_headful_demo():
    """Run UI tests with visible browser"""
    print("🎬 Starting Bubble Frontend Demo - Headful Mode")
    print("=" * 60)
    print("🌐 Frontend URL: http://localhost:8081")
    print("🔌 API URL: http://localhost:5001")
    print("👀 Browser will be visible - you can watch the automation!")
    print("=" * 60)
    
    # Import the UI tester
    sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
    from test_bubble_ui import BubbleUITester
    
    # Test credentials (matching what's in the API)
    test_credentials = {
        "email": "test@personai.com",
        "password": "test_password"
    }
    
    # Create UI tester
    ui_tester = BubbleUITester("http://localhost:8081", test_credentials)
    
    try:
        print("🚀 Setting up browser (will be visible)...")
        await ui_tester.setup_browser()
        
        print("🔑 Testing login workflow...")
        login_success = await ui_tester.login()
        if login_success:
            print("✅ Login successful!")
            
            # Wait a bit so you can see the dashboard
            print("⏳ Waiting 3 seconds to view dashboard...")
            await asyncio.sleep(3)
            
            print("📊 Testing navigation workflow...")
            await ui_tester.test_navigation_ui()
            print("✅ Navigation test completed!")
            
            print("⏳ Waiting 2 seconds...")
            await asyncio.sleep(2)
            
            print("📝 Testing briefings workflow...")
            await ui_tester.test_briefing_scheduling_ui()
            print("✅ Briefings test completed!")
            
            print("⏳ Waiting 2 seconds...")
            await asyncio.sleep(2)
            
            print("⚙️ Testing preferences workflow...")
            await ui_tester.test_preferences_toggle_ui()
            print("✅ Preferences test completed!")
            
            print("⏳ Waiting 2 seconds...")
            await asyncio.sleep(2)
            
            print("🔗 Testing Slack integration setup...")
            await ui_tester.test_integration_setup_ui('slack')
            print("✅ Slack integration test completed!")
            
            print("⏳ Waiting 2 seconds...")
            await asyncio.sleep(2)
            
            print("📧 Testing Email integration setup...")
            await ui_tester.test_integration_setup_ui('email')
            print("✅ Email integration test completed!")
            
            print("⏳ Final wait - 3 seconds to see the results...")
            await asyncio.sleep(3)
            
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔚 Cleaning up browser...")
        await ui_tester.teardown_browser()
        print("✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(run_headful_demo())
