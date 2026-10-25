import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
import tr
k=int(sys.argv[1]); N=int(sys.argv[2]); minlen=int(sys.argv[3])
w='101010'+'110'*k+'1'
s=Sim.from_word(tr.TM,'0000'+w+'0',4+len(w),'G')
base=s.pos-len(w)
prevd=0; last=(0,0)
out=[]
while s.steps<N:
    p0=s.pos
    if not s.step(): print('HALT'); break
    d=s.pos-p0
    if d!=prevd:
        out.append((s.steps,s.pos-base,ST[s.state]))
    prevd=d
# print runs of consecutive turning points that are far apart
print(' '.join('%d:%d%s'%o for o in out if True)[:3000])
print()
print('E events:',' '.join('%d:%d'%(o[0],o[1]) for o in out if o[2]=='E'))
print('G events:',' '.join('%d:%d'%(o[0],o[1]) for o in out if o[2]=='G'))
