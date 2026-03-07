import json
import time
import random
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DRAFT_FILE = PROJECT_ROOT / "data" / "drafts" / "latest_batch.json"
COOKIE_FILE = PROJECT_ROOT / "config" / "x_cookies.json"
LOGS_DIR = PROJECT_ROOT / "logs"


def human_type(page, selector, text):
    for char in text:
        page.type(selector, char, delay=random.randint(30, 100))


def _load_first_draft() -> str:
    if not DRAFT_FILE.exists():
        raise FileNotFoundError(f"Draft file missing: {DRAFT_FILE}")

    drafts = json.loads(DRAFT_FILE.read_text(encoding="utf-8"))
    tweets = drafts.get("tweets") or []
    for item in tweets:
        draft = (item or {}).get("draft")
        if isinstance(draft, str) and draft.strip():
            return draft.strip()
    raise ValueError("No non-empty tweet draft found in data/drafts/latest_batch.json")


def post_with_cookies(tweet_text: str | None = None):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if not COOKIE_FILE.exists():
        raise FileNotFoundError(
            f"Cookie file missing: {COOKIE_FILE}. "
            "Create it with scripts/x_login.py or place exported cookies there."
        )

    if not tweet_text:
        tweet_text = _load_first_draft()

    print("[DEBUG] Starting Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )

        cookies = json.loads(COOKIE_FILE.read_text(encoding="utf-8"))

        clean_cookies = []
        for c in cookies:
            s_site = c.get("sameSite", "None")
            if str(s_site).lower() == "no_restriction":
                s_site = "None"
            else:
                s_site = str(s_site).capitalize()
            clean_cookies.append({**c, "sameSite": s_site})
        context.add_cookies(clean_cookies)

        print(f"[DEBUG] {len(cookies)} cookies injected.")

        page = context.new_page()

        print("[DEBUG] Navigating to X Home...")
        try:
            page.goto("https://mobile.x.com/home", wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"[DEBUG] Navigation timeout/error: {e}")

        time.sleep(5)
        page.screenshot(path=str(LOGS_DIR / "check_home.png"))

        if "login" in page.url:
            browser.close()
            raise RuntimeError(f"Cookie auth failed, still on login page: {page.url}")

        print("[DEBUG] Navigating to Post Compose...")
        page.goto("https://mobile.x.com/compose/tweet", wait_until="domcontentloaded")
        time.sleep(3)

        print("[DEBUG] Entering Tweet Text...")
        editor = '[data-testid="tweetTextarea_0"]'
        page.wait_for_selector(editor, timeout=10000)
        page.click(editor)
        page.fill(editor, tweet_text)
        page.keyboard.press(" ")
        page.keyboard.press("Backspace")
        time.sleep(2)

        print("[DEBUG] Clicking Post Button...")
        post_btn = '[data-testid="tweetButton"], [data-testid="tweetButtonInline"]'
        page.click(post_btn, force=True)

        time.sleep(5)
        print(f"[DEBUG] Final URL: {page.url}")
        page.screenshot(path=str(LOGS_DIR / "final_verify.png"))

        browser.close()
        print("[DEBUG] Success.")


if __name__ == "__main__":
    post_with_cookies()
