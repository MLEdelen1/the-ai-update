import json
import os
import requests
import time
from pathlib import Path

# Configuration
API_KEY_PATH = "/a0/usr/projects/x-manage/config/gemini_keys.json"
NEWS_CACHE_PATH = "/a0/usr/projects/x-manage/data/news_cache/latest_scan.json"
RESEARCH_DIR = "/a0/usr/projects/x-manage/data/research/briefings_2026_02/"
PROMPTS_DIR = "/a0/usr/projects/x-manage/data/assets/prompts/"

# Load API Key
with open(API_KEY_PATH, 'r') as f:
    API_KEY = json.load(f)["gemini_api_key"]

class GeminiClient:
    def __init__(self, key):
        self.key = key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.key}"

    def generate(self, prompt, system_instruction=None):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_instruction:
             payload["system_instruction"] = {"parts": [{"text": system_instruction}]}
        
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"API Error: {e}")
            return None

class Newsroom:
    def __init__(self):
        self.client = GeminiClient(API_KEY)
        self.researcher_prompt = Path(PROMPTS_DIR + "researcher_prompt.txt").read_text()
        self.writer_prompt = Path(PROMPTS_DIR + "writer_prompt.txt").read_text()
        Path(RESEARCH_DIR).mkdir(parents=True, exist_ok=True)

    def load_targets(self):
        with open(NEWS_CACHE_PATH, 'r') as f:
            data = json.load(f)
        # Filter for the high-value 'mega_intel' items or specific high-interest items
        targets = [item for item in data if item.get('id', '').startswith('mega_intel') or item.get('id', '').startswith('v2026')]
        return targets

    def process_story(self, story):
        title = story['title']
        safe_id = story['id']
        output_file = Path(RESEARCH_DIR) / f"briefing_{safe_id}.md"
        
        if output_file.exists():
            print(f"Skipping {title} (Already Researched)")
            return

        print(f"\n--- Processing: {title} ---")
        
        # Phase 1: Research
        print(" > Phase 1: Researching...")
        research_context = f"Title: {title}\nOriginal Summary: {story.get('summary', '')}\nURL: {story.get('url', '')}"
        research_data = self.client.generate(research_context, system_instruction=self.researcher_prompt)
        
        if not research_data:
            print("Failed to research.")
            return

        # Phase 2: Writing
        print(" > Phase 2: Writing Briefing...")
        article_content = self.client.generate(f"Research Data:\n{research_data}", system_instruction=self.writer_prompt)
        
        if not article_content:
             print("Failed to write.")
             return

        # Save
        final_output = f"# {title}\n\n{article_content}"
        output_file.write_text(final_output)
        print(f" > SUCCESS: Saved to {output_file.name}")

    def run(self):
        targets = self.load_targets()
        print(f"Found {len(targets)} high-value targets.")
        for story in targets:
            self.process_story(story)
            time.sleep(1) # Polite delay

if __name__ == "__main__":
    newsroom = Newsroom()
    newsroom.run()
