import sys
from rules_v import pred,MS
def run(L,v,maxsingles=6):
    singles=[]
    while True:
        if len(L)>=2 and L[1]>=1: L=[L[0]+2*L[1],0]+L[2:]; continue
        if len(L)==1:
            singles.append(L[0])
            if L[0]%3!=1 and (len(singles)>maxsingles or L[0]>10**7): return ('OPEN',singles)
        p=pred(L,v)
        if p=='H': return ('H',singles)
        L=p
def first_singles(M,N):
    from sim import parse
    from probe import decl
    T=parse(M); tape=bytearray(1<<16); pos=1<<15; st=0; out=[]; first=None; lo=pos; hi=pos
    for n in range(N):
        c=tape[pos]
        if (st,c) not in T: out.append(('HALT',n+1,sum(tape))); break
        w,d,q=T[(st,c)]; tape[pos]=w
        if w: lo=min(lo,pos); hi=max(hi,pos)
        pos+=d; st=q
        if st==6 and tape[pos]==0 and lo>pos:
            r=decl(''.join('1' if x else '0' for x in tape[pos+1:hi+1]))
            if r is not None:
                if first is None: first=r
                if len(r)==1: out.append(r[0])
    return first,out
if __name__=='__main__':
    for v in 'abc':
        f,lit=first_singles(MS[v],int(sys.argv[1]))
        res=run(list(f),v)
        print(v,'first K',f,'literal singles',lit,'| macro',res[0],[ (s if s<10**9 else '%.4e(mod3=%d)'%(s,s%3)) for s in res[1]])
