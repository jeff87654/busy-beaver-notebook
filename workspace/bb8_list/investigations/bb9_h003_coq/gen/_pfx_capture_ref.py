import planner8 as pl
from planner8 import BLANK, V
from common import TB, run
import sys, time; sys.path.insert(0,'../eg'); sys.path.insert(0,'../tools')
from ktparse import parse
import mexp, d0spec
from d0spec import D0
def D0f_concrete(L,P,s,y,t,ltoks):
    def D(x): return [1]+[0,1]*x
    lcells=[]
    for d in ltoks: lcells+=D(d)
    lcells+=[1,1]
    return ('B',[1,0,0,1]+list(TB)*t+[1,1]+[1]*L+[0,0,1]*P+[1,1,0]+[0,1]*y+[1,0,1]+[0,1]*s+[1]+lcells,[BLANK],'>')
def to_preESC(cfg,maxsteps=400000):
    for i in range(maxsteps):
        q,Lc,Rc,mode=cfg
        if q=='B' and mode=='>' and (Rc==[BLANK] or all(c==BLANK for c in Rc)) and Lc[:4]==[1,0,0,1] and i>50:
            w=''.join(str(c) for c in reversed([c for c in Lc if c!=BLANK])).lstrip('0'); r=parse(w)
            if r and r[1] and r[2]==1 and r[3]==2:
                toks=r[1]
                for j in range(len(toks)-3):
                    if toks[j:j+4]==[2,8,6,7] and all(x==1 for x in toks[j+4:]): return Lc
        try: cfg=pl.step(cfg)
        except pl.Halted: return None
    return None
base=to_preESC(D0f_concrete(38,24,3,8,2,[9,13]))
seg1=base[76:88]; seg2=base[115:163]; seg3=base[179:180]
# symbolic TARGET (nearest-first), E=0 variant (P=6p+18, near K=6p+3)
Lsym=[1,0,0,1]+[run(TB,t=1)]+list(TB)*7+seg1+[run((1,0,1)*6,p=1)]+[1,0,1]*3+seg2+[run((0,1),y=1)]+seg3+[run((0,1),s=1)]+[1,V('l')]
T=('B',Lsym,[BLANK],'>')
# sanity: substitute base values, compare to base (without l tail)
def subst_concrete(cfg,vals):
    q,L,R,m=cfg; out=[]
    for c in L:
        if isinstance(c,tuple) and c and c[0]=='run':
            blk=c[1]; cnt=sum(vals[k]*v for k,v in c[2]); out+=list(blk)*cnt
        elif isinstance(c,tuple) and c[0]=='VAR': out+=('L',)  # placeholder
        else: out.append(c)
    return out
chk=subst_concrete(T,{'t':2,'p':1,'y':8,'s':3})
base_noL=base[:base.index(1,186)] if False else None
# compare chk up to the l marker with base up to base[186]
i=chk.index('L') if 'L' in chk else len(chk)
print('reproduces base head?', chk[:i]==base[:i], 'chk_i',i,'base[:i]==',base[:i]==chk[:i])
if chk[:i]!=base[:i]:
    for k in range(min(i,len(base))):
        if chk[k]!=base[k]: print('first diff at',k,'chk',chk[k-2:k+3],'base',base[k-2:k+3]); break
# START symbolic (E=0: P=6p+18, PBASE=18)
d0spec.PB=6; d0spec.KL=6
S=D0(1,'s',0,'y',18,'p',[1]*38)
print('explore...'); t0=time.time()
pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
try:
    tree=mexp.explore(S,T,splits=0)
    print('OK %.1fs'%(time.time()-t0))
    import pickle; pickle.dump((S,T,tree),open('tree_pfx_37_0.pkl','wb'))
except Exception as e:
    import traceback; traceback.print_exc()
g=mexp.Gen('PFX370'); lem=mexp.rule_lemma('PFX37_0', S, T, tree, g, progress=True)
print('LEMMAS', len(g.lemmas))
print(lem.split('Proof')[0])
