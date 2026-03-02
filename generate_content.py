import json
import requests
import re
import sys

def enforce_english(text):
    if not isinstance(text, str): return text
    return re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\u31f0-\u31ff\uac00-\ud7af]+', '', text)

API_KEY_PATH = '/a0/usr/projects/x-manage/config/gemini_keys.json'
with open(API_KEY_PATH, 'r') as f:
    API_KEY = json.load(f)['gemini_api_key']

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

with open('/a0/usr/projects/x-manage/data/news_cache/latest_scan.json', 'r') as f:
    news_data = json.load(f)

top_story = news_data[0]
title = top_story.get('title')
summary = top_story.get('summary')

article_prompt = f"""Write a technical, 8th-grade reading level Deep Dive article based on this story:
CRITICAL RULE: NO ROBOTICS OR HARDWARE. ONLY write about software LLMs and digital agents. Do NOT mention physical robots.

Title: {title}
Summary: {summary}

The article should be in Markdown format, with headers, bullet points, and practical takeaways.
No CJK characters allowed."""

tweet_prompt = f"""Draft a high-signal, punchy tweet about this new article:
Title: {title}

Include engaging emojis and relevant hashtags. No CJK characters allowed.
Keep it under 280 characters."""

def generate(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        print(f"API Error: {resp.text}")
        return None

print("Generating article with gemini-2.5-flash...")
article_content = generate(article_prompt)
print("Generating tweet with gemini-2.5-flash...")
tweet_content = generate(tweet_prompt)

if article_content and tweet_content:
    article_content = enforce_english(article_content)
    tweet_content = enforce_english(tweet_content)
        tweet_content += "\n\nRead the full Deep Dive: https://theaiupdate.org"
    top_story['deep_dive'] = article_content
    with open('/a0/usr/projects/x-manage/data/news_cache/latest_scan.json', 'w') as f:
        json.dump(news_data, f, indent=2)
    with open('/a0/usr/projects/x-manage/data/drafts/latest_tweet.txt', 'w') as f:
        f.write(tweet_content)
    print("Content generation successful.")
else:
    print("Content generation failed.")
    sys.exit(1)
