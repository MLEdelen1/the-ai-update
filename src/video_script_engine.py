#!/usr/bin/env python3
import json
from pathlib import Path

def generate_video_brief():
    # In a real run, this would prompt the LLM to write a script from latest_scan.json
    script = {
        "hook": "Did you know you can run a billion-parameter AI model on your phone for $0?",
        "body": "Today on The AI Update: Anthropic faces drama, DeepSeek wins on price, and we show you how to automate your email with local models.",
        "cta": "Link in bio for the Zero-Dollar AI Toolkit."
    }
    out_path = Path(__file__).resolve().parents[1] / "data/video_scripts/latest_brief.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2)
    print("Daily Video Brief generated.")

if __name__ == "__main__":
    generate_video_brief()
