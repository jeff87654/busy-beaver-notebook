# abstract F-turn system: L = list of bits (stack, last = nearest), P in prefixes, G = list of gaps (G[0] nearest), INF at end implicit
import sys
INF=10**9
def step(L,P,G):
    """returns (L,P,G) or raises"""
    G=list(G); L=list(L)
    def g(i): return G[i] if i<len(G) else INF
    if P in ('111','1111','11101'):
        x=L.pop() if L else 0
        if P=='111':
            if G: G[0]+=1
            return L,'%d11'%x,G
        if P=='1111':
            if x==1: return L,'11101',G
            raise Exception('1111 with x=0')
        if P=='11101':
            return L,'%d11'%x,[2]+G
    if P in ('011','0111'):
        x=L.pop() if L else 0
        if P=='011':
            if G: G[0]+=2
            return L,'%d1'%x,G
        return L,'%d1'%x,[2]+G
    if P=='11':
        m=0
        while g(m)==2: m+=1
        gg=g(m)
        if gg<4: raise Exception('R3 gap %d'%gg)
        L=L+[0]+[1,1,0]*m+[1]
        rest=G[m+1:]
        if gg==INF: return L,'111',[]
        if gg-3==1: return L,'11101',rest
        return L,'111',[gg-3]+rest
    if P=='01':
        m=0
        while g(m)==2: m+=1
        gg=g(m)
        if gg<3: raise Exception('R4 gap %d'%gg)
        rest=G[m+1:]
        if m==0:
            if gg==INF: return L,'0111',[]
            if gg-2==1: raise Exception('0111 gap1')
            return L,'0111',[gg-2]+rest
        L=L+[0,0,1]+[1,0,1]*(m-1)
        if gg==INF: return L,'1111',[]
        return L,'1111',[gg-2]+rest
    raise Exception('bad P '+P)
def tostr(L,P,G):
    s=''.join(map(str,L))+'[F]'+P+''.join('0'*x+'1' for x in G)
    return s
if __name__=='__main__':
    # start from S(k): [F](010)^k = P=01, G=[2]*(k-1) then INF; L empty
    k=int(sys.argv[1]); n=int(sys.argv[2])
    L,P,G=[],'01',[2]*(k-1)
    for i in range(n):
        print(i,tostr(L,P,G))
        L,P,G=step(L,P,G)
