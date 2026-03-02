
import json
import time
from playwright.sync_api import sync_playwright

def run_engagement():
    print("[SOCIAL] Starting Autonomous Engagement Session...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Load existing X cookies
        with open('/a0/usr/projects/x-manage/config/x_cookies.json', 'r') as f:
            cookies = json.load(f)
            context.add_cookies(cookies)

        page = context.new_page()

        # 1. Check Notifications
        print("[SOCIAL] Checking Notifications...")
        page.goto("https://x.com/notifications")
        time.sleep(5)
        page.screenshot(path="/a0/usr/projects/x-manage/logs/notifications_check.png")

        # 2. Check Mentions
        print("[SOCIAL] Checking Mentions...")
        page.goto("https://x.com/mentions")
        time.sleep(5)
        page.screenshot(path="/a0/usr/projects/x-manage/logs/mentions_check.png")

        print("[SOCIAL] Engagement scan complete. Reviewing logs for response drafting...")
        browser.close()

if __name__ == '__main__':
    try:
        run_engagement()
    except Exception as e:
        print(f"Engagement Failed: {e}")
