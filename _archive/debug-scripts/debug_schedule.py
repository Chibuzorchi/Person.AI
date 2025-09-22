#!/usr/bin/env python3
"""
Debug test for schedule briefing form visibility
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_schedule_form():
    """Debug schedule briefing form visibility"""
    print("🔍 Debugging Schedule Briefing Form")
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
            
            # Navigate to briefings
            print("📅 Navigating to briefings...")
            await page.evaluate("window.app.showPage('briefings')")
            await page.wait_for_timeout(1000)
            
            # Check if briefings content is visible
            briefings_content = page.locator('#briefings-content')
            briefings_visible = await briefings_content.is_visible()
            print(f"📅 Briefings content visible: {briefings_visible}")
            
            # Click schedule briefing button
            print("➕ Clicking schedule briefing button...")
            await page.click('button[onclick="showPage(\'schedule-briefing\')"]')
            await page.wait_for_timeout(2000)
            
            # Check schedule briefing content
            schedule_content = page.locator('#schedule-briefing-content')
            schedule_visible = await schedule_content.is_visible()
            schedule_classes = await schedule_content.get_attribute("class")
            print(f"📝 Schedule briefing content visible: {schedule_visible}")
            print(f"📝 Schedule briefing content classes: {schedule_classes}")
            
            # Check form
            form = page.locator('#schedule-form')
            form_visible = await form.is_visible()
            form_classes = await form.get_attribute("class")
            print(f"📋 Form visible: {form_visible}")
            print(f"📋 Form classes: {form_classes}")
            
            # Check checkboxes
            slack_checkbox = page.locator('#slack-channel')
            slack_visible = await slack_checkbox.is_visible()
            slack_enabled = await slack_checkbox.is_enabled()
            print(f"☑️  Slack checkbox visible: {slack_visible}, enabled: {slack_enabled}")
            
            # Check computed styles
            slack_display = await slack_checkbox.evaluate("el => getComputedStyle(el).display")
            slack_visibility = await slack_checkbox.evaluate("el => getComputedStyle(el).visibility")
            print(f"☑️  Slack checkbox computed styles - display: {slack_display}, visibility: {slack_visibility}")
            
            # Take a screenshot
            await page.screenshot(path="debug_schedule.png")
            print("📸 Screenshot saved as debug_schedule.png")
            
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
    asyncio.run(debug_schedule_form())
