from msim import *
from eng import step
a=V('a',0)*2+1; d=V('d',0)*2+3; c=V('c',0)*2+1
bad=0; n=0
def cmp(cfg, exp):
    global bad,n
    n+=1
    try:
        r,s=next_K(cfg)
        ok = r!='HALT' and same(r,exp)
        if not ok: bad+=1; print('MISMATCH',show(cfg),show(r) if r!='HALT' else r,'exp',show(exp))
        return getattr(s,'rnew',0)
    except Fail as e: bad+=1; print('FAIL',show(cfg),e)
for K in range(1,21):
    for rest in ([],[c],[1,c]):
        rn=cmp([a]+[1]*K+[d]+rest, [1]*K+[a+4,d-2]+rest)
        if rn: print('rnew>0 for B',K,rest)
    cmp([a]+[1]*K, [a+4] if K==1 else [1]*(K-1)+[a+4])
cmp([a],[('Z',a+2)])
for rest in ([],[c],[1,c]): cmp([a,d]+rest,[a+4,d-2]+rest)
print('msim small-K symbolic tests',n,'bad',bad)
