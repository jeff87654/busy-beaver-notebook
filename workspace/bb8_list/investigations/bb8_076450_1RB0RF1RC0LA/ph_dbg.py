import sys
from phases import *
SEEN=[]
def m_log(cfg):
    q,L,R,mode=cfg
    if q=='A' and ((mode=='<' and L[0]==BL) or (mode=='>' and L==[BL] and R[0]==0)):
        SEEN.append(cfg)
    return None
m_log.anytime=True
start = BEX([0,1]*4 + run((0,1,0,1),'a'), [1,0]*4 + run((1,0,1,0),'k'))
tgt = ALX([0,1]*2 + run((0,1,0,1),'a'), [0,1]*33 + run((0,1)*8,'k'))
script, end = P.drive('BE', norm(start), norm(tgt), matchers=[m_log]+MATCH, maxev=3000, verbose=False)
for c in SEEN: print(P.show(c)[:250])
print('target', P.show(norm(tgt))[:250])
print(P.canon(SEEN[1]) if len(SEEN)>1 else None)
print(P.canon(norm(tgt)))
