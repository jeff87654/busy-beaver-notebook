from sim import *
import sys
t=parse(M);tape={};p=0;s=0;lo=hi=0
last=None
for i in range(int(sys.argv[1])):
    r=t[(s,tape.get(p,0))]
    if r is None: print('HALT',i);break
    tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2]
    lo=min(lo,p);hi=max(hi,p)
    if p<lo+1 and s==1 and (i>0):  # B at left edge
        st=''.join(str(tape.get(q,0)) for q in range(lo,hi+1))
        print(i+1,st.rstrip('0') if False else st)
