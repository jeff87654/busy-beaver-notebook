import sys
sys.path.insert(0,'.')
import planner8 as pl
import gen_p0 as g
from gen_p0 import R,Z,BLANK,U
from cexp import cs
def summarize(script):
    out=[]
    i=0
    while i<len(script):
        op=script[i]
        if op[0]=='steps':
            n=op[1]
            nxt=script[i+1] if i+1<len(script) else None
            if nxt and nxt[0]=='cross': out.append('%d>%s'%(n,nxt[1].replace('cx_','').replace('cr_',''))); i+=2; continue
            if nxt and nxt[0]=='align': out.append('%d>al%d%s'%(n,nxt[1][1],''.join(map(str,nxt[1][2])))); i+=2; continue
            if nxt and nxt[0]=='peel': out.append('%d>PEEL(%s)'%(n,nxt[1])); i+=2; continue
            if nxt and nxt[0]=='stop': out.append('%d>STOP'%n); i+=2; continue
            out.append('%d'%n)
        else:
            out.append(str(op))
        i+=1
    return ' '.join(out)
def go(start,lim=None,maxev=600,target=None):
    pl.LEMMAS.clear(); pl.PEELS.clear()
    script,c=pl.drive('x',start,target,maxev=maxev,verbose=False,peel_limit=lim)
    print(summarize(script))
    print(cs(c,100)); print(dict(pl.PEELS))
    return script,c
