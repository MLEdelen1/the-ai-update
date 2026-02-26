
import sys
import time
import json
import re
from playwright.sync_api import sync_playwright

ACCOUNTS = [
    'OpenAI', 'AnthropicAI', 'GoogleDeepMind', 'DeepSeek_AI', 'sama', 
    'rowancheung', 'SmokeAwayyy', 'bindureddy', 'AndrewYNg', 'karpathy'
]

print("\nStarting Slow Auto-Follow Sequence...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    try:
        with open('/a0/usr/projects/x-manage/config/x_cookies.json', 'r') as f:
            context.add_cookies(json.load(f))
    except Exception as e:
        print(f"Cookie error: {e}")

    page = context.new_page()
    followed = 0

    for account in ACCOUNTS:
        print(f"Checking @{account}...")
        try:
            page.goto(f"https://x.com/{account}", timeout=30000)
            page.wait_for_selector('[data-testid="primaryColumn"]', timeout=15000)
            time.sleep(3)

            follow_btn = page.locator('button[data-testid$="-follow"]').first
            if follow_btn.count() == 0:
                follow_btn = page.get_by_role("button", name=re.compile(r"^Follow( @.*)?$")).first

            if follow_btn.count() > 0 and follow_btn.is_visible():
                follow_btn.click()
                print(f"[+] Followed @{account}. Waiting 15 seconds to avoid bot detection...")
                time.sleep(15)  # 15 SECOND DELAY
                followed += 1
            else:
                print(f"[-] Already following or button hidden for @{account}")
        except Exception as e:
            print(f"[!] Error on {account}: Timeout/Page Load Failed.")

    print(f"\nSlow Auto-Follow Complete. Total new follows: {followed}")
    browser.close()
