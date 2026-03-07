#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.topic_filter import briefing_is_ai, is_ai_topic_strict
from src.x_api import XAPIClient

ARTICLES_DIR = PROJECT_ROOT / "data" / "research" / "briefings_2026_02"
POSTED_FILE = PROJECT_ROOT / "data" / "posted" / "x_posted_articles.json"


def purge_briefings() -> dict:
    removed = []
    kept = 0
    if not ARTICLES_DIR.exists():
        return {"removed": removed, "kept": kept}

    for md in ARTICLES_DIR.glob("briefing_*.md"):
        if briefing_is_ai(md):
            kept += 1
            continue
        removed.append(md.name)
        md.unlink(missing_ok=True)

    return {"removed": removed, "kept": kept}


def purge_x_posts(delete_remote: bool = True) -> dict:
    if not POSTED_FILE.exists():
        return {"deleted_remote": [], "removed_state": [], "kept_state": 0, "errors": []}

    payload = json.loads(POSTED_FILE.read_text(encoding="utf-8"))
    posted = payload.get("posted", []) if isinstance(payload, dict) else []

    client = XAPIClient()
    can_delete = delete_remote and client.is_configured()

    kept_rows = []
    removed_state = []
    deleted_remote = []
    errors = []

    for row in posted:
        title = (row or {}).get("title", "")
        url = (row or {}).get("url", "")
        ai = is_ai_topic_strict(title=title, summary=url)
        if ai:
            kept_rows.append(row)
            continue

        removed_state.append({"title": title, "url": url, "tweet_id": (row or {}).get("tweet_id")})
        tweet_id = (row or {}).get("tweet_id")
        if can_delete and tweet_id:
            try:
                res = client.delete_tweet(str(tweet_id))
                if res.get("success"):
                    deleted_remote.append(str(tweet_id))
                else:
                    errors.append({"tweet_id": str(tweet_id), "error": res})
            except Exception as exc:
                errors.append({"tweet_id": str(tweet_id), "error": str(exc)})

    payload["posted"] = kept_rows
    POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    POSTED_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {
        "deleted_remote": deleted_remote,
        "removed_state": removed_state,
        "kept_state": len(kept_rows),
        "errors": errors,
    }


def main() -> int:
    brief = purge_briefings()
    posts = purge_x_posts(delete_remote=True)

    summary = {
        "briefings_removed": len(brief["removed"]),
        "briefings_kept": brief["kept"],
        "state_rows_removed": len(posts["removed_state"]),
        "state_rows_kept": posts["kept_state"],
        "remote_tweets_deleted": len(posts["deleted_remote"]),
        "delete_errors": posts["errors"],
        "removed_briefings": brief["removed"],
        "removed_state_rows": posts["removed_state"],
    }
    print(json.dumps(summary, indent=2))
    return 0 if not posts["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
