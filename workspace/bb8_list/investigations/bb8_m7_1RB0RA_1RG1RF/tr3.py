import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
import tr
from tr import start, disp
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); lo_s=int(sys.argv[4]); hi_s=int(sys.argv[5])
s=start(ds,a,b)
prevd=0
while s.steps<hi_s:
    q=s.state; p0=s.pos
    if not s.step(): print('HALT'); break
    d=s.pos-p0
    if s.steps>=lo_s and d!=prevd:
        print(s.steps,disp(s))
    prevd=d
