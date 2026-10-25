import idle, json, sys
from bfollow import follow
R=[r for r in map(json.loads,open('bf.jsonl')) if r['res'] in sys.argv[2].split(',')]
with open(sys.argv[1],'w') as fo:
    for r in R:
        try: x=follow(r['m'],r['base'],rounds=10)
        except Exception as e: x=('ERR',repr(e)[:200])
        fo.write(json.dumps({'m':r['m'],'base':r['base'],'old':r['res'],'res':x[0],'detail':str(x[1:])[:1500]})+'\n'); fo.flush()
