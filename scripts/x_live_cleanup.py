#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.topic_filter import is_ai_topic_strict
from src.x_api import XAPIClient

POSTED_FILE = PROJECT_ROOT / "data" / "posted" / "x_posted_articles.json"
REPORT_FILE = PROJECT_ROOT / "data" / "reports" / "x_live_cleanup_latest.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_retry_after(resp_json: dict) -> int | None:
    try:
        detail = ((resp_json or {}).get("data") or {}).get("detail", "")
        if isinstance(detail, str):
            # ex: "Too Many Requests"
            return None
    except Exception:
        pass
    return None


def get_all_user_tweets(client: XAPIClient, user_id: str, max_pages: int = 10) -> list[dict]:
    tweets = []
    seen = set()
    token = None
    pages = 0

    while pages < max_pages:
        pages += 1
        url = f"{client.BASE_URL}/users/{user_id}/tweets"
        params = {
            "max_results": "100",
            "exclude": "retweets,replies",
            "tweet.fields": "created_at,text",
        }
        if token:
            params["pagination_token"] = token

        headers = client._get_bearer_headers()
        resp = client.client.get(url, params=params, headers=headers)
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}

        if resp.status_code != 200:
            raise RuntimeError(f"timeline fetch failed status={resp.status_code} body={data}")

        chunk = data.get("data") or []
        for t in chunk:
            tid = str(t.get("id"))
            if tid and tid not in seen:
                seen.add(tid)
                tweets.append(t)

        token = ((data.get("meta") or {}).get("next_token"))
        if not token or not chunk:
            break

    return tweets


def classify_non_ai(tweets: list[dict]) -> tuple[list[dict], list[dict]]:
    keep, flagged = [], []
    for t in tweets:
        text = (t.get("text") or "").strip()
        ok = is_ai_topic_strict(title=text, summary=text, content=text)
        rec = {
            "id": str(t.get("id")),
            "created_at": t.get("created_at"),
            "text": text,
            "decision": "keep_ai" if ok else "remove_non_ai",
        }
        if ok:
            keep.append(rec)
        else:
            flagged.append(rec)
    return keep, flagged


def delete_with_backoff(client: XAPIClient, ids: list[str], max_seconds: int = 1200) -> tuple[list[str], list[dict], list[str], int]:
    start = time.time()
    queue = list(dict.fromkeys(ids))
    deleted: list[str] = []
    failed_errors: list[dict] = []
    attempts = 0

    backoff = 20
    while queue and (time.time() - start) < max_seconds:
        tid = queue.pop(0)
        attempts += 1
        res = client.delete_tweet(tid)
        if res.get("success"):
            deleted.append(tid)
            backoff = 20
            continue

        status = None
        try:
            status = (((res or {}).get("data") or {}).get("status"))
        except Exception:
            status = None

        is_429 = status == 429
        if is_429:
            queue.append(tid)
            sleep_for = min(backoff, 180)
            time.sleep(sleep_for)
            backoff = min(backoff * 2, 180)
            continue

        failed_errors.append({"id": tid, "error": res})

    failed_remaining_ids = queue[:]
    return deleted, failed_errors, failed_remaining_ids, attempts


def update_state_remove_ids(ids_to_remove: set[str]) -> tuple[int, int]:
    if not POSTED_FILE.exists():
        return 0, 0
    try:
        state = json.loads(POSTED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return 0, 0

    rows = state.get("posted", []) if isinstance(state, dict) else []
    before = len(rows)
    kept = [r for r in rows if str((r or {}).get("tweet_id") or "") not in ids_to_remove]
    removed = before - len(kept)
    state["posted"] = kept
    POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    POSTED_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return before, removed


def main() -> int:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    client = XAPIClient()
    if not client.is_configured():
        payload = {
            "ok": False,
            "error": "X API credentials missing",
            "generated_at": now_iso(),
        }
        REPORT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2

    me = client.get_me()
    if "data" not in me:
        payload = {
            "ok": False,
            "error": "Failed to resolve authenticated user",
            "me": me,
            "generated_at": now_iso(),
        }
        REPORT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 3

    user = me["data"]
    tweets = get_all_user_tweets(client, user_id=str(user["id"]), max_pages=10)
    kept, flagged = classify_non_ai(tweets)

    flagged_ids = [r["id"] for r in flagged if r.get("id")]
    deleted_ids, delete_errors, failed_remaining_ids, delete_attempts = delete_with_backoff(client, flagged_ids, max_seconds=1200)

    ids_to_remove_from_state = set(flagged_ids) | set(deleted_ids)
    state_before, state_removed = update_state_remove_ids(ids_to_remove_from_state)

    payload = {
        "ok": True,
        "user": {
            "id": str(user.get("id")),
            "name": user.get("name"),
            "username": user.get("username"),
        },
        "scanned": len(tweets),
        "flagged": len(flagged),
        "deleted": len(deleted_ids),
        "failed_remaining": failed_remaining_ids,
        "failed_errors": delete_errors,
        "delete_attempts": delete_attempts,
        "state": {
            "file": str(POSTED_FILE.relative_to(PROJECT_ROOT)),
            "rows_before": state_before,
            "rows_removed": state_removed,
            "rows_after": max(state_before - state_removed, 0),
        },
        "flagged_rows": flagged,
        "kept_rows": kept,
        "generated_at": now_iso(),
    }

    REPORT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "scanned": payload["scanned"],
        "flagged": payload["flagged"],
        "deleted": payload["deleted"],
        "failed_remaining": len(payload["failed_remaining"]),
        "report": str(REPORT_FILE),
    }, indent=2))
    return 0 if not failed_remaining_ids else 4


if __name__ == "__main__":
    raise SystemExit(main())
