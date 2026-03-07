#!/usr/bin/env python3
import hashlib
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))
from runtime_paths import python_executable  # noqa: E402
from topic_filter import is_ai_topic_strict  # noqa: E402

DATA_DIR = PROJECT_ROOT / "data"
CACHE_FILE = DATA_DIR / "news_cache" / "latest_scan.json"
RESEARCH_DIR = DATA_DIR / "research" / "briefings_2026_02"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"

PREFERRED_SOURCES = ["julian_goldie_seo_yt", "ai_revolution_yt", "ai_search_yt"]
PREFERRED_CHANNELS = {
    "julian_goldie_seo_yt": "UCGpsgNbzdF7BECCVbB1COHw",
    "ai_revolution_yt": "UC5LTm52VaiV-5Q3C-txWVGQ",
    "ai_search_yt": "UCIgnGlGkVRhd4qNFcEwLL4A",
}
BANNED_TERMS = {
    "government", "federal", "politics", "policy", "permit", "biden", "trump", "senate", "congress",
    "president", "court", "election", "war", "military", "crime", "murder", "suicide", "adult", "nsfw"
}


def ensure_dirs():
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def enforce_english(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\u31f0-\u31ff\uac00-\ud7af]+", "", text)


def _make_id(text: str) -> str:
    return hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()[:12]


def scan_news():
    subprocess.run([python_executable(), str(SRC_DIR / "news_scanner.py")], check=True, cwd=str(PROJECT_ROOT))


def load_stories():
    if not CACHE_FILE.exists():
        return []
    return json.loads(CACHE_FILE.read_text(encoding="utf-8"))


def parse_ts(story):
    raw = story.get("timestamp") or ""
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc) - timedelta(days=365)


def story_priority(story):
    src = (story.get("source") or "").lower()
    ts = parse_ts(story)
    source_rank = 2
    if src in PREFERRED_SOURCES:
        source_rank = 0
    elif src.endswith("_yt"):
        source_rank = 1
    age_rank = -int(ts.timestamp())
    return (source_rank, age_rank)


def _source_allows(story):
    title = story.get("title") or ""
    summary = story.get("summary") or ""
    text = (title + " " + summary).lower()
    if any(term in text for term in BANNED_TERMS):
        return False
    if not is_ai_topic_strict(title=title, summary=summary):
        return False
    return bool(story.get("url"))


def fetch_preferred_youtube_items(max_per_channel=6):
    out = []
    now = datetime.now(timezone.utc)
    for source, channel_id in PREFERRED_CHANNELS.items():
        channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
        cmd = [
            python_executable(), "-m", "yt_dlp", "--flat-playlist", "--playlist-end", str(max_per_channel),
            "--dump-single-json", channel_url,
        ]
        try:
            raw = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, cwd=str(PROJECT_ROOT))
            data = json.loads(raw)
        except Exception:
            continue

        for e in data.get("entries", []) or []:
            vid = e.get("id")
            if not vid:
                continue
            ts = now
            up = e.get("upload_date")
            if up and len(up) == 8:
                try:
                    ts = datetime.strptime(up, "%Y%m%d").replace(tzinfo=timezone.utc)
                except Exception:
                    ts = now
            out.append({
                "source": source,
                "title": e.get("title") or "Untitled video",
                "url": f"https://www.youtube.com/watch?v={vid}",
                "summary": (e.get("description") or "")[:1000],
                "timestamp": ts.isoformat(),
                "id": _make_id((e.get("title") or "") + vid),
            })
    return out


def select_stories(stories, max_count=8):
    pool = [s for s in stories if _source_allows(s)]

    if len(pool) < max_count:
        fallback = fetch_preferred_youtube_items(max_per_channel=max(4, max_count))
        pool.extend([s for s in fallback if _source_allows(s)])

    pool.sort(key=story_priority)
    seen = set()
    selected = []
    for s in pool:
        sid = s.get("id") or (s.get("title", "") + s.get("url", ""))
        if sid in seen:
            continue
        seen.add(sid)
        selected.append(s)
        if len(selected) >= max_count:
            break
    return selected


def video_id_from_url(url: str):
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    q = parse_qs(urlparse(url).query)
    vals = q.get("v") or []
    return vals[0] if vals else None


