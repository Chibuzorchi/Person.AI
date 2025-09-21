#!/usr/bin/env python3
"""
Debug test for briefings navigation
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_briefings():
    """Debug briefings navigation"""
    print("🔍 Debugging Briefings Navigation")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in visible mode
        page = await browser.new_page()
        
        try:
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
            
            # Navigate to briefings
            print("📅 Navigating to briefings...")
            await page.evaluate("window.app.showPage('briefings')")
            await page.wait_for_timeout(2000)
            
            # Check briefings content
            briefings_content = page.locator('#briefings-content')
            briefings_visible = await briefings_content.is_visible()
            briefings_classes = await briefings_content.get_attribute("class")
            print(f"📅 Briefings content visible: {briefings_visible}")
            print(f"📅 Briefings content classes: {briefings_classes}")
            
            # Check briefings list
            briefings_list = page.locator('#briefings-list')
            briefings_list_visible = await briefings_list.is_visible()
            briefings_list_classes = await briefings_list.get_attribute("class")
            print(f"📋 Briefings list visible: {briefings_list_visible}")
            print(f"📋 Briefings list classes: {briefings_list_classes}")
            
            # Check dashboard page visibility
            dashboard_page = page.locator('#dashboard-page')
            dashboard_page_visible = await dashboard_page.is_visible()
            dashboard_page_classes = await dashboard_page.get_attribute("class")
            print(f"📄 Dashboard page visible: {dashboard_page_visible}")
            print(f"📄 Dashboard page classes: {dashboard_page_classes}")
            
            # Take a screenshot
            await page.screenshot(path="debug_briefings.png")
            print("📸 Screenshot saved as debug_briefings.png")
            
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
    asyncio.run(debug_briefings())
