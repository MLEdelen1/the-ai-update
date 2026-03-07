#!/usr/bin/env python3
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.x_runtime import drafts_file, cookie_file, x_api_local_secret_file

REQUIRED_ENV = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]


def _check_draft():
    path = drafts_file()
    if not path.exists():
        return False, f"Missing draft file: {path}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        tweets = payload.get("tweets") or []
        has_draft = any(isinstance((t or {}).get("draft"), str) and (t or {}).get("draft").strip() for t in tweets)
        if has_draft:
            return True, f"Draft ready: {path}"
        return False, f"No non-empty drafts in: {path}"
    except Exception as exc:
        return False, f"Draft JSON invalid: {exc}"


def _check_env_api():
    missing = [k for k in REQUIRED_ENV if not __import__("os").getenv(k)]
    if not missing:
        return True, "API creds from env vars"
    return False, f"Env API creds missing: {', '.join(missing)}"


def _check_local_api_file():
    path = x_api_local_secret_file()
    if not path.exists():
        return False, f"Local API file not found: {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        keys = ["api_key", "api_secret", "access_token", "access_token_secret"]
        if all(data.get(k) for k in keys):
            return True, f"API creds from local file: {path}"
        return False, f"Local API file missing required keys: {path}"
    except Exception as exc:
        return False, f"Local API file invalid JSON: {exc}"


def _check_cookie_file():
    path = cookie_file()
    if not path.exists():
        return False, f"Cookie file not found: {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list) and len(data) > 0:
            return True, f"Cookie mode ready: {path}"
        return False, f"Cookie file empty/invalid list: {path}"
    except Exception as exc:
        return False, f"Cookie file invalid JSON: {exc}"


def main() -> int:
    checks = []
    draft_ok, draft_msg = _check_draft()
    checks.append((draft_ok, draft_msg))

    env_ok, env_msg = _check_env_api()
    file_ok, file_msg = _check_local_api_file()
    cookie_ok, cookie_msg = _check_cookie_file()

    checks.extend([(env_ok, env_msg), (file_ok, file_msg), (cookie_ok, cookie_msg)])

    auth_ready = env_ok or file_ok or cookie_ok
    overall_ok = draft_ok and auth_ready

    print("X Readiness Check")
    print("=" * 40)
    for ok, msg in checks:
        print(("PASS" if ok else "FAIL") + ": " + msg)

    if not auth_ready:
        print("ACTION: Provide one auth mode: env vars, ~/.clawdbot/secrets/x-api.json, or config/x_cookies.json")

    print("RESULT: " + ("PASS" if overall_ok else "FAIL"))
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
