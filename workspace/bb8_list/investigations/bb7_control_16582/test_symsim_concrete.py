"""Cross-check symsim (concrete exponents, run crossing) against a plain literal simulator."""
import sys, random
from symsim import *

def expand(c):
    def ex(toks):
        s=''
        for t in toks:
            s += t[1] if t[0]=='L' else t[1]*t[2].c
        return s
    L=ex(c.left); R=ex(c.right)
    s=(L+str(c.cell)+R)
    pos=len(L)
    # canonical: strip zeros both ends keeping head
    a=len(s)-len(s.lstrip('0')); a=min(a,pos); s=s[a:]; pos-=a
    s2=s.rstrip('0')
    if len(s2)<=pos: s2=s[:pos+1]
    return s2,pos,c.state

def literal(nsteps):
    tape={}; pos=0; st=0
    for i in range(nsteps):
        w,d,ns=TM[st][tape.get(pos,0)]
        tape[pos]=w; pos+=d; st=ns
    lo=min(min(tape),pos); hi=max(max(tape),pos)
    s=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
    p=pos-lo
    a=len(s)-len(s.lstrip('0')); a=min(a,p); s=s[a:]; p-=a
    s2=s.rstrip('0')
    if len(s2)<=p: s2=s[:p+1]
    return s2,p,st

c=make_config('[A0]')
checks=[]
LIM=int(sys.argv[1]) if len(sys.argv)>1 else 3_000_000
while c.steps<LIM:
    c.step(); c.normalize()
    checks.append((c.steps,expand(c)))
random.seed(1)
sample=sorted(random.sample(checks,40)+checks[-3:])
# run literal once, checking at sample step counts
tape={}; pos=0; st=0; i=0; bad=0
for n,(s,p,stt) in sample:
    while i<n:
        w,d,ns=TM[st][tape.get(pos,0)]
        tape[pos]=w; pos+=d; st=ns; i+=1
    lo=min(min(tape),pos); hi=max(max(tape),pos)
    t=''.join(str(tape.get(k,0)) for k in range(lo,hi+1)); q=pos-lo
    a=len(t)-len(t.lstrip('0')); a=min(a,q); t=t[a:]; q-=a
    t2=t.rstrip('0')
    if len(t2)<=q: t2=t[:q+1]
    ok=(t2,q,st)==(s,p,stt)
    if not ok: bad+=1; print('MISMATCH at',n)
print('checked',len(sample),'points up to step',sample[-1][0],'mismatches',bad)
