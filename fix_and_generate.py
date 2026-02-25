import json
import os
import re
import time
import requests
from pathlib import Path

SITE_GEN = '/a0/usr/projects/x-manage/src/site_generator.py'
with open(SITE_GEN, 'r') as f:
    lines = f.read().split('\n')

new_func = """def format_title(title):
    import re
    title = str(title).replace('-', ' ').replace('_', ' ')
    title = re.sub(r'^[a-zA-Z0-9.-]+/', '', title)
    title = re.sub(r'[^a-zA-Z0-9\\s]', ' ', title)
    title = re.sub(r'\\s+', ' ', title).strip().title()
    words = title.split()
    if len(words) == 1:
        title = f"Technical Overview: {title}"
    elif len(words) == 2:
        title = f"Understanding {title}"
    elif len(words) > 10:
        title = " ".join(words[:10]) + "..."
    return title"""

out = []
skip = False
for line in lines:
    if line.startswith('def format_title('):
        skip = True
        out.append(new_func)
        continue
    if skip and line.startswith('def '):
        skip = False
    if not skip:
        out.append(line)

with open(SITE_GEN, 'w') as f:
    f.write('\n'.join(out))
print("Updated site_generator.py format_title.")

API_KEY = json.load(open('/a0/usr/projects/x-manage/config/gemini_keys.json'))['gemini_api_key']
NEWS_DATA = Path('/a0/usr/projects/x-manage/data/news_cache/latest_scan.json')
RESEARCH_DIR = Path('/a0/usr/projects/x-manage/data/research/briefings_2026_02/')

stories = json.loads(NEWS_DATA.read_text())
missing = []
for s in stories[:100]:
    aid = s.get('id', 'unknown')
    if aid == 'unknown': continue
    if not (RESEARCH_DIR / f"briefing_{aid}.md").exists():
        missing.append(s)

print(f"Generating {len(missing)} missing articles...")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
SYS_PROMPT = '''You are a highly capable technical AI writer.
For every article, you MUST cover these three core elements:
1. A highly descriptive overview of what the model/tool/software is and how it works.
2. What makes it good (its strengths, standout features, best use cases, pros).
3. The drawbacks (its weaknesses, limitations, trade-offs, cons).
CRITICAL RULE: DO NOT MAKE EVERY ARTICLE LOOK THE SAME. Vary headings and structure. Use Markdown.'''

for i, s in enumerate(missing):
    title = s.get('title', 'Unknown')
    aid = s.get('id')
    summary = s.get('summary', s.get('description', ''))
    print(f"[{i+1}/{len(missing)}] Writing: {title[:30]}...")
    payload = {
        "system_instruction": {"parts": [{"text": SYS_PROMPT}]},
        "contents": [{"parts": [{"text": f"Topic: {title}\nContext: {summary}\n\nWrite a descriptive article covering what it is, why it's good, and its drawbacks."}]}]
    }
    try:
        r = requests.post(URL, json=payload, timeout=60)
        r.raise_for_status()
        content_md = r.json()['candidates'][0]['content']['parts'][0]['text']
        out_path = RESEARCH_DIR / f"briefing_{aid}.md"
        out_path.write_text(f"# {title}\n\n{content_md}")
    except Exception as e:
        print(f"Error on {title}: {e}")
    time.sleep(2)

print("Rebuilding site...")
os.system("python3 " + SITE_GEN)
print("Pushing to GitHub...")
os.chdir("/a0/usr/projects/x-manage")
os.system("git add . && git commit -m 'Generate missing content and fix titles' && git push")
print("All tasks completed.")
