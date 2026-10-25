"""cmp.py EVFILE: compare ev7 literal non-R1 events with the K-level model, starting at the event at step 132."""
import idle, sys
from model import enc, step
st=None; n=0; last=None
for line in open(sys.argv[1]):
    f=line.split()
    if f[0]!='E': print('literal end:',line.strip()); break
    stp=int(f[1]); sk=int(f[2]); bl=[int(x) for x in f[3:]]
    if stp<132: continue
    if st is None:
        st=('H',[],2,0); assert enc(st)==bl, (enc(st),bl); continue
    for i in range(sk):
        assert st[2]>0, ('expected R1',st)
        st=step(st)
    st=step(st)
    if st[0] in ('OUT','HALT'): print('model left domain',st,'at literal step',stp); break
    if enc(st)!=bl:
        print('MISMATCH at step',stp,'model',st,enc(st)[:30],'lit',bl[:30]); break
    n+=1; last=(stp,st)
print('matched',n,'non-R1 events; last',last[0],last[1][0],last[1][1][:12],'len',len(last[1][1]),'a',last[1][2],'b',last[1][3])
