"""compact explorer: python cexp.py PHASE [peel_limit] [maxev]"""
import sys
sys.path.insert(0,'.')
import gen_p0 as g
import planner8 as pl
def tw(side):
    out=''
    for t in side:
        if isinstance(t,int): out+=str(t)
        elif t==pl.BLANK: out+='|'
        elif t[0]=='run': out+='[%s]^%s'%(''.join(map(str,t[1])),pl.cnt_str(t[2]))
        else: out+='<%s>'%t[1]
    return out
def cs(c, lim=80):
    L=tw(c[1]); R=tw(c[2])
    if len(L)>lim: L=L[:lim//2]+'..'+L[-lim//2:]
    if len(R)>lim: R=R[:lim//2]+'..'+R[-lim//2:]
    return '%s%s L:%s R:%s'%(c[0],c[3],L,R)
def run(name, st, pl_lim=None, maxev=60, tg=None):
    pl.LEMMAS.clear(); pl.PEELS.clear()
    import io,contextlib
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            script,c=pl.drive(name,st,tg,maxev=maxev,verbose=True,peel_limit=pl_lim)
        except RuntimeError as e:
            script,c=[('err',str(e))],st
    for line in buf.getvalue().splitlines():
        if len(line)>200: line=line[:200]+'...'
        print(line)
    return script,c
if __name__=='__main__':
    name=sys.argv[1]
    lim=int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2]!='-' else None
    mx=int(sys.argv[3]) if len(sys.argv)>3 else 60
    st,tg=g.PH[name]
    script,c=run(name,st,lim,mx)
    print(script[-2:]); print(cs(c)); print(dict(pl.PEELS))
