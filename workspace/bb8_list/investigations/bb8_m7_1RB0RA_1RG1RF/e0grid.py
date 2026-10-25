import sys,re
sys.path.insert(0,'.')
from tmlit import Sim, ST
import tr
bad=0; tot=0
for tm in (tr.TM, tr.TM[:-3]+'1RH'):
  for n in range(1,6):
    for b in range(0,5):
        s=Sim.from_word(tm,'0000'+tr.kword([0]*n,0,b)+'0',4+len(tr.kword([0]*n,0,b)),'G')
        found=None
        while s.steps<200000:
            if not s.step(): break
            if ST[s.state]=='C':
                t=s.tape; lo,hi=s.bounds()
                if s.pos-lo==1:
                    w=''.join(map(str,t[lo:hi+1]))
                    if re.match(r'^11(?:101)+$',w): found=(s.steps,(len(w)-2)//3); break
        M=n-1
        tot+=1
        if not found or found[1]!=12*b+M+12: bad+=1; print('BAD',tm[-3:],n,b,found)
print('E0 grid',tot,'bad',bad)
