import sys
sys.path.insert(0,'.')
from tmlit import Sim
import tr
from fam import parse
def run(tm,tcount,N=10**6):
    w='0000'+'11'+'101'*tcount+'0'
    s=Sim.from_word(tm,w,5,'C')
    while s.steps<N:
        if not s.step(): return ('HALT',s.steps)
        p=parse(s)
        if p is not None: return ('K',s.steps,p[1],p[2],len(p[0]),p[0][:2],set(p[0][1:]))
    return ('TO',)
for t in range(1,14):
    print(t,run(tr.TM,t))
