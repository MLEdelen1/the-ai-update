#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

COOKIE_FILE = Path("/a0/usr/projects/x-manage/config/x_cookies.json")
SD = Path("/a0/usr/projects/x-manage/data")

async def login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled",
                  "--disable-dev-shm-usage", "--window-size=1920,1080"]
        )
        ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-US", timezone_id="America/Chicago",
        )
        await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await ctx.new_page()

        print("[1] Loading x.com...")
        await page.goto("https://x.com", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        print("    URL:", page.url)

        print("[2] Loading login page...")
        await page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)
        print("    URL:", page.url)
        await page.screenshot(path=str(SD / "s2_login.png"))

        print("[3] Looking for username field...")
        found = False
        for sel in ['input[autocomplete="username"]', 'input[name="text"]', 'input[type="text"]']:
            try:
                el = await page.wait_for_selector(sel, timeout=5000)
                if el:
                    await el.type("the_aiupdate", delay=50)
                    found = True
                    print("    Typed username via", sel)
                    break
            except:
                continue

        if not found:
            print("    ERROR: No username field!")
            body = await page.text_content("body")
            if body:
                print("    Body:", body[:300])
            await page.screenshot(path=str(SD / "s_error.png"))
            await browser.close()
            return False

        await asyncio.sleep(1)
        await page.screenshot(path=str(SD / "s3_user.png"))

        print("[4] Clicking Next...")
        try:
            btns = await page.query_selector_all("button")
            for b in btns:
                t = await b.text_content()
                if t and "next" in t.lower().strip():
                    await b.click()
                    print("    Clicked Next")
                    break
        except Exception as e:
            print("    Next button error:", e)

        await asyncio.sleep(3)
        await page.screenshot(path=str(SD / "s4_next.png"))

        print("[5] Looking for password field...")
        pw_found = False
        for sel in ['input[name="password"]', 'input[type="password"]']:
            try:
                el = await page.wait_for_selector(sel, timeout=5000)
                if el:
                    await el.type("1980Trek!@!", delay=50)
                    pw_found = True
                    print("    Password entered")
                    break
            except:
                continue

        if not pw_found:
            print("    No password field found")
            body = await page.text_content("body")
            if body:
                print("    Body:", body[:300])
            await page.screenshot(path=str(SD / "s_nopw.png"))
            await browser.close()
            return False

        await asyncio.sleep(1)

        print("[6] Clicking Log in...")
        try:
            btns = await page.query_selector_all("button")
            for b in btns:
                t = await b.text_content()
                if t and "log in" in t.lower().strip():
                    await b.click()
                    print("    Clicked Log in")
                    break
        except Exception as e:
            print("    Login button error:", e)

        await asyncio.sleep(6)
        await page.screenshot(path=str(SD / "s5_result.png"))
        print("    Final URL:", page.url)

        url = page.url
        if "home" in url or url.rstrip("/") == "https://x.com":
            cookies = await ctx.cookies()
            COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
            COOKIE_FILE.write_text(json.dumps(cookies, indent=2))
            print("\nLOGIN SUCCESS! Cookies saved.")
            await browser.close()
            return True
        else:
            print("\nLogin unclear. URL:", url)
            body = await page.text_content("body")
            if body:
                print("Body:", body[:300])
            await browser.close()
            return False

if __name__ == "__main__":
    result = asyncio.run(login())
    print("\nResult:", result)
