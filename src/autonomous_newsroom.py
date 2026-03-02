import json
import os
import requests
import time
from pathlib import Path

from runtime_paths import project_root

PROJECT_ROOT = project_root(Path(__file__))
API_KEY_PATH = PROJECT_ROOT / "config/gemini_keys.json"
NEWS_CACHE_PATH = PROJECT_ROOT / "data/news_cache/latest_scan.json"
RESEARCH_DIR = PROJECT_ROOT / "data/research/briefings_2026_02"
PROMPTS_DIR = PROJECT_ROOT / "data/assets/prompts"

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY and API_KEY_PATH.exists():
    with open(API_KEY_PATH, 'r', encoding='utf-8') as f:
        API_KEY = json.load(f).get("gemini_api_key")


class GeminiClient:
    def __init__(self, key):
        self.key = key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={self.key}"

    def generate(self, prompt, system_instruction=None):
        if not self.key:
            return None
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_instruction:
            payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

        try:
            response = requests.post(self.url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"API Error: {e}")
            return None


class Newsroom:
    def __init__(self):
        self.client = GeminiClient(API_KEY)
        self.researcher_prompt = (PROMPTS_DIR / "researcher_prompt.txt").read_text(encoding='utf-8')
        self.writer_prompt = (PROMPTS_DIR / "writer_prompt.txt").read_text(encoding='utf-8')
        RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    def load_targets(self):
        with open(NEWS_CACHE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        targets = [item for item in data if item.get('id', '').startswith('mega_intel') or item.get('id', '').startswith('v2026')]
        return targets

    def process_story(self, story):
        title = story['title']
        safe_id = story['id']
        output_file = RESEARCH_DIR / f"briefing_{safe_id}.md"

        if output_file.exists():
            print(f"Skipping {title} (Already Researched)")
            return

        print(f"\n--- Processing: {title} ---")
        print(" > Phase 1: Researching...")
        research_context = f"Title: {title}\nOriginal Summary: {story.get('summary', '')}\nURL: {story.get('url', '')}"
        research_data = self.client.generate(research_context, system_instruction=self.researcher_prompt)

        if not research_data:
            print("Failed to research.")
            return

        print(" > Phase 2: Writing Briefing...")
        article_content = self.client.generate(f"Research Data:\n{research_data}", system_instruction=self.writer_prompt)

        if not article_content:
            print("Failed to write.")
            return

        final_output = f"# {title}\n\n{article_content}"
        output_file.write_text(final_output, encoding='utf-8')
        print(f" > SUCCESS: Saved to {output_file.name}")

    def run(self):
        targets = self.load_targets()
        print(f"Found {len(targets)} high-value targets.")
        for story in targets:
            self.process_story(story)
            time.sleep(1)


if __name__ == "__main__":
    newsroom = Newsroom()
    newsroom.run()
