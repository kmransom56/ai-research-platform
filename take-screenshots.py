#!/usr/bin/env python3
"""
Take screenshots of all running web interfaces
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def take_screenshots():
    """Take screenshots of all running interfaces"""
    
    # Create screenshots directory
    os.makedirs("images/screenshots", exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Set viewport for consistent screenshots
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        screenshots = [
            {
                "url": "http://localhost:11040",
                "filename": "images/screenshots/main-dashboard.png",
                "title": "Main Dashboard Interface"
            },
            {
                "url": "http://localhost:11032", 
                "filename": "images/screenshots/restaurant-voice.png",
                "title": "Restaurant Voice Interface"
            },
            {
                "url": "http://localhost:11031",
                "filename": "images/screenshots/it-voice.png", 
                "title": "IT Voice Interface"
            },
            {
                "url": "http://localhost:11050",
                "filename": "images/screenshots/network-topology.png",
                "title": "Network Topology Dashboard"
            },
            {
                "url": "http://localhost:7474",
                "filename": "images/screenshots/neo4j-browser.png",
                "title": "Neo4j Database Browser"
            }
        ]
        
        for screenshot in screenshots:
            try:
                print(f"📸 Taking screenshot of {screenshot['title']}...")
                
                # Navigate to page
                await page.goto(screenshot["url"], wait_until="networkidle", timeout=10000)
                
                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)
                
                # Take screenshot
                await page.screenshot(
                    path=screenshot["filename"],
                    full_page=True
                )
                
                print(f"✅ Screenshot saved: {screenshot['filename']}")
                
            except Exception as e:
                print(f"❌ Failed to screenshot {screenshot['title']}: {e}")
                continue
        
        await browser.close()
        
        print("🎯 All screenshots completed!")

if __name__ == "__main__":
    asyncio.run(take_screenshots())