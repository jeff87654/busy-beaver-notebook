import re,sys
from val import probe
m='1RB1RA_0LC0RG_1LE1LD_1LC0LB_0RF1RD_1RB1RD_1RE0RH_1RA---'
def enc(L): return 'F 1'+'0'.join('01'*d for d in L)+'0|0'
def dec(r):
    if r[0]!='S': return (r[0],r[1])
    if r[4].strip('0'): return ('R?',)
    t=r[2].lstrip('0')
    if not t.startswith('1') or not t.endswith('0'): return ('?',t[:80])
    body=t[1:-1]
    if not re.fullmatch(r'(01|0)*',body): return ('?',t[:80])
    L=[];d=0;i=0
    while i<len(body):
        if body.startswith('01',i): d+=1;i+=2
        else: L.append(d);d=0;i+=1
    L.append(d)
    return tuple(L)
def step(Ls,N=10**9):
    res=probe(m,'F','R',[enc(L) for L in Ls],N)
    return [dec(r) for r in res]
if __name__=='__main__':
    Ls=[tuple(map(int,a.split(','))) for a in sys.argv[1:]]
    for L,o in zip(Ls,step(Ls)): print(L,'->',o)
def nstep(Ls,N=10**9,maxev=20):
    """advance each list to the next native event; returns (list or status, events)"""
    cur=[enc(L) for L in Ls]; out=[None]*len(Ls); nev=[0]*len(Ls); act=list(range(len(Ls)))
    for it in range(maxev):
        if not act: break
        res=probe(m,'F','R',[cur[i] for i in act],N); nact=[]
        for i,r in zip(act,res):
            d=dec(r); nev[i]+=1
            if d and d[0]=='?': cur[i]='F '+r[2]+'|'+r[4]; nact.append(i)
            else: out[i]=d
        act=nact
    return list(zip(out,nev))
