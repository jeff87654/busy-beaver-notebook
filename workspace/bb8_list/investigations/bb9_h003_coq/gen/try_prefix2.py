"""try_prefix2.py KEY E : capture+explore the entry prefix D0f(key+1) -> pre-ESC (clean Kt m=1 r=2).
 Parked (001)^(6p+18+E). Auto-derives const segments by single-stepping a concrete rep (p=1, s=3,y=8,t=2)."""
import sys, time, pickle
import planner8 as pl
from planner8 import BLANK, V
from common import TB, run
sys.path.insert(0,'../eg'); sys.path.insert(0,'../tools')
from ktparse import parse
import mexp, d0spec
from d0spec import D0
KEY=int(sys.argv[1]); E=int(sys.argv[2]); PBASE=18; L=KEY+1
def D0fc(P,s,y,t):
    def D(x): return [1]+[0,1]*x
    lc=D(9)+D(13)+[1,1]
    return ('B',[1,0,0,1]+list(TB)*t+[1,1]+[1]*L+[0,0,1]*P+[1,1,0]+[0,1]*y+[1,0,1]+[0,1]*s+[1]+lc,[BLANK],'>')
def pre(P,s,y,t,maxsteps=500000):
    cfg=D0fc(P,s,y,t)
    for i in range(maxsteps):
        q,Lc,Rc,mode=cfg
        if q=='B' and mode=='>' and (Rc==[BLANK] or all(c==BLANK for c in Rc)) and Lc[:4]==[1,0,0,1] and i>50:
            w=''.join(str(c) for c in reversed([c for c in Lc if c!=BLANK])).lstrip('0'); r=parse(w)
            if r and r[1] and r[2]==1 and r[3]==2:
                tk=r[1]
                for j in range(len(tk)-1):
                    if tk[j:j+2]==[6,7] and all(x==1 for x in tk[j+2:]) and len(tk)-(j+2)>=1:
                        return Lc, tk[j+2:].count(1), r[3]
        try: cfg=pl.step(cfg)
        except pl.Halted: return None,None,None
    return None,None,None
p0=1; P=6*p0+PBASE+E
base,K,pre_t=pre(P,3,8,2)
assert base is not None, 'no pre-ESC'
Kconst=K-6*p0
def insp(big): 
    i=0
    while i<len(base) and base[i]==big[i]: i+=1
    return i
pT=insp(pre(P,3,8,3)[0]); DT=(pT-4)//8-2; pP=insp(pre(P+6,3,8,2)[0]); pY=insp(pre(P,3,9,2)[0]); pS=insp(pre(P,4,8,2)[0])
nearS=pP-3*K; yS=pY-16; sS=pS-6
seg1=base[pT:nearS]; seg2=base[pP:yS]; seg3=base[pY:sS]
# checks
assert base[sS:pS]==[0,1]*3 and base[yS:pY]==[0,1]*8 and base[nearS:pP]==[1,0,1]*K and base[4:4+8]==list(TB), 'seg boundary'
assert base[pS]==1, 'sep'
print('KEY',KEY,'E',E,'K',K,'Kconst',Kconst,'DT',DT,'pT',pT,'pP',pP,'pY',pY,'pS',pS)
Lsym=[1,0,0,1]+[run(TB,t=1)]+list(TB)*DT+seg1+[run((1,0,1)*6,p=1)]+[1,0,1]*Kconst+seg2+[run((0,1),y=1)]+seg3+[run((0,1),s=1)]+[1,V('l')]
T=('B',Lsym,[BLANK],'>')
# sanity reproduce base
def sub(vals):
    out=[]
    for c in Lsym:
        if isinstance(c,tuple) and c and c[0]=='run': out+=list(c[1])*sum(vals[k]*v for k,v in c[2])
        elif isinstance(c,tuple) and c[0]=='VAR': return out,True
        else: out.append(c)
    return out,False
chk,_=sub({'t':2,'p':1,'y':8,'s':3})
assert chk==base[:len(chk)], 'reproduce fail at %d'%next((k for k in range(len(chk)) if chk[k]!=base[k]),-1)
d0spec.PB=6; d0spec.KL=6
S=D0(1,'s',0,'y',PBASE+E,'p',[1]*L)
t0=time.time(); pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
tree=mexp.explore(S,T,splits=0)
print('OK %.1fs'%(time.time()-t0))
pickle.dump((S,T,tree),open('tree_pfx_%d_%d.pkl'%(KEY,E),'wb'))
