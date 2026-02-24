import os
import json
import time
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

def human_type(page, selector, text):
    for char in text:
        page.type(selector, char, delay=random.randint(50, 150))

def post_tweet(username, password, tweet_text):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth(page)

        print(f"Navigating to X login...")
        page.goto("https://x.com/i/flow/login")
        time.sleep(5)
        page.screenshot(path="/a0/usr/projects/x-manage/logs/step1_login_page.png")

        # Enter Username
        print("Entering username...")
        username_selector = 'input[autocomplete="username"]'
        page.wait_for_selector(username_selector)
        page.click(username_selector)
        human_type(page, username_selector, username)
        page.keyboard.press("Enter")
        time.sleep(5)
        page.screenshot(path="/a0/usr/projects/x-manage/logs/step2_after_username.png")

        # Check for password field or suspicious activity check
        if page.query_selector('input[name="password"]'):
            print("Entering password...")
            human_type(page, 'input[name="password"]', password)
            page.keyboard.press("Enter")
            time.sleep(7)
        else:
            # Handle unusual activity check if it appears
            if "unusual activity" in page.content().lower():
                 print("Unusual activity check detected. Manual intervention might be needed.")
            else:
                 print("Password field not found. Current URL:", page.url)
        
        page.screenshot(path="/a0/usr/projects/x-manage/logs/step3_after_login.png")

        # Navigate to compose
        print("Navigating to compose...")
        page.goto("https://x.com/compose/tweet")
        time.sleep(5)

        # Post Tweet
        print("Attempting to post tweet...")
        editor_selector = '.public-DraftEditor-content'
        page.wait_for_selector(editor_selector)
        page.click(editor_selector)
        human_type(page, editor_selector, tweet_text)
        time.sleep(2)
        
        page.screenshot(path="/a0/usr/projects/x-manage/logs/step4_before_post.png")

        print("Clicking Post button...")
        post_button = '[data-testid="tweetButton"]'
        page.click(post_button)
        time.sleep(5)
        
        page.screenshot(path="/a0/usr/projects/x-manage/logs/step5_final.png")
        print("Done. Final URL:", page.url)
        browser.close()

if __name__ == "__main__":
    with open('/a0/usr/projects/x-manage/config/twitter_credentials.json', 'r') as f:
        creds = json.load(f)
    
    # Using the credentials provided by the user in chat for the stealth poster
    username = "the_aiupdate"
    password = "1980Trek!@!"
    
    with open('/a0/usr/projects/x-manage/data/drafts/latest_batch.json', 'r') as f:
        drafts = json.load(f)
    
    tweet_text = drafts['tweets'][0]['draft']
    
    os.makedirs('/a0/usr/projects/x-manage/logs', exist_ok=True)
    post_tweet(username, password, tweet_text)
