import idle, json, sys
from bfollow import *
def sig(m,nm):
    v=Var(m,nm); out=[]
    for c in (6151,6150,1029,1030):
        o=v.probe(*build([],[],c,[1,0,5],[' ',' ']))
        out.append('ABS%d:%s'%(c,fmt(*o[1:]) if o[0]=='M' else o[0]))
    for c in (None,0,701,702):
        for K in (2,3):
            y=249
            o=v.probe(*build([],[],c,[0]*K+[0,y],[' ']*(K+1)))
            out.append('NOTOP c=%s K=%d:%s'%(c,K,fmt(*o[1:]) if o[0]=='M' else o[0]))
    for c in (None,701,702):
        ok,why=topacc_ok(v,[],[],c)
        out.append('TOPACC c=%s:%s'%(c,'ok' if ok else str(why)))
    return out
if __name__=='__main__':
    R=[r for r in map(json.loads,open('bf.jsonl')) if r['res'] in sys.argv[1].split(',') and r['base'] in sys.argv[2].split(',')]
    groups={}
    for r in R:
        s=tuple(x[:60] for x in sig(r['m'],r['base']))
        groups.setdefault(s,[]).append(r['base']+':'+r['m'])
    for s,ms in groups.items():
        print(len(ms),ms[:3])
        for x in s: print('     ',x)
