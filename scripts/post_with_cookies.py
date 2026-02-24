
import json
import time
import random
import os
from playwright.sync_api import sync_playwright

def human_type(page, selector, text):
    for char in text:
        page.type(selector, char, delay=random.randint(30, 100))

def post_with_cookies():
    print('[DEBUG] Starting Playwright...')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )

        with open('/a0/usr/projects/x-manage/config/x_cookies.json', 'r') as f:
            cookies = json.load(f)

        # Clean and inject cookies to handle compatibility issues
        clean_cookies = []
        for c in cookies:
            s_site = c.get('sameSite', 'None')
            if s_site.lower() == 'no_restriction': s_site = 'None'
            else: s_site = s_site.capitalize()
            clean_cookies.append({**c, 'sameSite': s_site})
        context.add_cookies(clean_cookies)

        print(f'[DEBUG] {len(cookies)} cookies injected.')

        page = context.new_page()

        print('[DEBUG] Navigating to X Home...')
        try:
            page.goto('https://mobile.x.com/home', wait_until='domcontentloaded', timeout=45000)
        except Exception as e:
            print(f'[DEBUG] Navigation timeout/error: {e}')

        time.sleep(5)
        page.screenshot(path='/a0/usr/projects/x-manage/logs/check_home.png')

        if 'login' in page.url:
            print(f'[DEBUG] FAILED: Still on login page: {page.url}')
            browser.close()
            return

        print('[DEBUG] Navigating to Post Compose...')
        page.goto('https://mobile.x.com/compose/tweet', wait_until='domcontentloaded')
        time.sleep(3)

        # Load draft
        with open('/a0/usr/projects/x-manage/data/drafts/latest_batch.json', 'r') as f:
            drafts = json.load(f)
        if not drafts.get("tweets") or len(drafts["tweets"]) == 0:
            print("[DEBUG] No tweets to post. Exiting.")
            browser.close()
            return
        tweet_text = drafts["tweets"][0]["draft"]

        print('[DEBUG] Entering Tweet Text...')
        editor = '[data-testid="tweetTextarea_0"]'
        page.wait_for_selector(editor, timeout=10000)
        page.click(editor)
        page.fill(editor, tweet_text)
        page.keyboard.press(" ")
        page.keyboard.press("Backspace")
        time.sleep(2)

        print('[DEBUG] Clicking Post Button...')
        post_btn = '[data-testid="tweetButton"], [data-testid="tweetButtonInline"]'
        page.click(post_btn)

        time.sleep(5)
        print(f'[DEBUG] Final URL: {page.url}')
        page.screenshot(path='/a0/usr/projects/x-manage/logs/final_verify.png')

        browser.close()
        print('[DEBUG] Success.')

if __name__ == "__main__":
    post_with_cookies()
