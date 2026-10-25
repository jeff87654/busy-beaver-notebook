# canonical abstract system: P in {111,011,11,01}, G list with first gap possibly 0/1
INF=10**9
class Stuck(Exception): pass
def canon(P,G):
    if P=='1111': return '111',[0]+G
    if P=='11101': return '111',[1]+G
    if P=='0111': return '011',[0]+G
    return P,list(G)
def step(L,P,G):
    L=list(L);G=list(G)
    def g(i): return G[i] if i<len(G) else INF
    if P in ('111','011'):
        x=L.pop() if L else 0
        if not G: G=[INF]
        if P=='111': G[0]+=1; return L,'%d11'%x,G
        G[0]+=2; return L,'%d1'%x,G
    m=0
    while g(m)==2: m+=1
    gg=g(m); rest=G[m+1:]
    if P=='11':
        if gg<4: raise Stuck('R3 gap %d'%gg)
        return L+[0]+[1,1,0]*m+[1],'111',([gg-3] if gg<INF else [])+rest
    if P=='01':
        if gg<3: raise Stuck('R4 gap %d'%gg)
        G2=[0]+([gg-2] if gg<INF else [])+rest
        if m==0: return L,'011',G2
        return L+[0,0]+[1,1,0]*(m-1)+[1],'111',G2
    raise Stuck('P '+P)
