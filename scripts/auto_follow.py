
from playwright.sync_api import sync_playwright
import json
import time
import re

ACCOUNTS = [
    'OpenAI', 'AnthropicAI', 'GoogleDeepMind', 'DeepSeek_AI', 'sama', 
    'rowancheung', 'SmokeAwayyy', 'bindureddy', 'AndrewYNg', 'karpathy'
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        with open('/a0/usr/projects/x-manage/config/x_cookies.json', 'r') as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
    except Exception as e:
        print(f"Could not load cookies: {e}")

    page = context.new_page()
    followed = 0

    for account in ACCOUNTS:
        try:
            print(f"Checking @{account}...")
            page.goto(f"https://x.com/{account}", timeout=30000)
            page.wait_for_selector('[data-testid="primaryColumn"]', timeout=15000)
            time.sleep(3)

            # Find a button with exact text "Follow"
            follow_btn = page.locator('button[data-testid$="-follow"]').first
            if follow_btn.count() == 0:
                follow_btn = page.get_by_role("button", name=re.compile(r"^Follow( @.*)?$")).first

            if follow_btn.count() > 0 and follow_btn.is_visible():
                follow_btn.click()
                print(f"[+] Successfully followed @{account}")
                followed += 1
                time.sleep(2)
            else:
                print(f"[-] Already following or button hidden for @{account}")
        except Exception as e:
            print(f"[!] Skipped {account} due to error: {e}")

    print(f"\nTotal successfully followed this run: {followed}")
    browser.close()
