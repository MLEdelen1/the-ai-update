#!/usr/bin/env python3
import json
import sys
import html
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.x_api import XAPIClient
from src.x_runtime import drafts_file, logs_dir, cookie_file


REQUIRED_KEYS = ("api_key", "api_secret", "access_token", "access_token_secret")


def load_first_draft() -> str:
    path = drafts_file()
    if not path.exists():
        raise FileNotFoundError(f"Draft file missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    tweets = payload.get("tweets") or []
    for item in tweets:
        draft = (item or {}).get("draft")
        if isinstance(draft, str) and draft.strip():
            cleaned = draft.strip()
            # Normalize HTML entities from content pipeline (e.g., &#8217; / &amp;#8217;)
            cleaned = html.unescape(html.unescape(cleaned))
            return cleaned
    raise ValueError("No non-empty draft found in data/drafts/latest_batch.json")


def main() -> int:
    log_path = logs_dir() / "x_post.log"
    tweet = load_first_draft()

    client = XAPIClient()
    has_api = all(client.config.get(k) for k in REQUIRED_KEYS)

    if has_api:
        result = client.post_tweet(tweet)
        log_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        if result.get("success"):
            print("PASS: Tweet posted via X API.")
            return 0
        print(f"FAIL: X API post failed: {result.get('error')} (status={result.get('status')})")
        return 1

    if cookie_file().exists():
        try:
            from scripts.post_with_cookies import post_with_cookies
            post_with_cookies(tweet)
            log_path.write_text(json.dumps({"success": True, "mode": "cookies"}, indent=2), encoding="utf-8")
            print("PASS: Tweet posted via cookie mode.")
            return 0
        except Exception as exc:
            log_path.write_text(json.dumps({"success": False, "mode": "cookies", "error": str(exc)}, indent=2), encoding="utf-8")
            print(f"FAIL: Cookie post failed: {exc}")
            return 1

    print("FAIL: No X credentials found. Configure env vars, ~/.clawdbot/secrets/x-api.json, or config/x_cookies.json")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