def extract_transcript_yt_dlp(video_url: str):
    vid = video_id_from_url(video_url)
    if not vid:
        return None
    temp_dir = PROJECT_ROOT / "temp" / "transcripts"
    temp_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(temp_dir / f"{vid}.%(ext)s")
    cmd = [
        python_executable(), "-m", "yt_dlp", "--skip-download", "--write-auto-subs", "--write-subs",
        "--sub-langs", "en.*", "--convert-subs", "vtt", "-o", outtmpl, video_url
    ]
    try:
        subprocess.run(cmd, check=True, cwd=str(PROJECT_ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return None

    vtts = list(temp_dir.glob(f"{vid}*.vtt"))
    if not vtts:
        return None

    raw = vtts[0].read_text(encoding="utf-8", errors="ignore")
    lines = []
    for line in raw.splitlines():
        l = line.strip()
        if not l or l == "WEBVTT" or "-->" in l or l.isdigit() or l.startswith("Kind:") or l.startswith("Language:"):
            continue
        l = re.sub(r"<[^>]+>", "", l)
        if l:
            lines.append(l)
    text = re.sub(r"\s+", " ", " ".join(lines)).strip()
    return text[:12000] if text else None


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    cfg = PROJECT_ROOT / "config" / "gemini_keys.json"
    if not key and cfg.exists():
        try:
            key = json.loads(cfg.read_text(encoding="utf-8")).get("gemini_api_key")
        except Exception:
            key = None
    return key


import time

def generate_article(story, api_key=None):
    title = story.get("title", "Untitled")
    summary = story.get("summary", "")
    url = story.get("url", "")
    source = story.get("source", "")

    transcript = None
    if "youtube.com" in url or "youtu.be" in url:
        transcript = extract_transcript_yt_dlp(url)

    grounding = f"Source URL: {url}\nSource: {source}\n"
    if transcript:
        cleaned_transcript = transcript
        for term in BANNED_TERMS:
            cleaned_transcript = re.sub(rf"\b{re.escape(term)}\b", "", cleaned_transcript, flags=re.IGNORECASE)
        grounding += f"Transcript excerpt: {cleaned_transcript[:6000]}\n"
    else:
        grounding += f"Summary excerpt: {summary[:1000]}\n"

    # Step 1: Research with OpenAI Codex 5.3
    research_prompt = (
        "You are an expert AI technical researcher. "
        "Analyze the following story, summary, or transcript and extract the absolute most important technical facts, product launches, breakthroughs, and actionable insights. "
        "Distill this into a dense, highly factual brief answering: 1. What changed/launched? 2. Why does it matter to developers/creators? 3. What should they do next? "
        "Stay completely factual and grounded.\n\n"
        f"Title: {title}\n{grounding}"
    )

    research_notes = ""
    try:
        endpoint = "http://127.0.0.1:18789/v1/chat/completions"
        headers = {
            "Authorization": "Bearer 77ccd923284fcd42f76fab03762cf4ead1749f64e08cc068",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai-codex/gpt-5.3-codex",
            "messages": [{"role": "user", "content": research_prompt}],
            "temperature": 0.2
        }
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            research_notes = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Research failed: {e}")

    if not research_notes:
        research_notes = grounding

    # Step 2: Write with Gemini 3.1 Pro Preview
    write_prompt = (
        "Write a highly engaging, SEO-optimized markdown article for an AI updates website based on these research notes. "
        "The tone should be dopamine-inducing, fast-paced, and wildly exciting, keeping readers hooked on the bleeding edge of AI. "
        "Use high-impact phrasing and strong hooks. Include natural SEO keywords related to AI breakthroughs. "
        "Stay factual to the research but make it thrilling. "
        "Include these exact section headings in this order:\n"
        "## What changed\n## Why it matters\n## What to do next\n"
        "Include at least one explicit source link in markdown format.\n\n"
        f"Research Notes:\n{research_notes}\n\n"
        f"Source Link to include: {url}"
    )

    body = None
    if api_key:
        endpoint_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={api_key}"
        payload_gemini = {"contents": [{"parts": [{"text": write_prompt}]}]}
        for attempt in range(3):
            try:
                resp = requests.post(endpoint_gemini, json=payload_gemini, timeout=90)
                if resp.status_code == 200:
                    body = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    break
                elif resp.status_code == 429:
                    print(f"Rate limit hit on Gemini. Retrying in {15 * (attempt + 1)} seconds...")
                    time.sleep(15 * (attempt + 1))
                else:
                    print(f"Gemini failed with status: {resp.status_code}")
                    break
            except Exception as e:
                print(f"Exception during Gemini request: {e}")
                time.sleep(5)
    
    # Pace Gemini to stay under the 15 RPM limit safely
    time.sleep(6)

    if not body:
        base = transcript[:900] if transcript else summary
        body = (
            f"## What changed\n{base or 'A fresh AI update was published and reviewed from the source material.'}\n\n"
            f"Source: [{title}]({url})\n\n"
            "## Why it matters\n"
            "This affects near-term AI workflows, model/tool selection, and practical implementation decisions. "
            "It should be validated in a real use case before broad rollout.\n\n"
            "## What to do next\n"
            "Read the primary source, run a small pilot in one workflow, track quality and speed impact, and only scale if measurable gains hold."
        )

    body = enforce_english(body)
    if not body.lstrip().startswith("#"):
        body = f"# {title}\n\n" + body

    sid = story.get("id") or re.sub(r"[^a-z0-9]+", "_", title.lower())[:40]
    out_file = RESEARCH_DIR / f"briefing_{sid}.md"
    out_file.write_text(body, encoding="utf-8")

    return {"id": sid, "title": title, "source": source, "url": url, "transcript_used": bool(transcript), "file": str(out_file)}


def qa_article(item):
    text = Path(item["file"]).read_text(encoding="utf-8", errors="ignore")
    low = text.lower()
    reasons = []

    if "## what changed" not in low or "## why it matters" not in low or "## what to do next" not in low:
        reasons.append("missing required section headings")
    if "http://" not in low and "https://" not in low and "](" not in low:
        reasons.append("missing source link")
    wc = len(re.findall(r"\b\w+\b", text))
    if wc < 160:
        reasons.append("insufficient substance (<160 words)")
    banned_hits = 0
    for term in BANNED_TERMS:
        banned_hits += len(re.findall(rf"\\b{re.escape(term)}\\b", low))
    if banned_hits >= 3:
        reasons.append("contains banned topic")
    if not is_ai_topic_strict(title=item.get("title", ""), content=text):
        reasons.append("non-ai/off-topic article")

    return {"id": item["id"], "title": item["title"], "file": item["file"], "passed": not reasons, "reasons": reasons}


def rebuild_site():
    subprocess.run([python_executable(), str(SRC_DIR / "site_generator.py")], check=True, cwd=str(PROJECT_ROOT))


def run(max_count=8, workers=4):
    ensure_dirs()
    scan_news()
    stories = load_stories()
    selected = select_stories(stories, max_count=max_count)

    api_key = get_api_key()
    generated = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futures = [ex.submit(generate_article, s, api_key) for s in selected]
        for fut in as_completed(futures):
            generated.append(fut.result())

    qa_results = [qa_article(g) for g in generated]
    passed = [q for q in qa_results if q["passed"]]
    rejected = [q for q in qa_results if not q["passed"]]

    for q in rejected:
        p = Path(q["file"])
        if p.exists():
            p.unlink(missing_ok=True)

    rebuild_site()

    distribution = {
        "by_source": {},
        "transcript_first_count": 0,
        "selected_count": len(selected),
        "generated_count": len(generated),
        "qa_passed": len(passed),
        "published_count": len(passed),
        "rejected": [{"id": r["id"], "title": r["title"], "reasons": r["reasons"]} for r in rejected],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    for g in generated:
        distribution["by_source"][g["source"]] = distribution["by_source"].get(g["source"], 0) + 1
        if g["transcript_used"]:
            distribution["transcript_first_count"] += 1

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"multi_article_run_{stamp}.json"
    report_file.write_text(json.dumps(distribution, indent=2), encoding="utf-8")

    print(json.dumps({
        "report": str(report_file),
        "generated": len(generated),
        "qa_passed": len(passed),
        "published": len(passed),
        "rejected": distribution["rejected"],
    }, indent=2))
    return distribution, report_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run multi-article generation with parallel workers + QA.")
    parser.add_argument("--max-count", type=int, default=8)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    run(max_count=args.max_count, workers=args.workers)
