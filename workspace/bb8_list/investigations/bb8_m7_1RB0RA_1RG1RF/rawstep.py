import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
import tr
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); lo_s=int(sys.argv[4]); hi_s=int(sys.argv[5])
s=tr.start(ds,a,b)
while s.steps<hi_s:
    if not s.step(): print('HALT'); break
    if s.steps>=lo_s:
        t=s.tape; lo,hi=s.bounds()
        L=''.join(map(str,t[lo:s.pos])); R=''.join(map(str,t[s.pos+1:hi+1]))
        print(s.steps, L, '<%s%d>'%(ST[s.state],t[s.pos]), R)
