import idle, json, sys
from bfollow import follow
G=json.load(open('b9groups.json'))
with open('bf9.jsonl','w') as fo:
    for nm,ms in G:
        try: r=follow(ms[0],nm,rounds=10)
        except Exception as e: r=('ERR',repr(e)[:200])
        fo.write(json.dumps({'m':ms[0],'base':nm,'n':len(ms),'res':r[0],'detail':str(r[1:])[:1500]})+'\n'); fo.flush()
