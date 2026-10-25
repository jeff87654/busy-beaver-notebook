import sys
sys.path.insert(0,'.')
from tmlit import Sim
import tr
k=int(sys.argv[1]); N=int(sys.argv[2])
w='101010'+'110'*k+'1'
s=Sim.from_word(tr.TM,'0000'+w+'0',4+len(w),'G')
prevd=0
while s.steps<N:
    p0=s.pos
    if not s.step(): print('HALT'); break
    d=s.pos-p0
    if d!=prevd: print(s.steps,tr.disp(s)[:150])
    prevd=d
