import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.x_api import XAPIClient
import scripts.x_article_poster as xp

state_path = Path('data/posted/x_posted_articles.json')
state = json.loads(state_path.read_text(encoding='utf-8'))
client = XAPIClient()

hex_title = re.compile(r'^[0-9a-fA-F]{12}$')
repaired = []
for row in list(state.get('posted', [])):
    title = (row.get('title') or '').strip()
    if not hex_title.match(title):
        continue
    article_id = row.get('article_id')
    tweet_id = row.get('tweet_id')
    md = Path('data/research/briefings_2026_02') / f'briefing_{article_id}.md'
    better = xp._extract_title(md) if md.exists() else title
    text = xp._build_tweet(better, row['url'], 0)

    del_res = client.delete_tweet(tweet_id)
    post_res = client.post_tweet(text)
    if post_res.get('success'):
        new_id = (((post_res.get('data') or {}).get('data') or {}).get('id'))
        row['title'] = better
        row['tweet_id'] = new_id
        row['repaired_at'] = xp._now_iso()
        repaired.append({'article_id': article_id, 'old_tweet_id': tweet_id, 'new_tweet_id': new_id, 'title': better, 'deleted': del_res.get('success')})

state_path.write_text(json.dumps(state, indent=2), encoding='utf-8')
print(json.dumps({'repaired_count': len(repaired), 'repaired': repaired}, indent=2))