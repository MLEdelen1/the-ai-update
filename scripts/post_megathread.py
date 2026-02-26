
import sys
import time
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

text_path = Path('/a0/usr/projects/x-manage/data/drafts/latest_megathread.txt')
text = text_path.read_text(encoding='utf-8')
parts = re.split(r'\n(?=\d+/)', text)
tweets = [p.strip() for p in parts if p.strip()]

print(f"Posting Megathread ({len(tweets)} parts)...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 1080}
    )
    try:
        with open('/a0/usr/projects/x-manage/config/x_cookies.json', 'r') as f:
            context.add_cookies(json.load(f))
    except Exception as e:
        print(f"Cookie error: {e}")

    page = context.new_page()
    page.goto("https://x.com/compose/tweet", timeout=60000)

    try:
        page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=20000)
        time.sleep(2)
    except Exception as e:
        print("Compose box not found. Cookies might be invalid or account locked.")
        page.screenshot(path="/a0/usr/projects/x-manage/logs/thread_error_3.png")
        browser.close()
        sys.exit(1)

    for i, tweet_text in enumerate(tweets):
        print(f"-> Typing tweet {i+1}...")
        textarea_selector = f'[data-testid="tweetTextarea_{i}"]'
        try:
            page.wait_for_selector(textarea_selector, timeout=10000)
            page.click(textarea_selector)
            page.keyboard.insert_text(tweet_text)
            time.sleep(2)
        except Exception as e:
            print(f"Error typing tweet {i+1}: {e}")
            browser.close()
            sys.exit(1)

        if i < len(tweets) - 1:
            print("   Clicking Add (+)...")
            page.click('[data-testid="addTweetButton"]')
            time.sleep(2)

    print("Submitting thread...")
    try:
        page.click('[data-testid="tweetButton"]')
        time.sleep(8)
        print("SUCCESS: Megathread is live.")
    except Exception as e:
        print(f"Error posting thread: {e}")
    browser.close()
