import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
from tr import TM, start
from fam import parse
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); N=int(sys.argv[4])
s=start(ds,a,b)
def disp(s):
    t=s.tape; lo,hi=s.bounds()
    L=''.join(map(str,t[lo:s.pos])); R=''.join(map(str,t[s.pos+1:hi+1]))
    return '%s<%s%d>%s'%(L,ST[s.state],t[s.pos],R)
last=None
print(0,disp(s))
while s.steps<N:
    if not s.step(): print('HALT'); break
    # print when head at right edge (hi<=pos) or left edge
    lo,hi=s.bounds()
    if s.pos>=hi and s.tape[s.pos]==0 and ST[s.state] in 'GHA':
        print(s.steps,disp(s))
    if parse(s): print('K',s.steps,parse(s)); break
