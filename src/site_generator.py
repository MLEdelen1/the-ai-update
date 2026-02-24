#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
TEMPLATE_PATH = PROJECT_ROOT / "website/templates/master.html"
OUTPUT_PATH = PROJECT_ROOT / "website/index.html"

# Data Paths
NEWS_DATA = PROJECT_ROOT / "data/news_cache/latest_scan.json"
TOOLS_DATA = PROJECT_ROOT / "data/assets/tools_db.json"
TRACKER_DATA = PROJECT_ROOT / "data/stats/job_tracker.json"
ARCHIVE_DIR = PROJECT_ROOT / "data/newsletter_archive"

def generate_site():
    with open(TEMPLATE_PATH, 'r') as f: html = f.read()

    # 1. Generate Job Tracker
    tracker_html = ""
    if TRACKER_DATA.exists():
        stats = json.loads(TRACKER_DATA.read_text())
        tracker_html = f'''
        <section class="max-w-7xl mx-auto px-6 py-16">
            <div class="bg-white border border-slate-100 rounded-[2.5rem] p-10 shadow-sm flex flex-col md:flex-row justify-between items-center">
                <div class="mb-8 md:mb-0">
                    <h3 class="text-2xl font-black mb-2">The AI Job Tracker</h3>
                    <p class="text-slate-500 font-medium">Monitoring 2026 industry shifts in real-time.</p>
                </div>
                <div class="flex gap-12">
                    <div class="text-center"><p class="text-4xl font-black text-blue-600">{stats['augmented_roles']}</p><p class="text-xs font-bold text-slate-400 uppercase tracking-tighter">Roles Augmented</p></div>
                    <div class="text-center"><p class="text-4xl font-black text-red-500">{stats['displaced_roles']}</p><p class="text-xs font-bold text-slate-400 uppercase tracking-tighter">Roles Displaced</p></div>
                    <div class="text-center"><p class="text-4xl font-black text-green-500">{stats['new_ai_roles']}</p><p class="text-xs font-bold text-slate-400 uppercase tracking-tighter">New AI Roles</p></div>
                </div>
            </div>
        </section>'''

    # 2. Generate Tools HTML
    tools_html = ""
    if TOOLS_DATA.exists():
        tools = json.loads(TOOLS_DATA.read_text())
        for t in tools:
            tools_html += f'''
            <div class="p-6 border border-slate-100 rounded-3xl bg-white shadow-sm hover:shadow-md transition">
                <h5 class="font-black text-lg mb-1">{t['name']}</h5>
                <span class="text-xs font-bold text-blue-500 uppercase">{t['category']}</span>
                <p class="text-sm text-slate-600 mt-4 mb-4">{t['use_case']}</p>
                <a href="{t['url']}" target="_blank" class="text-sm font-black text-blue-600 hover:underline">Try Tool &rarr;</a>
            </div>'''

    # 3. Generate News HTML
    news_html = ""
    if NEWS_DATA.exists():
        stories = json.loads(NEWS_DATA.read_text())
        for s in stories[:6]:
            news_html += f'''
            <div class="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
                <span class="text-xs font-bold text-slate-400 uppercase">{s['source']}</span>
                <h4 class="text-xl font-bold mt-2 mb-4">{s['title']}</h4>
                <p class="text-slate-500 text-sm mb-6">{s.get('summary', '')[:140]}...</p>
                <a href="{s['url']}" target="_blank" class="text-blue-600 font-bold hover:underline">Full Intelligence &rarr;</a>
            </div>'''

    # 4. Generate Archive HTML
    archive_html = ""
    if ARCHIVE_DIR.exists():
        for issue in sorted(os.listdir(ARCHIVE_DIR), reverse=True)[:5]:
            if issue.endswith('.md'):
                name = issue.replace('_', ' ').replace('.md', '').upper()
                archive_html += f'<li><a href="toolkit.html" class="text-slate-600 hover:text-blue-600 font-medium">{name} - Read Archive</a></li>'

    # Perform Replacements
    html = html.replace("{{JOB_TRACKER_HTML}}", tracker_html)
    html = html.replace("{{TOOLS_HTML}}", tools_html)
    html = html.replace("{{NEWS_HTML}}", news_html)
    html = html.replace("{{ARCHIVE_HTML}}", archive_html)

    with open(OUTPUT_PATH, 'w') as f: f.write(html)
    print(f"Website generated successfully: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_site()
