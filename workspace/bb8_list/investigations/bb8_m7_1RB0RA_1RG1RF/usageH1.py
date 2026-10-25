import sys
sys.path.insert(0,'.')
from tmlit import Sim
import tr
def mk(M, ds,a,b):
    w=tr.kword(ds,a,b)
    return Sim.from_word(M,'0000'+w+'0',4+len(w),'G')
P0='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RF'
CH='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF'
import itertools
from fam import parse
def run(M,ds,a,b,N=3*10**6):
    s=mk(M,ds,a,b); s.usage={}
    while s.steps<N:
        if not s.step(): return ('HALT',s.steps,s.usage)
        p=parse(s)
        if p is not None: return ('K',s.steps,p,s.usage)
    return ("TO",N,{})
for ds,a,b in [([1],1,0),([1],1,2),([2],0,1),([0,0,1],0,2),([0,1],0,0),([3],2,1),([0,0],0,3)]:
    r1=run(P0,ds,a,b); r2=run(CH,ds,a,b)
    print(ds,a,b, r1[:3], r2[:3], 'H1 used:', r1[-1].get((7,1),0), r2[-1].get((7,1),0))
