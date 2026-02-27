import os, sys, json, requests, re, subprocess

print("\n=== [1] Scanning News ===")
subprocess.run(['python3', 'src/news_scanner.py'], check=True)

print("\n=== [2 & 5] Generating Article & Tweet (Gemini 3.1 Pro) ===")
def enforce_english(text):
    if not isinstance(text, str): return text
    return re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\u31f0-\u31ff\uac00-\ud7af]+', '', text)

with open('config/gemini_keys.json', 'r') as f:
    API_KEY = json.load(f)['gemini_api_key']

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={API_KEY}"

try:
    with open('data/news_cache/latest_scan.json', 'r') as f:
        news_data = json.load(f)
except Exception:
    news_data = []

if not news_data:
    print("No new stories found. Exiting gracefully.")
    sys.exit(0)

import random
existing = os.listdir('data/research/briefings_2026_02') if os.path.exists('data/research/briefings_2026_02') else []

# --- STRICT TOPIC FILTERING ---
allowed_terms = ['llm', 'open source', 'model', 'api', 'agentic', 'workflow', 'n8n', 'ollama', 'openclaw', 'ai', 'software', 'startup', 'consumer', 'guide', 'tutorial', 'gemini', 'nano banana', 'sora', 'music', 'image', 'video', 'generator', 'editor', 'multimodal', 'kling', 'midjourney', 'suno']
banned_terms = ['government', 'federal', 'politics', 'policy', 'permit', 'biden', 'trump', 'senate', 'congress', 'laboratory', 'pnnl', 'draftnepabench', 'president', 'court']

valid_story = None
for s in news_data:
    t = s.get('title', '').lower()
    sm = s.get('summary', '').lower()
    text = t + ' ' + sm

    if any(b in text for b in banned_terms):
        continue

    if any(a in text for a in allowed_terms):
        tslug = re.sub(r'[^a-z0-9]+', '_', t.strip())[:40]
        if not any(tslug in ex for ex in existing):
            valid_story = s
            break

if not valid_story:
    print("No valid LLM/OpenSource stories found. Exiting gracefully without posting junk.")
    sys.exit(0)

title = valid_story.get('title', 'Unknown Title')
summary = valid_story.get('summary', 'No summary available.')

# --- STRICT PROMPT CONSTRAINTS ---
article_prompt = f""""Write a technical, 8th-grade reading level Deep Dive article based on this story:
Title: {title}
Summary: {summary}

The article should be in Markdown format, with headers, bullet points, and practical takeaways.
No CJK characters allowed. Do not write about physical robotics. 
STRICT TOPIC RULE: Focus ONLY on AI software, LLMs (ALL models like Gemini, Claude, etc), AI music/image/video generators and editors (like Sora, Nano Banana, Kling, Suno), open-source tools, and step-by-step guides. NEVER write about government, politics, federal policies, or physical robotics."""

tweet_prompt = f""""Draft a high-signal, punchy tweet about this new article focusing purely on LLMs/software models:
Title: {title}

Include engaging emojis and relevant hashtags. No CJK characters allowed. Keep it under 150 characters."""

def generate(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    return None

article_content = enforce_english(generate(article_prompt))
tweet_content = enforce_english(generate(tweet_prompt))
if tweet_content:
    tweet_content += "\n\nRead the full Deep Dive: https://theaiupdate.org"

if not article_content or not tweet_content:
    print("Content generation failed!")
    sys.exit(1)

valid_story['deep_dive'] = article_content
with open('data/news_cache/latest_scan.json', 'w') as f:
    json.dump(news_data, f, indent=2)

slug = re.sub(r'[^a-z0-9]+', '_', title.lower().strip())[:40]
if not slug: slug = 'auto_article'
md_filename = f'data/research/briefings_2026_02/briefing_{slug}.md'
os.makedirs('data/research/briefings_2026_02', exist_ok=True)
final_md = article_content
if not final_md.strip().startswith('#'):
    final_md = f"# {title}\n\n" + final_md
with open(md_filename, 'w') as f:
    f.write(final_md)
print(f'Saved Markdown to {md_filename}')

with open('data/drafts/latest_tweet.txt', 'w') as f:
    f.write(tweet_content)

with open('data/drafts/latest_batch.json', 'w') as f:
    json.dump({"tweets": [{"draft": tweet_content}]}, f)

print("\n=== [3] Rebuilding Website ===")
subprocess.run(['python3', 'src/site_generator.py'], check=True)

print("\n=== [4] Deploying to GitHub (Cloudflare) ===")
subprocess.run(['git', 'add', '.'], check=True)
subprocess.run(['git', 'commit', '-m', 'Purge political article & strictly enforce LLM only topics'], check=False)
subprocess.run(['git', 'push', 'origin', 'main'], check=True)
