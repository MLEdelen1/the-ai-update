import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COOKIE_FILE = PROJECT_ROOT / 'config' / 'x_cookies.json'
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def run_engagement():
    print("[SOCIAL] Starting Autonomous Engagement Session...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            context.add_cookies(cookies)

        page = context.new_page()

        print("[SOCIAL] Checking Notifications...")
        page.goto("https://x.com/notifications")
        time.sleep(5)
        page.screenshot(path=str(LOGS_DIR / 'notifications_check.png'))

        print("[SOCIAL] Checking Mentions...")
        page.goto("https://x.com/mentions")
        time.sleep(5)
        page.screenshot(path=str(LOGS_DIR / 'mentions_check.png'))

        print("[SOCIAL] Engagement scan complete. Reviewing logs for response drafting...")
        browser.close()


if __name__ == '__main__':
    try:
        run_engagement()
    except Exception as e:
        print(f"Engagement Failed: {e}")
