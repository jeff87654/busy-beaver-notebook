import sys
from sim import parse
from probe import enc
def lit(L,M,maxn):
    T=parse(M); s=enc(L); size=len(s)+2*10**6; tape=bytearray(size); pos=10**6
    for i,ch in enumerate(s): tape[pos+1+i]=1 if ch=='1' else 0
    st=6
    for n in range(maxn):
        c=tape[pos]
        if (st,c) not in T: return ('HALT',n+1,sum(tape))
        w,d,q=T[(st,c)]; tape[pos]=w; pos+=d; st=q
    return ('NOHALT',maxn)
if __name__=='__main__':
    M=sys.argv[1]
    for c in sys.argv[2:]:
        print(c, lit([int(x) for x in c.split(',')],M,5*10**7))
