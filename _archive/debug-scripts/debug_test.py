#!/usr/bin/env python3
"""
Debug test to investigate UI visibility issues
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_ui_issues():
    """Debug UI visibility issues"""
    print("🔍 Debugging UI Issues")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in visible mode
        page = await browser.new_page()
        
        try:
            # Navigate to the page
            print("🌐 Navigating to frontend...")
            await page.goto("http://localhost:8081")
            await page.wait_for_load_state('networkidle')
            
            # Get page title
            title = await page.title()
            print(f"📄 Page title: {title}")
            
            # Check if login page is visible
            login_page = page.locator("#login-page")
            is_visible = await login_page.is_visible()
            print(f"👁️  Login page visible: {is_visible}")
            
            # Check login page classes
            login_page_classes = await login_page.get_attribute("class")
            print(f"🏷️  Login page classes: {login_page_classes}")
            
            # Check email input
            email_input = page.locator("#email-input")
            email_visible = await email_input.is_visible()
            email_enabled = await email_input.is_enabled()
            email_editable = await email_input.is_editable()
            print(f"📧 Email input - visible: {email_visible}, enabled: {email_enabled}, editable: {email_editable}")
            
            # Check email input classes and attributes
            email_classes = await email_input.get_attribute("class")
            email_style = await email_input.get_attribute("style")
            print(f"📧 Email input classes: {email_classes}")
            print(f"📧 Email input style: {email_style}")
            
            # Check if email input is in viewport
            try:
                email_in_viewport = await email_input.is_in_viewport()
                print(f"📧 Email input in viewport: {email_in_viewport}")
            except:
                print("📧 Email input in viewport: method not available")
            
            # Check computed styles
            email_display = await email_input.evaluate("el => getComputedStyle(el).display")
            email_visibility = await email_input.evaluate("el => getComputedStyle(el).visibility")
            email_opacity = await email_input.evaluate("el => getComputedStyle(el).opacity")
            print(f"📧 Email computed styles - display: {email_display}, visibility: {email_visibility}, opacity: {email_opacity}")
            
            # Check parent elements
            email_parent = email_input.locator("..")
            parent_visible = await email_parent.is_visible()
            parent_classes = await email_parent.get_attribute("class")
            print(f"👨‍👩‍👧‍👦 Email parent visible: {parent_visible}, classes: {parent_classes}")
            
            # Check form element
            form = page.locator("#login-form")
            form_visible = await form.is_visible()
            form_classes = await form.get_attribute("class")
            print(f"📝 Form visible: {form_visible}, classes: {form_classes}")
            
            # Check for JavaScript errors
            console_messages = []
            page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
            
            # Wait for JavaScript to load
            await page.wait_for_timeout(2000)
            
            # Check console messages
            if console_messages:
                print("🔍 Console messages:")
                for msg in console_messages:
                    print(f"  {msg}")
            else:
                print("🔍 No console messages")
            
            # Check if JavaScript is working by looking for the app object
            app_exists = await page.evaluate("typeof window.app !== 'undefined'")
            print(f"🔧 JavaScript app object exists: {app_exists}")
            
            # Try to manually trigger the login page display
            await page.evaluate("if (window.app) { window.app.showPage('login-page'); }")
            await page.wait_for_timeout(1000)
            
            # Check login page visibility again
            login_page_visible_after = await login_page.is_visible()
            login_page_classes_after = await login_page.get_attribute("class")
            print(f"👁️  Login page visible after manual trigger: {login_page_visible_after}")
            print(f"🏷️  Login page classes after manual trigger: {login_page_classes_after}")
            
            # Take a screenshot for visual debugging
            await page.screenshot(path="debug_screenshot.png")
            print("📸 Screenshot saved as debug_screenshot.png")
            
            # Wait a bit to see the page
            print("⏳ Waiting 5 seconds for visual inspection...")
            await page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"❌ Debug failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_ui_issues())
