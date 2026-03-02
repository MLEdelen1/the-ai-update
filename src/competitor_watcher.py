#!/usr/bin/env python3
import json
from pathlib import Path

def get_competitor_targets():
    return [
        {"name": "The AI Search", "handle": "@theAIsearch", "focus": "AI Tools & Search"},
        {"name": "Matt Wolfe", "handle": "@m_wolfe", "focus": "AI News & Tutorials"},
        {"name": "Rowan Cheung", "handle": "@rowancheung", "focus": "Breaking AI News"}
    ]

if __name__ == "__main__":
    targets = get_competitor_targets()
    print(f"Monitoring {len(targets)} competitor intelligence channels.")
    # Future: Use search_engine to scrape their latest high-engagement posts
