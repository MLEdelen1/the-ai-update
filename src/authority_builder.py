#!/usr/bin/env python3
import json
import random
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
TOPICS_FILE = PROJECT_ROOT / "data/deep_dive_topics.json"
DRAFTS_DIR = PROJECT_ROOT / "data/drafts"

def generate_deep_dive_prompt():
    if not TOPICS_FILE.exists(): return
    
    with open(TOPICS_FILE, 'r') as f:
        topics = json.load(f)
    
    topic = random.choice(topics)
    
    prompt = f"""You are @The_AIUpdate. Expert in practical AI implementation.
Create a high-authority X/Twitter THREAD (5-7 tweets) about this topic:

TOPIC: {topic['topic']}
FOCUS: {topic['focus']}

GOAL: Build reputation. Show practical/cost side.

STRUCTURE:
1. The Hook, 2. The Shift, 3. The Solution, 4. Implementation, 5. Result, 6. CTA.
Rules: <280 chars per tweet, separate with ---"""
    
    batch_file = DRAFTS_DIR / "latest_batch.json"
    if batch_file.exists():
        with open(batch_file, 'r') as f:
            batch = json.load(f)
        
        # Ensure keys exist to avoid KeyError
        if "threads" not in batch: batch["threads"] = []
        
        batch["threads"].append({
            "type": "deep_dive",
            "topic": topic['topic'],
            "prompt": prompt,
            "status": "pending"
        })
        
        with open(batch_file, 'w') as f:
            json.dump(batch, f, indent=2)
            
    print(f"Deep Dive prompt generated for topic: {topic['topic']}")

if __name__ == "__main__":
    generate_deep_dive_prompt()
