#!/usr/bin/env python3
"""
Debug test for preferences form visibility
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_preferences():
    """Debug preferences form visibility"""
    print("🔍 Debugging Preferences Form")
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
            
            # Check what page we're on after login
            dashboard_content = page.locator('#dashboard-content')
            dashboard_visible = await dashboard_content.is_visible()
            print(f"📊 Dashboard content visible after login: {dashboard_visible}")
            
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
            
            # Check if the form is in the DOM
            form_exists = await page.locator('#preferences-form').count() > 0
            print(f"📋 Preferences form exists in DOM: {form_exists}")
            
            # Check parent elements
            form_parent = page.locator('#preferences-form').locator('..')
            parent_visible = await form_parent.is_visible()
            parent_classes = await form_parent.get_attribute("class")
            print(f"👨‍👩‍👧‍👦 Form parent visible: {parent_visible}")
            print(f"👨‍👩‍👧‍👦 Form parent classes: {parent_classes}")
            
            # Try clicking on settings navigation link
            print("🔗 Trying to click settings navigation link...")
            await page.click('a[onclick="showPage(\'settings\')"]')
            await page.wait_for_timeout(2000)
            
            # Check again
            settings_visible_after = await settings_content.is_visible()
            preferences_visible_after = await preferences_form.is_visible()
            print(f"⚙️ Settings content visible after nav click: {settings_visible_after}")
            print(f"📋 Preferences form visible after nav click: {preferences_visible_after}")
            
            # Take a screenshot
            await page.screenshot(path="debug_preferences.png")
            print("📸 Screenshot saved as debug_preferences.png")
            
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
    asyncio.run(debug_preferences())
