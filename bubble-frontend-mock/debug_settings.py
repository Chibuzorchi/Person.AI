#!/usr/bin/env python3
"""
Debug test for settings page visibility
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_settings():
    """Debug settings page visibility"""
    print("🔍 Debugging Settings Page")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in visible mode
        page = await browser.new_page()
        
        try:
            # Set smaller viewport
            await page.set_viewport_size({"width": 1280, "height": 720})
            
            # Navigate to the page
            print("🌐 Navigating to frontend...")
            await page.goto("http://localhost:8081")
            await page.wait_for_load_state('networkidle')
            
            # Login first
            print("🔐 Logging in...")
            await page.fill('#email-input', 'test@personai.com')
            await page.fill('#password-input', 'test_password')
            await page.click('#login-button')
            await page.wait_for_timeout(2000)
            
            # Navigate to settings
            print("⚙️ Navigating to settings...")
            await page.evaluate("window.app.showPage('settings')")
            await page.wait_for_timeout(2000)
            
            # Check settings content
            settings_content = page.locator('#settings-content')
            settings_visible = await settings_content.is_visible()
            settings_classes = await settings_content.get_attribute("class")
            print(f"⚙️ Settings content visible: {settings_visible}")
            print(f"⚙️ Settings content classes: {settings_classes}")
            
            # Check preferences form
            preferences_form = page.locator('#preferences-form')
            preferences_visible = await preferences_form.is_visible()
            preferences_classes = await preferences_form.get_attribute("class")
            print(f"📋 Preferences form visible: {preferences_visible}")
            print(f"📋 Preferences form classes: {preferences_classes}")
            
            # Check dashboard page visibility
            dashboard_page = page.locator('#dashboard-page')
            dashboard_page_visible = await dashboard_page.is_visible()
            dashboard_page_classes = await dashboard_page.get_attribute("class")
            print(f"📄 Dashboard page visible: {dashboard_page_visible}")
            print(f"📄 Dashboard page classes: {dashboard_page_classes}")
            
            # Take a screenshot
            await page.screenshot(path="debug_settings.png")
            print("📸 Screenshot saved as debug_settings.png")
            
            # Wait for visual inspection
            print("⏳ Waiting 5 seconds for visual inspection...")
            await page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"❌ Debug failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_settings())
