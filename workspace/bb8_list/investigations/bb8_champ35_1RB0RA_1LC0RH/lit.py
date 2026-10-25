import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
from tr import TM
w='1'+'01'*4+'1'+'1'+'01'*4
s=Sim.from_word(TM,'0000'+w+'0',4+len(w),'G')
def d(s):
    t=s.tape; lo,hi=s.bounds()
    return ''.join(map(str,t[lo:s.pos]))+'<%s%d>'%(ST[s.state],t[s.pos])+''.join(map(str,t[s.pos+1:hi+1]))
print(d(s))
for i in range(60):
    s.step(); print(s.steps,d(s))
