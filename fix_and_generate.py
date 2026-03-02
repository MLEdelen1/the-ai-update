import json
import os
import re
import sys
import time
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SITE_GEN = PROJECT_ROOT / 'src/site_generator.py'
with open(SITE_GEN, 'r', encoding='utf-8') as f:
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

with open(SITE_GEN, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Updated site_generator.py format_title.")

api_key_path = PROJECT_ROOT / 'config/gemini_keys.json'
API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY and api_key_path.exists():
    API_KEY = json.loads(api_key_path.read_text(encoding='utf-8')).get('gemini_api_key')
if not API_KEY:
    raise RuntimeError('Missing Gemini key. Set GEMINI_API_KEY or create config/gemini_keys.json')

NEWS_DATA = PROJECT_ROOT / 'data/news_cache/latest_scan.json'
RESEARCH_DIR = PROJECT_ROOT / 'data/research/briefings_2026_02/'

stories = json.loads(NEWS_DATA.read_text(encoding='utf-8'))
missing = []
for s in stories[:100]:
    aid = s.get('id', 'unknown')
    if aid == 'unknown':
        continue
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
        out_path.write_text(f"# {title}\n\n{content_md}", encoding='utf-8')
    except Exception as e:
        print(f"Error on {title}: {e}")
    time.sleep(2)

print("Rebuilding site...")
os.system(f'"{sys.executable}" "{SITE_GEN}"')
print("Pushing to GitHub...")
os.chdir(PROJECT_ROOT)
os.system("git add . && git commit -m 'Generate missing content and fix titles' && git push")
print("All tasks completed.")
