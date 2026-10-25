import sys
sys.path.insert(0,'.')
from tmlit import Sim
import tr
from fam import parse
for tm in (tr.TM, tr.TM[:-3]+'1RH'):
    s=Sim(tm)
    while s.steps<6000:
        if not s.step(): print('HALT'); break
        p=parse(s)
        if p is not None:
            print(tm[-3:], s.steps, len(p[0]), p[0][:2], p[1], p[2], set(p[0][1:])); break
