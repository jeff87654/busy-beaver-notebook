# pycheck.py CERT : independent re-check of an ngann certificate with the semantics used in the Coq proof.
# Only the learned state sets S_L, S_R are read; preds and the configuration set C are recomputed here.
import sys
from collections import deque
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
tm={}
for i,r in enumerate(M.split('_')):
    for c in range(2):
        t=r[3*c:3*c+3]; tm[(i,c)]=None if t[0]=='-' else (int(t[0]),'R' if t[1]=='R' else 'L',ord(t[2])-65)
L=open(sys.argv[1]).read().split('\n')
kL,kR,ann,gon=map(int,L[0].split()[1:])
assert ann==2 and gon==1
SL=set(); SR=set(); Cdump=set()
for l in L[1:]:
    p=l.split()
    if not p: continue
    if p[0]=='S': (SL if p[1]=='0' else SR).add(int(p[2]))
    elif p[0]=='C': Cdump.add((int(p[1]),int(p[2]),int(p[3]),int(p[4])))
CW=5; CODES=list(range(18))
wL=(1<<(CW*kL))-1; wR=(1<<(CW*kR))-1
def gt(g,x):
    r=0
    for X in range(8):
        t=tm[(X,x)]
        if t is None or (t[1]=='R' and (g>>t[2])&1): r|=1<<X
    return r
def foldL(s,c): return ((s&wL)<<CW|c)&wL
def foldR(s,c): return (((s&wR)<<CW|c)&wR)|(gt(s>>55,c&1)<<55)
g=0
for _ in range(64): g=gt(g,0)
zL=0; zR=g<<55
assert foldL(zL,0)==zL and foldR(zR,0)==zR and zL in SL and zR in SR
def preds(S,fold):
    P={}
    for s in S:
        for c in CODES: P.setdefault(fold(s,c),[]).append((c,s))
    return P
PL=preds(SL,foldL); PR=preds(SR,foldR)
def code(w,q): return w+2*(1+q)
start=(0,0,zL,zR)
C={start}; Q=deque([start]); bad=0
while Q:
    q,m,sl,sr=Q.popleft()
    t=tm[(q,m)]
    if t is None: print('HALTING config reached'); sys.exit(1)
    w,d,q2=t
    if d=='R':
        if sl not in SL: print('fold of unlearned left state'); sys.exit(1)
        nl=foldL(sl,code(w,q))
        succ=[(q2,c&1,nl,s2) for c,s2 in PR.get(sr,[])]
    else:
        if sr not in SR: print('fold of unlearned right state'); sys.exit(1)
        nr=foldR(sr,code(w,q))
        succ=[(q2,c&1,s2,nr) for c,s2 in PL.get(sl,[])]
    for s in succ:
        if s not in C: C.add(s); Q.append(s)
print('closed: %d configs (dump has %d, equal sets: %s), |S_L|=%d |S_R|=%d'%(len(C),len(Cdump),C==Cdump,len(SL),len(SR)))
