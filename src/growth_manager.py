#!/usr/bin/env python3
"""
Growth Manager - Finds high-engagement topics for @The_AIUpdate to join
"""
import json
from pathlib import Path

def analyze_growth_opportunities():
    print("Analyzing trending AI topics for engagement...")
    # In a real scenario, this would use search_engine to find trending X posts
    # For now, it identifies 'Hot' items from the latest scan
    scan_file = Path("/a0/usr/projects/x-manage/data/news_cache/latest_scan.json")
    if not scan_file.exists(): return
    
    stories = json.loads(scan_file.read_text())
    high_signal = [s for s in stories if "breakthrough" in s['title'].lower() or "free" in s['title'].lower()]
    
    print(f"Found {len(high_signal)} high-signal growth opportunities.")
    return high_signal

if __name__ == "__main__":
    analyze_growth_opportunities()
