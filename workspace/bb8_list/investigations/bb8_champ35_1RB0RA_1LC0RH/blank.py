import sys
sys.path.insert(0,'.')
from tmlit import Sim
from fam import parse
from tr import TM
s=Sim(TM)
seen=0
while s.steps<7000:
    if not s.step(): print('HALT',s.steps); break
    p=parse(s)
    if p is not None:
        seen+=1
        print(s.steps,p if len(str(p))<200 else (p[0][:3],len(p[0]),p[1],p[2]))
        if seen>6: break
