#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPORTS_DIR = Path("/a0/usr/projects/x-manage/data/reports")
CACHE_DIR = Path("/a0/usr/projects/x-manage/data/news_cache")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_weekly_summary():
    latest_scan = CACHE_DIR / "latest_scan.json"
    if not latest_scan.exists(): return
    
    stories = json.loads(latest_scan.read_text())
    
    report_content = f"# 🧠 The AI Update: Intelligence Report\n"
    report_content += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    report_content += "## 🏢 AI in the Workplace\n"
    
    # Filtering and summarizing for business
    for s in stories[:10]:
        if "business" in s.get("summary", "").lower() or "enterprise" in s.get("summary", "").lower():
            report_content += f"### {s['title']}\n- **Source:** {s['source']}\n- **Insight:** {s['summary'][:200]}...\n- **Action:** [Read Full Story]({s['url']})\n\n"

    report_content += "## 🛠️ Practical AI for Regular People\n"
    for s in stories[:10]:
        if "free" in s.get("summary", "").lower() or "tool" in s.get("summary", "").lower():
            report_content += f"### {s['title']}\n- **Source:** {s['source']}\n- **Value:** Why this matters for non-technical users...\n- **Link:** {s['url']}\n\n"

    report_path = REPORTS_DIR / f"report_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.write_text(report_content)
    print(f"Weekly Report generated at {report_path}")

if __name__ == "__main__":
    generate_weekly_summary()
