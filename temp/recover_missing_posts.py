import json,sys
from pathlib import Path
sys.path.insert(0,'.')
from src.x_api import XAPIClient
from scripts.x_rewrite_all_live import get_all_user_tweets, build_rewrite, _parse_article_html, now_iso

root=Path('.')
state_path=root/'data'/'posted'/'x_posted_articles.json'
report_path=root/'data'/'reports'/'x_rewrite_all_latest.json'
state=json.loads(state_path.read_text(encoding='utf-8'))
posted=state.get('posted',[])
client=XAPIClient()
me=client.get_me()['data']
live=get_all_user_tweets(client,str(me['id']),max_pages=10)
live_ids={str(t['id']) for t in live}

mappings=[]
fails=[]
created=0
for row in posted:
    tid=str(row.get('tweet_id') or '')
    if tid and tid in live_ids:
        continue
    article_url=str(row.get('url') or '')
    article_id=str(row.get('article_id') or '')
    meta=_parse_article_html(article_url,article_id)
    title=(meta.get('title') or row.get('title') or '').strip()
    summary=(meta.get('summary') or '').strip()
    draft=build_rewrite(title,article_title=title,article_summary=summary,article_url=article_url)
    suffixes=['','\n\nNow test one workflow.','\n\nTry this in your stack today.','\n\nSteal this and move faster.']
    res=None
    final_txt=draft
    for s in suffixes:
        txt=draft+s
        if len(txt)>280:
            txt=txt[:280]
        res=client.post_tweet(txt)
        final_txt=txt
        if res.get('success'):
            nid=str(res['data']['data']['id'])
            mappings.append({'old_tweet_id':tid,'new_tweet_id':nid,'new_text':txt,'article_title':title})
            row['tweet_id']=nid
            row['rewritten_at']=now_iso()
            created+=1
            break
        err=(res.get('error') or '').lower()
        if 'duplicate content' not in err:
            break
    if not res or not res.get('success'):
        fails.append({'old_tweet_id':tid,'article_id':article_id,'error':res,'draft':final_txt})

state_path.write_text(json.dumps(state,indent=2),encoding='utf-8')

live2=get_all_user_tweets(client,str(me['id']),max_pages=10)
payload={
 'ok': len(fails)==0,
 'user':{'id':str(me['id']),'name':me.get('name'),'username':me.get('username')},
 'counts':{'scanned':len(live2),'rewritten':created,'deleted':0,'reposted':created,'failed':len(fails),'mappings_total':len(mappings)},
 'mappings_first_10':mappings[:10],
 'failures':fails,
 'remaining_ids':[f.get('old_tweet_id') for f in fails if f.get('old_tweet_id')],
 'retry_command':'python temp/recover_missing_posts.py',
 'generated_at':now_iso()
}
report_path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps({'created':created,'failed':len(fails),'live_now':len(live2)},indent=2))
