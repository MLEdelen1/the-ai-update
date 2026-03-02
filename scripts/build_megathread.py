
import os
from pathlib import Path

md_dir = Path('/a0/usr/projects/x-manage/data/research/briefings_2026_02')
files = list(md_dir.glob('*.md'))
files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
top_5 = files[:5]

thread = "I read 50+ AI updates this week so you don't have to.\n\nHere are the top 5 tools and insights to 10x your productivity and ROI right now: 🧵👇\n\n"

for i, f in enumerate(top_5):
    content = f.read_text(encoding='utf-8')
    lines = content.splitlines()
    title = lines[0].replace('# ', '') if lines else f.name

    summary = "A massive shift in how we approach AI architecture."
    for line in lines[1:]:
        if len(line.strip()) > 80 and not line.startswith('#'):
            summary = line.strip()[:150] + "..."
            break

    url = f"https://theaiupdate.org/articles/{f.stem.replace('briefing_', '')}.html"
    thread += f"{i+1}/ {title}\n\n{summary}\n\nDeep Dive: {url}\n\n"

thread += "6/ That's the roundup for this week.\n\nIf you want passive income frameworks and extreme productivity tools without the noise:\n\n1. Follow @The_AIUpdate\n2. Bookmark this thread\n3. Check out theaiupdate.org for the full archive."

draft_dir = Path('/a0/usr/projects/x-manage/data/drafts')
draft_dir.mkdir(exist_ok=True, parents=True)
(draft_dir / 'latest_megathread.txt').write_text(thread, encoding='utf-8')
print("Megathread generated successfully at data/drafts/latest_megathread.txt")
