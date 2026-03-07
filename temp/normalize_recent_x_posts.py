import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.x_api import XAPIClient
import scripts.x_article_poster as xp

state_path = Path('data/posted/x_posted_articles.json')
state = json.loads(state_path.read_text(encoding='utf-8'))
client = XAPIClient()

rows = state.get('posted', [])[-8:]
updated=[]
for i,row in enumerate(rows):
    title = (row.get('title') or '').strip()
    text = xp._build_tweet(title, row['url'], i)
    old=row.get('tweet_id')
    d=client.delete_tweet(old)
    p=client.post_tweet(text)
    if p.get('success'):
        new_id=(((p.get('data') or {}).get('data') or {}).get('id'))
        row['tweet_id']=new_id
        row['rewritten_at']=xp._now_iso()
        updated.append({'article_id':row.get('article_id'),'old':old,'new':new_id,'deleted':d.get('success')})

state_path.write_text(json.dumps(state, indent=2), encoding='utf-8')
print(json.dumps({'updated':len(updated),'rows':updated}, indent=2))