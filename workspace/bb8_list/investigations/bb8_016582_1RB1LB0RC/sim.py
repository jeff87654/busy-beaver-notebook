import sys
M="1RB1LB_0RC---_1RD1RG_0LE0RH_1LF1LE_0RD0RA_1RB0LE_1RC0LD"
def parse(m):
    T={}
    for i,g in enumerate(m.split('_')):
        for s in range(2):
            t=g[3*s:3*s+3]
            T[(chr(65+i),s)]=None if t[0]=='-' else (int(t[0]),t[1],t[2])
    return T
T=parse(M)
def run(n,show=None):
    tape={};p=0;q='A';st=0
    while st<n:
        s=tape.get(p,0);t=T[(q,s)]
        if t is None: print("HALT",st);return
        w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
        if show and show(st,q,p,tape): pass
    return tape,p,q
def fmt(tape,p,q):
    lo=min(min(tape),p);hi=max(max(tape),p)
    s=''
    for i in range(lo,hi+1):
        if i==p: s+='['+q+']'
        s+=str(tape.get(i,0))
    return s
if __name__=="__main__":
    n=int(sys.argv[1])
    tape={};p=0;q='A'
    import collections
    st=0;lo=hi=0
    while st<n:
        s=tape.get(p,0);t=T[(q,s)]
        if t is None: print("HALT",st);break
        w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
        if p<lo:
            lo=p; print(st,'L',fmt(tape,p,q)[:200])
        if p>hi:
            hi=p; print(st,'R',fmt(tape,p,q)[:200])
