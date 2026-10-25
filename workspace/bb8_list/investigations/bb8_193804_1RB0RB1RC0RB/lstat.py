import sys, collections, re
from dig import step, norm
L,R=[1],[0]+[3]*int(sys.argv[2])+[1]
N=int(sys.argv[1])
runs1=collections.Counter(); runs0=collections.Counter(); tops=collections.Counter(); bottom=collections.Counter()
for i in range(N):
    r,L2,R2=step(L,R)
    if r.startswith('STUCK'): print(r,i,L,R); break
    s=''.join(map(str,L))
    # runs
    for m in re.finditer(r'1+',s[:-1] if s.endswith('1') else s): runs1[len(m.group())]+=1
    if r in ('R3','R5'):
        m=re.search(r'(0*)(1+)$',s); tops[(r,len(m.group(1)) if len(m.group(1))<6 else '6+',len(m.group(2)))]+=1
    L,R=norm(L2,R2)
    if len(R)==1 and R[0]==0: pass
print('inner 1-runs',sorted(runs1.items())[:20])
print('tops',sorted(tops.items(),key=str))
