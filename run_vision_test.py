import asyncio
from playwright.async_api import async_playwright
import json

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Desktop
        context_desktop = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page_desktop = await context_desktop.new_page()
        
        console_errors = []
        page_errors = []
        page_desktop.on('console', lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == 'error' else None)
        page_desktop.on('pageerror', lambda err: page_errors.append(f"{err.name}: {err.message}"))
        
        try:
            print("Navigating to https://ads-fedu-vn.pages.dev ...")
            await page_desktop.goto("https://ads-fedu-vn.pages.dev", wait_until='networkidle')
            await page_desktop.evaluate('() => document.fonts.ready')
            await page_desktop.wait_for_timeout(2000)
            
            # Click Tab 2
            await page_desktop.evaluate("if(document.getElementById('btnTabVietnd')) document.getElementById('btnTabVietnd').click();")
            await page_desktop.wait_for_timeout(1000)
            
            await page_desktop.screenshot(path='vision_report_desktop.png')
            print("Desktop screenshot saved.")
            
            dom_report = await page_desktop.evaluate('''() => {
                const checks = {};
                checks.consoleErrors = window.__capturedErrors || [];
                const targets = document.querySelectorAll('h1, h2, h3, button, #kpiSpendVietnd, #kpiOffline, #kpiOnline, table');
                checks.elements = [...targets].map(el => {
                    return {
                        tag: el.tagName, id: el.id, classes: el.className,
                        text: el.textContent?.slice(0, 100).replace(/\\s+/g, ' ') || ''
                    };
                });
                return checks;
            }''')
            with open('dom_probe_desktop.json', 'w') as f:
                json.dump(dom_report, f, indent=2)
                
        except Exception as e:
            print(f"Error desktop: {e}")
            
        with open('js_errors.txt', 'w') as f:
            for e in page_errors + console_errors:
                f.write(e + "\\n")
        
        await browser.close()

asyncio.run(run())
