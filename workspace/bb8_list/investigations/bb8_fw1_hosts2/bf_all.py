import idle, sys, json, os
from ana import load, kind
from bfollow import follow
out=sys.argv[1]; names=sys.argv[2:]
done=set()
if os.path.exists(out):
    for l in open(out): done.add(json.loads(l)['m'])
with open(out,'a') as fo:
    for nm in names:
        labs,V=load(nm,'8')
        for m,outs in V:
            if m in done: continue
            ks=''.join(kind(o,'B') for o in outs)
            if nm in ('B1','B3'):
                rel=[i for i,l in enumerate(labs) if l[0].startswith('TOP') or (l[0].startswith('ABS') and int(l[0].split('=')[1])%2==0)]
                if all(outs[i]=='=' for i in rel):
                    fo.write(json.dumps({'m':m,'base':nm,'ks':''.join(sorted(set(ks)-{'='})),'res':'ODD-ONLY(never: c=0 mod 4 invariant)','detail':''})+chr(10)); done.add(m); continue
            try: r=follow(m,nm,rounds=10)
            except Exception as e: r=('ERR',repr(e)[:200])
            fo.write(json.dumps({'m':m,'base':nm,'ks':''.join(sorted(set(ks)-{'='})),'res':r[0],'detail':str(r[1:])[:1500]})+'\n'); fo.flush()
            done.add(m)
